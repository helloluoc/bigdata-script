#coding:utf-8
#!/usr/bin/env python

#配置文件
from collector import *
'''
todoList = [
    getCPU,
    getDisk,
    getGetmemoryUse,
    getNetFlowInfo,
    getPingDelayAndPackageLose,
    getDbResponse,
    getQueueQuality,
    getSrvMaintainace,
    getFramework,
    getOnline,
    getQueue,
]
'''

#采集区相关
DEFAULT_GTYPE = 1

DEFAULT_QTYPE = "total"

#日志名，默认为y_event_monitor_1.0
LOG_NAME = "y_event_monitor_1.0"

#JSON字段分隔符
SEP = "\t"

#请求头部
HTTP_HEADER = {"Content-Type:application/json"}

#服务器帧数,需要在配置文件定义OLD_SHELLTYPE_FLAG
OLD_SHELLTYPE_FLAG="/home/dy1/old.shelltype"

#假定一个服务器编号
SERVERNUMBER = "652-450"

#假定一个项目代号
PROJECTID = "3721"

#假定一个服务器所属机房ID
MACHINEID = "6379"


