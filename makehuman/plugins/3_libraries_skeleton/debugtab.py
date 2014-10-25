#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

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

Skeleton library.
Developer help taskview that allows inspecting properties of a skeleton
"""

import gui
import gui3d
import material
import mh
import skeleton_drawing
import numpy as np

#------------------------------------------------------------------------------------------
#   class SkeletonDebugLibrary
#------------------------------------------------------------------------------------------

class SkeletonDebugLibrary(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Skeleton Debug')
        self.human = gui3d.app.selectedHuman

        self.displayBox = self.addRightWidget(gui.GroupBox('Display'))

        self.selectedBone = None
        self.boneBox = self.addRightWidget(gui.GroupBox('Bones'))
        self.boneSelector = []

        self.xray_mat = None

        self.skelMesh = None
        self.skelObj = None

        self.showWeightsTggl = self.displayBox.addWidget(gui.CheckBox("Show bone weights"))
        @self.showWeightsTggl.mhEvent
        def onClicked(event):
            if self.showWeightsTggl.selected:
                # Highlight bone selected in bone explorer again
                for rdio in self.boneSelector:
                    if rdio.selected:
                        self.highlightBone(str(rdio.text()))
            else:
                self.clearBoneWeights()
        self.showWeightsTggl.setSelected(True)

    def _unloadSkeletonMesh(self):
        if self.skelObj:
            # Remove old skeleton mesh
            self.removeObject(self.skelObj)
            self.human.removeBoundMesh(self.skelObj.name)
            self.skelObj = None
            self.skelMesh = None

    def drawSkeleton(self):
        self._unloadSkeletonMesh()

        skel = self.human.getSkeleton()
        if not skel:
            return

        # Create a mesh from the skeleton in rest pose
        skel.setToRestPose() # Make sure skeleton is in rest pose when constructing the skeleton mesh
        self.skelMesh = skeleton_drawing.meshFromSkeleton(skel, "Prism")
        self.skelMesh.name = self.skelMesh.name + '-skeletonDebug'
        self.skelMesh.priority = 100
        self.skelMesh.setPickable(False)
        self.skelObj = self.addObject(gui3d.Object(self.skelMesh, self.human.getPosition()) )
        self.skelObj.setShadeless(0)
        self.skelObj.setSolid(0)
        self.skelObj.setRotation(self.human.getRotation())

        # Add the skeleton mesh to the human AnimatedMesh so it animates together with the skeleton
        # The skeleton mesh is supposed to be constructed from the skeleton in rest and receives
        # rigid vertex-bone weights (for each vertex exactly one weight of 1 to one bone)
        mapping = skeleton_drawing.getVertBoneMapping(skel, self.skelMesh)
        self.human.addBoundMesh(self.skelMesh, mapping)

        self.human.refreshPose()  # Pose drawn skeleton if human is posed
        mh.redraw()

    def reloadBoneExplorer(self):
        # Remove old radio buttons
        for radioBtn in self.boneSelector:
            radioBtn.hide()
            radioBtn.destroy()
        self.boneSelector = []

        skel = self.human.getSkeleton()
        if not skel:
            return

        for bone in skel.getBones():
            radioBtn = self.boneBox.addWidget(gui.RadioButton(self.boneSelector, bone.name))
            @radioBtn.mhEvent
            def onClicked(event):
                for rdio in self.boneSelector:
                    if rdio.selected:
                        self.removeBoneHighlights()
                        self.highlightBone(str(rdio.text()))

    def highlightBone(self, name):
        # Highlight bones
        self.selectedBone = name
        setColorForFaceGroup(self.skelMesh, self.selectedBone, [216, 110, 39, 255])
        gui3d.app.statusPersist(name)

        # Draw bone weights
        boneWeights = self.human.getVertexWeights()
        self.showBoneWeights(name, boneWeights)

        gui3d.app.redraw()

    def showBoneWeights(self, boneName, boneWeights):
        # TODO also allow coloring subdivided and proxy meshes
        mesh = self.human.meshData
        try:
            weights = np.asarray(boneWeights.data[boneName][1], dtype=np.float32)
            verts = boneWeights.data[boneName][0]
        except:
            return
        red = np.maximum(weights, 0)
        green = 1.0 - red
        blue = np.zeros_like(red)
        alpha = np.ones_like(red)
        color = np.array([red,green,blue,alpha]).T
        color = (color * 255.99).astype(np.uint8)
        mesh.color[verts,:] = color
        mesh.markCoords(verts, colr = True)
        mesh.sync_all()


    def removeBoneHighlights(self):
        # Disable highlight on bone
        if self.selectedBone:
            setColorForFaceGroup(self.skelMesh, self.selectedBone, [255,255,255,255])
            gui3d.app.statusPersist('')

            self.clearBoneWeights()
            self.selectedBone = None

            gui3d.app.redraw()


    def clearBoneWeights(self):
        mesh = self.human.meshData
        mesh.color[...] = (255,255,255,255)
        mesh.markCoords(colr = True)
        mesh.sync_all()

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)

        if self.skelObj is None:
            self.drawSkeleton()

        # Set X-ray material
        if self.xray_mat is None:
            self.xray_mat = material.fromFile(mh.getSysDataPath('materials/xray.mhmat'))
            self.xray_mat.setShaderParameter('edgefalloff', 5)
            self.xray_mat.configureShading(vertexColors=True)
        self.oldHumanMat = self.human.material.clone()
        self.oldPxyMats = dict()
        self.human.material = self.xray_mat
        for pxy in self.human.getProxies(includeHumanProxy=False):
            obj = pxy.object
            self.oldPxyMats[pxy.uuid] = obj.material.clone()
            obj.material = self.xray_mat

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

        self.human.material = self.oldHumanMat
        for pxy in self.human.getProxies(includeHumanProxy=False):
            if pxy.uuid in self.oldPxyMats:
                pxy.object.material = self.oldPxyMats[pxy.uuid]

        mh.redraw()

    def onHumanChanged(self, event):
        human = event.human
        if event.change == 'reset':
            if self.isShown():
                # Refresh onShow status
                self.onShow(event)
        elif event.change == 'skeleton':
            self._unloadSkeletonMesh()
            self.reloadBoneExplorer()

def setColorForFaceGroup(mesh, fgName, color):
    if mesh is None:
        return
    color = np.asarray(color, dtype=np.uint8)
    try:
        groupVerts = mesh.getVerticesForGroups([fgName])
        mesh.color[groupVerts] = color[None,:]
    except KeyError:
        return
    mesh.markCoords(colr=True)
    mesh.sync_color()
