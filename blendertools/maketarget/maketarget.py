#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Abstract
--------

The MakeHuman application uses predefined morph target files to distort
the humanoid model when physiological changes or changes to the pose are
applied by the user. The morph target files contain extreme mesh
deformations for individual joints and features which can used
proportionately to apply less extreme deformations and which can be
combined to provide a very wide range of options to the user of the
application.

This module contains a set of functions used by 3d artists during the
development cycle to create these extreme morph target files from
hand-crafted models.

"""

import bpy
import os
import sys
import math
import random
from mathutils import Vector, Quaternion, Matrix
from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper

from . import mh
from .error import MHError, handleMHError
from . import utils
from .utils import round, setObjectMode, invokeWithFileCheck, drawFileCheck, getMHBlenderDirectory
from . import import_obj
from .proxy import CProxy
from .symmetry_map import *

Epsilon = 1e-4
Comments = []

#----------------------------------------------------------
#   Settings
#----------------------------------------------------------

from . import mt

def setSettings(context):
    ob = context.object
    if len(ob.data.vertices) == mt.settings["alpha7"].nTotalVerts:
        print("Alpha 7 mesh detected")
        ob.MhMeshVersion = "alpha7"
    elif len(ob.data.vertices) == mt.settings["alpha8"].nTotalVerts:
        print("Alpha 8 mesh detected")
        ob.MhMeshVersion = "alpha8"
    else:
        print("Unknown mesh version with %d verts" % len(ob.data.vertices))
        ob.MhMeshVersion = ""


def getSettings(ob):
    return mt.settings[ob.MhMeshVersion]

#----------------------------------------------------------
#
#----------------------------------------------------------

def afterImport(context, filepath, deleteHelpers, useMaterials):
    ob = context.object
    ob.MhFilePath = filepath
    ob.MhDeleteHelpers = deleteHelpers
    ob.MhUseMaterials = useMaterials
    setSettings(context)
    settings = getSettings(ob)

    if ob.MhUseMaterials:
        addMaterial(ob, 0, "Body", (1,1,1), (0, settings.nTotalVerts))
        addMaterial(ob, 1, "Tongue", (0.5,0,0.5), settings.vertices["Tongue"])
        addMaterial(ob, 2, "Joints", (0,1,0), settings.vertices["Joints"])
        addMaterial(ob, 3, "Eyes", (0,1,1), settings.vertices["Eyes"])
        addMaterial(ob, 4, "EyeLashes", (1,0,1), settings.vertices["EyeLashes"])
        addMaterial(ob, 5, "LoTeeth", (0,0.5,0.5), settings.vertices["LoTeeth"])
        addMaterial(ob, 6, "UpTeeth", (0,0.5,1), settings.vertices["UpTeeth"])
        addMaterial(ob, 7, "Penis", (0.5,0,1), settings.vertices["Penis"])
        addMaterial(ob, 8, "Tights", (1,0,0), settings.vertices["Tights"])
        addMaterial(ob, 9, "Skirt", (0,0,1), settings.vertices["Skirt"])
        addMaterial(ob, 10, "Hair", (1,1,0), settings.vertices["Hair"])
        addMaterial(ob, 11, "Ground", (1,0.5,0.5), (settings.vertices["Hair"][1], settings.nTotalVerts))

    if ob.MhDeleteHelpers:
        affect = "Body"
    else:
        affect = "All"
    deleteIrrelevant(ob, affect)


def addMaterial(ob, index, name, color, verts):
    first,last = verts
    try:
        mat = bpy.data.materials[name]
    except KeyError:
        mat = bpy.data.materials.new(name=name)
    ob.data.materials.append(mat)
    if mat.name != name:
        print("WARNING: duplicate material %s => %s" % (name, mat.name))
    mat.diffuse_color = color
    for f in ob.data.polygons:
        vn = f.vertices[0]
        if vn >= first and vn < last:
            f.material_index = index


class VIEW3D_OT_ImportBaseMhcloButton(bpy.types.Operator):
    bl_idname = "mh.import_base_mhclo"
    bl_label = "Load Human + Fit Tools"
    bl_description = "Load the base object. Clothes fitting enabled."
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            import_obj.importBaseMhclo(context, filepath=mt.baseMhcloFile)
            afterImport(context, mt.baseMhcloFile, False, True)
            loadAndApplyTarget(context)
        except MHError:
            handleMHError(context)
        return {'FINISHED'}


class VIEW3D_OT_ImportBaseObjButton(bpy.types.Operator):
    bl_idname = "mh.import_base_obj"
    bl_label = "Load Human"
    bl_description = "Load the base object. Clothes fitting disabled."
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            import_obj.importBaseObj(context, filepath=mt.baseObjFile)
            afterImport(context, mt.baseObjFile, True, False)
            loadAndApplyTarget(context)
        except MHError:
            handleMHError(context)
        return {'FINISHED'}


def loadAndApplyTarget(context):
    bodytype = context.scene.MhBodyType
    if bodytype == 'None':
        return
    trgpath = os.path.join(os.path.dirname(__file__), "../makeclothes/targets", bodytype + ".target")
    try:
        utils.loadTarget(trgpath, context)
        found = True
    except FileNotFoundError:
        found = False
    if not found:
        raise MHError("Target \"%s\" not found.\nPath \"%s\" does not seem to be the path to the MakeHuman program" % (trgpath, scn.MhProgramPath))

    ob = context.object
    props = {}
    for key in ob.keys():
        props[key] = ob[key]
    applyTargets(context)
    for key in props.keys():
        ob[key] = props[key]
    ob.name = bodytype.split("-")[1]
    ob.shape_key_add(name="Basis")
    ob["NTargets"] = 0


def makeBaseObj(context):
    mh.proxy = None
    ob = context.object
    if ob.type != 'MESH':
        return
    for mod in ob.modifiers:
        if mod.type == 'ARMATURE':
            mod.show_in_editmode = True
            mod.show_on_cage = True
        else:
            ob.modifiers.remove(mod)
    utils.removeShapeKeys(ob)
    ob.shape_key_add(name="Basis")
    ob["NTargets"] = 0
    ob.ProxyFile = ""
    ob.ObjFile =  ""
    ob.MhHuman = True


def unmakeBaseObj(ob):
    utils.removeShapeKeys(ob)
    try:
        del ob["NTargets"]
    except KeyError:
        pass
    ob.MhHuman = False


class VIEW3D_OT_MakeBaseObjButton(bpy.types.Operator):
    bl_idname = "mh.make_base_obj"
    bl_label = "Set As Base"
    bl_description = "Make the selected object into a maketarget base object."
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            makeBaseObj(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}


def deleteIrrelevant(ob, affect):
    settings = getSettings(ob)
    if ob.MhIrrelevantDeleted or settings is None:
        return
    if affect != 'All':
        nVerts = len(ob.data.vertices)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        for n in range(nVerts):
            ob.data.vertices[n].select = False
        for first,last in settings.irrelevantVerts[affect]:
            for n in range(first, last):
                ob.data.vertices[n].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

        ob.MhMeshVertsDeleted = True
        ob.MhIrrelevantDeleted = True
        ob.MhAffectOnly = affect
        print("Deleted verts: %d -> %d" % (first, last))
        print("# Verts: %d -> %d" % (nVerts, len(ob.data.vertices)))


class VIEW3D_OT_DeleteIrrelevantButton(bpy.types.Operator):
    bl_idname = "mh.delete_irrelevant"
    bl_label = "Delete Irrelevant Verts"
    bl_description = "Delete not affected vertices for better visibility."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        setObjectMode(context)
        try:
            ob = context.object
            deleteIrrelevant(ob, ob.MhAffectOnly)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}


def loadTargetFile(context, filepath):
    global Comments
    setObjectMode(context)
    ob = context.object
    settings = getSettings(ob)
    if ob.MhMeshVertsDeleted:
        _,Comments = utils.loadTarget(
            filepath,
            context,
            irrelevant=settings.irrelevantVerts[ob.MhAffectOnly],
            offset=settings.offsetVerts[ob.MhAffectOnly])
    else:
        _,Comments = utils.loadTarget(filepath, context)


class VIEW3D_OT_LoadTargetButton(bpy.types.Operator):
    bl_idname = "mh.load_target"
    bl_label = "Load Target File"
    bl_description = "Load a target file"
    bl_options = {'UNDO'}

    filename_ext = ".target"
    filter_glob = StringProperty(default="*.target", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for target file",
        maxlen= 1024, default= "")

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        try:
            loadTargetFile(context, self.properties.filepath)
        except MHError:
            handleMHError(context)
        print("Target loaded")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#----------------------------------------------------------
#   loadTargetFromMesh(context):
#----------------------------------------------------------

def getMeshes(context):
    ob = context.object
    scn = context.scene
    if not utils.isBaseOrTarget(ob):
        raise MHError("Active object %s is not a base object" % ob.name)
    trg = None
    for ob1 in scn.objects:
        if ob1.select and ob1.type == 'MESH' and ob1 != ob:
            trg = ob1
            break
    if not trg:
        raise MHError("Two meshes must be selected")
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob,trg,scn


def createNewMeshShape(ob, name, scn):
    scn.objects.active = ob
    skey = ob.shape_key_add(name=name, from_mix=False)
    ob.active_shape_key_index = utils.shapeKeyLen(ob) - 1
    skey.name = name
    skey.slider_min = -1.0
    skey.slider_max = 1.0
    skey.value = 1.0
    ob.show_only_shape_key = False
    ob.use_shape_key_edit_mode = True
    ob["NTargets"] += 1
    ob["FilePath"] = 0
    ob.SelectedOnly = False
    return skey


def loadTargetFromMesh(context):
    ob,trg,scn = getMeshes(context)
    scn.objects.active = trg
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    skey = createNewMeshShape(ob, trg.name, scn)
    nVerts = len(ob.data.vertices)
    for v in trg.data.vertices[0:nVerts]:
        skey.data[v.index].co = v.co
    scn.objects.unlink(trg)


class VIEW3D_OT_LoadTargetFromMeshButton(bpy.types.Operator):
    bl_idname = "mh.load_target_from_mesh"
    bl_label = "Load Target From Mesh"
    bl_description = "Make selected mesh a shapekey of active mesh."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object
        #return (context.object and not context.object.MhMeshVertsDeleted)

    def execute(self, context):
        setObjectMode(context)
        try:
            loadTargetFromMesh(context)
        except MHError:
            handleMHError(context)
        return {'FINISHED'}


#----------------------------------------------------------
#   loadTargetFromMesh(context):
#----------------------------------------------------------

def applyArmature(context):
    ob = context.object
    scn = context.scene
    rig = ob.parent
    if rig is None or rig.type != 'ARMATURE':
        raise MHError("Parent of %s is not an armature" % ob)

    bpy.ops.object.select_all(action='DESELECT')
    ob.select = True
    bpy.ops.object.duplicate()
    bpy.ops.object.shape_key_remove(all=True)
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Armature")
    statue = context.object
    statue.name = "Statue"
    statue.parent = None
    return ob,rig,statue


def createStatueFromPose(context):
    ob,rig,statue = applyArmature(context)
    scn = context.scene
    scn.objects.active = statue
    scn.layers = statue.layers = 10*[False] + [True] + 9*[False]
    unmakeBaseObj(statue)


class VIEW3D_OT_CreateStatueFromPoseButton(bpy.types.Operator):
    bl_idname = "mh.create_statue_from_pose"
    bl_label = "Create Statue From Pose"
    bl_description = "Apply the current pose to the mesh"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object
        #return (context.object and not context.object.MhMeshVertsDeleted)

    def execute(self, context):
        setObjectMode(context)
        try:
            createStatueFromPose(context)
        except MHError:
            handleMHError(context)
        return {'FINISHED'}


#----------------------------------------------------------
#   loadStatueMinusPose(context):
#----------------------------------------------------------

def loadStatueMinusPose(context):
    ob,statue,scn = getMeshes(context)
    ob,rig,posed = applyArmature(context)
    posed.name = "Temporary"

    nVerts = len(ob.data.vertices)

    relMats = {}
    for vg in ob.vertex_groups:
        try:
            pb = rig.pose.bones[vg.name]
        except KeyError:
            pb = None
        if pb:
            relMats[vg.index] = pb.matrix * pb.bone.matrix_local.inverted()
        else:
            print("Skipping vertexgroup %s" % vg.name)
            relMats[vg.index] = Matrix().identity()

    svs = statue.data.vertices
    pvs = posed.data.vertices
    ovs = ob.data.vertices

    skey = createNewMeshShape(ob, statue.name, scn)
    relmat = Matrix()
    y = Vector((0,0,0,1))
    for v in ob.data.vertices:
        vn = v.index
        diff = svs[vn].co - pvs[vn].co
        if diff.length > 1e-4:
            relmat.zero()
            wsum = 0.0
            for g in v.groups:
                w = g.weight
                relmat += w * relMats[g.group]
                wsum += w
            factor = 1.0/wsum
            relmat *= factor

            y[:3] = svs[vn].co
            x = relmat.inverted() * y
            skey.data[vn].co = Vector(x[:3])

            z = relmat * x

            xdiff = skey.data[vn].co - ovs[vn].co

            if False and vn in [8059]:
                print("\nVert", vn, diff.length, xdiff.length)
                print("det", relmat.determinant())
                print("d (%.4f %.4f %.4f)" % tuple(diff))
                print("xd (%.4f %.4f %.4f)" % tuple(xdiff))
                checkRotationMatrix(relmat)
                print("Rel", relmat)
                print("Inv", relmat.inverted())

                s = pvs[vn].co
                print("s ( %.4f  %.4f  %.4f)" % (s[0],s[1],s[2]))
                print("x ( %.4f  %.4f  %.4f)" % (x[0],x[1],x[2]))
                print("y ( %.4f  %.4f  %.4f)" % (y[0],y[1],y[2]))
                print("z ( %.4f  %.4f  %.4f)" % (z[0],z[1],z[2]))
                o = ovs[vn].co
                print("o (%.4f %.4f %.4f)" % (o[0],o[1],o[2]))
                print("r (%.4f %.4f %.4f)" % tuple(skey.data[vn].co))

                for g in v.groups:
                    print("\nGrp %d %f %f" % (g.group, g.weight, relMats[g.group].determinant()))
                    print("Rel", relMats[g.group])

    #scn.objects.unlink(statue)
    scn.objects.unlink(posed)


def checkRotationMatrix(mat):
    for n in range(3):
        vec = mat.col[n]
        if abs(vec.length-1) > 0.1:
            print("No rot %d %f\n%s" % (n, vec.length, mat))
            return True
    return False


class VIEW3D_OT_LoadMeshMinusPoseButton(bpy.types.Operator):
    bl_idname = "mh.load_statue_minus_pose"
    bl_label = "Load Statue Minus Pose"
    bl_description = "Make selected mesh a shapekey of active mesh, and subtract the current pose."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object
        #return (context.object and not context.object.MhMeshVertsDeleted)

    def execute(self, context):
        setObjectMode(context)
        try:
            loadStatueMinusPose(context)
        except MHError:
            handleMHError(context)
        return {'FINISHED'}


#----------------------------------------------------------
#   newTarget(context):
#----------------------------------------------------------

def newTarget(context):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    skey = ob.shape_key_add(name="Target", from_mix=False)
    ob.active_shape_key_index = utils.shapeKeyLen(ob) - 1
    skey.slider_min = -1.0
    skey.slider_max = 1.0
    skey.value = 1.0
    ob.show_only_shape_key = False
    ob.use_shape_key_edit_mode = True
    ob["NTargets"] += 1
    ob["FilePath"] = 0
    ob.SelectedOnly = False
    return


class VIEW3D_OT_NewTargetButton(bpy.types.Operator):
    bl_idname = "mh.new_target"
    bl_label = "New Target"
    bl_description = "Create a new target and make it active."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        global Comments
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            Comments = []
            newTarget(context)
        except MHError:
            handleMHError(context)
        return {'FINISHED'}

#----------------------------------------------------------
#   saveTarget(context):
#----------------------------------------------------------

def doSaveTarget(context, filepath):
    global Comments
    ob = context.object
    settings = getSettings(ob)
    if not utils.isTarget(ob):
        raise MHError("%s is not a target")
    bpy.ops.object.mode_set(mode='OBJECT')
    ob.active_shape_key_index = ob["NTargets"]
    if not checkValid(ob):
        return
    saveAll = not ob.SelectedOnly
    skey = ob.active_shape_key
    if skey.name[0:6] == "Target":
        skey.name = utils.nameFromPath(filepath)
    verts = evalVertLocations(ob)

    (fname,ext) = os.path.splitext(filepath)
    filepath = fname + ".target"
    print("Saving target %s to %s" % (ob, filepath))
    if False and ob.MhMeshVertsDeleted and ob.MhAffectOnly != 'All':
        first,last = settings.affectedVerts[ob.MhAffectOnly]
        before,after = readLines(filepath, first,last)
        fp = open(filepath, "w", encoding="utf-8", newline="\n")
        for line in before:
            fp.write(line)
        if ob.MhMeshVertsDeleted:
            offset = settings.offsetVerts[ob.MhAffectOnly]
        else:
            offset = 0
        saveVerts(fp, ob, verts, saveAll, first, last, offset)
        for (vn, string) in after:
            fp.write("%d %s" % (vn, string))
    else:
        fp = open(filepath, "w", encoding="utf-8", newline="\n")
        if Comments == []:
            Comments = getDefaultComments()
        for line in Comments:
            fp.write(line)
        saveVerts(fp, ob, verts, saveAll, 0, len(verts), 0)
    fp.close()
    ob["FilePath"] = filepath


def getDefaultComments():
    filepath = os.path.join(getMHBlenderDirectory(), "make_target.notice")
    try:
        fp = open(filepath, "rU")
    except:
        print("Could not open %s" % filepath)
        return []
    comments = []
    for line in fp:
        comments.append(line)
    return comments


def readLines(filepath, first, last):
    before = []
    after = []
    try:
        fp = open(filepath, "rU")
    except FileNotFoundError:
        return before,after
    for line in fp:
        words = line.split(None, 1)
        if len(words) >= 2:
            vn = int(words[0])
            if vn < first:
                before.append(line)
            elif vn >= last:
                after.append((vn, words[1]))
    fp.close()
    return before,after


def saveVerts(fp, ob, verts, saveAll, first, last, offs):
    for n in range(first, last):
        vco = verts[n-offs]
        bv = ob.data.vertices[n-offs]
        vec = vco - bv.co
        if vec.length > Epsilon and (saveAll or bv.select):
            fp.write("%d %s %s %s\n" % (n, round(vec[0]), round(vec[2]), round(-vec[1])))


def evalVertLocations(ob):
    verts = {}
    for v in ob.data.vertices:
        verts[v.index] = v.co.copy()

    for skey in ob.data.shape_keys.key_blocks:
        if (skey.name == "Basis" or
            (ob.MhZeroOtherTargets and skey != ob.active_shape_key)):
            print("Skipped", skey.name)
            continue
        print("Adding", skey.name)
        for n,v in enumerate(skey.data):
            bv = ob.data.vertices[n]
            vec = v.co - bv.co
            verts[n] += skey.value*vec
    return verts


class VIEW3D_OT_SaveTargetButton(bpy.types.Operator):
    bl_idname = "mh.save_target"
    bl_label = "Save Target"
    bl_description = "Save target(s), overwriting existing file. If Active Only is selected, only save the last target, otherwise save the sum of all targets"
    bl_options = {'UNDO'}

    filepath = StringProperty(default="")

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        setObjectMode(context)
        try:
            doSaveTarget(context, self.filepath)
            print("Target saved")
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

    def invoke(self, context, event):
        return invokeWithFileCheck(self, context, context.object["FilePath"])

    def draw(self, context):
        drawFileCheck(self)


class VIEW3D_OT_SaveasTargetButton(bpy.types.Operator, ExportHelper):
    bl_idname = "mh.saveas_target"
    bl_label = "Save Target As"
    bl_description = "Save target(s) to new file. If Active Only is selected, only save the last target, otherwise save the sum of all targets"
    bl_options = {'UNDO'}

    filename_ext = ".target"
    filter_glob = StringProperty(default="*.target", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for target file",
        maxlen= 1024, default= "")

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        setObjectMode(context)
        try:
            doSaveTarget(context, self.properties.filepath)
        except MHError:
            handleMHError(context)
        print("Target saved")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#----------------------------------------------------------
#   Apply targets to mesh
#----------------------------------------------------------

def applyTargets(context):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    verts = evalVertLocations(ob)
    utils.removeShapeKeys(ob)
    for prop in ob.keys():
        del ob[prop]
    for v in ob.data.vertices:
        v.co = verts[v.index]
    return


class VIEW3D_OT_ApplyTargetsButton(bpy.types.Operator):
    bl_idname = "mh.apply_targets"
    bl_label = "Apply Targets"
    bl_description = "Apply all shapekeys to mesh"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        try:
            setObjectMode(context)
            applyTargets(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#----------------------------------------------------------
#
#----------------------------------------------------------

def pruneTarget(ob, filepath):
    settings = getSettings(ob)
    lines = []
    before,after = readLines(filepath, -1,-1)
    for vn,string in after:
        if vn < settings.nTotalVerts and ob.data.vertices[vn].select:
            lines.append((vn, string))
    print("Pruning", len(before), len(after), len(lines))
    fp = open(filepath, "w", encoding="utf-8", newline="\n")
    for vn,string in lines:
        fp.write(str(vn) + " " + string)
    fp.close()


def pruneFolder(ob, folder):
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isdir(path):
            if ob.MhPruneRecursively:
                pruneFolder(ob, path)
        else:
            (name,ext) = os.path.splitext(file)
            if ext == ".target":
                print("Prune", path)
                pruneTarget(ob, path)


class VIEW3D_OT_PruneTargetFileButton(bpy.types.Operator, ExportHelper):
    bl_idname = "mh.prune_target_file"
    bl_label = "Prune Target File"
    bl_description = "Remove not selected vertices from target file(s)"
    bl_options = {'UNDO'}

    filename_ext = ".target"
    filter_glob = StringProperty(default="*.target", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for target file",
        maxlen= 1024, default= "")

    @classmethod
    def poll(self, context):
        return (context.object and context.object.MhPruneEnabled)

    def execute(self, context):
        try:
            setObjectMode(context)
            ob = context.object
            if ob.MhPruneWholeDir:
                folder = os.path.dirname(self.properties.filepath)
                pruneFolder(ob, folder)
                print("Targets pruned")
            else:
                pruneTarget(ob, self.properties.filepath)
                print("Target pruned")
        except MHError:
            handleMHError(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#----------------------------------------------------------
#   batch
#----------------------------------------------------------

def batchFitTargets(context, folder):
    global Comments
    print("Batch", folder)
    for fname in os.listdir(folder):
        (root, ext) = os.path.splitext(fname)
        file = os.path.join(folder, fname)
        if os.path.isfile(file) and ext == ".target":
            print(file)
            _,Comments = utils.loadTarget(file, context)
            fitTarget(context)
            doSaveTarget(context, file)
            discardTarget(context)
        elif os.path.isdir(file):
            batchFitTargets(context, file)
    return


class VIEW3D_OT_BatchFitButton(bpy.types.Operator):
    bl_idname = "mh.batch_fit"
    bl_label = "Batch Fit Targets"
    bl_description = "Fit all targets in directory"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        global TargetSubPaths
        setObjectMode(context)
        scn = context.scene
        folder = os.path.realpath(os.path.expanduser(scn.MhTargetPath))
        batchFitTargets(context, folder)
        #for subfolder in TargetSubPaths:
        #    if scn["Mh%s" % subfolder]:
        #        batchFitTargets(context, os.path.join(folder, subfolder))
        print("All targets fited")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=200, height=20)

    def draw(self, context):
        self.layout.label("Really batch fit targets?")

#----------------------------------------------------------
#   batch render
#----------------------------------------------------------

def batchRenderTargets(context, folder, opengl, outdir):
    global Comments
    print("Batch render", folder)
    for fname in os.listdir(folder):
        (root, ext) = os.path.splitext(fname)
        file = os.path.join(folder, fname)
        if os.path.isfile(file) and ext == ".target":
            print(file)
            context.scene.render.filepath = os.path.join(outdir, root)
            _,Comments = utils.loadTarget(file, context)
            if opengl:
                bpy.ops.render.opengl(animation=True)
            else:
                bpy.ops.render.render(animation=True)
            discardTarget(context)
        elif os.path.isdir(file):
            batchRenderTargets(context, file, opengl, outdir)
    return


class VIEW3D_OT_BatchRenderButton(bpy.types.Operator):
    bl_idname = "mh.batch_render"
    bl_label = "Batch Render"
    bl_description = "Render all targets in directory"
    bl_options = {'UNDO'}
    opengl = BoolProperty()

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        global TargetSubPaths
        setObjectMode(context)
        scn = context.scene
        folder = os.path.expanduser(scn.MhTargetPath)
        outdir = os.path.join(getMHBlenderDirectory(), "pictures/")
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        scn.frame_start = 1
        scn.frame_end = 1
        for subfolder in TargetSubPaths:
            if scn["Mh%s" % subfolder]:
                batchRenderTargets(context, os.path.join(folder, subfolder), self.opengl, outdir)
        print("All targets rendered")
        return {'FINISHED'}

#----------------------------------------------------------
#   fitTarget(context):
#----------------------------------------------------------

def fitTarget(context):
    ob = context.object
    settings = getSettings(ob)
    bpy.ops.object.mode_set(mode='OBJECT')
    scn = context.scene
    if not utils.isTarget(ob):
        return
    ob.active_shape_key_index = ob["NTargets"]
    if not checkValid(ob):
        return
    if not mh.proxy:
        path = ob.ProxyFile
        if path:
            print("Rereading %s" % path)
            mh.proxy = CProxy()
            mh.proxy.read(path)
        else:
            raise MHError("Object %s has no associated mhclo file. Cannot fit" % ob.name)
            return
    if ob.MhAffectOnly != 'All':
        first,last = settings.affectedVerts[ob.MhAffectOnly]
        mh.proxy.update(ob.active_shape_key.data, ob.active_shape_key.data, skipBefore=first, skipAfter=last)
    else:
        mh.proxy.update(ob.active_shape_key.data, ob.active_shape_key.data)
    return


class VIEW3D_OT_FitTargetButton(bpy.types.Operator):
    bl_idname = "mh.fit_target"
    bl_label = "Fit Target"
    bl_description = "Fit clothes to character"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return (not context.object.MhMeshVertsDeleted)

    def execute(self, context):
        try:
            setObjectMode(context)
            fitTarget(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#----------------------------------------------------------
#   discardTarget(context):
#----------------------------------------------------------

def discardTarget(context):
    ob = context.object
    if not utils.isTarget(ob):
        return
    bpy.ops.object.mode_set(mode='OBJECT')
    ob.active_shape_key_index = ob["NTargets"]
    bpy.ops.object.shape_key_remove()
    ob["NTargets"] -= 1
    ob.active_shape_key_index = ob["NTargets"]
    checkValid(ob)
    return


def discardAllTargets(context):
    ob = context.object
    while utils.isTarget(ob):
        discardTarget(context)
    return


def checkValid(ob):
    nShapes = utils.shapeKeyLen(ob)
    if nShapes != ob["NTargets"]+1:
        print("Consistency problem:\n  %d shapes, %d targets" % (nShapes, ob["NTargets"]))
        return False
    return True


class VIEW3D_OT_DiscardTargetButton(bpy.types.Operator):
    bl_idname = "mh.discard_target"
    bl_label = "Discard Target"
    bl_description = "Remove the active target and make the second last active"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        try:
            setObjectMode(context)
            discardTarget(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}


class VIEW3D_OT_DiscardAllTargetsButton(bpy.types.Operator):
    bl_idname = "mh.discard_all_targets"
    bl_label = "Discard All Targets"
    bl_description = "Discard all targets in the target stack"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        try:
            setObjectMode(context)
            discardAllTargets(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#----------------------------------------------------------
# symmetrizeTarget(context, left2right, mirror):
#----------------------------------------------------------
'''
class CPairing:

    def __init__(self):
        self.left = {}
        self.right = {}
        self.mid = {}
        self.epsilon = 1e-3
        self.verts = []
        self.nmax = 0
        self.notfound = []


    def setup(self, context, insist):
        if self.left.keys() and not insist:
            print("Vertex pair already set up")
            return
        ob = context.object
        self.verts = []
        for v in ob.data.vertices:
            x = v.co[0]
            y = v.co[1]
            z = v.co[2]
            self.verts.append((z,y,x,v.index))
        self.verts.sort()
        self.nmax = len(self.verts)

        self.left = {}
        self.right = {}
        self.mid = {}
        self.notfound = []
        for n,data in enumerate(self.verts):
            (z,y,x,vn) = data
            self.findMirrorVert(n, vn, x, y, z)

        if self.notfound:
            print("Did not find mirror image for vertices:")
            for n,vn,x,y,z in self.notfound:
                print("  %d at (%.4f %.4f %.4f)" % (vn, x, y, z))
            self.selectVerts(ob)
        print("left-right-mid", len(self.left), len(self.right), len(self.mid))
        return self


    def findMirrorVert(self, n, vn, x, y, z):
        n1 = n - 20
        n2 = n + 20
        if n1 < 0: n1 = 0
        if n2 >= self.nmax: n2 = self.nmax
        vmir = self.findVert(n, self.verts[n1:n2], vn, -x, y, z)
        if vmir < 0:
            self.mid[vn] = vn
        elif x > self.epsilon:
            self.left[vn] = vmir
        elif x < -self.epsilon:
            self.right[vn] = vmir
        else:
            self.mid[vn] = vmir


    def selectVerts(self, ob):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        for n,vn,x,y,z in self.notfound:
            ob.data.vertices[vn].select = True
        return


    def findVert(self, n, verts, v, x, y, z):
        for (z1,y1,x1,v1) in verts:
            dx = x-x1
            dy = y-y1
            dz = z-z1
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist < self.epsilon:
                return v1
        if abs(x) > self.epsilon:
            self.notfound.append((n,v,x,y,z))
        return -1
'''

def symmetrizeTarget(context, left2right, mirror):
    #pairing = CPairing().setup(context, False)

    ob = context.object
    scn = context.scene
    if not utils.isTarget(ob):
        return
    bpy.ops.object.mode_set(mode='OBJECT')
    verts = ob.active_shape_key.data
    nVerts = len(verts)

    for vn in Mid2Mid.keys():
        if vn >= nVerts:
            break
        v = verts[vn]
        v.co[0] = 0

    for (lvn,rvn) in Left2Right.items():
        if lvn >= nVerts or rvn >= nVerts:
            break
        lv = verts[lvn].co
        rv = verts[rvn].co
        if mirror:
            tv = rv.copy()
            verts[rvn].co = (-lv[0], lv[1], lv[2])
            verts[lvn].co = (-tv[0], tv[1], tv[2])
        elif left2right:
            rv[0] = -lv[0]
            rv[1] = lv[1]
            rv[2] = lv[2]
        else:
            lv[0] = -rv[0]
            lv[1] = rv[1]
            lv[2] = rv[2]

    bverts = ob.data.vertices
    selected = {}
    for v in bverts:
        selected[v.index] = v.select

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    for vn in Mid2Mid.keys():
        if vn >= nVerts:
            break
        bverts[vn].select = selected[vn]

    for (lvn,rvn) in Left2Right.items():
        if lvn >= nVerts or rvn >= nVerts:
            break
        if mirror:
            bverts[lvn].select = selected[rvn]
            bverts[rvn].select = selected[lvn]
        elif left2right:
            bverts[lvn].select = selected[lvn]
            bverts[rvn].select = selected[lvn]
        else:
            bverts[lvn].select = selected[rvn]
            bverts[rvn].select = selected[rvn]

    print("Target symmetrized")
    return


class VIEW3D_OT_SymmetrizeTargetButton(bpy.types.Operator):
    bl_idname = "mh.symmetrize_target"
    bl_label = "Symmetrize"
    bl_description = "Symmetrize or mirror active target"
    bl_options = {'UNDO'}
    action = StringProperty()

    def execute(self, context):
        try:
            setObjectMode(context)
            symmetrizeTarget(context, (self.action=="Right"), (self.action=="Mirror"))
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#----------------------------------------------------------
#   Snapping
#----------------------------------------------------------

def snapWaist(context):
    ob = context.object
    settings = getSettings(ob)
    if ob.MhIrrelevantDeleted:
        offset = settings.offsetVerts['Skirt']
    else:
        offset = 0

    nVerts = len(settings.skirtWaist)
    if len(settings.tightsWaist) != nVerts:
        raise RuntimeError("snapWaist: %d %d" % (len(settings.tightsWaist), nVerts))
    bpy.ops.object.mode_set(mode='OBJECT')
    skey = ob.data.shape_keys.key_blocks[-1]
    verts = skey.data
    for n in range(nVerts):
        verts[settings.skirtWaist[n]-offset].co = verts[settings.tightsWaist[n]-offset].co

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')


class VIEW3D_OT_SnapWaistButton(bpy.types.Operator):
    bl_idname = "mh.snap_waist"
    bl_label = "Snap Skirt Waist"
    bl_description = "Snap the top row of skirt verts to the corresponding tight verts"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        ob = context.object
        return (ob.MhAffectOnly == 'Skirt' or not ob.MhIrrelevantDeleted)

    def execute(self, context):
        try:
            setObjectMode(context)
            snapWaist(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}


def straightenSkirt(context):
    ob = context.object
    settings = getSettings(ob)
    if ob.MhIrrelevantDeleted:
        offset = settings.offsetVerts['Skirt']
    else:
        offset = 0

    bpy.ops.object.mode_set(mode='OBJECT')
    skey = ob.data.shape_keys.key_blocks[-1]
    verts = skey.data

    for col in settings.XYSkirtColumns:
        xsum = 0.0
        ysum = 0.0
        for vn in col:
            xsum += verts[vn-offset].co[0]
            ysum += verts[vn-offset].co[1]
        x = xsum/len(col)
        y = ysum/len(col)
        for vn in col:
            verts[vn-offset].co[0] = x
            verts[vn-offset].co[1] = y

    for row in settings.ZSkirtRows:
        zsum = 0.0
        for vn in row:
            zsum += verts[vn-offset].co[2]
        z = zsum/len(row)
        for vn in row:
            verts[vn-offset].co[2] = z

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')


class VIEW3D_OT_StraightenSkirtButton(bpy.types.Operator):
    bl_idname = "mh.straighten_skirt"
    bl_label = "Straighten Skirt"
    bl_description = "Make (the right side of) the skirt perfectly straight."
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        ob = context.object
        return (ob.MhAffectOnly == 'Skirt' or not ob.MhIrrelevantDeleted)

    def execute(self, context):
        try:
            setObjectMode(context)
            straightenSkirt(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}


#----------------------------------------------------------
#   Skip
#----------------------------------------------------------

def fixInconsistency(context):
    ob = context.object
    if ob.data.shape_keys:
        ob["NTargets"] = len(ob.data.shape_keys.key_blocks)
    else:
        ob.shape_key_add(name="Basis")
        ob["NTargets"] = 0


class VIEW3D_OT_FixInconsistencyButton(bpy.types.Operator):
    bl_idname = "mh.fix_inconsistency"
    bl_label = "Fix It!"
    bl_description = "Due to a bug, the target stack has become corrupt. Fix it."
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            setObjectMode(context)
            fixInconsistency(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#----------------------------------------------------------
#   Init
#----------------------------------------------------------

MTIsInited = False

def init():
    global MTIsInited

    bpy.types.Scene.MhUnlock = BoolProperty(default = False)

    bpy.types.Object.ProxyFile = StringProperty(default = "")
    bpy.types.Object.ObjFile = StringProperty(default = "")
    bpy.types.Object.MhHuman = BoolProperty(default = False)

    bpy.types.Object.MhDeleteHelpers = BoolProperty(name="Delete Helpers", default = False)
    bpy.types.Object.MhUseMaterials = BoolProperty(name="Use Materials", default = False)

    bpy.types.Object.MhPruneWholeDir = BoolProperty(name="Prune Entire Directory", default = False)
    bpy.types.Object.MhPruneEnabled = BoolProperty(name="Pruning Enabled", default = False)
    bpy.types.Object.MhPruneRecursively = BoolProperty(name="Prune Folders Recursively", default = False)

    bpy.types.Object.MhFilePath = StringProperty(default = "")
    bpy.types.Object.MhMeshVersion = StringProperty(default = "None")

    #bpy.types.Object.MhTightsOnly = BoolProperty(default = False)
    #bpy.types.Object.MhSkirtOnly = BoolProperty(default = False)

    bpy.types.Object.MhAffectOnly = EnumProperty(
        items = [('Body','Body','Body'),
                 ('Tights','Tights','Tights'),
                 ('Skirt','Skirt','Skirt'),
                 ('Hair','Hair','Hair'),
                 ('All','All','All')],
    default='All')

    bpy.types.Scene.MhBodyType = EnumProperty(
        items = [('None', 'Base Mesh', 'None'),
                 ('caucasian-male-young', 'Average Male', 'caucasian-male-young'),
                 ('caucasian-female-young', 'Average Female', 'caucasian-female-young'),
                ],
        description = "Character to load",
    default='caucasian-female-young')

    bpy.types.Object.MhIrrelevantDeleted = BoolProperty(name="Irrelevant deleted", default = False)
    bpy.types.Object.MhMeshVertsDeleted = BoolProperty(name="Cannot load", default = False)

    bpy.types.Object.SelectedOnly = BoolProperty(name="Selected verts only", default = True)
    bpy.types.Object.MhZeroOtherTargets = BoolProperty(name="Active target only", description="Save the active (last) target only, setting the values of all other targets to 0", default = False)

    from . import settings
    settings.init()
    from . import import_obj
    import_obj.init()
    #from . import character
    #character.init()
    from . import convert
    convert.init()
    from . import pose
    pose.init()

    MTIsInited = True


def initBatch():
    global TargetSubPaths
    TargetSubPaths = []
    folder = os.path.realpath(os.path.expanduser(scn.MhTargetPath))
    for fname in os.listdir(folder):
        file = os.path.join(folder, fname)
        if os.path.isdir(file) and fname[0] != ".":
            TargetSubPaths.append(fname)
            setattr(bpy.types.Scene, "Mh%s" % fname, BoolProperty(name=fname))
            scn["Mh%s" % fname] = False
    return


def isInited(scn):
    return True
    try:
        TargetSubPaths
        scn.MhTargetPath
        return True
    except:
        return False


class VIEW3D_OT_InitButton(bpy.types.Operator):
    bl_idname = "mh.init"
    bl_label = "Initialize"
    bl_description = ""
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        return context.object

    def execute(self, context):
        initScene(context.scene)
        return{'FINISHED'}

