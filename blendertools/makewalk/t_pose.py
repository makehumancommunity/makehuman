#!/usr/bin/python
# -*- coding: utf-8 -*-

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
# Code Home Page:      https://bitbucket.org/MakeHuman/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2015
# Coding Standards:    See http://www.makehuman.org/node/165

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import *

import os
import math
from mathutils import Quaternion, Matrix
from .utils import *
from .io_json import *

#------------------------------------------------------------------
#   Define current pose as rest pose
#------------------------------------------------------------------

def applyRestPose(context, value):
    rig = context.object
    scn = context.scene
    children = []
    for ob in scn.objects:
        if ob.type != 'MESH':
            continue

        reallySelect(ob, scn)
        if ob != context.object:
            raise StandardError("Context switch did not take:\nob = %s\nc.ob = %s\nc.aob = %s" %
                (ob, context.object, context.active_object))

        if (ob.McpArmatureName == rig.name and
            ob.McpArmatureModifier != ""):
            mod = ob.modifiers[ob.McpArmatureModifier]
            ob.modifiers.remove(mod)
            ob.data.shape_keys.key_blocks[ob.McpArmatureModifier].value = value
            children.append(ob)
        else:
            for mod in ob.modifiers:
                if (mod.type == 'ARMATURE' and
                    mod.object == rig):
                    children.append(ob)
                    bpy.ops.object.modifier_apply(apply_as='SHAPE', modifier=mod.name)
                    ob.data.shape_keys.key_blocks[mod.name].value = value
                    ob.McpArmatureName = rig.name
                    ob.McpArmatureModifier = mod.name
                    break

    reallySelect(rig, scn)
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.armature_apply()
    for ob in children:
        name = ob.McpArmatureModifier
        reallySelect(ob, scn)
        mod = ob.modifiers.new(name, 'ARMATURE')
        mod.object = rig
        mod.use_vertex_groups = True
        bpy.ops.object.modifier_move_up(modifier=name)
        #setShapeKey(ob, name, value)

    reallySelect(rig, scn)
    print("Applied pose as rest pose")


def setShapeKey(ob, name, value):
    if not ob.data.shape_keys:
        return
    skey = ob.data.shape_keys.key_blocks[name]
    skey.value = value


class VIEW3D_OT_McpRestCurrentPoseButton(bpy.types.Operator):
    bl_idname = "mcp.rest_current_pose"
    bl_label = "Current Pose => Rest Pose"
    bl_description = "Change rest pose to current pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            initRig(context)
            applyRestPose(context, 1.0)
            print("Set current pose to rest pose")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

#------------------------------------------------------------------
#   Automatic T-Pose
#------------------------------------------------------------------

TPose = {
    "upper_arm.L" : (0, 0, -pi/2, 'XYZ'),
    "forearm.L" :   (0, 0, -pi/2, 'XYZ'),
    #"hand.L" :      (0, 0, -pi/2, 'XYZ'),

    "upper_arm.R" : (0, 0, pi/2, 'XYZ'),
    "forearm.R" :   (0, 0, pi/2, 'XYZ'),
    #"hand.R" :      (0, 0, pi/2, 'XYZ'),

    "thigh.L" :     (-pi/2, 0, 0, 'XYZ'),
    "shin.L" :      (-pi/2, 0, 0, 'XYZ'),
    #"foot.L" :      (None, 0, 0, 'XYZ'),
    #"toe.L" :       (pi, 0, 0, 'XYZ'),

    "thigh.R" :     (-pi/2, 0, 0, 'XYZ'),
    "shin.R" :      (-pi/2, 0, 0, 'XYZ'),
    #"foot.R" :      (None, 0, 0, 'XYZ'),
    #"toe.R" :       (pi, 0, 0, 'XYZ'),
}

def autoTPose(rig, scn):
    print("Auto T-pose", rig.name)
    selectAndSetRestPose(rig, scn)
    for pb in rig.pose.bones:
        try:
            ex,ey,ez,order = TPose[pb.McpBone]
        except KeyError:
            continue

        euler = pb.matrix.to_euler(order)
        if ex is None:
            ex = euler.x
        if ey is None:
            ey = euler.y
        if ez is None:
            ez = euler.z
        euler = Euler((ex,ey,ez), order)
        mat = euler.to_matrix().to_4x4()
        mat.col[3] = pb.matrix.col[3]

        loc = pb.bone.matrix_local
        if pb.parent:
            mat = pb.parent.matrix.inverted() * mat
            loc = pb.parent.bone.matrix_local.inverted() * loc
        mat =  loc.inverted() * mat
        euler = mat.to_euler('YZX')
        euler.y = 0
        pb.matrix_basis = euler.to_matrix().to_4x4()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='POSE')

#------------------------------------------------------------------
#   Set current pose to T-Pose
#------------------------------------------------------------------

def setTPose(rig, scn, filename=None, reload=False):
    if reload or not rig.McpTPoseDefined:
        if filename is None:
            filename = rig.McpTPoseFile
        hasFile = loadPose(rig, filename)
        if not hasFile:
            autoTPose(rig, scn)
        defineTPose(rig)
    else:
        getStoredTPose(rig)


class VIEW3D_OT_McpSetTPoseButton(bpy.types.Operator):
    bl_idname = "mcp.set_t_pose"
    bl_label = "Set T-pose"
    bl_description = "Set current pose to T-pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            rig = initRig(context)
            isdefined = rig.McpTPoseDefined
            setTPose(rig, context.scene)
            rig.McpTPoseDefined = isdefined
            print("Pose set to T-pose")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

#------------------------------------------------------------------
#   Set T-Pose
#------------------------------------------------------------------

def getStoredTPose(rig):
    for pb in rig.pose.bones:
        pb.matrix_basis = getStoredBonePose(pb)


def getStoredBonePose(pb):
        try:
            quat = Quaternion((pb.McpQuatW, pb.McpQuatX, pb.McpQuatY, pb.McpQuatZ))
        except KeyError:
            quat = Quaternion()
        return quat.to_matrix().to_4x4()


def addTPoseAtFrame0(rig, scn):
    from .source import getSourceTPoseFile

    scn.frame_current = 0
    if rig.McpTPoseDefined:
        getStoredTPose(rig)
    elif getSourceTPoseFile():
        rig.McpTPoseFile = getSourceTPoseFile()
        defineTPose(rig)
    else:
        setRestPose(rig)
        defineTPose(rig)

    for pb in rig.pose.bones:
        if pb.rotation_mode == 'QUATERNION':
            pb.keyframe_insert('rotation_quaternion', group=pb.name)
        else:
            pb.keyframe_insert('rotation_euler', group=pb.name)

#------------------------------------------------------------------
#   Define current pose as T-Pose
#------------------------------------------------------------------

def defineTPose(rig):
    for pb in rig.pose.bones:
        quat = pb.matrix_basis.to_quaternion()
        pb.McpQuatW = quat.w
        pb.McpQuatX = quat.x
        pb.McpQuatY = quat.y
        pb.McpQuatZ = quat.z
    rig.McpTPoseDefined = True


class VIEW3D_OT_McpDefineTPoseButton(bpy.types.Operator):
    bl_idname = "mcp.define_t_pose"
    bl_label = "Define T-pose"
    bl_description = "Define T-pose as current pose"
    bl_options = {'UNDO'}

    problems = ""

    def execute(self, context):
        if self.problems:
            return{'FINISHED'}
        try:
            rig = initRig(context)
            defineTPose(rig)
            print("T-pose defined as current pose")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

    def invoke(self, context, event):
        return checkObjectProblems(self, context)

    def draw(self, context):
        drawObjectProblems(self)

#------------------------------------------------------------------
#   Undefine stored T-pose
#------------------------------------------------------------------

def setRestPose(rig):
    unit = Matrix()
    for pb in rig.pose.bones:
        pb.matrix_basis = unit


class VIEW3D_OT_McpUndefineTPoseButton(bpy.types.Operator):
    bl_idname = "mcp.undefine_t_pose"
    bl_label = "Undefine T-pose"
    bl_description = "Remove definition of T-pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            rig = initRig(context)
            rig.McpTPoseDefined = False
            print("Undefined T-pose")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

#------------------------------------------------------------------
#   Load T-pose from file
#------------------------------------------------------------------

def loadPose(rig, filename):
    if filename:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        filepath = os.path.normpath(filepath)
        print("Loading %s" % filepath)
        struct = loadJson(filepath)
        rig.McpTPoseFile = filename
    else:
        return False

    setRestPose(rig)

    for name,value in struct:
        bname = getBoneName(rig, name)
        try:
            pb = rig.pose.bones[bname]
        except KeyError:
            continue
        quat = Quaternion(value)
        pb.matrix_basis = quat.to_matrix().to_4x4()

    return True


def getBoneName(rig, name):
    if rig.McpIsSourceRig:
        return name
    else:
        pb = getTrgBone(name, rig)
        if pb:
            return pb.name
        else:
            return ""


class VIEW3D_OT_McpLoadPoseButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mcp.load_pose"
    bl_label = "Load Pose"
    bl_description = "Load pose from file"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath to tpose file", maxlen=1024, default="")

    def execute(self, context):
        rig = initRig(context)
        filename = os.path.relpath(self.filepath, os.path.dirname(__file__))
        try:
            loadPose(rig, filename)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        print("Loaded pose")
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#------------------------------------------------------------------
#   Save current pose to file
#------------------------------------------------------------------

def savePose(context, filepath):
    rig = context.object
    struct = []
    for pb in rig.pose.bones:
        bmat = pb.matrix
        rmat = pb.bone.matrix_local
        if pb.parent:
            bmat = pb.parent.matrix.inverted() * bmat
            rmat = pb.parent.bone.matrix_local.inverted() * rmat
        mat = rmat.inverted() * bmat
        q = mat.to_quaternion()
        magn = math.sqrt( (q.w-1)*(q.w-1) + q.x*q.x + q.y*q.y + q.z*q.z )
        if magn > 1e-4:
            if pb.McpBone:
                struct.append((pb.McpBone, tuple(q)))

    if os.path.splitext(filepath)[1] != ".json":
        filepath = filepath + ".json"
    filepath = os.path.join(os.path.dirname(__file__), filepath)
    print("Saving %s" % filepath)
    saveJson(struct, filepath)


class VIEW3D_OT_McpSavePoseButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mcp.save_pose"
    bl_label = "Save Pose"
    bl_description = "Save current pose as .json file"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath to tpose file", maxlen=1024, default="")

    def execute(self, context):
        try:
            savePose(context, self.filepath)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        print("Saved current pose")
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#------------------------------------------------------------------
#   Utils
#------------------------------------------------------------------

def initRig(context):
    from . import target
    from . import source
    from .fkik import setRigifyFKIK

    rig = context.object
    pose = [(pb, pb.matrix_basis.copy()) for pb in rig.pose.bones]

    if rig.McpIsSourceRig:
        source.findSrcArmature(context, rig)
    else:
        target.getTargetArmature(rig, context.scene)

    for pb,mat in pose:
        pb.matrix_basis = mat

    if isRigify(rig):
        setRigifyFKIK(rig, 0.0)

    return rig

