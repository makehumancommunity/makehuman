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

#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import pprint
import gui3d
import gui
from core import G
import log

class DataTree(gui.TreeView):
    def __init__(self, root):
        super(DataTree, self).__init__()
        self.item = self.addTopLevel('Application')
        self.root = root

    def getItemPath(self, item):
        path = []
        while item is not None and item.parent is not None:
            path.append(item.text)
            item = item.parent
        path = list(reversed(path))
        return path

    def getValue(self, path):
        root = self.root
        for key in path:
            root = getattr(root, key, None)
            if root is None:
                break
        return root

    def populate(self, item):
        # log.message('populate: %s', item)
        path = self.getItemPath(item)
        # log.message('populate: path=%s', path)
        value = self.getValue(path)
        for name in sorted(value.__dict__.keys()):
            if name[:2] == '__' and name[-2:] == '__':
                continue
            child = getattr(value, name, None)
            if hasattr(child, '__dict__'):
                item.addChild(name, True)
            else:
                item.addChild(name, False)

class DataTaskView(gui3d.TaskView):
    def __init__(self, category):
        super(DataTaskView, self).__init__(category, 'Data')
        self.pp = pprint.PrettyPrinter()
        self.left.child.setSizePolicy(
            gui.SizePolicy.MinimumExpanding,
            gui.SizePolicy.MinimumExpanding)

        self.tree = self.addLeftWidget(DataTree(G.app))
        self.clear = self.addLeftWidget(gui.Button('Clear'))
        self.text = self.addTopWidget(gui.DocumentEdit())

        self.tree.setHeaderHidden(True)
        self.tree.resizeColumnToContents(0)
        self.tree.setSizePolicy(
            gui.SizePolicy.Ignored,
            gui.SizePolicy.Expanding)
        self.left.layout.setStretchFactor(self.tree, 1)

        @self.tree.mhEvent
        def onActivate(item):
            path = self.tree.getItemPath(item)
            # log.message('data: %s', path)
            self.showData(path)

        @self.tree.mhEvent
        def onExpand(item):
            self.tree.populate(item)
            self.tree.resizeColumnToContents(0)

        @self.clear.mhEvent
        def onClicked(event):
            self.clearData()

    def clearData(self):
        self.text.setText('')

    def showData(self, path):
        val = self.tree.getValue(path)
        self.text.setText(self.pp.pformat(val))

def load(app):
    category = app.getCategory('Utilities')
    taskview = category.addTask(DataTaskView(category))

def unload(app):
    pass

