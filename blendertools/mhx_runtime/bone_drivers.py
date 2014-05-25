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
import json
import bpy
from bpy.props import *
from mathutils import *
from .drivers import *

#------------------------------------------------------------------------
#   Bone drivers
#------------------------------------------------------------------------
'''
def addBoneDrivers(rig, propname, prefix, act):
    # The driving property names are stored in several string properties,
    # since the size of a string property in Blender is limited.
    # Joint them into one string and split it
    nchars = len(propname)
    keys = [ key for key in rig.keys() if key[0:nchars] == propname ]
    keys.sort()
    string = ":".join([rig[key] for key in keys])
    if string == "":
        return
    props = string.split(':')

    # Create the properties that will drive the bones
    initRnaProperties(rig)
    for prop in props:
        pname = prefix+prop
        rig[pname] = 0.0
        rig["_RNA_UI"][pname] = {"min":0.0, "max":1.0}

    # Collect all nonzero keyframes belonging to one bone.
    # The poses are spread out over several f-curves.
    poseTable = {}
    times = {}
    for fcu in act.fcurves:
        channel = fcu.data_path.split(".")[-1]
        idx = fcu.array_index
        if channel == "rotation_quaternion":
            if idx == 0:
                default = 1
            else:
                default = 0
        elif channel == "rotation_euler":
            default = 0
        else:
            continue

        bname = getBoneName(fcu)
        try:
            quats = poseTable[bname]
        except KeyError:
            quats = poseTable[bname] = {}

        for kp in fcu.keyframe_points:
            val = kp.co[1] - default
            if abs(val) > 1e-3:
                t = int(round(kp.co[0]))
                times[t] = True
                try:
                    quat = quats[t]
                except KeyError:
                    quat = quats[t] = Quaternion()
                quat[idx] = kp.co[1]

    # Set up a time -> used keyframe number map
    usedTimes = list(times.keys())
    usedTimes.append(1)
    usedTimes.sort()
    timeMap = {}
    for n,t in enumerate(usedTimes):
        timeMap[t] = n

    # Create drivers for the posebones.
    zeroQuat = ("1", "0", "0", "0")
    for bname,quats in poseTable.items():
        data = [[], [], [], []]
        for t,quat in quats.items():
            n = timeMap[t]
            for idx in range(1,4):
                if abs(quat[idx]) > 1e-4:
                    data[idx].append((prefix+props[n], quat[idx]))
        try:
            pb = rig.pose.bones[bname]
        except KeyError:
            pb = None
            print("Warning: Bone %s missing" % bname)
        if pb:
            addDrivers(rig, pb, "rotation_quaternion", data, zeroQuat)


class VIEW3D_OT_AddFaceRigDriverButton(bpy.types.Operator):
    bl_idname = "mhx.add_facerig_drivers"
    bl_label = "Add Facerig Drivers"
    bl_description = "Control face rig with rig properties."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and
                rig.animation_data and
                rig.animation_data.action and
                rig.type == 'ARMATURE'
               )

    def execute(self, context):
        rig = context.object
        act = rig.animation_data.action
        addBoneDrivers(rig, "MhxFaceShapeNames", "Mfa", act)
        rig.animation_data.action = None
        rig.MhxFaceRigDrivers = True
        return{'FINISHED'}
'''

#------------------------------------------------------------------------
#   Bone drivers
#------------------------------------------------------------------------

def getStruct(filename, struct):
    from collections import OrderedDict
    if struct is None:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        struct = json.load(open(filepath, 'rU'), object_pairs_hook=OrderedDict)
    return struct


_FacePoses = None

def getFacePoses():
    global _FacePoses
    _FacePoses = getStruct("data/face-poses.json", _FacePoses)
    return _FacePoses


def addBoneDrivers(rig, prefix, struct):
    initRnaProperties(rig)
    for prop in struct["poses"].keys():
        pname = prefix+prop
        rig[pname] = 0.0
        rig["_RNA_UI"][pname] = {"min":0.0, "max":1.0}

    bdrivers = {}
    for pose,bones in struct["poses"].items():
        for bname,quat in bones.items():
            try:
                bdriver = bdrivers[bname]
            except KeyError:
                bdriver = bdrivers[bname] = [[],[],[],[]]
            for n in range(4):
                bdriver[n].append((prefix+pose, quat[n]))

    zeroQuat = ("1", "0", "0", "0")
    for bname,data in bdrivers.items():
        try:
            pb = rig.pose.bones[bname]
        except KeyError:
            pb = None
        if pb is None:
            bname = bname.replace(".","_")
            try:
                pb = rig.pose.bones[bname]
            except KeyError:
                print("Warning: Bone %s missing" % bname)
        if pb:
            addDrivers(rig, pb, "rotation_quaternion", data, zeroQuat)


class VIEW3D_OT_AddFaceRigDriverButton(bpy.types.Operator):
    bl_idname = "mhx.add_facerig_drivers"
    bl_label = "Add Facerig Drivers"
    bl_description = "Control face rig with rig properties."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and
                rig.type == 'ARMATURE'
               )

    def execute(self, context):
        global _FacePoses
        rig = context.object
        addBoneDrivers(rig, "Mfa", getFacePoses())
        rig.MhxFaceRigDrivers = True
        return{'FINISHED'}

