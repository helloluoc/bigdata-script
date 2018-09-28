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

from config import *
from funcpublic import *



#采集每个核心的负载
def getCPU():
    print "负载采集执行完毕"
    return [x for x in psutil.cpu_percent(interval=1, percpu=True)]

#获取磁盘使用率
def getDisk():
    #获取采集时间
    collectorTime = time()
    #采集磁盘使用率事件名称
    METRIC = "df.bytes.used.percent"

    # 磁盘利用率
    hardDiskusPercent = psutil.disk_usage('/').used / float(psutil.disk_usage('/').total) * 100
    hardDiskusPercent = round(hardDiskusPercent,2)
    resultInfo = str(hardDiskusPercent)

    #拼接body的字符串
    bodyInfo = collectorTime + SEP + SERVERNUMBER + SEP + LOG_NAME + SEP + PROJECTID + SEP + METRIC + SEP + resultInfo + SEP + \
                "mroom:" + MACHINEID + ",gtype:1,qtype:total"
    #采用有序字典，防止转换成JSON顺序错乱
    httpString = OrderedDict()
    httpString["headers"] = {}
    httpString["body"] = bodyInfo
    httpSenderInfo = json.dumps(httpString)
    print "磁盘使用率执行完毕"
    return httpSenderInfo


#获取内存使用率,realMemoryUse=[used-buffer-cache]
def getGetmemoryUse():
    collectorTime = time()
    METRIC = "men.menused.percent"

    #内存使用率
    changeToList = list(psutil.virtual_memory())
    realMemoryUse = changeToList[3] - changeToList[7] - changeToList[-3]
    realMemoryUsePercent = realMemoryUse * 100 / changeToList[0]
    resultInfo = str(round(realMemoryUsePercent,2))

    # 拼接body的字符串
    bodyInfo = collectorTime + SEP + SERVERNUMBER + SEP + LOG_NAME + SEP + PROJECTID + SEP + METRIC + SEP + resultInfo + SEP + \
               "mroom:" + MACHINEID + ",gtype:1,qtype:total"
    # 采用有序字典，防止转换成JSON顺序错乱
    httpString = OrderedDict()
    httpString["headers"] = {}
    httpString["body"] = bodyInfo
    httpSenderInfo = json.dumps(httpString)
    print "内存使用率执行完毕"
    return httpSenderInfo


#获取网卡入栈流量
def getNetFlowInfo():
    collectorTime = time()
    METRIC = "net.if.in.bytes"

    key_info = psutil.net_io_counters(pernic=True).keys()  # 获取网卡名称
    get = 0
    for key in key_info:
        get = get + (psutil.net_io_counters(pernic=True).get(key).bytes_recv)  # 各网卡接收的字节数
    resultInfo = str(round(get/1024/1024, 1))

    # 拼接body的字符串
    bodyInfo = collectorTime + SEP + SERVERNUMBER + SEP + LOG_NAME + SEP + PROJECTID + SEP + METRIC + SEP + resultInfo + SEP + \
               "mroom:" + MACHINEID + ",gtype:1,qtype:total"
    # 采用有序字典，防止转换成JSON顺序错乱
    httpString = OrderedDict()
    httpString["headers"] = {}
    httpString["body"] = bodyInfo
    httpSenderInfo = json.dumps(httpString)
    print "网卡入栈流量采集执行完毕"
    return httpSenderInfo



# 获取网卡出栈流量
def getNetSendInfo():
    collectorTime = time()
    METRIC = "net.if.out.bytes"

    key_info = psutil.net_io_counters(pernic=True).keys()  # 获取网卡名称
    sent = 0
    for key in key_info:
        sent = sent + psutil.net_io_counters(pernic=True).get(key).bytes_sent  # 各网卡发送的字节数
    resultInfo = str(round(sent / 1024 / 1024, 1))

    # 拼接body的字符串
    bodyInfo = collectorTime + SEP + SERVERNUMBER + SEP + LOG_NAME + SEP + PROJECTID + SEP + METRIC + SEP + resultInfo + SEP + \
               "mroom:" + MACHINEID + ",gtype:1,qtype:total"
    # 采用有序字典，防止转换成JSON顺序错乱
    httpString = OrderedDict()
    httpString["headers"] = {}
    httpString["body"] = bodyInfo
    httpSenderInfo = json.dumps(httpString)
    print "网卡出栈执行完毕"
    return httpSenderInfo




#采集服务器ping其他机房的延迟和丢包率,ip地址只能通过root进程发送进来？？？
def getPingDelayAndPackageLose():
    list1 = ["www.google.com",]
    child = subprocess.Popen(["ping", "-c", "5", list1[0]], stdout=subprocess.PIPE)
    child.wait()
    pinginfo = str(child.communicate())

    #获取丢包率
    los = r"\d*(?:%)"
    lostt = re.search(los, pinginfo)
    lostt = lostt.group()
    lostt = float(lostt.split("%", 1)[0]) / 100
    lostt = round(lostt, 2)

    #获取ping其他IP地址的延迟时间
    avgtime = r"\d*\.\d*\/\d*\.\d*\/\d*\.\d*\/\d*\.\d*"
    timelost = re.search(avgtime, pinginfo)
    timelost = str(timelost.group())
    timelost = round(float(timelost.split("/", 3)[1]), 2)
    print "延迟和丢包率执行完毕"
    return lostt,timelost





#判断数据库响应是否超时,超时返回1，非超时返回0
def getDbResponse():
    collectorTime = time()
    METRIC = "svr.db.answer"

    result = subprocess.call("ps aux|grep -v 'grep'|grep 'mysql'|grep '\-\-socket=/var/run/mysqld/mysqld.sock'|wc -l", shell=True)
    if result == 1:
        resultInfo = str(0)
    else:
        resultInfo = str(1)

    # 拼接body的字符串
    bodyInfo = collectorTime + SEP + SERVERNUMBER + SEP + LOG_NAME + SEP + PROJECTID + SEP + METRIC + SEP + resultInfo + SEP + \
            "mroom:" + MACHINEID + ",gtype:1"
    # 采用有序字典，防止转换成JSON顺序错乱
    httpString = OrderedDict()
    httpString["headers"] = {}
    httpString["body"] = bodyInfo
    httpSenderInfo = json.dumps(httpString)
    print "数据库响应执行完毕"
    return httpSenderInfo


#通道故障率
def getQueueQuality():
    collectorTime = time()
    METRIC = "svr.fault"

    httpRequestList = []
    httpErrorList = []
    wntRequestList = []
    wntErrorList = []
    httpErrorPercent = 0
    wntErrorPercent = 0
    SERVERNUM = SERVERNUMBER
    # 文件存在且是一个普通文件
    if os.path.exists(OLD_SHELLTYPE_FLAG) and os.path.isfile(OLD_SHELLTYPE_FLAG):
        sQualityLog = "/home/dy1/gs" + SERVERNUM + "/log/pubpathpublic.txt"
    else:
        sQualityLog = "/home/dy1/gs" + SERVERNUM + "/log/oslog/pubpathpublic.txt"
    if os.path.exists(sQualityLog) and os.path.isfile(sQualityLog):
    # 获取最近一次记录的通道信息
        lastLogTime = tailer.tail(open(sQualityLog), 1)[0].split(']')[0].split("[")[1]
        while True:
            i = 2
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
                httpRequestList.append(i.split("]")[1].split(" ")[2])
                httpErrorList.append(i.split("]")[1].split(" ")[3])
                httpErrorPercent = round(sum(httpErrorList) / sum(httpRequestList), 2)
            else:
                wntRequestList.append(i.split("]")[1].split(" ")[2])
                wntErrorList.append(i.split("]")[1].split(" ")[3])
                wntErrorPercent = round(sum(wntErrorList) / sum(wntRequestList), 2)
    else:
        return "文件不存在"
    #需求文档未标明两种通道是否分开发送
    resultInfo1 = str(httpErrorPercent)
    resultInfo2 = str(wntErrorPercent)


    # 拼接body的字符串,http通道故障率
    bodyInfo1 = collectorTime + SEP + SERVERNUMBER + SEP + LOG_NAME + SEP + PROJECTID + SEP + METRIC + SEP + resultInfo1 + SEP + \
               "mroom:" + MACHINEID + ",gtype:1"
    httpString1 = OrderedDict()
    httpString1["headers"] = {}
    httpString1["body"] = bodyInfo1
    httpSenderInfo1 = json.dumps(httpString1)

    # 拼接body的字符串,wnt通道故障率
    bodyInfo2 = collectorTime + SEP + SERVERNUMBER + SEP + LOG_NAME + SEP + PROJECTID + SEP + METRIC + SEP + resultInfo2 + SEP + \
                "mroom:" + MACHINEID + ",gtype:1"
    httpString2 = OrderedDict()
    httpString2["headers"] = {}
    httpString2["body"] = bodyInfo2
    httpSenderInfo2 = json.dumps(httpString2)

    queueList = [httpSenderInfo1, httpSenderInfo2]
    queueList = json.dumps(queueList)
    print "通道故障率执行完毕"
    return queueList


#判断服务器是否在维护
def getSrvMaintainace():
    collectorTime = time()
    METRIC = "svr.maintainace"

    result = os.path.exists("/home/dy1/maintain.run")
    if result:
        resultInfo = str(1)
    else:
        resultInfo = str(0)
    # 拼接body的字符串
    bodyInfo = collectorTime + SEP + SERVERNUMBER + SEP + LOG_NAME + SEP + PROJECTID + SEP + METRIC + SEP + resultInfo + SEP + \
            "mroom:" + MACHINEID + ",gtype:1"
    # 采用有序字典，防止转换成JSON顺序错乱
    httpString = OrderedDict()
    httpString["headers"] = {}
    httpString["body"] = bodyInfo
    httpSenderInfo = json.dumps(httpString)
    print "服务器维护执行完毕"
    return httpSenderInfo





def getFramework():
    collectorTime = time()
    METRIC = "svr.framecnt"
    SERVERNUM = SERVERNUMBER

    #根据标志位设置文件路径
    if os.path.exists(OLD_SHELLTYPE_FLAG) and os.path.isfile(OLD_SHELLTYPE_FLAG):
        sFrameLog = "/home/dy1/gs" + SERVERNUM + "/log/frameratio.txt"
    else:
        sFrameLog = "/home/dy1/gs" + SERVERNUM + "/log/oslog/frameratio.txt"
    #文件存在且是一个普通文件
    if os.path.exists(sFrameLog) and os.path.isfile(sFrameLog):
        frameList = tailer.tail(open(sFrameLog), 1)
        #类似   [2018-09-25 15:01:45]5656 124 569
        frameNumber = frameList[0].split("]")[1].split(" ")[0]
    else:
        return "file of directory not found"
    resultInfo = str(frameNumber)

    # 拼接body的字符串
    bodyInfo = collectorTime + SEP + SERVERNUMBER + SEP + LOG_NAME + SEP + PROJECTID + SEP + METRIC + SEP + resultInfo + SEP + \
               "mroom:" + MACHINEID + ",gtype:1"
    # 采用有序字典，防止转换成JSON顺序错乱
    httpString = OrderedDict()
    httpString["headers"] = {}
    httpString["body"] = bodyInfo
    httpSenderInfo = json.dumps(httpString)
    print "帧数执行完毕"
    return httpSenderInfo


#服务器在线人数
def getOnline():
    collectorTime = time()
    METRIC = "svr.online"

    SERVERNUM = SERVERNUMBER
    sOnlineLog = "/home/dy1/gs" + SERVERNUM + "/log/frameratio.txt"
    # 根据标志位设置文件路径
    if os.path.exists(OLD_SHELLTYPE_FLAG) and os.path.isfile(OLD_SHELLTYPE_FLAG):
        sOnlineLog = "/home/dy1/gs" + SERVERNUM + "/log/online.txt"
    #文件存在且是一个普通文件
    if os.path.exists(sOnlineLog) and os.path.isfile(sOnlineLog):
        onlineList = tailer.tail(open(sOnlineLog), 1)
        #类似  [2018-09-25 15:01:45]5656 124 569 2 6 5
        resultInfo = str(onlineList[0].split("]")[1].split(" ")[0])
    else:
        return "file of directory not found"

        # 拼接body的字符串
    bodyInfo = collectorTime + SEP + SERVERNUMBER + SEP + LOG_NAME + SEP + PROJECTID + SEP + METRIC + SEP + resultInfo + SEP + \
               "mroom:" + MACHINEID + ",gtype:1"
    # 采用有序字典，防止转换成JSON顺序错乱
    httpString = OrderedDict()
    httpString["headers"] = {}
    httpString["body"] = bodyInfo
    httpSenderInfo = json.dumps(httpString)
    print "在线人数执行完毕"
    return httpSenderInfo






#服务器排队人数
def getQueue():
    collectorTime = time()
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
            shit = getNetFlowInfo()
            print shit
        elif number == "4":
            shit = getNetSendInfo()
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
        else:
            break


