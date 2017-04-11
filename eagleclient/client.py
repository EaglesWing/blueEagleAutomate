#/usr/bin/python
#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os, json, datetime, struct, socket, comm_lib, select, time, multiprocessing, subprocess, re, shutil, signal
import socket, select, commands, threading, Queue
from daemon import Daemon

def propre_file(filepath):
    if not filepath:
        dest_dir=curr_path+os.sep+"file/twisted"
        dest_path=dest_dir+os.sep+os.path.split(filepath)[1]
    else:
        dest_dir=os.path.split(filepath)[0]
        dest_path=dest_dir+os.sep+os.path.split(filepath)[1]
    
    if not os.path.exists(dest_dir):
        #并发时候会冲突，导致线程崩溃
        try:
            os.makedirs(dest_dir)
        except:
            pass
            
    if os.path.isdir(dest_path):
        log.err('dest_path err, it is can not dir.need file.skip.')
        return 

    if os.path.exists(dest_path):
        os.rename(dest_path, dest_path+str(comm_lib.get_now()).replace(' ', '_'))
    if os.path.exists(dest_path):
        log.warn('file %s backup failed. please check!' % dest_path)
    else:
        log.info("file %s backup done." % filepath)

    
def post_propre_file(filepath):
    log.info("file %s post-preproccess done." % filepath)
    
 
def file_data_check(request):
    log.info("do file data check.")
    deploy_type=request.get('deploy_type')
    file_path=request.get('dest_path')
    file_md5=request.get('md5')
    is_exec=request.get('isexcute')
    
    curr_file_md5=''
    if not os.path.exists(file_path):
        #还未接收到文件数据
        log.warn('file %s is not exists, skip check.' % file_path)
        file_state=-1
    else:
        curr_file_md5=comm_lib.getmd5(file_path)
        if curr_file_md5 == file_md5:
            log.info('file %s data check success.can call(or not:is_exec[%s]) it now.' % (file_path, is_exec))
            file_state=2
            
    request.update({
        'request':'file_data_check_response', 
        'send_state':file_state
    })
    return comm_lib.send_socket_data(sk.s, request)

def execute_task_cmd(taskdata):
    if taskdata.get('object')=="file_data_check":
        return file_data_check(taskdata)
        
    task_name=taskdata.get('task_name')
    cmd_obj=taskdata.get('object')
    dotype=taskdata.get('dotype')
    collecttemplate=taskdata.get('collecttemplate')

    taskdata.update({
        'request':'task_response', 
        'task_status':''
    })

    #任务使用预处理脚本调用
    script_path=curr_path+os.sep+'sh/task_call_prehandle.sh'
    if not os.path.exists(script_path):
        return log.err('can not find task_call_prehandle.sh, skip.')
    #一次接收一个任务调用
    if isinstance(cmd_obj, list):
        cmd_obj=cmd_obj[0]
        
    exc_failed=False
    if not cmd_obj:
        return log.err('task[%s] execute failed. cmd obj is None.')
        
    cmd=cmd_obj
    taskdata['task_status']="running"
    cmd_type=dotype
    if not cmd_type:
        cmd_type='run'
    elif cmd_type=="cancel":
        cmd_type='stop'
    elif cmd_type=="restart" or cmd_type =="single_restart":
        cmd_type='stop'
        log.info('call task_call_prehandle.sh[%s %s  %s  %s] begin.' % (script_path, cmd_type, task_name, cmd))
        exec_cmd='dos2unix %s >/dev/null 2>&1;chmod u+x %s;%s %s  %s  %s' % (script_path, script_path, script_path, cmd_type, task_name, cmd)
        
        commands.getstatusoutput(exec_cmd)
        cmd_type='run'
        
    exec_cmd='dos2unix %s >/dev/null 2>&1;chmod u+x %s;%s %s  %s  %s' % (script_path, script_path, script_path, cmd_type, task_name, cmd)
        
    log.info('call task_call_prehandle.sh[%s %s  %s  %s] begin.' % (script_path, cmd_type, task_name, cmd))   
    ret, detail=commands.getstatusoutput(exec_cmd)
    if ret >> 8 !=0:
        exc_failed=True
        taskdata['task_status']="failed"
        log.err('call task_call_prehandle.sh err.\n%s' % detail)
    else:
        if dotype=="cancel":
            taskdata['task_status']="cancel"
        else:
            taskdata['task_status']="success"
            if collecttemplate:
                taskdata.update({'collectdata':detail})
    log.info('task %s call done.' % str(cmd))

    if exc_failed:
        log.warn('task %s  can not execute done.' % cmd_obj)
    else:
        log.info('call %s done.' % task_name)
    return comm_lib.send_socket_data(sk.s, taskdata)

def get_task_log(request):
    task_name=request.get('task_name')
    filename=request.get('filename')
    download=request.get('download')
    request['request']="task_log_response"    
    request['response']='' 

    log_file=curr_path+os.sep+task_log_path+os.sep+task_name+os.sep+filename.split(os.sep)[-1]+".log"

    log.info('get task log[%s]' % log_file)
    if not  os.path.exists(log_file):
        request['response']='log file[%s] is not exists' % log_file
        return comm_lib.send_socket_data(sk.s, request)

    with open(log_file, 'rb') as f:
        #下载日志时候读取后直接返回
        if download:
            dt=f.read()
            request['response']=dt
            return comm_lib.send_socket_data(sk.s, request)

        count=int()    
        while 1:
            request['response']=''
            lines=f.readlines()
            if not lines:
                count+=1
                #1分钟没新的数据写到日志则退出
                if count >= 60:
                    return
                    
                time.sleep(1)
            else:
                request['response']=lines
                if re.match(r'^:::task[ \t]+call[ \t]+done[ \t]+.*[0-9]+', lines[-1]):
                    request.update({
                        'logdone':'yes'
                    })
                comm_lib.send_socket_data(sk.s, request)   
                if  request.get('logdone') == 'yes':
                    return
                
def file_execute(data):
    file=data.get('file')
    if os.path.exists(file):
        cmd='''chmod a+x %s;%s''' % (file, file)
        ret, detail=commands.getstatusoutput(cmd)
        return log.info(detail)
        
def download_file(data):
    file=data.get('file')
    filedata=''
    if not os.path.exists(file):
        filedata=-1
    with open(file, 'rb') as f:
        filedata=f.read()
    data.update({
        'request':'download_file_response',
        'filedata':filedata
    })
    return comm_lib.send_socket_data(sk.s, data)
        
def find_file_path(data):
    role=data.get('role')
    if not role:
        return False
    roletmp=''
    for i in role.split(os.sep):
        if i:
            if not re.match(r'.*[a-zA-Z0-9-_]+.*', i):
                break

            roletmp+=os.sep+str(i)

    cmd=''' getfacl %s -R 2>/dev/null|grep -P "%s"|awk '{a=a"/"$NF"::::::"}END{print a}' ''' % (roletmp, re.sub('^/+', '', role))
    ret, detail=commands.getstatusoutput(cmd)
    if ret >> 8 !=0:
        filelist=''
    else:
        filelist=detail

    data.update({
        'request':'find_file_path_response',
        'filelist':filelist.split('::::::')
    })
    return comm_lib.send_socket_data(sk.s, data)
        
def client_handle(data):
    type=data.get('method')
    client_sh=curr_path+os.sep+'sh'+os.sep+"client.sh"
    if type not in ['stop', 'start', 'restart', 'update']:
        return 
   
    log.info('client %s .' % type)
    if not os.path.exists(client_sh):
        return log.info('can not find %s , skip.' % client_sh)
    
    cmd=''' dos2unix %s >/dev/null 2>&1;chmod u+x %s;sh %s %s''' % (client_sh, client_sh, client_sh, type)
    dt={}
    dt['request']="client_handle_respose"
    dt['method']=type
    
    ret, detail=commands.getstatusoutput(cmd)
    if ret >> 8 != 0:
        log.info(detail)
        log.info('client %s falied.' % type)
        dt['status']="failed"
    else:
        dt['status']="success"
        log.info('client %s  success.' % type)
        
    return comm_lib.send_socket_data(sk.s, dt)
   
def do_task(request):
    if request.get('type')=="preproccess" and request.get('filename'):
        return propre_file(request['filename'])
    elif request.get('type')=="post-preproccess" and request.get('filename'):
        return post_propre_file(request['filename'])
    elif request.get('type')=="obj_execute" and request.get('object') and request.get('task_name'):
        return execute_task_cmd(request)
    elif request.get('type')=="file_execute":
        return file_execute(request)
    elif request.get('type')=="find_file_path":
        return find_file_path(request)
    elif request.get('type')=="download_file":
        return download_file(request)
    elif request.get('type')=="client_handle":
        return client_handle(request)
    elif request.get('type')=="get_task_log" and request.get('task_name'):
        return get_task_log(request)
    else:
        return log.warn('do_task err.')
        
def write_file(filename, data, id):
    if id == 0:
        propre_file(filename)
        
    with open(filename, 'ab+') as f:
        f.write(buffer(data))

    if not  os.path.exists(filename):
        return log.err('write file err. %s  is not exists.' % filename)
    return log.info("file %s write done." % filename)
    
def do_request(request):
    if request['d_type']==0:
        try:
            request_data=json.loads(request['data'])
        except:
            request_data=request['data']
        return do_task(request_data)
        
    elif request['d_type']==1:
        return write_file(request['filename'], request['data'], request['id'])

def get_data(data):
    d=sk.unpack(data)
    return d

def getconf(cfg, attrname=None, attrvalue=None):
    if not os.path.exists(cfg):
        return False
    info={}
    tw_xml=comm_lib.xml(cfg)
    tw_conf=tw_xml.get_tag("config", attrname, attrvalue)
    for child_node in tw_conf.childNodes:
        if child_node.nodeType ==1:
            attr={}
            for att, value in zip(child_node.attributes.keys(), child_node.attributes.values()):
                attr.update({att:value.nodeValue})
            info[child_node.nodeName]=attr

    return  info

class clientdaemon(Daemon):
    def __init__(self, *args, **kwargs):
        super(clientdaemon, self).__init__(*args, **kwargs)

    def run(self):
        server_ip=self.server_ip
        server_port=self.server_port
        global sk
        skt=comm_lib.sock_client(server_ip, int(server_port))
        sk=skt
        if not skt.conn():
            log.err('connection to %s:%s failed' %(server_ip, server_port))
            sys.exit()
        else:
            log.info('connection to %s:%s success' %(server_ip, server_port))

        epoll=select.epoll()
        thread_poll=comm_lib.thread_manager()

        epoll.register(skt.get_fielno(), select.EPOLLOUT)
        try:
            while 1:
                events=epoll.poll(-1)
                for fileno, event in events:
                    if event & select.EPOLLOUT:
                        epoll.modify(fileno, select.EPOLLIN)
                    elif event & select.EPOLLIN:
                        data=''
                        try:
                            data=skt.recv_data()
                        except:
                            if sys.exc_info()[0]:
                                log.warn('lineno:' + str(sys._getframe().f_lineno)+": "+str(sys.exc_info()))
                        if not data:
                            count=0
                            log.err('disconnection from  %s' % server_ip)
                            while 1:
                                try:
                                    epoll.unregister(fileno)
                                except:
                                    pass

                                skt=comm_lib.sock_client(server_ip, int(server_port))
                                if not skt.conn():
                                    log.err('reconntinue %s:%s failed.continue.'%(server_ip, server_port))
                                    if count < 30:
                                        time.sleep(1)
                                    elif count > 30 and count < 90:
                                        time.sleep(10)
                                    else:
                                        time.sleep(60)
                                        continue
                                else:
                                    log.info('reconntinue %s:%s success.'%(server_ip, server_port))
                                    sk=skt
                                    #新的 fileno
                                    fileno=sk.get_fielno()
                                    #重新注册一遍
                                    epoll.register(fileno,select.EPOLLOUT)
                                    break

                        else:
                            dt=get_data(data)
                            if dt:
                                if dt['data'] != "conn" and dt['data'] != "close":
                                    try:
                                        thread_poll.add_worker(target=do_request, args=(dt, ))
                                    except:
                                        if sys.exc_info()[0]:
                                            log.warn('lineno:' + str(sys._getframe().f_lineno)+": "+str(sys.exc_info()))
                                    
                        epoll.modify(fileno, select.EPOLLOUT)
                    elif event & select.EPOLLERR:
                        epoll.modify(fileno, select.EPOLLOUT)
                    elif event & select.EPOLLHUP:
                        epoll.unregister(fileno)
                        skt.close()
        finally:
            log.info(sys.exc_info())
            epoll.unregister(skt.socket().fileno())
            epoll.close()
            skt.close()

if __name__=="__main__":
    curr_path=os.path.split(os.path.realpath(__file__))[0]
    curr_file_name=os.path.split(os.path.realpath(__file__))[1]
    p_client=curr_path+os.sep+"config"+os.sep+"config.xml"
    client_conf=getconf(p_client, 'name', 'client')
    p_log=curr_path + os.sep + 'log' +os.sep + 'client.log'
    log=comm_lib.log(p_log)
    server_ip=client_conf['server']['ip']
    server_port=client_conf['server']['port']
    task_log_path=client_conf['server']['task_log_path']
    global sk
    sk=''

    help_msg = 'Usage: python %s <start|stop|restart|debug>' % sys.argv[0]
    clientdaemon=clientdaemon(curr_path+'/client_pid.pid', server_ip=server_ip, server_port=server_port)
    if len(sys.argv) == 1:
        clientdaemon.start()
    elif sys.argv[1] in ['debug']:
        clientdaemon.run()
    elif sys.argv[1] in ['start', 'stop', 'restart']:
        getattr(clientdaemon, sys.argv[1])()
    else:
        print help_msg
        sys.exit(1)
    