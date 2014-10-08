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

TODO
"""

import os
import gui3d
import mh
import gui
import filechooser as fc
import log

#import cProfile

import posemode

class PoseAction(gui3d.Action):
    def __init__(self, name, library, before, after):
        super(PoseAction, self).__init__(name)
        self.library = library
        self.before = before
        self.after = after

    def do(self):
        clearOnly = self.after is None
        self.library.pose = posemode.loadMhpFile(self.after, self.library.pose, clearOnly)
        self.library.posefile = self.after
        return True

    def undo(self):
        clearOnly = self.before is None
        self.library.pose = posemode.loadMhpFile(self.before, self.library.pose, clearOnly)
        self.library.posefile = self.before
        return True

#
#   Pose library
#

class PoseLoadTaskView(gui3d.TaskView):

    def __init__(self, category):

        self.systemPoses = mh.getSysDataPath('poses')
        self.userPoses = mh.getPath('data/poses')
        self.paths = [self.systemPoses, self.userPoses]

        self.posefile = None
        self.pose = None

        gui3d.TaskView.__init__(self, category, 'Poses')
        if not os.path.exists(self.userPoses):
            os.makedirs(self.userPoses)
        #self.filechooser = self.addTopWidget(fc.FileChooser(self.paths, 'mhp', 'thumb', mh.getSysDataPath('notfound.thumb')))
        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.paths, 'mhp', 'thumb', notFoundImage=mh.getSysDataPath('notfound.thumb'), name='Pose', noneItem=True, clearImage=os.path.join(self.systemPoses, 'clear.thumb')))
        self.filechooser.setIconSize(50,50)
        #self.addLeftWidget(self.filechooser.createSortBox())

        @self.filechooser.mhEvent
        def onFileSelected(filepath):
            oldFile = self.posefile

            gui3d.app.do(PoseAction("Change pose",
                self,
                oldFile,
                filepath))
            #mh.changeCategory('Modelling')

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        self.filechooser.setFocus()
        if gui3d.app.settings.get('cameraAutoZoom', True):
            gui3d.app.setGlobalCamera()

        self.posefile = posemode.enterPoseMode()
        if self.posefile:
            self.pose = posemode.loadMhpFile(self.posefile)
        else:
            self.pose = None


    def onHide(self, event):
        posemode.exitPoseMode(self.posefile)
        gui3d.TaskView.onHide(self, event)


    def onHumanChanging(self, event):
        posemode.touchStorage()
        if event.change == 'reset':
            self.posefile = None
            self.pose = None


    def onHumanChanged(self, event):
        posemode.touchStorage()
        #posemode.changePoseMode(event)

    def loadHandler(self, human, values):
        pass

    def saveHandler(self, human, file):
        pass

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Pose/Animate')
    taskview = PoseLoadTaskView(category)
    taskview.sortOrder = 1
    category.addTask(taskview)

    app.addLoadHandler('poses', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass
