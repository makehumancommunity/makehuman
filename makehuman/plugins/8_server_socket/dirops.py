#!/usr/bin/python3
# -*- coding: utf-8 -*-

import mh
import os

from .abstractop import AbstractOp

class SocketDirOps(AbstractOp):

    def __init__(self, sockettaskview):
        super().__init__(sockettaskview)
        self.functions["getUserDir"] = self.getUserDir
        self.functions["getSysDir"] = self.getSysDir

    def getUserDir(self,conn,jsonCall):
        jsonCall.data = os.path.abspath(mh.getPath())

    def getSysDir(self,conn,jsonCall):
        jsonCall.data = os.path.abspath(mh.getSysPath()) 


