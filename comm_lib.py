#!/usr/bin/python
#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import logging, os, re, socket, signal, json, datetime, time, struct, zipfile, shutil, telnetlib, threading, Queue, thread, urllib2, hashlib,smtplib, cookielib, urllib
#from xml.etree import ElementTree as et
from  xml.dom import minidom
from email.mime.text import MIMEText
from email.header import Header

curr_path=os.path.split(os.path.realpath(__file__))[0]

def obj_to_json(data):
    try:
        return json.dumps(data, ensure_ascii=False)
    except:
        return data
        
def json_to_obj(data):
    try:
        return json.loads(data)
    except:
        return data
    
def makedirs(filepath):
    if not os.path.exists(os.path.split(filepath)[0]):
        os.makedirs(os.path.split(filepath)[0])
    
def filecopy(source, dest):
    if not isexists(source):
        return 
    makedirs(dest)
    shutil.copy(source, dest)

def read_file(file_path):
    with open(file_path) as f:
        return f.read()
        
def write_file(file_path, file_obj, overwrite=False):
    makedirs(file_path)
    if file_obj:
        if not overwrite:
            k='a+'
        else:
            k='wb'
        with open(file_path, k) as f :
            f.write(file_obj)
    if os.path.exists(file_path):
        return  True
    else:
        return  False
        
def create_dirs(file_path):
    if not os.path.exists(file_path):
        try:
            os.makedirs(file_path)
        except:
            pass
        
        
def filter_int(data):
    return [ i for i in data if not isinstance(i, int) ]
         

def to_datetime_obj(time_str):
    if not time_str:
        return to_datetime_obj(str(datetime.datetime.now()).split('.')[0])
    date_time_info=time_str.replace('-', " ").replace(":", " ").replace(".", " ").split(" ")
    return datetime.datetime(int(date_time_info[0]), int(date_time_info[1]), int(date_time_info[2]), int(date_time_info[3]), int(date_time_info[4]), int(date_time_info[5]))

def get_now():
    return re.match(r'(.*)\.[0-9]+', str(datetime.datetime.now())).group(1)
    
def get_today():
    return  datetime.date.today()
    
def get_dest_day(day):
    day=str(day)
    if re.match(r'^-{1}\d+$', day):
        #timedelta可以控制days、seconds、minutes、hours、weeks等
        #负数为几天后，正数为几天前
        return (datetime.datetime.now()-datetime.timedelta(days=int(day.replace('-', '')))).strftime("%Y-%m-%d")
    elif re.match(r'^\d+$', day):
        return (datetime.datetime.now()-datetime.timedelta(days=int('-'+str(day)))).strftime("%Y-%m-%d")
    else:
        return None

def get_dest_time(minutes):
    minutes=str(minutes)
    if re.match(r'^-{1}\d+$', minutes):
        return (datetime.datetime.now()-datetime.timedelta(minutes=int(minutes.replace('-', '')))).strftime("%Y-%m-%d %H:%M:%S")
    elif re.match(r'^\d+$', minutes):
        return (datetime.datetime.now()-datetime.timedelta(minutes=int('-'+str(minutes)))).strftime("%Y-%m-%d %H:%M:%S")
    else:
        return None
        
def isexists(filepath):
    if os.path.exists(filepath):
        return True
    else:
        return False

def backup_file(filepath):
    if os.path.exists(filepath):
        os.rename(filepath, filepath+str(get_now()).replace(' ', '_'))
        

def pack_socket_data(data, data_type='str', dest_path=None, id=None):
    if isinstance(data, dict) or isinstance(data, list) or isinstance(data, tuple):
        data=json.dumps(data)

    if isinstance(dest_path, unicode):
        dest_path=str(dest_path)
    
    #打包格式为：包长，类型（0为字符串，1为文件），文件名长度（拆包时候使用）, md5，文件名（类型为1时候）/数据
    if data_type=='file':
        format='IIII%ds%ds%ds' % (len(dest_path), 32, len(data))
        dt=struct.pack(format,struct.calcsize(format), 1, len(dest_path), int(id), dest_path, getmd5(data), bytes(data))

    elif data_type=='str':
        if not isinstance(data, str):
            data=json.dumps(data)
        format='II%ds%ds' % (32, len(data))
        dt=struct.pack(format, struct.calcsize(format), 0, getmd5(data), data)

    else:
        raise Exception("parameter err.")

    return dt

def recv_data(skt, getheader=False, getbody=False, header=None):
    buff=''
    r_len=0
    toal_len=0
    n_len=0
    
    def recv_data_from_socket(ln, recved=False, count_len=False):
        dt=""
        ln=int(ln)
        while 1:
            try:
                data=skt.recv(ln)
                dt+=data
                ln-=len(data)
            except:
                pass
            finally:
                if (not recved or dt) and not count_len:
                    return dt
                
                elif count_len :
                    if ln == 0:
                        return dt
                #return dt
    if not getbody:                    
        #首4字节是包长    
        d=recv_data_from_socket(4) 
        if not d:
            return False
        d_len=struct.unpack('I', d)[0]
        if getheader:
            return d_len
    else:
        d_len=header

    #第二4字节是类型
    r_d=recv_data_from_socket(4, recved=True)
    t_p=struct.unpack('I', r_d)[0]
    #0为字符串
    if t_p==0:
        #前8(II)字节已收, 剩下的为s类型
        toal_len=int(d_len) - 8 
    #1为文件
    elif t_p==1:
        #收取dest_path长度
        dest_path=recv_data_from_socket(4, recved=True)
        #文件处理类型0/1
        fid=recv_data_from_socket(4, recved=True)
        #前16(IIII)字节已收, 剩下的为s类型
        toal_len=int(d_len) - 16 
        r_d=r_d+dest_path+fid

    #剩下的数据为字符串S类型, 用len获取长度
    buff=skt.recv(toal_len)
    r_len=len(buff)
    if r_len < toal_len:
        n_len=toal_len - r_len
        n_data=recv_data_from_socket(n_len, recved=True, count_len=True)
    else:
        n_data=''

    buff=r_d+buff+n_data
    return    buff     

def recv_socket_data(skt):    
    d=recv_data(skt)
    if not d:
        return d
    else:
        #这里只返回数据json串需要手动转，其他时候为数据本身，需要返回所有打包信息使用recv_data在手动拆包
        return unpack_sock_data(d)['data']
        
def unpack_sock_data(data):
    try:
        #文件
        file_len=int(struct.unpack('I', data[4:8])[0])
        return  dict(zip(['d_type', 'file_name_len', 'id', 'filename', 'md5', 'data'], struct.unpack('III%ds%ds%ds' % (file_len, 32, len(data)-12-file_len-32), data)))
    except:
        #字符串 
        return  dict(zip(['d_type', 'md5', 'data'], struct.unpack('I%ds%ds' % (32, int(len(data))-36), data)))


def send_socket_data(skt, data, data_type='str', dest_path=None, id=None):
    pack_data=pack_socket_data(data, data_type=data_type, dest_path=dest_path, id=id)
    failed_count=int()
    while 1:
        try:
           data=pack_data
           while 1:
              if not data:
                 break;
              s_len=skt.send(data)
              if s_len != len(data):
                 data=data[s_len:]
                 failed_count=int()
                 time.sleep(0.001)
              else:
                 return True
        except:
           failed_count+=1
           if failed_count >= 300:
              return False
           pack_data=data
           time.sleep(0.2)

class log:
    def __init__(self, log_name):
        if not isexists(os.path.split(log_name)[0]):
            os.makedirs(os.path.split(log_name)[0])
        #定义日志文件
        self.log_name=log_name
        #创建logger对象
        self.logger = logging.getLogger('logger') 
        self.logger.setLevel(logging.DEBUG)
        #输出格式
        #self.formatter=logging.Formatter('%(asctime)s - %(funcName)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s')
        self.formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #2个handle，logfile_handle写日志，screen_handle输出到屏幕
        self.logfile_handle=logging.FileHandler(self.log_name)  
        self.logfile_handle.setLevel(logging.DEBUG)
        #设置格式
        self.logfile_handle.setFormatter(self.formatter)
        self.logger.addHandler(self.logfile_handle)
        self.screen_handle=logging.StreamHandler()
        self.screen_handle.setLevel(logging.DEBUG)
        self.screen_formatter=logging.Formatter('%(message)s')
        self.screen_handle.setFormatter(self.screen_formatter)
        #handle添加到logger
        self.logger.addHandler(self.screen_handle)
    def checkback(self):
        if not os.path.exists(self.log_name+str(get_dest_day(-1))):
            if os.path.exists(self.log_name):
                shutil.copy(self.log_name, self.log_name+str(get_dest_day(-1)))
                with open(self.log_name, 'wb') as f:
                    pass
            
    def file(self, info):
        self.checkback()
        self.logger.removeHandler(self.screen_handle)
        self.logger.info(info)
    def info(self, info):
        self.checkback()
        self.logger.addHandler(self.screen_handle)
        self.logger.info(info)
    def warn(self, info):
        self.checkback()
        self.logger.addHandler(self.screen_handle)
        self.logger.warning(info)
    def err(self, info):
        self.checkback()
        self.logger.addHandler(self.screen_handle)
        self.logger.error(info)

class xml:
    def __init__(self, filepath):
        self.xmlpath=filepath
        self.dom=minidom.parse(self.xmlpath)
        self.root=self.dom.documentElement
        
    def get_all_tag(self, tagname):
        return self.root.getElementsByTagName(tagname)
        
    def get_tag(self, tagname, attribkey=None, attribvalue=None):
        tag_list=self.dom.getElementsByTagName(tagname)
        for tn in tag_list:
            if tn.getAttribute(attribkey) == attribvalue:
               return  tn
        return None

    def get_text(self, element, tag, attrib=None):
        for e in element.childNodes:
            if e.nodeName == tag and attrib == None:
                return e.firstChild.data
            elif e.nodeName == tag and attrib != None:
                return e.getAttribute(attrib)
                
    def getallconf(self, confname):
        return self.get_tag(self.root)
        
    def write(self, filepath):
        with open(filepath, 'wb') as f :
            self.dom.writexml(f, '\n', "\t", '', "utf-8")
        
    def get_attrib(self, element, tag_name, attrib):
        return self.get_text(element, tag_name, attrib)
        
def get_db_info(dbxmlconf):
    dbxml=xml(dbxmlconf)
    db_config=dbxml.get_tag("config", "name", "db")
    all_child={}
    for ch in db_config.childNodes:
        if ch.firstChild == None or ch.firstChild.nodeType != 3:
           continue
        all_child[ch.nodeName]=ch.firstChild.data
    return all_child

def getmd5(obj):
    md5=hashlib.md5()
    try:
        if os.path.exists(obj) == True:
            with open(obj, 'rb') as pr:
                while True:
                    black=pr.read(1024)
                    if not black:
                        break;
                md5.update(black)
        else:
            md5.update(obj)
    except:
        md5.update(obj)
        
    return md5.hexdigest()

def do_send_wechat(**kws):
    #微信公众号上应用的CropID和Secret
    id=kws.get('weid')
    user=kws.get('user')
    secret=kws.get('wechatsecret')
    message=kws.get('message')
    title='[operation_platform]%s' % message[:50]
    
    #获取access_token
    GURL="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (id, secret)
    result=json.loads(urllib2.urlopen(urllib2.Request(GURL)).read())
    token=result['access_token']
    #生成通过post请求发送消息的url
    puturl="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % token

    #企业号中的应用id
    AppID=1
    #部门成员id，微信接收者
    UserID=1
    if user:
       UserID=user 
    #生成post请求信息
    post_data = {
        "touser":UserID,
        "msgtype":'text',
        "agentid":AppID,
        "text":{
            "content":message
        },
        "safe":"0"
    }

    header = {'Content-Type':'application/x-www-form-urlencoded','charset':'utf-8'}
    cj_c = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj_c))
    urllib2.install_opener(opener)
    request=urllib2.Request(url=puturl, data=json.dumps(post_data, ensure_ascii=False), headers=header)
    #request=urllib2.Request(url=puturl, data=urllib.urlencode(post_data))
    response=json.loads(urllib2.urlopen(request).read())
    return response

def send_wechat(user, dbinfo, message):
    weid=dbinfo.get('wechatid')
    secret=dbinfo.get('wechatsecret')
    do_send_wechat(weid=weid, wechatsecret=secret, message=message, user=user)

def do_send_email(**kws):
    fromuser=kws.get('fromuser')
    pwd=kws.get('pwd')
    touser=kws.get('touser')
    ssl_port=kws.get('ssl_port')
    smtp_server=kws.get('smtp_server')
    smtp_port=kws.get('smtp_port', 25)
    msg=kws.get('message')
    Subject=msg[0:50]
    From='blueEagle'
    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText('%s' % msg, 'plain', 'utf-8')
    #re零宽断言exp只支持定长字符串, 所以简单的匹配
    #if re.match(r'(?<=<(\W+)>).*(?=<\/\1>)', msg):
    if re.match(r'.*(<html>|<a>|<div>|<br>|<table>|<p>|<tr>|<td>).*', msg):
        message = MIMEText('%s' % msg, 'html', 'utf-8')

    #添加邮件header
    message['From'] = Header(From, 'utf-8')
    message['To'] =  Header('%s' % touser, 'utf-8')
    message['Subject'] = Header(Subject, 'utf-8')

    try:
        #创建邮件对象，smtp发送邮件
        if re.match(r'^[0-9]+$', str(ssl_port)):
            smtpObj = smtplib.SMTP_SSL(smtp_server, int(ssl_port))
        else:
            smtpObj = smtplib.SMTP(smtp_server,int(smtp_port))
        try:
            smtpObj.starttls()
        except:
            pass
        
        smtpObj.login(fromuser, pwd)
        #发送邮件，as_string显示详情
        smtpObj.sendmail(fromuser, touser, message.as_string())
        smtpObj.quit()
        return True
        
    except smtplib.SMTPException:
        return False

def send_email(dbinfo, message):
    user=dbinfo.get('name')
    member=dbinfo.get('member', '')
    if not isinstance(member, list):
        member=member.split(',')
    ssl_port=dbinfo.get('smtp_ssl_port')
    smtp_port=dbinfo.get('smtp_port')
    if not re.match(r'^[0-9]+$', str(smtp_port)):
        smtp_port=25
    email_server=dbinfo.get('email_server')
    pwd=dbinfo.get('pwd')
    return do_send_email(fromuser=user, touser=member, pwd=pwd, ssl_port=ssl_port,
                    smtp_port=smtp_port, smtp_server=email_server, message=message)

class sock_client:
    def __init__(self, ip, port):
        self.port=port
        self.ip=ip
        self.max=1024
        self.hearbeat_pkg=json.dumps('0')
        self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.u=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #recv非阻塞
        self.s.setblocking(0)
        self.s.settimeout(10)
        self.s.setsockopt(socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)
        
    def conn(self):
        try:
            self.s.connect((self.ip, self.port))
            return self.s
        except socket.error:
            return False
            
    def socket(self):
        return self.s
        
    def get_fielno(self):
        return self.s.fileno()
        
    def udp_send(self, data):
        self.u.sendto(data, (self.ip, self.port))

    def recv_data(self):
        return recv_data(self.s)

    def unpack(self, data):
        return unpack_sock_data(data)

    def write_file(self, filename, d):
        with open(filename, "ab+") as f:
            f.write(d)
            
    def get_data(self, size):
        try:
            return self.s.recv(size)
        except socket.error:
            return False
            
    def gethostname(self):
        for ip in socket.gethostbyname_ex(socket.gethostname()):
            if ip.find("127.0.0.1") != -1 and ip.find("192.168") != -1 and ip.find("localhost") != -1:
                return ip
                
    def send_data(self, data):
        try:
            self.s.sendall(data)
            time.sleep(0.1)
            return True
        except socket.error:
            return False

    def socket_check(self):
        try:
            self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.s.sendall(self.hearbeat_pkg)
            return True
        except socket.error:
            return False
        finally:
            self.s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0)
            
    def send_file(self, filename):
        while True: 
            with open(filename, "rb") as f:
                d=f.read(self.max)
                if d:
                    self.s.sendall(d)
                else:
                    break;
        time.sleep(0.5)
        log.info("send file %s success." % filename)
        return True
    
    def close(self):
        self.s.close()
        self.u.close()
        
def telnet(ip, port):
    t=telnetlib.Telnet()
    try:
        t.open(ip, port)
        return True
    except:
        return False
    finally:
        t.close()
        

class zip_file:
    def __init__(self, filepath):
        self.filepath=filepath
        self.curr_path=curr_path
        if filepath.find(os.sep) == -1:
            self.dir='.'
        else:
            self.dir=re.match(r'(.*%s).*' % os.sep, filepath).group(1)
        if os.path.isdir(filepath) == True:
            self.type='dir'
            self.zipname=filepath.split(os.sep)[-1]+".zip"
        else:
            self.type='file'
            self.zipname=filepath.split(os.sep)[-1].split(".")[0]+".zip"
        self.zpf=self.dir+os.sep+self.zipname

    def zipfile(self):
        with zipfile.ZipFile(self.zipname, 'w', zipfile.ZIP_DEFLATED) as myzip:
            if self.type=='dir':
                os.chdir(self.dir)
                for dirpath, dirnames, filenames in os.walk(self.filepath):
                    for filename in filenames:
                        myzip.write(os.path.join(dirpath, filename))
                os.chdir(self.curr_path)
            else:
                myzip.write(self.filepath)
        if os.path.exists(self.zpf) == True:
            return self.zpf
        else:
            return False

class thread_worker(threading.Thread):
    def __init__(self, work_que):
        threading.Thread.__init__(self)
        self.work_que=work_que
        self.setDaemon(True)
        self.start()
        
    def run(self):
        while 1:
            if self.work_que.empty():
                time.sleep(0.1)
                continue
            
            function, args=self.work_que.get(block=True)
            try:
                t=threading.Thread(target=function, args=(args[0], ))
                t.setDaemon(True)
                t.start()
                self.work_que.task_done()
            except:
                raise Exception('do function %s failed.' % function)

class thread_manager(object):
    def __init__(self, pool_count=1000, work_count=2):
        self.pool_que=Queue.Queue(pool_count)
        self.threads=[]
        self.init_threads(work_count)
    
    def init_threads(self, workers):
        for i in xrange(0, workers):
            self.threads.append(thread_worker(self.pool_que))
                  
    def add_worker(self, target=None, args=None):
        self.pool_que.put((target, args))
            
    def wait_all_done(self):
        for item in self.threads:
            if item.isAlive():
                item.join()
                
    
def get_list(list):
    return [ i[0] for i in list]

def getconf(cfg, attrname=None, attrvalue=None):
    if not os.path.exists(cfg):
        return False
    info={}
    tw_xml=xml(cfg)
    tw_conf=tw_xml.get_tag("config", "name", "twsited")
    for child_node in tw_conf.childNodes:
        if child_node.nodeType ==1:
            attr={}
            for att, value in zip(child_node.attributes.keys(), child_node.attributes.values()):
                attr.update({att:value.nodeValue})
            info[child_node.nodeName]=attr

    return  info
    
