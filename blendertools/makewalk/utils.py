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
from bpy.props import *
from math import sin, cos, atan, pi
from mathutils import *

Deg2Rad = pi/180
Rad2Deg = 180/pi

#
#   printMat3(string, mat)
#

def printMat3(string, mat, pad=""):
    if not mat:
        print("%s None" % string)
        return
    print("%s " % string)
    mc = "%s  [" % pad
    for m in range(3):
        s = mc
        for n in range(3):
            s += " %6.3f" % mat[m][n]
        print(s+"]")

def printMat4(string, mat, pad=""):
    if not mat:
        print("%s None" % string)
        return
    print("%s%s " % (pad, string))
    mc = "%s  [" % pad
    for m in range(4):
        s = mc
        for n in range(4):
            s += " %6.3f" % mat[m][n]
        print(s+"]")

#
#  quadDict():
#

def quadDict():
    return {
        0: {},
        1: {},
        2: {},
        3: {},
    }

MhxLayers = 8*[True] + 8*[False] + 8*[True] + 8*[False]
RigifyLayers = 27*[True] + 5*[False]

#
#   Identify rig type
#

def allBonesInList(list, rig):
    for bname in list:
        if bname not in rig.pose.bones.keys():
            return False
    return True


def isMhxRig(rig):
    return ('foot.rev.L' in rig.pose.bones.keys())

def isDefaultRig(rig):
    return allBonesInList(['risorius03.L', 'shoulder01.R', "upperleg01.L", "upperleg02.L"], rig)

def isMbRig(rig):
    return allBonesInList(["LeftArm", "LeftArmRoll"], rig)

def isMhx7Rig(rig):
    return ('FootRev_L' in rig.pose.bones.keys())

def isRigify(rig):
    return ('MCH-spine.flex' in rig.pose.bones.keys())


def isMakeHumanRig(rig):
    return ("MhAlpha8" in rig.keys())

#
#   nameOrNone(string):
#

def nameOrNone(string):
    if string == "None":
        return None
    else:
        return string


def canonicalName(string):
    return string.lower().replace(' ','_').replace('-','_')


#
#   getRoll(bone):
#

def getRoll(bone):
    return getRollMat(bone.matrix_local)


def getRollMat(mat):
    quat = mat.to_3x3().to_quaternion()
    if abs(quat.w) < 1e-4:
        roll = pi
    else:
        roll = -2*atan(quat.y/quat.w)
    return roll


#
#   getTrgBone(b):
#

def getTrgBone(bname, rig):
    for pb in rig.pose.bones:
        if pb.McpBone == bname:
            return pb
    return None


#
#   getIkBoneList(rig):
#

def getIkBoneList(rig):
    hips = getTrgBone('hips', rig)
    if hips is None:
        if isMhxRig(rig):
            hips = rig.pose.bones["root"]
        elif isRigify(rig):
            hips = rig.pose.bones["hips"]
        else:
            for bone in rig.data.bones:
                if bone.parent is None:
                    hips = bone
                    break
    blist = [hips]
    for bname in ['hand.ik.L', 'hand.ik.R', 'foot.ik.L', 'foot.ik.R']:
        try:
            blist.append(rig.pose.bones[bname])
        except KeyError:
            pass
    return blist

#
#   getAction(ob):
#

def getAction(ob):
    try:
        return ob.animation_data.action
    except:
        print("%s has no action" % ob)
        return None

#
#   deleteAction(act):
#

def deleteAction(act):
    act.use_fake_user = False
    if act.users == 0:
        bpy.data.actions.remove(act)
    else:
        print("%s has %d users" % (act, act.users))

#
#   copyAction(act1, name):
#

def copyAction(act1, name):
    act2 = bpy.data.actions.new(name)
    for fcu1 in act1.fcurves:
        fcu2 = act2.fcurves.new(fcu1.data_path, fcu1.array_index)
        for kp1 in fcu1.keyframe_points:
            fcu2.keyframe_points.insert(kp1.co[0], kp1.co[1], options={'FAST'})
    return act2

#
#
#

def insertLocation(pb, mat):
    pb.location = mat.to_translation()
    pb.keyframe_insert("location", group=pb.name)


def insertRotation(pb, mat):
    q = mat.to_quaternion()
    if pb.rotation_mode == 'QUATERNION':
        pb.rotation_quaternion = q
        pb.keyframe_insert("rotation_quaternion", group=pb.name)
    else:
        pb.rotation_euler = q.to_euler(pb.rotation_mode)
        pb.keyframe_insert("rotation_euler", group=pb.name)


def isRotationMatrix(mat):
    mat = mat.to_3x3()
    prod = mat * mat.transposed()
    diff = prod - Matrix().to_3x3()
    for i in range(3):
        for j in range(3):
            if abs(diff[i][j]) > 1e-3:
                print("Not a rotation matrix")
                print(mat)
                print(prod)
                return False
    return True


#
#   getActiveFrames(ob):
#

def getActiveFrames0(ob):
    active = {}
    if ob.animation_data is None:
        return active
    action = ob.animation_data.action
    if action is None:
        return active
    for fcu in action.fcurves:
        for kp in fcu.keyframe_points:
            active[kp.co[0]] = True
    return active


def getActiveFrames(ob, minTime=None, maxTime=None):
    active = getActiveFrames0(ob)
    frames = list(active.keys())
    frames.sort()
    if minTime is not None:
        while frames[0] < minTime:
            frames = frames[1:]
    if maxTime is not None:
        frames.reverse()
        while frames[0] > maxTime:
            frames = frames[1:]
        frames.reverse()
    return frames


def getActiveFramesBetweenMarkers(ob, scn):
    minTime,maxTime = getMarkedTime(scn)
    if minTime is None:
        return getActiveFrames(ob)
    active = getActiveFrames0(ob)
    frames = []
    for time in active.keys():
        if time >= minTime and time <= maxTime:
            frames.append(time)
    frames.sort()
    return frames

#
#    getMarkedTime(scn):
#

def getMarkedTime(scn):
    markers = []
    for mrk in scn.timeline_markers:
        if mrk.select:
            markers.append(mrk.frame)
    markers.sort()
    if len(markers) >= 2:
        return (markers[0], markers[-1])
    else:
        return (None, None)

#
#   fCurveIdentity(fcu):
#

def fCurveIdentity(fcu):
    words = fcu.data_path.split('"')
    if len(words) < 2:
        return (None, None)
    name = words[1]
    words = fcu.data_path.split('.')
    mode = words[-1]
    return (name, mode)

#
#   findFCurve(path, index, fcurves):
#

def findFCurve(path, index, fcurves):
    for fcu in fcurves:
        if (fcu.data_path == path and
            fcu.array_index == index):
            return fcu
    print('F-curve "%s" not found.' % path)
    return None


def findBoneFCurve(pb, rig, index, mode='rotation'):
    if mode == 'rotation':
        if pb.rotation_mode == 'QUATERNION':
            mode = "rotation_quaternion"
        else:
            mode = "rotation_euler"
    path = 'pose.bones["%s"].%s' % (pb.name, mode)

    if rig.animation_data is None:
        return None
    action = rig.animation_data.action
    if action is None:
        return None
    return findFCurve(path, index, action.fcurves)


def fillKeyFrames(pb, rig, frames, nIndices, mode='rotation'):
    for index in range(nIndices):
        fcu = findBoneFCurve(pb, rig, index, mode)
        if fcu is None:
            return
        for frame in frames:
            y = fcu.evaluate(frame)
            fcu.keyframe_points.insert(frame, y, options={'FAST'})

#
#   isRotation(mode):
#   isLocation(mode):
#

def isRotation(mode):
    return (mode[0:3] == 'rot')

def isLocation(mode):
    return (mode[0:3] == 'loc')


#
#    setRotation(pb, mat, frame, group):
#

def setRotation(pb, rot, frame, group):
    if pb.rotation_mode == 'QUATERNION':
        try:
            quat = rot.to_quaternion()
        except:
            quat = rot
        pb.rotation_quaternion = quat
        pb.keyframe_insert('rotation_quaternion', frame=frame, group=group)
    else:
        try:
            euler = rot.to_euler(pb.rotation_mode)
        except:
            euler = rot
        pb.rotation_euler = euler
        pb.keyframe_insert('rotation_euler', frame=frame, group=group)


#
#   setRestPose(rig):
#

def selectAndSetRestPose(rig, scn):
    reallySelect(rig, scn)
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.rot_clear()
    bpy.ops.pose.loc_clear()
    bpy.ops.pose.scale_clear()

#
#  reallySelect(ob, scn)
#  Make sure that selecting an object really takes.
#

def reallySelect(ob, scn):
    ob.hide = False
    visible = False
    for n,vis in enumerate(ob.layers):
        if vis and scn.layers[n]:
            visible = True
            break
    if not visible:
        for n,vis in enumerate(ob.layers):
            if vis:
                scn.layers[n] = True
                visible = True
                break
    if not visible:
        for n,vis in enumerate(scn.layers):
            if vis:
                ob.layers[n] = True
                visible = True
                break
    if not visible:
        ob.layers[0] = scn.layers[0] = True
    scn.objects.active = ob


#
#    setInterpolation(rig):
#

def setInterpolation(rig):
    if not rig.animation_data:
        return
    act = rig.animation_data.action
    if not act:
        return
    for fcu in act.fcurves:
        for pt in fcu.keyframe_points:
            pt.interpolation = 'LINEAR'
        fcu.extrapolation = 'CONSTANT'
    return

#
#   insertRotationKeyFrame(pb, frame):
#

def insertRotationKeyFrame(pb, frame):
    rotMode = pb.rotation_mode
    grp = pb.name
    if rotMode == "QUATERNION":
        pb.keyframe_insert("rotation_quaternion", frame=frame, group=grp)
    elif rotMode == "AXIS_ANGLE":
        pb.keyframe_insert("rotation_axis_angle", frame=frame, group=grp)
    else:
        pb.keyframe_insert("rotation_euler", frame=frame, group=grp)

#
#   checkObjectProblems(self, context):
#

def getObjectProblems(self, context):
    self.problems = ""
    epsilon = 1e-2
    rig = context.object
    scn = context.scene

    eu = rig.rotation_euler
    print(eu)
    if abs(eu.x) + abs(eu.y) + abs(eu.z) > epsilon:
        if scn.McpApplyObjectTransforms:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        else:
            self.problems += "object rotation\n"

    vec = rig.scale - Vector((1,1,1))
    print(vec, vec.length)
    if vec.length > epsilon:
        if scn.McpApplyObjectTransforms:
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        else:
            self.problems += "object scaling\n"

    if self.problems:
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300, height=20)
    else:
        return False


def checkObjectProblems(self, context):
    problems = getObjectProblems(self, context)
    if problems:
        return problems
    else:
        return self.execute(context)


def problemFreeFileSelect(self, context):
    problems = getObjectProblems(self, context)
    if problems:
        return problems
    context.window_manager.fileselect_add(self)
    return {'RUNNING_MODAL'}


def drawObjectProblems(self):
    if self.problems:
        self.layout.label("MakeWalk cannot use this rig because it has:")
        for problem in self.problems.split("\n"):
            self.layout.label("  %s" % problem)
        self.layout.label("Apply object transformations before using MakeWalk")

#
#   showProgress(n, frame):
#

def startProgress(string):
    print("%s (0 pct)" % string)


def endProgress(string):
    print("%s (100 pct)" % string)


def showProgress(n, frame, nFrames, step=20):
    if n % step == 0:
        print("%d (%.1f pct)" % (int(frame), (100.0*n)/nFrames))

#
#
#

_category = ""
_errorLines = ""

def setCategory(string):
    global _category
    _category = string

def clearCategory():
    global _category
    _category = "General error"

clearCategory()


class MocapError(Exception):
    def __init__(self, value):
        global _errorLines
        self.value = value
        _errorLines = (
            ["Catogory: %s" % _category] +
            value.split("\n") +
            ["" +
             "For corrective actions see:",
             "http://www.makehuman.org/doc/node/",
             "  makewalk_errors_and_corrective_actions.html"]
            )
        print("*** Mocap error ***")
        for line in _errorLines:
            print(line)

    def __str__(self):
        return repr(self.value)


class ErrorOperator(bpy.types.Operator):
    bl_idname = "mcp.error"
    bl_label = "Mocap error"

    def execute(self, context):
        clearCategory()
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        global _errorLines
        for line in _errorLines:
            self.layout.label(line)

