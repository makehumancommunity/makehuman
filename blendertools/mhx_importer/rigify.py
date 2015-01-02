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

Postprocessing of rigify rig

"""

import bpy
import os
from bpy.props import *

from .error import *


class RigifyBone:
    def __init__(self, eb):
        self.name = eb.name
        self.realname = None
        self.realname1 = None
        self.realname2 = None
        self.fkname = None
        self.ikname = None

        self.head = eb.head.copy()
        self.tail = eb.tail.copy()
        self.roll = eb.roll
        self.customShape = None
        self.lockLocation = None
        self.deform = eb.use_deform
        self.parent = None
        self.child = None
        self.connect = False
        self.original = False
        self.extra = (eb.name in ["spine-1"])

        if eb.layers[10]:   # Old Face
            self.layer = 0
        elif eb.layers[8]:  # New face
            self.layer = 1
        elif eb.layers[9]:  # Tweak
            self.layer = 1
        else:
            self.layer = 29  # Muscle

    def __repr__(self):
        return ("<RigifyBone %s %s %s>" % (self.name, self.realname, self.realname1))


def rigifyMhx(context):
    from collections import OrderedDict

    print("Modifying MHX rig to Rigify")
    scn = context.scene
    ob = context.object
    if ob.type == 'ARMATURE':
        rig = ob
    elif ob.type == 'MESH':
        rig = ob.parent
    else:
        rig = None
    if not(rig and rig.type == 'ARMATURE'):
        raise RuntimeError("Rigify: %s is neither an armature nor has armature parent" % ob)
    rig.MhxRigify = True
    scn.objects.active = rig

    group = None
    for grp in bpy.data.groups:
        if rig.name in grp.objects:
            group = grp
            break
    print("Group: %s" % group)

    # Setup info about MHX bones
    bones = OrderedDict()
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in rig.data.edit_bones:
        bone = bones[eb.name] = RigifyBone(eb)
        if eb.parent:
            bone.parent = eb.parent.name
            bones[bone.parent].child = eb.name
    bpy.ops.object.mode_set(mode='OBJECT')

    for pb in rig.pose.bones:
        bone = bones[pb.name]
        bone.lockLocation = pb.lock_location
        if pb.custom_shape:
            bone.customShape = pb.custom_shape
            if pb.custom_shape.parent:
                pb.custom_shape.parent.parent = None
                pb.custom_shape.parent = None
            pb.custom_shape = None

    # Create metarig
    try:
        bpy.ops.object.armature_human_metarig_add()
    except AttributeError:
        raise MyError("The Rigify add-on is not enabled. It is found under rigging.")
    bpy.ops.object.location_clear()
    bpy.ops.object.rotation_clear()
    bpy.ops.object.scale_clear()
    bpy.ops.transform.resize(value=(100, 100, 100))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Fit metarig to default MHX rig
    meta = context.object
    bpy.ops.object.mode_set(mode='EDIT')
    extra = []
    for bone in bones.values():
        try:
            eb = meta.data.edit_bones[bone.name]
        except KeyError:
            eb = None
        if eb:
            eb.head = bone.head
            eb.tail = bone.tail
            eb.roll = bone.roll
            bone.original = True
        elif bone.extra:
            extra.append(bone.name)
            bone.original = True
            eb = meta.data.edit_bones.new(bone.name)
            eb.use_connect = False
            eb.head = bones[bone.parent].tail
            eb.tail = bones[bone.child].head
            eb.roll = bone.roll
            parent = meta.data.edit_bones[bone.parent]
            child = meta.data.edit_bones[bone.child]
            child.parent = eb
            child.head = bones[bone.child].head
            parent.tail = bones[bone.parent].tail
            eb.parent = parent
            eb.use_connect = True

    # Add rigify properties to extra bones
    bpy.ops.object.mode_set(mode='OBJECT')
    for bname in extra:
        pb = meta.pose.bones[bname]
        pb["rigify_type"] = ""

    # Generate rigify rig
    bpy.ops.pose.rigify_generate()
    gen = context.object
    print("Generated", gen)
    scn.objects.unlink(meta)
    del meta

    for bone in bones.values():
        if bone.original:
            setBoneName(bone, gen)

    # Add extra bone to generated rig
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in bones.values():
        if not bone.original:
            if bone.layer == 1:
                bone.realname = bone.name
            elif bone.deform:
                bone.realname = "DEF-" + bone.name
            else:
                bone.realname = "MCH-" + bone.name
            eb = gen.data.edit_bones.new(bone.realname)
            eb.head = bone.head
            eb.tail = bone.tail
            eb.roll = bone.roll
            eb.use_deform = bone.deform
            if bone.parent:
                parent = bones[bone.parent]
                if parent.realname:
                    eb.parent = gen.data.edit_bones[parent.realname]
                elif parent.realname1:
                    eb.parent = gen.data.edit_bones[parent.realname1]
                else:
                    print(bone)
            eb.use_connect = (eb.parent != None and eb.parent.tail == eb.head)
            layers = 32*[False]
            layers[bone.layer] = True
            eb.layers = layers

    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in bones.values():
        if not bone.original:
            pb = gen.pose.bones[bone.realname]
            db = rig.pose.bones[bone.name]
            pb.rotation_mode = db.rotation_mode
            pb.lock_location = bone.lockLocation
            if bone.customShape:
                pb.custom_shape = bone.customShape
            for cns1 in db.constraints:
                cns2 = pb.constraints.new(cns1.type)
                fixConstraint(cns1, cns2, gen, bones)

    # Add MHX properties
    for key in rig.keys():
        gen[key] = rig[key]

    # Copy MHX bone drivers and actions
    if rig.animation_data:
        if rig.animation_data.action:
            gen.keyframe_insert(data_path="location", frame=1)
            act = gen.animation_data.action
            gen.animation_data.action = rig.animation_data.action
            #del act

        for fcu1 in rig.animation_data.drivers:
            rna,channel = fcu1.data_path.rsplit(".", 1)
            pb = mhxEval("gen.%s" % rna)
            fcu2 = pb.driver_add(channel, fcu1.array_index)
            copyDriver(fcu1, fcu2, gen)

    # Copy MHX morph drivers and change armature modifier
    for ob in rig.children:
        if ob.type == 'MESH':
            ob.parent = gen

            if ob.data.animation_data:
                for fcu in ob.data.animation_data.drivers:
                    print(ob, fcu.data_path)
                    changeDriverTarget(fcu, gen)

            if ob.data.shape_keys and ob.data.shape_keys.animation_data:
                for fcu in ob.data.shape_keys.animation_data.drivers:
                    print(skey, fcu.data_path)
                    changeDriverTarget(fcu, gen)

            for mod in ob.modifiers:
                if mod.type == 'ARMATURE' and mod.object == rig:
                    mod.object = gen

    if group:
        group.objects.link(gen)

    # Parent widgets under empty
    empty = bpy.data.objects.new("Widgets", None)
    scn.objects.link(empty)
    empty.layers = 20*[False]
    empty.layers[19] = True
    empty.parent = gen
    for ob in scn.objects:
        if (ob.type == 'MESH' and
            ob.name[0:4] in ["WGT-", "GZM_"] and
            not ob.parent):
            ob.parent = empty
            grp.objects.link(ob)

    #Clean up
    gen.show_x_ray = True
    gen.data.draw_type = 'STICK'
    gen.MhxRigify = False
    name = rig.name
    scn.objects.unlink(rig)
    del rig
    gen.name = name
    gen.data.layers[1] = False    # Face components
    bpy.ops.object.mode_set(mode='POSE')
    print("MHX rig %s successfully rigified" % name)
    return gen


def setBoneName(bone, gen):
    fkname = bone.name.replace(".", ".fk.")
    try:
        gen.data.bones[fkname]
        bone.fkname = fkname
        bone.ikname = fkname.replace(".fk.", ".ik")
    except KeyError:
        pass

    defname = "DEF-" + bone.name
    try:
        gen.data.bones[defname]
        bone.realname = defname
        return
    except KeyError:
        pass

    defname1 = "DEF-" + bone.name + ".01"
    try:
        gen.data.bones[defname1]
        bone.realname1 = defname1
        bone.realname2 = defname1.replace(".01.", ".02.")
        return
    except KeyError:
        pass

    defname1 = "DEF-" + bone.name.replace(".", ".01.")
    try:
        gen.data.bones[defname1]
        bone.realname1 = defname1
        bone.realname2 = defname1.replace(".01.", ".02")
        return
    except KeyError:
        pass

    try:
        gen.data.edit_bones[bone.name]
        bone.realname = bone.name
    except KeyError:
        pass


def fixConstraint(cns1, cns2, gen, bones):
    for key in dir(cns1):
        if ((key[0] != "_") and
            (key not in ["bl_rna", "type", "rna_type", "is_valid", "error_location", "error_rotation"])):
            expr = ("cns2.%s = cns1.%s" % (key, key))
            setattr(cns2, key, getattr(cns1, key))

    try:
        cns2.target = gen
    except AttributeError:
        pass

    if cns1.type == 'STRETCH_TO':
        bone = bones[cns1.subtarget]
        if bone.realname:
            cns2.subtarget = bone.realname
            cns2.head_tail = cns1.head_tail
        elif not bone.realname1:
            raise RuntimeError("Cannot fix STRETCH_TO constraint for bone %s" % (bone))
        elif cns1.head_tail < 0.5:
            cns2.subtarget = bone.realname1
            cns2.head_tail = 2*cns1.head_tail
        else:
            cns2.subtarget = bone.realname2
            cns2.head_tail = 2*cns1.head_tail-1

    elif cns1.type == 'TRANSFORM':
        bone = bones[cns1.subtarget]
        if bone.fkname:
            cns2.subtarget = bone.fkname
        elif bone.ikname:
            cns2.subtarget = bone.ikname
        else:
            cns2.subtarget = bone.realname


def copyDriver(fcu1, fcu2, id):
    drv1 = fcu1.driver
    drv2 = fcu2.driver

    for var1 in drv1.variables:
        var2 = drv2.variables.new()
        var2.name = var1.name
        var2.type = var1.type
        targ1 = var1.targets[0]
        targ2 = var2.targets[0]
        targ2.id = id
        targ2.data_path = targ1.data_path

    drv2.type = drv1.type
    drv2.expression = drv1.expression
    drv2.show_debug_info = drv1.show_debug_info


def changeDriverTarget(fcu, id):
    for var in fcu.driver.variables:
        targ = var.targets[0]
        targ.id = id


'''
#
#   class OBJECT_OT_RigifyMhxButton(bpy.types.Operator):
#

class OBJECT_OT_RigifyMhxButton(bpy.types.Operator):
    bl_idname = "mhxrig.rigify_mhx"
    bl_label = "Rigify MHX rig"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            rigifyMhx(context)
        except MhxError as err:
            print("Error when rigifying mhx rig: %s" % err)
        return{'FINISHED'}

#
#   class RigifyMhxPanel(bpy.types.Panel):
#

class RigifyMhxPanel(bpy.types.Panel):
    bl_label = "Rigify MHX"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRigify)

    def draw(self, context):
        self.layout.operator("mhxrig.rigify_mhx")
        return

'''
