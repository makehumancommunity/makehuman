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
# Script copyright (C) MakeHuman Team 2001-2014
# Coding Standards:    See http://www.makehuman.org/node/165

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import *

import os
import math
from mathutils import Quaternion, Matrix
from .utils import *
from .io_json import *


def setTPoseAsRestPose(context):
    rig = context.object
    setTPose(rig, context.scene)
    if not rig.McpRestTPose:
        applyRestPose(context, 1.0)
        invertQuats(rig)
        rig.McpRestTPose = True


def setDefaultPoseAsRestPose(context):
    rig = context.object
    clearTPose(rig)
    if rig.McpRestTPose:
        applyRestPose(context, 0.0)
        invertQuats(rig)
        rig.McpRestTPose = False


def invertQuats(rig):
    for pb in rig.pose.bones:
        quat = Quaternion((pb.McpQuatW, pb.McpQuatX, pb.McpQuatY, pb.McpQuatZ))
        pb.McpQuatW, pb.McpQuatX, pb.McpQuatY, pb.McpQuatZ = quat.inverted()


def applyRestPose(context, value):
    rig = context.object
    scn = context.scene
    children = []
    for ob in scn.objects:
        if ob.type != 'MESH':
            continue

        scn.objects.active = ob
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

    scn.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.armature_apply()
    for ob in children:
        name = ob.McpArmatureModifier
        scn.objects.active = ob
        mod = ob.modifiers.new(name, 'ARMATURE')
        mod.object = rig
        mod.use_vertex_groups = True
        bpy.ops.object.modifier_move_up(modifier=name)
        #setShapeKey(ob, name, value)

    scn.objects.active = rig
    print("Created T-pose")


def setShapeKey(ob, name, value):
    if not ob.data.shape_keys:
        return
    skey = ob.data.shape_keys.key_blocks[name]
    skey.value = value


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

        quat = pb.matrix_basis.to_quaternion()
        setBoneTPose(pb, quat)

        rig.McpTPoseLoaded = True
        rig.McpRestTPose = False


def setTPose(rig, scn, filename=None, reload=True):
    if reload or not rig.McpTPoseLoaded:
        if isMakeHumanRig(rig):
            filename = "target_rigs/makehuman_tpose.json"
        elif filename is None:
            filename = rig.McpTPoseFile
        hasFile = loadTPose(rig, filename)
        if not hasFile:
            autoTPose(rig, scn)
    if rig.McpRestTPose:
        setRestPose(rig)
    else:
        setStoredPose(rig)


def clearTPose(rig):
    if not rig.McpTPoseLoaded:
        loadTPose(rig, rig.McpTPoseFile)
    if rig.McpRestTPose:
        setStoredPose(rig)
    else:
        setRestPose(rig)


def getStoredBonePose(pb):
    try:
        quat = Quaternion((pb.McpQuatW, pb.McpQuatX, pb.McpQuatY, pb.McpQuatZ))
    except KeyError:
        quat = Quaternion()
    return quat.to_matrix().to_4x4()


def setStoredPose(rig):
    for pb in rig.pose.bones:
        pb.matrix_basis = getStoredBonePose(pb)


def addTPoseAtFrame0(rig, scn):
    from .source import getSourceTPoseFile

    scn.frame_current = 0
    if rig.McpTPoseLoaded:
        setTPose(rig, scn)
    elif getSourceTPoseFile():
        rig.McpTPoseFile = getSourceTPoseFile()
        setTPose(rig, scn)
    else:
        setRestPose(rig)
    for pb in rig.pose.bones:
        if pb.rotation_mode == 'QUATERNION':
            pb.keyframe_insert('rotation_quaternion', group=pb.name)
        else:
            pb.keyframe_insert('rotation_euler', group=pb.name)


def getCurrentPose(rig):
    return [(pb, pb.matrix_basis.copy()) for pb in rig.pose.bones]


def setCurrentPose(pose):
    for pb,mat in pose:
        pb.matrix_basis = mat


class VIEW3D_OT_McpRestTPoseButton(bpy.types.Operator):
    bl_idname = "mcp.rest_t_pose"
    bl_label = "T-pose => Rest Pose"
    bl_description = "Change rest pose to T-pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            initRig(context)
            setTPoseAsRestPose(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


class VIEW3D_OT_McpRestDefaultPoseButton(bpy.types.Operator):
    bl_idname = "mcp.rest_default_pose"
    bl_label = "Default Pose => Rest Pose"
    bl_description = "Change rest pose to default pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            initRig(context)
            setDefaultPoseAsRestPose(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


class VIEW3D_OT_McpRestCurrentPoseButton(bpy.types.Operator):
    bl_idname = "mcp.rest_current_pose"
    bl_label = "Current Pose => Rest Pose"
    bl_description = "Change rest pose to current pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            pose = getCurrentPose(context.object)
            initRig(context)
            setCurrentPose(pose)
            applyRestPose(context, 1.0)
            print("Set current pose to rest pose")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


class VIEW3D_OT_McpSetTPoseButton(bpy.types.Operator):
    bl_idname = "mcp.set_t_pose"
    bl_label = "Set T-pose"
    bl_description = "Set pose to stored T-pose"
    bl_options = {'UNDO'}

    problems = ""

    def execute(self, context):
        from .retarget import changeTargetData, restoreTargetData
        from .fkik import setRigifyFKIK

        if self.problems:
            return{'FINISHED'}

        rig = context.object
        scn = context.scene
        print("EXE")
        #data = changeTargetData(rig, scn)
        try:
            initRig(context)
            if isRigify(rig):
                setRigifyFKIK(rig, 0)
            setTPose(rig, scn)
            print("Set T-pose")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        finally:
            pass
            #restoreTargetData(rig, data)
        return{'FINISHED'}

    def invoke(self, context, event):
        return checkObjectProblems(self, context)

    def draw(self, context):
        drawObjectProblems(self)


class VIEW3D_OT_McpClearTPoseButton(bpy.types.Operator):
    bl_idname = "mcp.clear_t_pose"
    bl_label = "Clear T-pose"
    bl_description = "Clear stored T-pose"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            initRig(context)
            clearTPose(context.object)
            print("Cleared T-pose")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


def loadTPose(rig, filename):
    if filename:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        filepath = os.path.normpath(filepath)
        print("Loading %s" % filepath)
        struct = loadJson(filepath)
        rig.McpTPoseFile = filename
    else:
        return False

    unit = Matrix()
    for pb in rig.pose.bones:
        pb.matrix_basis = unit

    for name,value in struct:
        bname = getBoneName(rig, name)
        try:
            pb = rig.pose.bones[bname]
        except KeyError:
            continue
        quat = Quaternion(value)
        pb.matrix_basis = quat.to_matrix().to_4x4()
        setBoneTPose(pb, quat)

    rig.McpTPoseLoaded = True
    rig.McpRestTPose = False
    return True


def setBoneTPose(pb, quat):
    pb.McpQuatW = quat.w
    pb.McpQuatX = quat.x
    pb.McpQuatY = quat.y
    pb.McpQuatZ = quat.z


class VIEW3D_OT_McpLoadTPoseButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mcp.load_t_pose"
    bl_label = "Load T-pose"
    bl_description = "Load T-pose to active rig"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath to tpose file", maxlen=1024, default="")

    def execute(self, context):
        initRig(context)
        rig = context.object
        filename = os.path.relpath(self.filepath, os.path.dirname(__file__))
        try:
            loadTPose(rig, filename)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        print("Loaded T-pose")
        setTPose(rig, context.scene)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def saveTPose(context, filepath):
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


class VIEW3D_OT_McpSaveTPoseButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mcp.save_t_pose"
    bl_label = "Save T-pose"
    bl_description = "Save current pose as T-pose"
    bl_options = {'UNDO'}

    filename_ext = ".json"
    filter_glob = StringProperty(default="*.json", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath to tpose file", maxlen=1024, default="")

    def execute(self, context):
        try:
            saveTPose(context, self.filepath)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        print("Saved T-pose")
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def initRig(context):
    from . import target
    from . import source
    rig = context.object
    if rig.McpIsSourceRig:
        source.findSrcArmature(context, rig)
    else:
        target.getTargetArmature(rig, context.scene)


def getBoneName(rig, name):
    if rig.McpIsSourceRig:
        return name
    else:
        pb = getTrgBone(name, rig)
        if pb:
            return pb.name
        else:
            return ""

