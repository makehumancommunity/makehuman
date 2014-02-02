#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson, Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Eye chooser library.
"""

import gui3d
import mh
import proxychooser

class EyesTaskView(proxychooser.ProxyChooserTaskView):

    def __init__(self, category):
        super(EyesTaskView, self).__init__(category, 'eyes')

    def getObjectLayer(self):
        #return 3
        return 5

    def proxySelected(self, proxy, obj):
        self.human.eyesObj = obj
        self.human.eyesProxy = proxy

    def proxyDeselected(self, proxy, obj, suppressSignal = False):
        self.human.eyesObj = None
        self.human.eyesProxy = None

    def onShow(self, event):
        super(EyesTaskView, self).onShow(event)
        if gui3d.app.settings.get('cameraAutoZoom', True):
            gui3d.app.setFaceCamera()

    def onHumanChanged(self, event):
        if event.change == 'reset':
            self.selectProxy(mh.getSysDataPath("eyes/high-poly/high-poly.mhclo"))
            self.getObjects()[0].mesh.material = self.getSelection()[0].material
            return
        super(EyesTaskView, self).onHumanChanged(event)


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements

taskview = None

def load(app):
    global taskview

    category = app.getCategory('Geometries')
    taskview = EyesTaskView(category)
    taskview.sortOrder = 1
    category.addTask(taskview)

    taskview.registerLoadSaveHandlers()

    # Load initial eyes
    taskview.selectProxy(mh.getSysDataPath("eyes/low-poly/low-poly.mhclo"))

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    taskview.onUnload()

