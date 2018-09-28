#coding:utf-8
#!/usr/bin/env python

import os
import socket
from datetime import datetime


'''
公共函数
'''
#从gs.conf中获得相关信息，默认为SERVERNUM
#服务器所属项目编号PRODUCTID
#
def getServreNum(name="SERVERNUM"):
    with open("/myshell/gs.conf") as f:
        gsConfInfo = f.readline().strip('\n')
        while True:
            splistList = gsConfInfo.split("=", 1)
            if splistList[0] == name:
                return (splistList[1])
                break
            else:
                continue
            gsConfInfo = f.readline().strip('\n')

#获取采集数据时间
def time():
    dt = datetime.now()
    collectoTime = dt.strftime('%Y-%m-%d %H:%M:%S')
    return collectoTime

#获取服务器IP
#通过UDP协议来实现，生成一个UDP包，把所在服务器的IP放到UDP协议的头中，然后从该UDP包中获取到IP地址
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('10.0.0.1',8080))
        ip= s.getsockname()[0]
    finally:
        s.close()
    return ip

'''
#判断日志文件是否存在，不存在则创建
def makeLog():
    if os.path.isfile("/myshell/sendlog.txt"):
        print "文件已存在"
        pass
    else:
        try:
            f = open("/myshell/sendlog.txt", "w")
            f.close()
            print "文件已创建"
        except:
            return "创建文件权限不足"
    if os.path.isfile("/myshell/errorlog.txt"):
        print "文件已存在"
        pass
    else:
        try:
            f = open("/myshell/errorlog.txt", "w")
            f.close()
            print "文件已创建"
        except:
            print "dfd"
            return "创建文件权限不足"
'''

#获取服务器所属机房名称
def getMachneinfo():
    #引入getmachineinfo.py文件调用里面的函数即可
    pass