#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

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

Convert targets

"""

import bpy
import os
import math
from mathutils import Vector
from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper

from . import mh
from . import mt
from .utils import round
from .proxy import CProxy

theSettings = mt.CSettings("alpha7")

Epsilon = 1e-4

#----------------------------------------------------------
#
#----------------------------------------------------------


class VIEW3D_OT_SetTargetDirButton(bpy.types.Operator):
    bl_idname = "mh.set_target_dir"
    bl_label = "Set Target Directory"
    bl_description = ""
    bl_options = {'UNDO'}

    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for target",
        maxlen= 1024, default= "")

    def execute(self, context):
        context.scene.MhTargetDir = os.path.dirname(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_SetSourceTargetButton(bpy.types.Operator):
    bl_idname = "mh.set_source_target"
    bl_label = "Set Source Target File"
    bl_description = ""
    bl_options = {'UNDO'}

    filename_ext = ".target"
    filter_glob = StringProperty(default="*.target", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for target",
        maxlen= 1024, default= "")

    def execute(self, context):
        context.scene.MhSourceTarget = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_SetSourceClothingButton(bpy.types.Operator):
    bl_idname = "mh.set_source_mhclo"
    bl_label = "Set Source Clothing File"
    bl_options = {'UNDO'}

    filename_ext = ".mhclo"
    filter_glob = StringProperty(default="*.mhclo;*.proxy", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for clothing",
        maxlen= 1024, default= "")

    def execute(self, context):
        context.scene.MhSourceMhclo = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_SetSourceVGroupButton(bpy.types.Operator):
    bl_idname = "mh.set_source_vgroup"
    bl_label = "Set Source Vertex Group File"
    bl_options = {'UNDO'}

    filename_ext = ".vgrp"
    filter_glob = StringProperty(default="*.vgrp;*.rig", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for vertex groups",
        maxlen= 1024, default= "")

    def execute(self, context):
        context.scene.MhSourceVGroup = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


#----------------------------------------------------------
#
#----------------------------------------------------------

def readConverter(scn):
    print("Reading %s" % mt.baseObjFile)
    baseVerts = readBaseObj(mt.baseObjFile)

    print("Reading %s" % mt.convertMhcloFile)
    proxy = CProxy()
    proxy.read(mt.convertMhcloFile)

    return proxy, baseVerts


def readBaseObj(filepath):
    fp = open(filepath, "rU")
    verts = {}
    vn = 0
    for line in fp:
        words = line.split()
        if len(words) == 4 and words[0] == 'v':
            x,y,z = float(words[1]), float(words[2]), float(words[3])
            verts[vn] = CVertex(x,y,z)
            vn += 1
    fp.close()
    return verts


def copyVerts(verts):
    newverts = {}
    for n,v in verts.items():
        newverts[n] = v.copy()
    return newverts


def zeroVerts(nVerts):
    zero = CVertex(0,0,0)
    verts = {}
    for n in range(nVerts):
        verts[n] = zero
    return verts


def subVerts(verts1, verts2):
    for n in range(len(verts1)):
        verts1[n].sub(verts2[n])

#----------------------------------------------------------
#   Convert target
#----------------------------------------------------------

class VIEW3D_OT_ConvertTargetButton(bpy.types.Operator):
    bl_idname = "mh.convert_target"
    bl_label = "Convert Target File"
    bl_description = ""
    bl_options = {'UNDO'}

    def execute(self, context):
        convertTargetFile(context)
        return {'FINISHED'}


def convertTargetFile(context):
    scn = context.scene
    proxy,baseVerts = readConverter(scn)

    srcVerts = zeroVerts(theSettings.nTotalVerts)
    diffVerts = copyVerts(baseVerts)
    proxy.update(srcVerts, diffVerts)

    srcFile = scn.MhSourceTarget
    srcVerts = zeroVerts(theSettings.nTotalVerts)
    readTarget(srcFile, srcVerts)

    trgFile = os.path.join(scn.MhTargetDir, os.path.basename(srcFile))
    trgVerts = copyVerts(baseVerts)
    proxy.update(srcVerts, trgVerts)
    subVerts(trgVerts, diffVerts)
    saveTarget(trgVerts, trgFile)


def readTarget(filepath, verts):
    fp = open(filepath, "rU")
    for line in fp:
        words = line.split()
        if len(words) == 4:
            x,y,z = float(words[1]), float(words[2]), float(words[3])
            verts[int(words[0])] = CVertex(x,y,z)
    fp.close()
    return verts


def saveTarget(trgVerts, filepath):
    fp = open(filepath, "w", encoding="utf-8", newline="\n")
    for vn,trgVert in trgVerts.items():
        if trgVert.length() > Epsilon:
            co = trgVert.co
            fp.write("%d %s %s %s\n" % (vn, round(co[0]), round(co[1]), round(co[2])))
    fp.close()
    print("Target %s saved" % (filepath))

#----------------------------------------------------------
#   Convert vertex groups
#----------------------------------------------------------

class VIEW3D_OT_ConvertVGroupButton(bpy.types.Operator):
    bl_idname = "mh.convert_vgroup"
    bl_label = "Convert VGroup File"
    bl_description = ""
    bl_options = {'UNDO'}

    def execute(self, context):
        convertVGroupFile(context)
        return {'FINISHED'}


def convertVGroupFile(context):
    scn = context.scene
    proxy,baseVerts = readConverter(scn)
    srcFile = scn.MhSourceVGroup
    trgFile = os.path.join(scn.MhTargetDir, os.path.basename(srcFile))
    srcGroups,before,after = readVGroups(srcFile)
    trgGroups = []
    for name,srcGroup in srcGroups:
        trgGroup = proxy.updateWeights(srcGroup)
        trgGroups.append((name, trgGroup))
        print(name)
    saveVGroups(trgGroups, before, after, trgFile)


def readVGroups(filepath):
    vgroups = []
    lines = before = []
    after = []
    fp = open(filepath, "rU")
    for line in fp:
        words = line.split()
        if len(words) > 0 and words[0]== '#':
            if len(words) == 3 and words[1] == "weights":
                vgrp = {}
                for n in range(theSettings.nTotalVerts):
                    vgrp[n] = 0
                vgroups.append((words[2], vgrp))
                lines = after
            else:
                lines.append(line)
        elif len(words) == 2:
            vgrp[int(words[0])] = float(words[1])
        else:
            lines.append(line)
    fp.close()
    return vgroups,before,after


def saveVGroups(vgroups, before, after, filepath):
    fp = open(filepath, "w", encoding="utf-8", newline="\n")
    for line in before:
        fp.write(line)
    for (name, vgroup) in vgroups:
        vlist = list(vgroup.items())
        vlist.sort()
        fp.write("# weights %s\n" % name)
        for (vn,w) in vlist:
            if abs(w) > 1e-4:
                fp.write("  %d %s\n" % (vn, round(w)))
        fp.write("\n")
    for line in after:
        fp.write(line)
    fp.close()
    print("VGroup file %s saved" % (filepath))

#----------------------------------------------------------
#   Convert clothes
#----------------------------------------------------------

class VIEW3D_OT_ConvertMhcloButton(bpy.types.Operator):
    bl_idname = "mh.convert_mhclo"
    bl_label = "Convert Mhclo File"
    bl_description = ""
    bl_options = {'UNDO'}

    def execute(self, context):
        convertMhcloFile(context)
        return {'FINISHED'}


#----------------------------------------------------------
#   class CVertex:
#----------------------------------------------------------

class CVertex:

    def __init__(self, x, y, z):
        self.co = Vector((x,y,z))

    def __repr__(self):
        return ("<CVertex %s %s %s>" % (round(self.co[0]), round(self.co[1]), round(self.co[2])))

    def copy(self):
        return CVertex(self.co[0], self.co[1], self.co[2])

    def sub(self, v):
        self.co -= v.co

    def length(self):
        return self.co.length

#----------------------------------------------------------
#   Init
#----------------------------------------------------------

def init():
    bpy.types.Scene.MhTargetDir = StringProperty(
        description = "Directory where converted targets are saved",
        default = os.path.expanduser("~"))

    bpy.types.Scene.MhSourceTarget = StringProperty(
        description = "Target file to be converted")

    bpy.types.Scene.MhSourceMhclo = StringProperty(
        description = "Mhclo file to be converted")

    bpy.types.Scene.MhSourceVGroup = StringProperty(
        description = "Vgrp file to be converted")

    return
