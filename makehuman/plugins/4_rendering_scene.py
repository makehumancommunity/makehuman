#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           ...none yet

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

Scene library.
"""

import mh
import guirender
from core import G
import filechooser as fc
import scene


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
            G.app.setScene(scene.Scene(filename))

    def onShow(self, event):
        guirender.RenderTaskView.onShow(self, event)
        self.filechooser.refresh()
        self.filechooser.selectItem(G.app.scene.file.path)
        self.filechooser.setFocus()


def load(app):
    category = app.getCategory('Rendering')
    taskview = SceneLibraryTaskView(category)
    taskview.sortOrder = 20.0
    category.addTask(taskview)


def unload(app):
    pass
