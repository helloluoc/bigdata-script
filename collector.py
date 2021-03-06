#coding:utf-8
#!/usr/bin/env python
import sys
import psutil
import subprocess
import tailer
import os
import re
import json
from collections import OrderedDict

from funcpublic import *


"""
功能：采集cpu负载
入参：None
返回：单核、总体的cpu负载（保留两位小数)
"""
def getCPU():
    # 获取采集时间
    collectorTime = collectTime()
    # 采集磁盘使用率事件名称
    METRIC = "cpu.busy"
    senderInfoList = []
    i = 0
    #单个核心负载
    for x in psutil.cpu_percent(interval=1, percpu=True):
        resultInfo = str(x)
        i += 1
        cpuNumber = "cpu" + str(i)
        httpSenderInfo = addString(collectorTime, resultInfo, METRIC,qType=cpuNumber)
        senderInfoList.append(httpSenderInfo)
    #获取总的CPU负载
    total_cpu = psutil.cpu_times().user + psutil.cpu_times().idle
    user_cpu = psutil.cpu_times().user
    cpu_syl = user_cpu / total_cpu * 100
    resultInfo = str(round(cpu_syl, 2))
    # 拼接发送字符串
    senderInfoList.append(addString(collectorTime, resultInfo, METRIC,qType="total"))
    sendToLog(collectorTime,senderInfoList)
    #print senderInfoList
    return senderInfoList

"""
功能：获取使用率
入参：None
返回：单个、总体磁盘使用率
"""
def getDisk():
    #获取采集时间
    collectorTime = collectTime()
    #采集磁盘使用率事件名称
    METRIC = "df.bytes.used.percent"
    senderInfoList = []

    for i in psutil.disk_partitions():
        resultInfo = str(round(psutil.disk_usage(i.mountpoint).percent))
        httpSenderInfo = addString(collectorTime, resultInfo, METRIC, qType=i.device)
        senderInfoList.append(httpSenderInfo)
    # 磁盘利用率
    resultInfo = str(round(psutil.disk_usage('/').used / float(psutil.disk_usage('/').total) * 100,2))
    #拼接发送字符串
    senderInfoList.append(addString(collectorTime, resultInfo, METRIC,qType="total"))
    sendToLog(collectorTime, senderInfoList)
    return senderInfoList

"""
功能：获取内存使用率
参数：None
返回：内存使用率
"""
def getGetmemoryUse():
    collectorTime = collectTime()
    METRIC = "men.menused.percent"
    senderInfoList = []

    resultInfo = str(round(psutil.virtual_memory().percent,2))
    print resultInfo

    #拼接发送字符串
    senderInfoList.append(addString(collectorTime, resultInfo, METRIC,qType="total"))
    sendToLog(collectorTime, senderInfoList)
    return senderInfoList


"""
功能：获取单个、总体网卡出栈流量数据
入参：None
返回：单个、总体网卡的出栈流量数据
"""
def getNetOutInfo():
    collectorTime = collectTime()
    METRIC = "net.if.in.bytes"
    senderInfoList = []

    for k,v in psutil.net_io_counters(pernic=True,nowrap=True).items():
        networkInfo = str(v).split("(")[1].split(")")[0]
        netWorkName = k
        sendByte = float(networkInfo.split(",")[0].split("=")[1])
        resultInfo = str(round(sendByte/1024/1024, 1))
        senderInfoList.append(addString(collectorTime,resultInfo,METRIC,qType=netWorkName))

    key_info = psutil.net_io_counters(pernic=True).keys()  # 获取网卡名称
    get = 0
    for key in key_info:
        get = get + (psutil.net_io_counters(pernic=True).get(key).bytes_recv)  # 各网卡接收的字节数
    resultInfo = str(round(get/1024/1024, 1))
    # 拼接发送字符串
    senderInfoList.append(addString(collectorTime, resultInfo, METRIC,qType="total"))
    sendToLog(collectorTime, senderInfoList)
    return senderInfoList


"""
功能：获取网卡入栈流量数据
入参：None
返回：单个、总体网卡的入栈流量数据
"""
def getNetInfo():
    collectorTime = collectTime()
    METRIC = "net.if.out.bytes"
    senderInfoList = []

    for k,v in psutil.net_io_counters(pernic=True,nowrap=True).items():
        networkInfo = str(v).split("(")[1].split(")")[0]
        networkName = k
        inByte = float(networkInfo.split(",")[1].split("=")[1])
        resultInfo = str(round(inByte / 1024 / 1024, 1))
        senderInfoList.append(addString(collectorTime,resultInfo,METRIC,qType=networkName))

    key_info = psutil.net_io_counters(pernic=True).keys()  # 获取网卡名称
    sent = 0
    for key in key_info:
        sent = sent + psutil.net_io_counters(pernic=True).get(key).bytes_sent  # 各网卡发送的字节数
    resultInfo = str(round(sent / 1024 / 1024, 1))
    # 拼接发送字符串
    senderInfoList.append(addString(collectorTime,resultInfo,METRIC,qType="total"))
    sendToLog(collectorTime, senderInfoList)
    return senderInfoList


"""
功能：采集服务器ping其他机房的丢包率
入参：None
返回：ping其他机房的丢包率
"""
def getPingPackageLose():
    collectorTime = collectTime()
    METRIC = "ping.value.loss"
    target = "lospkg"
    idroom = "iroomid"
    idmachine = "machineid"
    resultNtype = str(getNtype())
    #需要ping的IP地址列表
    pingAbleList = getPingList()
    senderInfoList = []

    for i in pingAbleList:
        resultInfo = str(getPingInfo(i, target))
        irromId = getId(idroom,i)
        imachineid = getId(idmachine,i)
        resultSon = addString(collectorTime, resultInfo, METRIC, iRromId=irromId,iMachineId=imachineid,nType=resultNtype)
        senderInfoList.append(resultSon)
    sendToLog(collectorTime, senderInfoList)
    return senderInfoList


"""
功能：采集服务器ping其他机房的延迟
入参：None
返回：ping其他机房的延迟
"""
def getPingDelay():
    collectorTime = collectTime()
    METRIC = "ping.value"
    target = "timeout"
    idroom = "iroomid"
    idmachine = "machineid"
    resultNtype = str(getNtype())
    #需要ping的IP地址列表
    pingAbleList = getPingList()
    senderInfoList = []

    for i in pingAbleList:
        resultInfo = str(getPingInfo(i,target))
        irromid = getId(idroom,i)
        imachineid = getId(idmachine,i)
        resultSon = addString(collectorTime, resultInfo, METRIC, iRromId=irromid,iMachineId=imachineid,nType=resultNtype)
        senderInfoList.append(resultSon)
    sendToLog(collectorTime, senderInfoList)
    return senderInfoList


"""
功能：判断数据库响应是否超时，超时返回1，非超时返回0
入参：None
返回：超时返回1，非超时返回0
"""
def getDbResponse():
    collectorTime = collectTime()
    METRIC = "svr.db.answer"
    senderInfoList = []

    result = subprocess.call("ps aux|grep -v 'grep'|grep 'mysql'|grep '\-\-socket=/var/run/mysqld/mysqld.sock'|wc -l", shell=True)
    if result == 1:
        resultInfo = str(0)
    else:
        resultInfo = str(1)
    # 拼接发送字符串
    senderInfoList.append(addString(collectorTime, resultInfo, METRIC))
    sendToLog(collectorTime, senderInfoList)
    return senderInfoList


"""
功能：读取日志，获得http/wnt的通道故障率
入参：None
返回：http、wnt的通道故障率
"""
def getQueueQuality():
    collectorTime = collectTime()
    METRIC = "svr.fault"
    senderInfoList = []
    i = 2

    httpRequestList = []
    httpErrorList = []
    wntRequestList = []
    wntErrorList = []
    httpErrorPercent = 0
    wntErrorPercent = 0
    SERVERNUM = SERVERNUMBER
    # 文件存在且是一个普通文件
    if OLD_SHELLTYPE_FLAG:
        sQualityLog = "/myshell/pubpathquality.txt"
        #sQualityLog = "/home/dy1/gs" + SERVERNUM + "/log/pubpathquality.txt"
    else:
        sQualityLog = "/home/dy1/gs" + SERVERNUM + "/log/oslog/pubpathquality.txt"
    if os.path.isfile(sQualityLog):
    # 获取最近一次记录的通道信息
        info = tailer.tail(open(sQualityLog), 1)
        print info
        lastLogTime = info[0].split(']')[0].split("[")[1]
        while True:
            findLogTime = tailer.tail(open(sQualityLog),i)[0].split(']')[0].split("[")[1]
            if findLogTime == lastLogTime:
                i = i + 1
            else:
                #i表示最后面的i条都是最后一次记录的日志
                i = i -1
                break
        #最近一次日志记录的所有记录
        checkLog = tailer.tail(open(sQualityLog), i)
        for i in checkLog:
            #将http和wnt通道故障率分别统计
            type = i.split("]")[1].split(" ")[0]
            if type == "http":
                httpRequestList.append(float(i.split("]")[1].split(" ")[2]))
                httpErrorList.append(float(i.split("]")[1].split(" ")[3]))
                resultInfo1 = str(round(sum(httpErrorList) / sum(httpRequestList), 2))
                senderInfoList.append(addString(collectorTime, resultInfo1, METRIC, qType="http"))
            else:
                wntRequestList.append(float(i.split("]")[1].split(" ")[2]))
                wntErrorList.append(float(i.split("]")[1].split(" ")[3]))
                resultInfo2 = str(round(sum(wntErrorList) / sum(wntRequestList), 2))
                senderInfoList.append(addString(collectorTime, resultInfo2, METRIC, qType="wnt"))
    sendToLog(collectorTime, senderInfoList)
    return senderInfoList


"""
功能：判断服务器是否在维护
入参：None
返回：维护返回1，非维护返回0
"""
def getSrvMaintainace():
    collectorTime = collectTime()
    METRIC = "svr.maintainace"
    senderInfoList = []

    result = os.path.exists("/home/dy1/maintain.run")
    if result:
        resultInfo = str(1)
    else:
        resultInfo = str(0)
    senderInfoList.append(addString(collectorTime,resultInfo,METRIC))
    sendToLog(collectorTime, senderInfoList)
    return senderInfoList


"""
功能：获取服务器帧数
入参：None
返回：服务器帧数
"""
def getFramework():
    collectorTime = collectTime()
    METRIC = "svr.framecnt"
    frameNumber = ""
    senderInfoList = []

    #根据标志位设置文件路径
    sFrameLog = "/myshell/frameratio.txt"
    #文件存在且是一个普通文件
    if os.path.isfile(sFrameLog):
        frameList = tailer.tail(open(sFrameLog), 1)
        #类似   [2018-09-25 15:01:45]5656 124 569
        frameNumber = frameList[0].split("]")[1].split(" ")[0]
    resultInfo = str(frameNumber)

    # 拼接发送字符串
    senderInfoList.append(addString(collectorTime, resultInfo, METRIC))
    sendToLog(collectorTime, senderInfoList)
    return senderInfoList


"""
功能：获取服务器在线人数
入参：None
返回：服务器在线人数
"""
def getOnline():
    collectorTime = collectTime()
    METRIC = "svr.online"
    resultInfo = ""
    senderInfoList = []

    SERVERNUM = SERVERNUMBER
    #sOnlineLog = "/home/dy1/gs" + SERVERNUM + "/log/frameratio.txt"
    # 根据标志位设置文件路径
    if OLD_SHELLTYPE_FLAG:
        sOnlineLog = "/myshell/online.txt"
        #sOnlineLog = "/home/dy1/gs" + SERVERNUM + "/log/online.txt"
    #文件存在且是一个普通文件
    if os.path.isfile(sOnlineLog):
        onlineList = tailer.tail(open(sOnlineLog), 1)
        #类似  [2018-09-25 15:01:45]5656 124 569 2 6 5
        resultInfo = str(onlineList[0].split("]")[1].split(" ")[0])
    # 拼接发送字符串
    senderInfoList.append(addString(collectorTime, resultInfo, METRIC))
    return senderInfoList


"""
功能：返回服务器排队人数
入参：None
返回：服务器排队人数（日志文件不统一，暂不实现）
"""
def getQueue():
    collectorTime = collectTime()
    METRIC = "svr.queue"
    SERVERNUM = SERVERNUMBER

    sQuenueLog = "/home/dy1/gs" + SERVERNUM + "/log/oslog/queuing.txt"
    # 文件存在且是一个普通文件
    if os.path.exists(OLD_SHELLTYPE_FLAG) and os.path.isfile(OLD_SHELLTYPE_FLAG):
        sQuenueLog = "/home/dy1/gs" + SERVERNUM + "/log/queuing.txt"
    #日志不统一，暂时不写
    pass






if __name__ == '__main__':
    while True:
        number = str(input("请输入数字执行对应程序："))
        if number == "1":
            shit = getDisk()
            print shit
        elif number == "2":
            shit = getGetmemoryUse()
            print shit
        elif number == "3":
            shit = getNetOutInfo()
            print shit
        elif number == "4":
            shit = getNetInfo()
            print shit
        elif number == "5":
            shit = getDbResponse()
            print shit
        elif number == "6":
            shit = getQueueQuality()
            print shit
        elif number == "7":
            shit = getFramework()
            print shit
        elif number == "8":
            shit = getOnline()
            print shit
        elif number == "9":
            shit = getCPU()
            print shit
        elif number == "22":
            shit = getPingPackageLose()
            print shit
        elif number == "33":
            shit = getPingDelay()
            print shit
        else:
            break

    print tailer.tail(open("/myshell/pubpathquality.txt"), 1)

