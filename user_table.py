#!/usr/bin/python
#coding=utf-8
import functools, torndb, re, json, threading, sys, copy, time

sql_lock=threading.RLock()

def sql_result(par=None):
    def exec_fn(func):
        @functools.wraps(func)
        def exec_f(*args, **kwargs):
            ret=sql_lock.acquire()

            sql=''
            try:
                try:
                    db, sql=func(*args, **kwargs)
                except TypeError:
                    db, sql=func(args[0], **kwargs)
                #print sql
                
                #db.execute('SET @@session.time_zone = "+08:00";')
                if not par:
                    #直接执行sql，create/update/insert等等操作
                    db.execute(sql)
                    return True
                elif par == 'get':
                    #返回一个字典
                    return db.get(sql)
                elif par == 'query':
                    #返回一个list，里面1个或多个字典
                    return db.query(sql)
            except:
                if sql:
                    err="exec %s faild." % sql
                else:
                    print sys.exc_info()
                    err="exec %s faild." % func 
                raise Exception(err)

            finally:
                sql_lock.release()

        return exec_f
    return exec_fn
    
    

class user_table(object):
    def __init__(self, ip, port, db_name, user, password):
        self.db=torndb.Connection(ip+":"+port, db_name, user=user, password=password)
        #super(user_table, self).__init__()
        #用户表，存放用户信息
        self.t_user_info="t_user_info"
        #用户组表
        self.t_group_info="t_group_info"
        #资产表
        self.t_assets_info='t_assets_info'
        #资产变更历史记录表
        self.t_assets_history_change='t_assets_history_change'
        #服务器登录管理表/针对单台服务器
        self.t_server_login_manager='t_server_login_manager'
        #服务器初始化登录信息表/初始化使用(包含初始化静态信息和动态获取)
        self.t_server_init_manager='t_server_init_manager'
        #服务器初始化记录表
        self.t_server_init_history='t_server_init_history'
        #服务器默认登录信息管理表(包含静态信息和动态获取)
        self.t_server_login_default='t_server_login_default'
        #主机类型表
        self.t_serverapp_info='t_serverapp_info'
        #主机组成员信息表
        self.t_serverhost_info='t_serverhost_info'
        #主机组信息表
        self.t_servergroup_info='t_servergroup_info'
        #权限管理，key表
        self.t_verify_key='t_verify_key'
        #用户权限关联/分配表
        self.t_privilege_allocate='t_privilege_allocate'
        #权限信息表
        self.t_privilege_info='t_privilege_info'
        #通知管理主账号表
        self.t_inform_account_info='t_inform_account_info'
        #通知管理联系人表
        self.t_inform_contact_info='t_inform_contact_info'
        #其他类型设置记录表
        self.t_other_setvalue_record='t_other_setvalue_record'
        #自定义任务信息表
        self.t_task_info='t_task_info'
        #信息收集模板表
        self.t_task_informationcollect='t_task_informationcollect'
        #信息收集记录表
        self.t_task_informationcollect_history='t_task_informationcollect_history'
        #任务关联表
        self.t_task_relevance='t_task_relevance'
        #任务信息记录表
        self.t_task_history='t_task_history'
        #任务主机/任务详情记录表
        self.t_task_servers_history='t_task_servers_history'
        #任务主机/任务标记执行完成记录表
        self.t_task_done_history='t_task_done_history'
        #主机服务器权限开放信息
        self.t_serverprivilege_info='t_serverprivilege_info'
        #故障处理
        self.t_fault_handle='t_fault_handle'

    @sql_result('query')
    def get_now(self):
        sql='''select now()'''
        return [self.db, sql]

    @sql_result('query') 
    def get_server_login_info(self, ip):
        sql='''select * from  %s where ip='%s' ''' % (self.t_server_login_default, ip)
        return  [self.db, sql]

    def get_sql_in_list(self, str_or_list):
        if not isinstance(str_or_list, list):
            str_or_list=str_or_list.split(', ')
            
        str_dest='"'+','.join(str_or_list).replace(',', '","')+'"'

        return str_dest

    @sql_result()
    def mod_user_pwd(self, user, pwd):
        sql='update %s set pwd="%s", m_pwd_time=now() where user="%s";' % (self.t_user_info, pwd, user)
        return  [self.db, sql]

    @sql_result()
    def privilege_info_add(self, name, des, remark):
        sql='''replace into %s (name, des, remark) values('%s', '%s', '%s') ''' % (self.t_privilege_info, name, des, remark)
        return  [self.db, sql]

    def get_servergroup_table(self, type):
        if type == 'serverapp':
            table=self.t_serverapp_info
        elif type == 'servergroup':
            table=self.t_servergroup_info
        elif type == 'serverhost':
            table=self.t_serverhost_info
        return table 
        
    @sql_result('query')
    def get_collecttemplate_info(self, **kws):
        sql='''select * from %s '''  % self.t_task_informationcollect
        where_str=self.get_sql_with_keys(kws)
        if where_str:
            sql += ''' where %s'''  % where_str
        sql+=' order by c_time desc'
        return [self.db, sql]

    @sql_result('query')
    def get_task_info(self, **kws):
        sql='''select * from %s '''  % self.t_task_info
        if kws.get('key'):
            sql += ''' where task_id regexp '%s' or des regexp '%s' ''' % (kws.get('key'), kws.get('key'))
        else:
            where_str=self.get_sql_with_keys(kws)
            if where_str:
                sql += ''' where %s'''  % where_str
        sql+=' order by c_time desc'
        return [self.db, sql]
    
    def filter_key(self, data, keylist):
        newdata={}
        for i in data:
            if i in keylist:
                newdata[i]=data[i]

        return newdata
        
    @sql_result()
    def delete_collecttemplate_history(self, **kws):
        d={}
        d['template_id']=kws.get('template_id')
        d['id']=kws.get('id')
        where_str=self.get_sql_with_keys(d, result=True)
        sql='''delete from %s where %s ''' % (self.t_task_informationcollect_history, where_str)
        return [self.db, sql]
        
    @sql_result('query')
    def get_collecttemplate_history(self, **kws):
        sql='''select * from %s ''' % self.t_task_informationcollect_history
        where_stra=''
        if kws.get('c_time'):
            where_stra=''' and c_time regexp '%s' ''' % kws.get('c_time')
            del kws['c_time']
        where_str=self.get_sql_with_keys(kws, result=True)
        where_str+=where_stra
        if where_str:
            where_str=where_str.strip(' ').strip('and')
            sql+='''  where %s '''  % where_str
        sql+=''' order by id desc'''
        return [self.db, sql]
        
    @sql_result()
    def add_collecttemplate_history(self, **kws):
        key, value=self.get_insert_key_value(kws)
        sql='''insert into %s (%s, c_time) values (%s, now())''' % (self.t_task_informationcollect_history, key, value)
        return [self.db, sql]
    
    @sql_result()
    def delete_collecttemplate_info(self, template_id):
        self.delete_collecttemplate_history(template_id=template_id)
        sql='''delete from %s where template_id='%s' ''' % (self.t_task_informationcollect, template_id)
        return [self.db, sql]
        
    @sql_result()
    def delete_task_info(self, task_id):
        sql='''delete from %s where task_id='%s' ''' % (self.t_task_info, task_id)
        return [self.db, sql]
        
    @sql_result()
    def task_update_info(self, **kws):
        value=self.get_update_key_value(self.filter_key(kws, ['task_id', 'filename', 'c_user']))
        sql='''update %s set %s where task_id='%s' ''' % (self.t_task_info, value, kws.get('task_id'))
        return [self.db, sql]
        
        
    @sql_result()
    def add_collecttemplate_info(self, **kws):
        key, value=self.get_insert_key_value(kws)
        sql='''insert into %s (%s, c_time) values(%s, now()) '''   % (self.t_task_informationcollect, key, value)
        return [self.db, sql]
        
    @sql_result()
    def add_task_info(self, **kws):
        key, value=self.get_insert_key_value(kws)
        sql='''insert into %s (%s, c_time) values(%s, now()) '''   % (self.t_task_info, key, value)
        return [self.db, sql]

    @sql_result()
    def delete_servergroup_info(self, **kws):
        type=kws.get('type')

        table=self.get_servergroup_table(type)
        del kws['type']

        sql_keys=self.get_sql_with_keys(kws, result=True)
        if type == 'serverapp':
            sql='''delete from %s where %s '''   % (table, sql_keys)
            cdt={}
            cdt['type']='servergroup'
            cdt['app']=kws.get('app')
            self.delete_servergroup_info(**cdt)
            
        elif type == 'servergroup':
            sql='''delete from %s where %s ''' % (table, sql_keys)
            cdt={}
            cdt['type']='serverhost'
            if kws.get('group_id'):
                cdt['group_id']=kws.get('group_id')
            elif kws.get('app'):
                cdt['app']=kws.get('app')
            self.delete_servergroup_info(**cdt)
            
        elif type == 'serverhost':
            sql='''delete from %s where %s  ''' % (table, sql_keys)
            
        return [self.db, sql]    

    @sql_result()
    def delete_task_relevance_info(self, **kws):
        sql='''delete from %s ''' % self.t_task_relevance
        where_str=self.get_sql_with_keys(kws)
        if where_str:
            sql+=''' where  %s '''  % where_str
        return [self.db, sql] 
        
    @sql_result('query')
    def get_task_relevance(self, **kws):
        sql='''select * from %s ''' % self.t_task_relevance
        where_str=self.get_sql_with_keys(kws)
        if where_str:
            sql+=''' where  %s '''  % where_str
        return [self.db, sql] 
        
    @sql_result('query')
    def get_task_history(self, **kws):
        sql='''select * from %s ''' % self.t_task_history
        date_end=str(kws.get('date_end', ''))
        date_start=str(kws.get('date_start', ''))
        custominfo=str(kws.get('custominfo', ''))
        task_name=str(kws.get('task_name', ''))
        
        status=str(kws.get('status', ''))
        task_type=str(kws.get('task_type', ''))
        relevance_id=str(kws.get('relevance_id', ''))
        new_data={}
        if status and status != '0':
            new_data['status']=status
        if task_type and task_type != '0':
            new_data['task_type']=task_type
        if relevance_id and relevance_id != '0':
            new_data['relevance_id']=relevance_id
 
        where_str=self.get_sql_with_keys(new_data)    
        if date_start and date_end:
            where_str+=''' and  c_time >= '%s' and c_time <= '%s' ''' % (date_start, date_end)
        elif date_start and not date_end:
            where_str+=''' and  c_time = '%s' ''' % date_start
        elif date_end and not date_start:
            where_str+=''' and  c_time = '%s' ''' % date_end
        elif task_name:
            where_str+=''' and  task_name = '%s' ''' % task_name
        if custominfo:
            where_str+=''' and  custom_name = '%s' or custom_type = '%s' ''' % (custominfo, custominfo)
        
        if where_str:
            where_str=where_str.strip().strip('and')
            sql+=''' where  %s '''  % where_str
        if re.match(r'.*where.*', sql) and status != 'done':
            sql+=''' and status !='done' '''
        elif status != 'done':
            sql+=''' where status !='done' order by id desc '''
        return [self.db, sql] 
        
        
    @sql_result('query')
    def get_task_done_info(self, **kws):
        sql='''select * from %s ''' % self.t_task_done_history
        where_str=self.get_sql_with_keys(kws, result=True)
        if where_str:
            sql+=''' where  %s '''  % where_str
        return [self.db, sql] 
        
    @sql_result('query')
    def get_task_servers_info(self, **kws):
        sql='''select * from %s ''' % self.t_task_servers_history
        where_str=self.get_sql_with_keys(kws, result=True)
        if where_str:
            sql+=''' where  %s '''  % where_str
        return [self.db, sql] 

    def task_status_update(self, type, c_user, **kws):
        if type == 'status':
            status=kws.get('status')
            task_name=kws.get('task_name')
            self.update_task_history_status(c_user, status, task_name)
            if status == 'done':
                self.copy_task_servers_to_done_history(task_name)
                self.task_servers_delete(task_name)
                self.update_done_history(c_user, task_name)
        elif type == 'timemodify':
            self.update_task_history_exectime(c_user, **kws)
            
        return True
        
    @sql_result()
    def task_servers_status_update(self, taskname, task_info, ip):
        sql='''update %s set task_info='%s' where task_name='%s' and telecom_ip='%s' '''  % (self.t_task_servers_history, task_info, taskname, ip)
        return [self.db, sql]
        
    @sql_result()
    def task_servers_delete(self, task_name):
        sql='''delete from %s  where task_name='%s' '''  % (self.t_task_servers_history, task_name)
        return [self.db, sql] 
        
    @sql_result()
    def update_done_history(self, c_user, task_name):
        sql='''update %s set c_user='%s', c_time=now() where task_name='%s' ''' % (self.t_task_done_history, c_user, task_name)
        return [self.db, sql] 
        
    @sql_result()
    def copy_task_servers_to_done_history(self, task_name):
        sql='''insert into %s (task_name,telecom_ip,modal,login_info,group_id,task_info,server_key,asset_app) select task_name,telecom_ip,modal,login_info,group_id,task_info,server_key,asset_app  from %s where task_name='%s' ''' % (self.t_task_done_history, self.t_task_servers_history, task_name) 
        return [self.db, sql] 
        
    @sql_result()
    def update_task_history_exectime(self, c_user, **kws):
        execute_time=kws.get('execute_time')
        task_name=kws.get('task_name')
        sql='''update %s set execute_time='%s',c_user='%s', c_time=now() where task_name='%s' '''  % (self.t_task_history, execute_time, c_user, task_name)
        return [self.db, sql] 
        
    @sql_result()
    def update_task_history_status_for_twisted(self, status, task_name):
        sql='''update %s set status='%s' where task_name='%s' ''' % (self.t_task_history, status, task_name)
        return [self.db, sql] 
        
    @sql_result()
    def update_task_history_status(self, c_user, status, task_name):
        sql='''update %s set status='%s',c_time=now(),c_user='%s' where task_name='%s' ''' % (self.t_task_history, status, c_user, task_name)
        return [self.db, sql] 
        
    @sql_result()
    def add_task_servers_history(self, c_user, **kws):
        key, value=self.get_insert_key_value(kws)
        sql='''insert into %s (%s, c_time, c_user) values(%s, now(), '%s')''' % (self.t_task_servers_history, key ,value, c_user)
        return [self.db, sql] 
        
    @sql_result()
    def add_task_history(self, c_user, **kws):
        key, value=self.get_insert_key_value(kws)
        sql='''insert into %s (%s, c_time, c_user) values(%s, now(), '%s')''' % (self.t_task_history, key ,value, c_user)
        return [self.db, sql] 
        
    @sql_result()
    def task_relevance_update(self, c_user, **kws):
        value=self.get_update_key_value(kws)
        sql='''update  %s  set %s, c_time=now(), c_user='%s' where relevance_id='%s' '''  % (self.t_task_relevance, value, c_user, kws.get('relevance_id'))
        return [self.db, sql]
        
    @sql_result()
    def task_relevance(self, c_user, **kws):
        key, value=self.get_insert_key_value(kws)
        sql='''insert into %s (%s, c_time, c_user) values (%s, now(), '%s') '''  % (self.t_task_relevance, key, value, c_user)
        return [self.db, sql]
        
    @sql_result()
    def do_dml_sql(self, sql):
        #解决递归场景问题
        return [self.db, sql]

    def get_false(self, datalist):
        for i in datalist:
            if not i:
                return True
        return False
        
    def servergroup_info_change(self, **kws):
        line=kws.get('line')
        line_des=kws.get('line_des')
        product=kws.get('product')
        product_des=kws.get('product_des')
        app=kws.get('app')
        group_id=kws.get('group_id')
        member=kws.get('member')
        app_des=kws.get('app_des')
        group_des=kws.get('group_des')
        type=kws.get('type')
        c_user=kws.get('c_user')
        dotype=kws.get('dotype')
        olddata=kws.get('olddata')
        
        oldline=olddata.get('line')['name']
        oldline_des=olddata.get('line')['des']
        oldproduct=olddata.get('product')['name']
        oldproduct_des=olddata.get('product')['des']
        oldapp=olddata.get('app')['name']
        oldapp_des=olddata.get('app')['des']
        oldgroupinfo=olddata.get('group_id')
        if oldgroupinfo:
            oldgroup_id=oldgroupinfo['name']
            oldgroup_des=oldgroupinfo['des']
        else:
            oldgroup_id=''
            oldgroup_des=''
        oldmember=member
        
        redata={
            'line':line,
            'product':product,
            'app':app
        }
        oldredata={
            'line':oldline,
            'product':oldproduct,
            'app':oldapp
        }
        
        def do_app_update():
            rtd=copy.deepcopy(redata)
            rtdold=copy.deepcopy(oldredata) 
            table='t_serverapp_info'
            
            
            ret=self.get_servergroup_info(type='serverapp', **rtd)
            oldret=self.get_servergroup_info(type='serverapp', **rtdold)
            
            rtd.update({'app_des':app_des})
            key, value=self.get_insert_key_value(rtd)
            insertsql='''insert into %s (%s, c_time, c_user) values (%s, now(), '%s') ''' % (table, key, value, c_user)

            upkey=self.get_update_key_value(rtd)
            wherekey=self.get_sql_with_keys(rtdold)
            updatesql='''update %s set %s, c_time=now(), c_user='%s' where %s ''' % (table, upkey, c_user, wherekey)
            deletesql='''delete from %s where %s '''% (table, wherekey)

            if not ret:
                #添加app
                self.do_dml_sql(insertsql)
                if dotype == "serverappremoval":
                    if ret and oldret and ret != oldret:
                        self.do_dml_sql(deletesql)
                    else:
                        self.do_dml_sql(updatesql)
            else:
                #更新到新记录
                if dotype == "serverappremoval":
                    if ret and oldret and ret != oldret:
                        self.do_dml_sql(deletesql)
                    else:
                        self.do_dml_sql(updatesql)
                elif dotype != 'groupmemberremoval':
                    self.do_dml_sql(updatesql)


                
        def do_group_update():
            rtd=copy.deepcopy(redata)
            rtdold=copy.deepcopy(oldredata) 
            table='t_servergroup_info'
            rtd.update({'group':group_id})
            rtdold.update({'group':oldgroup_id})

            ret=self.get_servergroup_info(type='servergroup', **rtd)
            oldret=self.get_servergroup_info(type='servergroup', **rtdold)

            del rtd['group']
            del rtdold['group']
            rtd.update({'group_id':group_id})
            rtdold.update({'group_id':oldgroup_id})
            rtd.update({'group_des':group_des})
            rtdold.update({'group_des':oldgroup_des})  
            upkey=self.get_update_key_value(rtd, result=True)
            wherekey=self.get_sql_with_keys(rtdold, result=True)
            updatesql='''update %s set %s, c_time=now(), c_user='%s' where %s ''' % (table, upkey, c_user, wherekey)
            deletesql='''delete from %s where %s '''% (table, wherekey)

            if not ret :
                if dotype == "serverappremoval":
                    self.do_dml_sql(updatesql)
                else:    
                    rtd.update({'modal':'yes'})
                    key, value=self.get_insert_key_value(rtd)
                    insertsql='''insert into %s (%s, c_time, c_user) values (%s, now(), '%s') ''' % (table, key, value, c_user)
                    #添加group
                    self.do_dml_sql(insertsql)
                    if dotype == "servergroupremoval" and ret != oldret:
                        self.do_dml_sql(deletesql)
            else: 
                #更新到新记录
                if dotype == "servergroupremoval" and ret != oldret:
                    self.do_dml_sql(deletesql)
                elif dotype != 'groupmemberremoval':    
                    self.do_dml_sql(updatesql)
                    
        def do_member_update():
            rtd=copy.deepcopy(redata)
            rtdold=copy.deepcopy(oldredata) 
            table='t_serverhost_info'
            rtd.update({'member':member})
            rtd.update({'group':group_id})
            rtdold.update({'group':oldgroup_id})
            rtdold.update({'member':member})

            ret=self.get_servergroup_info(type='serverhost', **rtd)
            oldret=self.get_servergroup_info(type='serverhost', **rtdold)
            del rtd['group']
            del rtdold['group']
            rtd.update({'group_id':group_id})
            rtdold.update({'group_id':oldgroup_id})
            upkey=self.get_update_key_value(rtd, result=True)
            wherekey=self.get_sql_with_keys(rtdold, result=True)
            updatesql='''update %s set %s, c_time=now(), c_user='%s' where %s ''' % (table, upkey, c_user, wherekey)
            #if not ret :
            #    key, value=self.get_insert_key_value(rtd)
            #    sql='''insert into %s (%s, c_time, c_user) values (%s, now(), '%s') ''' % (table, key, value, c_user)
            #    #添加group
            #    self.do_dml_sql(sql)
            #else: 
            #更新到新记录
            self.do_dml_sql(updatesql)
            
        if self.get_false([line, product, app, oldline, oldproduct, oldapp ]):
            raise Exception('parameter err.')
        do_app_update()    
        do_group_update()    
        do_member_update()
        return True
        
    def modify_servergroup_info(self, **kws):
        type=kws.get('type')
        if type in ['serverappremoval' , 'servergroupremoval' , 'groupmemberremoval']:
            kws['dotype']=type
            return self.servergroup_info_change(**kws)
        else:
            return self.do_modify_servergroup_info(**kws)
            
    @sql_result()
    def do_modify_servergroup_info(self, **kws):
        type=kws.get('type')
        olddata=kws.get('olddata')
        exclude=['type', 'c_user', 'olddata']
        setkey=[]
        sql_str=''
        if type == 'serverapp':
            table=self.t_serverapp_info
            setkey=['app','label','product','line']
            
        elif type == 'servergroup':
            table=self.t_servergroup_info
            setkey=['app', 'product', 'line' ,'label', 'group_id']

        elif type == "hostlabel":
            table=self.t_serverhost_info
            setkey=['ip', 'label']

        elif type == 'hostchange':
            table=self.t_serverhost_info
            setkey=['ip', 'product', 'app', 'label', 'group_id', 'line']

        elif type == 'serverappremoval' :
            table=self.t_serverhost_info
            setkey=['ip', 'member', 'asset_app', 'group_des', 'group_id', 'modal', 'app_des', 'remark', 'label']

        elif type == 'servergroupremoval' or type == 'groupmemberremoval':
            table=self.t_serverhost_info
            setkey=['ip', 'asset_app', 'member', 'label', 'modal', 'modal', 'app_des', 'remark', 'group_des']

        elif type == 'serverhost' :
            table=self.t_serverhost_info
            setkey=['ip','member','product','app','label','group_id','line']
            
        exclude+=setkey

        
        new_kws={}
        ip=kws.get('ip')
        member=kws.get('member')
        c_user=kws.get('c_user')
        app=kws.get('app')
        app_des=kws.get('app_des')
        group_id=kws.get('group_id')
        group_des=kws.get('group_des')
        label=kws.get('label')

        
        for k in exclude:
            if kws.get(k):
                del kws[k]

        value=self.get_update_key_value(kws, result=True)

        if type == 'serverapp':
            sql='''update %s set %s, c_time=now(), c_user='%s' where app='%s' '''  % (table, value, c_user, app)
        elif type == 'servergroup':                                                                    
            sql='''update %s set %s, c_time=now(), c_user='%s' where group_id='%s' '''  % (table, value, c_user, group_id)
        elif type == 'hostlabel':  
            keys=self.get_sql_with_keys(kws, result=True)
            sql='''update %s set label='%s', c_time=now(), c_user='%s' where %s '''  % (table, label, c_user, keys)
        elif type == 'hostchange':      
            sql='''update %s set %s, c_time=now(), c_user='%s' where member='%s' '''  % (table, value, c_user, ip)
        elif type == 'serverhost':                                                                     
            sql='''update %s set %s, c_time=now(), c_user='%s' where member='%s' '''  % (table, value, c_user, member)

        return [self.db, sql]
        
    @sql_result('query')
    def get_servergroup_info(self, **kws):
        type=kws.get('type')
        sql_str=''
        
        if type == 'serverapp':
            table=self.t_serverapp_info
        elif type in ['servergroup', 'privileges']:
            table=self.t_servergroup_info
        elif type == 'serverhost':
            table=self.t_serverhost_info
            
        sql='''select * from %s '''  % table
        

        if kws.get('app'):
            sql_str+='''  where app='%s' '''  % kws.get('app')
        if kws.get('line'):
            sql_str+='''  and line='%s' '''  % kws.get('line')
        if kws.get('product'):
            sql_str+='''  and product='%s' '''  % kws.get('product')
        if kws.get('group'):
            sql_str+='''  and group_id='%s' '''  % kws.get('group')
        if kws.get('member'):
            if isinstance(kws.get('member'), list):
                str_list=self.get_sql_in_list(kws.get('member'))
                sql_str+='''  and member in (%s) '''  % str_list
            else:
                sql_str+='''  and member='%s' '''  % kws.get('member')
        if kws.get('searchlist'):
            str_list=self.get_sql_in_list(kws.get('searchlist'))
            if type == 'servergroup':
                sql_str+=''' and group_id in (%s) ''' %  str_list
            elif type == 'serverhost':
                sql_str+=''' and member in (%s) ''' %  str_list
        if re.match(r'^[ ]+and(.*)$', sql_str):
            sql_str='where  '+re.match(r'^[ ]+and(.*)$', sql_str).group(1)
            
        sql+=sql_str
        return [self.db, sql]
        
    @sql_result()
    def add_servergroup_info(self, user, **kws):
        type=kws.get('type')
        if type == 'serverapp':
            table=self.t_serverapp_info
        elif type == 'servergroup':
            table=self.t_servergroup_info
        elif type == 'serverhost':
            table=self.t_serverhost_info
        
        del kws['type']
        key, value=self.get_insert_key_value(kws)
        sql='''insert into %s (%s, c_time, c_user) values (%s, now(), '%s') '''  % (table, key, value, user)
        return [self.db, sql]
    
    def get_update_key_value(self, data, result=False):
        sql_str=''
        for k,v in data.items():
            if result and not v:
                continue
            sql_str+=''' %s='%s',''' % (k, v)
            
        return sql_str.strip(',')
        
    def get_insert_key_value(self, data):
        sql_key=''
        sql_value=''
        for k,v in data.items():
            sql_key+=',`'+k+'`'
            sql_value+=''','%s' ''' % v
            
        return [sql_key.strip(','), sql_value.strip(',')]
    
    def get_sql_with_keys(self, data, result=False):
        sql_str=''
        for k,v in data.items():
            if result and not v:
                continue
            sql_str+='''and %s='%s' ''' % (k, v)
        return sql_str.strip('and')
        
    @sql_result()
    def serverinit_reset(self, ip):
        sql='''update %s set status='faild' where telecom_ip='%s' '''  % (self.t_server_init_history, ip)
        return [self.db, sql]
        
    @sql_result()
    def add_serverinit_history(self, telecom_ip, status, tool, c_user):
        if status == '2':
            status='success'
        else:
            status='failed'
        sql='''insert into %s (telecom_ip, status, tool, c_time, c_user) values (
                                '%s', '%s', '%s', now(), '%s') '''  % (self.t_server_init_history, 
                                    telecom_ip, status, tool, c_user)
        return [self.db, sql]
        
    @sql_result('query')
    def get_serverinit_history(self, iplist, type=None):
        sql='''select * from %s '''  % self.t_server_init_history
        sql_str=''
        if type == '2':
            type='success'
        elif type == '1':
            type=''
        elif type == '3':
            type='failed'
            
        if type:
            sql_str+='''  where status='%s' '''  %  type
        if iplist:
            sql_str+=''' and telecom_ip in (%s) '''  % self.get_iplist_sql_str(iplist)
        if re.match(r'^[ ]+and(.*)$', sql_str):
            sql_str='where  '+re.match(r'^[ ]+and(.*)$', sql_str).group(1)
            
        sql+=sql_str

        return [self.db, sql]
        
    @sql_result()
    def delete_logindefault_info(self, data, type=None):
        sql_keys=self.get_sql_with_keys(data)
        if type== 'logindefault' or type == "logintools":
            sql='''delete from %s where %s ''' % (self.t_server_login_default, sql_keys)
        elif type == 'logininit' or type == 'logininitools':
            sql='''delete from %s where %s ''' % (self.t_server_init_manager, sql_keys)
        elif type == 'initoolsmanager':
            sql='''update %s  set tool_path='' where %s ''' % (self.t_server_init_manager, sql_keys)
        return [self.db, sql]
        
    @sql_result()
    def modify_initoolsmanager_info(self, c_user, data, type=None):
        if not self.get_login_default_info(self, line=data.get('line'), product=data.get('product'), app=data.get('app'), 
                    idc=data.get('idc'), owner=data.get('owner'), type=type, name=type):
            key, value=self.get_insert_key_value(data)
            sql='''insert into  %s (%s, c_time, c_user) values(%s, '%s', now(), '%s') ''' % (self.t_server_init_manager, key, value, c_user)
        else:
            value=self.get_update_key_value(data)
            for k in ['user', 'port', 'pwd', 'tool_path']:
                if data.get(k):
                    del data[k]
            sql_keys=self.get_sql_with_keys(data)
            sql='''update %s set %s, c_time=now(), c_user='%s' where %s '''  % (self.t_server_init_manager, value, c_user, sql_keys)

        return [self.db, sql]
        
    @sql_result()
    def modify_logininit_info(self, c_user, data, type=None):
        if not self.get_login_default_info(self, line=data.get('line'), product=data.get('product'), app=data.get('app'), 
                    idc=data.get('idc'), owner=data.get('owner'), type=type, name=type):
            key, value=self.get_insert_key_value(data)
            sql='''insert into  %s (%s, type, c_time, c_user) values(%s, '%s', now(), '%s') ''' % (self.t_server_init_manager, key, value, type, c_user)
        else:
            value=self.get_update_key_value(data)
            for k in ['user', 'port', 'pwd']:
                if data.get(k):
                    del data[k]
            sql_keys=self.get_sql_with_keys(data)
            sql='''update %s set %s, type='%s',c_time=now(), c_user='%s' where %s '''  % (self.t_server_init_manager, value,  type, c_user, sql_keys)

        return [self.db, sql]
        
    @sql_result()
    def modify_logindefault_info(self, c_user, data, type=None):
        if not self.get_login_default_info(self, line=data.get('line'), product=data.get('product'), app=data.get('app'), 
                    idc=data.get('idc'), owner=data.get('owner'), type=type):
            key, value=self.get_insert_key_value(data)
            sql='''insert into  %s (%s, type, c_time, c_user) values(%s, '%s', now(), '%s') ''' % (self.t_server_login_default, key, value, type, c_user)
        else:
            value=self.get_update_key_value(data)
            for k in ['user', 'port', 'pwd']:
                if data.get(k):
                    del data[k]
            sql_keys=self.get_sql_with_keys(data)
            sql='''update %s set %s, type='%s', c_time=now(), c_user='%s' where %s '''  % (self.t_server_login_default, value,  type, c_user, sql_keys)

        return [self.db, sql]
        
    @sql_result()
    def delete_loginmanager_info(self, ip):
        sql='''delete from %s where ip='%s' ''' % (self.t_server_login_manager, ip)
        return [self.db, sql]
        
    @sql_result()
    def modify_loginmanager_ip(self, ip, newip, c_user):
        sql='''update %s set ip='%s', c_time=now(), c_user='%s' where ip='%s' ''' % (self.t_server_login_manager, newip, c_user, ip)
        return [self.db, sql]
        
    @sql_result()
    def modify_loginmanager_info(self, ip, user, port, enpwd, c_user):
        sql='''replace into %s (ip,user,port,pwd,c_time,c_user) values('%s', '%s', '%s', '%s', now(), '%s') ''' % (self.t_server_login_manager, ip, user, port, enpwd, c_user)
        return [self.db, sql]
        
    @sql_result('query')
    def get_login_default_info(self, line=None, product=None, app=None, 
                    idc=None, owner=None, type=None, name=None):
        if type in ["logininit", "logininitools", 'initoolsmanager']:
            sql='''select * from %s '''  % self.t_server_init_manager
        elif not name or name == 'logindefault' or name == 'logintools':
            sql='''select * from %s '''  % self.t_server_login_default
            
        sql_str=''
        if line and line != '0':
            sql_str+=''' where line='%s' '''   % line
        if product and product != '0':
            sql_str+=''' and product='%s' '''   % product
        if app and app != '0':
            sql_str+=''' and app='%s' '''   % app
        if idc and idc != '0':
            sql_str+=''' and idc='%s' '''   % idc
        if owner:
            sql_str+=''' and owner='%s' '''   % owner

        if re.match(r'^[ ]+and(.*)$', sql_str):
            sql_str='where  '+re.match(r'^[ ]+and(.*)$', sql_str).group(1)
            
        sql+=sql_str

        return  [self.db, sql]
    
    @sql_result('query')
    def get_login_manager_info(self, iplist):
        iplist_sql=self.get_iplist_sql_str(iplist)
        sql='''select * from %s where ip in (%s) ''' % (self.t_server_login_manager, iplist_sql)
        return  [self.db, sql]
        
    @sql_result()
    def mod_asset(self, ip, data):
        setlist=''
        for k,v in data.items():
            setlist+='`'+k+"`"+"='%s'" % v + ","
        setlist=setlist.strip(',')

        sql='''update %s set %s where telecom_ip='%s' '''  % (self.t_assets_info, setlist, ip)
        return  [self.db, sql]

    def modfiy_asset_info(self, ip, data, user):
        self.add_assets_history('modify', user, data, ip=ip)
        self.mod_asset(ip, data)
        return True

    @sql_result()
    def del_info(self, ip):
        sql='''delete from %s where telecom_ip="%s" ''' % (self.t_assets_info, ip)
        return [self.db, sql]
        
    def delete_asset_info(self, ip, user):
        self.add_assets_history('delete', user, ip)
        self.del_info(ip)
        return True

    @sql_result('query')
    def get_other_setvalue_record(self, key=None):
        if not key:
            sql='''select * from %s '''   % self.t_other_setvalue_record
        else:
            sql='''select * from %s where `key`='%s' '''  % (self.t_other_setvalue_record, key)
        return [self.db, sql]
        
    @sql_result()
    def other_setvalue_record(self, key, value , user=None):
        sql='''replace into %s (`key`, `value`, c_time, c_user) values ('%s', '%s', now(), '%s') '''  % (self.t_other_setvalue_record, key, value, user)
        return [self.db, sql]
    
    
    @sql_result('query')
    def assets_history_search(self, line=None, product=None, app=None, 
                    idc=None, other_key=None, iplist=None, key=None, key_value=None,
                    start=None, end=None
                    ):
        if key:
            if key_value:
                sql='''select * from %s where %s='%s' ''' % (self.t_assets_history_change, key, key_value)
            else:
                sql='''select %s from %s ''' % (key, self.t_assets_history_change)
        else:
            sql='''select * from %s '''  % self.t_assets_history_change
        sql_str=''
        if line and line != '0':
            line=line.replace('*', '\\\*').replace('.','\\\.')
            sql_str+='''  where (old_info regexp '"line": "%s"' or new_info regexp '"line": "%s"') '''   % (line, line)
        if product and product != '0':
            product=product.replace('*', '\\\*').replace('.','\\\.')
            sql_str+=''' and (old_info regexp '"product": "%s"' or new_info regexp '"product": "%s"') '''   % (product, product)
        if app and app != '0':
            app=app.replace('*', '\\\*').replace('.','\\\.')
            sql_str+=''' and (old_info regexp '"app": "%s"' or new_info regexp '"app": "%s"') '''   % (app, app)
        if idc and idc != '0':
            idc=idc.replace('*', '\\\*').replace('.','\\\.')
            sql_str+=''' and (old_info regexp '"idc": "%s"' or new_info regexp '"idc": "%s"') '''   % (idc, idc)
        if other_key:
            kl=other_key.split(':')
            sql_str+=''' and old_info regexp '"%s": "%s"' '''   % (kl[0], kl[1].replace('*', '\\\*').replace('.','\\\.'))

        if iplist:
            if not isinstance(iplist, list):
                iplist=[iplist]
            ip_reg=''
            for ip in iplist:
                ip_reg+='"telecom_ip": "%s"|"unicom_ip": "%s"|"inner_ip": "%s"|' % (ip, ip, ip)
            ip_reg=ip_reg.strip('|')
            sql_str+=''' and (old_info  regexp '(%s)' or new_info regexp '(%s)') ''' % (ip_reg, ip_reg)
            
        if re.match(r'^[ ]+and(.*)$', sql_str):
            sql_str='where  '+re.match(r'^[ ]+and(.*)$', sql_str).group(1)
        sql+=sql_str
        if start and end:
            sql += ''' limit %s, %s '''  % (int(start), int(end))
        
        return  [self.db, sql]
       
    def get_iplist_sql_str(self, iplist):
        if not isinstance(iplist, list):
            iplist=[iplist]
        return '"'+', '.join(iplist).replace(', ', '","')+'"'
                    
    @sql_result('query')
    def assets_search(self, line=None, product=None, app=None, 
                    idc=None, other_key=None, iplist=None, key=None,
                    start=None, end=None):
        if key:
            sql='''select %s from %s ''' % (key, self.t_assets_info)
        else:
            sql='''select * from %s '''  % self.t_assets_info
        sql_str=''
        if line and line != '0':
            sql_str+='''  where line='%s' '''   % line
        if product and product != '0':
            sql_str+=''' and product='%s' '''   % product
        if app and app != '0':
            sql_str+=''' and app='%s' '''   % app
        if idc and idc != '0':
            sql_str+=''' and idc='%s' '''   % idc
        if other_key:
            kl=other_key.split(':')
            sql_str+=''' and %s='%s' '''   % (kl[0], kl[1])
        if iplist:
            if not isinstance(iplist, list):
                iplist=[iplist]
            
            iplist=self.get_iplist_sql_str(iplist)
            sql_str+=''' and telecom_ip in (%s) or unicom_ip in (%s) or inner_ip in (%s) ''' % (iplist, iplist, iplist)
            
        if re.match(r'^[ ]+and(.*)$', sql_str):
            sql_str='where  '+re.match(r'^[ ]+and(.*)$', sql_str).group(1)
        sql+=sql_str
        if start and end:
            sql += ''' limit %s, %s '''  % (int(start), int(end))
        
        return  [self.db, sql]
        
    @sql_result('query')
    def get_assets(self, ip=None, start=None, end=None):
        if not ip and not start and  not  end:
            sql='''select * from %s''' %  self.t_assets_info
        elif end and not ip and not start:
            sql='''select * from %s limit 0, %s''' %  (self.t_assets_info, end)
        elif ip and not start and not end:
            sql='''select * from %s where telecom_ip="%s"''' %  (self.t_assets_info, ip)
            
        return  [self.db, sql]

    @sql_result('get')
    def import_check(self, cvsdata):
        sql='''select distinct telecom_ip  from %s  where telecom_ip="%s"'''  % (self.t_assets_info, cvsdata['telecom_ip'])
        return  [self.db, sql]

    def import_assets_info(self, cvsdata, user, operation='import'):
        if self.import_check(cvsdata):
           return "exists"
        self.import_asset(user, cvsdata)
        self.add_assets_history(operation, user, cvsdata)
        return True
        
    @sql_result()
    def import_asset(self, user, cvsdata):
        sql='''replace into %s (telecom_ip, unicom_ip, inner_ip, line, product, app, `describe`, idc, serial_number, owner, os, mem, disk, cpu, firm, remark, c_time, c_user)   values("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", now(),"%s")''' % (self.t_assets_info, cvsdata['telecom_ip'], cvsdata['unicom_ip'], cvsdata['inner_ip'], cvsdata['line'], cvsdata['product'], cvsdata['app'], cvsdata['describe'], cvsdata['idc'], cvsdata['serial_number'], cvsdata['owner'], cvsdata['os'], cvsdata['mem'], cvsdata['disk'], cvsdata['cpu'], cvsdata['firm'], cvsdata['remark'], user)
        return  [self.db, sql]
        
    
    @sql_result()
    def add_assets_history(self, operation, user, cvsdata, ip=None):
        if operation == 'import':
            old=json.dumps(self.get_assets(ip=cvsdata['telecom_ip']), ensure_ascii=False)
            sql='''insert into %s (ip, c_user, old_info, c_type, c_time) values("%s","%s",'%s', '%s', now())''' % (self.t_assets_history_change, cvsdata['telecom_ip'], user, old, operation)
        elif operation=="delete": 
            old=json.dumps(self.get_assets(ip=cvsdata), ensure_ascii=False)
            sql='''insert into %s (ip, c_user, old_info, c_type, c_time) values("%s","%s", '%s',"%s", now())''' % (self.t_assets_history_change, cvsdata, user, old, operation)
        elif operation=="modify":
            #为了和delete信息统一，使用[{}]格式
            new=json.dumps([cvsdata], ensure_ascii=False)
            old=json.dumps(self.get_assets(ip=ip), ensure_ascii=False)
            sql='''insert into %s (ip, c_user, old_info, new_info, c_type, c_time) values("%s","%s", '%s', '%s',"%s", now())''' % (self.t_assets_history_change, ip, user, old, new, operation)
            
        return  [self.db, sql]
        
    
    @sql_result()
    def account_contact_info_update(self, name, type, data, user):
        if type == "email":
            sql='''update %s set member='%s', c_time=now(), c_user='%s' where name='%s' and type='email' ''' % (self.t_inform_account_info, data, user , name)
        elif type == "wechat":
            sql='''update %s set member='%s', c_time=now() , c_user='%s' where wechatid='%s' and type='wechat' ''' % (self.t_inform_account_info, data, user , name)
        return  [self.db, sql]    
        
    @sql_result()
    def privilege_user_member_update(self, group, data, user):
        sql='''update %s set member='%s', type='member_change', opertion_time=now(), opertion_user='%s' where name='%s' '''  % (self.t_privilege_allocate, data, user, group)
        return  [self.db, sql]
        
    @sql_result()
    def privilege_peivilege_member_update(self, group, data, user):
        sql='''update %s set privi_list='%s', type='privilege_change', opertion_time=now(), opertion_user='%s' where name='%s' '''  % (self.t_privilege_allocate, data, user, group)
        return  [self.db, sql]

    @sql_result()
    def privilege_user_group_update(self, group, member, oper_user, type=None):
        sql=''' update %s set member='%s',opertion_time=now(),opertion_user='%s' where name='%s' ''' % (self.t_privilege_allocate, member, oper_user, group)
        return  [self.db, sql]
 
    @sql_result()
    def delete_contact_info(self, name):
        sql='''delete from %s where  name='%s' '''  % (self.t_inform_contact_info, name)
        return  [self.db, sql]
    
    @sql_result()
    def delete_account_info(self, account, type=None):
        if type == "email":
            sql='''delete from %s where name='%s' ''' % (self.t_inform_account_info, account)
        elif type == "wechat":
            sql='''delete from %s where wechatid='%s' ''' % (self.t_inform_account_info, account)
        
        return  [self.db, sql]

    @sql_result()
    def modify_key_info(self, name, value, user):
        sql='''update %s set value='%s', opertion_time=now(), opertion_user='%s' where name='%s' ''' % (self.t_verify_key, value, user, name)
        return  [self.db, sql]
        
    
    @sql_result()
    def delete_key_info(self, name):
        sql='''delete from %s where name='%s' ''' % (self.t_verify_key, name)
        return  [self.db, sql]
        
    
    @sql_result()
    def delete_user_info(self, user):
        sql=''' delete from %s where user='%s' ''' % (self.t_user_info, user)
        return  [self.db, sql]
        
    @sql_result()
    def delete_privilege_member(self, user, oper_user):
        sql='''update %s  set member=replace(member, ', %s', ''), opertion_time=now(), type="member_delete", opertion_user='%s' where member regexp '", %s,"' ''' % (self.t_privilege_allocate, user, oper_user, user)
        return  [self.db, sql]

    def delete_group_info(self, group):
        self.delete_group(group)
        self.delete_privilege_allocate_info(group)
        return True
        
    @sql_result()
    def delete_privilege_allocate_info(self, group):
        sql='''delete from %s where name='%s' ''' % (self.t_privilege_allocate, group)
        return  [self.db, sql]
    
    @sql_result()
    def delete_group(self, group):
        sql='''delete from %s where name='%s' ''' % (self.t_group_info, group)
        return  [self.db, sql]
    
    @sql_result()
    def privilege_group_member_update(self, group, member, oper_user, type=None):
        sql=''' replace into %s (name, privi_list, member, type, time, user) values('%s', privi_list, ', %s', now(), '%s', '%s') ''' % (self.t_privilege_allocate, group, member, type, oper_user)
        return  [self.db, sql]
    
    @sql_result('query')
    def get_privilege_allocate_info(self, group=None, user=None):
        if not group and not user:
            sql=''' select * from %s ''' % self.t_privilege_allocate
        elif group and not user:
            sql=''' select * from  %s where  name='%s' '''  % (self.t_privilege_allocate, group)
        elif not group and user:
            sql=''' select * from  %s where  member  regexp ',{0,}[ ]{0,}%s' '''  % (self.t_privilege_allocate, user)
        elif group and user:
            sql=''' select * from  %s where name='%s' and member  regexp ',[ ]{0,}%s' '''  % (self.t_privilege_allocate, group, user)
        return  [self.db, sql]
    
    @sql_result()
    def account_status_change(self, type, name, status, c_user):
        if status == "on":
            estatus="off"
        else:
            estatus="on"

        if type == 'email' and status=="on":
            sql='''update %s set status=case when name='%s'  and (status='off' or status is null) then '%s' else '%s' end, c_time=now(), c_user='%s'  where type='%s' ''' %(self.t_inform_account_info, name, status, estatus, c_user, type)
        elif type=="email"  and status=="off":
            sql='''update %s set status='%s', c_time=now(), c_user='%s'  where type='%s' and name='%s' ''' %(self.t_inform_account_info, status, c_user, type, name)
        elif type=="wechat"  and status=="off":
            sql='''update %s set status='%s', c_time=now(), c_user='%s'  where type='%s' and wechatid='%s' ''' %(self.t_inform_account_info, status, c_user, type, name)
        elif type=="wechat"  and status=="on":
            sql='''update %s set status=case when wechatid='%s'  and (status='off' or status is null) then '%s' else '%s' end, c_time=now(), c_user='%s'  where type='%s' ''' %(self.t_inform_account_info, name, status, estatus, c_user, type)
        return  [self.db, sql]
    
    @sql_result()
    def add_inform_contact(self, name, des, type , c_user):
        sql='''insert into %s (name, des, type, c_time, c_user) values ('%s', '%s', '%s', now(), '%s') ''' % (self.t_inform_contact_info, name, des, type, c_user)
        return  [self.db, sql]  
        
    @sql_result()
    def add_inform_account(self, c_user, name=None, des=None, pwd=None, server=None, smtp_ssl_port=None, smtp_port=None, wechatid=None, wechatsecret=None, type=None):
        if type == "email":
            sql='''insert into %s (name, pwd, des, email_server, smtp_ssl_port, smtp_port, type, c_time, c_user) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', now(), '%s')''' % (self.t_inform_account_info, name, pwd, des, server , smtp_ssl_port, smtp_port, type, c_user)
        elif type =="wechat":
            sql='''insert into %s (wechatid, wechatsecret, type, c_time, c_user) values('%s', '%s', '%s', now(), '%s') ''' % (self.t_inform_account_info, wechatid, wechatsecret, type, c_user)
        return  [self.db, sql]  
        
    @sql_result('query')
    def get_inform_contact_info(self, type=None, name=None):
        if name and type:
            sql='''select * from %s where name='%s' and type='%s' '''  % (self.t_inform_contact_info, name, type)
        elif type:
            sql='''select * from %s where type='%s' '''  % (self.t_inform_contact_info, type)
        else:
            sql='''select * from %s '''  % (self.t_inform_contact_info)

        return  [self.db, sql]     
        
    @sql_result('query')
    def get_inform_account_info(self, name=None, type=None):
        if name and type:
            if type == "email":
                key_name="name='%s'" % name
            elif type == "wechat":
                key_name="wechatid='%s'" % name
            sql='''select * from %s where %s and type='%s' '''  % (self.t_inform_account_info, key_name, type)
        elif type:
            sql='''select * from %s where type='%s' '''  % (self.t_inform_account_info, type)
        else:
            sql='''select * from %s '''  % (self.t_inform_account_info)
            
        return  [self.db, sql]  
        
    @sql_result('query')
    def get_privilege_info(self, name=None):
        if not name:
            sql='''select * from %s '''  % self.t_privilege_info
        else:
            sql ='''select * from %s where name='%s' '''  % (self.t_privilege_info, name)
        return  [self.db, sql]  
         
    @sql_result()
    def add_verify_key_info(self, name, des, value, user):
        sql='''insert into %s (name, des, value, opertion_time, opertion_user) values('%s', '%s', '%s', now(), '%s') ''' % (self.t_verify_key, name, des, value, user)
        return  [self.db, sql]
    
    @sql_result('query')
    def get_verify_key_info(self, name=None):
        if not name:
            sql='''select * from %s ''' % (self.t_verify_key)
        else:
            sql='''select * from %s where name='%s' ''' % (self.t_verify_key, name)
        return  [self.db, sql]
        
    @sql_result('query')
    def get_user_info(self, user=None):
        if user:
            sql='''select * from %s where user="%s"''' % (self.t_user_info, user)
        else:
            sql='''select * from %s ''' % (self.t_user_info)
        return  [self.db, sql]
        
    @sql_result()
    def set_login_time(self, **kws):
        user=kws.get('user')
        sql='''update %s set last_login=now() where user='%s' ''' % (self.t_user_info, user)
        return  [self.db, sql]
        
    @sql_result()
    def add_user_info(self, user, des, c_user):
        sql='insert into %s (user, des, type, c_time, c_user) values ("%s","%s","create", now(),"%s");' % (self.t_user_info, user, des, c_user)
        return  [self.db, sql]
        
    @sql_result('query')
    def get_group_info(self, group=None):
        if not group:
            sql=''' select * from %s  ''' % self.t_group_info
        else:
            sql='''select * from %s where name="%s"''' % (self.t_group_info, group)
        return  [self.db, sql]
    
    def add_group_info(self, group, des, c_user):
        self.add_group(group, des, c_user)
        self.add_group_to(group)
        return True

    @sql_result()
    def add_group_to(self, group):
        sql='insert into %s (name) values ("%s");' % (self.t_privilege_allocate, group)
        return  [self.db, sql]
    
    @sql_result()
    def add_group(self, group, des, c_user):
        sql='insert into %s (name, des , c_time, c_user) values ("%s","%s", now(),"%s");' % (self.t_group_info, group, des, c_user)
        return  [self.db, sql]
        
    @sql_result('query')
    def get_fault_info(self, name=None, zone=None, h_time=None, status=None, iplist=None):
        sql='''select * from %s '''   % self.t_fault_handle
        sql_str=''
        if name and str(name) != '0':
            sql_str+='''  where name='%s' '''  % name
        if zone and str(zone) != '0':
            sql_str+='''  and  zone_name='%s' '''  % zone
        if status and str(status) != '0':
            sql_str+='''  and  status='%s' '''  % status
        if h_time and str(h_time) != '0':
            sql_str+='''  and  h_time regexp '%s' '''  % h_time.split(' ')[0]
        if iplist:
            sql_str+='''  and  ip in (%s) '''  % self.get_sql_iplist(iplist)
        if re.match(r'^[ ]+and(.*)$', sql_str):
            sql_str='where  '+re.match(r'^[ ]+and(.*)$', sql_str).group(1)
            
        sql+=sql_str    
        return [self.db,sql]

    @sql_result()
    def fault_commit(self, id, status, remark, c_user):
        sql='''update %s set status='%s', remark='%s', c_time=now(), c_user='%s' where id='%s' '''   % (self.t_fault_handle, status, remark, c_user, id)
        return [self.db,sql]
        
    @sql_result()
    def fault_add(self, ip, name, zone=None, des=None):
        sql='''insert into %s (ip, name, zone_name, status, h_time, faultdes) values('%s', '%s', '%s', '%s', now(), '%s') '''   %   (self.t_fault_handle, ip, name, zone, '1', des) 
        return [self.db,sql]
         
    @sql_result('query')
    def get_server_privilege(self, **kws):
        where_str=self.get_sql_with_keys(kws)
        sql=''' select * from %s where %s ''' % (self.t_serverprivilege_info, where_str)
        return [self.db,sql]
        
    @sql_result()
    def add_server_privilege(self, c_user, **kws):
        key, value=self.get_insert_key_value(kws)
        sql='''insert into %s (%s, c_time, c_user) values (%s, now(), '%s') '''  % (self.t_serverprivilege_info, key, value, c_user)
        return  [self.db, sql]
        
    @sql_result()
    def del_server_privilege(self, **kws):
        where_str=self.get_sql_with_keys(kws)
        sql='''delete from %s where %s ''' % (self.t_serverprivilege_info, where_str)
        return  [self.db, sql]
        
    @sql_result()
    def update_server_privilege(self, c_user, **kws):
        td={}
        td['privilege']=kws.get('privilege')
        td['filelist']=kws.get('filelist')

        d={}
        d["id"]=kws.get('id')
        d["line"]=kws.get('line')
        d["product"]=kws.get('product')
        d["app"]=kws.get('app')
        d["group_id"]=kws.get('group')
        
        upkey=self.get_update_key_value(td, result=True)
        if d.get('id'):
            where_str=''' `id`='%s' ''' % d.get('id')
        else:
            where_str=self.get_sql_with_keys(d)
        sql='''update %s set %s, c_user='%s', c_time=now() where  %s '''  % (self.t_serverprivilege_info, upkey, c_user, where_str)
        return  [self.db, sql]
    
