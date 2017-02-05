#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

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

TODO
"""

import os
import numpy as np

import gui3d
import mh
import gui
import algos3d
from core import G
import log

class TargetsTree(gui.TreeView):
    def __init__(self):
        super(TargetsTree, self).__init__()
        self.root = self.addTopLevel('targets')

    @staticmethod
    def getItemPath(item):
        path = []
        while item is not None:
            path.append(item.text)
            item = item.parent
        path = mh.getSysDataPath(os.path.join(*reversed(path)))
        return path

    def populate(self, item):
        path = self.getItemPath(item)
        for name in sorted(os.listdir(path)):
            if name[0] == '.':
                continue
            pathname = os.path.join(path, name)
            if os.path.isdir(pathname):
                item.addChild(name, True)
            elif name.lower().endswith('.target') and os.path.isfile(pathname):
                item.addChild(name, False)

class TargetsTaskView(gui3d.TaskView):
    def __init__(self, category):
        super(TargetsTaskView, self).__init__(category, 'Targets')
        self.targets = self.addTopWidget(TargetsTree())
        self.clear = self.addLeftWidget(gui.Button('Clear'))

        @self.targets.mhEvent
        def onActivate(item):
            path = self.targets.getItemPath(item)
            log.message('target: %s', path)
            self.showTarget(path)
            mh.changeCategory('Modelling')

        @self.targets.mhEvent
        def onExpand(item):
            self.targets.populate(item)

        @self.clear.mhEvent
        def onClicked(event):
            self.clearColor()
            mh.changeCategory('Modelling')

    def clearColor(self):
        mesh = G.app.selectedHuman.meshData
        mesh.color[...] = (255,255,255,255)
        mesh.markCoords(colr = True)
        mesh.sync_all()

    def showTarget(self, path):
        mesh = G.app.selectedHuman.meshData
        target = algos3d.getTarget(mesh, path)
        sizes = np.sqrt(np.sum(target.data ** 2, axis = -1))
        sizes /= np.amax(sizes)
        val = sizes * 2 - 1
        del sizes
        red = np.maximum(val, 0)
        blue = np.maximum(-val, 0)
        green = 1.0 - red - blue
        del val
        color = np.array([red,green,blue,np.ones_like(red)]).T
        color = (color * 255.99).astype(np.uint8)
        mesh.color[target.verts,:] = color
        mesh.markCoords(target.verts, colr = True)
        mesh.sync_all()

def load(app):
    category = app.getCategory('Utilities')
    taskview = category.addTask(TargetsTaskView(category))

def unload(app):
    pass

