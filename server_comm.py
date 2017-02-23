#coding=utf-8
import sys, re, os, comm_lib , pexpect, time
#import paramiko, MySQLdb

def ssh(ip, port, username, passwd, cmd=None, file=None, dest_file=None, isexcute=True, timeout=5):
    ret=0
    d=''
    if file:
        if not os.path.exists(file):
            ret=-1
        if not dest_file:
            dest_file='/tmp/%s' % file.split(os.sep)[-1]
        r_cmd='scp -P %s %s %s@%s:%s' % (int(port), file, username, ip, dest_file)
    elif cmd:
        if os.path.exists(cmd):
            ret=-2
        r_cmd='ssh -p %s %s@%s "%s"' % (int(port),username, ip, cmd)
    else:
        r_cmd='ssh -p %s %s@%s ' % (int(port),username, ip)

    sh = pexpect.spawn(r_cmd)
    try:
        i = sh.expect(['password:', 'continue connecting (yes/no)?'], timeout=timeout)
        if i == 0 :
            sh.sendline(passwd)
        elif i == 1:
            sh.sendline('yes\n')
            sh.expect('password: ')
            sh.sendline(passwd)
 
        if cmd:
            #是命令则执行
            sh.sendline(cmd)
            d = sh.read().replace(cmd,'').strip()
        elif file:
            #是文件则执行
            while 1:
                d = sh.read().strip()
                if re.match('.*100%.*',d):
                    break
                else:
                    time.sleep(0.5)
            if isexcute:
                check_cmd='chmod a+x %s;%s' % (dest_file, dest_file)
                if cmd:
                    ssh(ip, port, username, passwd, cmd=cmd)
                else:
                    ssh(ip, port, username, passwd, cmd=check_cmd)
        ret = 2
    except pexpect.EOF:
        d="EOF"
    except pexpect.TIMEOUT:
        d="TIMEOUT"
    finally:
        sh.close()
        
    return [ret ,d.strip()]
