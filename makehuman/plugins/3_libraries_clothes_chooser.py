#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers, Jonas Hauquier, Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Clothes library.
"""

import proxychooser

import os
import gui3d
import mh
import files3d
import mh2proxy
import exportutils
import gui
import filechooser as fc
import log
import numpy as np


#
#   Clothes
#

class ClothesTaskView(proxychooser.ProxyChooserTaskView):

    def __init__(self, category):
        super(ClothesTaskView, self).__init__(category, 'clothes', multiProxy = True, tagFilter = True)

        #self.taggedClothes = {}

        self.originalHumanMask = gui3d.app.selectedHuman.meshData.getFaceMask().copy()
        self.faceHidingTggl = self.optionsBox.addWidget(gui.CheckBox("Hide faces under clothes"))
        @self.faceHidingTggl.mhEvent
        def onClicked(event):
            self.updateFaceMasks(self.faceHidingTggl.selected)
        self.faceHidingTggl.setSelected(True)

        self.blockFaceMasking = False

    def createFileChooser(self):
        self.optionsBox = self.addLeftWidget(gui.GroupBox('Options'))
        super(ClothesTaskView, self).createFileChooser()

    def getObjectLayer(self):
        return 10

    def proxySelected(self, proxy, obj):
        uuid = proxy.getUuid()

        self.human.clothesObjs[uuid] = obj
        self.human.clothesProxies[uuid] = proxy

        self.updateFaceMasks(self.faceHidingTggl.selected)

    def proxyDeselected(self, proxy, obj, suppressSignal = False):
        uuid = proxy.uuid
        del self.human.clothesObjs[uuid]
        del self.human.clothesProxies[uuid]

        if not suppressSignal:
            self.updateFaceMasks(self.faceHidingTggl.selected)

    def resetSelection(self):
        super(ClothesTaskView, self).resetSelection()
        self.updateFaceMasks(self.faceHidingTggl.selected)

    def getClothesRenderOrder(self):
        """
        Return UUIDs of clothes proxys sorted on proxy.z_depth render queue 
        parameter (the order in which they will be rendered).
        """
        decoratedClothesList = [(proxy.z_depth, proxy.uuid) for proxy in self.getSelection()]
        decoratedClothesList.sort()
        return [uuid for (_, uuid) in decoratedClothesList]

    def updateFaceMasks(self, enableFaceHiding = True):
        """
        Apply facemask (deleteVerts) defined on clothes to body and lower layers
        of clothing. Uses order as defined in self.clothesList.
        """
        if self.blockFaceMasking:
            return

        log.debug("Clothes library: updating face masks (face hiding %s).", "enabled" if enableFaceHiding else "disabled")

        human = gui3d.app.selectedHuman
        if not enableFaceHiding:
            human.meshData.changeFaceMask(self.originalHumanMask)
            human.meshData.updateIndexBufferFaces()
            for uuid in [proxy.uuid for proxy in self.getSelection()]:
                obj = human.clothesObjs[uuid]
                faceMask = np.ones(obj.mesh.getFaceCount(), dtype=bool)
                obj.mesh.changeFaceMask(faceMask)
                obj.mesh.updateIndexBufferFaces()
            return

        vertsMask = np.ones(human.meshData.getVertexCount(), dtype=bool)
        log.debug("masked verts %s", np.count_nonzero(~vertsMask))
        for uuid in reversed(self.getClothesRenderOrder()):
            proxy = human.clothesProxies[uuid]
            obj = human.clothesObjs[uuid]

            # Convert basemesh vertex mask to local mask for proxy vertices
            proxyVertMask = np.ones(len(proxy.refVerts), dtype=bool)
            for idx,vs in enumerate(proxy.refVerts):
                # Body verts to which proxy vertex with idx is mapped
                (v1,v2,v3) = vs.getHumanVerts()
                # Hide proxy vert if any of its referenced body verts are hidden (most agressive)
                #proxyVertMask[idx] = vertsMask[v1] and vertsMask[v2] and vertsMask[v3]
                # Alternative1: only hide if at least two referenced body verts are hidden (best result)
                proxyVertMask[idx] = np.count_nonzero(vertsMask[[v1, v2, v3]]) > 1
                # Alternative2: Only hide proxy vert if all of its referenced body verts are hidden (least agressive)
                #proxyVertMask[idx] = vertsMask[v1] or vertsMask[v2] or vertsMask[v3]

            proxyKeepVerts = np.argwhere(proxyVertMask)[...,0]
            proxyFaceMask = obj.mesh.getFaceMaskForVertices(proxyKeepVerts)

            # Apply accumulated mask from previous clothes layers on this clothing piece
            obj.mesh.changeFaceMask(proxyFaceMask)
            obj.mesh.updateIndexBufferFaces()
            log.debug("%s faces masked for %s", np.count_nonzero(~proxyFaceMask), proxy.name)

            if proxy.deleteVerts != None and len(proxy.deleteVerts > 0):
                log.debug("Loaded %s deleted verts (%s faces) from %s", np.count_nonzero(proxy.deleteVerts), len(human.meshData.getFacesForVertices(np.argwhere(proxy.deleteVerts)[...,0])),proxy.name)

                # Modify accumulated (basemesh) verts mask
                verts = np.argwhere(proxy.deleteVerts)[...,0]
                vertsMask[verts] = False
            log.debug("masked verts %s", np.count_nonzero(~vertsMask))

        basemeshMask = human.meshData.getFaceMaskForVertices(np.argwhere(vertsMask)[...,0])
        human.meshData.changeFaceMask(np.logical_and(basemeshMask, self.originalHumanMask))
        human.meshData.updateIndexBufferFaces()

        # Transfer face mask to subdivided mesh if it is set
        if human.isSubdivided():
            human.updateSubdivisionMesh(rebuildIndexBuffer=True, progressCallback=gui3d.app.progress)

        log.debug("%s faces masked for basemesh", np.count_nonzero(~basemeshMask))


    def onShow(self, event):
        super(ClothesTaskView, self).onShow(event)
        if gui3d.app.settings.get('cameraAutoZoom', True):
            gui3d.app.setGlobalCamera()

    def loadHandler(self, human, values):
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

        super(ClothesTaskView, self).loadHandler(human, values)

    def onHumanChanged(self, event):
        super(ClothesTaskView, self).onHumanChanged(event)
        if event.change == 'reset':
            self.faceHidingTggl.setSelected(True)

    def saveHandler(self, human, file):
        super(ClothesTaskView, self).saveHandler(human, file)
        file.write('clothesHideFaces %s\n' % self.faceHidingTggl.selected)

    def registerLoadSaveHandlers(self):
        super(ClothesTaskView, self).registerLoadSaveHandlers()
        gui3d.app.addLoadHandler('clothesHideFaces', self.loadHandler)


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

