#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

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

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Pose library
"""

import gui3d
import mh
import gui
import log
import filechooser as fc
import animation
import bvh
import os
from core import G

class PoseLibraryTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Pose')
        self.human = G.app.selectedHuman

        self.paths = [mh.getDataPath('poses'), mh.getSysDataPath('poses')]

        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.paths, ['bvh', 'mhp'], 'thumb', mh.getSysDataPath('poses/notfound.thumb'), name='Pose'))
        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(False)

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            self.loadPose(filename)

        box = self.addLeftWidget(gui.GroupBox('Pose'))

    def loadPose(self, filepath):
        if not self.human.getSkeleton():
            log.error("No skeleton selected, cannot load pose")
            return

        if os.path.splitext(filepath)[1].lower() == '.mhp':
            anim = self.loadMhp(filepath)
        elif os.path.splitext(filepath)[1].lower() == '.bvh':
            anim = self.loadBvh(filepath)
        else:
            log.error("Cannot load pose file %s: File type unknown." % filepath)
            return

        self.human.addAnimation(anim)
        self.human.setActiveAnimation(anim.name)
        self.human.setToFrame(0)
        self.human.setPosed(True)

    def loadMhp(self, filepath):
        return animation.loadPoseFromMhpFile(filepath, self.human.getSkeleton())

    def loadBvh(self, filepath):
        bvh_file = bvh.load(filepath)
        jointNames = [bone.name for bone in self.human.getSkeleton().getBones()]
        return bvh_file.createAnimationTrack(jointNames)

    def onShow(self, event):
        self.filechooser.refresh()

    def onHide(self, event):
        gui3d.app.statusPersist('')

category = None
taskview = None

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Pose/Animate')
    taskview = PoseLibraryTaskView(category)
    taskview.sortOrder = 2
    category.addTask(PoseLibraryTaskView(category))


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass
