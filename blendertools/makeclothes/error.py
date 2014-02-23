#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

"""

import bpy

theMessage = "No message"
theErrorLines = []

class ErrorOperator(bpy.types.Operator):
    bl_idname = "mhclo.error"
    bl_label = "Error using MakeHuman tool"

    def execute(self, context):
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        global theMessage, theErrorLines
        theErrorLines = theMessage.split('\n')
        maxlen = len(self.bl_label)
        for line in theErrorLines:
            if len(line) > maxlen:
                maxlen = len(line)
        width = 20+5*maxlen
        height = 20+5*len(theErrorLines)
        #self.report({'INFO'}, theMessage)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=width, height=height)

    def draw(self, context):
        global theErrorLines
        for line in theErrorLines:
            self.layout.label(line)


class MHError(Exception):

    def __init__(self, value):
        global theMessage
        theMessage = value
        print("ERROR:", theMessage)
        bpy.ops.mhclo.error('INVOKE_DEFAULT')

    def __str__(self):
        return repr(self.value)


def handleMHError(context):
    global theMessage

#
#   Warnings
#

_Warnings = []

def initWarnings():
    global _Warnings
    _Warnings = []

def handleWarnings():
    global _Warnings
    if _Warnings:
        string = "Operation succeeded but there were warnings:\n"
        for warning in _Warnings:
            string += "\n" + warning
        raise MHError(string)

def addWarning(string):
    global _Warnings
    _Warnings.append(string)
