# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; eimcp.r version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See mcp.
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2014
# Coding Standards:    See http://www.makehuman.org/node/165

import bpy
from bpy.props import EnumProperty, StringProperty

from . import utils
from .utils import *

#
#   Global variables
#

_actions = []

#
#   Select or delete action
#   Delete button really deletes action. Handle with care.
#
#   listAllActions(context):
#   findActionNumber(name):
#   class VIEW3D_OT_McpUpdateActionListButton(bpy.types.Operator):
#

def listAllActions(context):
    global _actions

    scn = context.scene
    try:
        doFilter = scn.McpFilterActions
        filter = context.object.name
        if len(filter) > 4:
            filter = filter[0:4]
            flen = 4
        else:
            flen = len(filter)
    except:
        doFilter = False

    _actions = []
    for act in bpy.data.actions:
        name = act.name
        if (not doFilter) or (name[0:flen] == filter):
            _actions.append((name, name, name))
    bpy.types.Scene.McpActions = EnumProperty(
        items = _actions,
        name = "Actions")
    bpy.types.Scene.McpFirstAction = EnumProperty(
        items = _actions,
        name = "First action")
    bpy.types.Scene.McpSecondAction = EnumProperty(
        items = _actions,
        name = "Second action")
    print("Actions declared")


def findActionNumber(name):
    global _actions
    for n,enum in enumerate(_actions):
        (name1, name2, name3) = enum
        if name == name1:
            return n
    raise MocapError("Unrecognized action %s" % name)


class VIEW3D_OT_McpUpdateActionListButton(bpy.types.Operator):
    bl_idname = "mcp.update_action_list"
    bl_label = "Update Action List"
    bl_description = "Update the action list"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object

    def execute(self, context):
        listAllActions(context)
        return{'FINISHED'}

#
#   deleteAction(context):
#   class VIEW3D_OT_McpDeleteButton(bpy.types.Operator):
#

def deleteAction(context):
    global _actions
    listAllActions(context)
    scn = context.scene
    try:
        act = bpy.data.actions[scn.McpActions]
    except KeyError:
        act = None
    if not act:
        raise MocapError("Did not find action %s" % scn.McpActions)
    print('Delete action', act)
    act.use_fake_user = False
    if act.users == 0:
        print("Deleting", act)
        n = findActionNumber(act.name)
        _actions.pop(n)
        bpy.data.actions.remove(act)
        print('Action', act, 'deleted')
        listAllActions(context)
        #del act
    else:
        raise MocapError("Cannot delete. Action %s has %d users." % (act.name, act.users))


class VIEW3D_OT_McpDeleteButton(bpy.types.Operator):
    bl_idname = "mcp.delete"
    bl_label = "Delete Action"
    bl_description = "Delete the action selected in the action list"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            deleteAction(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200, height=20)

    def draw(self, context):
        self.layout.label("Really delete action?")

#
#   deleteHash():
#   class VIEW3D_OT_McpDeleteHashButton(bpy.types.Operator):
#

def deleteHash():
    for act in bpy.data.actions:
        if act.name[0] == '#':
            deleteAction(act)
    return


class VIEW3D_OT_McpDeleteHashButton(bpy.types.Operator):
    bl_idname = "mcp.delete_hash"
    bl_label = "Delete Temporary Actions"
    bl_description = (
        "Delete all actions whose name start with '#'. " +
        "Such actions are created temporarily by MakeWalk. " +
        "They should be deleted automatically but may be left over."
    )
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            deleteHash()
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

#
#   setCurrentAction(context, prop):
#   class VIEW3D_OT_McpSetCurrentActionButton(bpy.types.Operator):
#

def setCurrentAction(context, prop):
    listAllActions(context)
    name = getattr(context.scene, prop)
    act = getAction(name)
    context.object.animation_data.action = act
    print("Action set to %s" % act)
    return


def getAction(name):
    try:
        return bpy.data.actions[name]
    except KeyError:
        pass
    raise MocapError("Did not find action %s" % name)


class VIEW3D_OT_McpSetCurrentActionButton(bpy.types.Operator):
    bl_idname = "mcp.set_current_action"
    bl_label = "Set Current Action"
    bl_description = "Set the action selected in the action list as the current action"
    bl_options = {'UNDO'}
    prop = StringProperty()

    def execute(self, context):
        try:
            setCurrentAction(context, self.prop)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

