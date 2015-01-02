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
MHX (MakeHuman eXchange format) importer for Blender 2.6x.

"""

import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper, ExportHelper

###################################################################################
#
#    Main panel
#
###################################################################################

MhxLayers = [
    (( 0,    'Root', 'MhxRoot'),
     ( 1,    'Spine', 'MhxFKSpine')),
    ((10,    'Head', 'MhxHead'),
     ( 8,    'Face', 'MhxFace')),
    (( 9,    'Tweak', 'MhxTweak'),
     (16,    'Clothes', 'MhxClothes')),
    #((17,    'IK Spine', 'MhxIKSpine'),
     #((13,    'Inv FK Spine', 'MhxInvFKSpine')),
    ('Left', 'Right'),
    (( 2,    'IK Arm', 'MhxIKArm'),
     (18,    'IK Arm', 'MhxIKArm')),
    (( 3,    'FK Arm', 'MhxFKArm'),
     (19,    'FK Arm', 'MhxFKArm')),
    (( 4,    'IK Leg', 'MhxIKLeg'),
     (20,    'IK Leg', 'MhxIKLeg')),
    (( 5,    'FK Leg', 'MhxFKLeg'),
     (21,    'FK Leg', 'MhxFKLeg')),
    ((12,    'Extra', 'MhxExtra'),
     (28,    'Extra', 'MhxExtra')),
    (( 6,    'Fingers', 'MhxFingers'),
     (22,    'Fingers', 'MhxFingers')),
    (( 7,    'Links', 'MhxLinks'),
     (23,    'Links', 'MhxLinks')),
    ((11,    'Palm', 'MhxPalm'),
     (27,    'Palm', 'MhxPalm')),
]

OtherLayers = [
    (( 1,    'Spine', 'MhxFKSpine'),
     ( 10,    'Head', 'MhxHead')),
    (( 9,    'Tweak', 'MhxTweak'),
     ( 8,    'Face', 'MhxFace')),
    ('Left', 'Right'),
    (( 3,    'Arm', 'MhxFKArm'),
     (19,    'Arm', 'MhxFKArm')),
    (( 5,    'Leg', 'MhxFKLeg'),
     (21,    'Leg', 'MhxFKLeg')),
    (( 7,    'Fingers', 'MhxLinks'),
     (23,    'Fingers', 'MhxLinks')),
    ((11,    'Palm', 'MhxPalm'),
     (27,    'Palm', 'MhxPalm')),
]


class VIEW3D_OT_MhxEnableAllLayersButton(bpy.types.Operator):
    bl_idname = "mhx.pose_enable_all_layers"
    bl_label = "Enable all layers"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig,mesh = getMhxRigMesh(context.object)
        for (left,right) in MhxLayers:
            if type(left) != str:
                for (n, name, prop) in [left,right]:
                    rig.data.layers[n] = True
        return{'FINISHED'}


class VIEW3D_OT_MhxDisableAllLayersButton(bpy.types.Operator):
    bl_idname = "mhx.pose_disable_all_layers"
    bl_label = "Disable all layers"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig,mesh = getMhxRigMesh(context.object)
        layers = 32*[False]
        pb = context.active_pose_bone
        if pb:
            for n in range(32):
                if pb.bone.layers[n]:
                    layers[n] = True
                    break
        else:
            layers[0] = True
        if rig:
            rig.data.layers = layers
        return{'FINISHED'}



def saveMhpFile(rig, scn, filepath):
    roots = []
    for pb in rig.pose.bones:
        if pb.parent is None:
            roots.append(pb)

    (pname, ext) = os.path.splitext(filepath)
    mhppath = pname + ".mhp"

    fp = open(mhppath, "w", encoding="utf-8", newline="\n")
    for root in roots:
        writeMhpBones(fp, root, None)
    fp.close()
    print("Mhp file %s saved" % mhppath)


def writeMhpBones(fp, pb, log):
    if not isMuscleBone(pb):
        b = pb.bone
        if pb.parent:
            mat = b.matrix_local.inverted() * b.parent.matrix_local * pb.parent.matrix.inverted() * pb.matrix
        else:
            mat = pb.matrix.copy()
            maty = mat[1].copy()
            matz = mat[2].copy()
            mat[1] = matz
            mat[2] = -maty

        diff = mat - Matrix()
        nonzero = False
        for i in range(4):
            if abs(diff[i].length) > 5e-3:
                nonzero = True
                break

        if nonzero:
            fp.write("%s\tmatrix" % pb.name)
            for i in range(4):
                row = mat[i]
                fp.write("\t%.4f\t%.4f\t%.4f\t%.4f" % (row[0], row[1], row[2], row[3]))
            fp.write("\n")

    for child in pb.children:
        writeMhpBones(fp, child, log)


def isMuscleBone(pb):
    layers = pb.bone.layers
    if (layers[14] or layers[15] or layers[30] or layers[31]):
        return True
    for cns in pb.constraints:
        if (cns.type == 'STRETCH_TO' or
            cns.type == 'TRANSFORM' or
            cns.type == 'TRACK_TO' or
            cns.type == 'IK' or
            cns.type[0:5] == 'COPY_'):
            return True
    return False


def loadMhpFile(rig, scn, filepath):
    unit = Matrix()
    for pb in rig.pose.bones:
        pb.matrix_basis = unit

    (pname, ext) = os.path.splitext(filepath)
    mhppath = pname + ".mhp"

    fp = open(mhppath, "rU")
    for line in fp:
        words = line.split()
        if len(words) < 4:
            continue

        try:
            pb = rig.pose.bones[words[0]]
        except KeyError:
            print("Warning: Did not find bone %s" % words[0])
            continue

        if isMuscleBone(pb):
            pass
        elif words[1] == "quat":
            q = Quaternion((float(words[2]), float(words[3]), float(words[4]), float(words[5])))
            mat = q.to_matrix().to_4x4()
            pb.matrix_basis = mat
        elif words[1] == "gquat":
            q = Quaternion((float(words[2]), float(words[3]), float(words[4]), float(words[5])))
            mat = q.to_matrix().to_4x4()
            maty = mat[1].copy()
            matz = mat[2].copy()
            mat[1] = -matz
            mat[2] = maty
            pb.matrix_basis = pb.bone.matrix_local.inverted() * mat
        elif words[1] == "matrix":
            rows = []
            n = 2
            for i in range(4):
                rows.append((float(words[n]), float(words[n+1]), float(words[n+2]), float(words[n+3])))
                n += 4
            mat = Matrix(rows)
            if pb.parent:
                pb.matrix_basis = mat
            else:
                maty = mat[1].copy()
                matz = mat[2].copy()
                mat[1] = -matz
                mat[2] = maty
                pb.matrix_basis = pb.bone.matrix_local.inverted() * mat
        elif words[1] == "scale":
            pass
        else:
            print("WARNING: Unknown line in mcp file:\n%s" % line)
    fp.close()
    print("Mhp file %s loaded" % mhppath)


class VIEW3D_OT_LoadMhpButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mhx.load_mhp"
    bl_label = "Load MHP File"
    bl_description = "Load a pose in MHP format"
    bl_options = {'UNDO'}

    filename_ext = ".mhp"
    filter_glob = StringProperty(default="*.mhp", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for mhp file",
        maxlen= 1024, default= "")

    def execute(self, context):
        loadMhpFile(context.object, context.scene, self.properties.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_SaveasMhpFileButton(bpy.types.Operator, ExportHelper):
    bl_idname = "mhx.saveas_mhp"
    bl_label = "Save MHP File"
    bl_description = "Save current pose in MHP format"
    bl_options = {'UNDO'}

    filename_ext = ".mhp"
    filter_glob = StringProperty(default="*.mhp", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for mhp file",
        maxlen= 1024, default= "")

    def execute(self, context):
        saveMhpFile(context.object, context.scene, self.properties.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


###################################################################################
#
#    Common functions
#
###################################################################################
#
#   getMhxRigMesh(ob):
#

def getMhxRigMesh(ob):
    if ob.type == 'ARMATURE':
        for mesh in ob.children:
            if mesh.MhxMesh and ob.MhxRig:
                return (ob, mesh)
        return (ob, None)
    elif ob.type == 'MESH':
        par = ob.parent
        if (par and par.type == 'ARMATURE' and par.MhxRig):
            if ob.MhxMesh:
                return (par, ob)
            else:
                return (par, None)
        else:
            return (None, None)
    return (None, None)



