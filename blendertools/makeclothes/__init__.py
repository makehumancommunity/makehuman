#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Utility for making clothes to MH characters.
"""

bl_info = {
    "name": "Make Clothes",
    "author": "Thomas Larsson",
    "version": (0, 949),
    "blender": (2, 6, 9),
    "location": "View3D > Properties > Make MH clothes",
    "description": "Make clothes and UVs for MakeHuman characters",
    "warning": "",
    'wiki_url': "http://makehuman.org/doc/node/makeclothes.html",
    "category": "MakeHuman"}


if "bpy" in locals():
    print("Reloading makeclothes v %d.%d" % bl_info["version"])
    import imp
    imp.reload(maketarget)
    imp.reload(mc)
    imp.reload(materials)
    imp.reload(makeclothes)
    imp.reload(project)
else:
    print("Loading makeclothes v %d.%d" % bl_info["version"])
    import bpy
    import os
    from bpy.props import *
    import maketarget
    from .error import MHError, handleMHError, initWarnings, handleWarnings
    from maketarget.utils import drawFileCheck
    from . import mc
    from . import materials
    from . import makeclothes
    from . import project


def setObjectMode(context):
    if context.object:
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            return


def invokeWithFileCheck(self, context, ftypes):
    try:
        ob = makeclothes.getClothing(context)
        scn = context.scene
        for ftype in ftypes:
            (outpath, outfile) = mc.getFileName(ob, scn.MhClothesDir, ftype)
            filepath = os.path.join(outpath, outfile)
            if os.path.exists(filepath):
                break
        return maketarget.utils.invokeWithFileCheck(self, context, filepath)
    except MHError:
        handleMHError(context)
        return {'FINISHED'}

#
#    class MakeClothesPanel(bpy.types.Panel):
#


def inset(layout):
    split = layout.split(0.05)
    split.label("")
    return split.column()


class MakeClothesPanel(bpy.types.Panel):
    bl_label = "Make Clothes version %d.%d" % bl_info["version"]
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        ob = context.object

        #layout.operator("mhclo.snap_selected_verts")

        layout.prop(scn, "MCBodyType", text="Type")
        layout.operator("mhclo.load_human")

        if not (ob and ob.type == 'MESH'):
            return

        layout.separator()
        row = layout.row()
        row.label("Mesh Type:")
        if ob and ob.MhHuman:
            row.operator("mhclo.set_human", text="Human").isHuman = False
            layout.separator()
            layout.operator("mhclo.auto_vertex_groups", text="Create Vertex Groups From Selection")
        else:
            row.operator("mhclo.set_human", text="Clothing").isHuman = True
            layout.separator()
            layout.operator("mhclo.auto_vertex_groups")

        layout.separator()
        layout.operator("mhclo.make_clothes")
        layout.separator()

        layout.prop(scn, "MCShowSelect")
        if scn.MCShowSelect:
            ins = inset(layout)
            props = ins.operator("mhclo.select_human_part", text="Select Body")
            props.btype = 'Body'

            for helper in ["Tights", "Skirt", "Coat", "Hair", "Joints"]:
                props = ins.operator("mhclo.select_human_part", text="Select %s" % helper)
                props.btype = 'Helpers'
                props.htype = helper


        layout.prop(scn, "MCShowMaterials")
        if scn.MCShowMaterials:
            ins = inset(layout)
            ins.operator("mhclo.export_material")
            ins.separator()

        '''
        layout.prop(scn, "MCShowAdvanced")
        if scn.MCShowAdvanced:
            ins = inset(layout)
            ins.label("Algorithm Control")
            row = ins.row()
            row.prop(scn, "MCThreshold")
            row.prop(scn, "MCListLength")
            ins.separator()
        '''

        layout.prop(scn, "MCShowUVProject")
        if scn.MCShowUVProject:
            ins = inset(layout)
            ins.operator("mhclo.create_seam_object")
            ins.operator("mhclo.auto_seams")
            ins.operator("mhclo.project_uvs")
            ins.operator("mhclo.reexport_files")
            ins.separator()

        layout.prop(scn, "MCShowZDepth")
        if scn.MCShowZDepth:
            ins = inset(layout)
            ins.prop(scn, "MCZDepthName")
            ins.operator("mhclo.set_zdepth")
            ins.prop(scn, "MCZDepth")
            ins.separator()

        layout.prop(scn, "MCShowBoundary")
        if scn.MCShowBoundary:
            ins = inset(layout)
            ins.prop(scn, "MCScaleUniform")
            ins.prop(scn, "MCScaleCorrect")
            ins.separator()
            ins.prop(scn, "MCBodyPart")
            vnums = makeclothes.getBodyPartVerts(scn)
            self.drawXYZ(vnums[0], "X", ins)
            self.drawXYZ(vnums[1], "Y", ins)
            self.drawXYZ(vnums[2], "Z", ins)
            ins.operator("mhclo.examine_boundary")

            ins.separator()
            ins.label("Custom Boundary")
            row = ins.row()
            row.prop(scn, "MCCustomX1")
            row.prop(scn, "MCCustomX2")
            row = ins.row()
            row.prop(scn, "MCCustomY1")
            row.prop(scn, "MCCustomY2")
            row = ins.row()
            row.prop(scn, "MCCustomZ1")
            row.prop(scn, "MCCustomZ2")
            ins.separator()
            ins.operator("mhclo.print_vnums")
            ins.separator()

        layout.prop(scn, "MCShowSettings")
        if scn.MCShowSettings:
            ins = inset(layout)
            ins.operator("mhclo.factory_settings").prefix = "MC"
            ins.operator("mhclo.read_settings").tool = "make_clothes"
            props = ins.operator("mhclo.save_settings")
            props.tool = "make_clothes"
            props.prefix = "MC"
            ins.label("Output Directory")
            ins.prop(scn, "MhClothesDir", text="")
            ins.separator()

        layout.prop(scn, "MCShowLicense")
        if scn.MCShowLicense:
            ins = inset(layout)
            ins.prop(scn, "MCAuthor")
            ins.prop(scn, "MCLicense")
            ins.prop(scn, "MCHomePage")
            ins.label("Tags")
            ins.prop(scn, "MCTag1")
            ins.prop(scn, "MCTag2")
            ins.prop(scn, "MCTag3")
            ins.prop(scn, "MCTag4")
            ins.prop(scn, "MCTag5")
            ins.separator()

        '''
        layout.prop(scn, "MCShowUtils")
        if scn.MCShowUtils:
            ins = inset(layout)
            #ins.operator("mhclo.copy_vert_locs")
            ins.separator()
        '''

        if not scn.MCUseInternal:
            return
        ins.separator()
        ins.label("For internal use")
        ins.prop(scn, "MCLogging")
        ins.prop(scn, "MhProgramPath")
        ins.prop(scn, "MCSelfClothed")
        ins.operator("mhclo.select_helpers")
        ins.operator("mhclo.export_base_uvs_py")


    def drawXYZ(self, pair, name, layout):
        m,n = pair
        row = layout.row()
        row.label("%s1:   %d" % (name,m))
        row.label("%s2:   %d" % (name,n))


#----------------------------------------------------------
#   Settings buttons
#----------------------------------------------------------

class OBJECT_OT_FactorySettingsButton(bpy.types.Operator):
    bl_idname = "mhclo.factory_settings"
    bl_label = "Restore Factory Settings"

    prefix = StringProperty()

    def execute(self, context):
        maketarget.settings.restoreFactorySettings(context, self.prefix)
        return{'FINISHED'}


class OBJECT_OT_SaveSettingsButton(bpy.types.Operator):
    bl_idname = "mhclo.save_settings"
    bl_label = "Save Settings"

    tool = StringProperty()
    prefix = StringProperty()

    def execute(self, context):
        maketarget.settings.saveDefaultSettings(context, self.tool, self.prefix)
        return{'FINISHED'}


class OBJECT_OT_ReadSettingsButton(bpy.types.Operator):
    bl_idname = "mhclo.read_settings"
    bl_label = "Read Settings"

    tool = StringProperty()

    def execute(self, context):
        maketarget.settings.readDefaultSettings(context, self.tool)
        return{'FINISHED'}

#----------------------------------------------------------
#
#----------------------------------------------------------
#
#    class OBJECT_OT_SnapSelectedVertsButton(bpy.types.Operator):
#

class OBJECT_OT_SnapSelectedVertsButton(bpy.types.Operator):
    bl_idname = "mhclo.snap_selected_verts"
    bl_label = "Snap Selected"
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        makeclothes.snapSelectedVerts(context)
        return{'FINISHED'}

#
#    class OBJECT_OT_MakeClothesButton(bpy.types.Operator):
#

class OBJECT_OT_MakeClothesButton(bpy.types.Operator):
    bl_idname = "mhclo.make_clothes"
    bl_label = "Make Clothes"
    bl_options = {'UNDO'}

    filepath = StringProperty(default="")

    def execute(self, context):
        setObjectMode(context)
        try:
            initWarnings()
            makeclothes.makeClothes(context, True)
            makeclothes.exportObjFile(context)
            handleWarnings()
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

    def invoke(self, context, event):
        return invokeWithFileCheck(self, context, ["mhclo", "obj"])

    def draw(self, context):
        drawFileCheck(self)


class OBJECT_OT_ExportMaterialButton(bpy.types.Operator):
    bl_idname = "mhclo.export_material"
    bl_label = "Export Material Only"
    bl_options = {'UNDO'}

    filepath = StringProperty(default="")

    def execute(self, context):
        setObjectMode(context)
        try:
            matfile = materials.writeMaterial(context.object, context.scene.MhClothesDir)
            print("Exported \"%s\"" % matfile)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

    def invoke(self, context, event):
        return invokeWithFileCheck(self, context, ["mhmat"])

    def draw(self, context):
        drawFileCheck(self)

#
#   class OBJECT_OT_CopyVertLocsButton(bpy.types.Operator):
#

class OBJECT_OT_CopyVertLocsButton(bpy.types.Operator):
    bl_idname = "mhclo.copy_vert_locs"
    bl_label = "Copy Vertex Locations"
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        src = context.object
        for trg in context.scene.objects:
            if trg != src and trg.select and trg.type == 'MESH':
                print("Copy vertex locations from %s to %s" % (src.name, trg.name))
                for n,sv in enumerate(src.data.vertices):
                    tv = trg.data.vertices[n]
                    tv.co = sv.co
                print("Vertex locations copied")
        return{'FINISHED'}


#
#   class OBJECT_OT_ExportBaseUvsPyButton(bpy.types.Operator):
#   class OBJECT_OT_SplitHumanButton(bpy.types.Operator):
#

class OBJECT_OT_ExportBaseUvsPyButton(bpy.types.Operator):
    bl_idname = "mhclo.export_base_uvs_py"
    bl_label = "Export Base UV Py File"
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            makeclothes.exportBaseUvsPy(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

class OBJECT_OT_SelectHelpersButton(bpy.types.Operator):
    bl_idname = "mhclo.select_helpers"
    bl_label = "Select Helpers"
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            makeclothes.selectHelpers(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#    class OBJECT_OT_MakeHumanButton(bpy.types.Operator):
#

class OBJECT_OT_MakeHumanButton(bpy.types.Operator):
    bl_idname = "mhclo.set_human"
    bl_label = "Make Human"
    bl_options = {'UNDO'}
    isHuman = BoolProperty()

    def execute(self, context):
        setObjectMode(context)
        try:
            ob = context.object
            if self.isHuman:
                nverts = len(ob.data.vertices)
                okVerts = makeclothes.getLastVertices()
                if nverts in okVerts:
                    ob.MhHuman = True
                else:
                    raise MHError(
                        "Illegal number of vertices: %d\n" % nverts +
                        "An MakeHuman human must have\n" +
                        "".join(["  %d\n" % n for n in okVerts]) +
                        "vertices"
                        )
            else:
                ob.MhHuman = False
            print("Object %s: Human = %s" % (ob.name, ob.MhHuman))
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#    class OBJECT_OT_LoadHumanButton(bpy.types.Operator):
#

class OBJECT_OT_LoadHumanButton(bpy.types.Operator):
    bl_idname = "mhclo.load_human"
    bl_label = "Load Human Mesh"
    bl_options = {'UNDO'}
    helpers = BoolProperty()

    def execute(self, context):
        setObjectMode(context)
        try:
            makeclothes.loadHuman(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#    class OBJECT_OT_ExamineBoundaryButton(bpy.types.Operator):
#

class OBJECT_OT_ExamineBoundaryButton(bpy.types.Operator):
    bl_idname = "mhclo.examine_boundary"
    bl_label = "Examine Boundary"
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            makeclothes.examineBoundary(context.object, context.scene)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#    class OBJECT_OT_SetZDepthButton(bpy.types.Operator):
#

class OBJECT_OT_SetZDepthButton(bpy.types.Operator):
    bl_idname = "mhclo.set_zdepth"
    bl_label = "Set Z Depth"
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            makeclothes.setZDepth(context.scene)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#    class VIEW3D_OT_SelectHumanPartButton(bpy.types.Operator):
#

class VIEW3D_OT_SelectHumanPartButton(bpy.types.Operator):
    bl_idname = "mhclo.select_human_part"
    bl_label = "Select Human Part"
    bl_options = {'UNDO'}

    btype = StringProperty()
    htype = StringProperty()

    def execute(self, context):
        setObjectMode(context)
        try:
            makeclothes.selectHumanPart(context.object, self.btype, self.htype)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#    class VIEW3D_OT_PrintVnumsButton(bpy.types.Operator):
#

class VIEW3D_OT_PrintVnumsButton(bpy.types.Operator):
    bl_idname = "mhclo.print_vnums"
    bl_label = "Print Vertex Numbers"
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            makeclothes.printVertNums(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#    class VIEW3D_OT_DeleteHelpersButton(bpy.types.Operator):
#

class VIEW3D_OT_DeleteHelpersButton(bpy.types.Operator):
    bl_idname = "mhclo.delete_helpers"
    bl_label = "Delete Helpers Until Above"
    bl_options = {'UNDO'}
    answer = StringProperty()

    def execute(self, context):
        setObjectMode(context)
        ob = context.object
        scn = context.scene
        if makeclothes.isHuman(ob):
            makeclothes.deleteHelpers(context)
        return{'FINISHED'}

#
#   class VIEW3D_OT_AutoVertexGroupsButton(bpy.types.Operator):
#

class VIEW3D_OT_AutoVertexGroupsButton(bpy.types.Operator):
    bl_idname = "mhclo.auto_vertex_groups"
    bl_label = "Create Vertex Groups"
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            makeclothes.autoVertexGroups(context.object, 'Selected', None)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#    class OBJECT_OT_RecoverSeamsButton(bpy.types.Operator):
#

class OBJECT_OT_CreateSeamObjectButton(bpy.types.Operator):
    bl_idname = "mhclo.create_seam_object"
    bl_label = "Recover Seams"
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            project.createSeamObject(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}


class OBJECT_OT_AutoSeamsButton(bpy.types.Operator):
    bl_idname = "mhclo.auto_seams"
    bl_label = "Auto Seams"
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            project.autoSeams(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#    class OBJECT_OT_ProjectUVsButton(bpy.types.Operator):
#

class OBJECT_OT_ProjectUVsButton(bpy.types.Operator):
    bl_idname = "mhclo.project_uvs"
    bl_label = "Project UVs"
    bl_options = {'UNDO'}

    def execute(self, context):
        from .makeclothes import getObjectPair
        setObjectMode(context)
        try:
            (human, clothing) = getObjectPair(context)
            project.unwrapObject(clothing, context)
            project.projectUVs(human, clothing, context)
            print("UVs projected")
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#   class OBJECT_OT_ReexportMhcloButton(bpy.types.Operator):
#

class OBJECT_OT_ReexportFilesButton(bpy.types.Operator):
    bl_idname = "mhclo.reexport_files"
    bl_label = "Reexport Files"
    bl_options = {'UNDO'}

    def execute(self, context):
        setObjectMode(context)
        try:
            project.reexportMhclo(context)
            makeclothes.exportObjFile(context)
        except MHError:
            handleMHError(context)
        return{'FINISHED'}

#
#    Init and register
#

def register():
    makeclothes.init()
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
    maketarget.unregister()

if __name__ == "__main__":
    register()

print("MakeClothes loaded")
