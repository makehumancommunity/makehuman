#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson, Marc Flerackers

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

Eye chooser library.
"""

import gui3d
import mh
import proxychooser

class EyesTaskView(proxychooser.ProxyChooserTaskView):

    def __init__(self, category):
        super(EyesTaskView, self).__init__(category, 'eyes', tagFilter = True, descriptionWidget = False)

    def getObjectLayer(self):
        #return 3
        return 5

    def proxySelected(self, proxy):
        self.human.eyesProxy = proxy

    def proxyDeselected(self, proxy, suppressSignal = False):
        self.human.eyesProxy = None

    def onShow(self, event):
        super(EyesTaskView, self).onShow(event)
        if gui3d.app.getSetting('cameraAutoZoom'):
            gui3d.app.setFaceCamera()

    def onHumanChanged(self, event):
        super(EyesTaskView, self).onHumanChanged(event)
        if event.change == 'reset':
            # Load initial eyes
            self.selectProxy(mh.getSysDataPath("eyes/high-poly/high-poly.mhclo"))
            # Reset default material on eyes (in case it was changed)
            self.getObjects()[0].material = self.getSelection()[0].material


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
    taskview.selectProxy(mh.getSysDataPath("eyes/high-poly/high-poly.mhclo"))

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    taskview.onUnload()

