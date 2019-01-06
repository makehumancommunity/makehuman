#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2019

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

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

        self.items = {}

        self.left.child.setSizePolicy(gui.SizePolicy.MinimumExpanding, gui.SizePolicy.MinimumExpanding)

        self.clear = self.addLeftWidget(gui.Button('Clear'))

        self.targets = self.addLeftWidget(TargetsTree())
        self.targets.setHeaderHidden(True)
        self.targets.resizeColumnToContents(0)
        self.targets.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.Expanding)
        self.left.layout.setStretchFactor(self.targets, 1)

        self.itemsBox = gui.GroupBox('Selected Targets:')
        self.itemsList = gui.TextView('')
        self.itemsList.setWordWrap(False)
        self.itemsList.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)
        self.itemsBox.addWidget(self.itemsList)
        self.addRightWidget(self.itemsBox)

        @self.targets.mhEvent
        def onActivate(item):
            path = self.targets.getItemPath(item)
            log.message('target: %s', path)
            if item.text not in self.items:
                self.items[item.text] = [item, path]
                self.showTarget(path)
            else:
                self.clearColor()
                del self.items[item.text]
                item.setSelected(False)
                for itm in self.items:
                    self.showTarget(self.items[itm][1])
            itemsString = '\n'.join(key.split('.')[0] for key in sorted(self.items))
            for key in self.items:
                self.items[key][0].setSelected(True)
            self.itemsList.setText(itemsString)

        @self.targets.mhEvent
        def onExpand(item):
            self.targets.populate(item)
            self.targets.resizeColumnToContents(0)

        @self.clear.mhEvent
        def onClicked(event):
            self.clearColor()
            self.itemsList.setText('')
            for key in self.items:
                self.items[key][0].setSelected(False)
            self.items.clear()

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

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        gui3d.app.actions.wireframe.setDisabled(True)
        if not gui3d.app.actions.wireframe.isChecked():
            G.app.selectedHuman.setSolid(False)

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)
        if not gui3d.app.actions.wireframe.isChecked():
            G.app.selectedHuman.setSolid(True)
        gui3d.app.actions.wireframe.setDisabled(False)

def load(app):
    category = app.getCategory('Utilities')
    taskview = category.addTask(TargetsTaskView(category))

def unload(app):
    pass
