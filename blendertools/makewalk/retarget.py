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

#
#   M_b = global bone matrix, relative world (PoseBone.matrix)
#   L_b = local bone matrix, relative parent and rest (PoseBone.matrix_local)
#   R_b = bone rest matrix, relative armature (Bone.matrix_local)
#   T_b = global T-pose marix, relative world
#
#   M_b = M_p R_p^-1 R_b L_b
#   M_b = A_b M'_b
#   T_b = A_b T'_b
#   A_b = T_b T'^-1_b
#   B_b = R^-1_b R_p
#
#   L_b = R^-1_b R_p M^-1_p A_b M'_b
#   L_b = B_b M^-1_p A_b M'_b
#


import bpy
import mathutils
import time
from collections import OrderedDict
from mathutils import *
from bpy_extras.io_utils import ImportHelper
from bpy.props import *

from .simplify import simplifyFCurves, rescaleFCurves
from .utils import *
from . import t_pose


class CAnimation:

    def __init__(self, srcRig, trgRig, boneAssoc, scn):
        self.srcRig = srcRig
        self.trgRig = trgRig
        self.scene = scn
        self.boneAnims = OrderedDict()

        for (trgName, srcName) in boneAssoc:
            try:
                trgBone = trgRig.pose.bones[trgName]
                srcBone = srcRig.pose.bones[srcName]
            except KeyError:
                print("  -", trgName, srcName)
                continue
            banim = self.boneAnims[trgName] = CBoneAnim(srcBone, trgBone, self, scn)


    def printResult(self, scn, frame):
        scn.frame_set(frame)
        for name in ["LeftHip"]:
            banim = self.boneAnims[name]
            banim.printResult(frame)


    def setTPose(self, scn):
        selectAndSetRestPose(self.srcRig, scn)
        t_pose.setTPose(self.srcRig, scn)
        selectAndSetRestPose(self.trgRig, scn)
        t_pose.setTPose(self.trgRig, scn)
        for banim in self.boneAnims.values():
            banim.insertTPoseFrame()
        scn.frame_set(0)
        for banim in self.boneAnims.values():
            banim.getTPoseMatrix()


    def retarget(self, frames, scn):
        objects = hideObjects(scn, self.srcRig)
        try:
            for frame in frames:
                scn.frame_set(frame)
                for banim in self.boneAnims.values():
                    banim.retarget(frame)
        finally:
            unhideObjects(objects)


class CBoneAnim:

    def __init__(self, srcBone, trgBone, anim, scn):
        self.name = srcBone.name
        self.srcMatrices = {}
        self.trgMatrices = {}
        self.srcMatrix = None
        self.trgMatrix = None
        self.srcBone = srcBone
        self.trgBone = trgBone
        self.order,self.locks = getLocks(trgBone, scn)
        self.aMatrix = None
        self.parent = self.getParent(trgBone, anim)
        if self.parent:
            self.trgBone.McpParent = self.parent.trgBone.name
            trgParent = self.parent.trgBone
            self.bMatrix = trgBone.bone.matrix_local.inverted() * trgParent.bone.matrix_local
        else:
            self.bMatrix = trgBone.bone.matrix_local.inverted()
        self.useLimits = anim.scene.McpUseLimits


    def __repr__(self):
        if self.parent:
            parname = self.parent.name
        else:
            parname = None
        return (
            "<CBoneAnim %s\n" % self.name +
            "  src %s\n" % self.srcBone.name +
            "  trg %s\n" % self.trgBone.name +
            "  par %s\n" % parname +
            "  A %s\n" % self.aMatrix +
            "  B %s\n" % self.bMatrix)


    def printResult(self, frame):
        print(
            "Retarget %s => %s\n" % (self.srcBone.name, self.trgBone.name) +
            "S %s\n" % self.srcBone.matrix +
            "T %s\n" % self.trgBone.matrix +
            "R %s\n" % (self.trgBone.matrix * self.srcBone.matrix.inverted())
            )


    def getParent(self, pb, anim):
        pb = pb.parent
        while pb:
            if pb.McpBone:
                try:
                    return anim.boneAnims[pb.name]
                except KeyError:
                    pass

            subtar = None
            for cns in pb.constraints:
                if (cns.type[0:4] == "COPY" and
                    cns.influence > 0.8):
                    subtar = cns.subtarget

            if subtar:
                pb = anim.trgRig.pose.bones[subtar]
            else:
                pb = pb.parent
        return None


    def insertKeyFrame(self, mat, frame):
        pb = self.trgBone
        setRotation(pb, mat, frame, pb.name)
        if not self.parent:
            pb.location = mat.to_translation()
            pb.keyframe_insert("location", frame=frame, group=pb.name)


    def insertTPoseFrame(self):
        mat = t_pose.getStoredBonePose(self.trgBone)
        self.insertKeyFrame(mat, 0)


    def getTPoseMatrix(self):
        self.aMatrix =  self.srcBone.matrix.inverted() * self.trgBone.matrix
        if not isRotationMatrix(self.trgBone.matrix):
            print("* WARNING *\nTarget %s not rotation matrix:\n%s" % (self.trgBone.name, self.trgBone.matrix))
        if not isRotationMatrix(self.srcBone.matrix):
            print("* WARNING *\nSource %s not rotation matrix:\n%s" % (self.srcBone.name, self.srcBone.matrix))
        if not isRotationMatrix(self.aMatrix):
            print("* WARNING *\nA %s not rotation matrix:\n%s" % (self.trgBone.name, self.aMatrix))


    def retarget(self, frame):
        self.srcMatrix = self.srcBone.matrix.copy()
        self.trgMatrix = self.srcMatrix * self.aMatrix
        self.trgMatrix.col[3] = self.srcMatrix.col[3]
        if self.parent:
            mat1 = self.parent.trgMatrix.inverted() * self.trgMatrix
        else:
            mat1 = self.trgMatrix
        mat2 = self.bMatrix * mat1
        mat3 = correctMatrixForLocks(mat2, self.order, self.locks, self.trgBone, self.useLimits)
        self.insertKeyFrame(mat3, frame)

        self.srcMatrices[frame] = self.srcMatrix
        mat1 = self.bMatrix.inverted() * mat3
        if self.parent:
            self.trgMatrix = self.parent.trgMatrix * mat1
        else:
            self.trgMatrix = mat1
        self.trgMatrices[frame] = self.trgMatrix

        return

        if self.name == "upper_arm.L":
            print()
            print(self)
            print("S ", self.srcMatrix)
            print("T ", self.trgMatrix)
            print(self.parent.name)
            print("TP", self.parent.trgMatrix)
            print("M1", mat1)
            print("M2", mat2)
            print("MB2", self.trgBone.matrix)


def getLocks(pb, scn):
    locks = []
    order = 'XYZ'
    if scn.McpClearLocks:
        pb.lock_rotation[0] = pb.lock_rotation[2] = False
        for cns in pb.constraints:
            if cns.type == 'LIMIT_ROTATION':
                cns.use_limit_x = cns.use_limit_z = 0

    if pb.lock_rotation[1]:
        locks.append(1)
        order = 'YZX'
        if pb.lock_rotation[0]:
            order = 'YXZ'
            locks.append(0)
        if pb.lock_rotation[2]:
            locks.append(2)
    elif pb.lock_rotation[2]:
        locks.append(2)
        order = 'ZYX'
        if pb.lock_rotation[0]:
            order = 'ZXY'
            locks.append(0)
    elif pb.lock_rotation[0]:
        locks.append(0)
        order = 'XYZ'

    if pb.rotation_mode != 'QUATERNION':
        order = pb.rotation_mode

    return order,locks


def correctMatrixForLocks(mat, order, locks, pb, useLimits):
    head = Vector(mat.col[3])

    if locks:
        euler = mat.to_3x3().to_euler(order)
        for n in locks:
            euler[n] = 0
        mat = euler.to_matrix().to_4x4()

    if not useLimits:
        mat.col[3] = head
        return mat

    for cns in pb.constraints:
        if (cns.type == 'LIMIT_ROTATION' and
            cns.owner_space == 'LOCAL' and
            not cns.mute and
            cns.influence > 0.5):
            euler = mat.to_3x3().to_euler(order)
            if cns.use_limit_x:
                euler.x = min(cns.max_x, max(cns.min_x, euler.x))
            if cns.use_limit_y:
                euler.y = min(cns.max_y, max(cns.min_y, euler.y))
            if cns.use_limit_z:
                euler.z = min(cns.max_z, max(cns.min_z, euler.z))
            mat = euler.to_matrix().to_4x4()

    mat.col[3] = head
    return mat


def hideObjects(scn, rig):
    objects = []
    for ob in scn.objects:
        if ob != rig:
            objects.append((ob, list(ob.layers)))
            ob.layers = 20*[False]
    return objects


def unhideObjects(objects):
    for (ob,layers) in objects:
        ob.layers = layers
    return


def clearMcpProps(rig):
    keys = list(rig.keys())
    for key in keys:
        if key[0:3] == "Mcp":
            del rig[key]

    for pb in rig.pose.bones:
        keys = list(pb.keys())
        for key in keys:
            if key[0:3] == "Mcp":
                del pb[key]


def retargetAnimation(context, srcRig, trgRig):
    from . import source, target
    from .fkik import setMhxIk, setRigifyFKIK

    startProgress("Retargeting")
    scn = context.scene
    setMhxIk(trgRig, True, True, 0.0)
    frames = getActiveFrames(srcRig)
    nFrames = len(frames)
    reallySelect(trgRig, scn)
    if trgRig.animation_data:
        trgRig.animation_data.action = None
    scn.update()

    if isRigify(trgRig):
        setRigifyFKIK(trgRig, 0.0)

    try:
        scn.frame_current = frames[0]
    except:
        raise MocapError("No frames found.")
    oldData = changeTargetData(trgRig, scn)

    source.ensureSourceInited(scn)
    source.setArmature(srcRig, scn)
    print("Retarget %s --> %s" % (srcRig.name, trgRig.name))

    target.ensureTargetInited(scn)
    boneAssoc = target.getTargetArmature(trgRig, scn)
    disconnectHips(trgRig, boneAssoc)
    anim = CAnimation(srcRig, trgRig, boneAssoc, scn)
    anim.setTPose(scn)

    setCategory("Retarget")
    frameBlock = frames[0:100]
    index = 0
    try:
        while frameBlock:
            showProgress(index, frames[index], nFrames)
            anim.retarget(frameBlock, scn)
            index += 100
            frameBlock = frames[index:index+100]

        scn.frame_current = frames[0]
    finally:
        restoreTargetData(trgRig, oldData)

    #anim.printResult(scn, 1)

    setInterpolation(trgRig)
    act = trgRig.animation_data.action
    act.name = trgRig.name[:4] + srcRig.name[2:]
    act.use_fake_user = True
    clearCategory()
    endProgress("Retargeted %s --> %s" % (srcRig.name, trgRig.name))


def disconnectHips(rig, boneAssoc):
    for bname,mname in boneAssoc:
        if mname == "hips":
            bpy.ops.object.mode_set(mode='EDIT')
            rig.data.edit_bones[bname].use_connect = False
            bpy.ops.object.mode_set(mode='POSE')
            return

#
#   changeTargetData(rig, scn):
#   restoreTargetData(rig, data):
#

def changeTargetData(rig, scn):
    tempProps = [
        ("MhaRotationLimits", 0.0),
        ("MhaArmIk_L", 0.0),
        ("MhaArmIk_R", 0.0),
        ("MhaLegIk_L", 0.0),
        ("MhaLegIk_R", 0.0),
        ("MhaSpineIk", 0),
        ("MhaSpineInvert", 0),
        ("MhaElbowPlant_L", 0),
        ("MhaElbowPlant_R", 0),
        ]

    props = []
    for (key, value) in tempProps:
        try:
            props.append((key, rig[key]))
            rig[key] = value
        except KeyError:
            pass

    permProps = [
        ("MhaElbowFollowsShoulder", 0),
        ("MhaElbowFollowsWrist", 0),
        ("MhaKneeFollowsHip", 0),
        ("MhaKneeFollowsFoot", 0),
        ("MhaArmHinge", 0),
        ("MhaLegHinge", 0),
        ]

    for (key, value) in permProps:
        try:
            rig[key+"_L"]
            rig[key+"_L"] = value
            rig[key+"_R"] = value
        except KeyError:
            pass

    layers = list(rig.data.layers)
    if rig.MhAlpha8:
        rig.data.layers = MhxLayers
    elif isRigify(rig):
        rig.data.layers = RigifyLayers

    locks = []
    for pb in rig.pose.bones:
        constraints = []
        if not scn.McpUseLimits:
            for cns in pb.constraints:
                if cns.type == 'LIMIT_DISTANCE':
                    cns.mute = True
                elif cns.type[0:5] == 'LIMIT':
                    constraints.append( (cns, cns.mute) )
                    cns.mute = True
        locks.append( (pb, constraints) )

    norotBones = []
    return (props, layers, locks, norotBones)


def restoreTargetData(rig, data):
    (props, rig.data.layers, locks, norotBones) = data

    for (key,value) in props:
        rig[key] = value

    for b in norotBones:
        b.use_inherit_rotation = True

    for lock in locks:
        (pb, constraints) = lock
        for (cns, mute) in constraints:
            cns.mute = mute


#
#    loadRetargetSimplify(context, filepath):
#

def loadRetargetSimplify(context, filepath):
    from . import load
    from .fkik import limbsBendPositive

    print("\nLoad and retarget %s" % filepath)
    time1 = time.clock()
    scn = context.scene
    trgRig = context.object
    data = changeTargetData(trgRig, scn)
    try:
        #clearMcpProps(trgRig)
        srcRig = load.readBvhFile(context, filepath, scn, False)
        try:
            load.renameAndRescaleBvh(context, srcRig, trgRig)
            retargetAnimation(context, srcRig, trgRig)
            scn = context.scene
            if scn.McpDoBendPositive:
                limbsBendPositive(trgRig, True, True, (0,1e6))
            if scn.McpDoSimplify:
                simplifyFCurves(context, trgRig, False, False)
            if scn.McpRescale:
                rescaleFCurves(context, trgRig, scn.McpRescaleFactor)
        finally:
            load.deleteSourceRig(context, srcRig, 'Y_')
    finally:
        restoreTargetData(trgRig, data)
    time2 = time.clock()
    print("%s finished in %.3f s" % (filepath, time2-time1))
    return


########################################################################
#
#   Buttons
#

class VIEW3D_OT_NewRetargetMhxButton(bpy.types.Operator):
    bl_idname = "mcp.retarget_mhx"
    bl_label = "Retarget Selected To Active"
    bl_description = "Retarget animation to the active (target) armature from the other selected (source) armature"
    bl_options = {'UNDO'}

    problems = ""

    def execute(self, context):
        from . import target

        if self.problems:
            return{'FINISHED'}

        trgRig = context.object
        scn = context.scene
        data = changeTargetData(trgRig, scn)
        rigList = list(context.selected_objects)

        try:
            target.getTargetArmature(trgRig, scn)
            for srcRig in rigList:
                if srcRig != trgRig:
                    retargetAnimation(context, srcRig, trgRig)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        finally:
            restoreTargetData(trgRig, data)
        return{'FINISHED'}

    def invoke(self, context, event):
        return checkObjectProblems(self, context)

    def draw(self, context):
        drawObjectProblems(self)


class VIEW3D_OT_LoadAndRetargetButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mcp.load_and_retarget"
    bl_label = "Load And Retarget"
    bl_description = "Load animation from bvh file to the active armature"
    bl_options = {'UNDO'}

    problems = ""
    filename_ext = ".bvh"
    filter_glob = StringProperty(default="*.bvh", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for importing the BVH file", maxlen=1024, default="")

    @classmethod
    def poll(self, context):
        return (context.object and context.object.type == 'ARMATURE')

    def execute(self, context):
        if self.problems:
            return{'FINISHED'}

        try:
            loadRetargetSimplify(context, self.properties.filepath)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

    def invoke(self, context, event):
        return problemFreeFileSelect(self, context)

    def draw(self, context):
        drawObjectProblems(self)


class VIEW3D_OT_ClearTempPropsButton(bpy.types.Operator):
    bl_idname = "mcp.clear_temp_props"
    bl_label = "Clear Temporary Properties"
    bl_description = "Clear properties used by MakeWalk. Animation editing may fail after this."
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            clearMcpProps(context.object)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}
