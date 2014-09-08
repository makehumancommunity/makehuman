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

Pose library
"""

import gui3d
import mh
import gui
import log
import filechooser as fc
import animation
import bvh
import os
from core import G

import skeleton_drawing
import material

class PoseLibraryTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Pose')
        self.human = G.app.selectedHuman
        self.currentPose = None

        self.paths = [mh.getDataPath('poses'), mh.getSysDataPath('poses')]

        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.paths, ['bvh'], 'thumb', mh.getSysDataPath('poses/notfound.thumb'), name='Pose'))
        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(False)

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            # TODO add action
            self.loadPose(filename)

        box = self.addLeftWidget(gui.GroupBox('Pose'))

        self.skelObj = None

    def loadPose(self, filepath, apply_pose=True):
        if not self.human.getSkeleton():
            log.error("No skeleton selected, cannot load pose")
            return

        self.currentPose = filepath

        if not filepath:
            self.human.resetToRestPose()

        if os.path.splitext(filepath)[1].lower() == '.mhp':
            anim = self.loadMhp(filepath)
        elif os.path.splitext(filepath)[1].lower() == '.bvh':
            anim = self.loadBvh(filepath, convertFromZUp="auto")
        else:
            log.error("Cannot load pose file %s: File type unknown." % filepath)
            return

        #self.human.setAnimateInPlace(True)
        self.human.addAnimation(anim)
        self.human.setActiveAnimation(anim.name)
        self.human.setToFrame(0, update=False)
        if apply_pose:
            self.human.setPosed(True)

    def loadMhp(self, filepath):
        return animation.loadPoseFromMhpFile(filepath, self.human.getSkeleton())

    def loadBvh(self, filepath, convertFromZUp="auto"):
        bvh_file = bvh.load(filepath, convertFromZUp)
        self.autoScaleBVH(bvh_file)
        jointNames = [bone.name for bone in self.human.getSkeleton().getBones()]
        return bvh_file.createAnimationTrack(jointNames)

    def autoScaleBVH(self, bvh_file):
        """
        Auto scale BVH translations by comparing upper leg length
        """
        import numpy as np
        import numpy.linalg as la
        if "upperleg02.L" not in bvh_file.joints:
            raise RuntimeError('Failed to auto scale BVH file %s, it does not contain a joint for "upperleg02.L"' % bvh_file.name)
        bvh_joint = bvh_file.joints["upperleg02.L"]
        bone = self.human.getSkeleton().getBone("upperleg02.L")
        joint_length = la.norm(bvh_joint.children[0].position - bvh_joint.position)
        scale_factor = bone.length / joint_length
        log.message("Scaling BVH file %s with factor %s" % (bvh_file.name, scale_factor))
        bvh_file.scale(scale_factor)

    def onShow(self, event):
        self.filechooser.refresh()
        self.drawSkeleton(self.human.getSkeleton())
        self.human.refreshPose()

        # Set X-ray material
        self.oldHumanMat = self.human.material.clone()
        self.oldPxyMats = dict()
        xray_mat = material.fromFile(mh.getSysDataPath('materials/xray.mhmat'))
        self.human.material = xray_mat
        for pxy in self.human.getProxies(includeHumanProxy=False):
            obj = pxy.object
            self.oldPxyMats[pxy.uuid] = obj.material.clone()
            obj.material = xray_mat
        mh.redraw()

    def onHide(self, event):
        gui3d.app.statusPersist('')

        # Restore material
        self.human.material = self.oldHumanMat
        for pxy in self.human.getProxies(includeHumanProxy=False):
            if pxy.uuid in self.oldPxyMats:
                pxy.object.material = self.oldPxyMats[pxy.uuid]

    def drawSkeleton(self, skel):
        if self.skelObj:
            # Remove old skeleton mesh
            self.removeObject(self.skelObj)
            self.human.removeBoundMesh(self.skelObj.name)
            self.skelObj = None
            self.skelMesh = None
            self.selectedBone = None

        if not skel:
            return

        # Create a mesh from the skeleton in rest pose
        skel.setToRestPose() # Make sure skeleton is in rest pose when constructing the skeleton mesh
        self.skelMesh = skeleton_drawing.meshFromSkeleton(skel, "Prism")
        self.skelMesh.name = 'SkeletonMesh-poseLibrary'
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

        # Store a reference to the skeleton mesh object for other plugins
        self.human.getSkeleton().object = self.skelObj
        mh.redraw()

    def onHumanChanged(self, event):
        if event.change == 'skeleton':
            self.drawSkeleton(self.human.getSkeleton())
            if self.currentPose:
                self.loadPose(self.currentPose, apply_pose=False)
        elif event.change == 'reset':
            # Update GUI after reset (if tab is currently visible)
            if self.isShown():
                self.onShow(event)

category = None
taskview = None

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Pose/Animate')
    taskview = PoseLibraryTaskView(category)
    taskview.sortOrder = 2
    category.addTask(PoseLibraryTaskView(category))


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass
