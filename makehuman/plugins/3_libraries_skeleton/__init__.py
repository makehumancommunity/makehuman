#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Skeleton library.
Allows a selection of skeletons which can be exported with the MH character.
Skeletons are used for skeletal animation (skinning) and posing.
"""

# TODO add sort by number of bones

import gui3d
import mh

from . import skeletonlibrary

#------------------------------------------------------------------------------------------
#   Load plugin
#------------------------------------------------------------------------------------------

def load(app):
    category = app.getCategory('Pose/Animate')
    maintask = skeletonlibrary.SkeletonLibrary(category)
    maintask.sortOrder = 3
    category.addTask(maintask)

    human = gui3d.app.selectedHuman
    app.addLoadHandler('skeleton', maintask.loadHandler)
    app.addSaveHandler(maintask.saveHandler)

    if not mh.isRelease():
        from . import debugtab
        debugtask = debugtab.SkeletonDebugLibrary(category, maintask)
        debugtask.sortOrder = 3
        category = app.getCategory('Utilities')
        category.addTask(debugtask)

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements
def unload(app):
    pass

