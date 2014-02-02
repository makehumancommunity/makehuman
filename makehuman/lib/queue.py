#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

from threading import Lock, Condition
from PyQt4 import QtCore

class Queue(object):
    def __init__(self):
        self.lock = Lock()
        self.cond = Condition(self.lock)
        self.data = []
        self.live = True

    def put(self, values):
        self.cond.acquire()
        self.data.extend(values)
        self.cond.notify()
        self.cond.release()

    def get(self):
        if not self.cond.acquire(False):
            return []
        self.cond.wait()
        result = self.data
        self.data = []
        self.cond.release()
        return result

    def close(self):
        self.cond.acquire()
        self.live = False
        self.cond.notify()
        self.cond.release()

class Thread(QtCore.QThread):
    def __init__(self, queue, callback):
        QtCore.QThread.__init__(self)
        self.queue = queue
        self.callback = callback

    def __del__(self):
        self.wait()

    def run(self):
        while self.queue.live:
            for func in self.queue.get():
                self.callback(func)

class Manager(object):
    def __init__(self, callback):
        self.queue = Queue()
        self.thread = Thread(self.queue, callback)

    def start(self):
        self.thread.start()

    def stop(self):
        self.queue.close()
        self.thread.wait()

    def post(self, value):
        self.queue.put([value])
