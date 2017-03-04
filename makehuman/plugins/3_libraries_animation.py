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

Animation library
"""

import mh
import gui
import gui3d
import log
from collections import OrderedDict
import filechooser as fc

import skeleton
import animation
import getpath
import material

import numpy as np
import os


class AnimationLibrary(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Animations')

        self.human = gui3d.app.selectedHuman

        self.playbackSlider = self.addLeftWidget(gui.Slider(label='Frame'))
        self.playbackSlider.setMin(0)
        self.frameLbl = self.addLeftWidget(gui.TextView(''))
        self.frameLbl.setTextFormat(u"Frame: %s", 0)

        @self.playbackSlider.mhEvent
        def onChange(value):
            self.updateFrame(int(value))

        @self.playbackSlider.mhEvent
        def onChanging(value):
            self.updateFrame(int(value))

    def updateFrame(self, frame):
        self.human.setToFrame(frame)
        self.human.refreshPose()
        self.frameLbl.setTextFormat(["Frame",": %s"], frame)

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        if gui3d.app.getSetting('cameraAutoZoom'):
            gui3d.app.setGlobalCamera()

        if self.human.getSkeleton():
            if self.human.getActiveAnimation() and self.human.getActiveAnimation().nFrames > 1:
                self.playbackSlider.setEnabled(True)
                self.playbackSlider.setMax(self.human.getActiveAnimation().nFrames-1)
            else:
                self.playbackSlider.setEnabled(False)
        else:
            self.playbackSlider.setEnabled(False)

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

    def onHumanChanged(self, event):
        human = event.human
        if event.change == 'reset':
            if self.isShown():
                # Refresh onShow status
                self.onShow(event)


def load(app):
    category = app.getCategory('Pose/Animate')
    maintask = AnimationLibrary(category)
    maintask.sortOrder = 8
    category.addTask(maintask)


def unload(app):
    pass
