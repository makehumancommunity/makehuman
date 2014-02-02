#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Proxy mesh library

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Library plugin for variations of the human mesh. Usually with reduced polygon
count or geometry adapted to special cases.
"""

import gui3d
import mh
import proxychooser
import filechooser as fc
import os
import mh2proxy


class ProxyFileSort(fc.FileSort):

    def __init__(self):
        super(ProxyFileSort, self).__init__()
        self.meta = {}

    def fields(self):
        return list(super(ProxyFileSort, self).fields()) + ["faces"]

    def sortFaces(self, filenames):
        self.updateMeta(filenames)
        decorated = [(self.meta[filename]['faces'], i, filename) for i, filename in enumerate(filenames)]
        decorated.sort()
        return [filename for gender, i, filename in decorated]

    def updateMeta(self, filenames):
        for filename in filenames:
            if filename in self.meta:
                if self.meta[filename]['modified'] < os.path.getmtime(filename):
                    self.meta[filename] = self.getMeta(filename)
            else:
                self.meta[filename] = self.getMeta(filename)

    def getMeta(self, filename):
        meta = {}
        meta['modified'] = os.path.getmtime(filename)
        faces = 0
        try:
            f = open(filename.replace('.proxy', '.obj'))
            for line in f:
                lineData = line.split()
                if lineData and lineData[0] == 'f':
                    faces += 1
            f.close()
        except:
            pass
        meta['faces'] = faces

        return meta


class ProxyTaskView(proxychooser.ProxyChooserTaskView):

    def __init__(self, category):
        super(ProxyTaskView, self).__init__(category, 'proxymeshes', tabLabel = 'Topologies')

    def getObjectLayer(self):
        return 4

    def getSaveName(self):
        return "proxy"

    def getFileExtension(self):
        return 'proxy'

    def proxySelected(self, proxy, obj):
        self.human.setProxy(proxy)
        self.human.genitalsProxy = proxy

    def proxyDeselected(self, proxy, obj):
        self.human.genitalsObj = None
        self.human.genitalsProxy = None

    def onShow(self, event):
        super(ProxyTaskView, self).onShow(event)
        if gui3d.app.settings.get('cameraAutoZoom', True):
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

        self.filechooser.selectItem(mhclofile)

        if not mhclofile:
            self.signalChange()
            return

        if mhclofile not in self._proxyCache:
            proxy = mh2proxy.readProxyFile(self.human.meshData,
                                           mhclofile,
                                           type=self.proxyName.capitalize())
            self._proxyCache[mhclofile] = proxy
        else:
            proxy = self._proxyCache[mhclofile]

        self.human.setProxy(proxy)
        self.human.updateProxyMesh()

        # Add to selection
        self.selectedProxies.append(proxy)

        self.filechooser.selectItem(mhclofile)

        self.signalChange()

    def deselectProxy(self, mhclofile, suppressSignal = False):
        """
        Deselect specified proxy from library selections.
        """
        if not self.isProxySelected():
            return

        self.human.setProxy(None)
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

    def adaptAllProxies(self):
        pass


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

