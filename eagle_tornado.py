#!/usr/bin/python
#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import tornado
from tornado import web, ioloop, options, httpserver, websocket
from tornado.options import define, options
import os, re, json, comm_lib, datetime, time, encrypt, tenjin, base64, uuid, csv, torndb, functools, Queue, random, copy, shutil, user_table, urllib2, threading
from tenjin.helpers import *
# 这个并发库在python3自带;在python2需要安装sudo pip install futures
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from daemon import Daemon

def dict_slice(dt, end, start=0):
    new_dict={}
    for i in dt.keys()[int(start):int(end)]:
        new_dict[i]=dt[i]
        
    return new_dict

def get_list(data):
    if isinstance(data, list):
        return data
    elif not data:
        return []
    else:
        return data.split(',')

        
def get_ret(code, message, status='info', isjson=True):
    #status:info/err/warning
    data={}
    data['code']=code
    data['message']=message
    data['status']=status
    if isjson:
        return json.dumps(data, ensure_ascii=False)
    else:
        return data

def tj_render(filepath, context=None):
    #context默认
    filepath=curr_path+os.sep+filepath.replace(curr_path, '')
    if not os.path.exists(filepath):
        return get_ret(-8, 'tenjin file path err.', status='err')
    if filepath.find(os.sep) != -1:
        fp=re.match(r'(.*)%s(.*)'%os.sep, filepath).group(1)
        fn=re.match(r'(.*)%s(.*)'%os.sep, filepath).group(2)
    else:
        fp="."
        fn=filepath
    engine=tenjin.Engine(path=[fp])
    log.info("tenjin render %s%s%s." % (fp, os.sep, fn))
    #return engine.render(fn, context)
    try:
        return engine.render(fn, context)
    except:
        log.warn('lineno:' + str(sys._getframe().f_lineno)+": "+str(sys.exc_info()))
        return get_ret(-9, 'render err.', status='err')

def check_true(*argv):
    ret=True
    for i in argv:
        if not i:
            ret=False
            break
    return ret        
    
def isexists(n):
    if n in locals().keys():
        return True
    else:
        return False

def request_twisted(request, long=None):
    sk=comm_lib.sock_client(tw_server_ip, int(tw_server_port))
    sock=sk.conn()
    if not sock:
        log.err("%s:%s conn failed."%(tw_server_ip, tw_server_port))
        return -9
    else:
        log.info("%s:%s conn success."%(tw_server_ip, tw_server_port))
    
    ret=comm_lib.send_socket_data(sock, request)
    if not ret:
        return -9

    if long:
        #长链接时候设置超时时间为30分左右
        sock.settimeout(600)
        return sock
    else:
        sock.settimeout(10)
        
    data=''
    while 1:
        try:
            data=comm_lib.recv_socket_data(sock)
        except:
            log.warn('socket timeout.')
            sk.close()
            return -9
  
        if not data:
            sleep(0.2)
            continue
            
        try:    
            data=json.loads(data)
        except:
            pass
            
        break
    sk.close()
    return data

        
def sleep(t):
    return time.sleep(t)


class baseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('user')
        
class websocketHandler(tornado.websocket.WebSocketHandler):
    conn={}
    twisted_conn={}
    executor = ThreadPoolExecutor(2000)
    def check_origin(self, origin):
        return True

    def show_task_log(self, data):
        task_name=data.get('name')
        filename=data.get('filename')

        if not task_name or not filename:
            return self.write_message(get_ret(-1, '参数错误', status='err'))
            
        if self.twisted_conn.get(self):
            self.twisted_conn[self].close()
            
        sk=request_twisted(data, long=True)
        if sk == -9:
            return self.write_message(get_ret(-2, '请求twisted失败' ,status='err'))
            
        self.twisted_conn[self]=sk
        count=int()
        while 1:
            try:
                data=comm_lib.recv_socket_data(sk)
            except:
                break;
                
            if not data:
                if count >= 180 :
                    #3分钟收不到数据就退出, 避免阻塞
                    break;
                count+=1
                sleep(0.5)
                continue

            count=int()
            logdone=False
            data=comm_lib.json_to_obj(data)
            if isinstance(data, dict):
                rspdt=json.dumps(data.get('response'))
                if data.get('logdone') == 'yes':
                    logdone=True
            else:
                rspdt=data
            self.write_message(rspdt)    
            if logdone:
                break
        sk.close()
        del self.twisted_conn[self]

    def open(self):
        log.info('websocket open')
        if self not in self.conn:
            self.conn[self]=self

    def do_request(self, data):
        if self not in self.conn:
            return None
        request_data=comm_lib.json_to_obj(data)
        if callable(getattr(self, request_data.get('request', None))):
            try:
                #getattr(self, request_data.get('request', None))(request_data)
                t=threading.Thread(target=getattr(self, request_data.get('request', None)), args=(request_data,))
                t.setDaemon(True)
                t.start()
            except:
                log.warn('lineno:' + str(sys._getframe().f_lineno)+": "+str(sys.exc_info()))
                #执行出错
                return self.write_message(get_ret(-101, 'execute err.', status='err'))

    @tornado.gen.coroutine
    def on_message(self, message):
        log.info('websocket get message '+str(message))
        yield self.executor.submit(self.do_request, message) 

    def on_close(self):
        log.info('on_close')
        try:
            self.conn[self].close()
            self.twisted_conn[self].close()
            del self.twisted_conn[self]
        except:
            pass
        del self.conn[self]
        
        
class loginHandler(baseHandler):
    #用户会话
    user_session={}
    def get(self):
        #检查会话cookie, 若通过则重定向到主界面
        user=self.get_secure_cookie("user")
        pwd=self.get_secure_cookie("pwd")
        if self.user_session.get(user):
            if self.user_session[user].get('remember') and pwd == self.user_session[user].get('pwd'):
                return self.redirect('/templates/main.html', permanent=True)
                
        self.render('login/index.html')
        
    def initialize(self):
        self.args={k:''.join(v) for k, v in self.request.arguments.iteritems()}
        if not self.args:
            #在 AngularJS 中，数据传递的是 application/json 格式的数据，在body里, ajax的则可以使用arguments获取
            #若arguments中没数据则使用body获取一次
            if self.request.body:
                self.args=json.loads(self.request.body)

        self.method=self.request.path.split(os.sep)[-1].replace('.',"_").replace('-', '_')  

    def post(self):
        username=self.args.get('user')
        pwd=self.args.get('password')
        pwd_md5=comm_lib.getmd5(pwd)
        self.set_secure_cookie("user", str(username))
        user_info=user_table.get_user_info(user=username)
        if user_info:
            pwd_info=user_info[0]['pwd']
        else:
            pwd_info=None

        try:
            try:
                #密码修改
                newpwd=self.args.get('pwdmodiy')
                if not newpwd:
                    #只为抛异常
                    raise Exception('err.')
                type='modify'
            except:
                #注册
                newpwd=self.args.get('newpwd')
                type='regster'
                
            if type=="modify" and pwd_md5 != pwd_info:
                result={'code':1, 'message':'密码错误', 'status':'err'}
            elif user_table.mod_user_pwd(username, comm_lib.getmd5(newpwd)) != None:
                #修改密码成功，注册成功
                result={'code':0, 'message':'注册成功', 'status':'info'}
            else:
                #修改密码失败，请联系管理员
                result={'code':2, 'message':'修改密码失败, 请联系管理员', 'status':'err'}
        except:        
            if not user_info and not pwd_info:
                #没有权限
                result={'code':-1, 'message':'没有权限, 请联系管理员添加当前用户', 'status':'err'}
            elif user_info and not pwd_info:
                #管理员添加用户后想要注册，由用户在界面上设置密码传过来
                result={'code':-2, 'message':'你需要注册, 请设置密码后登录', 'status':'err'}
            elif user_info and pwd_info and pwd_md5 == pwd_info:
                #验证通过
                result={'code':0, 'message':'验证通过', 'status':'info'}
                user_table.set_login_time(user=user_info[0]['user'])
            elif user_info and pwd_info and pwd_md5 != pwd_info:
                #密码错误
                result={'code':1, 'message':'密码错误', 'status':'err'}
        finally:
            if result['code'] == 0:
                #设置用户会话cookie, 有效期为1天
                self.set_secure_cookie("user", str(username), expires_days=None, expires=time.time()+86400)
                self.set_secure_cookie("pwd", str(pwd_md5), expires_days=None, expires=time.time()+86400)
                #更新用户信息
                self.user_session.setdefault(username, {})
                self.user_session[username]['pwd']=pwd_md5
                self.user_session[username]['remember']=self.args.get('remember')
            self.write(json.dumps(result))
                
def decode_utf8(dt):
    return { k : str(v).decode('GB18030').encode('utf-8').decode('utf-8') for k, v in dt.items() }

def write_csv(file, headers, dt):
    if not os.path.exists(os.path.split(file)[0]):
        os.makedirs(os.path.split(file)[0])
    if os.path.exists(file):
        os.rename(file, file+str(comm_lib.get_now()).replace(' ', '_'))
        
    with open(file, 'wb') as f:
        csv_w=csv.DictWriter(f, headers)
        csv_w.writeheader()
        #转换编码为GBK，支持execl和csv打开不乱码
        csv_w.writerows([{k:str(v).encode('gbk') for k, v in x.items()  if k in headers } for x in dt ])
        
    if os.path.exists(file):
        return True
    else:
        return False
        
class mainHandler(baseHandler):   
    def route_check(self, key):
        if re.match(r'%s'%key, self.request.path):
            return True
        else:
            return False

    def initialize(self):
        self.args={k:''.join(v) for k, v in self.request.arguments.iteritems()}
        if not self.args:
            #在 AngularJS 中，数据传递的是 application/json 格式的数据，在body里, ajax的则可以使用arguments获取
            #若arguments中没数据则使用body获取一次
            if self.request.body:
                self.args=json.loads(self.request.body)
        
        self.method=self.request.path.split(os.sep)[-1].replace('.',"_").replace('-', '_')

        if  self.args.get('requesttype') != 'platform_history':
            taskque.put({
                'type': 'add_history',
                'clsname': self.__class__.__name__,
                'remote_ip': self.request.remote_ip,
                'requestdata': { k:v for k,v in self.args.iteritems() },
                'verify_key': '',
                'c_user': self.get_current_user(),
                'method': self.method
            })
        self.args.update({'filepath':curr_path+self.request.path})
        self.args.update({'curruser':self.get_current_user()})
        self.assets_templeat_key='assets_templeat_key'
        self.page_line_length=15
        self.asset_tatistics_export_key=['line', 'product', 'app', 'idc', 'other_key', 'count']
        self.asset_tatistics_keys=[
            {'line':'产品线'},
            {'product':'业务'},
            {'app':'应用'},
            {'idc':'机房'},
            {'other_key':'other_key'},
            {'count':'统计数/服务器(台)'}
        ]
        self.asset_history_keys=[
            {'id':'id'},
            {'ip':'电信ip(主IP)'},
            {'c_type':'变更类型'},
            {'c_time':'变更时间'},
            {'c_user':'变更操作人'}
        ]
        self.assets_templeat_default=[
            {'telecom_ip':'电信ip(主)'}, 
            {'unicom_ip':'联通ip'}, 
            {'inner_ip':'内网ip'}, 
            {'line':'产品线'},
            {'product':'业务'}, 
            {'app':'应用'}, 
            {'idc':'机房'}
        ]
        self.assets_templeat_keys=[
            {'id':'id'},
            {'telecom_ip':'电信ip(主ip)'},
            {'unicom_ip':'联通ip'},
            {'inner_ip':'内网ip'},
            {'line':'产品线'},
            {'product':'业务'},
            {'app':'应用'},
            {'describe':'资产描述'},
            {'idc':'机房'},
            {'serial_number':'资产编号'},
            {'owner':'负责人'},
            {'os':'系统版本'},
            {'mem':'内存'},
            {'disk':'磁盘'},
            {'cpu':'cpu'},
            {'firm':'厂商'},
            {'remark':'备注'},
            {'c_time':'操作时间'},
            {'c_user':'操作用户'}
        ] 
        self.asset_key=['id', 'telecom_ip', 'unicom_ip', 'inner_ip', 'line', 'product' , 'app', 'describe', 'idc', 'serial_number' ,'owner' , 'os', 'mem', 'disk', 'cpu', 'firm', 'remark', 'c_time', 'c_user']
        self.asset_history_change_key=['id', 'ip', 'old_info', 'new_info', 'c_type', 'c_time', 'c_user']
        self.login_check_key=['line', 'product', 'app', 'idc', 'owner']
        self.login_info_display_keys=[
            {'line':'产品线'}, 
            {'product':'业务'}, 
            {'app':'应用'}, 
            {'idc':'机房'}, 
            {'owner':'负责人'}, 
            {'user':'登录用户'}, 
            {'port':'登录端口'}, 
            {'pwd':'登录密码'}
        ]
        self.loginmanager_key=[
            {'telecom_ip':'电信ip(主ip)'},
            {'unicom_ip':'联通ip'},
            {'inner_ip':'内网ip'},
            {'user':'登录用户'},
            {'port':'登录端口'},
            {'pwd':'登录密码'}
        ]
        self.logindefault_key=[
            {'line':'产品线'},
            {'product':'业务'},
            {'app':'应用'},
            {'idc':'机房'},
            {'owner':'负责人'},
            {'user':'登录用户'},
            {'port':'登录端口'},
            {'pwd':'登录密码'}
        ]
        
    def prepare(self):
        self.executor = ThreadPoolExecutor(2000)
        log.info('%s[%s] conn in, request %s;' % (self.request.remote_ip, self.args['curruser'], self.request.uri))
        
    def on_finish(self):
        log.info('%s request done;' % (self.request.remote_ip))
        
    def get_web_server_info(self):
        '''
        self-privilege::任务详情界面获取websocket url::任务管理-任务记录-详情界面自动发起请求
        '''
        tornado_server_info=str(tornado_ip)+':'+str(tornado_port)+"/online/websocket"
        return self.write(json.dumps({'url':tornado_server_info}))
        
    def get_comm_privileges(self):
        commprilist=['mainHandler.main_html', 'mainHandler.loginout_html']
        return commprilist

    def main_html(self):
        '''
        self-privilege::主页面::用户登录-平台主界面
        '''
        context={'username':self.args['curruser']}
        user_group=[]
        user_privilist=[]
        for k,v in self.args['groupdatainfo'].iteritems():
            if v.get('privi_list'):
                user_privilist+=v.get('privi_list').split(',')
            user_group.append(k)

        context.update({
            'user_privilist':user_privilist,
            'user_group':user_group
        })
        self.write(tj_render(self.args['filepath'], context))

    def loginout_html(self):
        '''
        self-privilege::退出平台::用户退出平台登录
        '''
        self.set_secure_cookie("user", '')
        self.write(json.dumps('success')) 

    def get_taskrelevance(self):
        '''
        self-privilege::任务关联界面::任务管理-任务创建-任务关联/任务详情
        '''
        context={}
        return self.write(tj_render('templates/task/taskrelevance.html', context))
        
    def get_task_servers_page(self):
        '''
        self-privilege::获取任务详情界面::任务管理-任务记录-详情
        '''
        task_name=self.args.get('task_name')
        history=user_table.get_task_history(task_name=task_name)
        if not history:
            history=user_table.get_task_history(task_name=task_name, status='done')
        new_history={}
        if history:
            server_info=json.loads(history[0].get('server_info', {}))
            { new_history.update({tuple(k.split('--=')):server_info.get(k)}) for k in  server_info }

        context={'task_name':task_name, 'history':new_history}
        return self.write(tj_render('templates/task/task_servers_info.html', context))
        
    def get_group_property(self):
        self.args['dotype']="mainpage"
        info=self.do_get_servergroup_info()
        app=user_table.get_servergroup_info(type="serverapp")
        applist={}
        newinfo={}
        #只返回有主机组的 line/product/app
        for i in app:
            line=i.get('line')
            product=i.get('product')
            line_des=info.get(line, {}).get('des', line)
            product_des=info.get(line, {}).get('product', {}).get(product, product)
            newinfo.setdefault(line, {})
            newinfo[line].setdefault('product', {})
            newinfo[line]['des']=line_des
            newinfo[line]['product'].setdefault(product, product_des)
            
            lp_id=tuple([line, product])
            applist.setdefault(lp_id, {})
            applist[lp_id][i.get('app')]=i.get('app_des')

        return {
                'info':newinfo,
                'app':applist
            }

    def get_server_privilegelist_main_page(self):
        '''
        self-privilege::权限信息主界面::主机管理-权限信息
        '''
        self.args['stype']="hostprivilegelist"
        return self.get_servergroup_main_page()
        
    def get_server_privilege_main_page(self):
        '''
        self-privilege::权限配置主界面::主机管理-权限配置
        '''
        self.args['stype']="hostprivilege"
        return self.get_servergroup_main_page()
        
    def get_fault_main_page(self):
        '''
        self-privilege::故障处理主界面::任务管理-故障处理
        '''
        faultinfo=user_table.get_fault_info()
        name=[]
        info=[]
        for i in faultinfo:
            name.append(i['name'])
            if str(i.get('status'))  == '1':
                info.append(i)
        context={'type':list(set(name))}
        return self.write(tj_render('templates/task/fault_handle.html', context))

    def get_taskcreate_main_page(self):
        '''
        self-privilege::任务创建主界面::任务管理-任务创建
        '''
        context=self.get_group_property()
        return self.write(tj_render('templates/task/taskcreate.html', context))
        
    def get_taskhistory_main_page(self):
        '''
        self-privilege::任务记录主界面::任务管理-任务记录
        '''
        history=user_table.get_task_history()
        relevance=user_table.get_task_relevance()
        used_app=[ i.get('task_type') for i in history]
        used_id=[ i.get('relevance_id') for i in history]

        relevanceinfo={ i.get('relevance_id'):i.get('relevance_name') for i in relevance if i.get('relevance_id') in used_id }
        relevanceapp={ i.get('relevance_app'):i.get('relevance_app_des') for i in relevance if i.get('relevance_app') in used_app }
        context={'relevanceapp':relevanceapp, 'relevanceinfo':relevanceinfo}
        return self.write(tj_render('templates/task/taskhistory.html', context))
        
    def get_informationcollect_main_page(self):
        '''
        self-privilege::信息收集主界面::任务管理-信息收集
        '''
        context={}
        return self.write(tj_render('templates/task/informationcollect.html', context))
        
    def get_taskcustom_main_page(self):
        '''
        self-privilege::自定义任务主界面::任务管理-自定义任务
        '''
        context={}
        return self.write(tj_render('templates/task/taskcustom.html', context))
        
    def get_serverlogin_main_page(self):
        '''
        self-privilege::登录管理主界面::资产管理-登录管理
        '''
        context={}
        return self.write(tj_render('templates/asset/server_login.html', context))

    def get_serverinit_main_page(self):
        '''
        self-privilege::初始化管理主界面::资产管理-初始化管理
        '''
        context={}
        return self.write(tj_render('templates/asset/server_init.html', context))
        
    def get_asset_template_keys(self):
        display_keys=user_table.get_other_setvalue_record(key=self.assets_templeat_key)
        new_keys=[]
        
        if display_keys:
            display_keys=json.loads(display_keys[0]['value'])

        if not display_keys:
            for i in self.assets_templeat_default:
                k=i.keys()[0]
                v=i[k]
                new_keys.append({k:v})
        else:
            for i in self.assets_templeat_keys:
                k=i.keys()[0]
                v=i[k]
                if k in display_keys:
                    new_keys.append({k:v})

        return new_keys

    
    def get_asset_main_page(self):
        '''
        self-privilege::资产管理主界面::资产管理-资产管理
        '''
        display_keys=self.get_asset_template_keys()
        history_keys=self.get_asset_history_key('history')
        tatistics_key=self.get_asset_history_key('tatistics')
        context={'display_keys':display_keys, 'history_keys':history_keys, 'tatistics_key':tatistics_key}
        return self.write(tj_render('templates/asset/assets.html', context))
        
    def get_inform_main_page(self):
        '''
        self-privilege::通知管理主界面::权限管理-通知管理
        '''
        context={'selfgroup':self.get_selfgroup()}
        return self.write(tj_render('templates/privilege/inform.html', context))

    def get_usergroup_main_page(self):
        '''
        self-privilege::用户组管理主界面::权限管理-用户组管理
        '''
        context={'selfgroup':self.get_selfgroup()}
        return self.write(tj_render('templates/privilege/user_group.html', context))

    def get_selfgroup(self):
        group=''
        groupinfo=user_table.get_privilege_allocate_info(user=self.args['curruser'])
        if groupinfo:
            group=groupinfo[0].get('name')
        return group
        
    def do_get_servergroup_info(self):
        assetinfo=user_table.get_assets()
        dotype=self.args.get('dotype')

        line=self.args.get('line')
        product=self.args.get('product')
        app=self.args.get('app')
        group=self.args.get('group_id')
        member=self.args.get('member')
        type=self.args.get('type')

        serverapp=''
        servergroup=''
        
        if dotype == "mainpage":
            serverhost=user_table.get_servergroup_info(type='serverhost')
        elif type == "serverappremoval":
            key=['line', 'product']
            serverhost=user_table.get_servergroup_info(type='serverapp')
        elif type =="servergroupremoval":
            key=['line', 'product', 'app']
            serverapp=user_table.get_servergroup_info(type='serverapp')
            serverhost=user_table.get_servergroup_info(type='servergroup')
        elif type == "groupmemberremoval":
            key=['line', 'product', 'app']
            serverapp=user_table.get_servergroup_info(type='serverapp')
            servergroup=user_table.get_servergroup_info(type='servergroup')
            serverhost=user_table.get_servergroup_info(type='serverhost')
            
        info={}
        asset_keys={}
        app_keys={}
        group_keys={}

        for i in assetinfo:
            describe=i.get('describe').split('-')
            cline=i.get('line')
            cline_des=describe[0]
            cproduct=i.get('product')
            cproduct_des=describe[1]

            asset_keys[tuple([cline, cproduct])]=i
            
            if dotype == "mainpage":
                info.setdefault(cline, {})
                info[cline].setdefault('product', {})
                info[cline]['des']=cline_des
                info[cline]['product'][cproduct]=cproduct_des
            elif dotype in ['serverappremoval', 'servergroupremoval', 'groupmemberremoval']:
                info.setdefault('line', [])
                info.setdefault('product', [])
                linedt={'key':{'name':cline, 'des':cline_des}}
                if linedt not in info['line']:
                    info['line'].append(linedt)
   
                productinfo={'key':{'name':cproduct, 'des':cproduct_des}, 'property':{'line':cline}}
                if productinfo not in info['product']:
                    info['product'].append(productinfo)
                    
        if serverapp:
            app_keys={ tuple([i.get('line'), i.get('product'), i.get('app')]):i for i in serverapp}
            serverhost+=serverapp
            
        if servergroup:
            group_keys={ tuple([i.get('line'), i.get('product'), i.get('app'), i.get('group_id')]):i for i in servergroup}
            serverhost+=servergroup
  
        for i in serverhost:
            if dotype == "mainpage":
                line=i.get('line')
                line_des=i.get('line')
                product=i.get('product')
                product_des=i.get('product')
                if not info.get(line):
                    info.setdefault(line, {})
                    info[line].setdefault('product', {})
                    info[line]['des']=line_des
                if product not in info[line]['product']:
                    info[line]['product'][product]=product_des
            elif dotype in ['serverappremoval', 'servergroupremoval', 'groupmemberremoval']:
                tapp=i.get('app')
                tapp_des=i.get('app_des')
                tline=i.get('line')
                tline_des=''
                tproduct=i.get('product')
                tproduct_des=''
                
                keys=tuple([tline, tproduct])
                asset_data=asset_keys.get(keys)

                if asset_data:
                    describe=asset_data.get('describe').split('-')
                    tline_des=describe[0]
                    tproduct_des=describe[1]
                else:
                    tline_des=tline
                    tproduct_des=tproduct
                    
                if app_keys:
                    tapp_des=app_keys.get(tuple([tline, tproduct, tapp]))
                    if tapp_des:
                        tapp_des=tapp_des.get('app_des')
                        
                if not tapp_des:
                    tapp_des=app
                    
                tgroup=i.get('group_id')
                tgroup_des=i.get('group_des')
                tmember=i.get('member')
                if group_keys:
                    tgroup_des=group_keys.get(tuple([tline, tproduct, tapp, tgroup]))
                    if tgroup_des:
                        tgroup_des=tgroup_des.get('group_des')
                if not tgroup_des:
                    tgroup_des=tgroup
                info.setdefault('line', [])
                info.setdefault('product', [])
                info.setdefault('app', [])
                info.setdefault('group', [])

                linedt={'key':{'name':tline, 'des':tline_des}}
                productdt={'key':{'name':tproduct, 'des':tproduct_des}, 'property':{'line':tline}}

                if  linedt in info['line'] and tline == line:
                    del info['line'][info['line'].index(linedt)]
                    info['line'].insert(0, linedt)
                else:
                    info['line'].append(linedt)

                if productdt in info['product'] and line == tline and product == tproduct:
                    del info['product'][info['product'].index(productdt)]
                    info['product'].insert(0, productdt)
                else:
                    info['product'].append(productdt)

                property={}
                for k in key:
                    property[k]=i.get(k)

                appinfo={'key':{'name':tapp, 'des':tapp_des}, 'property':property}

                if (group == tgroup or member == tmember or app == tapp) and line == tline and product == tproduct and tapp :
                    if appinfo in info['app']:
                        del info['app'][info['app'].index(appinfo)]
                    info['app'].insert(0, appinfo)
                elif appinfo not in info['app'] and tapp:    
                    info['app'].append(appinfo)

                groupinfo={'key':{'name':tgroup, 'des':tgroup_des}, 'property':property}
                if (group == tgroup or member == tmember) and line == tline and product == tproduct and tgroup :
                    if groupinfo in info['group']:
                        del info['group'][info['group'].index(groupinfo)]
                    info['group'].insert(0, groupinfo)
                elif groupinfo not in info['group'] and tgroup:     
                    info['group'].append(groupinfo)

        return info
        
    def get_servergroup_removal(self):
        '''
        self-privilege::获取主机主信息::主机管理-主机组管理-迁移时候获取
        '''
        self.args['dotype']=self.args.get('type')
        return  self.write(json.dumps(self.do_get_servergroup_info(), ensure_ascii=False))

    def serverhost_addlable(self):
        '''
        self-privilege::主机添加标签::主机管理-用户组管理
        '''
        self.args['success']='标签设置成功'
        self.args['err']='标签设置失败'
        self.args['dotype']='hostlabel'
        self.args['label']=self.args.get('data')
        return self.do_loginfo_modify()
            
    def get_servergroup_main_page(self):
        '''
        self-privilege::主机组管理主界面::主机管理-主机组管理
        '''
        stype=self.args.get('stype')
        if not stype:
            stype='hostgroup'
          
        self.args['dotype']="mainpage"
        info=self.do_get_servergroup_info()
        context={'info':info, 'stype':stype}
        return self.write(tj_render('templates/servermanager/group.html', context))
        
    def get_servergroup_page(self):
        ip=self.args.get('ip')
        role=self.args.get('role')
        line=self.args.get('line')
        product=self.args.get('product')
        app=self.args.get('app')
        group=self.args.get('group')
        pgtype=self.args.get('pgtype')
        member=self.args.get('member')
        serverid=self.args.get('serverid')
        
        if (pgtype in ['search_server_privilege'] and (not serverid or not ip)) or (pgtype in ['get_server_privilege'] and not serverid):
            return self.write(get_ret(-1, '参数错误', status='err'))
        
        if pgtype in ["groupmember", "server_privilege", "server_privilegelist"]:
            context={'line':line, 'product':product, 'app':app, 'group':group}
            if pgtype == "server_privilege":
                file='templates/servermanager/serverprivilege.html'
            elif pgtype == "groupmember":
                file='templates/servermanager/groupmember.html'
                stype=self.args.get('stype')
                context.update({'stype': stype}) 
            elif pgtype == "server_privilegelist":
                rolelist=user_table.get_server_privilege(line=line, product=product, app=app, group_id=group)
                context.update({'rolelist': { i.get('id'):i.get('role') for i in rolelist if i.get('role') }})
                file='templates/servermanager/serverprivilegelist.html'
        elif pgtype == "servergroup":
            context={'line':line, 'product':product, 'app':app}
            file='templates/servermanager/servergroup.html'
        elif pgtype == "memberlabel":
            if not member or not line or not product or not app or not group:
                return self.write(get_ret(-1, '参数错误', status='err'))
            info=user_table.get_servergroup_info(line=line, product=product, app=app, 
                        group_id=group, member=member, type="serverhost")
            if info:
                info=info[0].get('label')
                if info:
                    info=json.loads(info)
            if not info:
                info={}
            context={'member':member, 'info':info}
            file='templates/servermanager/memberlabel.html'
        elif pgtype == "get_server_privilege":
            rolelist=user_table.get_server_privilege(id=serverid)
            if not rolelist:
                rolelist={}
            else:
                privilege=rolelist[0].get('privilege')
                filelist=rolelist[0].get('filelist')
                rolelist={
                    'filelist': [ i for i in comm_lib.json_to_obj(filelist) if i ] if filelist else [],
                    'privilege': comm_lib.json_to_obj(privilege) if privilege else []
                }
            return self.write(json.dumps(rolelist, ensure_ascii=False))
            
        elif pgtype == "search_server_privilege":
            request={}
            request.update({
                'request':'search_server_privilege_filelist',
                'ip':ip,
                'serverid':serverid,
                'c_user':self.args['curruser'],
                'role':role
            })
            ret=request_twisted(request)
            if ret == 0:
                return self.write(get_ret(ret, '', status='info'))
            else:
                return self.write(get_ret(ret, ret, status='err'))
            
        elif pgtype == "serverapp":   
            context={'line':line, 'product':product}
            file='templates/servermanager/app.html'

        return self.write(tj_render(file, context))

    def get_server_privilege_filelist(self):
        '''
        self-privilege::获取主机权限对应的文件信息::主机管理-权限信息-服务器操作-选择规则
        '''
        self.args['pgtype']='get_server_privilege'
        return self.get_servergroup_page()
        
    def search_server_privilege_filelist(self):
        '''
        self-privilege::查询主机权限对应的文件信息::主机管理-权限信息-服务器操作-选择规则
        '''
        self.args['pgtype']='search_server_privilege'
        return self.get_servergroup_page()

    def get_server_privilegelist(self):
        '''
        self-privilege::获取主机权限信息页面::主机管理-权限信息-点击主机组后获取
        '''
        self.args['pgtype']='server_privilegelist'
        return self.get_servergroup_page()
        
    def get_server_privilege_config(self):
        '''
        self-privilege::获取主机权限配置页面::主机管理-权限配置-点击主机组后获取
        '''
        self.args['pgtype']='server_privilege'
        return self.get_servergroup_page()
        
    def get_member_servergroup(self):
        '''
        self-privilege::获取主机组成员页面::主机管理-主机组管理-点击主机组后获取
        '''
        self.args['pgtype']='groupmember'
        return self.get_servergroup_page()

    def get_group_servergroup(self):
        '''
        self-privilege::获取主机组页面::主机管理-主机组管理-点击分类后获取
        '''
        self.args['pgtype']='servergroup'
        return self.get_servergroup_page()
        
    def get_memberlabel(self):
        '''
        self-privilege::获取主机标签信息::主机管理-主机组管理-标签
        '''
        self.args['pgtype']='memberlabel'
        return self.get_servergroup_page()
        
    def get_app_servergroup(self):
        '''
        self-privilege::获取分类页面::主机管理-主机组管理-点击业务后获取
        '''
        self.args['pgtype']='serverapp'
        return self.get_servergroup_page()

    def get_key_main_page(self):
        '''
        self-privilege::key管理主界面::权限管理-key管理
        '''
        context={'selfgroup':self.get_selfgroup()}
        return self.write(tj_render('templates/privilege/key.html', context))

    def get_privilege_main_page(self):
        '''
        self-privilege::权限分配主界面::权限管理-权限分配
        '''
        context={'selfgroup':self.get_selfgroup()}
        return self.write(tj_render('templates/privilege/privilege.html', context))
    
    def get_groupselect_html(self):
        '''
        self-privilege::获取主机组信息用于任务创建::任务关联-任务创建-主机组下类型点击后加载
        '''
        context={
            'line':self.args.get('line'),
            'product':self.args.get('product'),
            'app':self.args.get('app')
        }
        return self.write(tj_render('templates/task/groupselect.html', context))

    def loginout_html(self):
        '''
        self-privilege::退出平台::用户退出平台登录
        '''
        self.set_secure_cookie("user", '')
        self.write(get_ret(0,"退出登录成功", status='info')) 
    
    def do_addinfo(self):
        addtype=self.args.get('addtype')
        name=self.args.get('name', '')
        des=self.args.get('des')
        type=self.args.get('type')
        status=self.args.get('status')
        value=self.args.get('value')
        line=self.args.get('line')
        product=self.args.get('product')
        app=self.args.get('app')
        modal=self.args.get('modal')
        remark=self.args.get('remark')
        #iplist
        host=name
        assetapp=self.args.get('assetapp')
        #task_relevance
        relevanceid=self.args.get('relevanceid')
        prepro=self.args.get('prepro')
        relevancepath=self.args.get('relevancepath')
        relevancename =self.args.get('relevancename')
        preprolist=self.args.get('preprolist')
        relevanceapp=self.args.get('relevanceapp')
        preproid=self.args.get('preproid')
        relevancetype=self.args.get('relevancetype')
        relevanceappdes=self.args.get('relevanceappdes')
        relevanceremark=self.args.get('relevanceremark')
        relevancechecklist=self.args.get('relevancechecklist')
        relevancelist =self.args.get('relevancelist')
        relevancetypedes=self.args.get('relevancetypedes')
        relevancerely=self.args.get('relevancerely')
        dotype=self.args.get('dotype')
        
        #任务创建
        data=self.args.get('data', {})
        breadcrumblist=self.args.get('breadcrumblist', {})
        
        relevance_id=data.get('taskname')
        task_name=data.get('task_name')
        custom_name=data.get('taskalias')
        custom_type=data.get('tasktypecustom')
        execute_time=data.get('executetime')
        isprepro=data.get('prepro')
        server_info=data.get('server_info', {})

        now=self.args.get('now')
        relevanceinfo=self.args.get('relevanceinfo')
        parameters=self.args.get('parameter')
        task_type=breadcrumblist.get('relevanceapp')

        task_servers_name=self.args.get('task_name')
        
        servergroup=self.args.get('group')
        success=self.args.get('success')
        err=self.args.get('err')

        paramete_err=False
        if (not name or not des) and addtype in ['useradd', 'groupadd', 'taskcustom', 'collecttemplate']:
            paramete_err=True
        elif not name and addtype in ['serverprivilege']:
            paramete_err=True
        elif (not data or not relevance_id or not execute_time or not task_type or not relevanceinfo) and addtype in ['task_create']:
            paramete_err=True
        elif (not name or not des or not type) and addtype in ['contactadd']:
            paramete_err=True
        elif  addtype in ['get_task_servers'] and not task_servers_name:
            paramete_err=True
        elif  addtype in ['task_relevance']:
            if not relevanceapp or not relevanceappdes or not relevanceid or not relevancename or len(relevancelist) == 0:
                paramete_err=True

            if prepro == "yes":
                if len(preprolist) == 0:
                    paramete_err=True
                else:
                    for i in preprolist:
                        index=preprolist.index(i)
                        if (i == 0 and not relevancelist[index]['preprotime']) or (i!=0 and not relevancelist[index]['preprofile']):
                            paramete_err=True

        elif (not name or not des or not value) and addtype in ['keyadd']:    
            paramete_err=True
        elif (not name or not des or not line or not product) and addtype in ['serverapp', 'servergroup', 'serverhost']:
            if addtype == 'servergroup' and  modal:
                paramete_err=False
            elif addtype == "serverhost" and host:
                paramete_err=False
            else:
                paramete_err=True
                
        #前端使用_and_分割取值
        if  re.match(r'.*_and_.*', name) and addtype != 'serverprivilege':
            return self.write(get_ret(-4, '添加失败,不能包含_and_字段', status='err'))
            
        if  paramete_err:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
        
        if addtype =="useradd":
            success='user[%s]添加成功'  % name 
            err='user[%s]添加失败'  % name
            if user_table.get_user_info(user=name):
                return self.write(get_ret(1, 'user添加失败:%s已经存在' % name, status='err'))
                
            if not user_table.add_user_info(name, des, self.args['curruser']):
                return self.write(get_ret(-2,  err, status='err'))
                
        elif addtype =="serverprivilege":
            gdata=user_table.get_server_privilege(line=line, product=product, app=app, group_id=servergroup, role=name)
            if gdata:
                return self.write(get_ret(-2, '添加失败, 当前规则已经存在', status='err'))

            ret=user_table.add_server_privilege(self.args['curruser'], line=line, product=product, app=app, group_id=servergroup, role=name)
            
        elif addtype =="task_create":
            relevanceinfo=relevanceinfo[0]
            task_list=json.loads(relevanceinfo['task_list'])
            relevanceinfo.update({'task_list':comm_lib.json_to_obj(relevanceinfo['task_list'])})
            
            server_info=self.do_task_create()
            if server_info == -9:
                return self.write(get_ret(-2, '请求twisted失败' ,status='err'))
            task_type=task_type.get('key')
            ret=user_table.add_task_history(self.args['curruser'], task_name=task_name, custom_name=custom_name,
                                task_type=task_type, custom_type=custom_type, relevance_id=relevance_id, 
                                status='ready', execute_time=execute_time, 
                                isprepro=isprepro, create_time=now,
                                parameters=json.dumps(parameters, ensure_ascii=False),
                                server_info=json.dumps(server_info, ensure_ascii=False, skipkeys=True),
                                task_info=json.dumps(relevanceinfo, ensure_ascii=False))
                                
        elif addtype =="get_task_servers":
            ret=user_table.get_task_servers_info(task_name=task_servers_name)
            err='任务记录不存在[%s]' % task_servers_name
        elif addtype =="groupadd":
            if user_table.get_group_info(group=name):
                return self.write(get_ret(1, 'group添加失败:%s已经存在' % name, status='err'))
                
            if not user_table.add_group_info(name, des, self.args['curruser']):
                return self.write(get_ret(-2, err, status='err'))
        elif addtype =="collecttemplate":
            if user_table.get_collecttemplate_info(template_id=name):
                return self.write(get_ret(1, '添加信息收集模板失败:%s已经存在' % name, status='err'))
                
            if not user_table.add_collecttemplate_info(template_id=name, des=des, remark=remark, c_user=self.args['curruser']):
                return self.write(get_ret(-2, err, status='err'))
        elif addtype =="taskcustom":
            if user_table.get_task_info(task_id=name):
                return self.write(get_ret(1, '添加自定义任务失败:%s已经存在' % name, status='err'))
                
            if not user_table.add_task_info(task_id=name, des=des, remark=remark, c_user=self.args['curruser']):
                return self.write(get_ret(-2, err, status='err'))
                
        elif addtype =="contactadd":
            success='联系人[%s]添加成功' % name
            err='联系人[%s]添加失败' % name
            if user_table.get_inform_contact_info(type=type, name=name):
                return self.write(get_ret(1, '联系人添加失败:%s已经存在' % name, status='err'))
                
            if not user_table.add_inform_contact(name, des, type, self.args['curruser']):
                return self.write(get_ret(-2, err % name, status='err'))
                
        elif addtype == 'task_relevance':
            task_list={'relevancelist':relevancelist, 'preprolist':preprolist}
            if dotype == "update":
                ret=user_table.task_relevance_update(self.args['curruser'], relevance_id=relevanceid, relevance_name=relevancename, 
                relevance_remark=relevanceremark, relevance_app=relevanceapp, relevance_app_des=relevanceappdes, relevance_type=relevancetype, relevance_type_des=relevancetypedes, relevance_rely=relevancerely, relevance_path=relevancepath, task_list=json.dumps(task_list, ensure_ascii=False))
            else:
                if user_table.get_task_relevance(relevance_id=relevanceid):
                    return self.write(get_ret('err', '关联任务失败,id已经存在[%s]' % relevanceid, status='err'))
                ret=user_table.task_relevance(self.args['curruser'], relevance_id=relevanceid, relevance_name=relevancename, 
                relevance_remark=relevanceremark, relevance_app=relevanceapp, relevance_app_des=relevanceappdes, relevance_type=relevancetype, relevance_type_des=relevancetypedes, relevance_rely=relevancerely, relevance_path=relevancepath, task_list=json.dumps(task_list, ensure_ascii=False))
                
        elif addtype == "keyadd":
            success='key[%s]添加成功' % name
            err='key[%s]添加失败' % name
            if user_table.get_verify_key_info(name=name):
                return self.write(get_ret(1, 'key添加失败:%s已经存在' % name, status='err'))
            
            if not user_table.add_verify_key_info(name, des, value, self.args['curruser']):
                return self.write(get_ret(-2, err, status='err'))
        elif addtype in ["serverapp", 'servergroup', 'serverhost']:
            if addtype == 'serverapp':
                winfo='分类添加失败:%s已经存在' % name
                reta=user_table.get_servergroup_info(line=line, product=product, app=name,  type=addtype)
            elif addtype =='servergroup':
                winfo='主机组添加失败:%s已经存在' % name
                reta=user_table.get_servergroup_info(line=line, product=product, app=app, group=name, type=addtype)
            elif addtype =='serverhost':
                winfo='主机组成员添加失败:%s已经存在' % name
                reta=user_table.get_servergroup_info(line=line, product=product, app=app, group=servergroup, member=host, type=addtype)
                
            if reta:
                return self.write(get_ret(1, winfo, status='err'))

            if addtype == 'serverapp':
                ret=user_table.add_servergroup_info(self.args['curruser'], line=line, product=product, app=name, app_des=des, type=addtype)

            elif addtype =='servergroup':
                ret=user_table.add_servergroup_info(self.args['curruser'], line=line, product=product, app=app, group_id=name, group_des=des, modal=modal, remark=remark , type=addtype)
            elif addtype =='serverhost':
                modalinfo=user_table.get_servergroup_info(line=line, product=product, app=app, group=servergroup, type='servergroup')
                if not modalinfo:
                    return self.write(get_ret(-2, '获取modal失败', status='err'))
                modal=modalinfo[0]['modal']
                ret=user_table.add_servergroup_info(self.args['curruser'], line=line, product=product, app=app, group_id=servergroup, modal=modal, member=host, asset_app=assetapp, type=addtype)

            if not ret:
                return self.write(get_ret(-2, err, status='err'))
            
        return self.write(get_ret(0, success, status='info'))
        
        
    def task_relevance(self):
        '''
        self-privilege::任务关联::任务管理-任务创建-任务关联
        '''
        self.args['addtype']='task_relevance'
        self.args['success']='关联任务成功'
        self.args['err']='关联任务失败'
        return self.do_addinfo()
        
    def add_info_serverprivilege_html(self):
        '''
        self-privilege::服务器权限规则添加::主机管理-权限配置-添加规则
        '''
        self.args['addtype']='serverprivilege'
        self.args['success']='主机组权限规则添加成功'
        self.args['err']='主机组权限规则添加失败'
        return self.do_addinfo()
        
    def add_info_fault_html(self):
        '''
        self-privilege::故障处理信息提交::任务管理-故障处理-操作
        '''
        id=self.args.get('id')
        status=self.args.get('status')
        remark=self.args.get('remark')
        if not id or not status:
            return self.write(get_ret(-1, '参数错误', status='err'))
        if not user_table.fault_commit(id, status, remark, self.args['curruser']):
            return self.write(get_ret(-2, '处理失败', status='err'))
            
        return self.write(get_ret(0, '处理成功', status='info'))
        
    def add_info_collecttemplate_html(self):
        '''
        self-privilege::添加信息收集模板::任务管理-信息收集-模板管理-添加模板
        '''
        self.args['addtype']='collecttemplate'
        self.args['success']='添加信息收集模板成功'
        self.args['err']='添加信息收集模板失败'
        return self.do_addinfo()
        
    def add_info_taskcustom_html(self):
        '''
        self-privilege::添加自定义任务::任务管理-自定义任务-添加任务
        '''
        self.args['addtype']='taskcustom'
        self.args['success']='添加自定义任务成功,请使用上传/更新功能上传可执行文件'
        self.args['err']='添加自定义任务失败'
        return self.do_addinfo()
        
    def add_info_groupmember_html(self):
        '''
        self-privilege::主机组成员添加::主机管理-主机组管理-添加成员
        '''
        self.args['addtype']='serverhost'
        self.args['success']='主机组成员添加成功'
        self.args['err']='主机组成员添加失败'
        return self.do_addinfo()
        
    def add_info_servergroup_html(self):
        '''
        self-privilege::主机组添加::主机管理-主机组管理-添加主机组
        '''
        self.args['addtype']='servergroup'
        self.args['success']='主机组加成功'
        self.args['err']='主机组加失败'
        return self.do_addinfo()
        
    def add_info_serverapp_html(self):
        '''
        self-privilege::主机组分类添加::主机管理-主机组管理-添加分类
        '''
        self.args['addtype']='serverapp'
        self.args['success']='分类添加成功'
        self.args['err']='分类添加失败'
        return self.do_addinfo()
        
    def add_info_useradd_html(self):
        '''
        self-privilege::添加用户::权限管理-用户组管理-用户管理-添加用户信息
        '''
        self.args['addtype']='useradd'
        self.args['name']=self.args.get('user')
        return self.do_addinfo()

        
    def add_info_groupadd_html(self):
        '''
        self-privilege::添加组::权限管理-用户组管理-组管理-添加组
        '''
        self.args['addtype']='groupadd'
        self.args['name']=self.args.get('group')
        self.args['success']='group添加成功'
        self.args['err']='group添加失败'
        return self.do_addinfo()

    def add_info_contactadd_html(self):
        '''
        self-privilege::通知联系人添加::权限管理-通知管理-联系人管理-添加联系人
        '''
        self.args['addtype']='contactadd'
        return self.do_addinfo()

        
    def add_info_accountadd_html(self):
        '''
        self-privilege::通知主账号添加::权限管理-通知管理-主账号管理-添加用户信息
        '''
        type=self.args.get('type')
        name=self.args.get('name')
        des=self.args.get('des')
        pwd=self.args.get('pwd')
        server=self.args.get('server')
        smtp_port=self.args.get('smtp_port')
        smtp_ssl_port=self.args.get('smtp_ssl_port')
        wechatid=self.args.get('id')
        wechatsecret=self.args.get('secret')
        if (type == "email" and (not name or not des or not pwd or not server)
            ) or (type=="wechat" and ( not wechatid or not wechatsecret)):
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
            
        if pwd:
            pwd=encrypt.en_pwd(pwd)
        
        if not name and wechatid:
            name=wechatid

        if user_table.get_inform_account_info(type=type, name=name):
            return self.write(get_ret(1, 'key添加失败:%s已经存在' % name, status='err'))

        if not user_table.add_inform_account(self.args['curruser'], 
                                                name=name, des=des, type=type, 
                                                pwd=pwd, server=server, smtp_ssl_port=smtp_ssl_port, smtp_port=smtp_port, 
                                                wechatid=wechatid, wechatsecret=wechatsecret):
            return self.write(get_ret(-2, 'key添加失败', status='err'))
            
        return self.write(get_ret(0, 'key添加成功', status='info'))

    def accountslider_status_change(self):
        '''
        self-privilege::通知管理主账号状态修改::权限管理-通知管理-主账号管理-设置滑块
        '''
        type=self.args.get('type')
        name=self.args.get('name')
        status=self.args.get('status')
        if not name or not type or not status:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
        
        if not user_table.account_status_change(type, name, status, self.args['curruser']):
            return self.write(get_ret(-2, '主账号[%s]状态修改失败' % name, status='err'))
        return self.write(get_ret(0, '主账号[%s]状态修改成功', status='info'))
        
    def add_info_keyadd_html(self):
        '''
        self-privilege::key添加::权限管理-key管理-添加key
        '''
        self.args['addtype']='keyadd'
        self.args['name']=self.args.get('id')
        return self.do_addinfo()
        
    def get_task_relevance_history(self):
        '''
        self-privilege::获取任务关联记录信息::任务关联-任务创建-任务创建界面前端自动加载
        '''
        name=self.args.get('name')
        type=self.args.get('type')
        if name:
            info=user_table.get_task_relevance(relevance_id=name)
        else:
            info=user_table.get_task_relevance()
        key=[
                {'relevance_id':'关联任务id'}, 
                {'relevance_name':'名称'}, 
                {'c_time':'操作时间'}, 
                {'c_user':'操作人'}
            ]
        if type == 'update':
            return self.write(json.dumps(info, ensure_ascii=False))
        else:
            return self.write(self.get_pagination_data(info, key))
        
    def get_task_relevance_info(self):
        '''
        self-privilege::获取任务关联信息::任务关联-任务创建-任务创建界面前端自动加载
        '''
        info=user_table.get_task_relevance()
        data={}
        for i in info:
            app=i.get('relevance_app')
            appdes=i.get('relevance_app_des')
            type=i.get('relevance_type')
            typedes=i.get('relevance_type_des')
            task_list=json.loads(i.get('task_list'))
            if task_list.get('preprolist') and task_list.get('relevancelist')[0].get('prepro') == 'yes':
                prepro='yes'
            else:
                prepro='no'
            data.setdefault(app, {})
            data[app].setdefault('type', {})
            data[app]['type'].setdefault(type, {})
            data[app]['type'][type].setdefault('tasklist', {})
            data[app]['des']=appdes
            data[app]['type'][type]['des']=typedes
            #data[app]['type'][type]['tasklist'][i.get('relevance_id')]=i.get('relevance_name')
            data[app]['type'][type]['tasklist'][i.get('relevance_id')]={}
            data[app]['type'][type]['tasklist'][i.get('relevance_id')]['des']=i.get('relevance_name')
            data[app]['type'][type]['tasklist'][i.get('relevance_id')]['prepro']=prepro

        return self.write(json.dumps(data, ensure_ascii=False))

    def task_servers_check(self):
        '''
        self-privilege::检查任务详情记录::任务管理-任务记录-详情
        '''
        self.args['addtype']='get_task_servers'
        self.args['success']='查询任务记录成功'
        self.args['err']='查询任务记录失败'
        return self.do_addinfo()

    def do_task_create(self):
        data=self.args.get('data')
        grouplist=data.get('grouplist', {})
        task_name=data.get('task_name')
        task_info=data.get('task_info', {})
        relevanceinfo=self.args.get('relevanceinfo', {})
        relevance_id=data.get('taskname')
        
        context=self.get_group_property()
        line_product=context['info']
        app_info=context['app']

        server_info={}
        groupinfo=[]
        for l in grouplist.keys():
            for p in grouplist[l].keys():
                for a in grouplist[l][p].keys():
                    ck=tuple([l, p])
                    app_des=app_info.get(ck, {}).get(a, a)
                    line_des=line_product.get(l, {}).get('des', l)
                    product_des=line_product.get(l, {}).get('product', {}).get(p, p)
                    for g in grouplist[l][p][a].keys():
                        member=grouplist[l][p][a].get(g, '')
                        ginfo=user_table.get_servergroup_info(line=l, product=p, app=a, group=g, member=member, type='serverhost')
                        if ginfo:
                            group_des=ginfo[0].get('group_des', g)
                        else:
                            group_des=g
                        #json不能dumps tuple 下标字典
                        server_key=str(l)+"--="+str(p)+"--="+str(a)+"--="+str(g)
                        server_data={server_key:{
                                            'line_des':line_des,
                                            'product_des':product_des,
                                            'app_des':app_des,
                                            'group_des':group_des,
                                        }
                                    }
                        server_info.update(server_data) 
                        #serveres里存list
                        [ i.update({'server_key': [l, p, a, g]}) for i in ginfo ]
                        #groupinfo+=user_table.get_servergroup_info(line=l, product=p, app=a, group=g, member=member, type='serverhost')
                        groupinfo+=ginfo
       
        #获取登录信息,modal为no的
        iplist=[ i.get('member') for i in groupinfo if i.get('modal') == 'no' ]
        logininfo=self.get_server_login_info(iplist)
            
        #请求twisted写详情记录,并进行环境检查(密码和客户端状态)
        request={}
        request['iplist']=iplist
        request['logininfo']=logininfo
        request['relevance_id']=relevance_id
        request['groupinfo']=groupinfo
        request['task_name']=task_name
        request['dotype']='run'
        request['task_info']=relevanceinfo
        request['request']='do_task_create'
        request['c_user']=self.args['curruser']
        
        sk=request_twisted(request)
        if sk == -9:
            return sk
        
        return server_info
        
    def task_exectime_check(self):
        data=self.args.get('data')
        if data:
            execute_time=data.get('executetime', '')
        else:
            execute_time=self.args.get('execute_time', '')

        if not re.match(r'([0-9]+-){2}[0-9]+[ \t]+([0-9]+:){2}[0-9]+', execute_time):
            self.args['errorinfo']=get_ret(-5, '执行时间格式不对' ,status='err', isjson=False)
            
        ret=re.match(r'^00.*$', execute_time)
        checktype=self.args.get('checktype')
        
        if checktype == 'modifycheck' and ret:
            self.args['errorinfo']=get_ret(-4, '执行时间不能为0开头' ,status='err', isjson=False)

        #不是立即执行的任务进行计划时间检查
        if not ret:
            sys_time=comm_lib.to_datetime_obj(str(datetime.datetime.now()).split('.')[0])
            ex_time=comm_lib.to_datetime_obj(execute_time)
            time_cmp=int(str((ex_time - sys_time).total_seconds()).split('.')[0])
            if time_cmp < 0 :
                self.args['errorinfo']=get_ret(-2, '执行时间不能小于当前时间' ,status='err', isjson=False)
        
    def task_single_restart(self):
        '''
        self-privilege::单独执行任务::任务管理-任务记录-详情-详情页面-重新执行
        '''
        self.args['success']='单独执行任务成功'
        self.args['err']='单独执行任务失败,请检查'
        self.args['dotype']='task_single_restart'
        return self.do_task_handel()
        
    def serverprivilegelist_download(self):
        '''
        self-privilege::服务器权限下载文件::主机管理-权限信息-服务器操作-下载
        '''
        self.args['name']='serverprivilegelist'
        self.args['err']='下载失败'
        return self.file_download()
        
    def task_log_download(self):
        '''
        self-privilege::下载任务日志::任务管理-任务记录-详情-下载日志
        '''
        self.args['success']='日志下载成功'
        self.args['err']='日志下载失败,请检查'
        self.args['dotype']='task_log_download'
        return self.do_task_handel()
        
    def task_restart(self):
        '''
        self-privilege::重新执行任务::任务管理-任务记录-重新执行
        '''
        self.args['success']='重新执行任务成功'
        self.args['err']='重新执行任务失败,请检查'
        self.args['dotype']='task_restart'
        return self.do_task_handel()
        
    def task_cancel(self):
        '''
        self-privilege::取消执行任务::任务管理-任务记录-取消执行
        '''
        self.args['success']='取消执行任务成功'
        self.args['err']='取消执行任务失败,请检查'
        self.args['dotype']='task_cancel'
        return self.do_task_handel()
        
    def do_task_handel(self):
        task=self.args.get('name')
        dotype=self.args.get('dotype')
        success=self.args.get('success')
        exectimetype=self.args.get('exectimetype')
        skipsuccess=self.args.get('skipsuccess')
        filename=self.args.get('filename')
        ip=self.args.get('ip')

        err=self.args.get('err')
        if not task or (dotype == 'task_log_download' and (not filename or not ip)) or (
                    dotype == 'task_restart' and (not exectimetype or not skipsuccess)):
            return self.write(get_ret(-1, '参数错误', status='err'))
            
        request={}
        request['request']=dotype
        request['task_name']=task
        if dotype == 'task_restart':
            request['exectimetype']=exectimetype
            request['skipsuccess']=skipsuccess
            user_table.update_task_history_status(self.args['curruser'], 'ready', task)

        if dotype == 'task_single_restart':
            serverhistory=user_table.get_task_servers_info(task_name=task, telecom_ip=ip)
            task_info=json.loads(serverhistory[0].get('task_info'))
            { i[i.keys()[0]].update({'status':'ready'}) for i in task_info if i.keys()[0] == filename }
            user_table.task_servers_status_update(task, json.dumps(task_info, ensure_ascii=False), ip)
            
        if dotype == 'task_cancel':
            user_table.update_task_history_status(self.args['curruser'], 'cancel', task)
            
        if dotype in ['task_log_download', 'task_single_restart']:
            request['filename']=filename
            request['ip']=ip
        
        ret=self.do_request_twisted(request, long=True)
        if ret == -9 or ret == -100:
            return self.write(get_ret(-2, '请求twisted失败' ,status='err'))
        elif ret == 'offline':
            return self.write(get_ret(-5, '下载日志失败, %s offline' % ip ,status='err'))
        elif ret == 'filenotexists':
            return self.write(get_ret(-6, 'log file not exists.' ,status='err'))   

        if dotype == 'task_log_download' :
            logfile=comm_lib.json_to_obj(ret)
            if not comm_lib.isexists(logfile):
                return self.write(get_ret(-3, logfile ,status='err'))
            else:
                return self.write("downloadfile/"+logfile.replace('/./', '/').replace(curr_path, '.'))
        return self.write(get_ret(0, success ,status='info'))
     
    def do_request_twisted(self, data, long=False):
        sk=request_twisted(data, long=long)
        if sk == -9:
            return sk
            
        if long:
            ret=''
            while 1:
                ret=comm_lib.recv_socket_data(sk)
                if ret:
                    sk.close()
                    return comm_lib.json_to_obj(ret)

    def task_create(self):
        '''
        self-privilege::任务创建::任务管理-任务创建-下一步-提交
        '''
        if not time_check():
            return self.write(get_ret(-1, '创建任务失败;os和db时间不一致' ,status='err'))
    
        data=self.args.get('data')
        self.task_exectime_check()
        if self.args.get('errorinfo'):
            return self.write(json.dumps(self.args.get('errorinfo'), ensure_ascii=False))

        relevance_id=data.get('taskname')
        now=str(comm_lib.get_now())
        task_name=relevance_id+"_"+now.replace(' ', '_')
        relevanceinfo=user_table.get_task_relevance(relevance_id=relevance_id)
        #写记录
        self.args['now']=now
        self.args['relevanceinfo']=relevanceinfo
        data.update({'task_name':task_name})
        self.args['addtype']='task_create'
        self.args['success']='任务创建成功'
        self.args['err']='任务创建失败'
        return self.do_addinfo()

    def get_taskcreate_confirm_html(self):
        '''
        self-privilege::任务创建获取确认界面::任务管理-任务创建-下一步
        '''
        context={'data':self.args.get('data'), 'breadcrumblist':self.args.get('breadcrumblist')}
        return self.write(tj_render('templates/task/taskcreate_confirm.html', context))
    
    def get_task_status(self, statuslist):
        status=''
        for i in statuslist:
            if i in ['offline', 'failed', 'cancel', 'ready', 'running', 'success', 'timeout', 'logininfoerr', 'filenotexists']:
                status=i
                break
        if not status:
            status="error"
        return status
    
    def get_taskservers(self):
        task=self.args.get('task_name')
        type=self.args.get('type')
        ip=self.args.get('ip')
        line=self.args.get('line')
        product=self.args.get('product')
        app=self.args.get('app')
        group=self.args.get('group')
        
        if not task:
            return self.write(get_ret(-1, '参数错误', status='err'))
        info=user_table.get_task_servers_info(task_name=task)
        if not info:
            info=user_table.get_task_done_info(task_name=task)
        data=[]
        serverinfo={}
        preproinfo={}
        
        for i in info:
            tip=i.get('telecom_ip')
            task_info=json.loads(i.get('task_info', '[{}]'))
            if not isinstance(task_info, list):
                task_info=[task_info]

            status=self.get_task_status([ f[f.keys()[0]].get('status') for f in task_info])
            modal=i.get('modal')
            assetapp=i.get('asset_app')
            
            if tip == 'localhost':
                preproinfo={'ip':tip, 'status':status}
                serverinfo=task_info
            elif  json.loads(i.get('server_key', '[]')) == [line, product, app, group]:
                serverdata={'ip':tip, 'status':status, 'modal':modal, 'assetapp':assetapp}
                if serverdata not in data:
                    data.append(serverdata)
                if tip == ip :
                    serverinfo=task_info
         
        context={
            'data':data,
            'serverinfo':serverinfo,
            'localhost':preproinfo
        }
        return self.write(json.dumps(context, ensure_ascii=False))

    def get_ngrepeat_data_serverprivilegedetails(self):
        '''
        self-privilege::获取主机组权限规则信息::主机管理-主机组管理-权限配置页面前端自动加载
        '''
        self.args['type']="serverprivilegedetails"
        self.args['infotype']="privileges"
        return self.get_ngrepeat_data_servergroup()
        
    def get_ngrepeat_data_taskservers(self):
        '''
        self-privilege::获取任务主机详情信息::任务管理-任务记录-详情界面自动加载
        '''
        return self.get_taskservers()
        
    def get_ngrepeat_data_groupdetails(self):
        '''
        self-privilege::获取主机组详情信息/任务创建界面获取主机组详情信息::主机管理/任务管理-主机组管理/主机组选择页面前端自动加载
        '''
        self.args['type']="groupdetails"
        self.args['infotype']="servergroup"
        return self.get_ngrepeat_data_servergroup()
        
    def get_ngrepeat_data_appdetails(self):
        '''
        self-privilege::获取主机组分类详情信息::主机管理-主机组管理-主机组管理页面前端自动加载
        '''
        self.args['type']="appdetails"
        self.args['infotype']="serverapp"
        return self.get_ngrepeat_data_servergroup()
        
    def get_ngrepeat_data_serverdetails(self):
        '''
        self-privilege::获取自定义任务信息::任务管理-自定义任务-自定义任务页面前端自动加载
        '''
        self.args['type']="serverdetails"
        self.args['infotype']="serverhost"
        return self.get_ngrepeat_data_servergroup()

    def get_ngrepeat_data_servergroup(self):
        '''
        self-privilege::获取主机组分类和主机组信息::主机管理-主机组管理-主机组管理页面前端自动加载
        '''
        line=self.args.get('line')
        product=self.args.get('product')
        app=self.args.get('app')
        type=self.args.get('type')
        group=self.args.get('group')
        servertype=self.args.get('infotype')
        searchlist=self.args.get('list')
        gettype=self.args.get('gettype')

        if type == 'serverprivilegedetails':
            info=user_table.get_server_privilege(line=line, product=product, app=app, group_id=group)
        else:
            if not servertype:
                servertype="serverapp"
    
            info=user_table.get_servergroup_info(line=line, product=product, app=app, group=group, type=servertype, searchlist=searchlist)
            if servertype == "serverapp":
                groupdata=user_table.get_servergroup_info(line=line, product=product, app=app, group=group, type='servergroup')

        new_info={}
        newinfo=[]
        for i in info:
            app=i.get('app')
            app_des=i.get('app_des')
            
            c_time=i.get('c_time')
            c_user=i.get('c_user')
            if  type == "appdetails":
                appinfo={'app':app, 'app_des':app_des, 'c_time':c_time, 'c_user':c_user}
                if appinfo not in newinfo:
                    newinfo.append(appinfo)
            elif type in ["groupdetails", 'serverprivilegedetails']:
                id=i.get('id')
                group_id=i.get('group_id')
                group_des=i.get('group_des')
                modal=i.get('modal')
                remark=i.get('remark')
                role=comm_lib.json_to_obj(i.get('role'))
                groupinfo={}
                if type == 'groupdetails':
                    groupinfo={'group_id':group_id, 'group_des':group_des, 'modal':modal, 'remark':remark, 'c_time':c_time, 'c_user':c_user}
                elif type == 'serverprivilegedetails' and role:
                    groupinfo={'role':role, 'c_time':c_time, 'c_user':c_user, 'id':id}

                if groupinfo not in newinfo and groupinfo:
                    newinfo.append(groupinfo)
                
            elif type == "serverdetails":
                group_id=i.get('group_id')
                member=i.get('member')
                modal=i.get('modal')
                asset_app=i.get('asset_app')
                hostinfo={'member':member, 'modal':modal, 'asset_app':asset_app, 'c_time':c_time, 'c_user':c_user}
                if hostinfo not in newinfo:
                    newinfo.append(hostinfo)
            else:
                #index=[]
                new_info.setdefault(app, {})
                new_info[app].setdefault('des', app_des)
                new_info[app].setdefault('group', [])
                for k in groupdata:
                    if k.get('app') != app:
                        continue
                    group=k.get('group_id')
                    group_des=k.get('group_des')
                    groupinfo={group:group_des}

                    if group and groupinfo not in new_info[app]['group']:
                        #index.append(groupdata.index(k))
                        new_info[app]['group'].append(groupinfo)
                
                #for l in index:
                #    del groupdata[l]

        if  type == "appdetails":
            if gettype == 'infoselect':
                return json.dumps(newinfo, ensure_ascii=False)
            else:
                return self.write(json.dumps(
                    self.get_pagination_data(newinfo, [{'app':'id'}, {'app_des':'描述'}, {'c_time':'操作时间'}, {'c_user':'操作用户'}])
                    , ensure_ascii=False))
        elif type in ["groupdetails", 'serverprivilegedetails']:
            if gettype == 'taskcreate':
                return self.write(json.dumps(newinfo, ensure_ascii=False))
            elif type == 'serverprivilegedetails':
                return self.write(json.dumps(
                    self.get_pagination_data(newinfo, [{'id':'id'}, {'role':'规则'}, {'c_time':'操作时间'}, {'c_user':'操作用户'}])
                    , ensure_ascii=False))
            else:
                return self.write(json.dumps(
                    self.get_pagination_data(newinfo, [{'modal':'模式'}, {'remark':'备注'}, {'group_id':'id'}, {'group_des':'描述'}, {'c_time':'操作时间'}, {'c_user':'操作用户'}])
                    , ensure_ascii=False))
        elif type == "serverdetails":
            if gettype == 'taskcreate':
                return self.write(json.dumps(newinfo, ensure_ascii=False))
            else:
                return self.write(json.dumps(
                    self.get_pagination_data(newinfo, [{'modal':'模式'}, {'asset_app':'资产应用类型'}, {'member':'成员'}, {'c_time':'操作时间'}, {'c_user':'操作用户'}])
                    , ensure_ascii=False))
        else:
            return self.write(json.dumps(new_info, ensure_ascii=False))
            
    def get_collecttemplate_history(self):
        '''
        self-privilege::搜索信息收集数据::任务管理-信息收集-信息收集-搜索
        '''
        name=self.args.get('name')
        date=self.args.get('datetime')
        template=user_table.get_collecttemplate_info()
        template={ i.get('template_id'):i for i in template}
        
        info=user_table.get_collecttemplate_history(template_id=name, c_time=date)
        { i.update({'des':template.get(i['template_id'])['des']}) for i in info}
        return self.write(json.dumps(self.get_pagination_data(info, [{'id':'id'}, {'template_id':'id'},  {'des':'名称'}, {'ip':'ip'}, {'c_time':'收集时间'}]), ensure_ascii=False))
        
    def get_ngrepeat_data_taskinfo(self):
        '''
        self-privilege::获取主机组详情信息::主机管理-主机组管理-主机组管理页面前端自动加载
        '''
        key=self.args.get('key')
        if key:
            info=user_table.get_task_info(key=key)
        else:    
            info=user_table.get_task_info()

        return self.write(json.dumps(self.get_pagination_data(info, [{'task_id':'id'}, {'filename':'文件名'}, {'des':'描述/名称'}, {'remark':'备注'}, {'c_time':'操作时间'}, {'c_user':'操作用户'}]), ensure_ascii=False))

    def get_ngrepeat_data_collecttemplatelist(self):
        '''
        self-privilege::获取信息收集模板信息::任务管理-信息收集-模板管理页面理前端自动加载
        '''
        return self.write(json.dumps(user_table.get_collecttemplate_info(), ensure_ascii=False))
        
    def get_ngrepeat_data_accountlist(self):
        '''
        self-privilege::获取通知管理主账号信息::权限管理-通知管理-主账号管理页面理前端自动加载
        '''
        self.args['dotype']='account'
        return self.write(json.dumps(self.get_privilegs(), ensure_ascii=False))

    def get_ngrepeat_data_contactlist(self):
        '''
        self-privilege::获取通知管理联系人信息::权限管理-通知管理-联系人管理页面理前端自动加载
        '''
        self.args['dotype']='contact'
        return self.write(json.dumps(self.get_privilegs(), ensure_ascii=False))

    def get_ngrepeat_data_userlist(self):
        '''
        self-privilege::获取用户列表::权限管理-用户组管理-用户管页面理前端自动加载
        '''
        self.args['dotype']='user'
        return self.write(json.dumps(self.get_privilegs(), ensure_ascii=False))

    def get_ngrepeat_data_taskhistoryinfo(self):
        '''
        self-privilege::获取任务记录::任务管理-任务记录-任务记录页面前端自动加载
        '''
        return self.write(json.dumps(self.get_task_history(), ensure_ascii=False))
        
    def getinfo_assetinfo(self):
        '''
        self-privilege::获取ip信息::主机管理-主机组管理-添加成员-输入ip搜索
        '''
        return self.write(json.dumps(self.get_asset_search_info(), ensure_ascii=False))
        
    def get_ngrepeat_data_grouplist(self):
        '''
        self-privilege::获取组列表::权限管理-用户组管理-组管理页面前端自动加载
        '''
        self.args['dotype']='group'
        return self.write(json.dumps(self.get_privilegs(), ensure_ascii=False))

    def get_ngrepeat_data_privilegepool(self):
        '''
        self-privilege::获取权限信息::权限管理-权限分配-权限列表页面前端自动加载
        '''
        self.args['dotype']='privilege'
        return self.write(json.dumps(self.get_privilegs(), ensure_ascii=False))

    def get_ngrepeat_data_privilegelist(self):
        '''
        self-privilege::获取组权限信息::权限管理-权限分配-权限分配页面前端自动加载
        '''
        self.args['dotype']='group'
        return self.write(json.dumps(self.get_privilegs(), ensure_ascii=False))

    def get_privilegs(self):
        dotype=self.args.get('dotype')
        dolist={
            'group':'get_group_info',
            'user':'get_user_info',
            'key':'get_verify_key_info',
            'account':'get_inform_account_info',
            'contact':'get_inform_contact_info',
            'privilege':'get_privilege_info',
            'privilegeinfo':'get_privilege_allocate_info'
        }
        usergroup=getattr(user_table, dolist['privilegeinfo'])(user=self.args['curruser'])
        group=''
        if usergroup:
            group=usergroup[0].get('name')
        data=getattr(user_table, dolist[dotype])()
        { i.update({'selfgroup':group}) for i in data }
        return data
        
    def get_task_history(self):
        data=self.args.get('data', {})

        status=data.get('status', '')
        date_end=data.get('date_end', '')
        date_start=data.get('date_start', '')
        task_type=data.get('relevanceapp', '')
        relevance_id=data.get('relevanceinfo', '')
        custominfo=data.get('custominfo', '')
        
        info=user_table.get_task_history(status=status, date_end=date_end, 
                    date_start=date_start, custominfo=custominfo, task_type=task_type, relevance_id=relevance_id)
                    
        for i in  info:
            execute_time=i.get('execute_time', '')
            create_time=i.get('create_time')
            if re.match(r'^00.*$', execute_time):
                timestatus=0
            else:
                execute_time=comm_lib.to_datetime_obj(i.get('execute_time'))
                sys_time=comm_lib.to_datetime_obj(str(datetime.datetime.now()).split('.')[0])
                timestatus=int(str((execute_time - sys_time).total_seconds()).split('.')[0])
            i.update({'timestatus':timestatus})    

        return self.get_pagination_data(info, [{'id':'id'}, {'relevance_id':'关联任务id'},
                                            {'timestatus':'任务倒计时时间'}, {'create_time':'任务创建时间'},
                                            {'custom_name':'自定义任务名'}, {'task_type':'任务分类'},  
                                            {'task_name':'任务名称'}, {'custom_type':'自定义分类名'}, 
                                            {'execute_time':'执行时间'}, {'status':'状态'},
                                            {'c_time':'创建时间'}, {'c_user':'操作用户'}])
    
    def commit_dialog_info_serverprivilege(self):
        '''
        self-privilege::主机组权限配置提交::主机管理-权限配置-权限配置按钮-提交
        '''
        id=self.args.get('id')
        name=self.args.get('name')
        data=self.args.get('data')
        if not id:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
        if not user_table.update_server_privilege(self.args['curruser'], privilege=json.dumps(data), id=id):
            return self.write(get_ret(-2, '提交失败', status='err'))
        return self.write(get_ret(0, '配置成功', status='info'))
        
    def commit_dialog_info_user(self):
        '''
        self-privilege::用户组变更提交信息::权限管理-用户组管理-用户管理-组变更-提交
        '''
        user=self.args.get('name')
        data=self.args.get('data')
        if not user:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))

        check=user_table.get_privilege_allocate_info()
        ckdt={ i['name']:i for i in check}

        allgroup=user_table.get_privilege_allocate_info(user=user)
        for i in allgroup:
            member=i.get('member')
            group=i.get('name')
            if not member:
                member=[]
            else:
                member=member.split(',')
            
            if group not in data:
                del member[member.index(user)]

            user_table.privilege_user_group_update(group, ','.join(member), 
                    self.args['curruser'], type="group_change")
            if  group in data:
                del data[data.index(group)]

        for i in data:
            group=i
            gdt=ckdt.get(group, {})
            if not gdt:
                continue
            member=gdt.get('member')
            if not member:
                member=[user]
            else:
                member=member.split(',')
                
            user_table.privilege_user_group_update(group, ','.join(member), 
                    self.args['curruser'], type="group_change")
        return self.write(get_ret(0, user + '组变更成功', status='info'))
    
    def get_dialog_info_serverprivilege(self):
        '''
        self-privilege::主机组权限配置::主机管理-权限配置-权限配置按钮
        '''
        prilist=['download', 'update', 'execute']
        id=self.args.get('id')
        if not id :
            return self.write(get_ret(-1, '参数错误', status='err'))
        d=user_table.get_server_privilege(id=id)
        privilege=comm_lib.json_to_obj(d[0].get('privilege'))
        if not privilege:
            privilege=[]
        return self.write(json.dumps({'leftdata':privilege, 'rightdata':prilist}, ensure_ascii=False))
        
    def get_dialog_info_group(self):
        '''
        self-privilege::用户组变更获取用户信息::权限管理-用户组管理-组管理-成员变更
        '''
        group=self.args.get('name', None)
        if not group:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
            
        member_list=[]    
        member_info=user_table.get_privilege_allocate_info(group=group)
        if member_info:
            if member_info[0]['member']:
                member_list=[ i.strip() for i in member_info[0]['member'].split(',') if i ]

        user_history=user_table.get_user_info()
        user_info=[ i['user'].strip() for i in user_history ]
        return self.write(json.dumps({'leftdata':member_list, 'rightdata':user_info}, ensure_ascii=False))
        
        
    def commit_dialog_info_group(self):
        '''
        self-privilege::用户组成员变更提交信息::权限管理-用户组管理-组管理-成员变更-提交
        '''
        data=self.args.get('data')
        group=self.args.get('name')
        if not group:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
        if not data:
            data=''
        if isinstance(data, dict):
            data=', '.join(data.keys())
        elif isinstance(data, list):
            data=', '.join(comm_lib.filter_int(data))
            
        if not user_table.privilege_user_member_update(group, data, self.args['curruser']):
            return self.write(get_ret(-2, group + '组成员变更失败', status='err'))
        return self.write(get_ret(0, group + '组成员变更成功', status='info'))   
            
    def commit_dialog_info_account(self):
        '''
        self-privilege::账号联系人变更提交::权限管理-通知管理-主账号管理-成员信息变更-提交
        '''
        data=self.args.get('data')
        name=self.args.get('name')
        type=self.args.get('type')
        if not name or not type:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
        if not data:
            data=''
        if isinstance(data, dict):
            data=','.join(data.keys())
        elif isinstance(data, list):
            data=','.join(comm_lib.filter_int(data))
            
        if not user_table.account_contact_info_update(name, type, data, self.args['curruser']):
            return self.write(get_ret(-2, name + '账号成员变更失败', status='err'))
            
        return self.write(get_ret(0, name + '账号成员变更成功', status='info'))   
          
    def commit_dialog_info_privilege(self):
        '''
        self-privilege::权限变更提交信息::权限管理-权限分配-权限分配-权限变更-提交
        '''
        data=self.args.get('data')
        group=self.args.get('name')
        if not group:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
        if not data:
            data=''
        if isinstance(data, dict):
            data=','.join(data.keys())
        elif isinstance(data, list):
            data=','.join(comm_lib.filter_int(data) 
                +  self.get_comm_privileges())
        if not user_table.privilege_peivilege_member_update(group, data, self.args['curruser']):
            return self.write(get_ret(-2, group + '组成员权限变更失败', status='err'))
        return self.write(get_ret(0, group + '组成员权限变更成功', status='info'))   
            
    def get_dialog_info_privilege(self):
        '''
        self-privilege::权限变更获取权限信息::权限管理-权限分配-权限分配-权限变更
        '''
        def find_mainpage_id(des):
            return privilege_set(['mainHandler'], findkey=des)
            
        group=self.args.get('name', None)
        if not group:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
            
        member_list=[]
        member_dict={}
        privilege_info={}
        member_history=user_table.get_privilege_allocate_info(group=group)
        if member_history:
            if member_history[0]['privi_list']:
                member_list=[ i.strip() for i in member_history[0]['privi_list'].split(',') if i ]

        privilege_history=user_table.get_privilege_info()

        finded={}
        for i in privilege_history:
            remark=i.get('remark')
            mainpageid=''
            if not re.match(r'.*-.*', remark):
                mainpageid=i.get('name')
                mainpagedes=i.get('des')
            elif re.match(r'.*主界面.*', remark.split('-')[0]):
                mainpageid=i.get('name')
                mainpagedes=i.get('des')
            else:
                mainpagedes=remark.split('-')[1]
                if mainpagedes not in finded:
                    mainpageid=find_mainpage_id(mainpagedes)
                    finded.update({mainpagedes:mainpageid})
                else:
                    mainpageid=finded.get(mainpagedes)
            if not mainpageid:
                mainpageid=i.get('name')
                mainpagedes=i.get('des')
            privilege_info.setdefault(mainpageid, {})
            privilege_info[mainpageid].setdefault('childlist', {})
            privilege_info[mainpageid].setdefault('des', mainpagedes)
            if i['name'] != mainpageid:
                privilege_info[mainpageid]['childlist'][i['name']]=i['des']
            if i['name'] in member_list:
                member_dict[i['name']]=i['des']

        return self.write(json.dumps({'leftdata':member_dict, 'rightdata':privilege_info}, ensure_ascii=False))
        
    def get_dialog_info_account(self):
        '''
        self-privilege::通知账号成员信息管理::权限管理-通知管理-主账号管理-成员信息管理
        '''
        account=self.args.get('name', None)
        type=self.args.get('type', None)
        if not account or not type:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
            
        member_list=[]    
        member_info=user_table.get_inform_account_info(name=account, type=type)
        if member_info:
            if member_info[0]['member']:
                member_list=[ i.strip() for i in member_info[0]['member'].split(',') if i ]

        contact_history=user_table.get_inform_contact_info(type=type)
        contact_info=[ i['name'].strip() for i in contact_history ]
        return self.write(json.dumps({'leftdata':member_list, 'rightdata':contact_info}, ensure_ascii=False))
        
    def getresult_serverinit(self):
        '''
        self-privilege::服务器初始化::资产管理-初始化管理-服务器初始化-搜索-初始化
        '''
        self.args['checktype']='serverinit'
        return self.login_check()
        
    def logincheck_logininitools(self):
        '''
        self-privilege::服务器初始化登录检测验证::资产管理-初始化管理-初始化登录管理-搜索-登录检测
        '''
        self.args['checktype']='logininitools'
        return self.login_check()
                
    def logincheck_logintools(self):
        '''
        self-privilege::服务器默认登录检测验证::资产管理-登录管理-默认登录管理-搜索-登录检测
        '''
        self.args['checktype']='logindefault'
        return self.login_check()
    def do_get_result(self):
        dotype=self.args.get('dotype')
        name=self.args.get('name')
        id=self.args.get('id')
        if not name:
            return self.write(get_ret(-1, '参数错误', status='err'))
            
        if dotype == "taskcustom":
            path=curr_path+os.sep+'task/%s' % name
            if not os.path.exists(path):
                return self.write(get_ret(-2, '任务文件路径不存在', status='err'))
            info=[ i[2] for i in os.walk(path)][0]

        elif dotype == "collecttemplatehistory":
            if not id:
                return self.write(get_ret(-1, '参数错误', status='err'))
            info=user_table.get_collecttemplate_history(template_id=name, id=id)
            text=[]
            if info:
                text=comm_lib.json_to_obj(info[0]['info'])
                if isinstance(text, dict):
                    #info=[ { k:v } for k,v in text.iteritems() ]
                    info=text
                elif text.find('=>') != -1 and text.find(':::') != -1:
                    info={ i.split('=>')[0]:i.split('=>')[1] for i in text.split(':::') if i } 

        ret=get_ret(0, '获取任务记录成功', status='info', isjson=False)
        ret.update({'data':info})
        return self.write(json.dumps(ret, ensure_ascii=False))
        
    def get_result_collecttemplatehistory(self):
        '''
        self-privilege::信息收集信息获取::任务管理-信息收集-信息收集-详情
        '''
        self.args['dotype']='collecttemplatehistory'
        return self.do_get_result()
        
    def get_result_taskcustom(self):
        '''
        self-privilege::自定义历史记录获取::任务管理-自定义任务-历史
        '''
        self.args['dotype']='taskcustom'
        return self.do_get_result()

    def logincheck_loginmanager(self):
        '''
        self-privilege::服务器登录检测验证::资产管理-登录管理-登录管理-搜索-登录检测
        '''
        self.args['checktype']='loginmanager'
        return self.login_check()
    
    def statuscheck_servergroup(self):
        '''
        self-privilege::主机组内成员客户端状态检测::主机管理-主机组管理-成员管理-组员客户端状态
        '''
        self.args['dotype']='groupcheck'
        self.args['task_type']='servergroup'
        return self.login_check()
        
    def statuscheck_groupmember(self):
        '''
        self-privilege::主机客户端状态检测::主机管理-主机组管理-客户端管理-客户端状态
        '''
        self.args['dotype']='membercheck'
        self.args['task_type']='servergroup'
        return self.login_check()
        
    def deploy_servergroup(self):
        '''
        self-privilege::部署组客户端::主机管理-主机组管理-成员管理-部署组员客户端
        '''
        self.args['dotype']='groupdeploy'
        self.args['task_type']='servergroup'
        return self.login_check()
        
    def deploy_groupmember(self):
        '''
        self-privilege::组成员部署客户端::主机管理-主机组管理-客户端管理-部署客户端
        '''
        self.args['dotype']='memberdeploy'
        self.args['task_type']='servergroup'
        return self.login_check()
        
        
    def get_server_login_info(self, iplist):
        if not isinstance(iplist, list):
            iplist=iplist.split(',')
        asset=user_table.assets_search(iplist=iplist)
        serverlogin=user_table.get_login_manager_info(iplist)
        serverlogin={ i['ip']:i for i in serverlogin}
        defaultlogin=user_table.get_login_default_info()
        key=self.login_check_key
        defaultlogin={ tuple([ i.get(k) for k in key]):i for i in defaultlogin}
        info={}
        
        def do_getlogin(k, kl , adt):
            d={}
            if k in kl:
                d['user']=kl[k].get('user')
                d['port']=kl[k].get('port')
                d['pwd']=kl[k].get('pwd')
                d['type']=kl[k].get('type')
                for kk in key:
                    d[kk]=adt.get(kk)
            return d
        
        for i in asset:
            ip=i.get('telecom_ip')
            #asset包含了 telecom_ip,unicom_ip,inner_ip 的信息,需要 telecom_ip的
            if ip not in iplist:
                continue

            info.setdefault(ip, {})
            dt=do_getlogin(ip, serverlogin, i)
            if dt:
                info[ip].update(dt)
            else:
                check_list=[ i.get(k) for k in key]
                check_key=tuple(check_list)
                #最小化匹配获取登录信息
                #owner-idc-app-product-line逐步放大匹配范围
                for l in range(0, len(check_key)):
                    dt=do_getlogin(check_key, defaultlogin, i)
                    if dt:
                        info[ip].update(dt)
                        break
                    check_list[len(check_list) - (l + 1)]=None
                    check_key=tuple(check_list)

        return info
         
    def get_servergroup_request(self):
        name=self.args.get('name')
        dotype=self.args.get('dotype')
        line=self.args.get('line')
        product=self.args.get('product')
        app=self.args.get('app')
        group=self.args.get('group')
        request={}
        request['request']="client_opertion"
        request['type']=dotype

        if not name:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
            
        if dotype == "groupdeploy" or dotype == "groupcheck":
            groupdata=user_table.get_servergroup_info(line=line, product=product, app=app, group=group, type='serverhost')
            iplist=[ i.get('member') for i in groupdata if i.get('member')]
        elif dotype == "membercheck" or dotype == "memberdeploy":
            iplist=[name]
            
        if not iplist:
            return get_ret(-3, "无主机信息,不需要检测",status='warn', isjson=False)
            
        request['iplist']=self.get_server_login_info(iplist)
        if not request['iplist']:
            return get_ret(-6, "获取登录信息失败,请先到登录管理进行配置",status='err', isjson=False)
        return request
        
    def login_check(self):
        task_type=self.args.get('task_type')
        if task_type =="servergroup":
            request=self.get_servergroup_request()
        else:
            request=self.get_logininfo()
            
        if request.get('code'):
            return self.write(request)
        
        ret=self.do_request_twisted(request, long=True)
        if ret == -9:
            return self.write(get_ret(-2, '请求twisted失败' ,status='err'))
        data=get_ret(0, '检测完成', isjson=False)
        data.update({'data':ret})
        return self.write(json.dumps(data))
            
    def get_asset_propety(self):
        line=self.args.get('line')
        product=self.args.get('product')
        app=self.args.get('app')
        idc=self.args.get('idc')
        owner=self.args.get('owner')
        return {
            'line':line,
            'product':product,
            'app':app,
            'idc':idc,
            'owner':owner
        }
        
    def get_logininfo(self):
        checktype=self.args.get('checktype')
        user=''
        port=''
        pwd=''
        logininfo=[]
        iplist=[]
        request={}
        request['request']='do_logincheck'
        request['c_user']=self.args['curruser']
        
        asset_propety=self.get_asset_propety()
    
        if checktype == "loginmanager":
            tip=self.args.get('name')
            if not tip:
                return get_ret(-1, "参数错误", status='err', isjson=False)
            info=user_table.get_login_manager_info(iplist=tip)
            for i in info:
                if i.get('ip') == tip:
                    logininfo=[i]
            iplist=[tip]
        elif checktype == "serverinit":
            iplist=self.args.get('iplist')
            self.args['type']=checktype
            request['request']=checktype
            logininfo=self.login_info_search()

        else:
            checkret=int()
            for k in self.login_check_key:
                if k in asset_propety:
                    checkret+=1
            if  checkret != len(self.login_check_key):
                return get_ret(-1, "参数错误", status='err', isjson=False)

            self.args['type']="logintools"
            logininfo=self.login_info_search()
            server_info=self.get_asset_search_info()
            for i in server_info:
                iplist.append(i.get('telecom_ip'))
                
        if not iplist:
            return get_ret(-2, '获取服务器信息失败', status='err', isjson=False)
            
        if not  logininfo:
            return get_ret(-3, '获取服务器登录信息失败', status='err', isjson=False)
            
        request['checktype']=checktype
        request['iplist']=iplist
        
        for k in self.login_check_key+['port', 'user', 'pwd' ,'type', 'tool_path']:
            kv=logininfo[0].get(k)
            if k == "tool_path" and kv:
                kv=curr_path+os.sep+kv
            
            request[k]=kv
             

        if not request['user'] or not request['port'] or not request['pwd']:
            return get_ret(-1, '获取登录信息失败[%s]' % ip, status='err', isjson=False)
        elif checktype == "serverinit" and (
            not request['tool_path'] or not os.path.exists(str(request['tool_path']))):
            return get_ret(-4, '获取初始化工具失败', status='err', isjson=False)
            
        return request
        
    def get_dialog_info_user(self):
        '''
        self-privilege::用户组变更获取组信息::权限管理-用户组管理-用户管理-组变更
        '''
        user=self.args.get('name', None)
        if not user:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
            
        user_group_info={}
        group_info={}
        user_group_list=[]
        
        owner_group_info=user_table.get_privilege_allocate_info(user=user)
        user_group_list=[ i['name'].strip() for i in owner_group_info if i['name']]

        group_history=user_table.get_group_info()
        for i in group_history:
            group_info[i['name']]=i['des']
            if i['name'] in user_group_list:
                user_group_info[i['name']]=i['des']
            
        return self.write(json.dumps({'leftdata':user_group_info, 'rightdata':group_info}, ensure_ascii=False))
        
    def get_opertion_dialog_html(self):
        '''
        self-privilege::获取操作会话框::组变更/成员变更等
        '''
        title=self.args.get('title')
        title_left=self.args.get('left_title')
        title_right=self.args.get('right_title')
        type=self.args.get('type')
        name=self.args.get('name')
        context={
            'title':title, 
            'title_left':title_left, 
            'title_right':title_right, 
            'type':type, 
            'name':name}
        return self.write(tj_render('templates/opertion_dialog.html', context))
        
    def get_ngrepeat_data_keylist(self):
        '''
        self-privilege::获取key列表::权限管理-key管理-key管理页面前端自动加载
        '''
        self.args['dotype']='key'
        return self.write(json.dumps(self.get_privilegs(), ensure_ascii=False))

    def do_delete_info(self):
        name=self.args.get('name')
        success=self.args.get('success')
        err=self.args.get('err')
        dtype=self.args.get('dtype')
        type=self.args.get('type')
        filename=self.args.get('filename')
        id=self.args.get('id')
        ret=True
        if not name:
           return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
           
        if dtype == 'group':
            if name =="admin":
                return self.write(get_ret(-3, '你不能删除admin组', status='err'))
            ret=user_table.delete_group_info(name)
        elif dtype == 'contact':
            ret=user_table.delete_contact_info(name)
        elif dtype == 'key':
            if name =="verify_key":
                return self.write(get_ret(-3, '你不能删除key[verify_key]', status='err'))
            ret=user_table.delete_key_info(name)
        elif dtype == 'user':
            if name =="admin":
                return self.write(get_ret(-3, '你不能删除admin用户', status='err'))
            if not user_table.delete_user_info(name) or not user_table.delete_privilege_member(name, self.args['curruser']):
                ret=False
        elif dtype == 'serverprivilege':
            ret=user_table.del_server_privilege(id=id)
        elif dtype == 'taskhistory':
            ret=user_table.task_status_update('status', self.args['curruser'], status='done', task_name=name)
        elif dtype == 'collecttemplatehistory':
            ret=user_table.delete_collecttemplate_history(template_id=name, id=id)
        elif dtype == 'taskrelevancehistory':
            ret=user_table.delete_task_relevance_info(relevance_id=name) 
        elif dtype == 'collecttemplate':
            if name == 'platform_history':
                return self.write(get_ret(-3, '不能删除platform_history', status='err'))
            ret=user_table.delete_collecttemplate_info(name)  
        elif dtype == 'taskcustom':
            if type == "file":
                file_path=curr_path+os.sep+'task/%s/%s' % (name, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
                ret=True
            else:
                ret=user_table.delete_task_info(name)
        elif dtype == 'account':
            user_table.delete_account_info(name, type=type)
        elif dtype in ['serverhost', 'servergroup', 'serverapp']:
            if dtype== "serverhost":
                ret=user_table.delete_servergroup_info(member=name, type=dtype)
            elif dtype =='servergroup':
                ret=user_table.delete_servergroup_info(group_id=name, type=dtype)
            elif dtype =='serverapp':
                ret=user_table.delete_servergroup_info(app=name, type=dtype)

        if not ret:
            return self.write(get_ret(-2, err, status='err'))
        return self.write(get_ret(0, success, status='info'))   
         
    def delete_serverprivilege_info(self):
        '''
        self-privilege::删除主机组权限规则::主机管理-权限配置-删除
        '''
        self.args['success']='删除规则成功'
        self.args['err']='删除规则失败'
        self.args['dtype']='serverprivilege'
        return self.do_delete_info()
        
    def delete_taskhistory_info(self):
        '''
        self-privilege::修改任务记录为完成状态::任务管理-任务记录-确认完成
        '''
        self.args['success']='修改任务状态成功'
        self.args['err']='修改任务状态失败'
        self.args['dtype']='taskhistory'
        return self.do_delete_info()
        
    def delete_taskrelevancehistory_info(self):
        '''
        self-privilege::删除关联任务记录::任务管理-任务创建-删除
        '''
        self.args['success']='删除关联任务记录成功'
        self.args['err']='删除关联任务记录失败'
        self.args['dtype']='taskrelevancehistory'
        return self.do_delete_info()
        
    def delete_collecttemplatehistory_info(self):
        '''
        self-privilege::删除信息收集记录::任务管理-信息收集-信息收集-删除
        '''
        self.args['success']='删除信息收集记录成功'
        self.args['err']='删除信息收集记录失败'
        self.args['dtype']='collecttemplatehistory'
        return self.do_delete_info()
        
    def delete_collecttemplate_info(self):
        '''
        self-privilege::删除信息收集模板及记录::任务管理-信息收集-模板管理-删除
        '''
        self.args['success']='删除信息收集模板及记录成功'
        self.args['err']='删除信息收集模板及记录失败'
        self.args['dtype']='collecttemplate'
        return self.do_delete_info()
        
    def delete_taskcustom_info(self):
        '''
        self-privilege::删除自定义任务信息::任务管理-自定义任务-删除
        '''
        tid=self.args.get('task_id')
        self.args['success']='删除自定义任务 %s 成功' % tid
        self.args['err']='删除自定义任务 %s 失败' % tid
        self.args['dtype']='taskcustom'
        return self.do_delete_info()
        
    def delete_groupmember_info(self):
        '''
        self-privilege::删除主机组成员::主机管理-主机组管理-主机成员界面-删除
        '''
        member=self.args.get('serverhost')
        self.args['success']='删除组 %s 成功' % member
        self.args['err']='删除组 %s 失败' % member
        self.args['dtype']='serverhost'
        return self.do_delete_info()
        
    def delete_servergroup_info(self):
        '''
        self-privilege::删除主机组::主机管理-主机组管理-主机组界面-删除
        '''
        group_id=self.args.get('group_id')
        self.args['success']='删除主机组 %s 成功' % group_id
        self.args['err']='删除主机组 %s 失败' % group_id
        self.args['dtype']='servergroup'
        return self.do_delete_info()
        
        
    def delete_serverapp_info(self):
        '''
        self-privilege::删除主机类型::主机管理-主机组管理-主机类型界面-删除
        '''
        app=self.args.get('app')
        self.args['success']='删除主机类型 %s 成功' % app
        self.args['err']='删除主机类型 %s 失败' % app
        self.args['dtype']='serverapp'
        return self.do_delete_info()
        
        
    def delete_group_info(self):
        '''
        self-privilege::删除组::权限管理-用户组管理-组管理-删除
        '''
        group=self.args.get('name')
        self.args['success']='删除组 %s 成功' % group
        self.args['err']='删除组 %s 失败' % group
        self.args['dtype']='group'
        return self.do_delete_info()
        
    def delete_contact_info(self):
        '''
        self-privilege::删除通知联系人::权限管理-通知管理-联系人管理-删除
        '''
        contact=self.args.get('name')
        self.args['success']='删除联系人 %s 成功' % contact
        self.args['err']='删除联系人 %s 失败' % contact
        self.args['dtype']='contact'

        return self.do_delete_info()

    
    def delete_account_info(self):
        '''
        self-privilege::删除通知账号::权限管理-通知管理-主账号管理-删除
        '''
        account=self.args.get('name')
        self.args['success']='删除账号 %s 成功' % account
        self.args['err']='删除账号 %s 失败' % account
        self.args['dtype']='account'

        return self.do_delete_info()

    def delete_key_info(self):
        '''
        self-privilege::删除key::权限管理-key管理-key管理-删除
        '''
        key=self.args.get('name')
        self.args['success']='删除key %s 成功' % key
        self.args['err']='删除key %s 失败' % key
        self.args['dtype']='key'

        return self.do_delete_info()

        
    def modify_key_info(self):
        '''
        self-privilege::修改key信息::权限管理-key管理-key管理-修改
        '''
        name=self.args.get('name')
        value=self.args.get('data')
        if not value or not name:
           return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
        
        if not user_table.modify_key_info(name, value, self.args['curruser']):
            return self.write(get_ret(-2, '修改key %s 失败' % name, status='err'))
        
        return self.write(get_ret(0, '修改key %s 成功' % name, status='info'))
        
    def delete_user_info(self):
        '''
        self-privilege::删除用户::权限管理-用户组管理-用户管理-删除
        '''
        self.args['success']='删除用户成功'
        self.args['err']='删除用户失败'
        self.args['dtype']='user'
        return self.do_delete_info()
    
    def get_asset_keylist(self, type, other_key=None, line=None, product=None, app=None, idc=None):
        def check(d, k):
            ret=True
            clist={}
            if k == "idc":
                clist={'line':line, 'product':product, 'app':app}
            elif k == "product":
                clist={'line':line}
            elif k == "app":
                clist={'line':line, 'product':product}
            for k,v in clist.items():
                if d[k] != v and v:
                    ret=False

            return ret
    
        info=user_table.get_assets()
        keylist=[]
        checklist=[]
        for i in info:
            newlist={}
            if type in ['line', 'product', 'app', "idc"]:
                desinfo=i['describe'].split('-')
                if i[type] in checklist or not check(i, type):
                    continue
                                     
                if type == "idc":
                    newlist['des']=i['idc']
                elif type == "line":
                    newlist['des']=desinfo[0]
                elif type == "product":
                    newlist['des']=desinfo[1]
                elif type == "app":
                    newlist['des']=desinfo[2]
  
                checklist.append(i[type])
                newlist['key']=i[type]
                newlist['line']=i['line']
                newlist['product']=i['product']
                newlist['app']=i['app']

            elif type == "other":
                if other_key and other_key in i.keys():
                    if i[other_key] in checklist:
                        continue
                    
                    checklist.append(i[other_key])
                    newlist['key']=other_key
                    newlist['des']=other_key+":"+str(i[other_key])
                    
            keylist.append(newlist)  
        return keylist
        
    def get_asset_search_info(self):
        line=self.args.get('line')
        product=self.args.get('product')
        app=self.args.get('app')
        idc=self.args.get('idc')
        other_key=self.args.get('other_key')
        type=self.args.get('type')
        iplist=get_list(self.args.get('iplist'))
        name=self.args.get('name')

        if name ==  "history":
            info=user_table.assets_history_search(line=line, product=product, 
                                        app=app, idc=idc, other_key=other_key,
                                        iplist=iplist)
        else:
            if name in ['logindefault', 'logintools', 'logininit', 'initoolsmanager']:
                key=','.join(self.login_check_key)
            else:
                key=[]
            info=user_table.assets_search(line=line, product=product, 
                                        app=app, idc=idc, other_key=other_key,
                                        iplist=iplist, key=key)
        return info
        
    def modify_assetmanager_info(self):
        '''
        self-privilege::资产信息修改::资产管理-资产管理-详情修改-提交
        '''
        ip=self.args.get('ip')
        data=self.args.get('data')
        message=''
        if not data or not ip:
            return self.write(get_ret(-1, '获取IP信息失败,参数错误', status='err'))
            
        for k,v  in data.items():
            if not v:
                v=''
            if k not in self.asset_key:
                message="电信IP[%s]格式不对, 请传送正确的字段类型." % ip
                break;
                
            if k == "telecom_ip" and not re.match(r'^([0-9]+.){3}[0-9]+$', v): 
                message="电信IP[%s]格式不对, 请填写正确格式的IP地址." % ip
                break
                
            if k in ['line', 'product', 'app', 'describe']:
                if not v:
                    message="电信IP[%s]的line/product/app/describe字段不能为空." % ip
                    break

                if (re.match(r'[^-_\d\w]+', v) and k != "describe") or (k == "describe" and v.count('-') != 2):
                    message="电信IP[%s]的line/product/app/describe字段不满足规范, 请安装资产模板说明填写." % ip
                    break

        if message:
            return self.write(get_ret(-2, message, status='err'))
        #登录密码的ip也跟着改变
        if data.get('telecom_ip'):
            user_table.modify_loginmanager_ip(ip, data['telecom_ip'], self.args['curruser'])
        if data.get('telecom_ip') or data.get('app'):
            #修改主机主信息,这里只修改ip和代理信息,其他变更需要使用主机组管理的迁移功能
            user_table.modify_servergroup_info(ip=ip, c_user=self.args['curruser'], member=data.get('telecom_ip'),
                                                asset_app=data.get('app'), type="hostchange")
                                                
        if not user_table.modfiy_asset_info(ip, data, self.args['curruser']):
            return self.write(get_ret(-3, 'IP[%s]资产信息修改失败' % ip, status='err'))
            
        return self.write(get_ret(0, 'IP[%s]资产信息修改成功' % ip, status='info'))
        
    def loginmanager_detail(self):
        '''
        self-privilege::单个服务器登录信息查询::资产管理-登录管理-登录管理-搜索-服务器详情
        '''
        info=self.get_asset_search_info()
        tip=self.args.get('iplist')
        context={}
        context['data']=[ i for i in info if i['telecom_ip'] == tip ]
        context['key']=self.assets_templeat_keys
        return self.write(json.dumps(context, ensure_ascii=False))
        
    def assethistory_detail(self):
        '''
        self-privilege::查询资产变更详情::资产管理-资产管理-资产变更记录-详情
        '''
        id=self.args.get('id')
        if not id:
            return self.write(get_ret(-1, '获取IP信息失败,参数错误', status='err'))
        info=user_table.assets_history_search(key='id', key_value=id)
        context={}
        context['data']=info
        context['key']=self.assets_templeat_keys
        return self.write(json.dumps(context, ensure_ascii=False))
        
    def get_asset_info(self):
        '''
        self-privilege::查询资产详情::资产管理-资产管理-详情修改
        '''
        ip=self.args.get('ip')
        if not ip:
            return self.write(get_ret(-1, '获取IP信息失败,参数错误', status='err'))
        self.args['iplist']=ip
        info=self.get_asset_search_info()
        #字典无序,由前端控制显示格式
        new_info={}
        new_info['data']=info
        new_info['key']=self.assets_templeat_keys

        return self.write(json.dumps(new_info, ensure_ascii=False))
        
    def assets_tatistics(self, data):
        other_key=self.args.get('other_key')
        check_key=['line', 'product', 'app', 'idc', 'other_key']
        new_data=[]
        info_line={}

        for i in data:
            key_index=[]
            for k in check_key:
                if k == 'other_key':
                    key_index.append(other_key)
                else:
                    key_index.append(i.get(k))

            index=tuple(key_index)
            info_line.setdefault(index,int())
            info_line[index]+=1

        for k,v in info_line.items():
            new_info={}
            keylist=list(k)
            for i in range(0,len(check_key)):
                new_info[check_key[i]]=keylist[i]
            new_info['count']=v
            new_data.append(new_info)

        return new_data
    
    def serverinit_reset(self):
        '''
        self-privilege::服务器初始化状态重置为失败::资产管理-初始化管理-服务器初始化-搜索-设为失败
        '''
        ip=self.args.get('ip')
        if not ip:
            return self.write(get_ret(-1, '参数错误', status='err'))
        if not user_table.serverinit_reset(ip):
            return self.write(get_ret(-1, '%s初始化状态设置失败' % ip, status='err'))
        return self.write(get_ret(0, '%s初始化状态设置成功' % ip, status='info'))

    def fault_searchinfo(self):
        '''
        self-privilege::故障处理信息查找::任务管理-故障处理-搜索
        '''
        name=self.args.get('name')
        status=self.args.get('status')
        htime=self.args.get('htime')
        zone=self.args.get('zone')
        iplist=self.args.get('iplist')
        info=user_table.get_fault_info(name=name, 
                status=status, h_time=htime, zone=zone, iplist=iplist)
        
        self.write(json.dumps(self.get_pagination_data(info, [{'id':'id'}, {'ip':'ip'}, {'name':'名称'}, {'status':'状态'}, {'zone_name':'故障key'}, {'faultdes':'详情'}, {'remark':'处理记录'}, {'h_time':'发生时间'}, {'c_time':'处理时间'}, {'c_user':'处理人'}]), ensure_ascii=False)) 
        
    def serverinit_searchinfo(self):
        '''
        self-privilege::服务器初始化查询::资产管理-初始化管理-服务器初始化-搜索
        '''
        self.args['type']='getserverinit'
        self.args['name']='getserverinit'
        return self.login_searchinfo()

    def logininit_searchinfo(self):
        '''
        self-privilege::服务器初始化登录信息查询::资产管理-初始化管理-初始化登录管理-搜索
        '''
        self.args['type']='logininit'
        self.args['name']='logininit'
        return self.login_searchinfo()

    def initoolsmanager_searchinfo(self):
        '''
        self-privilege::初始化工具信息查询::资产管理-初始化管理-初始化工具管理-搜索
        '''
        self.args['type']='initoolsmanager'
        self.args['name']='initoolsmanager'
        return self.login_searchinfo()
        
    def login_searchinfo(self):
        info=self.login_info_handle()
        if self.args.get('type')=='initoolsmanager':
            logininfokeys=self.login_info_display_keys[:-3]
            logininfokeys.append({'tool_path':'工具路径'})
        elif self.args.get('type')=='getserverinit':
            logininfokeys=self.assets_templeat_keys
            #为了和前端ng-repeat数据对齐
            del logininfokeys[logininfokeys.index({'c_time':'操作时间'})]
            del logininfokeys[logininfokeys.index({'c_user':'操作用户'})]
            logininfokeys.append({'tool_path':'初始化工具'})
            logininfokeys.append({'status':'状态'})
            logininfokeys.append({'c_time':'操作时间'})
            logininfokeys.append({'c_user':'操作人'})
        else:
            logininfokeys=self.login_info_display_keys

        data=self.get_pagination_data(info, logininfokeys)
        return self.write(json.dumps(data, ensure_ascii=False))
        
    def logindefault_searchinfo(self):
        '''
        self-privilege::默认登录信息查询::资产管理-登录管理-默认登录管理-搜索
        '''
        self.args['type']='logindefault'
        self.args['name']='logindefault'
        return self.login_searchinfo()

    def logintools_searchinfo(self):
        '''
        self-privilege::动态登录信息查询::资产管理-登录管理-动态登录管理-搜索
        '''
        self.args['type']='logintools'
        self.args['name']='logintools'
        return self.login_searchinfo()

    def login_info_handle(self):
        type=self.args.get('type')

        if type == 'getserverinit' :
            initype=self.args.get('initype')
            #服务器初始化查询记录为1,2时候直接返回数据库取的信息
            if initype and initype != '1':
                return self.login_info_search()

        info=self.get_asset_search_info()
        new_info=[]
        login_info=self.login_info_search()
        info_keys=self.login_check_key


        if type == 'getserverinit' :
            login_info={ i['telecom_ip']:i for i in login_info }
            #return [ i for i in info if i.get('telecom_ip') not in login_info ]
            for i in info :
                if i.get('telecom_ip') not in login_info :
                    i.update({
                        'tool_path':'',
                        'status':'未初始化',
                        'c_time':'',
                        'c_user':''
                    })
                    new_info.append(i)
            return new_info
            
        #[{}, {}]类型不能使用set去重
        for i in info:
            if i not in new_info:
                new_info.append(i)

        for i in new_info:
            logininfo=''
            tlps=''
            for k in login_info:
                if [ i.get(j) for j in info_keys] == [ u'' if str(k.get(j,u'')) == 'None'  else k.get(j)  for j in info_keys ]:
                    if type == "initoolsmanager":
                        if k.get('tool_path'):
                            tlps=k.get('tool_path').split(os.sep)[-1]
                        else:
                            tlps='未设置'
                        i.update({'tool_path': tlps})
                        continue
                    if k.get('user'):
                        user=k.get('user').split(os.sep)[-1]
                    else:
                        user=k.get('user')
                    if k.get('port'):
                        port=k.get('port').split(os.sep)[-1]
                    else:
                        port=k.get('port')
                    if k.get('pwd'):
                        pwd=k.get('pwd').split(os.sep)[-1]
                    else:
                        pwd=k.get('pwd')
                        
                    logininfo={
                        'user':user,
                        'port':port,
                        'pwd':pwd
                    }
                    i.update(logininfo)

            if type == "initoolsmanager" and not tlps:
                i.update({'tool_path': '未设置'})
                continue

            if not login_info or not logininfo:
                logininfo={
                    'user':'未设置',
                    'port':'未设置',
                    'pwd':'未设置'
                }
                i.update(logininfo)

        return new_info
                    
    def loginmanager_searchinfo(self):
        '''
        self-privilege::单台服务器登录信息查询::资产管理-登录管理-登录管理-搜索
        '''
        info=self.get_asset_search_info()
        iplist=get_list(self.args.get('iplist'))
        #只返回满足要求的电信IP信息
        info=[ i for i in info if i['telecom_ip'] in iplist]
        
        self.args['type']='loginmanager'
        login_info={ i['ip']:i for i in self.login_info_search()}
        
        for i in info:
            if i['telecom_ip'] in login_info:
                logininfo={
                    'user':login_info[i['telecom_ip']]['user'],
                    'port':login_info[i['telecom_ip']]['port'],
                    'pwd':login_info[i['telecom_ip']]['pwd']
                }
            else:
                logininfo={
                    'user':'未设置',
                    'port':'未设置',
                    'pwd':'未设置'
                }
            i.update(logininfo)

        data=self.get_pagination_data(info, self.get_asset_history_key('loginmanager'))

        return self.write(json.dumps(data, ensure_ascii=False))
        
    def login_info_search(self):
        type=self.args.get('type')
        line=self.args.get('line')
        product=self.args.get('product')
        app=self.args.get('app')
        idc=self.args.get('idc')
        owner=self.args.get('other_key')
        if owner:
            if owner.find(':')  == -1:
                owner=''
            else:
                owner=owner.split(':')[1]
            
        iplist=get_list(self.args.get('iplist'))
        
        if type == "loginmanager":
            if not iplist:
                return []
            return user_table.get_login_manager_info(iplist=iplist)
        elif type == 'getserverinit':
            initype=self.args.get('initype')
            return user_table.get_serverinit_history(iplist, type=initype)
            
        elif type == 'serverinit':
            return user_table.get_login_default_info(line=line,
                                product=product, app=app, idc=idc,
                                owner=owner, type='logininit', name='logininit')
                                
        elif type in ['logininit', 'logininitools']:
            return user_table.get_login_default_info(line=line,
                                product=product, app=app, idc=idc,
                                owner=owner, type=type, name=type)
        elif type in ['logindefault', 'logintools', 'logininit', 'initoolsmanager']:
            return user_table.get_login_default_info(line=line,
                                product=product, app=app, idc=idc,
                                owner=owner, type=type)
        else:
            return []
        
    def assetstatistics_searchinfo(self):
        '''
        self-privilege::统计资产信息::资产管理-资产管理-资产统计-搜索
        '''
        self.args['name']='tatistics'
        info=self.get_asset_search_info()
        display_keys=self.get_asset_history_key('tatistics')
        data=self.get_pagination_data(self.assets_tatistics(info), display_keys)
        return self.write(json.dumps(data, ensure_ascii=False))

    def get_asset_history_key(self, name):
        if name =="history":
            key=self.asset_history_keys
        elif name == "tatistics":
            key=self.asset_tatistics_keys
        elif name == "loginmanager":
            key=self.loginmanager_key
        elif name == "logindefault" or name == "logintools":
            key=self.logindefault_key
            
        new_keys=[]
        for i in key:
            k=i.keys()[0]
            v=i[k]
            new_keys.append({k:v})
        return new_keys
        
    def assetchangehistory_searchinfo(self):
        '''
        self-privilege::查询资产变更记录::资产管理-资产管理-资产变更记录-搜索
        '''
        self.args['name']='history'
        info=self.get_asset_search_info()
        display_keys=self.get_asset_history_key('history')

        data=self.get_pagination_data(info, display_keys)
        return self.write(json.dumps(data, ensure_ascii=False))
        
    def assetfilter_searchinfo(self):
        '''
        self-privilege::查询资产信息::资产管理-资产管理-搜索
        '''
        info=self.get_asset_search_info()
        display_keys=self.get_asset_template_keys()
        data=self.get_pagination_data(info, display_keys)
        return self.write(json.dumps(data, ensure_ascii=False))

    def get_pagination_data(self, info, key):
        pageid=self.args.get('pageid')
        new_info=[]

        if pageid:
            start=(int(pageid) - 1) * self.page_line_length
            end=int(pageid) * self.page_line_length
            pid=int(pageid)
            id_count=int()
        else:
            #返回前3页数据  3*self.page_line_length
            pid=1
            id_count=int()
            start=0
            end=self.page_line_length * 3

        data=info[start:end]
        data_len=len(info)
        for i in data:
            asset={}
            asset['list']=[]
            
            id_count+=1
            if str(id_count % self.page_line_length) == '1' and str(id_count) != '1':
                pid+=1
            asset['pid']=pid
            if pageid:
                asset['pagination']='1'
            else:
                asset['pagination']='0'
            #确保数据位置和display_keys的对齐,配合angularjs  ng-repeat使用
            for k in key:
                new_asset={}
                new_asset['key']=k.keys()[0]
                new_asset['value']=i.get(k.keys()[0])
                asset['list'].append(new_asset)
    
            new_info.append(asset)

        context={}
        context['data']=new_info
        context['tr_len']=self.page_line_length
        context['data_len']=data_len
        
        return context
        
    def check_login_info(self, data):
        user=data.get('user')
        port=data.get('port')
        pwd=data.get('pwd')
        line=data.get('line')
        product=data.get('product')
        app=data.get('app')
        idc=data.get('idc')
        owner=data.get('owner')
        type=data.get('type')
        id=self.args.get('id')
        
        app_des=data.get('app_des')
        group_id=data.get('group_id')
        group_des=data.get('group_des')
        modal=data.get('modal')
        remark=data.get('remark')
        groupmember=data.get('member')
        hostlabel=data.get('lable')

        tool_path=data.get('tool_path')
        if id in ['loginuser', 'loginport', 'loginpwd']:
            save_file=self.args.get('save_file')
            if not save_file or (self.args.get('loginuser') and not user or
                    self.args.get('loginport') and not port or self.args.get('loginpwd') and not pwd):
                return self.write(get_ret(-1, '参数错误' , status="err"))

            if id == "loginuser":
                user=save_file
            elif id =="loginport":
                port=save_file
            elif id =="loginpwd":
                pwd=save_file
        elif id == "initoolsmanager":
            if not tool_path:
                return {'code':-4,'message':'参数错误, 不完整'}

        elif type in ['serverapp', 'servergroup', 'serverhost' , 'hostlabel', 'serverappremoval', 'servergroupremoval', 'groupmemberremoval']:
            if (not line or not product or not app) or (type in ["servergroup", 'servergroupremoval', 'groupmemberremoval'] and not group_id) or (type in ["serverhost", "hostlabel", 'groupmemberremoval'] and  not groupmember):
                return {'code':-4,'message':'参数错误, 不完整'}
            
        else:
            if not user or not port or not pwd:
                return {'code':-2,'message':'登录信息设置失败,user/port/pwd不能为空'}
            if type != "loginmanager" and (not line or not product or not app or not idc):
                return {'code':-4,'message':'参数错误, 不完整'}

            try:
                pwd=encrypt.decode_pwd(data.get('pwd'))
            except:
                pwd=data.get('pwd')
            pwd=encrypt.en_pwd(pwd)
            
        dt={}
        for k in ['line', 'product', 'app', 'idc', 'owner', 'user', 'port', 'pwd', 'tool_path', 
            'app_des', 'group_id', 'group_des', 'remark', 'modal', 'groupmember', 'hostlabel']:
            if locals().get(k):
                dt[k]=locals().get(k)

        return dt
        
    def do_loginfo_modify(self):
        dotype=self.args.get('dotype')
        data=comm_lib.json_to_obj(self.args.get('data'))
        data['type']=dotype
        ip=data.get('telecom_ip')
        success=self.args.get('success')
        err=self.args.get('err')
        ret=True
        
        if dotype == 'loginmanager' and not ip:
            return self.write(get_ret(-1, '参数错误, 不完整' , status="err"))
            
        if dotype == 'initoolsmanager':
            data['tool_path']=self.args.get('save_file')
            
        logininfo=self.check_login_info(data)

        if logininfo.get('code'):
            return self.write(get_ret(logininfo.get('code'), logininfo.get('message'), status="err"))
            
        if dotype == 'loginmanager':
            if not user_table.modify_loginmanager_info(ip, logininfo.get('user'), 
                        logininfo.get('port'), 
                        logininfo.get('pwd'), self.args['curruser']):
                ret=False
                
        elif dotype == "logininitools":
            if not user_table.modify_logininit_info(self.args['curruser'], logininfo, type=data['type']):
                ret=False
                
        elif dotype in ['logintools', 'logindefault']:
            if not user_table.modify_logindefault_info(self.args['curruser'], logininfo, type=data['type']):
                ret=False
                
        elif dotype == 'initoolsmanager':
            if not user_table.modify_initoolsmanager_info(self.args['curruser'], logininfo, type=data['type']):
                ret=False
                
        elif dotype == 'logininit':
            if not user_table.modify_logininit_info(self.args['curruser'], logininfo, type=data['type']):
                ret=False
        elif dotype in ['serverapp', 'servergroup', 'serverhost', 'hostlabel', 'serverappremoval', 'servergroupremoval', 'groupmemberremoval']:
            if not user_table.modify_servergroup_info(line=logininfo.get('line'), product=logininfo.get('product'), 
                app=logininfo.get('app'), asset_app=logininfo.get('asset_app'), remark=logininfo.get('remark'), 
                app_des=logininfo.get('app_des'), group_id=logininfo.get('group_id'), 
                group_des=logininfo.get('group_des'),modal=logininfo.get('modal'), 
                member=logininfo.get('groupmember'), label=json.dumps(logininfo.get('hostlabel'), ensure_ascii=False), type=dotype, c_user=self.args['curruser'], olddata=self.args.get('old')):
                ret=False

        if not ret:
            return self.write(get_ret(-5, err , status="err"))
            
        return self.write(get_ret(0, success))
        
    def modify_taskhistory_info(self):
        '''
        self-privilege::任务执行时间修改::任务管理-任务记录-修改时间
        '''
        self.args['checktype']='modifycheck'
        self.task_exectime_check()
        if self.args.get('errorinfo'):
            return self.write(json.dumps(self.args.get('errorinfo'), ensure_ascii=False))
        task_name=self.args.get('name')
        execute_time=self.args.get('execute_time')
        if not task_name or not execute_time:
            return self.write(get_ret(-1, '参数错误', status='error'))
        if not user_table.task_status_update('timemodify', self.args['curruser'],
                                    task_name=task_name, execute_time=self.args.get('execute_time')):
            return self.write(get_ret(-2, '修改执行时间失败', status='error'))
        return self.write(get_ret(0, '修改执行时间成功', status='info'))
        
    def modify_serverappremoval_info(self):
        '''
        self-privilege::主机组分类迁移::主机管理-主机组管理-分类管理-迁移
        '''
        self.args['dotype']='serverappremoval'
        self.args['success']='主机组分类迁移成功'
        self.args['err']='主机组分类迁移失败'
        return self.do_loginfo_modify()
        
    def modify_servergroupremoval_info(self):
        '''
        self-privilege::主机组迁移::主机管理-主机组管理-主机管理-迁移
        '''
        self.args['dotype']='servergroupremoval'
        self.args['success']='主机组迁移成功'
        self.args['err']='主机组迁移失败'
        return self.do_loginfo_modify()
        
    def modify_groupmemberremoval_info(self):
        '''
        self-privilege::主机组成员迁移::主机管理-主机组管理-成员管理-迁移
        '''
        self.args['dotype']='groupmemberremoval'
        self.args['success']='主机组成员迁移成功'
        self.args['err']='主机组成员迁移失败'
        return self.do_loginfo_modify()
        
    def modify_groupmember_info(self):
        '''
        self-privilege::修改主机组成员信息::主机管理-主机组管理-成员管理-详情/变更
        '''
        self.args['dotype']='serverhost'
        self.args['success']='主机成员信息设置成功'
        self.args['err']='主机成员信息设置失败'
        return self.do_loginfo_modify()
        
    def modify_servergroup_info(self):
        '''
        self-privilege::修改主机组信息::主机管理-主机组管理-主机管理-详情/变更
        '''
        self.args['dotype']='servergroup'
        self.args['success']='主机组信息设置成功'
        self.args['err']='主机组信息设置失败'
        return self.do_loginfo_modify()
        
    def modify_serverapp_info(self):
        '''
        self-privilege::修改主机组类别信息::主机管理-主机组管理-分类管理-详情/变更
        '''
        self.args['dotype']='serverapp'
        self.args['success']='分类信息设置成功' 
        self.args['err']='分类信息设置失败' 
        return self.do_loginfo_modify()
        
    def modify_loginmanager_info(self):
        '''
        self-privilege::单台服务器登录信息设置::资产管理-登录管理-登录管理-搜索-登录设置/修改
        '''
        self.args['dotype']='loginmanager'
        self.args['success']='登录信息设置成功'
        self.args['err']='登录信息设置失败' 
        return self.do_loginfo_modify()

    def modify_logininitools_info(self):
        '''
        self-privilege::服务器初始化动态登录信息设置::资产管理-初始化管理-初始化登录管理-搜索-动态登录工具
        '''
        self.args['dotype']='logininitools'
        self.args['success']='登录信息设置成功'
        self.args['err']='登录信息设置失败'
        return self.do_loginfo_modify()

            
    def modify_logintools_info(self):
        '''
        self-privilege::服务器默认动态登录信息设置::资产管理-登录管理-动态登录管理-搜索-动态登录工具
        '''
        self.args['dotype']='logintools'
        self.args['success']='登录信息设置成功'
        self.args['err']='登录信息设置失败'
        return self.do_loginfo_modify()

    def modify_logindefault_info(self):
        '''
        self-privilege::服务器默认登录信息设置::资产管理-登录管理-默认登录管理-搜索-登录设置/修改
        '''
        self.args['dotype']='logindefault'
        self.args['success']='登录信息设置成功'
        self.args['err']='登录信息设置失败'
        return self.do_loginfo_modify()
            
    def modify_initoolsmanager_info(self):
        '''
        self-privilege::服务器初始化工具修改::资产管理-初始化管理-初始化工具管理-搜索-工具上传
        '''
        self.args['dotype']='initoolsmanager'
        self.args['success']='服务器初始化工具设置成功'
        self.args['err']='服务器初始化工具设置失败'
        return self.do_loginfo_modify()
            
    def modify_logininit_info(self):
        '''
        self-privilege::服务器初始化登录信息设置::资产管理-初始化管理-初始化登录管理-搜索-登录设置/修改
        '''
        self.args['dotype']='logininit'
        self.args['success']='登录信息设置成功'
        self.args['err']='登录信息设置失败'
        return self.do_loginfo_modify()
            
    def loginfile_download(self):
        '''
        self-privilege::动态获取服务器登录信息文件下载::资产管理-初始化管理/登录管理-旋转云图标
        '''
        filetype=self.args.get('filetype')
        filekey=self.args.get('filekey')
        keyvalue=self.args.get(filekey)
        if not filetype or not filekey or not keyvalue:
            return self.write(get_ret(-1, '参数错误', status='err'))
        self.args['type']=filetype
        self.args['name']=filetype
        info=self.login_info_search()

        filepath=''
        for i in info:
            #初始化,默认登录和初始化工具3种情况有文件下载
            if i.get(filekey):
                filename=os.path.split(i.get(filekey))[-1]
            else:
                continue

            if filetype== 'logininit' and i.get('type') == "logininitools" and keyvalue == filename:
                filepath=i.get(filekey)
            elif filetype== 'logindefault' and i.get('type') == "logintools" and keyvalue == filename:
                filepath=i.get(filekey)
            elif keyvalue == filename:
                filepath=i.get(filekey)
                
            if filepath:
                break;

        if  os.path.exists(curr_path+os.sep+filepath) and filepath: 
            return self.write("downloadfile/"+filepath)
        else:
            return filepath
               
    def delete_logininit_info(self):
        '''
        self-privilege::服务器初始化登录信息删除::资产管理-初始化管理-初始化登录管理-搜索-删除
        '''
        self.args['success']='初始化登录信息删除成功'
        self.args['err']='初始化信息删除失败'
        self.args['type']='logininit'
        return self.do_logininfo_delete()
        
    def do_logininfo_delete(self):
        data={ i:self.args.get(i) for i in self.login_check_key}
        if not user_table.delete_logindefault_info(data, type=self.args.get('type')):
            return self.write(get_ret(-1, self.args.get('err'), status='err'))
        
        return self.write(get_ret(0, self.args.get('success')))
        
    def delete_initoolsmanager_info(self):
        '''
        self-privilege::服务器初始化工具信息删除::资产管理-初始化管理-初始化工具管理-搜索-删除
        '''
        self.args['success']='初始化工具删除成功'
        self.args['err']='初始化工具删除失败'
        self.args['type']='initoolsmanager'
        return self.do_logininfo_delete()
        
    def delete_logininitools_info(self):
        '''
        self-privilege::服务器初始化登录工具删除::资产管理-初始化管理-初始化登录管理-搜索-删除
        '''
        self.args['success']='初始化登录工具删除成功'
        self.args['err']='初始化登录工具删除失败'
        self.args['type']='logininitools'
        return self.do_logininfo_delete()
        
    def delete_logintools_info(self):
        '''
        self-privilege::服务器动态获取登录信息删除::资产管理-登录管理-动态登录管理-搜索信息-删除
        '''
        self.args['success']='动态登录信息删除成功'
        self.args['err']='动态登录信息删除失败'
        self.args['type']='logintools'
        return self.do_logininfo_delete()
        
    def delete_logindefault_info(self):
        '''
        self-privilege::服务器默认登录信息删除::资产管理-登录管理-默认登录管理-搜索信息-删除
        '''
        self.args['success']='默认登录信息删除成功'
        self.args['err']='默认登录信息删除失败'
        self.args['type']='logintools'
        return self.do_logininfo_delete()
        
    def delete_loginmanager_info(self):
        '''
        self-privilege::单台服务器的登录信息删除::资产管理-登录管理-登录管理-搜索IP-删除
        '''
        ip=self.args.get('name')
        if not ip:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
        if not user_table.delete_loginmanager_info(ip):
            return self.write(get_ret(-2, '%s登录信息删除失败' % ip, status='err'))
        return self.write(get_ret(0, '%s登录信息删除成功' % ip))
        
    def delete_assetmanager_info(self):
        '''
        self-privilege::资产删除::资产管理-资产管理-删除
        '''
        ip=self.args.get('name')
        if not ip:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
        if not user_table.delete_asset_info(ip, self.args['curruser']):
            return self.write(get_ret(-1, 'ip[%s]的资产记录删除失败' % ip, status='err'))
        return self.write(get_ret(0, 'ip[%s]的资产记录删除成功' % ip))
            
            
    def get_relevance_accountfilter(self):
        '''
        self-privilege::获取任务关联下拉信息::任务关联-任务创建-关联任务/详情变更
        '''
        assetapp=self.get_asset_keylist('app')
        check_app={ i.get('app'):i for i in assetapp }
        relevanceapp=user_table.get_task_relevance()
        { assetapp.append({'app':i.get('relevance_app'), 'des':i.get('relevance_app_des'), 'type':'relevance'}) for i in relevanceapp if {'app':i.get('relevance_app'), 'des':i.get('relevance_app_des'), 'type':'relevance'} not in assetapp and i.get('relevance_app') not in check_app}

        return self.write(json.dumps(assetapp, ensure_ascii=False))
         
    def get_dropmeninfo_accountfilter(self):
        '''
        self-privilege::获取资产过滤下拉信息::资产管理-资产管理-点击产品线/业务/应用/机房/其他类型
        '''
        type=self.args.get('type')
        line=self.args.get('line')
        product=self.args.get('product')
        app=self.args.get('app')
        idc=self.args.get('idc')
        if not type:
            return self.write(get_ret(-1, '参数错误, 不完整', status='err'))
        if type == "other":
            return self.write(json.dumps(self.get_asset_keylist(type, line=line, 
                                        product=product, app=app, idc=idc, 
                                        other_key=self.args.get('key')), ensure_ascii=False))
        else:
            return self.write(json.dumps(self.get_asset_keylist(type, line=line, 
                                        product=product, app=app, idc=idc), ensure_ascii=False))
        
    def assettemplate_download(self):
        '''
        self-privilege::资产导入模板下载::资产管理-资产管理-模板下载
        '''
        templatecsv=curr_path+os.sep+"template.csv"
        if not os.path.exists(templatecsv):
            return self.write(get_ret(-1, '资产模板文件不存在,请检查', status='err'))
        
        return self.write('downloadfile'+os.sep+"template.csv")
        
    def do_server_privilege(self):
        dotype=self.args.get('dotype')
        id=self.args.get('id')
        ip=self.args.get('ip')
        save_file=self.args.get('save_file')
        file=self.args.get('file')
        filelist=user_table.get_server_privilege(id=id)
        filelist=comm_lib.json_to_obj(filelist[0].get('filelist'))

        if not all([id, ip, file]) or (not save_file and dotype in ['file_upload']) or file not in filelist:
            return self.write(get_ret(-1, '参数错误 ', status='err'))

        if dotype == 'file_upload':
            save_file=curr_path+os.sep+save_file
            if not os.path.exists(save_file):
                return self.write(get_ret(-2, '获取文件失败 ', status='err'))
            request={}
            request.update({
                'request': 'serverprivilege_file_update', 
                'id': id, 
                'ip': ip, 
                'save_file': save_file, 
                'file': file
            })

        elif dotype == 'file_execute':
            request={}
            request.update({
                'request': 'serverprivilege_file_execute', 
                'id': id, 
                'ip': ip, 
                'file': file
            })
            
        ret=request_twisted(request)
        if ret == 0:
            return self.write(get_ret(ret, '', status='info'))
        else:
            return self.write(get_ret(ret, ret, status='err'))   
    def serverprivilege_file_execute(self):
        '''
        self-privilege::服务器权限文件执行::主机管理-权限信息-服务器操作-执行-确定
        '''
        self.args['dotype']='file_execute'
        return self.do_server_privilege()
        
    def serverprivilege_file_upload(self):
        '''
        self-privilege::服务器权限文件更新::主机管理-权限信息-服务器操作-更新-提交
        '''
        self.args['dotype']='file_upload'
        return self.do_server_privilege()
        
    def task_file_upload(self):
        '''
        self-privilege::自定义任务文件上传/更新::任务管理-自定义任务-上传/更新-提交
        '''
        task_id=self.args.get('task_id')
        filename=self.args.get('save_file')
        if not task_id or not filename:
            return self.write(get_ret(-1, '参数错误 ', status='err'))
        if not user_table.task_update_info(task_id=task_id, filename=filename.split(os.sep)[-1], c_user=self.args['curruser']):
            return self.write(get_ret(-2, '更新任务[%s]失败' % task_id, status='err'))
            
        return self.write(get_ret(-2, '更新任务[%s]成功' % task_id, status='info'))
        
    def assets_import(self):
        '''
        self-privilege::资产导入::资产管理-资产管理-资产导入
        '''
        filename=self.args.get('filename')
        if not filename:
            return self.write(get_ret('-1', '参数错误', status='err'))
        file_path=curr_path+"/file/tornado/upload/"+filename.split(os.sep)[-1]
        if not os.path.exists(file_path):
            return self.write(get_ret('-2', '导入失败, 服务器获取文件失败', status='err'))
        
        assetlist=[]
        message=""
        import_ret=True
        repe_iplist=[]
        #数据格式检查
        with open(file_path, 'rb') as f:
            try:
                line_count=int()
                for line in csv.DictReader(f):
                    import_ret=False
                    line_count+=1
                    assetlist.append(line)
                    if not line['telecom_ip']:
                        message="资产csv文件[%s]中第%s行电信IP为空, 请检查." % (filename, line_count)
                        break
                        
                    if not re.match(r'^([0-9]+.){3}[0-9]+$', line['telecom_ip']):
                        message="电信IP[%s]格式不对, 请修改csv文件填写正确格式的IP地址." % line['telecom_ip']
                        break
                        
                    if not line['line'] or not line['product'] or not line['app']  or not line['describe'] :
                        message="电信IP[%s]的line/product/app/describe字段不能为空." % line['telecom_ip']
                        break
                        
                    if re.match(r'[^-_\d\w]+', line['line']) or re.match(r'[^-_\d\w]+', line['product']) or re.match(r'[^-_\d\w]+', line['app']) or line['describe'].count('-') != 2:
                        message="电信IP[%s]的line/product/app/describe字段不满足规范, 请安装资产模板说明填写." % line['telecom_ip']
                        break
                        
            except:
                if not message:
                    message="资产导入失败, 请确定文件是否为csv格式"

        if message:
            return self.write(get_ret('-3', message, status='err'))
        
        for line in assetlist:
            ret=user_table.import_assets_info(decode_utf8(line), self.args['curruser'])
            if not ret:
                log.err('asset import err. %s import err.' % line['telecom_ip'])
                message="电信IP为[%s]导入出错,请检查." % line['telecom_ip']
                return self.write(get_ret('-1', message, status='err'))
                
            elif ret == "exists":
                log.warn('ip info repetition: %s ' % line['telecom_ip'])
                repe_iplist.append(line['telecom_ip'])
            
        if not repe_iplist:
            return self.write(get_ret('0', '资产导入成功', status='info'))
        else:
            return self.write(get_ret('1', '资产导入成功,以下IP信息已经存在:%s,请确认'  % repe_iplist, status='warn'))

                    
    def add_info_assetdisplay_html(self):
        '''
        self-privilege::资产显示定制数据提交::资产管理-资产管理-显示定制-提交
        '''
        
        keys=self.args.get('keys')
        if not user_table.other_setvalue_record(self.assets_templeat_key, json.dumps(keys), user=self.args['curruser']):
            return self.write(get_ret('-1', '定制资产显示失败', status='err'))
        return self.write(get_ret(0, '定制资产显示成功,请刷新资产管理界面查看'))
        
    def get_dropmenu_for_semantic(self, data):
        keylist={}
        keylist["success"]='true'
        keylist["results"]=[]
        for i in data:
            k=i.keys()[0]
            v=i[k]
            keylist["results"].append({
                'name':v,
                'value':k,
                'text':v
            })
        return keylist
        
    def get_dropmenu_informationcollect(self):
        '''
        self-privilege::信息收集模板数据获取::任务管理-信息收集-信息收集-点击模板搜索框
        '''
        info=user_table.get_collecttemplate_info()
        data=[ { i.get('template_id'):i.get('des') } for i in info ]
        return self.write(json.dumps(self.get_dropmenu_for_semantic(data), ensure_ascii=False))
        
    def get_assets_templeat_keys(self):
        '''
        self-privilege::资产显示定制数据获取::资产管理-资产管理-显示定制
        '''
        return self.write(json.dumps(self.get_dropmenu_for_semantic(self.assets_templeat_keys), ensure_ascii=False))
        
    def serverprivilegefile_check(self):
        '''
        self-privilege::服务器权限文件下载检查::主机管理-权限信息-服务器操作-下载
        '''
        self.args['name']='serverprivilegefilecheck'
        self.args['err']='下载失败'
        return self.file_download()
        
    def file_download(self):
        name=self.args.get('name')
        id=self.args.get('id')
        err=self.args.get('err')
        ip=self.args.get('ip')
        filedownpath=self.args.get('downloadfile')
        file=self.args.get('file')
        
        if name in ['tatistics', 'assetscvs', 'history']:
            data=self.get_asset_search_info()
            
        if name == 'tatistics':
            data=self.assets_tatistics(data)
            export_key=self.asset_tatistics_export_key
            load_path="file/tornado/download/assets/assetstatistics.csv"
        elif name == 'taskcustom':
            filename=self.args.get('filename')
            task_id=self.args.get('task_id')
            load_path="task/%s/%s" % (task_id, filename)
            
        elif name == 'assetscvs':
            load_path="file/tornado/download/assets/assets.csv"
            export_key=self.asset_key
            
        elif name == 'serverprivilegelist':
            getret=True
            filelist=user_table.get_server_privilege(id=id)
            if not filelist:
                getret=False
            filelist=comm_lib.json_to_obj(filelist[0].get('filelist'))
            if not all([ip, file]) or file not in filelist:
                return self.write(get_ret(-1, '参数错误', status='err'))

            request={}
            request.update({
                'request': 'download_file',
                'ip': ip,
                'file': file
            })
            filedownpath=request_twisted(request)
            load_path=filedownpath
            
        elif name == 'serverprivilegefilecheck':
            load_path=re.sub(r'downloadfile/', '', filedownpath)
            if not os.path.exists(load_path):
                return self.write(get_ret(-2, '文件未下载完成, 请从试!', status='warn'))
            
        elif name == 'history':
            load_path="file/tornado/download/assets/assetshistorychange.csv"
            export_key=self.asset_history_change_key
            
        if name in ['tatistics', 'assetscvs', 'history']:
            if write_csv(load_path, export_key, data):
                return self.write("downloadfile/"+load_path)
            else:
                return self.write(get_ret(-1, err, status='err'))
        else:
            return self.write("downloadfile/"+load_path)
            
    def tatistics_download(self):
        '''
        self-privilege::资产统计信息导出::资产管理-资产管理-资产统计-统计结果导出
        '''
        self.args['name']='tatistics'
        self.args['err']='生成资产统计记录文件失败'
        return self.file_download()

    def taskcustom_download(self):
        '''
        self-privilege::自定义任务文件下载::任务管理-自定义任务-下载-
        '''
        self.args['name']='taskcustom'
        self.args['err']='任务文件下载失败'
        return self.file_download()
        
    def assethistory_download(self):
        '''
        self-privilege::资产变更记录导出::资产管理-资产管理-资产变更记录-变更记录导出
        '''
        self.args['name']='history'
        self.args['err']='生成资产变更记录文件失败'
        return self.file_download()
        
    def assetscvs_download(self):
        '''
        self-privilege::资产导出::资产管理-资产管理-资产导出
        ''' 
        self.args['name']='assetscvs'
        self.args['err']='生成资产文件失败'
        return self.file_download()

    def upload(self):
        '''
        self-privilege::文件上传::文件上传/资产导入/任务文件上传/集成工具文件上传
        '''
        #上传信息从 self.request.files获取，前端form设置method="post" enctype="multipart/form-data"，input设置type="file" name="file"，还有注意ajax请求的设置

        fileinfo=self.request.files['file'][0]
        if self.args.get("assetupload"):
            save_file=curr_path+"/file/tornado/upload/"+fileinfo['filename'].split(os.sep)[-1]
        elif self.args.get("loginuser") or self.args.get("loginport") or self.args.get("loginpwd"):
            for k in ["loginuser", "loginport", "loginpwd"]:
                if not self.args.get(k):
                    continue
                data=json.loads(self.args.get(k))
                logintype=data.get('logintype')
                if not logintype:
                    return self.write(get_ret(-1, '上传动态获取登录信息失败,参数错误', status='err'))
                save_file=curr_path+"/file/tornado/upload/"+logintype    
                
                if self.args.get(k):
                    for kk in self.login_check_key:
                        if data.get(kk):
                            save_file+=os.sep+data.get(kk)
                save_file+=os.sep+k
                break
            save_file+=os.sep+fileinfo['filename'].split(os.sep)[-1]
        elif self.args.get("taskcustom"):
            info=json.loads(self.args.get('taskcustom'))
            task_id=info.get('task_id')
            if not task_id:
                return self.write(get_ret(-1, '上传失败,获取task_id失败', status='err'))
            save_file=curr_path+"/task/%s/%s" % (task_id, fileinfo['filename'].split(os.sep)[-1])
            
        elif self.args.get("serverprivilegelist"):
            save_file=curr_path+"/file/tornado/upload/serverprivilegelist/"+fileinfo['filename'].split(os.sep)[-1]
        elif self.args.get("initoolsmanager"):
            save_file=curr_path+"/file/tornado/upload/initools/"+fileinfo['filename'].split(os.sep)[-1]

        if os.path.exists(save_file):
            os.rename(save_file, save_file+str(comm_lib.get_now()).replace(' ', '_'))
        elif not os.path.exists(os.sep.join(save_file.split(os.sep)[:-1])):
            os.makedirs(os.sep.join(save_file.split(os.sep)[:-1]))
            
        with open(save_file, 'wb') as s:
            s.write(fileinfo['body'])

        if not os.path.exists(save_file):
            return self.write(get_ret('-2', '上传失败', status='err'))
        else:
            return self.write(json.dumps({
                'code':'0', 
                'message':'上传成功', 
                'status':'info', 
                'save_file':save_file.replace(curr_path, '')
            }))

    def do_request(self):
        if hasattr(self, self.method) and self.method in requestlist:
            if callable(getattr(self, self.method)):
                log.info("exec function %s " % self.method)
                #根据请求path取最后一个字段动态调用事先定义好的方法
                try:
                    privi_name=self.__class__.__name__+"."+self.method
                    has_privi=False
                    isadmin=False
                    grouplist=[]
                    groupdatainfo={}
                    
                    privi_list=user_table.get_privilege_allocate_info(user=self.args['curruser'])
                    if not privi_list and self.args['curruser'] != 'admin':
                        #当前用户没有任何组，即没任何权限
                        return self.write(get_ret(-99, '你没有权限', status='err'))
                
                    for i in  privi_list:
                        if not i['privi_list'] and i['name'] != 'admin':
                            continue
                            
                        if i['name'] == 'admin':
                            isadmin=True
                        grouplist.append(i['name'])
                        groupdatainfo[i['name']]=i

                        if privi_name in str(i['privi_list']).split(','):
                            has_privi=True

                    if not has_privi and not isadmin and self.args['curruser'] != 'admin':
                        #没有权限执行当前函数
                        return self.write(get_ret(-98, '你没有当前请求权限', status='err'))
                    self.args['grouplist']=grouplist     
                    self.args['groupdatainfo']=groupdatainfo
                                       
                    apply(getattr(self, self.method))
                except:
                    log.warn('lineno:' + str(sys._getframe().f_lineno)+": "+str(sys.exc_info()))
                    #执行出错
                    return self.write(get_ret(-101, '请求失败', status='err'))
            else:
                raise KeyError("%s class method not in %s."%(self.method, self.__class__.__name__))

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        yield self.executor.submit(self.do_request)
        if self.route_check('.*/downloadfile/.*'):
            fn=self.args['filepath'].split(os.sep)[-1]
            download_path=urllib2.unquote(curr_path+os.sep+self.args['filepath'].split('downloadfile/')[-1])
            if not os.path.exists(download_path):
                raise Exception('file %s is not exists!' % download_path)    

            self.set_header ('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=%s' % fn)
            #self.write(tj_render(download_path)) 
            with open(download_path, 'rb') as f :
                self.write(f.read()) 

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        yield self.executor.submit(self.do_request)

class interfaceHandler(mainHandler):
    #不检查登录
    def prepare(self):
        log.info('%s conn in, request %s;' % (self.request.remote_ip, self.request.uri))
        if self.key_err:
            log.info('request err. key err.')
            return self.finish()
            
    def on_finish(self):
        log.info('%s[%s] request done;' % (self.request.remote_ip, self.request.uri))
        
    def initialize(self):
        self.key_err=False
        self.args={k:''.join(v) for k, v in self.request.arguments.iteritems()}
        if not self.args:
            #在 AngularJS 中，数据传递的是 application/json 格式的数据，在body里, ajax的则可以使用arguments获取
            #若arguments中没数据则使用body获取一次
            if self.request.body:
                self.args=json.loads(self.request.body)
                
        db_verify_key=user_table.get_verify_key_info(name='verify_key')[0]['value']
        self.method=self.request.path.split(os.sep)[-1].replace('.',"_").replace('-', '_') 

        if  self.args.get('requesttype') != 'platform_history':
            taskque.put({
                'type': 'add_history',
                'clsname': self.__class__.__name__,
                'remote_ip': self.request.remote_ip,
                'verify_key': db_verify_key,
                'requestdata': { k:v for k,v in self.args.iteritems() },
                'c_user': '',
                'method': self.method
            })
        self.args.update({'filepath':curr_path+self.request.path})
        self.args.update({'curruser':self.get_current_user()})
        self.line=self.args.get('line')
        self.product=self.args.get('product')
        self.app=self.args.get('app')
        self.name=self.args.get('name')
        self.member=self.args.get('member')
        self.group=self.args.get('group')
        self.idc=self.args.get('idc')
        self.other_key=self.args.get('other_key')
        self.assetapp=self.args.get('assetapp')
        self.c_user=self.args.get('c_user')
        self.iplist=self.args.get('iplist')
        verify_key=self.args.get('verify_key', None)
        
        if db_verify_key != verify_key:
            #key需要有效
            self.key_err=True
            return self.write(get_ret(-100, "verify_key err.", status="err"))

    def get_host_info(self):
        '''self-method'''
        return user_table.get_servergroup_info(line=self.line, product=self.product, app=self.app, 
                                group=self.group, type='serverhost')
                                
    def get_group_info(self):
        '''self-method'''
        info=self.get_host_info()
        groupinfo={}
        for i in info:
            groupinfo.setdefault(i.get('line'),{})
            groupinfo[i.get('line')].setdefault(i.get('product'),{})
            groupinfo[i.get('line')][i.get('product')].setdefault(i.get('app'),{})
            groupinfo[i.get('line')][i.get('product')][i.get('app')].setdefault(i.get('group_id'),[])
            if i.get('member') not in groupinfo[i.get('line')][i.get('product')][i.get('app')][i.get('group_id')]:
                groupinfo[i.get('line')][i.get('product')][i.get('app')][i.get('group_id')].append(i.get('member'))
            
        return self.write(json.dumps(groupinfo))
        
    def asset_search(self):
        '''self-method::资产查询接口'''
        #资产查询
        info=user_table.assets_search(line=self.line, product=self.product,
                                    app=self.app, idc=self.idc, other_key=self.other_key, iplist=self.iplist)
        info_str=''
        for i in info:
            for k in ['telecom_ip', 'unicom_ip', 'inner_ip', 'line', 'product', 'app', 'describe', 'idc', 'serial_number', 'owner', 'os', 'mem', 'disk', 'cpu', 'firm']:
                info_str+=i.get(k)+"|"
            info_str+='\n'
        return self.write(info_str)

    def group_member_add(self):
        '''self-method::主机组成员添加接口'''
        #组成员导入,可以配合资产查询使用
        #assetapp为资产的app, app为主机组分类
        return self.add_info_groupmember_html()
    
    def get_server_loginfo(self):
        '''self-method::获取服务器登录信息接口'''
        self.login_check_key=['line', 'product', 'app', 'idc', 'owner']
        return self.write(json.dumps(self.get_server_login_info(self.iplist), ensure_ascii=False))
        
    def get_server_info(self):
        '''self-method::获取主机组成员信息接口'''
        info=self.get_host_info()
        iplist=[i.get('member') for i in info]                      
        return self.write(json.dumps(iplist))
        
    def add_informationcollect(self):
        '''self-method::信息收集接口'''
        id=self.args.get('template_id')
        ip=self.args.get('ip')
        info=self.args.get('info')
        check_info=comm_lib.json_to_obj(info)
        
        template=user_table.get_collecttemplate_info()
        template_list={ i.get('template_id'):i for i in template}
        if not ip:
            return self.write(get_ret(-4, '获取ip失败', status='err'))
            
        if not id or id not in template_list:
            return self.write(get_ret(-1, '获取template_id失败', status='err'))
            
        if not isinstance(check_info, dict) and (check_info.find(':::') == -1 or check_info.find('=>') == -1):
            return self.write(get_ret(-2, '添加失败,请按照格式传递info数据', status='err'))
            
        if not user_table.add_collecttemplate_history(template_id=id, info=info, ip=ip):
            return self.write(get_ret(-3, '添加信息失败', status='err'))
            
        return self.write(get_ret(0, '添加信息成功', status='info'))
        
    def get_servergroup_info(self):
        '''self-method'''
        return self.get_ngrepeat_data_servergroup()
        
    def get_login_list(self):
        '''self-method'''
        self.args['dotype']='mainpage'
        return self.write(json.dumps(self.do_get_servergroup_info(), ensure_ascii=False))

    def fault_add(self):
        '''self-method::故障信息添加接口'''
        ip=self.args.get('ip')
        key=self.args.get('key')
        name=self.args.get('name')
        des=self.args.get('des')
        if not ip or not name:
            return self.write(get_ret(-2, '参数错误', status='err'))
        user_table.fault_add(ip, name, zone=key, des=des)
        return self.write(get_ret(0, '添加故障成功', status='info'))
        
        
    def get(self):
        if hasattr(self, self.method) and self.method in interfacelist:
            if callable(getattr(self, self.method)):
                log.info("exec function %s " % self.method)
                #根据请求path取最后一个字段动态调用事先定义好的方法
                try:
                    getattr(self, self.method)()
                except:
                    log.warn('lineno:' + str(sys._getframe().f_lineno)+": "+str(sys.exc_info()))
                    #执行出错
                    return self.write(get_ret(-101, "execute err.", status="err"))
            else:
                log.warn('lineno:' + str(sys._getframe().f_lineno)+": "+str(sys.exc_info()))

    def post(self):
        self.get()
        self.finish()

class eagledaemon(Daemon):
    def __init__(self, *args, **kwargs):
        super(eagledaemon, self).__init__(*args, **kwargs)
        
    def run(self):
        settings={
            'cookie_secret':base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes), 
            "login_url": "/login.html", 
            'debug':True, 
            "static_path": os.path.join(os.path.dirname(__file__),"static"), 
            "template_path":os.path.join(os.path.dirname(__file__),"templates")
        }
        app=tornado.web.Application(
            [
                (r'.*/login.html.*', loginHandler), 
                (r'/$', loginHandler), 
                (r'/interface/.*', interfaceHandler), 
                (r'/online/.*', websocketHandler), 
                (r'/upload', mainHandler), 
                (r'/download', mainHandler), 
                (r'/templates/.*', mainHandler)
            ], **settings
        )

        httpserver=tornado.httpserver.HTTPServer(app)
        httpserver.max_buffer_size=3048576000
        httpserver.listen(options.port)
        ioloop.PeriodicCallback(do_periodicTask, 90000).start()
        tornado.ioloop.IOLoop.instance().start()

        
def getconf(cfg, attrname=None, attrvalue=None):
    if not os.path.exists(cfg):
        log.info("config file %s is not exists." % cfg)
        return
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
    
def fetch_response(response):
    pass
    
def do_periodicTask():
    while not taskque.empty():
        data=taskque.get(False)
        if not data:
            break

        type=data.get('type')
        #平台审计
        if type in ['add_history']:
            method=data.get('method')
            clsname=data.get('clsname')
            remote_ip=data.get('remote_ip')
            c_user=data.get('c_user')
            requestdata=comm_lib.obj_to_json(data.get('requestdata'))
            verify_key=data.get('verify_key')
            if not verify_key:
                verify_key=user_table.get_verify_key_info(name='verify_key')[0]['value']
            template_id='platform_history'
            
            try:
                fn_doc=str(getattr(globals().get(clsname), method).__doc__).strip()
            except:
                continue

            _doclist=fn_doc.split('::')
            if len(_doclist) < 1:
                continue
            _doc=_doclist[1]
            if clsname == 'mainHandler':
                skey=c_user
            elif clsname == 'interfaceHandler':
                skey=remote_ip
            else:
                continue

            info='''remote_ip=>%s:::c_user=>%s:::method=>%s:::method_doc=>%s:::requestdata=>%s''' % (remote_ip, c_user, method, _doc, requestdata)
            key='''[%s]%s''' % (skey, _doc)
            request = tornado.httpclient.HTTPRequest(
                url='http://%s:%s/interface/add_informationcollect'   % (tornado_ip, tornado_port), 
                method='POST', 
                body='''ip=%s&template_id=%s&info=%s&requesttype=%s&verify_key=%s''' % (key, template_id, info, template_id, verify_key),
                validate_cert=False) 
            tornadoClient=tornado.httpclient.AsyncHTTPClient()
            return tornadoClient.fetch(request, fetch_response)
    
def queue(n=None):
    if not n:
        return Queue.Queue(-1)
    return Queue.Queue(n)


def time_check():
    sys_time=comm_lib.to_datetime_obj(str(datetime.datetime.now()).split('.')[0])
    db_time=str(user_table.get_now()[0]['now()'])
    db_time=comm_lib.to_datetime_obj(db_time)
    cmptime=int(str((db_time - sys_time).total_seconds()).split('.')[0])
    #数据库和系统时间差不能小于30秒
    if cmptime > 30 or cmptime  < -30:
        return False
    else:
        return True

def privilege_set(dest_obj_list, getkey=None, findkey=None):
    #遍历需要控制权限的class和class的方法，把信息列表入库, 为权限分配做准备
    #需要控制权限的方法需要添加doc信息
    #doc格式为:^self-privilege::[^ ]+::[^ ]+$
    #dest_obj_list为需要控制权限的class
    
    log.info('set privilege info begin.')
    fn_doc=''
    key_l=[]
    for i in globals().keys():
        if i in dest_obj_list:
            for f in dir(globals()[i]):
                fn_doc=str(getattr(globals()[i], f).__doc__).strip()
                if not re.match(r'^self-privilege.*', fn_doc):
                    continue
                    
                if not re.match(r'^self-privilege::[^:]+::[^:]+$', fn_doc):
                    log.err('set %s privilege err.doc info err.skip' % f)
                    continue
                    
                name=i+"."+f
                if getkey:
                    if re.match('.*%s.*' % getkey, fn_doc):
                        key_l.append(name)
                    continue

                key, des, remark=fn_doc.split('::')
                if findkey :
                    dk=str(findkey) + '主界面'
                    if dk == des: 
                        return name
                    elif re.match(r'.*/.*', findkey):
                        odk=str(findkey.split('/')[0]) + '主界面'
                        tdk=str(findkey.split('/')[1]) + '主界面'
                        if odk == des or tdk == des:
                            return name
                elif not user_table.privilege_info_add(name, des, remark):
                    log.err('privilege info set err.')
                    
    if  getkey:
        return key_l
    else:
        log.info('privilege info set done.')

def get_methodlist(clslist):
    global requestlist, interfacelist
    requestlist=[]
    interfacelist=[]
    for i in globals().keys():
        if i in clslist:
            for f in dir(globals()[i]):
                fn_doc=str(getattr(globals()[i], f).__doc__).strip()
                if i == 'mainHandler' and re.match(r'^self-privilege.*', fn_doc):
                    requestlist.append(f)
                elif i == 'interfaceHandler' and re.match(r'^self-method.*', fn_doc):
                    interfacelist.append(f)
                    
if __name__=="__main__":
    tornado.options.parse_command_line()
    curr_path=os.path.split(os.path.realpath(__file__))[0]
    p_dbcfg=curr_path + os.sep + 'config' + os.sep + 'db_config.xml'
    p_tornado=curr_path + os.sep + 'config' + os.sep + 'tornado' + os.sep + 'config.xml'
    p_twisted=curr_path + os.sep + 'config' + os.sep + 'twisted' + os.sep + 'config.xml'
    tornado_info=getconf(p_tornado, attrname="name", attrvalue="tornado")
    tornado_ip=tornado_info['tw_server']['ip']
    task_path=tornado_info['task']['file_path']
    tools_path=tornado_info['task']['tools']
    task_log_path=tornado_info['task']['client_log_save']
    tornado_port=tornado_info['run']['port']
    define('debug', default='info')
    define('port', default=int(tornado_port))
    
    tw_info=getconf(p_twisted, attrname="name", attrvalue="twsited")
    tw_server_ip=tw_info['client']['ip']
    tw_server_port=int(tw_info['run']['port'])

    p_log=curr_path + os.sep + 'log' + os.sep + 'tornado' + os.sep + 'tornado.log'
    log=comm_lib.log(p_log)
    dbinfo=comm_lib.get_db_info(p_dbcfg)

    user_table=user_table.user_table(dbinfo["ip"], dbinfo["port"], dbinfo["db_name"], dbinfo["user"], encrypt.decode_pwd(dbinfo["pwd"]))
    taskque=queue()
    if not time_check():
       log.err('os and db time cmp err.')
       sys.exit()

    help_msg = 'Usage: python %s <start|stop|restart|debug>' % sys.argv[0]
    eagle=eagledaemon(curr_path+'/tornado_pid.pid')

    get_methodlist(['mainHandler', 'interfaceHandler'])
    dest_obj_list=['mainHandler']
    privilege_set(dest_obj_list)

    if len(sys.argv) == 1: 
        eagle.restart()
    elif sys.argv[1] in ['debug']:
        eagle.run()
    elif sys.argv[1] in ['start', 'stop', 'restart']:
        getattr(eagle, sys.argv[1])()
    else:
        print help_msg
        sys.exit(1)

