#!/usr/bin/python
#coding=utf-8
import hashlib,struct,base64,sys,os,comm_lib
#需要安装 PyCrypto
from Crypto.Cipher import AES

#AES加密为新增加密方式,以前为简单的密码串做base64加盐加密
def aes_prpcrypt(pwd):
    #16为
    key="selfpwdprpcrypta"
    #为16的倍数
    length=16
    #不满足条件的用'%'补齐右边,解密时候删去
    pwd+= str('%') * (length - (len(pwd) % length))
    obj = AES.new(key, AES.MODE_CBC, key)
    return base64.b16encode(obj.encrypt(pwd))

def aes_decrypt(pwd):
    #16为
    key="selfpwdprpcrypta"
    obj = AES.new(key, AES.MODE_CBC, key)
    return obj.decrypt(base64.b16decode(pwd))

def pwd_solt_base64(pwd):
    en_pwd=base64.encodestring(pwd).strip("\n").rstrip("=")
    md5=comm_lib.getmd5(pwd)
    #取3的余数，base64规则1：==；2=；3""
    remainder=len(pwd)%3
    #真实密码中间加salt值
    en_pwd=en_pwd[:len(en_pwd)/2] + str(remainder) + en_pwd[len(en_pwd)/2:] + md5 + str(remainder)
    return en_pwd

def de_pwd(e_p,type=None):
    if not type:
        #新增aes加密
	e_p=aes_decrypt(e_p)
    e_p=e_p.rstrip('%')
    remainder=int(e_p[-1:])
    if remainder == 1:
        str="=="
    elif remainder == 2:
        str="="
    else:
        str=""
    #过滤掉加密的salt，还原真实密码加密串
    en_p=e_p[:len(e_p)-33]+str
    return base64.decodestring(en_p[:(len(en_p)-len(str)-1)/2]+en_p[(len(en_p)-len(str)-1)/2 + 1:])

def en_pwd(pwd):
    return aes_prpcrypt(pwd_solt_base64(pwd))
    
def decode_pwd(pwd):
    return de_pwd(aes_decrypt(pwd), type=True)
    
if __name__ == "__main__":
    try:
        type=sys.argv[1]
        value=sys.argv[2]
    except:
        type=''
        value=''
    if type is False and value is False:
        sys.exit()
    elif type == 'encode':
        #密码先做base加盐值加密,在对这个密文做aes加密,然后转成16进制
        print aes_prpcrypt(pwd_solt_base64(value))
    elif type == 'decode':
        #加密的反步骤
        print de_pwd(aes_decrypt(value), type=True)
