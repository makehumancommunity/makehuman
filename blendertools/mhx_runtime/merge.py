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
from .utils import *

#------------------------------------------------------------------------
#
#------------------------------------------------------------------------

def deleteHiddenVerts(body, clo):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    grpname = getDeleteName(clo)
    try:
        vgrp = body.vertex_groups[grpname]
    except KeyError:
        print("Did not find vertex group %s" % grpname)
        return

    for v in body.data.vertices:
        for g in v.groups:
            if g.group == vgrp.index:
                v.select = True

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')


def mergeObjects(context):
    scn = context.scene
    clothes = []
    body = None
    for ob in context.selected_objects:
        if ob.type == 'MESH':
            if isBody(ob):
                body = ob
            else:
                clothes.append(ob)

    matnums = []
    if body:
        scn.objects.active = body
        name = getRigName(body)

        names = []
        for clo in clothes:
            if getRigName(clo) == name:
                names.append(getProxyName(clo))

        delMods = []
        for mod in body.modifiers:
            if mod.type == 'MASK':
                mod.show_viewport = False
                vgname = getVGProxyName(mod.vertex_group)
                if vgname in names:
                    delMods.append(mod)

        for mod in delMods:
            body.modifiers.remove(mod)

        for clo in clothes:
            deleteHiddenVerts(body, clo)
            bpy.ops.object.join()
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=1e-3)
            bpy.ops.object.mode_set(mode='OBJECT')
            mn = len(body.data.materials)-1
            matnums.append(mn)

        for mod in body.modifiers:
            if mod.type == 'MASK':
                mod.show_viewport = True

    return matnums


def changeMaterial(body, mn):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    uvfaces = {}
    n = 0
    uvlayer = body.data.uv_layers[0]
    for f in body.data.polygons:
        nverts = len(f.vertices)
        if f.material_index == mn:
            f.select = True
            uvs = [tuple(uvlayer.data[n+k].uv) for k in range(nverts)]
            uvfaces[f.index] = uvs
        n += nverts

    body.data.uv_textures.active_index = 0
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.uv_texture_remove()
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')

    uvlayer = body.data.uv_layers[0]
    n = 0
    for f in body.data.polygons:
        nverts = len(f.vertices)
        if f.select:
            f.material_index = 0
            uvs = uvfaces[f.index]
            for k in range(nverts):
                uvlayer.data[n+k].uv = uvs[k]
        n += nverts

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')


class VIEW3D_OT_MergeObjectsButton(bpy.types.Operator):
    bl_idname = "mhx.merge_objects"
    bl_label = "Merge Selected To Active"
    bl_description = "Merge selected objects to active seamlessly"
    bl_options = {'UNDO'}

    def execute(self, context):
        matnums = mergeObjects(context)
        body = context.object
        for mn in matnums:
            changeMaterial(body, mn)
        return{'FINISHED'}

