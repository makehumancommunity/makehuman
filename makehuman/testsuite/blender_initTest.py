#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Blender initialize test script

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Blender script (to be used within blender) that initializes test environment
"""

import bpy

def enablePlugins():
    try:
        bpy.ops.wm.addon_enable(module = "io_import_scene_mhx")
        print("MH_TEST SUCCESS Loaded MHX importer plugin.")
    except:
        print("MH_TEST ERROR Could not import load MHX importer plugin. Is it installed?")

    try:
        bpy.ops.wm.addon_enable(module = "maketarget")
        print("MH_TEST SUCCESS Loaded maketarget plugin.")
    except:
        print("MH_TEST ERROR Could not import load maketarget plugin. Is it installed?")

    try:
        bpy.ops.wm.addon_enable(module = "makewalk")
        print("MH_TEST SUCCESS Loaded makewalk plugin.")
    except:
        print("MH_TEST ERROR Could not import load makewalk plugin. Is it installed?")

    try:
        bpy.ops.wm.addon_enable(module = "makeclothes")
        print("MH_TEST SUCCESS Loaded makeclothes plugin.")
    except:
        print("MH_TEST ERROR Could not import load makeclothes plugin. Is it installed?")
    
def quit():
    """
    Quit blender
    """
    bpy.ops.wm.quit_blender()



# Enable necessary plugins
enablePlugins()

quit()
