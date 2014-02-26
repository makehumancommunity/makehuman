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

Teeth proxy library.
"""

import gui3d
import mh
import proxychooser

class TeethTaskView(proxychooser.ProxyChooserTaskView):

    def __init__(self, category):
        super(TeethTaskView, self).__init__(category, 'teeth')

    def getObjectLayer(self):
        return 5

    def proxySelected(self, proxy, obj):
        self.human.teethObj = obj
        self.human.teethProxy = proxy

    def proxyDeselected(self, proxy, obj, suppressSignal = False):
        self.human.teethObj = None
        self.human.teethProxy = None

    def onShow(self, event):
        super(TeethTaskView, self).onShow(event)
        if gui3d.app.settings.get('cameraAutoZoom', True):
            gui3d.app.setFaceCamera()


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


taskview = None

def load(app):
    global taskview

    category = app.getCategory('Geometries')
    taskview = TeethTaskView(category)
    taskview.sortOrder = 1.3
    category.addTask(taskview)

    taskview.registerLoadSaveHandlers()


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    taskview.onUnload()

