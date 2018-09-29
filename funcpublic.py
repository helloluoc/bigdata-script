#coding:utf-8
#!/usr/bin/env python

import os
import socket
import subprocess
from datetime import datetime

from config import *

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

"""
功能：区分内网还是公网
入参：None
返回：私网（含内网）返回1，公网返回2
"""
def getNtype(ipAddress=None):
    if ipAddress == None:
        ipAddress = str(get_host_ip())
    if ipAddress[0:3] == "10." or ipAddress[0:8] == "192.168.":
        return 1
    else:
        return 2

"""
功能：获取扩展字段中的gtype字段（目前只有服务器）
入参：None
返回：维度标记（1-服务器 2-机房 3-线路 4-运营商）
"""
def getGtype():
    return DEFAULT_GTYPE


"""
功能：获取IP的roomid/machineid
入参：IP地址,roomid/machineid
返回：该IP地址的roomid/mahcineid
"""
def getId(idclass,ipAddress=None):
    if ipAddress == None:
        ipAddress = str(get_host_ip())
    info = pinglist.get(ipAddress)
    if idclass == "roomid":
        roomid = info.get("roomid")
        return roomid
    else:
        machineid = info.get("machineid")
        return machineid


"""
功能：获取ping之后返回的信息
入参：需要ping的IP地址，丢包率or延迟
返回：根据参数决定返回丢包率还是延迟
"""
def getPingInfo(ip,target):
    child = subprocess.Popen(["ping", "-c", "5", ip], stdout=subprocess.PIPE)
    child.wait()
    pinginfo = str(child.communicate())

    if target == "lospkg":
        los = r"\d*(?:%)"
        lostt = re.search(los, pinginfo)
        lostt = lostt.group()
        lostt = float(lostt.split("%", 1)[0]) / 100
        lostt = round(lostt, 2)
        return lostt
    else:
        avgtime = r"\d*\.\d*\/\d*\.\d*\/\d*\.\d*\/\d*\.\d*"
        timelost = re.search(avgtime, pinginfo)
        timelost = str(timelost.group())
        timelost = round(float(timelost.split("/", 3)[1]), 2)
        return avgtime

"""
功能：获取可ping的IP地址列表（内外网间不ping，广州成都内网不ping）
入参：None
返回：可ping的IP列表
"""
def getPingList():
    pingAbleList = []
    pingIp = []
    #roomId = "20"
    myIpAddress = get_host_ip()
    myNeteType = getNtype()
    roomId = getId("roomid")
    #获得自己在外其他服务器的代表ip列表
    for k,v in DELEGATE_DICT.items():
        if k != roomId:
            pingIp += v
    #根据规则对ip列表进行筛选
    for i in pingIp:
        targetType = getNtype(i)
        if myNeteType != targetType:
            #内外网之间不互ping
            continue
        elif myNeteType == 1:
            if myIpAddress[0:4] != i[0:4]:
                #广州和成都的内网不互ping
                continue
        pingAbleList.append(i)
    return pingAbleList


"""
功能：完成字符拼接
入参：
返回：拼接好的字符串
"""
def splicStr(collectorTime,resultInfo,METRIC,iRromId=None,iMachineId=None,line=None,qType=None):
    expandFile = ""
    expandFile1 = ""
    if METRIC in METRIC_LIST1:
        resultGtype = getGtype()
        expandFile1 = ",gtype:" + str(resultGtype) + ",qtype:total"
        expandFile = "mroom:" + MACHINEID + expandFile1
    elif METRIC in METRIC_LIST2:
        resultGtype = getGtype()
        expandFile1 = ",gtype:" + str(resultGtype)
        expandFile = "mroom:" + MACHINEID + expandFile1
    elif METRIC in METRIC_LIST3:
        resultGtype = getGtype()
        resultNtype = getNtype()
        expandFile1 = ",gtype:" + str(resultGtype) + ",ntype:" + resultNtype
        expandFile = "mroom:" + MACHINEID + ",rroom:" + iRromId + ",reserver:" + iMachineId + ",line:" + expandFile1


    expandList = [collectorTime, SERVERNUMBER, LOG_NAME, PROJECTID, METRIC, resultInfo, expandFile]
    addSeq = SEP.join(expandList)
    httpString = OrderedDict()
    httpString["headers"] = {}
    httpString["body"] = addSeq
    httpSenderInfo = json.dumps(httpString)
    return httpSenderInfo


"""
功能：完成字符拼接（完整版）
入参：
返回：拼接好的字符串
"""
def addString(collectorTime,resultInfo,METRIC,iRromId=None,iMachineId=None,line=None,nType=None,qType=None):
    expandFile = "mroom:" + MACHINEID
    resultGtype = getGtype()

    if iRromId:
        expandFile = expandFile + ",rroom:" + iRromId
    if iMachineId:
        expandFile = expandFile + ",reserver:" + iMachineId + ",line:"
    expandFile = expandFile + ",gtype:" + str(resultGtype)
    if nType:
        expandFile = expandFile + "," + nType
    if qType:
        expandFile = expandFile + ",qtype:" + qType

    expandList = [collectorTime, SERVERNUMBER, LOG_NAME, PROJECTID, METRIC, resultInfo, expandFile]
    addSeq = SEP.join(expandList)
    httpString = OrderedDict()
    httpString["headers"] = {}
    httpString["body"] = addSeq
    httpSenderInfo = json.dumps(httpString)
    return httpSenderInfo


























