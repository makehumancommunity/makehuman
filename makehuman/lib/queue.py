#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
