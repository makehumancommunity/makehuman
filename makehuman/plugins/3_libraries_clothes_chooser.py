#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers, Jonas Hauquier, Thomas Larsson

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

Clothes library.
"""

import proxychooser

import gui3d
import gui
import log
import numpy as np


#
#   Clothes
#

class ClothesTaskView(proxychooser.ProxyChooserTaskView):

    def __init__(self, category):
        super(ClothesTaskView, self).__init__(category, 'clothes', multiProxy = True, tagFilter = True)

        self.faceHidingTggl = self.optionsBox.addWidget(FaceHideCheckbox("Hide faces under clothes"))
        @self.faceHidingTggl.mhEvent
        def onClicked(event):
            self.updateFaceMasks(self.faceHidingTggl.selected)
        @self.faceHidingTggl.mhEvent
        def onMouseEntered(event):
            self.visualizeFaceMasks(True)
        @self.faceHidingTggl.mhEvent
        def onMouseExited(event):
            self.visualizeFaceMasks(False)
        self.faceHidingTggl.setSelected(True)

        self.oldPxyMats = {}
        self.blockFaceMasking = False

    def createFileChooser(self):
        self.optionsBox = self.addLeftWidget(gui.GroupBox('Options'))
        super(ClothesTaskView, self).createFileChooser()

    def getObjectLayer(self):
        return 10

    def proxySelected(self, pxy):
        self.human.addClothesProxy(pxy)
        self.updateFaceMasks(self.faceHidingTggl.selected)

    def proxyDeselected(self, pxy, suppressSignal = False):
        uuid = pxy.uuid
        self.human.removeClothesProxy(uuid)
        if not suppressSignal:
            self.updateFaceMasks(self.faceHidingTggl.selected)

    def resetSelection(self):
        super(ClothesTaskView, self).resetSelection()
        self.updateFaceMasks(self.faceHidingTggl.selected)

    def getClothesByRenderOrder(self):
        """
        Return UUIDs of clothes proxys sorted on proxy.z_depth render queue
        parameter (the order in which they will be rendered).
        """
        decoratedClothesList = [(pxy.z_depth, pxy.uuid) for pxy in self.getSelection()]
        decoratedClothesList.sort()
        return [uuid for (_, uuid) in decoratedClothesList]

    def updateFaceMasks(self, enableFaceHiding = True):
        """
        Apply facemask (deleteVerts) defined on clothes to body and lower layers
        of clothing. Uses order as defined in self.clothesList.
        """
        if self.blockFaceMasking:
            return

        import proxy
        log.debug("Clothes library: updating face masks (face hiding %s).", "enabled" if enableFaceHiding else "disabled")

        human = self.human
        if not enableFaceHiding:
            human.changeVertexMask(None)

            proxies = self.getSelection()
            for pxy in proxies:
                obj = pxy.object
                obj.changeVertexMask(None)
            return


        vertsMask = np.ones(human.meshData.getVertexCount(), dtype=bool)

        stackedProxies = [human.clothesProxies[uuid] for uuid in reversed(self.getClothesByRenderOrder())]

        for pxy in stackedProxies:
            obj = pxy.object

            # Remap vertices from basemesh to proxy verts
            proxyVertMask = proxy.transferVertexMaskToProxy(vertsMask, pxy)

            # Apply accumulated mask from previous clothes layers on this clothing piece
            obj.changeVertexMask(proxyVertMask)

            if pxy.deleteVerts is not None and len(pxy.deleteVerts > 0):
                log.debug("Loaded %s deleted verts (%s faces) from %s proxy.", np.count_nonzero(pxy.deleteVerts), len(human.meshData.getFacesForVertices(np.argwhere(pxy.deleteVerts)[...,0])),pxy.name)

                # Modify accumulated (basemesh) verts mask
                verts = np.argwhere(pxy.deleteVerts)[...,0]
                vertsMask[verts] = False

        human.changeVertexMask(vertsMask)

    def onShow(self, event):
        super(ClothesTaskView, self).onShow(event)
        if gui3d.app.getSetting('cameraAutoZoom'):
            gui3d.app.setGlobalCamera()

    def onHide(self, event):
        super(ClothesTaskView, self).onHide(event)
        self.visualizeFaceMasks(False)

    def loadHandler(self, human, values, strict):
        if values[0] == 'status':
            if values[1] == 'started':
                # Don't update face masks during loading (optimization)
                self.blockFaceMasking = True
            elif values[1] == 'finished':
                # When loading ends, update face masks
                self.blockFaceMasking = False
                self.updateFaceMasks(self.faceHidingTggl.selected)
            return

        if values[0] == 'clothesHideFaces':
            enabled = values[1].lower() in ['true', 'yes']
            self.faceHidingTggl.setChecked(enabled)
            return

        super(ClothesTaskView, self).loadHandler(human, values, strict)

    def onHumanChanged(self, event):
        super(ClothesTaskView, self).onHumanChanged(event)
        if event.change == 'reset':
            self.faceHidingTggl.setSelected(True)  # TODO super already reapplies masking before this is reset
        elif event.change == 'proxy' and event.pxy == 'proxymeshes' and \
             self.faceHidingTggl.selected:
            # Update face masks if topology was changed
            self.updateFaceMasks(self.faceHidingTggl.selected)

    def saveHandler(self, human, file):
        super(ClothesTaskView, self).saveHandler(human, file)
        file.write('clothesHideFaces %s\n' % str(self.faceHidingTggl.selected))

    def registerLoadSaveHandlers(self):
        super(ClothesTaskView, self).registerLoadSaveHandlers()
        gui3d.app.addLoadHandler('clothesHideFaces', self.loadHandler)

    def visualizeFaceMasks(self, enabled):
        import material
        import getpath
        if enabled:
            self.oldPxyMats = dict()
            xray_mat = material.fromFile(getpath.getSysDataPath('materials/xray.mhmat'))
            for pxy in self.human.getProxies(includeHumanProxy=False):
                print pxy.type
                if pxy.type == 'Eyes':
                    # Don't X-ray the eyes, it looks weird
                    continue
                self.oldPxyMats[pxy.uuid] = pxy.object.material.clone()
                pxy.object.material = xray_mat
        else:
            for pxy in self.human.getProxies(includeHumanProxy=False):
                if pxy.uuid in self.oldPxyMats:
                    pxy.object.material = self.oldPxyMats[pxy.uuid]

class FaceHideCheckbox(gui.CheckBox):
    def enterEvent(self, event):
        self.callEvent("onMouseEntered", None)

    def leaveEvent(self, event):
        self.callEvent("onMouseExited", None)


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements

taskview = None

def load(app):
    global taskview

    category = app.getCategory('Geometries')
    taskview = ClothesTaskView(category)
    taskview.sortOrder = 0
    category.addTask(taskview)

    taskview.registerLoadSaveHandlers()

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    taskview.onUnload()

