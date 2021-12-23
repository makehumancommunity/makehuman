#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sys import exc_info
import traceback
import sys

from core import G

class AbstractOp():

    def __init__(self, sockettaskview):
        self.parent = sockettaskview
        self.functions = dict()
        self.human = sockettaskview.human
        self.api = G.app.mhapi

    def hasOp(self,function):
        return function in self.functions.keys()

    def evaluateOp(self,conn,jsoncall):

        try:
            function = jsoncall.getFunction()
    
            if function in self.functions.keys():
                self.functions[function](conn,jsoncall)
            else:
                self.parent.addMessage("Did not understand '" + function + "'")
                jsoncall.setError('"' + function + '" is not valid command')
        except:
            print("Exception in JSON:")
            print('-'*60)
            traceback.print_exc(file=sys.stdout)
            print('-'*60)
            ex = exc_info()
            jsoncall.setError("runtime exception:  " + str(ex[1]))
            print(ex)

        return jsoncall


