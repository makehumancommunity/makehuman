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

bl_info = {
    'name': 'MakeHuman: MHX Runtime (.mhx)',
    'author': 'Thomas Larsson',
    'version': (1,1,0),
    "blender": (2, 71, 0),
    "location": "View3D > Properties > MHX Runtime",
    'description': 'Runtime support for characters imported with the MakeHuman eXchange format (.mhx)',
    'warning': '',
    'wiki_url': 'http://makehuman.org/doc/node/makehuman_blender.html',
    'category': 'MakeHuman'}


if "bpy" in locals():
    print("Reloading MakeHuman runtime v %d.%d.%d" % bl_info["version"])
    import imp
    imp.reload(utils)
    #imp.reload(error)
    imp.reload(layers)
    imp.reload(fkik)
    imp.reload(drivers)
    #imp.reload(bone_drivers)
    #imp.reload(faceshift)
    imp.reload(hide)
    imp.reload(shapekeys)
    imp.reload(merge)
else:
    print("Loading MakeHuman runtime v %d.%d.%d" % bl_info["version"])
    from . import utils
    #from . import error
    from . import layers
    from . import fkik
    from . import drivers
    #from . import bone_drivers
    #from . import faceshift
    from . import hide
    from . import shapekeys
    from . import merge

import bpy
from bpy.props import *

#------------------------------------------------------------------------
#    Setup panel
#------------------------------------------------------------------------

class MhxSetupPanel(bpy.types.Panel):
    bl_label = "MHX Setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX Runtime"

    @classmethod
    def poll(cls, context):
        return context.object

    def draw(self, context):
        layout = self.layout
        ob = context.object

        layout.operator("mhx.fix_hide_names")
        if ob.type == 'MESH':
            layout.separator()
            layout.operator("mhx.merge_objects")

        layout.separator()
        layout.operator("mhx.add_hide_drivers")
        layout.operator("mhx.remove_hide_drivers")

        #layout.separator()
        #layout.operator("mhx.add_facerig_drivers")
        #layout.operator("mhx.remove_facerig_drivers")
        #layout.operator("mhx.load_faceshift_bvh")

        layout.separator()
        layout.operator("mhx.add_shapekey_drivers")
        layout.operator("mhx.remove_shapekey_drivers")



#------------------------------------------------------------------------
#    Mhx Labels Panel
#------------------------------------------------------------------------

from .layers import MhxLayers, OtherLayers

class MhxLabelsPanel(bpy.types.Panel):
    bl_label = "Labels"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig)

    def draw(self, context):
        layout = self.layout
        layout.label("Layers")
        layout.operator("mhx.pose_enable_all_layers")
        layout.operator("mhx.pose_disable_all_layers")

        rig = context.object
        if rig.MhxRig == 'MHX':
            layers = MhxLayers
        else:
            layers = OtherLayers

        for (left,right) in layers:
            row = layout.row()
            if type(left) == str:
                row.label(left)
                row.label(right)
            else:
                for (n, name, prop) in [left,right]:
                    row.prop(rig.data, "layers", index=n, toggle=True, text=name)

        return
        layout.separator()
        layout.label("Export/Import MHP")
        layout.operator("mhx.saveas_mhp")
        layout.operator("mhx.load_mhp")


#------------------------------------------------------------------------
#    Mhx FK/IK switch panel
#------------------------------------------------------------------------

class MhxFKIKPanel(bpy.types.Panel):
    bl_label = "FK/IK Switch"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig == 'MHX')

    def draw(self, context):
        rig = context.object
        layout = self.layout

        row = layout.row()
        row.label("")
        row.label("Left")
        row.label("Right")

        layout.label("FK/IK switch")
        row = layout.row()
        row.label("Arm")
        self.toggleButton(row, rig, "MhaArmIk_L", " 3", " 2")
        self.toggleButton(row, rig, "MhaArmIk_R", " 19", " 18")
        row = layout.row()
        row.label("Leg")
        self.toggleButton(row, rig, "MhaLegIk_L", " 5", " 4")
        self.toggleButton(row, rig, "MhaLegIk_R", " 21", " 20")

        layout.label("IK Influence")
        row = layout.row()
        row.label("Arm")
        row.prop(rig, '["MhaArmIk_L"]', text="")
        row.prop(rig, '["MhaArmIk_R"]', text="")
        row = layout.row()
        row.label("Leg")
        row.prop(rig, '["MhaLegIk_L"]', text="")
        row.prop(rig, '["MhaLegIk_R"]', text="")

        try:
            ok = (rig["MhxVersion"] >= 12)
        except:
            ok = False
        if not ok:
            layout.label("Snapping only works with MHX version 1.12 and later.")
            return

        layout.separator()
        layout.label("Snapping")
        row = layout.row()
        row.label("Rotation Limits")
        row.prop(rig, '["MhaRotationLimits"]', text="")
        row.prop(rig, "MhxSnapExact", text="Exact Snapping")

        layout.label("Snap Arm bones")
        row = layout.row()
        row.label("FK Arm")
        row.operator("mhx.snap_fk_ik", text="Snap L FK Arm").data = "MhaArmIk_L 2 3 12"
        row.operator("mhx.snap_fk_ik", text="Snap R FK Arm").data = "MhaArmIk_R 18 19 28"
        row = layout.row()
        row.label("IK Arm")
        row.operator("mhx.snap_ik_fk", text="Snap L IK Arm").data = "MhaArmIk_L 2 3 12"
        row.operator("mhx.snap_ik_fk", text="Snap R IK Arm").data = "MhaArmIk_R 18 19 28"

        layout.label("Snap Leg bones")
        row = layout.row()
        row.label("FK Leg")
        row.operator("mhx.snap_fk_ik", text="Snap L FK Leg").data = "MhaLegIk_L 4 5 12"
        row.operator("mhx.snap_fk_ik", text="Snap R FK Leg").data = "MhaLegIk_R 20 21 28"
        row = layout.row()
        row.label("IK Leg")
        row.operator("mhx.snap_ik_fk", text="Snap L IK Leg").data = "MhaLegIk_L 4 5 12"
        row.operator("mhx.snap_ik_fk", text="Snap R IK Leg").data = "MhaLegIk_R 20 21 28"


    def toggleButton(self, row, rig, prop, fk, ik):
        if rig[prop] > 0.5:
            row.operator("mhx.toggle_fk_ik", text="IK").toggle = prop + " 0" + fk + ik
        else:
            row.operator("mhx.toggle_fk_ik", text="FK").toggle = prop + " 1" + ik + fk


#------------------------------------------------------------------------
#   Visibility panel
#------------------------------------------------------------------------

class VisibilityPanel(bpy.types.Panel):
    bl_label = "Visibility"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxVisibilityDrivers)

    def draw(self, context):
        ob = context.object
        layout = self.layout
        layout.operator("mhx.prettify_visibility")
        props = list(ob.keys())
        props.sort()
        for prop in props:
            if prop[0:3] == "Mhh":
                if hasattr(ob, prop):
                    path = prop
                else:
                    path = '["%s"]' % prop
                layout.prop(ob, path, text=prop[3:])

'''
#------------------------------------------------------------------------
#   Facerig panel
#------------------------------------------------------------------------

class FaceComponentsPanel(bpy.types.Panel):
    bl_label = "Face Components"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxFaceRigDrivers)

    def draw(self, context):
        drawPropPanel(self, context.object, "Mfa")

#------------------------------------------------------------------------
#   Shapekey panel
#------------------------------------------------------------------------

class MhxShapekeyPanel(bpy.types.Panel):
    bl_label = "Shapekeys"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MHX Runtime"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxShapekeyDrivers)

    def draw(self, context):
        drawPropPanel(self, context.object, "Mhs")

#------------------------------------------------------------------------
#   Common drawing code for property panels
#------------------------------------------------------------------------

def drawPropPanel(self, ob, prefix):
    from .drivers import getArmature
    rig = getArmature(ob)
    if rig:
        layout = self.layout
        layout.operator("mhx.reset_props").prefix = prefix
        for prop in rig.keys():
            if prop[0:3] != prefix:
                continue
            row = layout.split(0.8)
            row.prop(rig, '["%s"]' % prop, text=prop[3:])
            op = row.operator("mhx.pin_prop", icon='UNPINNED')
            op.key = prop
            op.prefix = prefix
'''
#------------------------------------------------------------------------
#   Init
#------------------------------------------------------------------------

def register():
    bpy.types.Object.MhxRig = StringProperty(default="")
    bpy.types.Object.MhxMesh = BoolProperty(default=False)
    bpy.types.Object.MhxSnapExact = BoolProperty(default=False)
    bpy.types.Object.MhxVisibilityDrivers = BoolProperty(default=False)
    bpy.types.Object.MhxShapekeyDrivers = BoolProperty(default=False)
    bpy.types.Object.MhxFaceRigDrivers = BoolProperty(default=False)

    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()


print("MHX runtime successfully (re)loaded")
