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
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165


import os
import bpy
from bpy.props import *
from mathutils import Vector

from .drivers import *

#------------------------------------------------------------------------
#   Setup and remove drivers
#------------------------------------------------------------------------

def addShapekeyDrivers(rig, ob):
    if not ob.data.shape_keys:
        return
    skeys = ob.data.shape_keys.key_blocks
    for skey in skeys:
        if skey.name != "Basis":
            sname = getShapekeyName(skey)
            rig[sname] = 0.0
            rig["_RNA_UI"][sname] = {"min":skey.slider_min, "max":skey.slider_max}
            addDriver(rig, skey, "value", sname, [])


def getShapekeyName(skey):
    if skey.name[0:3] == "Mhs":
        return skey.name
    else:
        return "Mhs"+skey.name


def hasShapekeys(ob):
    if (ob.type != 'MESH' or
        ob.data.shape_keys is None):
        return False
    for skey in ob.data.shape_keys.key_blocks:
        if skey.name != "Basis":
            return True
    return False


class VIEW3D_OT_AddShapekeyDriverButton(bpy.types.Operator):
    bl_idname = "mhx.add_shapekey_drivers"
    bl_label = "Add Shapekey Drivers"
    bl_description = "Control shapekeys with rig properties. For file linking."
    bl_options = {'UNDO'}

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        initRnaProperties(rig)
        for ob in meshes:
            if hasShapekeys(ob):
                addShapekeyDrivers(rig, ob)
                ob.MhxShapekeyDrivers = True
        rig.MhxShapekeyDrivers = True
        return{'FINISHED'}


def removeShapekeyDrivers(ob, rig):
    if not ob.data.shape_keys:
        return
    skeys = ob.data.shape_keys.key_blocks
    for skey in skeys:
        if skey.name != "Basis":
            sname = getShapekeyName(skey)
            skey.driver_remove("value")
            deleteRigProperty(rig, sname)


class VIEW3D_OT_MhxRemoveShapekeyDriverButton(bpy.types.Operator):
    bl_idname = "mhx.remove_shapekey_drivers"
    bl_label = "Remove Shapekey Drivers"
    bl_description = "Remove ability to control shapekeys from rig property"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        for ob in meshes:
            removeShapekeyDrivers(ob, rig)
            ob.MhxShapekeyDrivers = False
        if context.object == rig:
            rig.MhxShapekeyDrivers = False
        return{'FINISHED'}

#------------------------------------------------------------------------
#   Prettifying
#------------------------------------------------------------------------

class VIEW3D_OT_MhxPrettifyButton(bpy.types.Operator):
    bl_idname = "mhx.prettify_visibility"
    bl_label = "Prettify Visibility Panel"
    bl_description = "Prettify visibility panel"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig,_meshes = getRigMeshes(context)
        for prop in rig.keys():
            if prop[0:3] == "Mhh":
                setattr(bpy.types.Object, prop, BoolProperty(default=True))
        return{'FINISHED'}

#------------------------------------------------------------------------
#   User interface
#------------------------------------------------------------------------

def resetShapekeys(rig):
    for key in rig.keys():
        if key[0:3] in ["Mhs", "Mht"]:
            rig[key] = 0.0


def getArmature(ob):
    if ob.type == 'MESH':
        return ob.parent
    elif ob.type == 'ARMATURE':
        return ob


class VIEW3D_OT_PinShapekeyKeyButton(bpy.types.Operator):
    bl_idname = "mhx.pin_shapekey"
    bl_label = ""
    bl_description = "Pin shapekey"
    bl_options = {'UNDO'}

    key = StringProperty()

    def execute(self, context):
        rig = getArmature(context.object)
        if rig:
            resetShapekeys(rig)
            try:
                rig[self.key] = rig["_RNA_UI"][self.key]["max"]
            except KeyError:
                rig[self.key] = 1.0
            updateScene(context)
        return{'FINISHED'}


class VIEW3D_OT_ResetShapekeyButton(bpy.types.Operator):
    bl_idname = "mhx.reset_shapekeys"
    bl_label = "Reset Shapekeys"
    bl_description = ""
    bl_options = {'UNDO'}

    def execute(self, context):
        rig = getArmature(context.object)
        if rig:
            resetShapekeys(rig)
            updateScene(context)
        return{'FINISHED'}
