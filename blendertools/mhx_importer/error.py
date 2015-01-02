# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2015
# Coding Standards: See http://www.makehuman.org/node/165

"""
Abstract

"""

DEBUG = False
import bpy
from bpy.props import *

class ErrorOperator(bpy.types.Operator):
    bl_idname = "mhx.error"
    bl_label = "Error when loading MHX file"

    def execute(self, context):
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        global theErrorLines, theMessage
        maxlen = 0
        for line in theErrorLines:
            if len(line) > maxlen:
                maxlen = len(line)
        width = 20+5*maxlen
        height = 20+5*len(theErrorLines)
        #self.report({'INFO'}, theMessage)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=width, height=height)

    def draw(self, context):
        global theErrorLines, theMessage
        for line in theErrorLines:
            self.layout.label(line)


def MyError(message):
    global theMessage, theErrorLines, theErrorStatus
    theMessage = message
    theErrorLines = message.split('\n')
    theErrorStatus = True
    print(theMessage)
    bpy.ops.mhx.error('INVOKE_DEFAULT')
    raise MhxError(theMessage)


class MhxError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class SuccessOperator(bpy.types.Operator):
    bl_idname = "mhx.success"
    bl_label = "MHX file successfully loaded:"
    message = StringProperty()

    def execute(self, context):
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.label(self.message + theMessage)

