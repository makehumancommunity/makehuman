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

Skeleton library, allows selecting an animation skeleton or rig for the human
to be exported.
This skeleton is not used within MakeHuman, as all posing and animation
is applied to the base skeleton, which is the default or reference skeleton.
"""

import mh
import gui
import gui3d
import log
import filechooser as fc
import filecache

import skeleton
import skeleton_drawing
import getpath
import material

import numpy as np
import os

REF_RIG_PATH = getpath.getSysDataPath('rigs/default.mhskel')

#------------------------------------------------------------------------------------------
#   class SkeletonAction
#------------------------------------------------------------------------------------------

class SkeletonAction(gui3d.Action):
    def __init__(self, name, library, before, after):
        super(SkeletonAction, self).__init__(name)
        self.library = library
        self.before = before
        self.after = after

    def do(self):
        self.library.chooseSkeleton(self.after)
        return True

    def undo(self):
        self.library.chooseSkeleton(self.before)
        return True


#------------------------------------------------------------------------------------------
#   class SkeletonLibrary
#------------------------------------------------------------------------------------------

class SkeletonLibrary(gui3d.TaskView, filecache.MetadataCacher):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Skeleton')
        filecache.MetadataCacher.__init__(self, 'mhskel', 'skeleton_filecache.mhc')

        self.human = gui3d.app.selectedHuman

        self.referenceRig = None

        self.selectedRig = None

        self.skelMesh = None
        self.skelObj = None

        self.jointsMesh = None
        self.jointsObj = None

        self.selectedJoint = None

        self.oldHumanMat = self.human.material
        self.oldPxyMats = dict()

        self.sysDataPath = getpath.getSysDataPath('rigs')
        self.userDataPath = getpath.getDataPath('rigs')
        if not os.path.exists(self.userDataPath):
            os.makedirs(self.userDataPath)
        self.paths = [self.userDataPath, self.sysDataPath]

        self.filechooser = self.addRightWidget(fc.IconListFileChooser( \
                                                    self.paths,
                                                    'mhskel',
                                                    'thumb',
                                                    name='Rig presets',
                                                    notFoundImage = mh.getSysDataPath('notfound.thumb'), 
                                                    noneItem = True, 
                                                    doNotRecurse = True))
        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(False)

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            if filename:
                msg = "Change skeleton"
            else:
                msg = "Clear skeleton"
            gui3d.app.do(SkeletonAction(msg, self, self.selectedRig, filename))

        self.filechooser.setFileLoadHandler(fc.TaggedFileLoader(self))
        self.addLeftWidget(self.filechooser.createTagFilter())

        self.infoBox = self.addLeftWidget(gui.GroupBox('Rig info'))
        self.boneCountLbl = self.infoBox.addWidget(gui.TextView('Bones: '))
        self.infoBox.setSizePolicy(gui.QtGui.QSizePolicy.Preferred, gui.QtGui.QSizePolicy.Maximum)

        descBox = self.addLeftWidget(gui.GroupBox('Description'))
        self.descrLbl = descBox.addWidget(gui.TextView(''))
        self.descrLbl.setSizePolicy(gui.QtGui.QSizePolicy.Ignored, gui.QtGui.QSizePolicy.Preferred)
        self.descrLbl.setWordWrap(True)

        self.xray_mat = None

        # the reference skeleton
        self.referenceRig = self.human.getBaseSkeleton()

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        if gui3d.app.getSetting('cameraAutoZoom'):
            gui3d.app.setGlobalCamera()

        # Set X-ray material
        if self.xray_mat is None:
            self.xray_mat = material.fromFile(mh.getSysDataPath('materials/xray.mhmat'))
        self.oldHumanMat = self.human.material.clone()
        self.oldPxyMats = dict()
        self.human.material = self.xray_mat
        for pxy in self.human.getProxies(includeHumanProxy=False):
            obj = pxy.object
            self.oldPxyMats[pxy.uuid] = obj.material.clone()
            obj.material = self.xray_mat

        # Make sure skeleton is updated if human has changed
        if self.human.skeleton:
            self.drawSkeleton()

        self.filechooser.refresh()
        self.filechooser.selectItem(self.selectedRig)

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

        self.human.material = self.oldHumanMat
        for pxy in self.human.getProxies(includeHumanProxy=False):
            if pxy.uuid in self.oldPxyMats:
                pxy.object.material = self.oldPxyMats[pxy.uuid]

        mh.redraw()


    def chooseSkeleton(self, filename):
        log.debug("Loading skeleton from %s", filename)
        self.selectedRig = filename

        if not filename:
            if self.human.skeleton:
                # Unload current skeleton
                self.human.setSkeleton(None)

            if self.skelObj:
                # Remove old skeleton mesh
                self.removeObject(self.skelObj)
                self.human.removeBoundMesh(self.skelObj.name)
                self.skelObj = None
                self.skelMesh = None
            self.boneCountLbl.setTextFormat(["Bones",": %s"], "")
            self.descrLbl.setText("")
            self.filechooser.selectItem(None)
            return

        if getpath.isSamePath(filename, REF_RIG_PATH):
            skel = self.referenceRig.createFromPose()
        else:
            # Load skeleton definition from options
            skel = skeleton.load(filename, self.human.meshData)

            # Ensure vertex weights of skel are initialized
            skel.autoBuildWeightReferences(self.referenceRig)  # correct weights references if only (pose) references were defined
            vertexWeights = skel.getVertexWeights(self.referenceRig.getVertexWeights(), force_remap=False)
            log.message("Skeleton %s has %s weights per vertex.", skel.name, vertexWeights.getMaxNumberVertexWeights())

            # Remap bone orientation planes from reference rig
            skel.addReferencePlanes(self.referenceRig)  # Not strictly needed for the new way in which we determine bone normals

        # Update description
        descr = skel.description
        self.descrLbl.setText(descr)
        self.boneCountLbl.setTextFormat(["Bones",": %s"], skel.getBoneCount())

        # Assign to human
        self.human.setSkeleton(skel)

        # (Re-)draw the skeleton
        self.drawSkeleton()

        self.filechooser.selectItem(filename)

    def drawSkeleton(self):
        if self.skelObj:
            # Remove old skeleton mesh
            self.removeObject(self.skelObj)
            self.skelObj = None
            self.skelMesh = None

        skel = self.human.getSkeleton()
        if not skel:
            return

        # Create a mesh from the skeleton
        self.skelMesh = skeleton_drawing.meshFromSkeleton(skel, "Prism")
        self.skelMesh.priority = 100
        self.skelMesh.setPickable(False)
        self.skelObj = self.addObject(gui3d.Object(self.skelMesh, self.human.getPosition()) )
        self.skelObj.setShadeless(0)
        self.skelObj.setSolid(0)
        self.skelObj.setRotation(self.human.getRotation())

        mh.redraw()

    def getMetadataImpl(self, filename):
        return skeleton.peekMetadata(filename)

    def getTagsFromMetadata(self, metadata):
        name, desc, tags = metadata
        return tags

    def getSearchPaths(self):
        return self.paths

    def drawJointHelpers(self):
        """
        Draw the joint helpers from the basemesh that define the default or
        reference rig.
        """
        if self.jointsObj:
            self.removeObject(self.jointsObj)
            self.jointsObj = None
            self.jointsMesh = None
            self.selectedJoint = None

        jointPositions = []
        # TODO maybe define a getter for this list in the skeleton module
        jointGroupNames = [group.name for group in self.human.meshData.faceGroups if group.name.startswith("joint-")]
        if self.human.getSkeleton():
            jointGroupNames += self.human.getSkeleton().joint_pos_idxs.keys()
            for groupName in jointGroupNames:
                jointPositions.append(self.human.getSkeleton().getJointPosition(groupName, self.human))
        else:
            for groupName in jointGroupNames:
                jointPositions.append(skeleton._getHumanJointPosition(self.human, groupName))

        self.jointsMesh = skeleton_drawing.meshFromJoints(jointPositions, jointGroupNames)
        self.jointsMesh.priority = 100
        self.jointsMesh.setPickable(False)
        self.jointsObj = self.addObject( gui3d.Object(self.jointsMesh, self.human.getPosition()) )
        self.jointsObj.setRotation(self.human.getRotation())

        color = np.asarray([255, 255, 0, 255], dtype=np.uint8)
        self.jointsMesh.color[:] = color[None,:]
        self.jointsMesh.markCoords(colr=True)
        self.jointsMesh.sync_color()

        mh.redraw()

    def onHumanChanged(self, event):
        human = event.human
        if event.change == 'reset':
            if self.isShown():
                # Refresh onShow status
                self.onShow(event)

    def onHumanChanging(self, event):
        if event.change == 'reset':
            self.chooseSkeleton(None)
            self.filechooser.selectItem(None)


    def onHumanRotated(self, event):
        if self.skelObj:
            self.skelObj.setRotation(gui3d.app.selectedHuman.getRotation())
        if self.jointsObj:
            self.jointsObj.setRotation(gui3d.app.selectedHuman.getRotation())


    def onHumanTranslated(self, event):
        if self.skelObj:
            self.skelObj.setPosition(gui3d.app.selectedHuman.getPosition())
        if self.jointsObj:
            self.jointsObj.setPosition(gui3d.app.selectedHuman.getPosition())

    def loadHandler(self, human, values, strict):
        if values[0] == "skeleton":
            skelFile = values[1]

            skelFile = getpath.thoroughFindFile(skelFile, self.paths)
            if not os.path.isfile(skelFile):
                if strict:
                    raise RuntimeError("Could not load rig %s, file does not exist." % skelFile)
                log.warning("Could not load rig %s, file does not exist.", skelFile)
            else:
                self.chooseSkeleton(skelFile)
            return

    def saveHandler(self, human, file):
        if human.getSkeleton():
            rigFile = getpath.getRelativePath(self.selectedRig, self.paths)
            file.write('skeleton %s\n' % rigFile)
