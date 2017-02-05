#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Blender initialize test script

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

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
