#coding:utf-8
#!/usr/bin/env python

import Queue, threading, random


class Worker(threading.Thread):
    """
    定义一个能够处理任务的线程类，属于自定义线程类，自定义线程类就需要定义run()函数
    """

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
    """
    定义一个线程池的类
    """

    def __init__(self, num=10):  # 默认这个池子里有10个线程
        self.workqueue = Queue.Queue()  # 任务队列，
        self.resultqueue = Queue.Queue()  # 存放任务结果的队列
        self.workers = []  # 所有的线程都存放在这个列表中
        self._recruitthreads(num)  # 创建一系列线程的函数

    def _recruitthreads(self, num):
        """
        创建线程
        """
        for i in xrange(num):
            worker = Worker(self.workqueue, self.resultqueue)
            self.workers.append(worker)

    def start(self):
        """
        启动线程池中每个线程
        """
        for work in self.workers:
            work.start()

    def wait_for_complete(self):
        """
        等待至任务队列中所有任务完成
        """
        while len(self.workers):
            worker = self.workers.pop()
            worker.join()
            if worker.isAlive() and not self.workqueue.empty():
                self.workers.append(worker)

    def add_job(self, callable, *args, **kwargs):
        """
        往任务队列中添加任务
        """
        self.workqueue.put((callable, args, kwargs))

    def get_result(self, *args, **kwargs):
        """
        获取结果队列
        """
        return self.resultqueue.get(*args, **kwargs)

    def add_result(self, result):
        self.resultqueue.put(result)


def hello():
    print "hello"
    return random.random()

def send(number):
    with open("hello.txt", "a") as f:
        f.write(number + "\n")


if __name__ == '__main__':
    w = WorkerManger(3)
    for i in range(5):
        w.add_job(hello)
    w.start()
    while True:
        #打算在这里添加发送的函数
        if not w.resultqueue.empty():
            w.add_job(send, str(w.get_result()))
            print "1"
        else:
            break

    w.wait_for_complete()

