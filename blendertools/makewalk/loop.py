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
from math import pi, sqrt
from mathutils import *
from . import load, simplify, props, action
from .utils import *

#
#   normalizeRotCurves(scn, rig, fcurves, frames)
#


def normalizeRotCurves(scn, rig, fcurves, frames):
    hasQuat = {}
    for fcu in fcurves:
        (name, mode) = fCurveIdentity(fcu)
        if mode == 'rotation_quaternion':
            hasQuat[name] = rig.pose.bones[name]

    nFrames = len(frames)
    for n,frame in enumerate(frames):
        scn.frame_set(frame)
        showProgress(n, frame, nFrames)
        for (name, pb) in hasQuat.items():
            pb.rotation_quaternion.normalize()
            pb.keyframe_insert("rotation_quaternion", group=name)

#
#   loopFCurves(context):
#   loopFCurve(fcu, minTime, maxTime, scn):
#   class VIEW3D_OT_McpLoopFCurvesButton(bpy.types.Operator):
#

def loopFCurves(context):
    scn = context.scene
    rig = context.object
    act = getAction(rig)
    if not act:
        return
    (fcurves, minTime, maxTime) = simplify.getActionFCurves(act, False, True, scn)
    if not fcurves:
        return

    frames = getActiveFrames(rig, minTime, maxTime)
    nFrames = len(frames)
    normalizeRotCurves(scn, rig, fcurves, frames)

    hasLocation = {}
    for n,fcu in enumerate(fcurves):
        (name, mode) = fCurveIdentity(fcu)
        if isRotation(mode):
            loopFCurve(fcu, minTime, maxTime, scn)

    if scn.McpLoopInPlace:
        iknames = [pb.name for pb in getIkBoneList(rig)]
        ikbones = {}
        for fcu in fcurves:
            (name, mode) = fCurveIdentity(fcu)
            if isLocation(mode) and name in iknames:
                ikbones[name] = rig.pose.bones[name]

        for pb in ikbones.values():
            print("IK bone %s" % pb.name)
            scn.frame_set(minTime)
            head0 = pb.head.copy()
            scn.frame_set(maxTime)
            head1 = pb.head.copy()
            offs = (head1-head0)/(maxTime-minTime)

            restMat = pb.bone.matrix_local.to_3x3()
            restInv = restMat.inverted()

            heads = {}
            for n,frame in enumerate(frames):
                scn.frame_set(frame)
                showProgress(n, frame, nFrames)
                heads[frame] = pb.head.copy()

            for n,frame in enumerate(frames):
                showProgress(n, frame, nFrames)
                scn.frame_set(frame)
                head = heads[frame] - (frame-minTime)*offs
                diff = head - pb.bone.head_local
                pb.location = restInv * diff
                pb.keyframe_insert("location", group=pb.name)

    return
    for fcu in fcurves:
        (name, mode) = fCurveIdentity(fcu)
        if isLocation(mode):
            loopFCurve(fcu, minTime, maxTime, scn)


def loopFCurve(fcu, t0, tn, scn):
    delta = scn.McpLoopBlendRange

    v0 = fcu.evaluate(t0)
    vn = fcu.evaluate(tn)
    fcu.keyframe_points.insert(frame=t0, value=v0)
    fcu.keyframe_points.insert(frame=tn, value=vn)
    (mode, upper, lower, diff) = simplify.getFCurveLimits(fcu)
    if mode == 'location':
        dv = vn-v0
    else:
        dv = 0.0

    newpoints = []
    for dt in range(delta):
        eps = 0.5*(1-dt/delta)

        t1 = t0+dt
        v1 = fcu.evaluate(t1)
        tm = tn+dt
        vm = fcu.evaluate(tm) - dv
        if (v1 > upper) and (vm < lower):
            vm += diff
        elif (v1 < lower) and (vm > upper):
            vm -= diff
        pt1 = (t1, (eps*vm + (1-eps)*v1))

        t1 = t0-dt
        v1 = fcu.evaluate(t1) + dv
        tm = tn-dt
        vm = fcu.evaluate(tm)
        if (v1 > upper) and (vm < lower):
            v1 -= diff
        elif (v1 < lower) and (vm > upper):
            v1 += diff
        ptm = (tm, eps*v1 + (1-eps)*vm)

        newpoints.extend([pt1,ptm])

    newpoints.sort()
    for (t,v) in newpoints:
        fcu.keyframe_points.insert(frame=t, value=v)
    return

class VIEW3D_OT_McpLoopFCurvesButton(bpy.types.Operator):
    bl_idname = "mcp.loop_fcurves"
    bl_label = "Loop F-curves"
    bl_description = "Make the beginning and end of the selected time range connect smoothly. Use before repeating."
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            startProgress("Loop F-curves")
            loopFCurves(context)
            endProgress("F-curves looped")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

#
#   repeatFCurves(context, nRepeats):
#

def repeatFCurves(context, nRepeats):
    startProgress("Repeat F-curves %d times" % nRepeats)
    act = getAction(context.object)
    if not act:
        return
    (fcurves, minTime, maxTime) = simplify.getActionFCurves(act, False, True, context.scene)
    if not fcurves:
        return

    dt0 = maxTime-minTime
    for fcu in fcurves:
        (name, mode) = fCurveIdentity(fcu)
        dy0 = fcu.evaluate(maxTime) - fcu.evaluate(minTime)
        points = []
        for kp in fcu.keyframe_points:
            t = kp.co[0]
            if t >= minTime and t < maxTime:
                points.append((t, kp.co[1]))
        for n in range(1,nRepeats):
            dt = n*dt0
            dy = n*dy0
            for (t,y) in points:
                fcu.keyframe_points.insert(t+dt, y+dy, options={'FAST'})

    endProgress("F-curves repeated %d times" % nRepeats)


class VIEW3D_OT_McpRepeatFCurvesButton(bpy.types.Operator):
    bl_idname = "mcp.repeat_fcurves"
    bl_label = "Repeat Animation"
    bl_description = "Repeat the part of the animation between selected markers n times"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            repeatFCurves(context, context.scene.McpRepeatNumber)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


#
#   stitchActions(context):
#

def stitchActions(context):
    from .retarget import getLocks, correctMatrixForLocks

    action.listAllActions(context)
    scn = context.scene
    rig = context.object
    act1 = action.getAction(scn.McpFirstAction)
    act2 = action.getAction(scn.McpSecondAction)
    frame1 = scn.McpFirstEndFrame
    frame2 = scn.McpSecondStartFrame
    delta = scn.McpLoopBlendRange
    factor = 1.0/delta
    shift = frame1 - frame2 - delta

    if rig.animation_data:
        rig.animation_data.action = None

    first1,last1 = getActionExtent(act1)
    first2,last2 = getActionExtent(act2)
    frames1 = range(first1, frame1)
    frames2 = range(frame2, last2+1)
    frames = range(first1, last2+shift+1)
    bmats1,_ = getBaseMatrices(act1, frames1, rig, True)
    bmats2,useLoc = getBaseMatrices(act2, frames2, rig, True)

    deletes = []
    for bname in bmats2.keys():
        try:
            bmats1[bname]
        except KeyError:
            deletes.append(bname)
    for bname in deletes:
        del bmats2[bname]

    orders = {}
    locks = {}
    for bname in bmats2.keys():
        pb = rig.pose.bones[bname]
        orders[bname],locks[bname] = getLocks(pb, scn)

    nFrames = len(frames)
    for n,frame in enumerate(frames):
        scn.frame_set(frame)
        showProgress(n, frame, nFrames)

        if frame <= frame1-delta:
            n1 = frame - first1
            for bname,mats in bmats1.items():
                pb = rig.pose.bones[bname]
                mat = mats[n1]
                if useLoc[bname]:
                    insertLocation(pb, mat)
                insertRotation(pb, mat)

        elif frame >= frame1:
            n2 = frame - frame1
            for bname,mats in bmats2.items():
                pb = rig.pose.bones[bname]
                mat = mats[n2]
                if useLoc[bname]:
                    insertLocation(pb, mat)
                insertRotation(pb, mat)

        else:
            n1 = frame - first1
            n2 = frame - frame1 + delta
            eps = factor*n2
            for bname,mats2 in bmats2.items():
                pb = rig.pose.bones[bname]
                mats1 = bmats1[bname]
                mat1 = mats1[n1]
                mat2 = mats2[n2]
                mat = (1-eps)*mat1 + eps*mat2
                mat = correctMatrixForLocks(mat, orders[bname], locks[bname], pb, scn.McpUseLimits)
                if useLoc[bname]:
                    insertLocation(pb, mat)
                insertRotation(pb, mat)

    setInterpolation(rig)
    act = rig.animation_data.action
    act.name = scn.McpOutputActionName


def getActionExtent(act):
    first = 10000
    last = -10000
    for fcu in act.fcurves:
        t0 = int(fcu.keyframe_points[0].co[0])
        t1 = int(fcu.keyframe_points[-1].co[0])
        if t0 < first:
            first = t0
        if t1 > last:
            last = t1
    return first,last


class VIEW3D_OT_McpStitchActionsButton(bpy.types.Operator):
    bl_idname = "mcp.stitch_actions"
    bl_label = "Stitch Actions"
    bl_description = "Stitch two action together seamlessly"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            startProgress("Stitch actions")
            stitchActions(context)
            endProgress("Actions stitched")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


#
#   shiftBoneFCurves(rig, scn):
#   class VIEW3D_OT_McpShiftBoneFCurvesButton(bpy.types.Operator):
#

def getBaseMatrices(act, frames, rig, useAll):
    locFcurves = {}
    quatFcurves = {}
    eulerFcurves = {}
    for fcu in act.fcurves:
        (bname, mode) = fCurveIdentity(fcu)
        pb = rig.pose.bones[bname]
        if useAll or pb.bone.select:
            if mode == "location":
                try:
                    fcurves = locFcurves[bname]
                except KeyError:
                    fcurves = locFcurves[bname] = [None,None,None]
            elif mode == "rotation_euler":
                try:
                    fcurves = eulerFcurves[bname]
                except KeyError:
                    fcurves = eulerFcurves[bname] = [None,None,None]
            elif mode == "rotation_quaternion":
                try:
                    fcurves = quatFcurves[bname]
                except KeyError:
                    fcurves = quatFcurves[bname] = [None,None,None,None]
            else:
                continue

            fcurves[fcu.array_index] = fcu

    basemats = {}
    useLoc = {}
    for bname,fcurves in eulerFcurves.items():
        useLoc[bname] = False
        order = rig.pose.bones[bname].rotation_mode
        fcu0,fcu1,fcu2 = fcurves
        rmats = basemats[bname] = []
        for frame in frames:
            euler = Euler((fcu0.evaluate(frame), fcu1.evaluate(frame), fcu2.evaluate(frame)))
            rmats.append(euler.to_matrix().to_4x4())

    for bname,fcurves in quatFcurves.items():
        useLoc[bname] = False
        fcu0,fcu1,fcu2,fcu3 = fcurves
        rmats = basemats[bname] = []
        for frame in frames:
            quat = Quaternion((fcu0.evaluate(frame), fcu1.evaluate(frame), fcu2.evaluate(frame), fcu3.evaluate(frame)))
            rmats.append(quat.to_matrix().to_4x4())

    for bname,fcurves in locFcurves.items():
        useLoc[bname] = True
        fcu0,fcu1,fcu2 = fcurves
        tmats = []
        for frame in frames:
            loc = (fcu0.evaluate(frame), fcu1.evaluate(frame), fcu2.evaluate(frame))
            tmats.append(Matrix.Translation(loc))
        try:
            rmats = basemats[bname]
        except KeyError:
            basemats[bname] = tmats
            rmats = None
        if rmats:
            mats = []
            for n,rmat in enumerate(rmats):
                tmat = tmats[n]
                mats.append( tmat*rmat )
            basemats[bname] = mats

    return basemats, useLoc


def shiftBoneFCurves(rig, scn):
    from .retarget import getLocks, correctMatrixForLocks

    frames = [scn.frame_current] + getActiveFrames(rig)
    nFrames = len(frames)
    act = getAction(rig)
    if not act:
        return
    basemats, useLoc = getBaseMatrices(act, frames, rig, False)

    deltaMat = {}
    orders = {}
    locks = {}
    for bname,bmats in basemats.items():
        pb = rig.pose.bones[bname]
        bmat = bmats[0]
        deltaMat[pb.name] = pb.matrix_basis * bmat.inverted()
        orders[pb.name], locks[pb.name] = getLocks(pb, scn)

    for n,frame in enumerate(frames[1:]):
        scn.frame_set(frame)
        showProgress(n, frame, nFrames)
        for bname,bmats in basemats.items():
            pb = rig.pose.bones[bname]
            mat = deltaMat[pb.name] * bmats[n+1]
            mat = correctMatrixForLocks(mat, orders[bname], locks[bname], pb, scn.McpUseLimits)
            if useLoc[bname]:
                insertLocation(pb, mat)
            insertRotation(pb, mat)


def printmat(mat):
    print("   (%.4f %.4f %.4f %.4f)" % tuple(mat.to_quaternion()))


class VIEW3D_OT_McpShiftBoneFCurvesButton(bpy.types.Operator):
    bl_idname = "mcp.shift_bone"
    bl_label = "Shift Animation"
    bl_description = "Shift the animation globally for selected boens"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            startProgress("Shift animation")
            shiftBoneFCurves(context.object, context.scene)
            endProgress("Animation shifted")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


def fixateBoneFCurves(rig, scn):
    act = getAction(rig)
    if not act:
        return

    frame = scn.frame_current
    minTime,maxTime = getMarkedTime(scn)
    if minTime is None:
        minTime = -1e6
    if maxTime is None:
        maxTime = 1e6
    fixArray = [False,False,False]
    if scn.McpFixX:
        fixArray[0] = True
    if scn.McpFixY:
        fixArray[1] = True
    if scn.McpFixZ:
        fixArray[2] = True

    for fcu in act.fcurves:
        (bname, mode) = fCurveIdentity(fcu)
        pb = rig.pose.bones[bname]
        if pb.bone.select and isLocation(mode) and fixArray[fcu.array_index]:
            value = fcu.evaluate(frame)
            for kp in fcu.keyframe_points:
                if kp.co[0] >= minTime and kp.co[0] <= maxTime:
                    kp.co[1] = value


class VIEW3D_OT_McpFixateBoneFCurvesButton(bpy.types.Operator):
    bl_idname = "mcp.fixate_bone"
    bl_label = "Fixate Bone Location"
    bl_description = "Keep bone location fixed (local coordinates)"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            startProgress("Fixate bone locations")
            fixateBoneFCurves(context.object, context.scene)
            endProgress("Bone locations fixed")
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}
