#coding:utf-8
#!/usr/bin/env python

import Queue, threading, requests
import time


#from config import *
from collector import *

class Worker(threading.Thread):
    def __init__(self, workqueue, resultqueue, **kwargs):
        threading.Thread.__init__(self, **kwargs)
        self.workqueue = workqueue  # 存放任务的队列,任务一般都是函数
        self.resultqueue = resultqueue  # 存放结果的队列

    def run(self):
        while True:
            try:
                # 从任务队列中取出一个任务，block设置为False表示如果队列空了，就会抛出异常
                callable, args, kwargs = self.workqueue.get(block=False)
                res = callable(*args, **kwargs)
                self.resultqueue.put(res)  # 将任务的结果存放到结果队列中
            except Queue.Empty:  # 抛出空队列异常
                break


class WorkerManger(object):
    def __init__(self, num=10):  # 默认这个池子里有10个线程
        self.workqueue = Queue.Queue()  # 任务队列
        self.resultqueue = Queue.Queue()  # 存放任务结果的队列
        self.workers = []  # 所有的线程都存放在这个列表中
        self._recruitthreads(num)  # 创建一系列线程的函数

    def _recruitthreads(self, num):
        for i in xrange(num):
            worker = Worker(self.workqueue, self.resultqueue)
            self.workers.append(worker)

    def start(self):
        for work in self.workers:
            work.start()

    def wait_for_complete(self):
        while len(self.workers):
            worker = self.workers.pop()
            worker.join()
            if worker.isAlive() and not self.workqueue.empty():
                self.workers.append(worker)

    def add_job(self, callable, *args, **kwargs):
        self.workqueue.put((callable, args, kwargs))

    def get_result(self, *args, **kwargs):
        return self.resultqueue.get(*args, **kwargs)

    def add_result(self, result):
        self.resultqueue.put(result)



def send(number):
    print "shit"
    for i in number:
        print "dkdf"
        r = requests.post("http://httpbin.org/get", headers={}, data=i)
        with open("hello.txt","w+") as f:
            if i:
                f.write(i + "\n")
    print r.status_code




todoList = [
    getCPU,
    getDisk,
    getGetmemoryUse,
    getNetOutInfo,
    getNetInfo,
    getPingPackageLose,
    getPingDelay,
    getDbResponse,
    getQueueQuality,
    getSrvMaintainace,
    getFramework,
    getOnline,
]

if __name__ == '__main__':

    num = 0
    #global SERVERNUMBER
    SERVERNUMBER = getGsConfInfo()
    PROJECTID = getGsConfInfo("projectid")
    #print SERVERNUMBER
    #print PROJECTID

    httpheader = HTTP_HEADER
    w = WorkerManger(10)
    while True:
        num += 1
        httpheader = HTTP_HEADER

        #w = WorkerManger(10)
        for i in range(len(todoList)):
            w.add_job(todoList[i])
        w.start()
        w.wait_for_complete()
        while not w.resultqueue.empty():
            h = w.resultqueue.get()
            for i in h:
                print i
                requests.post("http://httpbin.org/get", headers={}, data=i)
        time.sleep(1)
        print "--"
        print num

