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
import math
import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper
from mathutils import Euler
from .error import *

#------------------------------------------------------------------------
#    Quick and dirty BVH load.
#------------------------------------------------------------------------

def faceshiftBvhLoad(filepath, useHead):
    readingBlendShapes = False
    readingMotion = False
    props = {}
    bones = {}
    pmotion = {}
    bmotion = {}
    idx = 0
    R = math.pi/180
    with open(filepath) as fp:
        for line in fp:
            words = line.split()
            if len(words) == 0:
                continue
            elif readingMotion:
                for idx,bone in bones.items():
                    angles = [float(words[idx+n])*R for n in range(3,6)]
                    euler = Euler(angles, 'ZXY')
                    bmotion[bone].append(euler)
                for idx,prop in props.items():
                    strength = float(words[idx+5])/90.0
                    pmotion[prop].append(strength)
            else:
                key = words[0]
                if key == "JOINT":
                    joint = words[1]
                    idx += 6
                    if readingBlendShapes:
                        try:
                            prop = "Mfa%s" % FaceShiftShapes[joint]
                        except KeyError:
                            raise MHXError("Unknown Blendshape %s.\nThis is not a FaceShift BVH file" % joint)
                        props[idx] = prop
                        pmotion[prop] = []
                    elif joint == "Blendshapes":
                        readingBlendShapes = True
                    elif useHead:
                        try:
                            bone = FaceShiftBones[joint]
                        except KeyError:
                            bone = None
                        if bone:
                            bones[idx] = bone
                            bmotion[bone] = []
                elif key == "MOTION":
                    if not readingBlendShapes:
                        raise MHXError("This is not a FaceShift BVH file")
                    readingBlendShapes = False
                elif key == "Frame":
                    readingMotion = True

    return bmotion,pmotion

#------------------------------------------------------------------------
#    Faceshift translation table
#------------------------------------------------------------------------

FaceShiftBones = {
    "Neck" : "neck",
    "eye_left" : "eye.L",
    "eye_right" : "eye.R",
}

FaceShiftShapes = {
 "neutral" :    "Neutral",
 "BrowsD_L" :   "LeftBrowDown",
 "BrowsD_R" :   "RightBrowDown",
 "BrowsU_C" :   "BrowsUp",
 "BrowsU_L" :   "LeftBrowUp",
 "BrowsU_R" :   "RightBrowUp",
 "CheekSquint_L" :      "LeftCheekUp",
 "CheekSquint_R" :      "RightCheekUp",
 "ChinLowerRaise" :     "ChinUp",
 "ChinUpperRaise" :     "UpperLipUp3",
 "EyeBlink_L" :     "LeftEyeClose",
 "EyeBlink_R" :     "RightEyeClose",
 "EyeDown_L" :      "LeftEyeDown",
 "EyeDown_R" :      "RightEyeDown",
 "EyeIn_L" :    "LeftEyeIn",
 "EyeIn_R" :    "RightEyeIn",
 "EyeOpen_L" :      "LeftEyeOpen",
 "EyeOpen_R" :      "RightEyeOpen",
 "EyeOut_L" :      "LeftEyeOut",
 "EyeOut_R" :   "RightEyeOut",
 "EyeSquint_L" :    "LeftEyeLowerUp",
 "EyeSquint_R" :    "RightEyeLowerUp",
 "EyeUp_L" :    "LeftEyeUp",
 "EyeUp_R" :    "RightEyeUp",
 "JawChew" :    "JawClosedOffset",
 "JawFwd" :     "JawMoveForward",
 "JawLeft" :    "JawMoveLeft",
 "JawRight" :   "JawMoveRight",
 "JawOpen" :    "JawOpen",
 "LipsFunnel" :     "LipsOpenKiss",
 "LipsLowerClose" :     "LowerLipsUp",
 "LipsLowerDown" :      "LowerLipsDown",
 "LipsLowerOpen" :      "LowerLipsDown2",
 "LipsPucker" :     "LipsKiss",
 "LipsStretch_L" :      "MouthLeftSmile",
 "LipsStretch_R" :      "MouthRightSmile",
 "LipsUpperClose" :     "UpperLipDown",
 "LipsUpperOpen" :      "UpperLipUp",
 "LipsUpperUp" :    "UpperLipUp2",
 "MouthDimple_L" :      "MouthLeftSmile2",
 "MouthDimple_R" :      "MouthRightSmile2",
 "MouthFrown_L" :   "MouthLeftFrown",
 "MouthFrown_R" :   "MouthRightFrown",
 "MouthLeft" :      "MouthMoveLeft",
 "MouthRight" :     "MouthMoveRight",
 "MouthSmile_L" :   "MouthLeftSmile3",
 "MouthSmile_R" :   "MouthRightSmile3",
 "Puff" :   "CheeksPump",
 "Sneer" :      "FaceTension",
}

#------------------------------------------------------------------------
#    Assign motion to rig properties and bones
#------------------------------------------------------------------------

def assignMotion(context, motion):
    rig = context.object
    if (rig.animation_data and rig.animation_data.action):
        rig.animation_data.action = None

    bmotion,pmotion = motion
    for bname in bmotion.keys():
        pb = rig.pose.bones[bname]
        pb.keyframe_insert(data_path="rotation_quaternion", frame=1)

    for prop in pmotion.keys():
        path = '["%s"]' % prop
        rig.keyframe_insert(data_path=path, frame=1)

    bcurves = {}
    for fcu in rig.animation_data.action.fcurves:
        words = fcu.data_path.split('"')
        if words[0] == "pose.bones[":
            bone = words[1]
            try:
                fcus = bcurves[bone]
            except KeyError:
                fcus = bcurves[bone] = {}
            fcus[fcu.array_index] = fcu
        else:
            addKeyPoints(fcu, pmotion[words[1]])

    for bname,fcus in bcurves.items():
        quats = [euler.to_quaternion() for euler in bmotion[bname]]
        for n in range(4):
            points = [quat[n] for quat in quats]
            addKeyPoints(fcus[n], points)


def addKeyPoints(fcu, points):
    points = list(points)
    nFrames = len(points)
    fcu.keyframe_points.add(nFrames-1)
    for n,val in enumerate(points):
        kp = fcu.keyframe_points[n]
        kp.co = (n+1, val)

#------------------------------------------------------------------------
#    Button
#------------------------------------------------------------------------

class VIEW3D_OT_LoadFaceshiftBvhButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mhx.load_faceshift_bvh"
    bl_label = "Load FaceShift BVH File (.bvh)"
    bl_description = "Load facesthift from a bvh file"
    bl_options = {'UNDO'}

    filename_ext = ".bvh"
    filter_glob = StringProperty(default="*.bvh", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for importing the BVH file", maxlen=1024, default="")

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and rig.MhxFaceRigDrivers)

    useHead = BoolProperty(name="Head animation", description="Include head and eye movements", default=True)

    def draw(self, context):
        self.layout.prop(self, "useHead")

    def execute(self, context):
        try:
            motion = faceshiftBvhLoad(self.properties.filepath, self.useHead)
            assignMotion(context, motion)
            print("Faceshift file %s loaded." % self.properties.filepath)
        except MHXError:
            handleMHXError(context)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
