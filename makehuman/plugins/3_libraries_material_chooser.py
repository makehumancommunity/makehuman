#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier, Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

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

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Material library plugin.

"""

__docformat__ = 'restructuredtext'

import material
import os
import gui3d
import mh
import gui
from proxy import SimpleProxyTypes
import filechooser as fc
from humanobjchooser import HumanObjectSelector
import log
import getpath

class MaterialAction(gui3d.Action):
    def __init__(self, obj, after):
        super(MaterialAction, self).__init__("Change material of %s" % obj.mesh.name)
        self.obj = obj
        self.before = material.Material().copyFrom(obj.material)
        self.after = after

    def do(self):
        self.obj.material = self.after
        return True

    def undo(self):
        self.obj.material = self.before
        return True


class MaterialTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Material', label='Skin/Material')
        self.human = gui3d.app.selectedHuman

        # Paths, in order, in which relative material filepaths will be searched
        self.searchPaths = [mh.getPath(), mh.getSysDataPath()]
        self.searchPaths = [os.path.abspath(p) for p in self.searchPaths]

        self.materials = None

        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.materials, 'mhmat', ['thumb', 'png'], mh.getSysDataPath('skins/notfound.thumb'), name='Material'))
        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(False)
        #self.filechooser.setFileLoadHandler(fc.MhmatFileLoader())
        #self.addLeftWidget(self.filechooser.createSortBox())

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            mat = material.fromFile(filename)
            human = self.human

            obj = self.humanObjSelector.getSelectedObject()
            if obj:
                gui3d.app.do(MaterialAction(obj, mat))

        self.humanObjSelector = self.addLeftWidget(HumanObjectSelector(self.human))
        @self.humanObjSelector.mhEvent
        def onActivate(value):
            self.reloadMaterialChooser()


    def onShow(self, event):
        # When the task gets shown, set the focus to the file chooser
        gui3d.TaskView.onShow(self, event)

        self.reloadMaterialChooser()


    def applyClothesMaterial(self, uuid, filename):
        human = self.human
        if uuid not in human.clothesProxies.keys():
            log.warning("Cannot set material for clothes with UUID %s, no such item", uuid)
            return False
        clo = human.clothesProxies[uuid].object
        clo.mesh.material = material.fromFile(filename)
        return True

    def getClothesMaterial(self, uuid):
        """
        Get the currently set material for clothing item with specified UUID.
        """
        human = self.human
        if uuid not in human.clothesProxies.keys():
            return None
        clo = human.clothesProxies[uuid].object
        return clo.material.filename

    def getMaterialPaths(self, objType, proxy = None):
        if objType == 'skin':
            objType = 'skins'
        elif objType not in [t.lower() for t in SimpleProxyTypes]:
            objType = 'clothes'
        objType = objType.lower()

        if proxy and objType != 'skins':
            subPath = None
        else:
            subPath = objType

        # General paths
        if subPath:
            paths = [mh.getPath(os.path.join('data', subPath)), mh.getSysDataPath(subPath)]
            for p in paths:
                if getpath.isSubPath(p, mh.getPath()) and not os.path.exists(p):
                    os.makedirs(p)
        else:
            paths = []

        # Global material paths
        for p in [mh.getPath(os.path.join('data', objType, 'materials')), mh.getSysDataPath(os.path.join(objType, 'materials'))]:
            if os.path.isdir(p):
                paths.append(p)

        # Path where proxy file is located
        if proxy:
            paths = [os.path.dirname(proxy.file)] + paths

        return paths

    def reloadMaterialChooser(self):
        human = self.human
        selectedMat = None

        self.materials = self.getMaterialPaths(self.humanObjSelector.selected, self.humanObjSelector.getSelectedProxy())
        obj = self.humanObjSelector.getSelectedObject()
        if obj:
            selectedMat = obj.material.filename

        # Reload filechooser
        self.filechooser.deselectAll()
        self.filechooser.setPaths(self.materials)
        self.filechooser.refresh()
        if selectedMat:
            self.filechooser.setHighlightedItem(selectedMat)
        self.filechooser.setFocus()

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

    def loadHandler(self, human, values):
        if values[0] == 'status':
            return

        if values[0] == 'skinMaterial':
            path = values[1]
            if os.path.isfile(path):
                mat = material.fromFile(path)
                human.material = mat
                return
            else:
                absP = getpath.findFile(path, [mh.getPath('data'), mh.getSysDataPath()])
                if not os.path.isfile(absP):
                    log.warning('Could not find material %s for skinMaterial parameter.', values[1])
                    return
                mat = material.fromFile(absP)
                human.material = mat
                return
        elif values[0] == 'material':
            if len(values) == 3:
                uuid = values[1]
                filepath = values[2]
                name = ""
            else:
                name = values[1]
                uuid = values[2]
                filepath = values[3]

            if human.hairProxy and human.hairProxy.getUuid() == uuid:
                proxy = human.hairProxy
                filepath = self.getMaterialPath(filepath, proxy.file)
                human.hairObj.material = material.fromFile(filepath)
                return
            elif human.eyesProxy and human.eyesProxy.getUuid() == uuid:
                proxy = human.eyesProxy
                filepath = self.getMaterialPath(filepath, proxy.file)
                human.eyesObj.material = material.fromFile(filepath)
                return
            elif human.genitalsProxy and human.genitalsProxy.getUuid() == uuid:
                proxy = human.genitalsProxy
                filepath = self.getMaterialPath(filepath, proxy.file)
                human.genitalsObj.material = material.fromFile(filepath)
                return
            elif not uuid in human.clothesProxies.keys():
                log.error("Could not load material for proxy with uuid %s (%s)! No such proxy." % (uuid, name))
                return

            proxy = human.clothesProxies[uuid]
            proxy = human.clothesProxies[uuid]
            filepath = self.getMaterialPath(filepath, proxy.file)
            self.applyClothesMaterial(uuid, filepath)
            return

    def getRelativeMaterialPath(self, filepath, objFile = None):
        """
        Produce a portable path for writing to file.
        """
        # TODO move as helper func to material module
        if objFile:
            objFile = os.path.abspath(objFile)
            if os.path.isdir(objFile):
                objFile = os.path.dirname(objFile)[0]
            searchPaths = [ objFile ] + self.searchPaths
        else:
            searchPaths = self.searchPaths

        return getpath.getRelativePath(filepath, searchPaths)

    def getMaterialPath(self, relPath, objFile = None):
        if objFile:
            objFile = os.path.abspath(objFile)
            if os.path.isdir(objFile):
                objFile = os.path.split(objFile)[0]
            searchPaths = [ objFile ] + self.searchPaths
        else:
            searchPaths = self.searchPaths

        return getpath.findFile(relPath, searchPaths)

    def onHumanChanged(self, event):
        if event.change == 'reset':
            self.humanObjSelector.refresh()
            self.reloadMaterialChooser()

    def saveHandler(self, human, file):
        file.write('skinMaterial %s\n' % self.getRelativeMaterialPath(human.material.filename))
        for name, pxy in human.clothesProxies.items():
            clo = pxy.object
            if clo:
                proxy = human.clothesProxies[name]
                if clo.material.filename !=  proxy.material.filename:
                    materialPath = self.getRelativeMaterialPath(clo.material.filename, proxy.file)
                    file.write('material %s %s %s\n' % (proxy.name, proxy.getUuid(), materialPath))
        if human.hairProxy:
            proxy = human.hairProxy
            hairObj = proxy.object
            materialPath = self.getRelativeMaterialPath(hairObj.material.filename, proxy.file)
            file.write('material %s %s %s\n' % (proxy.name, proxy.getUuid(), materialPath))
        if human.eyesProxy:
            proxy = human.eyesProxy
            eyesObj = proxy.object
            materialPath = self.getRelativeMaterialPath(eyesObj.material.filename, proxy.file)
            file.write('material %s %s %s\n' % (proxy.name, proxy.getUuid(), materialPath))
        if human.genitalsProxy:
            proxy = human.genitalsProxy
            genitalsObj = proxy.object
            materialPath = self.getRelativeMaterialPath(genitalsObj.material.filename, proxy.file)
            file.write('material %s %s %s\n' % (proxy.name, proxy.getUuid(), materialPath))


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Materials')
    taskview = MaterialTaskView(category)
    taskview.sortOrder = 0
    category.addTask(taskview)

    app.addLoadHandler('material', taskview.loadHandler)
    app.addLoadHandler('skinMaterial', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass
