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
MHX (MakeHuman eXchange format) importer for Blender.

"""

bl_info = {
    'name': 'Import: MakeHuman Exchange (.mhx)',
    'author': 'Thomas Larsson',
    'version': (1,1,0),
    "blender": (2, 71, 0),
    'location': "File > Import > MakeHuman (.mhx)",
    'description': 'Import files in the MakeHuman eXchange format (.mhx)',
    'warning': '',
    'wiki_url': 'http://makehuman.org/doc/node/makehuman_blender.html',
    'category': 'MakeHuman'}


if "bpy" in locals():
    print("Reloading MHX importer v %d.%d.%d" % bl_info["version"])
    import imp
    imp.reload(error)
    imp.reload(importer)
    imp.reload(rigify)
else:
    print("Loading MHX importer v %d.%d.%d" % bl_info["version"])
    from . import error
    from . import importer
    from . import rigify

from .error import *

from bpy_extras.io_utils import ImportHelper

importer.setVersion(bl_info)

###################################################################################
#
#    MHX importer
#
###################################################################################

class ImportMhx(bpy.types.Operator, ImportHelper):
    """Import from MHX file format (.mhx)"""
    bl_idname = "import_scene.makehuman_mhx"
    bl_description = 'Import from MHX file format (.mhx)'
    bl_label = "Import MHX"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'UNDO'}

    filename_ext = ".mhx"
    filter_glob = StringProperty(default="*.mhx", options={'HIDDEN'})
    filepath = StringProperty(subtype='FILE_PATH')

    helpers = BoolProperty(name="Helper geometry", description="Keep helper geometry", default=False)

    def draw(self, context):
        self.layout.prop(self, "helpers")

    def execute(self, context):
        importer.importMhxFile(self, context)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

###################################################################################
#
#    initialize and register
#
###################################################################################

def menu_func(self, context):
    self.layout.operator(ImportMhx.bl_idname, text="MakeHuman (.mhx)...")

def register():
    bpy.types.Object.MhxVersionStr = StringProperty(name="Version", default="", maxlen=128)
    bpy.types.Object.MhAlpha8 = BoolProperty(default=False)
    bpy.types.Object.MhxRig = StringProperty(default="")
    bpy.types.Object.MhxRigify = BoolProperty(default=False)
    bpy.types.Object.MhxShapekeyDrivers = BoolProperty(default=False)
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    try:
        bpy.utils.unregister_module(__name__)
    except:
        pass
    try:
        bpy.types.INFO_MT_file_import.remove(menu_func)
    except:
        pass

if __name__ == "__main__":
    unregister()
    register()

print("MHX importer successfully (re)loaded")
