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



import bpy, os, mathutils, math, time
from math import sin, cos
from mathutils import *
from bpy_extras.io_utils import ImportHelper
from bpy.props import *

from . import props
from . import simplify
from .utils import *

###################################################################################
#    BVH importer.
#    The importer that comes with Blender had memory leaks which led to instability.
#    It also creates a weird skeleton from CMU data, with hands theat start at the wrist
#    and ends at the elbow.
#

#
#    class CNode:
#

class CNode:
    def __init__(self, words, parent):
        name = words[1]
        for word in words[2:]:
            name += ' '+word

        self.name = name
        self.parent = parent
        self.children = []
        self.head = Vector((0,0,0))
        self.offset = Vector((0,0,0))
        if parent:
            parent.children.append(self)
        self.channels = []
        self.matrix = None
        self.inverse = None
        return

    def __repr__(self):
        return "CNode %s" % (self.name)

    def display(self, pad):
        vec = self.offset
        if vec.length < Epsilon:
            c = '*'
        else:
            c = ' '
        print("%s%s%10s (%8.3f %8.3f %8.3f)" % (c, pad, self.name, vec[0], vec[1], vec[2]))
        for child in self.children:
            child.display(pad+"  ")
        return

    def build(self, amt, orig, parent):
        self.head = orig + self.offset
        if not self.children:
            return self.head

        zero = (self.offset.length < Epsilon)
        eb = amt.edit_bones.new(self.name)
        if parent:
            eb.parent = parent
        eb.head = self.head
        tails = Vector((0,0,0))
        for child in self.children:
            tails += child.build(amt, self.head, eb)
        n = len(self.children)
        eb.tail = tails/n
        #self.matrix = eb.matrix.rotation_part()
        (loc, rot, scale) = eb.matrix.decompose()
        self.matrix = rot.to_matrix()
        self.inverse = self.matrix.copy()
        self.inverse.invert()
        if zero:
            return eb.tail
        else:
            return eb.head

#
#    readBvhFile(context, filepath, scn, scan):
#    Custom importer
#

Location = 1
Rotation = 2
Hierarchy = 1
Motion = 2
Frames = 3

Epsilon = 1e-5

def readBvhFile(context, filepath, scn, scan):
    props.ensureInited(context)
    setCategory("Load Bvh File")
    scale = scn.McpBvhScale
    startFrame = scn.McpStartFrame
    endFrame = scn.McpEndFrame
    frameno = 1
    if scn.McpFlipYAxis:
        flipMatrix = Matrix.Rotation(math.pi, 3, 'X') * Matrix.Rotation(math.pi, 3, 'Y')
    else:
        flipMatrix = Matrix.Rotation(0, 3, 'X')
    if True or scn.McpRot90Anim:
        flipMatrix = Matrix.Rotation(math.pi/2, 3, 'X') * flipMatrix
    if (scn.McpSubsample):
        ssFactor = scn.McpSSFactor
    else:
        ssFactor = 1
    defaultSS = scn.McpDefaultSS

    fileName = os.path.realpath(os.path.expanduser(filepath))
    (shortName, ext) = os.path.splitext(fileName)
    if ext.lower() != ".bvh":
        raise MocapError("Not a bvh file: " + fileName)
    startProgress( "Loading BVH file "+ fileName )

    time1 = time.clock()
    level = 0
    nErrors = 0
    scn = context.scene
    rig = None

    fp = open(fileName, "rU")
    print( "Reading skeleton" )
    lineNo = 0
    for line in fp:
        words= line.split()
        lineNo += 1
        if len(words) == 0:
            continue
        key = words[0].upper()
        if key == 'HIERARCHY':
            status = Hierarchy
            ended = False
        elif key == 'MOTION':
            if level != 0:
                raise MocapError("Tokenizer out of kilter %d" % level)
            if scan:
                return root
            amt = bpy.data.armatures.new("BvhAmt")
            rig = bpy.data.objects.new("BvhRig", amt)
            scn.objects.link(rig)
            reallySelect(rig, scn)
            scn.update()
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.mode_set(mode='EDIT')
            root.build(amt, Vector((0,0,0)), None)
            #root.display('')
            bpy.ops.object.mode_set(mode='OBJECT')
            status = Motion
            print("Reading motion")
        elif status == Hierarchy:
            if key == 'ROOT':
                node = CNode(words, None)
                root = node
                nodes = [root]
            elif key == 'JOINT':
                node = CNode(words, node)
                nodes.append(node)
                ended = False
            elif key == 'OFFSET':
                (x,y,z) = (float(words[1]), float(words[2]), float(words[3]))
                node.offset = scale * flipMatrix * Vector((x,y,z))
            elif key == 'END':
                node = CNode(words, node)
                ended = True
            elif key == 'CHANNELS':
                oldmode = None
                for word in words[2:]:
                    (index, mode, sign) = channelYup(word)
                    if mode != oldmode:
                        indices = []
                        node.channels.append((mode, indices))
                        oldmode = mode
                    indices.append((index, sign))
            elif key == '{':
                level += 1
            elif key == '}':
                if not ended:
                    node = CNode(["End", "Site"], node)
                    node.offset = scale * flipMatrix * Vector((0,1,0))
                    node = node.parent
                    ended = True
                level -= 1
                node = node.parent
            else:
                raise MocapError("Did not expect %s" % words[0])
        elif status == Motion:
            if key == 'FRAMES:':
                nFrames = int(words[1])
            elif key == 'FRAME' and words[1].upper() == 'TIME:':
                frameTime = float(words[2])
                frameFactor = int(1.0/(scn.render.fps*frameTime) + 0.49)
                if defaultSS:
                    ssFactor = frameFactor if frameFactor > 0 else 1
                startFrame *= ssFactor
                endFrame *= ssFactor
                status = Frames
                frame = 0
                frameno = 1

                #source.findSrcArmature(context, rig)
                bpy.ops.object.mode_set(mode='POSE')
                pbones = rig.pose.bones
                for pb in pbones:
                    pb.rotation_mode = 'QUATERNION'
        elif status == Frames:
            if (frame >= startFrame and
                frame <= endFrame and
                frame % ssFactor == 0 and
                frame < nFrames):
                addFrame(words, frameno, nodes, pbones, scale, flipMatrix)
                showProgress(frameno, frame, nFrames, step=200)
                frameno += 1
            frame += 1

    fp.close()
    if not rig:
        raise MocapError("Bvh file \n%s\n is corrupt: No rig defined" % filepath)
    setInterpolation(rig)
    time2 = time.clock()
    endProgress("Bvh file %s loaded in %.3f s" % (filepath, time2-time1))
    if frameno == 1:
        print("Warning: No frames in range %d -- %d." % (startFrame, endFrame))
    renameBvhRig(rig, filepath)
    rig.McpIsSourceRig = True
    clearCategory()
    return rig

#
#    addFrame(words, frame, nodes, pbones, scale, flipMatrix):
#

def addFrame(words, frame, nodes, pbones, scale, flipMatrix):
    m = 0
    first = True
    flipInv = flipMatrix.inverted()
    for node in nodes:
        name = node.name
        try:
            pb = pbones[name]
        except:
            pb = None
        if pb:
            for (mode, indices) in node.channels:
                if mode == Location:
                    vec = Vector((0,0,0))
                    for (index, sign) in indices:
                        vec[index] = sign*float(words[m])
                        m += 1
                    if first:
                        pb.location = node.inverse * (scale * flipMatrix * vec - node.head)
                        pb.keyframe_insert('location', frame=frame, group=name)
                    first = False
                elif mode == Rotation:
                    mats = []
                    for (axis, sign) in indices:
                        angle = sign*float(words[m])*Deg2Rad
                        mats.append(Matrix.Rotation(angle, 3, axis))
                        m += 1
                    mat = node.inverse * flipMatrix *mats[0] * mats[1] * mats[2] * flipInv * node.matrix
                    setRotation(pb, mat, frame, name)

    return

#
#    channelYup(word):
#    channelZup(word):
#

def channelYup(word):
    if word == 'Xrotation':
        return ('X', Rotation, +1)
    elif word == 'Yrotation':
        return ('Y', Rotation, +1)
    elif word == 'Zrotation':
        return ('Z', Rotation, +1)
    elif word == 'Xposition':
        return (0, Location, +1)
    elif word == 'Yposition':
        return (1, Location, +1)
    elif word == 'Zposition':
        return (2, Location, +1)

def channelZup(word):
    if word == 'Xrotation':
        return ('X', Rotation, +1)
    elif word == 'Yrotation':
        return ('Z', Rotation, +1)
    elif word == 'Zrotation':
        return ('Y', Rotation, -1)
    elif word == 'Xposition':
        return (0, Location, +1)
    elif word == 'Yposition':
        return (2, Location, +1)
    elif word == 'Zposition':
        return (1, Location, -1)

#
#   end BVH importer
#
###################################################################################


###################################################################################

#
#    class CEditBone():
#

class CEditBone():
    def __init__(self, bone):
        self.name = bone.name
        self.head = bone.head.copy()
        self.tail = bone.tail.copy()
        self.roll = bone.roll
        if bone.parent:
            self.parent = bone.parent.name
        else:
            self.parent = None
        if self.parent:
            self.use_connect = bone.use_connect
        else:
            self.use_connect = False
        #self.matrix = bone.matrix.copy().rotation_part()
        (loc, rot, scale) = bone.matrix.decompose()
        self.matrix = rot.to_matrix()
        self.inverse = self.matrix.copy()
        self.inverse.invert()

    def __repr__(self):
        return ("%s p %s\n  h %s\n  t %s\n" % (self.name, self.parent, self.head, self.tail))

#
#    renameBones(srcRig, scn):
#

def renameBones(srcRig, scn):
    from .source import getSourceBoneName

    srcBones = []
    trgBones = {}

    reallySelect(srcRig, scn)
    scn.update()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='EDIT')
    #print("Ren", bpy.context.object, srcRig.mode)
    ebones = srcRig.data.edit_bones
    for bone in ebones:
        srcBones.append( CEditBone(bone) )

    setbones = []
    adata = srcRig.animation_data
    if adata is None:
        action = None
    else:
        action = adata.action
    for srcBone in srcBones:
        srcName = srcBone.name
        trgName = getSourceBoneName(srcName)
        if isinstance(trgName, tuple):
            print("BUG. Target name is tuple:", trgName)
            trgName = trgName[0]
        eb = ebones[srcName]
        if trgName:
            if action:
                grp = action.groups[srcName]
                grp.name = trgName
            eb.name = trgName
            trgBones[trgName] = CEditBone(eb)
            setbones.append((eb, trgName))
        else:
            eb.name = '_' + srcName

    for (eb, name) in setbones:
        eb.name = name
    #createExtraBones(ebones, trgBones)
    bpy.ops.object.mode_set(mode='POSE')

#
#    renameBvhRig(srcRig, filepath):
#

def renameBvhRig(srcRig, filepath):
    base = os.path.basename(filepath)
    (filename, ext) = os.path.splitext(base)
    print("File", filename, len(filename))
    if len(filename) > 12:
        words = filename.split('_')
        if len(words) == 1:
            words = filename.split('-')
        name = 'Y_'
        if len(words) > 1:
            words = words[1:]
        for word in words:
            name += word
    else:
        name = 'Y_' + filename
    print("Name", name)

    srcRig.name = name
    adata = srcRig.animation_data
    if adata:
        adata.action.name = name
    return

#
#    deleteSourceRig(context, rig, prefix):
#

def deleteSourceRig(context, rig, prefix):
    ob = context.object
    scn = context.scene
    reallySelect(rig, scn)
    bpy.ops.object.mode_set(mode='OBJECT')
    reallySelect(ob, scn)
    scn.objects.unlink(rig)
    if rig.users == 0:
        bpy.data.objects.remove(rig)
    if bpy.data.actions:
        for act in bpy.data.actions:
            if act.name[0:2] == prefix:
                act.use_fake_user = False
                if act.users == 0:
                    bpy.data.actions.remove(act)
                    del act
    return


#
#    rescaleRig(scn, trgRig, srcRig):
#

def rescaleRig(scn, trgRig, srcRig):
    if not scn.McpAutoScale:
        return
    if isDefaultRig(trgRig):
        upleg1 = trgRig.data.bones["upperleg01.L"]
        upleg2 = trgRig.data.bones["upperleg02.L"]
        trgScale = upleg1.length + upleg2.length
    else:
        upleg = getTrgBone('thigh.L', trgRig)
        trgScale = upleg.length
    srcScale = srcRig.data.bones['thigh.L'].length
    scale = trgScale/srcScale
    print("Rescale %s with factor %f" % (srcRig.name, scale))
    scn.McpBvhScale = scale

    bpy.ops.object.mode_set(mode='EDIT')
    ebones = srcRig.data.edit_bones
    for eb in ebones:
        oldlen = eb.length
        eb.head *= scale
        eb.tail *= scale
    bpy.ops.object.mode_set(mode='POSE')
    adata = srcRig.animation_data
    if adata is None:
        return
    for fcu in adata.action.fcurves:
        words = fcu.data_path.split('.')
        if words[-1] == 'location':
            for kp in fcu.keyframe_points:
                kp.co[1] *= scale
    return


#
#    renameAndRescaleBvh(context, srcRig, trgRig):
#

def renameAndRescaleBvh(context, srcRig, trgRig):
    from . import source, target
    setCategory("Rename And Rescale")
    try:
        if srcRig["McpRenamed"]:
            raise MocapError("%s already renamed and rescaled." % srcRig.name)
    except:
        pass

    from . import t_pose
    scn = context.scene
    reallySelect(srcRig, scn)
    scn.update()
    #(srcRig, srcBones, action) =  renameBvhRig(rig, filepath)
    target.getTargetArmature(trgRig, scn)
    source.findSrcArmature(context, srcRig)
    t_pose.addTPoseAtFrame0(srcRig, scn)
    renameBones(srcRig, scn)
    setInterpolation(srcRig)
    rescaleRig(context.scene, trgRig, srcRig)
    srcRig["McpRenamed"] = True
    clearCategory()

########################################################################
#
#   class VIEW3D_OT_LoadBvhButton(bpy.types.Operator, ImportHelper):
#

class VIEW3D_OT_LoadBvhButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mcp.load_bvh"
    bl_label = "Load BVH File (.bvh)"
    bl_description = "Load an armature from a bvh file"
    bl_options = {'UNDO'}

    filename_ext = ".bvh"
    filter_glob = StringProperty(default="*.bvh", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for importing the BVH file", maxlen=1024, default="")

    def execute(self, context):
        try:
            readBvhFile(context, self.properties.filepath, context.scene, False)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#
#   class VIEW3D_OT_RenameBvhButton(bpy.types.Operator):
#

class VIEW3D_OT_RenameBvhButton(bpy.types.Operator):
    bl_idname = "mcp.rename_bvh"
    bl_label = "Rename And Rescale BVH Rig"
    bl_description = "Rename bones of active armature and scale it to fit other armature"
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = context.scene
        srcRig = context.object
        trgRig = None
        for ob in scn.objects:
            if ob.type == 'ARMATURE' and ob.select and ob != srcRig:
                trgRig = ob
                break
        try:
            if not trgRig:
                raise MocapError("No target rig selected")
            renameAndRescaleBvh(context, srcRig, trgRig)
            if scn.McpRescale:
                simplify.rescaleFCurves(context, srcRig, scn.McpRescaleFactor)
            print("%s renamed" % srcRig.name)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        return{'FINISHED'}

#
#   class VIEW3D_OT_LoadAndRenameBvhButton(bpy.types.Operator, ImportHelper):
#

class VIEW3D_OT_LoadAndRenameBvhButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mcp.load_and_rename_bvh"
    bl_label = "Load And Rename BVH File (.bvh)"
    bl_description = "Load armature from bvh file and rename bones"
    bl_options = {'UNDO'}

    problems = ""
    filename_ext = ".bvh"
    filter_glob = StringProperty(default="*.bvh", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="Filepath used for importing the BVH file", maxlen=1024, default="")

    def execute(self, context):
        from .retarget import changeTargetData, restoreTargetData
        if self.problems:
            return{'FINISHED'}

        scn = context.scene
        trgRig = context.object
        data = changeTargetData(trgRig, scn)
        try:
            srcRig = readBvhFile(context, self.properties.filepath, context.scene, False)
            renameAndRescaleBvh(context, srcRig, trgRig)
            if scn.McpRescale:
                simplify.rescaleFCurves(context, srcRig, scn.McpRescaleFactor)
            print("%s loaded and renamed" % srcRig.name)
        except MocapError:
            bpy.ops.mcp.error('INVOKE_DEFAULT')
        finally:
            restoreTargetData(trgRig, data)
        return{'FINISHED'}

    def invoke(self, context, event):
        return problemFreeFileSelect(self, context)

    def draw(self, context):
        drawObjectProblems(self)
