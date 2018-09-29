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

#扩展字段需加mroom gytpe gtype的事件列表
METRIC_LIST1 = ["cpu.busy","men.memused.percent","df.bytes.used.percent","net.if.in.bytes","net.if.out.bytes"]

#扩展字段需加mroom gtype的事件列表
METRIC_LIST2 = ["svr.online","svr.maintainace","svr.queue","svr.framecnt","svr.fault","svr.db.answer"]

#扩展字段需加mroom rroom rserver line gytpe ntype的事件列表
METRIC_LIST3 = ["ping.value","ping.packet.loss"]

#各IP地址的相关信息
pinglist = {
    "10.94.116.5":{
        "machineid":"93856",
        "roomid":"20",
    },
}



#各机房对应的服务器IP
DELEGATE_DICT = {
    "20":["10.94.116.5","10.94.116.9"],
    "18":["10.97.204.15","10.82.193.67"],
    "27":["98999","4789484"],
}