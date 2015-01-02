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

import bpy
from bpy.props import *
from .drivers import *


#------------------------------------------------------------------------
#    Setup: Add and remove groups
#------------------------------------------------------------------------

class VIEW3D_OT_MhxAddGroupsButton(bpy.types.Operator):
    bl_idname = "mhx.add_groups"
    bl_label = "Add Groups"
    bl_description = "Add meshes to rig group. For file linking."
    bl_options = {'UNDO'}

    def execute(self, context):
        rig,meshes = getRigMeshes(context)
        if rig:
            addGroup(rig, rig.name)
            for ob in meshes:
                addGroup(ob, rig.name)
        return{'FINISHED'}


def addGroup(ob, gname):
    group = None
    for grp in ob.groups:
        if grp.name = gname:
            group = grp
            break
    if not group:
        group = ob.groups.new(gname)
