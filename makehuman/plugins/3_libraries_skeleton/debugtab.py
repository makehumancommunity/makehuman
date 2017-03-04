#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

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
        self.axisMesh = None
        self.axisObj = None
        self.planesObj = None
        self.planesMesh = None

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

        self.showAxisTggl = self.displayBox.addWidget(gui.CheckBox("Show bone axis"))
        @self.showAxisTggl.mhEvent
        def onClicked(event):
            if self.axisObj:
                self.axisObj.setVisibility(self.showAxisTggl.selected)
        self.showAxisTggl.setSelected(True)

        self.showBonesTggl = self.displayBox.addWidget(gui.CheckBox("Show bones"))
        @self.showBonesTggl.mhEvent
        def onClicked(event):
            if self.skelObj:
                self.skelObj.setVisibility(self.showBonesTggl.selected)
        self.showBonesTggl.setSelected(True)

        self.showPlanesTggl = self.displayBox.addWidget(gui.CheckBox("Show bone planes"))
        @self.showPlanesTggl.mhEvent
        def onClicked(event):
            if self.planesObj:
                self.planesObj.setVisibility(self.showPlanesTggl.selected)
        self.showPlanesTggl.setSelected(False)

    def _unloadSkeletonMesh(self):
        if self.skelObj:
            # Remove old skeleton mesh
            self.removeObject(self.skelObj)
            self.removeObject(self.axisObj)
            self.removeObject(self.planesObj)
            self.skelObj = None
            self.skelMesh = None
            self.axisMesh = None
            self.axisObj = None
            self.planesObj = None
            self.planesMesh = None

    def drawSkeleton(self):
        self._unloadSkeletonMesh()

        skel = self.human.getSkeleton()
        if not skel:
            return

        # Create a mesh from the user-selected skeleton in its current pose (so we use the base skeleton for actually posing)
        self.skelMesh = skeleton_drawing.meshFromSkeleton(skel, "Prism")
        self.skelMesh.name = self.skelMesh.name + '-skeletonDebug'
        self.skelMesh.priority = 100
        self.skelMesh.setPickable(False)
        self.skelObj = self.addObject(gui3d.Object(self.skelMesh, self.human.getPosition()) )
        self.skelObj.setShadeless(0)
        self.skelObj.setSolid(0)
        self.skelObj.setRotation(self.human.getRotation())
        self.skelMesh.setVisibility(self.showBonesTggl.selected)

        self.axisMesh = skeleton_drawing.meshFromSkeleton(skel, "axis")
        self.axisMesh.name = self.axisMesh.name + '-axis-skeletonDebug'
        self.axisMesh.priority = 100
        self.axisMesh.setPickable(False)
        self.axisObj = self.addObject(gui3d.Object(self.axisMesh, self.human.getPosition()) )
        self.axisObj.material.ambientColor = [0.2, 0.2, 0.2]
        self.axisObj.material.configureShading(vertexColors=True)
        self.axisObj.material.depthless = True
        self.axisObj.setRotation(self.human.getRotation())
        self.axisObj.setVisibility(self.showAxisTggl.selected)

        self.drawPlanes(skel)

        mh.redraw()

    def drawPlanes(self, skel):
        def _get_face_count(skel):
            result = 0
            for bone in skel.getBones():
                if isinstance(bone.roll, list):
                    result += len(bone.roll)
                else:
                    result += 1
            return result

        import module3d
        self.planesMesh = module3d.Object3D("SkeletonPlanesMesh", 3)

        facecount = _get_face_count(skel)
        vertcount = 3*facecount
        faces = np.arange(vertcount, dtype=np.uint16).reshape((facecount, 3))
        verts = np.zeros((vertcount,3), dtype=np.float32)
        vcolors = 255*np.ones((vertcount, 4), dtype=np.uint8)
        PLANE_COLORS = [[60,230,200], [220, 60, 230], [230, 180, 60], [230, 90, 60], [60, 230, 60], [60, 120, 230]]

        fgroups = np.zeros(len(faces), dtype=np.uint16)
        v_offset = 0
        for bIdx, bone in enumerate(skel.getBones()):
            fg = self.planesMesh.createFaceGroup(bone.name)
            fgroups[bIdx:bIdx+1] = np.repeat(np.array(fg.idx, dtype=np.uint16), 1)
            if isinstance(bone.roll, list):
                for p_idx, plane_name in enumerate(bone.roll):
                    plane_name = bone.roll[0]
                    plane_joints = bone.planes[plane_name]

                    j1,j2,j3 = plane_joints
                    in_rest = False
                    p1 = skel.getJointPosition(j1, self.human, in_rest)[:3] * skel.scale
                    p2 = skel.getJointPosition(j2, self.human, in_rest)[:3] * skel.scale
                    p3 = skel.getJointPosition(j3, self.human, in_rest)[:3] * skel.scale
                    verts[v_offset:v_offset+3] = [p1, p2, p3]
                    vcolors[v_offset:v_offset+3,:3] = PLANE_COLORS[p_idx]
                    fgroups[v_offset/3] = fg.idx
                    v_offset += 3
            elif isinstance(bone.roll, basestring):
                plane_name = bone.roll
                plane_joints = bone.planes[plane_name]

                j1,j2,j3 = plane_joints
                in_rest = False
                p1 = skel.getJointPosition(j1, self.human, in_rest)[:3] * skel.scale
                p2 = skel.getJointPosition(j2, self.human, in_rest)[:3] * skel.scale
                p3 = skel.getJointPosition(j3, self.human, in_rest)[:3] * skel.scale
                verts[v_offset:v_offset+3] = [p1, p2, p3]
                vcolors[v_offset:v_offset+3,:3] = PLANE_COLORS[0]
                fgroups[v_offset/3] = fg.idx
                v_offset += 3
            else:
                p1 = p2 = p3 = [0.0, 0.0, 0.0]
                verts[v_offset:v_offset+3] = [p1, p2, p3]
                vcolors[v_offset:v_offset+3,:3] = [255, 0, 0]
                fgroups[v_offset/3] = fg.idx
                v_offset += 3

        self.planesMesh.setCoords(verts)
        self.planesMesh.setColor(vcolors)
        self.planesMesh.setUVs(np.zeros((1, 2), dtype=np.float32)) # Set trivial UV coordinates
        self.planesMesh.setFaces(faces, None, fgroups)
        
        self.planesMesh.updateIndexBuffer()
        self.planesMesh.calcNormals()
        self.planesMesh.update()

        self.planesMesh.setCameraProjection(0)

        self.planesMesh.priority = 100
        self.planesMesh.setPickable(False)
        self.planesObj = self.addObject(gui3d.Object(self.planesMesh, self.human.getPosition()) )
        self.planesObj.setShadeless(0)
        self.planesObj.setSolid(0)
        self.planesObj.setRotation(self.human.getRotation())
        self.planesObj.material.backfaceCull = False
        self.planesObj.setVisibility(self.showPlanesTggl.selected)


    def reloadBoneExplorer(self):
        # Remove old radio buttons
        for radioBtn in self.boneSelector:
            radioBtn.hide()
            radioBtn.destroy()
        self.boneSelector = []

        #skel = self.human.getSkeleton()
        skel = self.human.skeleton  # We do this because we do not need updated joint positions
        if not skel:
            return

        bones = [(bone.name, bone) for bone in skel.getBones()]
        bones.sort()  # Sort by name
        for _, bone in bones:
            # TODO using a tree widget here, as in Utilities > Data would be good
            radioBtn = self.boneBox.addWidget(gui.RadioButton(self.boneSelector, bone.name))
            @radioBtn.mhEvent
            def onClicked(event):
                for rdio in self.boneSelector:
                    if rdio.selected:
                        self.removeBoneHighlights()
                        self.highlightBone(str(rdio.text()))

    def highlightBone(self, name):
        if not self.showWeightsTggl.selected:
            return
        # Highlight bones
        self.selectedBone = name
        setColorForFaceGroup(self.skelMesh, self.selectedBone, [216, 110, 39, 255])
        gui3d.app.statusPersist(name)

        # Draw bone weights
        rawWeights = self.human.getVertexWeights(self.human.getSkeleton())

        objects = self.human.getObjects(excludeZeroFaceObjs=True)
        for obj in objects:
            # Remap vertex weights to mesh
            if obj.proxy:
                parentWeights = obj.proxy.getVertexWeights(rawWeights, self.human.getSkeleton())
            else:
                parentWeights = rawWeights
            weights = obj.mesh.getVertexWeights(parentWeights)

            self.showBoneWeights(name, weights, obj.mesh)

        gui3d.app.redraw()

    def showBoneWeights(self, boneName, boneWeights, mesh):
        # TODO also allow coloring subdivided and proxy meshes
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
        color = (color * 255).astype(np.uint8)
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
        objects = self.human.getObjects(excludeZeroFaceObjs=True)
        for obj in objects:
            # TODO this will go wrong when toggling between subdivided/unsubdivided state
            mesh = obj.mesh
            mesh.color[...] = (255,255,255,255)
            mesh.markCoords(colr = True)
            mesh.sync_all()

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)

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
        elif event.change == 'user-skeleton':
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
