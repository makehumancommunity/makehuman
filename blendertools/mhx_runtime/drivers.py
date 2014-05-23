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

#------------------------------------------------------------------------
#
#------------------------------------------------------------------------

def addDriver(rig, rna, path, bprop, props, expr="x"):
    fcu = rna.driver_add(path)
    drv = fcu.driver
    drv.type = 'SCRIPTED'
    n = 1
    addDriverVar("x", bprop, drv, rig)
    for prop,val in props:
        addDriverVar("x%d" % n, prop, drv, rig)
        expr += "+%.3f*x%d" % (val, n)
        n += 1
    drv.expression = expr

    if len(fcu.modifiers) > 0:
        fmod = fcu.modifiers[0]
        fcu.modifiers.remove(fmod)


def addDriverVar(vname, prop, drv, rig):
    var = drv.variables.new()
    var.name = vname
    var.type = 'SINGLE_PROP'
    trg = var.targets[0]
    trg.id_type = 'OBJECT'
    trg.id = rig
    trg.data_path = '["%s"]' % prop


def initRnaProperties(rig):
    try:
        rig["_RNA_UI"]
    except KeyError:
        rig["_RNA_UI"] = {}


def deleteRigProperty(rig, prop):
    try:
        del rig[prop]
    except KeyError:
        pass
    try:
        del rig["_RNA_UI"][prop]
    except KeyError:
        pass

#------------------------------------------------------------------------
#
#------------------------------------------------------------------------

def getRigMeshes(context):
    if context.object.type == 'ARMATURE':
        rig = context.object
        meshes = []
        for ob in context.scene.objects:
            if ob.parent == rig and ob.type == 'MESH':
                meshes.append(ob)
        return rig,meshes

    elif context.object.type == 'MESH':
        ob = context.object
        rig = ob.parent
        if rig and rig.type == 'ARMATURE':
            return rig,[ob]

    return None,[]


def updateScene(context):
    scn = context.scene
    scn.frame_current = scn.frame_current

