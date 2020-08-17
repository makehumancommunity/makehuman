#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Proxy mesh library

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2020

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

Library plugin for variations of the human mesh. Usually with reduced polygon
count or geometry adapted to special cases.
"""

import gui3d
import proxychooser
import filechooser as fc
import proxy


class ProxyFileSort(fc.FileSort):

    def __init__(self):
        super(ProxyFileSort, self).__init__()
        self.metaFields = ["faces"]

    def getMeta(self, filename):
        meta = {}

        faces = 0
        try:
            with open(filename.replace('.proxy', '.obj'), 'r', encoding="utf-8") as f:
                for line in f:
                    lineData = line.split()
                    if lineData and lineData[0] == 'f':
                        faces += 1
        except:
            pass
        meta['faces'] = faces

        return meta


class ProxyTaskView(proxychooser.ProxyChooserTaskView):

    def __init__(self, category):
        super(ProxyTaskView, self).__init__(category, 'proxymeshes', tabLabel = 'Topologies', tagFilter = True, descriptionWidget = True)

    def getObjectLayer(self):
        return 4

    def getSaveName(self):
        return "proxy"

    def getFileExtension(self):
        return ['mhpxy', 'proxy']

    def onShow(self, event):
        super(ProxyTaskView, self).onShow(event)
        if gui3d.app.getSetting('cameraAutoZoom'):
            gui3d.app.setGlobalCamera()

    def selectProxy(self, mhclofile):
        """
        Called when a new proxy has been selected.
        """
        if not mhclofile:
            self.deselectProxy(None, suppressSignal = True)

        if self.isProxySelected():
            # Deselect previously selected proxy
            self.deselectProxy(None, suppressSignal = True)

        if not mhclofile:
            self.signalChange()
            return

        pxy = proxy.loadProxy(self.human,
                              mhclofile,
                              type=self.proxyName.capitalize())

        # Override z_depth and mesh priority to the same as human mesh
        pxy.z_depth = self.human.getSeedMesh().priority
        mesh,obj = pxy.loadMeshAndObject(self.human)

        self.human.setProxy(pxy)

        if self.descriptionWidget:
            self.descrLbl.setText(pxy.description)

        self.filechooser.selectItem(mhclofile)

        self.signalChange()

    def deselectProxy(self, mhclofile, suppressSignal = False):
        """
        Deselect specified proxy from library selections.
        """
        if not self.isProxySelected():
            return

        self.human.setProxy(None)

        if self.descriptionWidget:
            self.descrLbl.setText('')

        self.filechooser.deselectItem(mhclofile)

        if not suppressSignal:
            self.signalChange()

    def getSelection(self):
        if self.isProxySelected():
            return [ self.human.proxy ]
        else:
            return []

    def getObjects(self):
        if self.isProxySelected():
            return [ self.human ]
        else:
            return []

    def isProxySelected(self):
        return self.human.isProxied()

    def adaptAllProxies(self, **kwargs):
        # Override super-class behaviour
        pass

    def onHumanChanging(self, event):
        # Override super-class behaviour
        pass

    def onHumanChanged(self, event):
        # Override super-class behaviour
        if event.change == 'reset':
            self.resetSelection()
        if event.change in ['targets', 'modifier']:
            self.adaptAllProxies()


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


taskview = None

def load(app):
    global taskview

    category = app.getCategory('Geometries')
    taskview = ProxyTaskView(category)
    category.addTask(taskview)

    taskview.registerLoadSaveHandlers()


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    taskview.onUnload()

