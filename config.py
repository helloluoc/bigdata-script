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
    "10.32.13.77":{
        "machineid":"93856",
        "roomid":"20",
    },

    "10.94.116.5":{
        "machineid": "3593",
        "roomid": "20",
    },

    "10.94.116.9":{
        "machineid": "3585",
        "roomid": "20",
    },

    "10.94.116.12":{
        "machineid": "3584",
        "roomid": "20",
    },

    "10.97.204.15":{
        "machineid": "3169",
        "roomid": "18",
    },

    "10.97.204.15":{
        "machineid": "3169",
        "roomid": "18",
    },

    "10.82.193.68":{
        "machineid": "6872",
        "roomid": "18",
    },

    "10.109.137.50":{
        "machineid": "6899",
        "roomid": "36",
    },

    "10.109.137.51":{
        "machineid": "6924",
        "roomid": "36",
    },

    "10.109.64.199":{
        "machineid": "6902",
        "roomid": "36",
    },

    "10.109.64.112":{
        "machineid": "7117",
        "roomid": "36",
    },

    "10.8.64.112":{
        "machineid": "7117",
        "roomid": "36",
    },

    "10.80.64.204":{
        "machineid": "5102",
        "roomid": "35",
    },

    "10.80.64.204":{
        "machineid": "5102",
        "roomid": "35",
    },

    "10.80.64.215":{
        "machineid": "7326",
        "roomid": "35",
    },

    "10.83.204.14":{
        "machineid": "2895",
        "roomid": "19",
    },

    "10.85.132.85": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.85.198.73": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.82.64.60": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.82.64.58": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.92.194.164": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.82.198.60": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.84.132.27": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.84.132.70": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.82.140.89": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.82.2.152": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.82.2.153": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.82.2.170": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.17.64.163": {
        "machineid": "2895",
        "roomid": "19",
    },

    "10.32.64.56": {
        "machineid": "2895",
        "roomid": "19",
    },

    "192.168.112.79": {
        "machineid": "2895",
        "roomid": "19",
    },

    "192.168.112.81": {
        "machineid": "2895",
        "roomid": "19",
    },

    "192.1668.112.94": {
        "machineid": "2895",
        "roomid": "19",
    },
}



#各机房对应的服务器IP
DELEGATE_DICT = {
    #中山电信
    "20":["10.94.116.5","10.94.116.9"],
    #佛山电信
    "18":["10.97.204.15","10.82.193.67"],
    #武汉金银湖
    "36":["10.109.137.50","10.109.137.51","10.109.64..199","10.109.64.112"],
    #成都二枢纽
    "35":["10.80.64.204","10.80.64.215"],
    #惠州电信
    "19":["10.83.204.14","10.85.132.85","10.85.198.73"],
    #顺德电信
    "21":["10.82.198.60","10.84.132.27","10.84.132.70"],
    #沈阳联通
    "22":["10.82.140.89"],
    #济南联通
    "23":["10.82.2.144","10.82.2.152","10.82.2.153","10.82.2.170"],
    #广州内部机房
    "27":["10.17.65.147","10.17.64.163","10.32.64.56"],
    #成都内部机房
    "28":["192.168.112.79","192.168.112.81","192.168.112.94"]
}
