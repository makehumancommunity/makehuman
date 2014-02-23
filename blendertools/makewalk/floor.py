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
from bpy.props import BoolProperty
from mathutils import Matrix, Vector
from .utils import *
from . import fkik

#-------------------------------------------------------------
#  Plane
#-------------------------------------------------------------

def getRigAndPlane(scn):
    rig = None
    plane = None
    for ob in scn.objects:
        if ob.select:
            if ob.type == 'ARMATURE':
                if rig:
                    raise MocapError("Two armatures selected: %s and %s" % (rig.name, ob.name))
                else:
                    rig = ob
            elif ob.type == 'MESH':
                if plane:
                    raise MocapError("Two meshes selected: %s and %s" % (plane.name, ob.name))
                else:
                    plane = ob
    if rig is None:
        raise MocapError("No rig selected")
    return rig,plane


def getPlaneInfo(plane):
    if plane is None:
        ez = Vector((0,0,1))
        origin = Vector((0,0,0))
        rot = Matrix()
    else:
        mat = plane.matrix_world.to_3x3().normalized()
        ez = mat.col[2]
        origin = plane.location
        rot = mat.to_4x4()
    return ez,origin,rot

#-------------------------------------------------------------
#   Offset and projection
#-------------------------------------------------------------

def getProjection(vec, ez):
    return ez.dot(Vector(vec[:3]))


def getOffset(point, ez, origin):
    vec = Vector(point[:3]) - origin
    offset = -ez.dot(vec)
    return offset


def getHeadOffset(pb, ez, origin):
    head = pb.matrix.col[3]
    return getOffset(head, ez, origin)


def getTailOffset(pb, ez, origin):
    head = pb.matrix.col[3]
    y = pb.matrix.col[1]
    tail = head + y*pb.length
    return getOffset(tail, ez, origin)


def addOffset(pb, offset, ez):
    gmat = pb.matrix.copy()
    x,y,z = offset*ez
    gmat.col[3] += Vector((x,y,z,0))
    pmat = fkik.getPoseMatrix(gmat, pb)
    fkik.insertLocation(pb, pmat)

#-------------------------------------------------------------
#   Toe below ball
#-------------------------------------------------------------

def toesBelowBall(context):
    scn = context.scene
    rig,plane = getRigAndPlane(scn)
    try:
        useIk = rig["MhaLegIk_L"] or rig["MhaLegIk_R"]
    except KeyError:
        useIk = False
    if useIk:
        raise MocapError("Toe Below Ball only for FK feet")

    layers = list(rig.data.layers)
    startProgress("Keep toes down")
    frames = getActiveFramesBetweenMarkers(rig, scn)
    print("Left toe")
    toeBelowBall(scn, frames, rig, plane, ".L")
    print("Right toe")
    toeBelowBall(scn, frames, rig, plane, ".R")
    endProgress("Toes kept down")
    rig.data.layers = layers


def toeBelowBall(scn, frames, rig, plane, suffix):
    from .retarget import getLocks

    foot,toe,mBall,mToe,mHeel = getFkFeetBones(rig, suffix)
    ez,origin,rot = getPlaneInfo(plane)
    order,lock = getLocks(toe, scn)
    factor = 1.0/toe.length
    nFrames = len(frames)
    if mBall:
        for n,frame in enumerate(frames):
            scn.frame_set(frame)
            showProgress(n, frame, nFrames)
            zToe = getProjection(mToe.matrix.col[3], ez)
            zBall = getProjection(mBall.matrix.col[3], ez)
            if zToe > zBall:
                pmat = offsetToeRotation(toe, ez, factor, order, lock, scn)
            else:
                pmat = fkik.getPoseMatrix(toe.matrix, toe)
            pmat = keepToeRotationNegative(pmat, scn)
            fkik.insertRotation(toe, pmat)
    else:
        for n,frame in enumerate(frames):
            scn.frame_set(frame)
            showProgress(n, frame, nFrames)
            dzToe = getProjection(toe.matrix.col[1], ez)
            if dzToe > 0:
                pmat = offsetToeRotation(toe, ez, factor, order, lock, scn)
            else:
                pmat = fkik.getPoseMatrix(toe.matrix, toe)
            pmat = keepToeRotationNegative(pmat, scn)
            fkik.insertRotation(toe, pmat)


def offsetToeRotation(toe, ez, factor, order, lock, scn):
    from .retarget import correctMatrixForLocks

    mat = toe.matrix.to_3x3()
    y = mat.col[1]
    y -= ez.dot(y)*ez
    y.normalize()
    x = mat.col[0]
    x -= x.dot(y)*y
    x.normalize()
    z = x.cross(y)
    mat.col[0] = x
    mat.col[1] = y
    mat.col[2] = z
    gmat = mat.to_4x4()
    gmat.col[3] = toe.matrix.col[3]
    pmat = fkik.getPoseMatrix(gmat, toe)
    return correctMatrixForLocks(pmat, order, lock, toe, scn.McpUseLimits)


def keepToeRotationNegative(pmat, scn):
    euler = pmat.to_3x3().to_euler('YZX')
    if euler.x > 0:
        pmat0 = pmat
        euler.x = 0
        pmat = euler.to_matrix().to_4x4()
        pmat.col[3] = pmat0.col[3]
    return pmat


class VIEW3D_OT_McpOffsetToeButton(bpy.types.Operator):
    bl_idname = "mcp.offset_toe"
    bl_label = "Offset Toes"
    bl_description = "Keep toes below balls"
    bl_options = {'UNDO'}

    def execute(self, context):
        from .target import getTargetArmature
        getTargetArmature(context.object, context.scene)
        try:
            toesBelowBall(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}


#-------------------------------------------------------------
#   Floor
#-------------------------------------------------------------

def floorFoot(context):
    startProgress("Keep feet above floor")
    scn = context.scene
    rig,plane = getRigAndPlane(scn)
    try:
        useIk = rig["MhaLegIk_L"] or rig["MhaLegIk_R"]
    except KeyError:
        useIk = False
    frames = getActiveFramesBetweenMarkers(rig, scn)
    if useIk:
        floorIkFoot(rig, plane, scn, frames)
    else:
        floorFkFoot(rig, plane, scn, frames)
    endProgress("Feet kept above floor")


def getFkFeetBones(rig, suffix):
    foot = getTrgBone("foot" + suffix, rig)
    toe = getTrgBone("toe" + suffix, rig)
    try:
        mBall = rig.pose.bones["ball.marker" + suffix]
        mToe = rig.pose.bones["toe.marker" + suffix]
        mHeel = rig.pose.bones["heel.marker" + suffix]
    except KeyError:
        mBall = mToe = mHeel = None
    return foot,toe,mBall,mToe,mHeel


def floorFkFoot(rig, plane, scn, frames):
    hips = getTrgBone("hips", rig)
    lFoot,lToe,lmBall,lmToe,lmHeel = getFkFeetBones(rig, ".L")
    rFoot,rToe,rmBall,rmToe,rmHeel = getFkFeetBones(rig, ".R")
    ez,origin,rot = getPlaneInfo(plane)

    nFrames = len(frames)
    for n,frame in enumerate(frames):
        scn.frame_set(frame)
        fkik.updateScene()
        offset = 0
        if scn.McpFloorLeft:
            offset = getFkOffset(rig, ez, origin, lFoot, lToe, lmBall, lmToe, lmHeel)
        if scn.McpFloorRight:
            rOffset = getFkOffset(rig, ez, origin, rFoot, rToe, rmBall, rmToe, rmHeel)
            if rOffset > offset:
                offset = rOffset
        showProgress(n, frame, nFrames)
        if offset > 0:
            addOffset(hips, offset, ez)


def getFkOffset(rig, ez, origin, foot, toe, mBall, mToe, mHeel):
    if mBall:
        offset = toeOffset = getHeadOffset(mToe, ez, origin)
        ballOffset = getHeadOffset(mBall, ez, origin)
        if ballOffset > offset:
            offset = ballOffset
        heelOffset = getHeadOffset(mHeel, ez, origin)
        if heelOffset > offset:
            offset = heelOffset
    elif toe:
        offset = getTailOffset(toe, ez, origin)
        ballOffset = getHeadOffset(toe, ez, origin)
        if ballOffset > offset:
            offset = ballOffset
        ball = toe.matrix.col[3]
        y = toe.matrix.col[1]
        heel = ball - y*foot.length
        heelOffset = getOffset(heel, ez, origin)
        if heelOffset > offset:
            offset = heelOffset
    else:
        offset = 0

    return offset


def floorIkFoot(rig, plane, scn, frames):
    root = rig.pose.bones["root"]
    lleg = rig.pose.bones["foot.ik.L"]
    rleg = rig.pose.bones["foot.ik.R"]
    ez,origin,rot = getPlaneInfo(plane)

    fillKeyFrames(lleg, rig, frames, 3, mode='location')
    fillKeyFrames(rleg, rig, frames, 3, mode='location')
    if scn.McpFloorHips:
        fillKeyFrames(root, rig, frames, 3, mode='location')

    nFrames = len(frames)
    for n,frame in enumerate(frames):
        scn.frame_set(frame)
        showProgress(n, frame, nFrames)

        if scn.McpFloorLeft:
            lOffset = getIkOffset(rig, ez, origin, lleg)
            if lOffset > 0:
                addOffset(lleg, lOffset, ez)
        else:
            lOffset = 0
        if scn.McpFloorRight:
            rOffset = getIkOffset(rig, ez, origin, rleg)
            if rOffset > 0:
                addOffset(rleg, rOffset, ez)
        else:
            rOffset = 0

        hOffset = min(lOffset,rOffset)
        if hOffset > 0 and scn.McpFloorHips:
            addOffset(root, hOffset, ez)


def getIkOffset(rig, ez, origin, leg):
    offset = getHeadOffset(leg, ez, origin)
    tailOffset = getTailOffset(leg, ez, origin)
    if tailOffset > offset:
        offset = tailOffset
    return offset


    foot = rig.pose.bones["foot.rev" + suffix]
    toe = rig.pose.bones["toe.rev" + suffix]


    ballOffset = getTailOffset(toe, ez, origin)
    if ballOffset > offset:
        offset = ballOffset

    ball = foot.matrix.col[3]
    y = toe.matrix.col[1]
    heel = ball + y*foot.length
    heelOffset = getOffset(heel, ez, origin)
    if heelOffset > offset:
        offset = heelOffset

    return offset


class VIEW3D_OT_McpFloorFootButton(bpy.types.Operator):
    bl_idname = "mcp.floor_foot"
    bl_label = "Keep Feet Above Floor"
    bl_description = "Keep Feet Above Plane"
    bl_options = {'UNDO'}

    def execute(self, context):
        from .target import getTargetArmature
        getTargetArmature(context.object, context.scene)
        try:
            floorFoot(context)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

