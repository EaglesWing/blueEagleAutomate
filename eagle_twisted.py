#!/usr/bin/python
#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from twisted.internet import reactor, task, main
from twisted.internet import threads, tcp

from twisted.internet.protocol import Protocol,Factory,defer
from twisted.protocols.basic import LineReceiver,NetstringReceiver
import os,time,copy,datetime,comm_lib,json,struct,shutil,server_comm,torndb,threading,socket,commands
import smtplib,encrypt,urllib2,re,Queue,user_table,random
from email.mime.text import MIMEText
from email.header import Header

from errno import EWOULDBLOCK
from daemon import Daemon

from twisted.internet import epollreactor
from select import epoll, EPOLLHUP, EPOLLERR, EPOLLIN, EPOLLOUT

class posixbase_replace(epollreactor.EPollReactor):
    def __init__(self):
        #super有缺陷, 多重继承时候self始终是第一个class
        #super(epollreactor.EPollReactor, self).__init__()
        epollreactor.EPollReactor.__init__(self)
        self.socketreadone={}
        
    def setfdfalse(self, fd):
        self.socketreadone[fd]=False
        
    def setfdtrue(self, fd):
        self.socketreadone[fd]=True
    
    def addto(self, skt):
        self.doadd(skt, self._reads, self._writes, self._selectables,
                    EPOLLIN, EPOLLOUT)

    def _doReadOrWrite(self, selectable, fd, event):
        why = None
        inRead = False
        if event & self._POLL_DISCONNECTED and not (event & self._POLL_IN):
            if fd in self._reads:
                inRead = True
                why = CONNECTION_DONE
            else:
                why = CONNECTION_LOST
        else:
            try:
                if selectable.fileno() == -1:
                    why = _NO_FILEDESC
                else:
                    if event & self._POLL_IN:
                        why = selectable.doRead()
                        inRead = True
                    if not why and event & self._POLL_OUT:
                        why = selectable.doWrite()
                        inRead = False
            except:
                why = sys.exc_info()[1]
                log.err()

        if self.socketreadone.get(fd):
            try:
                self._poller.modify(fd, EPOLLOUT)
            except:
                pass
            del self.socketreadone[fd]
        elif why:
            self._disconnectSelectable(selectable, why, inRead)


class transport_doread_replace(tcp.Connection):
    '''替换协议doread方法'''
    def __init__(self,skt, protocol, reactor=None):
        tcp.Connection.__init__(self,skt,protocol,reactor=reactor)
        self.read_lock=threading.Lock()
        
        self.socket = skt
        self.socket.setblocking(0)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)
        self.fileno=self.socket.fileno()
        self.protocol=protocol
        
    def getsocketdatadone(self, header):
        data=comm_lib.recv_data(self.socket, getbody=True, header=header)
        posixbase_replace.setfdtrue(self.fileno)
        self.read_lock.release()
        return self._dataReceived(data)
        
    def doRead(self):
        self.read_lock.acquire()
        data=""
        getdone=True
        try:
            data=comm_lib.recv_data(self.socket, getheader=True)
            if not data:
                return   
            posixbase_replace.setfdfalse(self.fileno)
            getdone=False
            t=threading.Thread(target=self.getsocketdatadone, args=(data, ))
            t.setDaemon(True)
            t.start()
        
        except socket.error as se:
            if se.args[0] == EWOULDBLOCK:
                return
            else:
                return main.CONNECTION_LOST
        finally:
            if getdone:
                self.read_lock.release()
                return self._dataReceived(data)

class clien(object):
    def __init__(self):
        self.client_pkg=curr_path+os.sep+'eagleclient.zip'

    def zip_client(self):
        '''压缩client目录'''
        log.info('zip %s to %s begin' % ('./eagleclient', self.client_pkg) )
        shutil.copy('./comm_lib.py','./eagleclient/comm_lib.py')
        shutil.copy('./daemon.py','./eagleclient/daemon.py')
        zip_file=comm_lib.zip_file('./eagleclient')
        zip_file.zipfile()
        if os.path.exists(self.client_pkg):
            log.info('client pkg zip success.')
            return True
        else:
            log.info('client pkg zip failed.')
            return False
            
    def do_client_opertion(self, ip, user, port, pwd):
        '''ssh方式登录ip进行操作'''
        if self.dotype in ['groupcheck', 'membercheck']:
            if self.connlist.get(ip):
                return True
            else:
                raise Exception('%s check status is offline.' % ip)
                
        elif self.dotype in ['groupdeploy', 'memberdeploy']:
            log.info('client deploy on %s begin.'% ip)
            if not self.zip_client():
                return log.warn('client pkg zip err.skip deploy.')
            file=self.client_pkg
            #创建路径
            self.do_check(ip, user, port, pwd, cmd='mkdir -p  %s' % client_deploy_path)
            #发送文件
            dest_file=client_deploy_path + os.sep + file.split(os.sep)[-1]
            self.do_check(ip, user, port, pwd, file=file, dest_file=dest_file, isexcute=False)
            cmd="yes|unzip %s -d %s;sh %s/eagleclient/sh/client.sh start" % (dest_file, client_deploy_path, client_deploy_path)
            return self.do_check(ip, user, port, pwd, cmd=cmd)
            
    def do_serverinit(self, ip, user, port, pwd, file):
        '''服务器初始化'''
        return self.do_check(ip, user, port, 
                                pwd, file=file, timeout=5)
        
    def do_check(self, ip, user, port, pwd, cmd=None, file=None, dest_file=None, isexcute=None, timeout=15):
        '''服务器检查'''
        #使用expect而不使用paramiko的原因:paramiko有的场景不能登录成功;如ssh v2的keyboard-interactive认证场景
        log.info('execute cmd[%s] or file[%s]  on %s' % (cmd, file, ip))
        ret, detail=server_comm.ssh(ip, port, user, pwd, cmd=cmd, 
                                    file=file, isexcute=isexcute, 
                                    dest_file=dest_file, timeout=timeout)
        log.info(detail)
        if not ret:
            log.warn('execute cmd[%s], file[%s] failed, on %s.' % (cmd, file, ip))
            raise Exception('failed')

    def check_success(self, reson, ip, c_user):
        if self.dotype in ['groupcheck', 'membercheck']:
            state="online"
        else:
            state="success"
        
        self.result_list[ip]=state
        if self.checktype== "serverinit":
            user_table.add_serverinit_history(ip, '2', tool_path, c_user)
            
    def check_err(self, reson, ip, c_user):
        log.err(reson)
        if self.dotype in ['groupcheck', 'membercheck']:
            state="offline"
        else:
            state="failed"
        self.result_list[ip]=state
        if self.checktype== "serverinit":
            user_table.add_serverinit_history(ip, '3', tool_path, c_user)
            
    def response_tornado(self, reson, skt, data):
        '''返回请求给tornado,tornado收到请求后关闭socket'''
        return comm_lib.send_socket_data(skt, data)

    def get_login(self, data):
        '''获取服务器登录信息'''
        info={
            'user':'',
            'port':'',
            'pwd':''
        }
        ip=data.get('ip')
        user=data.get('user')
        port=data.get('port')
        pwd=data.get('pwd')
        type=data.get('type')
        line=data.get('line')
        product=data.get('product')
        app=data.get('app')
        idc=data.get('idc')
        owner=data.get('owner')
        info['user']=user 
        info['port']=port
        
        if type == "logintools" or type == "logininitools":
            #安照前端设计:上传用户名获取工具,工具执行退出返回值应为0,且只能有用明文户名输出;
            #执行时候会把当前条件下'ip/产品线/业务/应用/机房/负责人'信息按序传给工具,按需获取;

            #安照前端设计:上传端口获取工具,工具执行退出返回值应为0,且只能有明文端口输出;
            #执行时候会把当前条件下'登录用户/ip/产品线/业务/应用/机房/负责人'信息按序传给工具,按需获取;

            #安照前端设计:上传用户名密码获取工具,工具执行退出返回值应为0,且只能有明文用户名密码输出;
            #执行时候会把当前条件下'登录用户/端口/ip/产品线/业务/应用/机房/负责人'信息按序传给工具,按需获取
            
            parameter_init='   %s %s %s %s %s %s' % (ip, line, product, app, idc, owner)
            file_key=['user', 'port', 'pwd']
            for i in file_key:
                if i == "user":
                    parameter=parameter_init
                elif i == 'port':
                    parameter= info['user'] + ' '+  parameter_init
                elif i == 'pwd':
                    parameter= info['user'] +' '+ info['port'] + ' '+ parameter_init
                    
                file=locals().get(i)
                cmd='chmod a+x %s;%s %s' % (curr_path+os.sep+file, curr_path+os.sep+file, parameter)
                ret,detail=commands.getstatusoutput(cmd)
                
                if ret >> 8 != 0:
                    info[i]='failed'
                    return info
                info[i]=detail
        else:
            #不传输明文密码,这里是密文
            pwd=decode_pwd(pwd)
            info['pwd']=pwd
  
        return info

    def inform_user(self, message):
        '''这部分还未验证,需要调测'''
        log.warn('inform:'+message)
        self.db_info_data['get_inform_account']='get_inform_account_info'
        accountlist=self.do_db_get_method('get_inform_account')
        account={ i.get('name'):i for i in accountlist if i.get('status') == 'on' }
        
        for k in account.keys():
            #微信或者/email
            type=account[k].get('type')
            member=account[k].get('member', '')
            if not member:
                continue
            if type == 'email':
                account[k].update({'pwd':decode_pwd(account[k].get('pwd'))})
                d=threads.deferToThread(comm_lib.send_email, account[k], message=message)
                d.addErrback(self.defer_show_expect)
            elif type == 'wechat':
                member=account[k].get('member')
                if not member:
                    continue
                member=member.split(',')
                for u in member:
                    d=threads.deferToThread(comm_lib.send_wechat, u, account[k], message)
                    d.addErrback(self.defer_show_expect)

    def client_check_and_inform(self, data):
        '''检查有无登录信息和客户端是否在线及任务文件是否存在'''
        logininfo=data.get('logininfo')
        groupinfo=data.get('groupinfo')
        task_name=data.get('task_name')
        task_info=data.get('task_info', [{}])[0].get('task_list', {}).get('relevancelist')

        for i in groupinfo:
            modal=i.get('modal')
            ip=i.get('member')
            ip_logininfo=logininfo.get(ip)
            massage=''
            if modal == 'no' and ( not ip_logininfo or (not ip_logininfo.get('user')
                                or not ip_logininfo.get('port') or not ip_logininfo.get('pwd'))):
                massage='[warn:]task[%s] server %s get loginfo err. please check.' % (task_name, ip)
            elif modal =='yes' and not self.connlist.get(ip):
                massage='[warn:]task[%s] server %s is off line. please check.' % (task_name, ip)
            if   massage:  
                self.inform_user(massage)
                
        for i in task_info:
            if self.prepro_isslave(i):
                file_source=i.get('preprofile')
            else:
                file_source=curr_path+os.sep+'task/'+i.get('task_id')+os.sep+os.path.split(i.get('filename'))[1]
            if not comm_lib.isexists(file_source):
                self.inform_user('[warn:]task[%s] file source %s is not exists. please check.' % (task_name, file_source))
       
    def clien_opertion(self, data):
        self.checktype=data.get('checktype')
        self.dotype=data.get('type')
        self.result_list={}
        c_user=data.get('c_user')
        iplist=data.get('iplist')
        dlist=[]

        for ip in iplist:
            if data['request']  in ['serverinit', 'do_logincheck']:
                infodata=data
            elif data['request']  in ['client_opertion']:
                infodata=iplist[ip]
            infodata.update({'ip':ip})
            logininfo = self.get_login(infodata)
            
            tool_path=infodata.get('tool_path')
            type=infodata.get('type')
            if type in  ["logininitools", 'logininitools']:
                checkret=False
                for i in ['user', 'port', 'pwd']:
                    if info.get(i) == 'failed':
                        checkret=True
                        file=logininfo.get(i)
                        self.result_list[os.path.split(file)[-1]]='failed'
                        break
                if  checkret:
                    break
                    
            user=logininfo.get('user')
            port=logininfo.get('port')
            pwd=logininfo.get('pwd')

            if self.checktype== "serverinit":
                d=threads.deferToThread(self.do_serverinit, ip, user, port, pwd, tool_path)
            elif data['request'] == "client_opertion":
                d=threads.deferToThread(self.do_client_opertion, ip, user, port, pwd)
            else:
                d=threads.deferToThread(self.do_check, ip, user, port, pwd)
            d.addCallback(self.check_success, ip, c_user)
            d.addErrback(self.check_err, ip, c_user)
            dlist.append(d)
            
        d=defer.DeferredList(dlist)
        d.addBoth(self.response_tornado, data.get('socket').transport.getHandle(), self.result_list)

class server_protocol(Protocol):
    def __init__(self):
        self.ip=''
        self.port=int()
        self.socket_fileno=''
        self.data=''
        
    def ipcheck(self, ip):
        '''检查当前链接的ip是不是tornado/在不在资产,若不是,拒绝链接'''
        ret=False
        if user_table.assets_search(iplist=ip) or ip == tornado_ip or ip == "127.0.0.1":
            ret=True
        return  ret 
       
    def close_conn(self,senddata=None):
        if senddata:
            self.transport.write(senddata)
        self.transport.loseConnection()
        if self.factory.connlist.get(self.ip):
            if self.ip == tornado_ip:
                del self.factory.connlist[self.ip][self.socket_fileno]
                log.info('the %s fileno lost of tornado.' % self.socket_fileno)

            if self.ip != tornado_ip or (not self.factory.connlist.get(tornado_ip) and self.ip == tornado_ip):
                del self.factory.connlist[self.ip]
                self.factory.conn_count-=1
                log.info("%s conn lost. count %s "% (self.ip,self.factory.conn_count))
        
    def connectionLost(self,reason):
        self.close_conn()

    def connectionMade(self):
        self.transport.doRead=transport_doread_replace(self.transport.getHandle(),self,reactor=reactor).doRead
        self.ip=self.transport.client[0]
        self.port=self.transport.client[1]
        self.socket_fileno=self.transport.socket.fileno()
        if self.ip not in self.factory.connlist:
            self.factory.conn_count+=1
        if self.ip == tornado_ip:
            self.factory.connlist.setdefault(self.ip,{})
            self.factory.connlist[self.ip][self.socket_fileno]=self
        else:
            self.factory.connlist[self.ip]=self

        if self.factory.conn_count >= self.factory.max_conn:
            return self.close_conn('too many connections.')
        if  not self.ipcheck(self.ip):
            return self.close_conn('Permission denied.')
            
        log.info("%s conn in. count %s" % (self.ip,self.factory.conn_count))
  
    def dataReceived(self,data):
        data=comm_lib.unpack_sock_data(data)
        if data.get('d_type') == 0:
            if len(str(data['data'])) < 1024:
                log.info("twisted get str %s" % data['data'])
            else:
                log.info("twisted get long str .hide it.")
                
        elif data.get('d_type') == 1:
            log.info("twisted get file %s" % data['filename'])
        else:
            log.err('twisted get scoket data err.')
            
        try:
            data=json.loads(data['data'])
        except:
            return
            
        if not data or str(data.get('data')) == '0':
            return
        data.update({'socket':self, 'selfip':self.ip})
        if self.ip == tornado_ip:
            data.update({'sktype':'tornado'})
        try:
            self.factory.data_analysis(data)
        except:
            log.err('lineno:' + str(sys._getframe().f_lineno)+": "+str(sys.exc_info()))

class server_factory(Factory, clien):
    protocol=server_protocol
    def __init__(self):
        self.db_info_data={}
        self.conn_count=int()
        self.connlist={}
        self.max_conn=10000
        self.buff=10485760
        self.task_list={}
        self.task_que=Queue.Queue(-1)
        self.client_pkg=curr_path+os.sep+'eagleclient.zip'
        self.socket_data_que=Queue.Queue(-1)
        self.socket_data_list={}
        self.status_level=[
            'done', 
            'success', 
            "ready", 
            "sending", 
            "sended", 
            "running", 
            "failed", 
            "cancel", 
            "offline", 
            'timeout', 
            'logininfoerr', 
            'filenotexists'
        ]
        self.task_done_status=[
            'done',
            "success", 
            'failed', 
            'timeout', 
            'logininfoerr', 
            "offline", 
            'filenotexists'
        ]
        self.task_type=['prepro', 'common']
        self.task_success=['success', 'done']
        self.task_failed=[
            "offline", 
            'failed', 
            'timeout', 
            'logininfoerr', 
            'filenotexists'
        ]
        self.task_callLater_list={}

    def data_analysis(self,data):
        request=data.get('request')
        if not request or not hasattr(self, request):
            #协议格式不对,断开链接
            comm_lib.send_socket_data(data.get('socket').transport.getHandle(), '-100')
            return data.get('socket').transport.loseConnection()
        #无协议方法,断开链接
        if not callable(getattr(self, request)):
            comm_lib.send_socket_data(data.get('socket').transport.getHandle(), '-99')
            return data.get('socket').transport.loseConnection()
        #调用协议方法    
        d=threads.deferToThread(getattr(self, request), data)
        d.addCallback(self.request_done, request)
        d.addErrback(self.request_err_done, request)
        
    def request_err_done(self, reson, handle):
        log.info(reson)
        return log.err('%s handle err.' % handle)
        
    def request_done(self, reson, handle):
        return log.info('%s handle done.' % handle)

    def client_opertion(self, data):
        return self.clien_opertion(data)
        
    def serverinit(self, data):
        return self.clien_opertion(data)
   
    def do_logincheck(self,data):
        return self.clien_opertion(data)
    
    def do_task_create(self, data):
        return self.task_handle(data)
        
    def conn_check(self, ip):
        if self.connlist.get(ip):
            return True
        else:
            return False
            
    def task_single_restart(self, data):
        data.update({'dotype':'single_restart'})
        return self.exec_task(data)

    def task_log_response(self, data):
        skt=self.connlist.get(tornado_ip, {}).get(data.get('tornadofileno'))
        if tornado_ip not in self.connlist or not skt:
            return log.err('response task log failed,tornado server %s off line.' % tornado_ip)

        task_name=data.get('task_name')
        filename=data.get('filename')

        if data.get('download'):
            log.info('reponse task[%s - %s] log file patch to tornado %s' % (task_name, filename, tornado_ip))
            task_log_save=curr_path+os.sep+task_log_path+os.sep+data['task_name']+os.sep+os.path.split(filename)[1]+".log"
            comm_lib.backup_file(task_log_save)
            if comm_lib.write_file(task_log_save, data['response']):
                log.info('create task log file[%s] success' % task_log_save)
                response=task_log_save
            else:
                log.info('create task log file[%s] failed' % task_log_save)
                response='create task log file[%s] failed' % task_log_save
        else:
            log.info('reponse task[%s - %s] log to tornado %s' % (task_name, filename, tornado_ip))
            response={
                'response':data.get('response'),
                'logdone':data.get('logdone')
            }

        self.response_tornado('', skt.transport.getHandle(), response)
        if data.get('logdone') == 'yes':
            return skt.transport.loseConnection()

    def download_file_response(self, data):
        savefile=data.get('savefile')
        filedata=data.get('filedata')
        return comm_lib.write_file(savefile, filedata)
        
    def find_file_path_response(self, data):
        filelist=json.dumps(data.get('filelist'), ensure_ascii=False)
        id=data.get('serverid')
        c_user=data.get('c_user')
        return user_table.update_server_privilege(c_user, filelist=filelist, id=id)
        
    def serverprivilege_file_execute(self, data):
        data.update({'requesttype': 'file_execute'})
        return self.tornado_request_client(data)
        
    def serverprivilege_file_update(self, data):
        data.update({'requesttype': 'file_update'})
        return self.tornado_request_client(data)
        
    def tornado_request_client(self, data):
        ip=data.get('ip')
        file=data.get('file')
        role=data.get('role')
        serverid=data.get('serverid')
        c_user=data.get('c_user')
        requesttype=data.get('requesttype')
        id=data.get('id')
        save_file=data.get('save_file')
        file=data.get('file')
        skt=data.get('socket').transport.getHandle()
        
        if self.conn_check(ip):
            ret=0
        else:
            ret=-1
            
        if requesttype == 'download_file':
            savefile='file/client/'+str(ip)+os.sep+re.sub(r'/+', '_', file)
            if os.path.exists(savefile):
                comm_lib.backup_file(savefile)
            cmd={
                'type':'download_file',
                'savefile':savefile,
                'file':file
            }
            if ret != -1:
                ret=savefile
                
        elif requesttype == 'file_execute':
            cmd={
                'type':'file_execute',
                'file':file
            }
        elif requesttype == 'file_update':
            cmd=save_file
            
        elif requesttype == 'search_filelist':
            cmd={
                'type':'find_file_path',
                'serverid':serverid,
                'c_user':c_user,
                'role':role
            }

        self.response_tornado('', skt, ret)
        if requesttype == 'file_update':
            return self.send_data(ip, cmd, dest_path=file)
        else:
            return self.send_data(ip, cmd)
        
    def download_file(self, data):
        data.update({'requesttype': 'download_file'})
        return self.tornado_request_client(data)

    def search_server_privilege_filelist(self, data):
        data.update({'requesttype': 'search_filelist'})
        return self.tornado_request_client(data)
        
    def show_task_log(self, data):
        return self.do_task_log(data)
        
    def do_task_log(self, data):
        task_name=data.get('task_name')
        if not task_name:
            task_name=data.get('name')
        filename=data.get('filename')
        ip=data.get('ip')
        download=data.get('download')
        taskinfo=self.get_task_servers(task_name=task_name, ip=ip)
        modal=taskinfo.get(ip, {}).get('modal')
        file=os.path.split(filename)[1]
        log_file=curr_path+os.sep+'log/localhost'+os.sep+task_name+os.sep+ip+os.sep+file+'.log'
        logresponse={}
        if modal == 'no':
            logdata=''
            if not comm_lib.isexists(log_file):
                if not download:
                   logdata='log file[%s] is not exists' % log_file
                else:
                   logresponse='filenotexists'
            else:
                if not download:
                    with open(log_file, 'rb') as f:
                        logdata=json.dumps(f.readlines())
                else:
                    logresponse=log_file
            if logdata:
               logresponse.update({
                  'logdone':'yes',
                  'response':logdata
               })
            self.response_tornado('', data.get('socket').transport.getHandle(), logresponse)
            #modal为no时候不支持动态日志显示
            return data.get('socket').transport.loseConnection()
            
        elif modal == 'yes':
            if self.connlist.get(ip):
                data.update({
                    'tornadofileno':data.get('socket').transport.socket.fileno(),
                    'socket':'',
                    'type':'get_task_log',
                    'task_name':task_name
                })
                self.send_data(ip, data)
            else:
                if not download:
                    logresponse.update({
                        'logdone':'yes',
                        'response':'show log failed.%s off line.' % ip
                    })
                else:
                    logresponse='offline'
                self.response_tornado('', data.get('socket').transport.getHandle(),
                        logresponse)
                return data.get('socket').transport.loseConnection()
                
    def task_log_download(self, data):
        data.update({'download':'yes'})
        return self.do_task_log(data)
        
    def task_restart(self, data):
        data.update({'dotype':'restart'})
        return self.exec_task(data)
        
    def task_cancel(self, data):
        data.update({'dotype':'cancel'})
        return self.exec_task(data)
        
    def task_response(self, data):
        return self.do_client_response('taskexecute', data)
                    
    def do_task_infocollect(self, ip, template, data):
        verify_key=user_table.get_verify_key_info(name='verify_key')[0]['value']
        if isinstance(data, list) or isinstance(data, dict):
            data=json.dumps(data, ensure_ascii=False)
            
        url='''http://%s:%s/interface/add_informationcollect?ip=%s&template_id=%s&info=%s&verify_key=%s'''  % (tornado_ip, tornado_port, ip, template, data, verify_key)
        ret=json.loads(urllib2.urlopen(url))
        log.info(ret)
        
    def do_client_response(self, type, data):
        status_key={
            'filecheck':'send_state',
            'taskexecute':'task_status'
        }
        status=data.get(status_key[type])
        collecttemplate=data.get('collecttemplate')
        if status in self.task_success and collecttemplate:
            collectdata=data.get('collectdata')
            self.do_task_infocollect(data.get('selfip'), collecttemplate, collectdata)

        task=data.get('task_name')
        client=data.get('selfip')
        taskid=int(data.get('taskid'))
        tasktype=data.get('tasktype')
        modal='yes'
        dest_path=data.get('dest_path')
        return self.task_job_status_set(taskname=task, status=status, 
                    ip=client, modal=modal, file=dest_path, taskid=taskid, tasktype=tasktype)

    def file_data_check_response(self, data):
        return self.do_client_response('filecheck', data)

    def get_task_destpath(self, relevance_path, taskinfo):
        path=''
        task_path=curr_path+os.sep+'task'+os.sep+taskinfo.get('task_id')+os.sep
        if self.prepro_isslave(taskinfo):
            path=relevance_path+os.sep+os.path.split(taskinfo.get('preprofile'))[1]
        elif self.prepro_ismaster(taskinfo):
            path=task_path+taskinfo.get('filename').replace(task_path, '')
        else:
            path=relevance_path+os.sep+taskinfo.get('filename').replace(relevance_path, '')
    
        return re.sub(r'/+', '/', path)
    
    def do_get_task_info(self, type, historydata, taskinfo=None):
        relevance_id=historydata.get('relevance_id')
        task_name=historydata.get('task_name')
        relevance_info=historydata.get('task_info', {})
        if isinstance(relevance_info, list):
            relevance_info=relevance_info[0]

        path=relevance_info.get('relevance_path', '')
        relevanceinfo=relevance_info.get('task_list', {}).get('relevancelist', [])
        relevance_path=path.replace('/${relevance_id}/', '/'+relevance_id+'/').replace('/${task_name}/', '/'+task_name+'/')

        if type == 'getdestpath':
            return self.get_task_destpath(relevance_path, taskinfo)
        elif type == 'gettaskdata':
            return relevanceinfo

    def get_task_info(self, relevance):
        relevanceinfo= self.do_get_task_info('gettaskdata', relevance)
        alltask={
            'prepro':'',
            'task_info':[]
        }
        
        for i in relevanceinfo:
            relevance_path= self.do_get_task_info('getdestpath', relevance, taskinfo=i)
            if self.prepro_isslave(i):
                dinfo={'des':i.get('filename')}
                file_source=i.get('preprofile')
            elif self.prepro_ismaster(i):
                dinfo={'des':i.get('des')}
                file_source=relevance_path
            else:
                dinfo={'des':i.get('des')}
                file_source=curr_path+os.sep+'task/'+i.get('task_id')+os.sep+os.path.split(i.get('filename'))[1]

            dinfo.update({
                'status':'ready',
                'scope':i.get('scope'),
                'prepro':i.get('preprotype'),
                'file_source':file_source
            })
            tinfo={relevance_path:dinfo}    
            if self.prepro_ismaster(i):
                alltask['prepro']=tinfo
                #del relevanceinfo[relevanceinfo.index(i)]
            elif tinfo not in alltask['task_info']:
                alltask['task_info'].append(tinfo)
                
        return alltask
        
    def task_handle(self, data):
        '''
        任务详情信息入库;
        任务主机信息检查,client状态(modal为yes)和/服务器登录信息(modal为no);
        添加任务信息到任务队列;
        '''
        self.response_tornado('', data.get('socket').transport.getHandle(), '0')
        #modal为no的ip信息
        iplist=data.get('iplist')
        #modal为no的ip登录信息
        logininfo=data.get('logininfo')
        #所有主机信息,包含modal为yes和no的服务器
        groupinfo=data.get('groupinfo')
        dotype=data.get('dotype', '')
        c_user=data.get('c_user')
        task_name=data.get('task_name')
        exectime=data.get('data', {}).get('executetime')
        self.inform_user('[info]:%s create task %s, it will be call in %s;' % (c_user, task_name, exectime))
        
        task_info=self.get_task_info(data)
        #若有预处理任务先存下来
        if task_info.get('prepro'):
            user_table.add_task_servers_history(c_user, task_name=task_name, telecom_ip='localhost', modal='no', 
                        task_info=json.dumps(task_info.get('prepro'), ensure_ascii=False))
                        
        #开线程检查, modal为no检查登录信息,为yes检查客户端状态,若检查失败则发送邮件/微信
        d=threads.deferToThread(self.client_check_and_inform, data)
        d.addErrback(self.defer_show_expect)
        for i in groupinfo:
            ip=i.get('member')
            group_id=i.get('group_id')
            modal=i.get('modal')
            server_key=i.get('server_key')
            asset_app=i.get('asset_app')
            login=logininfo.get(ip)
            taskinfo=task_info['task_info']
            #根据执行范围过滤任务
            new_taskinfo=[]

            for k in taskinfo:
                task=k.keys()[0]
                scope=k[task].get('scope')
                if scope in ['all', asset_app]:
                   new_taskinfo.append(k)

            user_table.add_task_servers_history(c_user, task_name=task_name, telecom_ip=ip, 
                        modal=modal, login_info=json.dumps(login, ensure_ascii=False), group_id=group_id, 
                        task_info=json.dumps(new_taskinfo, ensure_ascii=False), asset_app=asset_app,
                        server_key=json.dumps(server_key, ensure_ascii=False))
        #添加任务到队列
        task={
            'task_name':task_name,
            'dotype':dotype
        }
        log.info('add task[%s] to que.' % task)
        self.task_que.put(task)

    def send_data_to_iplist(self, iplist, data, dest_path=None):
        #发送数据到多个ip时候使用
        if isinstance(iplist, list) or isinstance(iplist, tuple):
            ip=tuple(iplist)
        return self.send_data(ip, data, dest_path=dest_path)

    def send_data(self, ip, data, dest_path=None):
        self.socket_data_list.setdefault(ip, {})
        self.socket_data_list[ip].setdefault('data_que', Queue.Queue(-1))
        self.socket_data_list[ip].setdefault('lock', threading.Lock())
        self.socket_data_list[ip]['data_que'].put((data, dest_path))
        self.socket_data_que.put(ip)

    def do_send_data(self,ip,data,dest_path=None):
        ret={}
        def send_data_to_ip(**kws):
            dt=kws.get('dt')
            iip=kws.get('ip')
            type=kws.get('type')
            destpath=kws.get('filepath')
            id=kws.get('id')
            ipret=ret.get(iip)
            if self.conn_check(iip):
                comm_lib.send_socket_data(self.connlist[iip].transport.getHandle(), dt, 
                            data_type=type, dest_path=destpath, id=id)
                if  not ipret:
                    ipret='success'

                if  destpath:
                    log.info("send %s[%s]  %sbytes to %s done." % (type, destpath, len(dt), iip))
                else:
                    log.info("send %s  %s to %s done." % (type, dt, iip))
                    
            else:
                ipret='offline'
                if destpath:
                    d=destpath
                else:
                    d=dt
                log.err("%s off line. skip %s[%s] send." % (iip, type, d))
            ret.update({iip: ipret})    
            return ret    
        
        if isinstance(data,dict) or isinstance(data,list) or isinstance(data,tuple):
            data=json.dumps(data)

        if isinstance(dest_path,unicode):
            dest_path=str(dest_path)

        if dest_path:
            if not dest_path:
                dest_path=client_deploy_path+os.sep+"file"+os.sep+data.split(os.sep)[-1]
                log.warn('dest path is None.it will be save to default path.')
            if not os.path.exists(data):
                log.err('source file path %s is not exists. skip send.' % data)
                return {ip:'filenotexists'}

            data_type='file'
            with open(data,'rb') as f:
                #用于客户端标示处理文件,0为第一次发送(客户端若存在相同文件则备份),1为直接写文件
                id=0
                while 1:
                    d=f.read(self.buff)
                    if d:
                        if isinstance(ip, list) or isinstance(ip, tuple):
                            ip=list(ip)
                            for i_p in ip:
                                thisret=send_data_to_ip(dt=d, ip=i_p, 
                                            type=data_type, filepath=dest_path, id=id)
                                if thisret.get(i_p) == "failed":
                                    continue
                                id=1
                        else:
                            thisret=send_data_to_ip(dt=d, ip=ip, 
                                        type=data_type, filepath=dest_path, id=id)
                            if thisret.get(ip) == "success":
                                id=1
                    else:
                        break
        else:
            data_type='str'
            if isinstance(ip, list) or isinstance(ip, tuple):
                for iip in list(ip):
                    send_data_to_ip(dt=data, ip=iip, type=data_type)
            else:
                #为字符串
                send_data_to_ip(dt=data, ip=ip, type=data_type)
        return ret
    
    def do_db_get_method(self, key, *args, **kws):
        db_obj=self.db_info_data.get(key)
        info=getattr(user_table, db_obj)(*args, **kws)
        for i in info:
            for k in i.keys():
                i.update({k:comm_lib.json_to_obj(i[k])})
        if not info:
            info=[{}]
        return info
    
    def get_task_time_cmp(self, exectime):
        '''获取当前系统时间和数据库时间差,单位为s'''
        if re.match(r'^00.*$', exectime):
            return 0
        sys_time=comm_lib.to_datetime_obj(str(datetime.datetime.now()).split('.')[0])
        ex_time=comm_lib.to_datetime_obj(exectime)
        time_cmp=int(str((ex_time - sys_time).total_seconds()).split('.')[0])
        return time_cmp

    def task_prepro_check(self, preprotask, time_cmp, taskname, exectimetype=None):
        prepro=preprotask.get('prepro')
        preprotype=preprotask.get('preprotype')
        #单位为分
        preprotime=int(preprotask.get('preprotime', 0)) * 60
        errinfo=''
        if not prepro:
            errinfo='task[%s] prepro err.' % taskname
        elif preprotype != "master":
            errinfo='task[%s] preprotype err. it is must be master.' % taskname
        elif not preprotime:
            errinfo='task[%s] preprotime is none.can not do prepro task.' % taskname
        elif time_cmp > preprotime or exectimetype == 'yes':
            #不到执行时间
            errinfo='fature'
            
        return errinfo
            
    def task_status_check(self, status, dotype, isprepro):
        errkey=''
        if dotype == "run" and (status != 'ready' and isprepro == 'no'):
            errkey='ready'
        elif dotype == 'cancel' and status != 'cancel':
            errkey='cancel'
        elif dotype == 'restart' and (status != 'ready' and isprepro == 'no'):
            errkey='ready'
            
        return errkey
        
    def get_task_history(self, task_name):
        self.db_info_data['task_history']='get_task_history'
        return self.do_db_get_method('task_history', task_name=task_name)[0]

    def get_task_servers(self, **kws):
        task_name=kws.get('task_name')
        ip=kws.get('ip')
        self.db_info_data['taskservers']='get_task_servers_info'
        taskdetail=self.do_db_get_method('taskservers', task_name=task_name, telecom_ip=ip)
        return { i.get('telecom_ip'):i for i in taskdetail}

    def isnot_prepro(self, task):
        if task.get('prepro') != 'yes':
            return True
        else:
            return False
            
    def prepro_ismaster(self, task):
        if task.get('prepro') == 'yes' and task.get('preprotype') == 'master':
            return True
        else:
            return False
        
    def prepro_isslave(self, task):
        if task.get('prepro') == 'yes' and task.get('preprotype') == 'slave':
            return True
        else:
            return False
        
    def find_task_info(self, history, servers, type=None, taskfile=None, skipsuccess=None, status='ready'):
        task_list={ i.get('filename'):i for i in self.get_task_list(history) }
        historystatus=history.get('status')
        taskname=history.get('task_name')
        task_info={}
        for k,v in servers.iteritems():
            ip=k
            modal=v.get('modal')
            task=v.get('task_info')
            logininfo=v.get('login_info')
            if ip != 'localhost':
                for t in task:
                    tf=t.keys()[0]
                    tstate=t.get(t.keys()[0])['status']
                    file_source=t.get(t.keys()[0])['file_source']
                    filename=t.keys()[0]
                    if taskfile and filename != taskfile:
                        continue
                        
                    if skipsuccess == 'yes' and tstate in self.task_success:
                        log.info('task[%s]->%s was already %s, skip' % (taskname, filename, tstate))
                        continue
                         
                    tf_detail= task_list.get(tf)
                    id=int(tf_detail.get('id'))
                    #获取 prepro salve任务和非prepro salve任务,默认获取ready状态的任务
                    if type == 'preproslave':
                        ret=self.prepro_isslave(tf_detail)
                    else:
                        ret=self.isnot_prepro(tf_detail)

                    if ret:
                        if tstate != status and historystatus != 'ready':
                            continue

                        tf_detail.update({'file_source':file_source})
                        if id not in task_info.keys():
                            tf_detail.update({
                                'iplist':{
                                    modal:{
                                        ip:{
                                            'status':tstate,
                                            'logininfo':logininfo
                                        }
                                    }
                                }
                            })
                            task_info[id]=tf_detail
                        else:
                            task_info[id].setdefault('iplist', {})
                            task_info[id]['iplist'].setdefault(modal, {})
                            task_info[id]['iplist'][modal][ip]={
                                            'status':tstate,
                                            'logininfo':logininfo
                                        }

        return task_info

    def get_task_list(self, historydata):
        relevance_info=historydata.get('task_info', {})
        task_list=relevance_info.get('task_list', {}).get('relevancelist', [{}])
        for i in task_list:
            i.update({'filename':self.do_get_task_info('getdestpath', historydata, taskinfo=i)})

        return task_list
    
    def task_localhost_log_create(self, taskname, filename, id, data):
        filename=os.path.split(filename)[1]
        lgph=curr_path+os.sep+'log/localhost'+os.sep+taskname+os.sep+id+os.sep+filename+'.log'
        log.warn(data)
        return comm_lib.write_file(lgph, data, overwrite=True)
        
    def do_prepro_task(self, history, servers, dotype, skipsuccess=None):
        task_info=servers.get('localhost').get('task_info', {})
        prepro=task_info.keys()[0]
        parameters=history.get('parameters', {})
        prepro_slave=self.find_task_info(history, servers, type="preproslave", skipsuccess=skipsuccess)

        task_name=history.get('task_name') 
        rely=history.get('task_info', {}).get('relevance_rely')
        if not prepro or not comm_lib.isexists(prepro):
            if not comm_lib.isexists(prepro):
                log.err('task[%s] prepro file[%s] is not exists.' % (task_name, prepro))
            return False
            
        status=task_info[prepro].get('status')
        if skipsuccess == 'no' or status not in self.task_success:
            task_info[prepro].update({'status':'running'})   
            user_table.task_servers_status_update(task_name, json.dumps(task_info, ensure_ascii=False), 'localhost')
        
            cmd='chmod a+x %s;%s  %s' % (prepro, prepro, ' '.join([ parameters[k] for k in sorted(parameters.keys())]))
            ret, detail=commands.getstatusoutput(cmd)
            if ret >> 8 != 0:
                status='failed'
            else:
                status='success'
            
            self.task_localhost_log_create(task_name, prepro, 'localhost', detail)    
            task_info[prepro].update({'status':status})
            user_table.task_servers_status_update(task_name, json.dumps(task_info, ensure_ascii=False), 'localhost')
            log.warn('task[%s] execute prepro cmd[%s] %s.' % (task_name, cmd, status))
            if status == 'failed':
                return False
        
        #防止重复执行
        if not self.task_list.get(task_name) and prepro_slave:
            self.task_job_add('prepro', dotype, task_name, rely, prepro_slave, skipsuccess=skipsuccess)
        elif not prepro_slave:
	    log.warn('task[%s] can not find anly prepro slave, skip.' % task_name)
        return True
        
    def do_task_stop_onclient(self, taskname):
        log.info('task[%s] begin to stop on client.' % taskname)
        taskdata=self.task_list.get(taskname, {})
        for tp in self.task_type:
            for id in taskdata.get(tp, {}):
                task=taskdata.get(tp, {}).get(id, {})
                iplist=task.get('iplist', {})
                isexcute=task.get('isexcute')
                collecttemplate=task.get('collecttemplate')
                dest_path=task.get('filename')
                for md in iplist:
                    info=iplist.get(md, {})
                    for ip in iplist.get(md, {}):
                        status=info[ip].get('status')
                        loginfo=info[ip].get('loginfo')
                        if status not in self.task_done_status:
                            if md == 'yes':
                                cmd={
                                    'type':'obj_execute',
                                    'is_exec':isexcute,
                                    'taskid':id,
                                    'tasktype':tp,
                                    'collecttemplate':collecttemplate,
                                    'dest_path':dest_path,
                                    'task_name':taskname,
                                    'object':dest_path,
                                    'dotype':'cancel'
                                }
                                self.send_data(ip, cmd)
                            elif md == "no":
                                d=threads.deferToThread(self.call_task_by_ssh, taskname=taskname,
                                                        task=task, ip=ip, runtype='stop')
                                d.addErrback(self.defer_show_expect)
                            
    def do_single_restart(self, taskdata):
        taskname=taskdata.get('task_name')
        filename=taskdata.get('filename')
        ip=taskdata.get('ip')
        task_history=self.get_task_history(task_name=taskname)
        servers_history=self.get_task_servers(task_name=taskname, ip=ip)
        taskinfo=self.find_task_info(task_history, servers_history, taskfile=filename)
        modal=servers_history.get(ip, {}).get('modal')
        for id in taskinfo:
            isexcute=taskinfo[id].get('isexcute')
            dest_path=taskinfo[id].get('filename')
            collecttemplate=taskinfo[id].get('collecttemplate')
            prepro=taskinfo[id].get('prepro')
            if prepro == 'yes':
                tp='prepro'
            else:
                tp='common'
            if modal == 'yes':
                cmd={
                    'type':'obj_execute',
                    'is_exec':isexcute,
                    'taskid':id,
                    'tasktype':tp,
                    'collecttemplate':collecttemplate,
                    'dest_path':dest_path,
                    'task_name':taskname,
                    'object':dest_path,
                    'dotype':'restart'
                }
                self.send_data(ip, cmd)
            elif modal == "no":
                d=threads.deferToThread(self.call_task_by_ssh, taskname=taskname,
                                        task=task, ip=ip, runtype='stop')
                d.addErrback(self.defer_show_expect)
        
    def exec_task(self, taskdata):
        taskname=taskdata.get('task_name')
        runtype=taskdata.get('dotype')
        exectimetype=taskdata.get('exectimetype')
        log.info('task[%s] do %s begin.' % (taskname, runtype))
        if runtype in ["restart", 'single_restart', 'cancel']:
            self.response_tornado('', taskdata.get('socket').transport.getHandle(), '0')
            if self.task_callLater_list.get(taskname):
                #还没执行任务,停止计划任务
                self.task_callLater_cancel(taskname)

            if self.task_list.get(taskname) and runtype == 'cancel':
                #取消任务
                return do_task_stop_onclient(taskname)

            elif runtype == "restart":
                #重新执行
                taskdata.update({'dotype':'run'})
                self.delete_empty(self.task_list, taskname)
                return self.exec_task(taskdata)
                
            elif runtype == "single_restart":
                #直接到对应服务器执行
                return self.do_single_restart(taskdata)
        else:
            #30秒运行一次,检查时间不过则继续等待
            self.calltasktime=15
            self.do_exec_task(taskdata)

    def task_callLater_cancel(self, taskname):
        fn=self.task_callLater_list.get(taskname)
        try:
            fn.cancel()
        except:
            pass
            
        self.delete_empty(self.task_callLater_list, taskname)
        
    def task_callLater_start(self, taskname, fn, deley, *args, **kws):
        id=reactor.callLater(deley, fn, *args, **kws)
        self.task_callLater_list[taskname]=id

    def do_exec_task(self, taskdata):
        '''执行任务前检查;调用任务参数设置函数'''
        taskname=taskdata.get('task_name')
        dotype=taskdata.get('dotype')
        skipsuccess=taskdata.get('skipsuccess', 'yes')
        exectimetype=taskdata.get('exectimetype')
        taskhistory=self.get_task_history(taskname)
        status=taskhistory.get('status')
        isprepro=taskhistory.get('isprepro')
        relevance=taskhistory.get('task_info', {})
        task_info=self.get_task_list(taskhistory)
        execute_time=taskhistory.get('execute_time', '')
        time_cmp=self.get_task_time_cmp(execute_time)
        servers_history=self.get_task_servers(task_name=taskname)

        self.task_callLater_cancel(taskname)
        if  isprepro == 'yes' and dotype == 'run':
            errinfo=self.task_prepro_check(task_info[0], time_cmp, taskname, exectimetype=exectimetype)
            if errinfo != 'fature' and errinfo:
                return log.err(errinfo)
            elif errinfo == 'fature' and not exectimetype:
                #不到执行时间, 启动延时任务
                return self.task_callLater_start(taskname, self.do_exec_task, self.calltasktime, taskdata)

            elif not self.do_prepro_task(taskhistory, servers_history, dotype, skipsuccess=skipsuccess):
                #执行预处理任务失败
                return log.err('task[%s] prepro failed.skip it.' % taskname)
     
        prepro_status=self.task_list.get(taskname, {}).get('prepro_status', {}).get('status')
        if  isprepro == 'yes'  and (prepro_status and prepro_status not in self.task_success):
            #阻塞执行预处理任务, 启动延时任务
            return self.task_callLater_start(taskname, self.do_exec_task, self.calltasktime, taskdata)

        errkey=self.task_status_check(status, dotype, isprepro)
        if  errkey:
            return log.err('task[%s] %s failed. status shuld be %s not %s.' % (
                                taskname, dotype, errkey, status))

        if  (time_cmp <= 30 and time_cmp >= -30) or  exectimetype == 'yes':
            log.info('run task[%s] begin.' % taskname)
            self.task_callLater_cancel(taskname)
        else:
            #不到执行时间, 启动延时任务
            return self.task_callLater_start(taskname, self.do_exec_task, self.calltasktime, taskdata)

        #处理任务信息添加到任务执行队列，不处理预处理任务信息,预处理在do_prepro_task
        common_task=self.find_task_info(taskhistory, servers_history, skipsuccess=skipsuccess)
        if self.prepro_failed(taskname):
            return log.err('task[%s] prepro execute failed. so skip common task.' % taskname)
        elif not common_task:
            log.warn('task[%s] can not find common task.' % taskname)
            self.delete_empty(self.task_list, taskname)
            user_table.update_task_history_status_for_twisted('success', taskname)
            self.inform_user('[info:]task[%s] call done. it is can not find common.' % taskname)
        else:
            rely=relevance.get('relevance_rely')
            self.task_job_add('common', dotype, taskname, rely, common_task, skipsuccess=skipsuccess)
        
    def prepro_failed(self, taskname):
        status=self.task_list.get(taskname, {}).get('prepro_status', {}).get('status')
        if status in self.task_failed:
            return True
        else:
            return False
        
    def update_task_status_in_db(self, **kws):
        '''修改对应任务指定任务文件执行状态'''
        taskname=kws.get('taskname')
        taskinfodata=kws.get('task_info')
        ip=kws.get('ip')
        status=kws.get('status')
        filename=kws.get('filename')
        onlyserver=kws.get('onlyserver')

        self.db_info_data['task_history']='get_task_history'
        taskhistory=self.do_db_get_method('task_history', task_name=taskname)
        if not taskhistory:
            return log.err('can not find task[%s] history.' % taskname)
            
        historystatus=taskhistory[0].get('status')
        if not isinstance(taskinfodata, list):
            taskinfodata=[taskinfodata]
            
        h_num=self.status_level.index(historystatus)
        t_num=self.status_level.index(status)
        if t_num > h_num or status in self.task_done_status:
            md=False
            if status in self.task_done_status and historystatus in self.task_done_status:
               if self.task_done_status.index(status) > self.task_done_status.index(historystatus):
                  md=True
            else:
               md=True      
            if md:
               historystatus=status

        for i in taskinfodata:
            for k,v in i.items():
                preprotype=v.get('prepro')
                #有文件则修改对应任务状态,否则修改当前ip全部任务状态
                #filename为文件推送路径
                if filename and k != filename:
                    continue
                
                tstatus=v.get('status')
                h_num=self.status_level.index(status)
                t_num=self.status_level.index(tstatus)
                if  t_num < h_num:
                    v.update({'status':status})
                    
        user_table.task_servers_status_update(taskname, json.dumps(taskinfodata, ensure_ascii=False), ip)
        if  historystatus != taskhistory[0].get('status') and not onlyserver:
            user_table.update_task_history_status_for_twisted(historystatus, taskname)
    
    def task_servers_clear(self, **kws):
        '''清理任务中执行失败的ip信息'''
        taskname=kws.get('taskname')
        tasktype=kws.get('tasktype')
        taskid=int(kws.get('taskid'))
        modal=kws.get('modal')
        filename=kws.get('filename')
        thisip=kws.get('ip')
        
        taskinfo=self.task_list.get(taskname, {}).get(tasktype, {}).get(taskid)
        if not taskinfo:
            return
        dotask_ip=taskinfo.get('dotask_ip', [])
        sendfile_iplist=taskinfo.get('sendfile_iplist', [])
        servers=taskinfo.get('iplist', {})

        for md in servers.keys():
            if modal and md != modal:
                continue

            iplist=servers.get(md, {})
            iplist_temp={ k:v for k,v in iplist.iteritems() }
            for ip in  iplist_temp.keys():
                status=thisip.get(ip)
                if status in self.task_failed:
                    for l in [sendfile_iplist, dotask_ip]:
                        if ip in l:
                            index=l.index(ip)
                            if index != -1:
                                del l[index]
                    self.task_db_status_check(ip, status, taskname, filename=filename)            
                    if status in self.task_done_status:
                        self.delete_done_servers(taskname=taskname, status=status, tip=ip, 
                                            modal=md, tasktype=tasktype, taskid=taskid)
                    else:
                        self.delete_empty(iplist, ip)

    def task_servers_clear_forclient(self, ret):
        '''清理任务中modal为yes发送数据offline的ip信息'''
        if not ret:
            return
            
        for task in self.task_list.keys():
            for tasktype in  self.task_list.get(task, {}):
                if tasktype not in self.task_type:
                    continue 
                if not isinstance(self.task_list.get(task, {}).get(tasktype, {}), dict):
                    continue
                tidlist=self.task_list.get(task, {}).get(tasktype, {})
                tidlist_temp={ k:v for k,v in tidlist.items()}
                for tid in tidlist_temp:
                    self.task_servers_clear(taskname=task, tasktype=tasktype, taskid=tid, ip=ret)
                    
    def delete_empty(self, data, key, check=False):
        try:
            if check and not data.get(key):
                del data[key]
            elif not check:
                del data[key]
        except:
            pass
            
    def all_server_done(self, taskname, tasktype):
        info=self.task_list.get(taskname, {}).get(tasktype, {})
        for id in info:
            iplist=info.get(id, {}).get('iplist')
            for md in  iplist.keys():
                server=iplist.get(md, {})
                for ip in server:
                    status=server.get(ip, {}).get('status')
                    if status and status not in self.task_done_status:
                        return False
        return True
    
    def delete_done_servers(self, **kws):
        '''已经完成的任务信息从iplist里清理ip，当前任务为最后一个时候task_list 里清理掉任务信息'''
        #此方法在任务执行/推送后需要调用
        taskname=kws.get('taskname')
        status=kws.get('status')
        taskid=int(kws.get('taskid'))
        tasktype=kws.get('tasktype')
        tip=kws.get('tip')
        modal=kws.get('modal')
        if status not in self.task_done_status:
            return 
            
        taskdata=self.task_list.get(taskname, {}).get(tasktype, {})
        taskinfo=taskdata.get(taskid, {})
        dest_path=taskinfo.get('filename')
        iplist=taskinfo.get('iplist', {}).get(modal, {})

        if tasktype == 'prepro':
            self.task_list[taskname]['prepro_status']['filelist'].setdefault(dest_path, {})
            self.task_list[taskname]['prepro_status']['filelist'][dest_path].update({tip:status})

        self.task_list[taskname]['prev_status'].setdefault(dest_path, {})
        self.task_list[taskname]['prev_status'].update({tip:status})
        log.info('task[%s]->%s->%s call done.it is  %s, clear it.' % (taskname, dest_path, tip, status))
        self.delete_empty(iplist, tip)
        
        self.delete_empty(taskinfo['iplist'], modal, check=True)
        #最后一个任务执行完成后清理任务
        if self.islast_task(taskname, tasktype, taskid
            ) and self.all_server_done(taskname, tasktype):
            if tasktype == 'prepro':
                log.info('task[%s] prepro call done.' % taskname)
                self.task_list[taskname]['prepro_status'].update({'status':'done'})
            else:
                log.info('task[%s] call done. clear it.' % taskname)
                self.inform_user('[info:]task[%s] call done, it is %s.' % (taskname, status))
                self.delete_empty(self.task_list, taskname)
            
    def task_job_status_set(self, **kws):
        taskname=kws.get('taskname')
        status=kws.get('status')
        taskid=int(kws.get('taskid'))
        tasktype=kws.get('tasktype')
        ip=kws.get('ip')
        modal=kws.get('modal')
        filename=kws.get('file')
        taskinfo=self.task_list.get(taskname, {}).get(tasktype, {}).get(taskid, {})
        file_source=taskinfo.get('file_source')
        dest_path=taskinfo.get('filename')
        isexcute=taskinfo.get('isexcute')
        iplist=taskinfo.get('iplist', {}).get(modal, {})

        for tip in  iplist.keys():
            if tip == ip:
                if str(status) == '-1':
                    #文件不存在,重新发送
                    log.info('task[%s]->%s is not exists on %s. send it again.' % (taskname, dest_path, tip))
                    status='ready'
                    self.send_data(tip, file_source, dest_path=dest_path)
                elif str(status) == '2':
                    #文件接收完成,可以进行下一步处理
                    if not self.conn_check(ip):
                        status='offline'
                    elif isexcute != "yes":
                        status='success'
                    else:
                        status='sended'

                iplist[tip].update({'status':status})
                h_num=self.status_level.index(iplist[tip]['status'])
                t_num=self.status_level.index(status)

                if  t_num >= h_num:
                    taskinfo['status']=status

                self.delete_done_servers(taskname=taskname, status=status, tip=ip, 
                                modal=modal, tasktype=tasktype, taskid=taskid)

        return  self.task_db_status_check(ip, status, taskname, filename=filename)
        
    def task_db_status_check(self, ip, status, taskname, filename=None, onlyserver=False):
        #修改数据库状态         
        if  status in self.status_level:
            self.db_info_data['taskservers']='get_task_servers_info'
            servershistory=self.do_db_get_method('taskservers', task_name=taskname)
            if not servershistory:
                return log.info('can not find task[%s] servers history.' % taskname)
            this_server=[ i.get('task_info') for i in servershistory if i.get('telecom_ip') == ip ]
            if not this_server:
                return log.info('can not find task[%s] servers[%s] history.' % (taskname, ip))
            if isinstance(this_server[0], list):
                this_server=this_server[0]
            return self.update_task_status_in_db(taskname=taskname, task_info=this_server, ip=ip,
                                                    status=status, filename=filename, onlyserver=onlyserver)

    def task_job_add(self, type, dotype, taskname, rely, taskdata, skipsuccess=None):
        #负责设置任务信息,由计划任务进行检查和执行
        #任务执行/restart时候默认跳过状态为success的任务
        log.info('task[%s] %s add to que.' % (taskname, type))
        self.task_list.setdefault(taskname, {})
        if type == 'prepro':
            #存放预处理任务执行状态
            self.task_list[taskname].setdefault('prepro_status', {})
            self.task_list[taskname]['prepro_status'].setdefault('status', 'ready')
            self.task_list[taskname]['prepro_status'].setdefault('filelist', {})
        #存放任务ip上一步任务执行状态,若上一步骤失败,当前ip通过任务执行
        self.task_list[taskname].setdefault('prev_status', {})
        self.task_list[taskname].setdefault(type, taskdata)
        self.task_list[taskname].setdefault('skip_success', skipsuccess)
        self.task_list[taskname].setdefault('rely', rely)
        self.task_list[taskname].setdefault('dotype', dotype)
        user_table.update_task_history_status_for_twisted('running', taskname)
        print self.task_list
        
    def thread_to_send_data(self,ip):
        if self.socket_data_list.get(ip):
            ret=False
            try:
                ret=self.socket_data_list[ip]['lock'].acquire(False)
                if not ret:
                    return self.socket_data_que.put(ip)
                while 1:
                    if self.socket_data_list[ip]['data_que'].empty():
                        return self.socket_data_que.put(ip)
                    else:
                        data, dest_path=self.socket_data_list[ip]['data_que'].get()
                        ret=self.do_send_data(ip, data, dest_path=dest_path)
                        err_ret={ k:v for k,v in ret.iteritems() if v == 'offline' }
                        self.task_servers_clear_forclient(err_ret)
            finally:
                if ret:
                    self.socket_data_list[ip]['lock'].release()
                    self.delete_empty(self.socket_data_list, ip)

    def defer_show_expect(self, reson):
        log.err(reson)
        
    def thread_to_check_socket_data(self):
        while 1:
            ip=self.socket_data_que.get()
            if ip and self.socket_data_list.get(ip):
                if not self.socket_data_list[ip]['lock'].locked():
                    d=threads.deferToThread(self.thread_to_send_data, ip)
                    d.addErrback(self.defer_show_expect)
            time.sleep(0.1)
            
    def check_socket_data(self):
        t=threading.Thread(target=self.thread_to_check_socket_data)
        t.setDaemon(True)
        t.start()
        
    def call_task_by_socket(self, **kws):
        taskname=kws.get('taskname')
        task=kws.get('task')
        modal=kws.get('modal')
        servers=task.get('iplist', {}).get(modal)
        isexcute=task.get('isexcute')
        taskfile=task.get('file_source')
        tasktype=task.get('tasktype')
        taskid=int(task.get('id'))
        dest_path=task.get('filename')
        
        file_filterkey=['ready', 'prevfailed']
        task_filterkey=['success', 'done', 'running', 'prevfailed']
        sendfile_iplist=[]
        dotask_ip=[]
        servers_temp={ k:v for k,v in servers.iteritems() }
        for ip in servers_temp:
            if not self.prev_task_check(taskname, tasktype, taskid, ip, modal):
                continue

            #任务ip状态在file_filterkey跳过发送文件
            if servers_temp[ip].get('status') in file_filterkey:
                sendfile_iplist.append(ip)
            #任务ip状态在task_filterkey跳过执行任务
            if servers_temp[ip].get('status') not in task_filterkey:
                dotask_ip.append(ip)

        task.update({
            'sendfile_iplist':sendfile_iplist,
            'dotask_ip':dotask_ip
        })
        #修改任务ip状态
        if sendfile_iplist  or dotask_ip:
            s='sending'
            { servers[ip].update({'status':s}) for ip in sendfile_iplist }
            self.task_status_update(task, s)
            if sendfile_iplist:
               self.send_data_to_iplist(sendfile_iplist, taskfile, dest_path=dest_path)
        #修改状态为sended, 当dotask_ip不在sendfile_iplist里时
        { servers[ip].update({'status':'sended'}) for ip in dotask_ip if ip not in sendfile_iplist }
        #不在这调用,检查里执行 task_exec_status_check

    def task_status_update(self, taskinfo, status):
        hstatus=taskinfo.get('status')
        if not hstatus:
            taskinfo.update({'status':status})
        elif self.status_level.index(status) > self.status_level.index(hstatus):
            taskinfo.update({'status':status})
            
    def call_task_by_ssh(self, **kws):
        taskname=kws.get('taskname')
        task=kws.get('task')
        taskfile=task.get('file_source')
        dest_file=task.get('filename')
        ip=kws.get('ip')
        isexcute=task.get('isexcute')
        tasktype=task.get('tasktype')
        dotype=task.get('exectype')
        taskid=int(task.get('id'))
        runtype=kws.get('runtype')
        collecttemplate=kws.get('collecttemplate')
        modal='no'
        serverinfo=task.get('iplist', {}).get(modal, {}).get(ip, {})
        loginfo=serverinfo.get('logininfo')
        status=serverinfo.get('status')
        if status != 'ready':
            return
            
        if serverinfo: serverinfo.update({'status':'running'})
        self.task_status_update(task, 'running')
        if not loginfo:
            err_info='task file[%s] execute failed on %s,logininfo err.' % (dest_file, ip)
            self.task_localhost_log_create(taskname, taskfile, ip, err_info)
            return self.task_servers_clear(taskname=taskname, tasktype=tasktype, modal=modal, 
                                taskid=taskid, ip={ip:'logininfoerr'}, filename=dest_file)

        timeout=int()
        for i in range(0,3):
            loginfo.update({'ip':ip})
            login= self.get_login(loginfo)
            if runtype == 'stop':
                cmd='''ps aux|grep %s|grep -v grep|awk '{print "kill -9 $2"}'|bash & ''' % dest_file
                ret, detail=server_comm.ssh(ip, login['port'], login['user'], login['pwd'], cmd=cmd)
            else:
                ret, detail=server_comm.ssh(ip, login['port'], login['user'], login['pwd'], 
                        file=taskfile, isexcute=isexcute, dest_file=dest_file)
            if detail != 'TIMEOUT':
                if not ret:
                    status='failed'
                else:
                    status='success'
                self.task_localhost_log_create(taskname, taskfile, ip, detail)
                break;
            else:
                status='timeout'
        if  status in ['success', 'failed'] and collecttemplate:
            self.do_task_infocollect(ip, collecttemplate, detail)
            
        log.info('task file[%s] execute %s on %s.' % (dest_file, status, ip))
        return self.task_servers_clear(taskname=taskname, tasktype=tasktype, taskid=taskid, modal=modal,
                                    ip={ip:status}, filename=dest_file)

    def get_task_place(self, taskname, tasktype, tid, type=None):
        info=self.task_list.get(taskname, {}).get(tasktype, {})
        if info:
            idlist=info.keys()
            if idlist:
                if idlist[-1] == tid and type == 'last':
                    return True
                elif idlist[0] == tid and type == 'frist':
                    return True
        return False
        
    def islast_task(self, taskname, tasktype, tid):
        return self.get_task_place(taskname, tasktype, tid, type='last')
        
    def isfrist_task(self, taskname, tasktype, tid):
        return self.get_task_place(taskname, tasktype, tid, type='frist')
    
    def server_prepro_failed(self, taskname, destfile, ip):
        info=self.task_list.get(taskname, {}).get('prepro_status', {}).get('filelist', {})
        status=info.get(destfile, {}).get(ip)
        if status in self.task_failed:
            return True
        else:
            return False

    def prev_task_check(self, taskname, tasktype, tid, ip, modal):
        #当前ip任务的  上一个任务没执行成功 则不执行当前任务
        task=self.task_list.get(taskname, {})
        taskinfo=task.get(tasktype, {})
        tkeys=sorted(taskinfo.keys())
        if not tkeys:
            return True
            
        prev_status=task.get('prev_status', {}).get(ip)
        if tkeys.index(int(tid)) == 0 and not prev_status:
            return True
            
        prev_id=tid - 1
        server=taskinfo.get(prev_id, {}).get('iplist', {}).get(modal, {}).get(ip, {})
        status=server.get('status')

        if (status and status not in self.task_success
            ) or ( prev_status and prev_status not in self.task_success):
            if prev_status and not status:
                status=prev_status
            elif prev_status and  status:
                if self.status_level.index(prev_status) > self.status_level.index(status):
                    status=prev_status
            if status:
                self.delete_done_servers(taskname=taskname, status=status, tip=ip, 
                        modal=modal, tasktype=tasktype, taskid=tid)
            return False
        else:
            return True
    
    def do_task(self, **kws):
        taskname=kws.get('taskname')
        task=kws.get('task')
        self.task_status_update(task, 'running')
        iplist=task.get('iplist')
        taskfile=task.get('file_source')
        tasktype=task.get('tasktype')
        dotype=task.get('exectype')
        taskid=int(task.get('id'))

        if not comm_lib.isexists(taskfile):
            task.update({'status':'filenotexists'})
            if self.isfrist_task(taskname, tasktype, taskid):
                log.err('task[%s]->[%s] is not exists. set it failed.' % (taskname, taskfile))
                self.delete_empty(self.task_list, taskname)
                return user_table.update_task_history_status_for_twisted('filenotexists', taskname)
        if not iplist:
            return 

        iplist_temp={ k:v for k,v in iplist.items() }
        for k in iplist_temp:
            #这里k为服务器modal
            if not iplist_temp.get(k):
                continue

            if k == 'yes':
                #采用请求client方式执行任务
                if not task.get('sendfile_iplist') and not task.get('dotask_ip'):
                    d=threads.deferToThread(self.call_task_by_socket, taskname=taskname, modal=k, task=task)
                    d.addErrback(self.defer_show_expect)
            elif k == "no":
                #pexcept/ssh方式执行任务
                iplist_tempa={ k:v for k,v in iplist_temp[k].iteritems() }
                for ip in iplist_tempa:
                    if not self.prev_task_check(taskname, tasktype, taskid, ip, k):
                        continue
                    d=threads.deferToThread(self.call_task_by_ssh, taskname=taskname,
                                            task=task, ip=ip)
                    d.addErrback(self.defer_show_expect)

    def task_exec_status_check(self, taskname, task):
        ret=True
        status=task.get('status')
        servers=task.get('iplist', {})
        dest_path=task.get('filename')
        isexcute=task.get('isexcute')
        file_source=task.get('file_source')
        taskid=int(task.get('id'))
        tasktype=task.get('tasktype')
        dotype=task.get('exectype')
        collecttemplate=task.get('collecttemplate')
        if status == 'ready':
            return ret

        for modal in servers:
            iplist=servers.get(modal)
            for ip in iplist:
                tstatus=iplist.get(ip).get('status')
                dotask_ip=task.get('dotask_ip', [])
                sendfile_iplist=task.get('sendfile_iplist', [])
                socket_locked=self.socket_data_list.get(tuple(sendfile_iplist), {}).get('lock')
                
                if socket_locked:
                    #还在发送数据
                    if socket_locked.locked():
                        continue

                if modal == 'yes':
                    cmd={
                        'type':'obj_execute',
                        'is_exec':isexcute,
                        'taskid':taskid,
                        'collecttemplate':collecttemplate,
                        'tasktype':tasktype,
                        'dest_path':dest_path,
                        'task_name':taskname
                    }
                     
                    if tstatus == 'sending' :
                        ret=False
                        #发送文件md5给client检查文件是否接收完成
                        md5=comm_lib.getmd5(file_source)
                        cmd.update({
                            'object':'file_data_check',
                            'md5':md5
                        })
                        self.send_data(ip, cmd)
                        
                    elif tstatus == 'sended' and dotask_ip and isexcute == 'yes':
                        ret=False
                        #发送命令给client执行任务文件
                        { iplist[ip].update({'status':'running'}) for tip in dotask_ip if ip == tip }
                        self.task_status_update(task, 'running')
                        cmd.update({
                            'object':dest_path,
                            'dotype':dotype
                        })

                        log.info('task[%s]->%s call on %s begin.' % (taskname, dest_path, ip))
                        self.send_data(ip, cmd)

        return ret
    
    def thread_to_check_task(self, taskname):
        '''若有预处理(prepro)任务则执行预处理任务,否则执行普通任务(common)'''
        taskinfo=self.task_list.get(taskname, {})
        prepro=taskinfo.get('prepro', {})
        common=taskinfo.get('common', {})
        rely=taskinfo.get('rely')
        exectype=taskinfo.get('dotype')
        prepro_status=taskinfo.get('prepro_status', {}).get('status')
        if prepro and prepro_status not in self.task_success:
            tasktype='prepro'
            taskdata=prepro
        else:
            taskdata=common
            tasktype='common'
            
        if not prepro and not common:
            return self.delete_empty(self.task_list, taskname)

        sorted_keys=sorted(taskdata.keys())
        #任务按id顺序执行
        #若rely为yes,则对上一个任务进行检查;检查失败就退出,即不执行后面的任务
        #若rely为no,当前任务不受上一个任务执行状态影响
        for id in sorted_keys: 
            task=taskdata[id]
            task.update({
                'tasktype':tasktype,
                'exectype':exectype
            })
            #状态不为ready,跳过
            check_ret=self.task_exec_status_check(taskname, task)
            if not check_ret:
                continue

            if rely != 'yes':
                d=threads.deferToThread(self.do_task, taskname=taskname, task=task)
                d.addErrback(self.defer_show_expect)
            else:
                #任务依赖模式
                if not self.task_obj_set(taskname, tasktype, id):
                    continue
                
                d=threads.deferToThread(self.do_task, taskname=taskname, task=task)
                d.addErrback(self.defer_show_expect)
                
    def task_obj_set(self, taskname, tasktype, tid):
        taskinfo=self.task_list.get(taskname, {})
        taskdata=taskinfo.get(tasktype, {})
        sorted_keys=sorted(taskdata.keys())
        failedgroup=[]
        statuscount=int()
        
        def do_group(des):
            for modal in iplist:
                servers=iplist.get(modal, {})
                for ip in servers:
                    state=servers.get(ip, {}).get('status')
                    groupid=servers.get(ip, {}).get('groupid')
                    if des == 'addkey' and state in self.task_failed and groupid not in failedgroup:
                        failedgroup.append(groupid)
                    elif des == 'setstatus' and groupid in failedgroup:
                        servers[ip]['status']='prevfailed'
                        
        for id in sorted_keys:
            task=taskdata.get(id)
            if not task:
                continue
            iplist=task.get('iplist', {})
            status=task.get('status')
            #获取执行失败的任务来进行匹配            
            if status in self.task_success:
                #当前任务执行成功
                continue
            elif failedgroup:
                #说明找到了失败的任务信息
                #修改主机任务状态为 prevfailed
                do_group('setstatus') 
            else:
                #当前第一个失败状态任务选为参照
                do_group('addkey')
 
        return True               
                      
    def check_task_status(self):
        for task in self.task_list:
            d=threads.deferToThread(self.thread_to_check_task, task)
            d.addErrback(self.defer_show_expect)
        
    def get_task(self):
        while 1:
            #无任务就退出，等待下一次检查
            if self.task_que.empty():
                break
            else:
                taskdata=self.task_que.get()
                if not taskdata:
                    break
                log.info('cron find task %s.' % taskdata['task_name']) 
                d=threads.deferToThread(self.exec_task, taskdata)
                d.addErrback(self.defer_show_expect)

def getconf(cfg,attrname=None,attrvalue=None):
    if not os.path.exists(cfg):
        return False
    info={}
    tw_xml=comm_lib.xml(cfg)
    tw_conf=tw_xml.get_tag("config",attrname,attrvalue)
    for child_node in tw_conf.childNodes:
        if child_node.nodeType ==1:
            attr={}
            for att,value in zip(child_node.attributes.keys(),child_node.attributes.values()):
                attr.update({att:value.nodeValue})
            info[child_node.nodeName]=attr

    return  info

def decode_pwd(pwd):
    try:
        return encrypt.decode_pwd(pwd)
    except:
        return pwd
        
class twistedserver(Daemon):
    def __init__(self, *args, **kwargs):
        super(twistedserver, self).__init__(*args, **kwargs)
        
    def run(self):
        factory=server_factory()
        #1秒钟检查一次，有任务就执行
        stime=1
        #获取执行任务
        gettask=task.LoopingCall(factory.get_task)
        checktask=task.LoopingCall(factory.check_task_status)
        #检查数据,队列发送,异步环境中避免相同socket发送数据串包和包被截断
        t=threading.Thread(target=factory.check_socket_data)
        t.setDaemon(False)
        t.start()
        gettask.start(stime)
        checktask.start(stime)
        reactor.listenTCP(listen_tcp_port,factory)
        reactor.run()
        
if __name__=="__main__":
    curr_path=os.path.split(os.path.realpath(__file__))[0]
    p_dbcfg=curr_path + os.sep + 'config' + os.sep + 'db_config.xml'
    p_tornado=curr_path + os.sep + 'config' + os.sep + 'tornado' + os.sep + 'config.xml'
    tornado_info=getconf(p_tornado,attrname="name",attrvalue="tornado")
    tornado_ip=tornado_info['tw_server']['ip']
    task_path=tornado_info['task']['file_path']
    task_log_path=tornado_info['task']['client_log_save']
    tornado_port=tornado_info['run']['port']
    p_twisted=curr_path + os.sep + 'config' + os.sep + 'twisted' + os.sep + 'config.xml'
    p_log=curr_path + os.sep + 'log' + os.sep + 'twisted' + os.sep + 'twisted.log'
    
    client_config=curr_path + os.sep + 'eagleclient' + os.sep + 'config' + os.sep + 'config.xml'
    client_info=getconf(client_config,attrname="name",attrvalue="client")
    client_deploy_path=client_info['server']['deploy_path']
    if not client_deploy_path or not re.match(r'^/.*', client_deploy_path):
        print 'client deploy path err.'
        sys.exit()
    posixbase_replace=posixbase_replace()
    epollreactor.EPollReactor._doReadOrWrite=posixbase_replace._doReadOrWrite
    
    log=comm_lib.log(p_log)
    tw_info=getconf(p_twisted,attrname="name",attrvalue="twsited")
    server_ip=tw_info['client']['ip']
    listen_tcp_port=int(tw_info['run']['port'])
    dbinfo=comm_lib.get_db_info(p_dbcfg)
    user_table=user_table.user_table(dbinfo["ip"],dbinfo["port"],dbinfo["db_name"],dbinfo["user"],encrypt.decode_pwd(dbinfo["pwd"]))

    help_msg = 'Usage: python %s <start|stop|restart|debug>' % sys.argv[0]
    twistedserver=twistedserver(curr_path+'/twisted_pid.pid')
    if sys.argv[1] in ['debug']:
        twistedserver.run()
    elif sys.argv[1] in ['start', 'stop', 'restart']:
        getattr(twistedserver, sys.argv[1])()
    else:
        print help_msg
        sys.exit(1)
