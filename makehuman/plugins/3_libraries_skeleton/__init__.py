#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
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

Skeleton library.
Allows a selection of skeletons which can be exported with the MH character.
Skeletons are used for skeletal animation (skinning) and posing.
"""

# TODO add sort by number of bones

from . import skeletonlibrary

#------------------------------------------------------------------------------------------
#   Load plugin
#------------------------------------------------------------------------------------------

def load(app):
    global maintask
    import gui3d
    import mh
    category = app.getCategory('Pose/Animate')
    maintask = skeletonlibrary.SkeletonLibrary(category)
    maintask.sortOrder = -0.5
    category.addTask(maintask)

    human = gui3d.app.selectedHuman
    app.addLoadHandler('skeleton', maintask.loadHandler)
    app.addSaveHandler(maintask.saveHandler, priority=5)

    if not mh.isRelease():
        from . import debugtab
        debugtask = debugtab.SkeletonDebugLibrary(category)
        debugtask.sortOrder = 3
        category = app.getCategory('Utilities')
        category.addTask(debugtask)

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements
def unload(app):
    maintask.onUnload()

