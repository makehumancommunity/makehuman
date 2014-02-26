#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           ...none yet

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Scene library.
"""

import mh
import guirender
from core import G
import filechooser as fc


class SceneLibraryTaskView(guirender.RenderTaskView):
    def __init__(self, category):
        guirender.RenderTaskView.__init__(self, category, 'Scene')

        self.filechooser = self.addRightWidget(
            fc.IconListFileChooser(
                [mh.getDataPath('scenes'), mh.getSysDataPath('scenes')],
                'mhscene', ['thumb', 'png'], 'notfound.thumb', 'Scene'))
        #self.addLeftWidget(self.filechooser.createSortBox())
        self.filechooser.enableAutoRefresh(False)

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            G.app.currentScene.load(filename)

    def onShow(self, event):
        guirender.RenderTaskView.onShow(self, event)
        self.filechooser.refresh()
        self.filechooser.selectItem(G.app.currentScene.path)
        self.filechooser.setFocus()


def load(app):
    category = app.getCategory('Rendering')
    taskview = SceneLibraryTaskView(category)
    taskview.sortOrder = 20.0
    category.addTask(taskview)


def unload(app):
    pass
