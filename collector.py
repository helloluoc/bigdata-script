#coding:utf-8
#!/usr/bin/env python
import sys
import psutil
import subprocess
import tailer
import os
import re

#从gs.conf中获得SERVERNUMBER
def getServreNum(name="servernumber"):
    with open("/myshell/gs.conf") as f:
        str = f.readline().strip('\n')
        while str:
            splistList = str.split("=", 1)
            if splistList[0] == name:
                return (splistList[1])
                break
            else:
                continue
            str = f.readline().strip('\n')


#采集每个核心的负载
def getCPU():
    return [x for x in psutil.cpu_percent(interval=1, percpu=True)]

#获取磁盘使用率
def getDisk():
    hardDiskusPercent = psutil.disk_usage('/').used / float(psutil.disk_usage('/').total) * 100
    return round(hardDiskusPercent,2)

#获取内存使用率,realMemoryUse=[used-buffer-cache]
def getGetmemoryUse():
    changeToList = list(psutil.virtual_memory())
    realMemoryUse = changeToList[3] - changeToList[7] - changeToList[-3]
    realMemoryUsePercent = realMemoryUse * 100 / changeToList[0]
    return round(realMemoryUsePercent,2)

#获取网卡入栈流量
def getNetFlowInfo():
    key_info = psutil.net_io_counters(pernic=True).keys()  # 获取网卡名称

    get = 0
    sent = 0

    for key in key_info:
        get = get + (psutil.net_io_counters(pernic=True).get(key).bytes_recv)  # 各网卡接收的字节数
        sent = sent + psutil.net_io_counters(pernic=True).get(key).bytes_sent # 各网卡发送的字节数

    get = round(get/1024/1024, 1)
    sent = round(sent/1024/1024, 1)
    return get,sent

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
    return lostt,timelost





#判断数据库响应是否超时,超时返回1，非超时返回0
def getDbResponse():
    result = subprocess.call("ps aux|grep -v 'grep'|grep 'mysql'|grep '\-\-socket=/var/run/mysqld/mysqld.sock'|wc -l", shell=True)
    if result == 1:
        return 0
    else:
        return 1


#通道故障率
def getQueueQuality():

    httpRequestList = []
    httpErrorList = []
    wntRequestList = []
    wntErrorList = []

    SERVERNUM = getServreNum()
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
    return httpErrorPercent, wntErrorPercent








#判断服务器是否在维护
def getSrvMaintainace():
    result = os.path.exists("/home/dy1/maintain.run")
    if result:
        return 1
    else:
        return 0

#服务器帧数,需要在配置文件定义OLD_SHELLTYPE_FLAG
OLD_SHELLTYPE_FLAG="/home/dy1/old.shelltype"
def getFramework():
    SERVERNUM = getServreNum()
    #print SERVERNUM
    #文件存在且是一个普通文件
    if os.path.exists(OLD_SHELLTYPE_FLAG) and os.path.isfile(OLD_SHELLTYPE_FLAG):
        sFrameLog = "/home/dy1/gs" + SERVERNUM + "/log/frameratio.txt"
    else:
        sFrameLog = "/home/dy1/gs" + SERVERNUM + "/log/oslog/frameratio.txt"
    if os.path.exists(sFrameLog) and os.path.isfile(sFrameLog):
        frameList = tailer.tail(open(sFrameLog), 1)
        #类似   [2018-09-25 15:01:45]5656 124 569
        frameNumber = frameList[0].split("]")[1].split(" ")[0]
    return frameNumber






#服务器在线人数
def getOnline():
    SERVERNUM = getServreNum()
    sOnlineLog = "/home/dy1/gs" + SERVERNUM + "/log/frameratio.txt"
    # 文件存在且是一个普通文件
    if os.path.exists(OLD_SHELLTYPE_FLAG) and os.path.isfile(OLD_SHELLTYPE_FLAG):
        sOnlineLog = "/home/dy1/gs" + SERVERNUM + "/log/online.txt"
    if os.path.exists(sOnlineLog) and os.path.isfile(sOnlineLog):
        onlineList = tailer.tail(open(sOnlineLog), 1)
        #类似  [2018-09-25 15:01:45]5656 124 569 2 6 5
        onlineList[0].split("]")[1].split(" ")[0]




#服务器排队人数
def getQueue():
    SERVERNUM = getServreNum()
    sQuenueLog = "/home/dy1/gs" + SERVERNUM + "/log/oslog/queuing.txt"
    # 文件存在且是一个普通文件
    if os.path.exists(OLD_SHELLTYPE_FLAG) and os.path.isfile(OLD_SHELLTYPE_FLAG):
        sQuenueLog = "/home/dy1/gs" + SERVERNUM + "/log/queuing.txt"
    #日志不统一，暂时不写
    pass






if __name__ == '__main__':
    print getPingDelayAndPackageLose()


