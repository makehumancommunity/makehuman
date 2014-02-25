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
Make some aspects of the targets mathematically perfect.
"""


import bpy
import os
import json
from mathutils import Vector

from .error import MHError, handleMHError
from .utils import round, setObjectMode


#----------------------------------------------------------
#   Eyes
#----------------------------------------------------------

def average(vnums, verts):
    sum = Vector((0,0,0))
    for vn in vnums:
        sum += verts[vn].co
    return (1.0/len(vnums)) * sum


def translate(offset, vnums, verts):
    for vn in vnums:
        verts[vn].co += offset


def rotate(angle, axis, r_center, vnums, verts):
    mat = Matrix.Rotation(angle, 3, axis)
    for vn in vnums:
        v = verts[vn]
        v.co = r_center + mat * (v.co - r_center)


def perfectEye(prefix, struct, verts):
    v_center = struct[prefix+"Center"]
    v_ring = struct[prefix+"Ring"]
    v_target = struct[prefix+"Target"]
    v_uplid = struct[prefix+"UpLid"]
    v_lolid = struct[prefix+"LoLid"]
    v_pupil = struct[prefix+"Pupil"]
    v_eye = struct[prefix+"Eye"]

    r_center = average(v_ring, verts)
    offset = r_center-average(v_center, verts)
    translate(offset, v_center, verts)

    offset = r_center-average(v_target, verts)
    offset[1] = offset[2] = 0
    translate(offset, v_target, verts)

    offset = r_center-average(v_uplid, verts)
    offset[1] = offset[2] = 0
    translate(offset, v_uplid, verts)

    offset = r_center-average(v_lolid, verts)
    offset[1] = offset[2] = 0
    translate(offset, v_lolid, verts)

    arrow = average(v_pupil, verts) - r_center
    arrow.normalize()
    forward = Vector((0,-1,0))
    cos = arrow.dot(forward)
    angle = math.acos(cos)
    if abs(angle) > 1e-3:
        axis = arrow.cross(forward)
        axis.normalize()
        rotate(angle, axis, r_center, v_eye, verts)


def perfectEyes(context):
    folder = os.path.dirname(__file__)
    filepath = os.path.join(folder, "data", "eye.json")
    with open(filepath, "rU") as fp:
        struct = json.load(fp)

    ob = context.object
    if ob.data.shape_keys:
        verts = ob.data.shape_keys.key_blocks[-1].data
    else:
        verts = ob.data.vertices

    perfectEye("Left", struct, verts)
    perfectEye("Right", struct, verts)


class VIEW3D_OT_LoadMhpButton(bpy.types.Operator):
    bl_idname = "mh.perfect_eyes"
    bl_label = "Perfect Eyes"
    bl_description = "Perfect location of eyes and eye helpers"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        setObjectMode(context)
        try:
            perfectEyes(context)
        except MHError:
            handleMHError(context)
        return {'FINISHED'}
