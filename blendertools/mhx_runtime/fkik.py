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
from bpy.props import StringProperty
from mathutils import *

#########################################
#
#   FK-IK snapping.
#
#########################################

def getPoseMatrix(gmat, pb):
    restInv = pb.bone.matrix_local.inverted()
    if pb.parent:
        parInv = pb.parent.matrix.inverted()
        parRest = pb.parent.bone.matrix_local
        return restInv * (parRest * (parInv * gmat))
    else:
        return restInv * gmat


def getGlobalMatrix(mat, pb):
    gmat = pb.bone.matrix_local * mat
    if pb.parent:
        parMat = pb.parent.matrix
        parRest = pb.parent.bone.matrix_local
        return parMat * (parRest.inverted() * gmat)
    else:
        return gmat


def matchPoseTranslation(pb, src, auto):
    pmat = getPoseMatrix(src.matrix, pb)
    insertLocation(pb, pmat, auto)


def insertLocation(pb, mat, auto):
    pb.location = mat.to_translation()
    if auto:
        pb.keyframe_insert("location", group=pb.name)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def matchPoseRotation(pb, src, auto):
    pmat = getPoseMatrix(src.matrix, pb)
    insertRotation(pb, pmat, auto)


def printMatrix(string,mat):
    print(string)
    for i in range(4):
        print("    %.4g %.4g %.4g %.4g" % tuple(mat[i]))


def insertRotation(pb, mat, auto):
    q = mat.to_quaternion()
    if pb.rotation_mode == 'QUATERNION':
        pb.rotation_quaternion = q
        if auto:
            pb.keyframe_insert("rotation_quaternion", group=pb.name)
    else:
        pb.rotation_euler = q.to_euler(pb.rotation_mode)
        if auto:
            pb.keyframe_insert("rotation_euler", group=pb.name)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def matchPoseTwist(pb, src, auto):
    pmat0 = src.matrix_basis
    euler = pmat0.to_3x3().to_euler('YZX')
    euler.z = 0
    pmat = euler.to_matrix().to_4x4()
    pmat.col[3] = pmat0.col[3]
    insertRotation(pb, pmat, auto)


def matchIkLeg(legIk, toeFk, mBall, mToe, mHeel, auto):
    rmat = toeFk.matrix.to_3x3()
    tHead = Vector(toeFk.matrix.col[3][:3])
    ty = rmat.col[1]
    tail = tHead + ty * toeFk.bone.length

    try:
        zBall = mBall.matrix.col[3][2]
    except AttributeError:
        return
    zToe = mToe.matrix.col[3][2]
    zHeel = mHeel.matrix.col[3][2]

    x = Vector(rmat.col[0])
    y = Vector(rmat.col[1])
    z = Vector(rmat.col[2])

    if zHeel > zBall and zHeel > zToe:
        # 1. foot.ik is flat
        if abs(y[2]) > abs(z[2]):
            y = -z
        y[2] = 0
    else:
        # 2. foot.ik starts at heel
        hHead = Vector(mHeel.matrix.col[3][:3])
        y = tail - hHead

    y.normalize()
    x -= x.dot(y)*y
    x.normalize()
    z = x.cross(y)
    head = tail - y * legIk.bone.length

    # Create matrix
    gmat = Matrix()
    gmat.col[0][:3] = x
    gmat.col[1][:3] = y
    gmat.col[2][:3] = z
    gmat.col[3][:3] = head
    pmat = getPoseMatrix(gmat, legIk)

    insertLocation(legIk, pmat, auto)
    insertRotation(legIk, pmat, auto)


def matchPoleTarget(pb, above, below, auto):
    ax,ay,az = above.matrix.to_3x3().to_euler('YZX')
    bx,by,bz = below.matrix.to_3x3().to_euler('YZX')
    x = Vector(above.matrix.col[1][:3])
    y = Vector(below.matrix.col[1][:3])
    p0 = Vector(below.matrix.col[3][:3])
    n = x.cross(y)
    if abs(n.length) > 1e-4:
        z = x - y
        n = n/n.length
        z -= z.dot(n)*n
        z = z/z.length
        p = p0 + 6*pb.bone.length*z
    else:
        p = p0
    gmat = Matrix.Translation(p)
    pmat = getPoseMatrix(gmat, pb)
    insertLocation(pb, pmat, auto)


def matchPoseReverse(pb, src, auto):
    gmat = src.matrix
    tail = gmat.col[3] + src.length * gmat.col[1]
    rmat = Matrix((gmat.col[0], -gmat.col[1], -gmat.col[2], tail))
    rmat.transpose()
    pmat = getPoseMatrix(rmat, pb)
    pb.matrix_basis = pmat
    insertRotation(pb, pmat, auto)


def matchPoseScale(pb, src, auto):
    pmat = getPoseMatrix(src.matrix, pb)
    pb.scale = pmat.to_scale()
    if auto:
        pb.keyframe_insert("scale", group=pb.name)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def snapFkArm(context, data):
    rig = context.object
    prop,old,suffix = setSnapProp(rig, data, 1.0, context, False)
    auto = context.scene.tool_settings.use_keyframe_insert_auto

    print("Snap FK Arm%s" % suffix)
    snapFk,cnsFk = getSnapBones(rig, "ArmFK", suffix)
    (uparmFk, loarmFk, handFk) = snapFk
    muteConstraints(cnsFk, True)
    snapIk,cnsIk = getSnapBones(rig, "ArmIK", suffix)
    (uparmIk, loarmIk, elbow, elbowPt, handIk) = snapIk

    matchPoseRotation(uparmFk, uparmIk, auto)
    matchPoseScale(uparmFk, uparmIk, auto)

    matchPoseRotation(loarmFk, loarmIk, auto)
    matchPoseScale(loarmFk, loarmIk, auto)

    restoreSnapProp(rig, prop, old, context)

    try:
        matchHand = rig["MhaHandFollowsWrist" + suffix]
    except KeyError:
        matchHand = True
    if matchHand:
        matchPoseRotation(handFk, handIk, auto)
        matchPoseScale(handFk, handIk, auto)

    #muteConstraints(cnsFk, False)
    return


def snapIkArm(context, data):
    rig = context.object
    prop,old,suffix = setSnapProp(rig, data, 0.0, context, True)
    auto = context.scene.tool_settings.use_keyframe_insert_auto

    print("Snap IK Arm%s" % suffix)
    snapIk,cnsIk = getSnapBones(rig, "ArmIK", suffix)
    (uparmIk, loarmIk, elbow, elbowPt, handIk) = snapIk
    snapFk,cnsFk = getSnapBones(rig, "ArmFK", suffix)
    (uparmFk, loarmFk, handFk) = snapFk
    muteConstraints(cnsIk, True)

    matchPoseTranslation(handIk, handFk, auto)
    matchPoseRotation(handIk, handFk, auto)

    matchPoleTarget(elbowPt, uparmFk, loarmFk, auto)

    #matchPoseRotation(uparmIk, uparmFk, auto)
    #matchPoseRotation(loarmIk, loarmFk, auto)

    restoreSnapProp(rig, prop, old, context)
    #muteConstraints(cnsIk, False)
    return


def snapFkLeg(context, data):
    rig = context.object
    prop,old,suffix = setSnapProp(rig, data, 1.0, context, False)
    auto = context.scene.tool_settings.use_keyframe_insert_auto

    print("Snap FK Leg%s" % suffix)
    snap,_ = getSnapBones(rig, "Leg", suffix)
    (upleg, loleg, foot, toe) = snap
    snapIk,cnsIk = getSnapBones(rig, "LegIK", suffix)
    (uplegIk, lolegIk, kneePt, ankleIk, legIk, footRev, toeRev, mBall, mToe, mHeel) = snapIk
    snapFk,cnsFk = getSnapBones(rig, "LegFK", suffix)
    (uplegFk, lolegFk, footFk, toeFk) = snapFk
    muteConstraints(cnsFk, True)

    matchPoseRotation(uplegFk, uplegIk, auto)
    matchPoseScale(uplegFk, uplegIk, auto)

    matchPoseRotation(lolegFk, lolegIk, auto)
    matchPoseScale(lolegFk, lolegIk, auto)

    restoreSnapProp(rig, prop, old, context)

    if not rig["MhaLegIkToAnkle" + suffix]:
        matchPoseReverse(footFk, footRev, auto)
        matchPoseReverse(toeFk, toeRev, auto)

    #muteConstraints(cnsFk, False)
    return


def snapIkLeg(context, data):
    rig = context.object
    scn = context.scene
    prop,old,suffix = setSnapProp(rig, data, 0.0, context, True)
    auto = scn.tool_settings.use_keyframe_insert_auto

    print("Snap IK Leg%s" % suffix)
    snapIk,cnsIk = getSnapBones(rig, "LegIK", suffix)
    (uplegIk, lolegIk, kneePt, ankleIk, legIk, footRev, toeRev, mBall, mToe, mHeel) = snapIk
    snapFk,cnsFk = getSnapBones(rig, "LegFK", suffix)
    (uplegFk, lolegFk, footFk, toeFk) = snapFk
    muteConstraints(cnsIk, True)

    legIkToAnkle = rig["MhaLegIkToAnkle" + suffix]
    if legIkToAnkle:
        matchPoseTranslation(ankleIk, footFk, auto)
    else:
        matchIkLeg(legIk, toeFk, mBall, mToe, mHeel, auto)

    matchPoseReverse(toeRev, toeFk, auto)
    matchPoseReverse(footRev, footFk, auto)

    matchPoleTarget(kneePt, uplegFk, lolegFk, auto)

    matchPoseTwist(lolegIk, lolegFk, auto)

    if not legIkToAnkle:
        matchPoseTranslation(ankleIk, footFk, auto)

    restoreSnapProp(rig, prop, old, context)
    #muteConstraints(cnsIk, False)
    return


SnapBonesAlpha8 = {
    "Arm"   : ["upper_arm", "forearm", "hand"],
    "ArmFK" : ["upper_arm.fk", "forearm.fk", "hand.fk"],
    "ArmIK" : ["upper_arm.ik", "forearm.ik", None, "elbow.pt.ik", "hand.ik"],
    "Leg"   : ["thigh", "shin", "foot", "toe"],
    "LegFK" : ["thigh.fk", "shin.fk", "foot.fk", "toe.fk"],
    "LegIK" : ["thigh.ik", "shin.ik", "knee.pt.ik", "ankle.ik", "foot.ik", "foot.rev", "toe.rev", "ball.marker", "toe.marker", "heel.marker"],
}


def getSnapBones(rig, key, suffix):
    try:
        pb = rig.pose.bones["UpLeg_L"]
    except KeyError:
        pb = None

    if pb is not None:
        raise RuntimeError("MakeHuman alpha 7 not supported after Blender 2.68")

    try:
        rig.pose.bones["thigh.fk.L"]
        names = SnapBonesAlpha8[key]
        suffix = '.' + suffix[1:]
    except KeyError:
        names = None

    if not names:
        raise RuntimeError("Not an mhx armature")

    pbones = []
    constraints = []
    for name in names:
        if name:
            try:
                pb = rig.pose.bones[name+suffix]
            except KeyError:
                pb = None
            pbones.append(pb)
            if pb is not None:
                for cns in pb.constraints:
                    if cns.type == 'LIMIT_ROTATION' and not cns.mute:
                        constraints.append(cns)
        else:
            pbones.append(None)
    return tuple(pbones),constraints


def muteConstraints(constraints, value):
    for cns in constraints:
        cns.mute = value


class VIEW3D_OT_MhxSnapFk2IkButton(bpy.types.Operator):
    bl_idname = "mhx.snap_fk_ik"
    bl_label = "Snap FK"
    bl_options = {'UNDO'}
    data = StringProperty()

    def execute(self, context):
        bpy.ops.object.mode_set(mode='POSE')
        rig = context.object
        if rig.MhxSnapExact:
            rig["MhaRotationLimits"] = 0.0
        if self.data[:6] == "MhaArm":
            snapFkArm(context, self.data)
        elif self.data[:6] == "MhaLeg":
            snapFkLeg(context, self.data)
        return{'FINISHED'}


class VIEW3D_OT_MhxSnapIk2FkButton(bpy.types.Operator):
    bl_idname = "mhx.snap_ik_fk"
    bl_label = "Snap IK"
    bl_options = {'UNDO'}
    data = StringProperty()

    def execute(self, context):
        bpy.ops.object.mode_set(mode='POSE')
        rig = context.object
        if rig.MhxSnapExact:
            rig["MhaRotationLimits"] = 0.0
        if self.data[:6] == "MhaArm":
            snapIkArm(context, self.data)
        elif self.data[:6] == "MhaLeg":
            snapIkLeg(context, self.data)
        return{'FINISHED'}


def setSnapProp(rig, data, value, context, isIk):
    words = data.split()
    prop = words[0]
    oldValue = rig[prop]
    rig[prop] = value
    ik = int(words[1])
    fk = int(words[2])
    extra = int(words[3])
    oldIk = rig.data.layers[ik]
    oldFk = rig.data.layers[fk]
    oldExtra = rig.data.layers[extra]
    rig.data.layers[ik] = True
    rig.data.layers[fk] = True
    rig.data.layers[extra] = True
    updatePose(context)
    if isIk:
        oldValue = 1.0
        oldIk = True
        oldFk = False
    else:
        oldValue = 0.0
        oldIk = False
        oldFk = True
        oldExtra = False
    return (prop, (oldValue, ik, fk, extra, oldIk, oldFk, oldExtra), prop[-2:])


def restoreSnapProp(rig, prop, old, context):
    updatePose(context)
    (oldValue, ik, fk, extra, oldIk, oldFk, oldExtra) = old
    rig[prop] = oldValue
    rig.data.layers[ik] = oldIk
    rig.data.layers[fk] = oldFk
    rig.data.layers[extra] = oldExtra
    updatePose(context)
    return


class VIEW3D_OT_MhxToggleFkIkButton(bpy.types.Operator):
    bl_idname = "mhx.toggle_fk_ik"
    bl_label = "FK - IK"
    bl_options = {'UNDO'}
    toggle = StringProperty()

    def execute(self, context):
        words = self.toggle.split()
        rig = context.object
        prop = words[0]
        value = float(words[1])
        onLayer = int(words[2])
        offLayer = int(words[3])
        rig.data.layers[onLayer] = True
        rig.data.layers[offLayer] = False
        rig[prop] = value
        # Don't do autokey - confusing.
        #if context.tool_settings.use_keyframe_insert_auto:
        #    rig.keyframe_insert('["%s"]' % prop, frame=scn.frame_current)
        updatePose(context)
        return{'FINISHED'}

#
#   updatePose(context):
#   class VIEW3D_OT_MhxUpdateButton(bpy.types.Operator):
#

def updatePose(context):
    scn = context.scene
    scn.frame_current = scn.frame_current
    bpy.ops.object.posemode_toggle()
    bpy.ops.object.posemode_toggle()
    return

class VIEW3D_OT_MhxUpdateButton(bpy.types.Operator):
    bl_idname = "mhx.update"
    bl_label = "Update"

    def execute(self, context):
        updatePose(context)
        return{'FINISHED'}


