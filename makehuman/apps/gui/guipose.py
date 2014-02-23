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

This module contains the Pose Mode Task View class to ease creation of
task views that utilize pose mode when they are active.
"""

import gui3d
import posemode

class PoseModeTaskView(gui3d.TaskView):
    def __init__(self, category, name, label=None):
        gui3d.TaskView.__init__(self, category, name, label)
        self.posefile = None

    def enterPoseMode(self):
        self.posefile = posemode.enterPoseMode()
        if self.posefile:
            posemode.loadMhpFile(self.posefile)

    def exitPoseMode(self):
        posemode.exitPoseMode(self.posefile)

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        self.enterPoseMode()

    def onHide(self, event):
        self.exitPoseMode()
        gui3d.TaskView.onHide(self, event)

