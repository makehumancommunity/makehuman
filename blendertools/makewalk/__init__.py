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

"""
Abstract
Tool for loading bvh files onto the MHX rig in Blender 2.5x

Place the script in the .blender/scripts/addons dir
Activate the script in the "Add-Ons" tab (user preferences).
Access from UI panel (N-key) when MHX rig is active.

Alternatively, run the script in the script editor (Alt-P), and access from UI panel.
"""

bl_info = {
    "name": "MakeWalk",
    "author": "Thomas Larsson",
    "version": (0, 943),
    "blender": (2, 6, 9),
    "location": "View3D > Tools > MakeWalk",
    "description": "Mocap tool for MakeHuman character",
    "warning": "",
    'wiki_url': "http://www.makehuman.org/doc/node/makewalk.html",
    "category": "MakeHuman"}

# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
    print("Reloading MakeWalk v %d.%d" % bl_info["version"])
    import imp
    imp.reload(utils)
    imp.reload(io_json)
    imp.reload(props)
    imp.reload(t_pose)
    imp.reload(armature)
    imp.reload(source)
    imp.reload(target)
    imp.reload(load)
    imp.reload(retarget)
    imp.reload(fkik)
    imp.reload(simplify)
    imp.reload(action)
    imp.reload(loop)
    imp.reload(edit)
    imp.reload(floor)
else:
    print("Loading MakeWalk v %d.%d" % bl_info["version"])
    import bpy, os
    from bpy_extras.io_utils import ImportHelper
    from bpy.props import *

    from . import utils
    from . import io_json
    from . import props
    from . import t_pose
    from . import armature
    from . import source
    from . import target
    from . import load
    from . import retarget
    from . import fkik
    from . import simplify
    from . import action
    from . import loop
    from . import edit
    from . import floor


def inset(layout):
    split = layout.split(0.05)
    split.label("")
    return split.column()

########################################################################
#
#   class MainPanel(bpy.types.Panel):
#

class MainPanel(bpy.types.Panel):
    bl_label = "MakeWalk v %d.%d: Main" % bl_info["version"]
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        layout = self.layout
        ob = context.object
        scn = context.scene
        if ob and ob.type == 'ARMATURE':
            layout.operator("mcp.load_and_retarget")
            layout.separator()
            layout.prop(scn, "McpStartFrame")
            layout.prop(scn, "McpEndFrame")
            layout.separator()
            layout.prop(scn, "McpShowDetailSteps")
            if scn.McpShowDetailSteps:
                ins = inset(layout)
                ins.operator("mcp.load_bvh")
                ins.operator("mcp.rename_bvh")
                ins.operator("mcp.load_and_rename_bvh")

                ins.separator()
                ins.operator("mcp.retarget_mhx")

                ins.separator()
                ins.operator("mcp.simplify_fcurves")
                ins.operator("mcp.rescale_fcurves")

        else:
            layout.operator("mcp.load_bvh")
            layout.separator()
            layout.prop(scn, "McpStartFrame")
            layout.prop(scn, "McpEndFrame")

########################################################################
#
#   class OptionsPanel(bpy.types.Panel):
#

class OptionsPanel(bpy.types.Panel):
    bl_label = "MakeWalk: Options"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.object and context.object.type == 'ARMATURE':
            return True

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        rig = context.object

        layout.prop(scn, "McpAutoScale")
        layout.prop(scn, "McpBvhScale")
        layout.prop(scn, "McpUseLimits")
        layout.prop(scn, "McpClearLocks")
        layout.prop(scn, "McpMakeHumanTPose")
        layout.prop(scn, 'McpAutoSourceRig')
        layout.prop(scn, 'McpAutoTargetRig')
        layout.prop(scn, "McpIgnoreHiddenLayers")
        layout.prop(scn, "McpDoBendPositive")

        layout.separator()
        layout.label("SubSample and Rescale")
        ins = inset(layout)
        ins.prop(scn, "McpDefaultSS")
        if not scn.McpDefaultSS:
            ins.prop(scn, "McpSubsample")
            ins.prop(scn, "McpSSFactor")
            ins.prop(scn, "McpRescale")
            ins.prop(scn, "McpRescaleFactor")
            ins.operator("mcp.rescale_fcurves")

        layout.separator()
        layout.label("Simplification")
        ins = inset(layout)
        ins.prop(scn, "McpDoSimplify")
        ins.prop(scn, "McpErrorLoc")
        ins.prop(scn, "McpErrorRot")
        ins.prop(scn, "McpSimplifyVisible")
        ins.prop(scn, "McpSimplifyMarkers")


########################################################################
#
#   class EditPanel(bpy.types.Panel):
#

class EditPanel(bpy.types.Panel):
    bl_label = "MakeWalk: Edit Actions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.object and context.object.type == 'ARMATURE':
            return True

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        rig = context.object

        layout.prop(scn, "McpShowIK")
        if scn.McpShowIK:
            ins = inset(layout)
            row = ins.row()
            row.prop(scn, "McpFkIkArms")
            row.prop(scn, "McpFkIkLegs")
            ins.operator("mcp.transfer_to_ik")
            ins.operator("mcp.transfer_to_fk")
            ins.operator("mcp.clear_animation", text="Clear IK Animation").type = "IK"
            ins.operator("mcp.clear_animation", text="Clear FK Animation").type = "FK"

        layout.separator()
        layout.prop(scn, "McpShowGlobal")
        if scn.McpShowGlobal:
            ins = inset(layout)
            ins.operator("mcp.shift_bone")

            #ins.separator()
            #row = ins.row()
            #row.prop(scn, "McpBendElbows")
            #row.prop(scn, "McpBendKnees")
            #ins.operator("mcp.limbs_bend_positive")

            ins.separator()
            row = ins.row()
            row.prop(scn, "McpFixX")
            row.prop(scn, "McpFixY")
            row.prop(scn, "McpFixZ")
            ins.operator("mcp.fixate_bone")

            ins.separator()
            ins.prop(scn, "McpRescaleFactor")
            ins.operator("mcp.rescale_fcurves")

        layout.separator()
        layout.prop(scn, "McpShowDisplace")
        if scn.McpShowDisplace:
            ins = inset(layout)
            ins.operator("mcp.start_edit")
            ins.operator("mcp.undo_edit")

            row = ins.row()
            props = row.operator("mcp.insert_key", text="Loc")
            props.loc = True
            props.rot = False
            props.delete = False
            props = row.operator("mcp.insert_key", text="Rot")
            props.loc = False
            props.rot = True
            props.delete = False
            row = ins.row()
            props = row.operator("mcp.insert_key", text="LocRot")
            props.loc = True
            props.rot = True
            props.delete = False
            props = row.operator("mcp.insert_key", text="Delete")
            props.loc = True
            props.rot = True
            props.delete = True

            row = ins.row()
            props = row.operator("mcp.move_to_marker", text="|<")
            props.left = True
            props.last = True
            props = row.operator("mcp.move_to_marker", text="<")
            props.left = True
            props.last = False
            props = row.operator("mcp.move_to_marker", text=">")
            props.left = False
            props.last = False
            props = row.operator("mcp.move_to_marker", text=">|")
            props.left = False
            props.last = True

            ins.operator("mcp.confirm_edit")

        layout.separator()
        layout.prop(scn, "McpShowFeet")
        if scn.McpShowFeet:
            ins = inset(layout)
            row = ins.row()
            row.prop(scn, "McpFloorLeft")
            row.prop(scn, "McpFloorRight")
            row.prop(scn, "McpFloorHips")
            ins.operator("mcp.offset_toe")
            ins.operator("mcp.floor_foot")

        layout.separator()
        layout.prop(scn, "McpShowLoop")
        if scn.McpShowLoop:
            ins = inset(layout)
            ins.prop(scn, "McpLoopBlendRange")
            ins.prop(scn, "McpLoopInPlace")
            ins.operator("mcp.loop_fcurves")

            ins.separator()
            ins.prop(scn, "McpRepeatNumber")
            ins.operator("mcp.repeat_fcurves")

        layout.separator()
        layout.prop(scn, "McpShowStitch")
        if scn.McpShowStitch:
            ins = inset(layout)
            ins.operator("mcp.update_action_list")
            ins.separator()
            ins.prop(scn, "McpFirstAction")
            split = ins.split(0.75)
            split.prop(scn, "McpFirstEndFrame")
            split.operator("mcp.set_current_action").prop = "McpFirstAction"
            ins.separator()
            ins.prop(scn, "McpSecondAction")
            split = ins.split(0.75)
            split.prop(scn, "McpSecondStartFrame")
            split.operator("mcp.set_current_action").prop = "McpSecondAction"
            ins.separator()
            ins.prop(scn, "McpLoopBlendRange")
            ins.prop(scn, "McpOutputActionName")
            ins.operator("mcp.stitch_actions")

########################################################################
#
#    class MhxSourceBonesPanel(bpy.types.Panel):
#

class MhxSourceBonesPanel(bpy.types.Panel):
    bl_label = "MakeWalk: Source armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        rig = context.object

        if not source.isSourceInited(scn):
            layout.operator("mcp.init_sources", text="Init Source Panel")
            return
        layout.operator("mcp.init_sources", text="Reinit Source Panel")
        layout.prop(scn, 'McpAutoSourceRig')
        layout.prop(scn, "McpSourceRig")

        if scn.McpSourceRig:
            from .source import getSourceArmature

            amt = getSourceArmature(scn.McpSourceRig)
            if amt:
                bones = amt.boneNames
                box = layout.box()
                for boneText in target.TargetBoneNames:
                    if not boneText:
                        box.separator()
                        continue
                    (mhx, text) = boneText
                    bone = source.findSourceKey(mhx, bones)
                    if bone:
                        row = box.row()
                        row.label(text)
                        row.label(bone)

########################################################################
#
#    class MhxTargetBonesPanel(bpy.types.Panel):
#

class MhxTargetBonesPanel(bpy.types.Panel):
    bl_label = "MakeWalk: Target armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'ARMATURE')

    def draw(self, context):
        layout = self.layout
        rig = context.object
        scn = context.scene

        if not target.isTargetInited(scn):
            layout.operator("mcp.init_targets", text="Init Target Panel")
            return
        layout.operator("mcp.init_targets", text="Reinit Target Panel")
        layout.separator()
        layout.prop(scn, "McpTargetRig")
        layout.prop(scn, 'McpAutoTargetRig')

        layout.separator()
        layout.prop(scn, "McpIgnoreHiddenLayers")
        layout.prop(rig, "MhReverseHip")
        layout.operator("mcp.get_target_rig")

        layout.separator()
        layout.operator("mcp.set_t_pose")

        layout.separator()
        layout.prop(scn, "McpSaveTargetTPose")
        layout.operator("mcp.save_target_file")
        layout.separator()

        if scn.McpTargetRig:
            from .target import getTargetInfo

            (bones, ikBones, tpose) = getTargetInfo(scn.McpTargetRig)

            layout.label("FK bones")
            box = layout.box()
            for boneText in target.TargetBoneNames:
                if not boneText:
                    box.separator()
                    continue
                (mhx, text) = boneText
                bone = target.findTargetKey(mhx, bones)
                row = box.row()
                row.label(text)
                if bone:
                    row.label(bone)
                else:
                    row.label("-")

            if ikBones:
                row = layout.row()
                row.label("IK bone")
                row.label("FK bone")
                box = layout.box()
                for (ikBone, fkBone) in ikBones:
                    row = box.row()
                    row.label(ikBone)
                    row.label(fkBone)
        return

########################################################################
#
#   class UtilityPanel(bpy.types.Panel):
#

class UtilityPanel(bpy.types.Panel):
    bl_label = "MakeWalk: Utilities"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.object and context.object.type == 'ARMATURE':
            return True

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        rig = context.object

        layout.label("Default Settings")
        #layout.operator("mcp.init_interface")
        layout.operator("mcp.save_defaults")
        layout.operator("mcp.load_defaults")

        layout.separator()
        layout.label("Manage Actions")
        layout.prop_menu_enum(context.scene, "McpActions")
        layout.prop(scn, 'McpFilterActions')
        layout.operator("mcp.update_action_list")
        layout.operator("mcp.set_current_action").prop = 'McpActions'
        #layout.prop(scn, "McpReallyDelete")
        layout.operator("mcp.delete")
        layout.operator("mcp.delete_hash")

        layout.separator()
        layout.operator("mcp.clear_temp_props")

        layout.separator()
        layout.label("T-pose")
        layout.operator("mcp.set_t_pose")
        layout.operator("mcp.clear_t_pose")
        layout.operator("mcp.load_t_pose")
        layout.operator("mcp.save_t_pose")

        layout.separator()
        layout.label("Rest Pose")
        layout.operator("mcp.rest_current_pose")
        #layout.operator("mcp.rest_t_pose")
        #layout.operator("mcp.rest_default_pose")

        return
        layout.operator("mcp.copy_angles_fk_ik")

        layout.separator()
        layout.label("Batch conversion")
        layout.prop(scn, "McpDirectory")
        layout.prop(scn, "McpPrefix")
        layout.operator("mcp.batch")

#
#    init
#

props.initInterface(bpy.context)

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

print("MakeWalk loaded")

