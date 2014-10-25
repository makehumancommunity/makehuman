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

Main skeleton tab
"""

import mh
import gui
import gui3d
import log
from collections import OrderedDict
import filechooser as fc

import skeleton
import skeleton_drawing
import animation
import getpath
import material

import numpy as np
import os

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

class SkeletonLibrary(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Skeleton')
        self.optionsSelector = None

        self._skelFileCache = None

        self.systemRigs = mh.getSysDataPath('rigs')
        self.userRigs = os.path.join(mh.getPath(''), 'data', 'rigs')
        self.rigPaths = [self.userRigs, self.systemRigs]
        if not os.path.exists(self.userRigs):
            os.makedirs(self.userRigs)
        self.extension = "rig"

        self.human = gui3d.app.selectedHuman

        self.referenceRig = None

        self.selectedRig = None

        self.humanChanged = False   # Used for determining when joints need to be redrawn

        self.skelMesh = None
        self.skelObj = None

        self.jointsMesh = None
        self.jointsObj = None

        self.selectedJoint = None

        self.oldHumanMat = self.human.material
        self.oldPxyMats = dict()

        #
        #   Display box
        #

        '''
        self.displayBox = self.addLeftWidget(gui.GroupBox('Display'))
        self.showHumanTggl = self.displayBox.addWidget(gui.CheckBox("Show human"))
        @self.showHumanTggl.mhEvent
        def onClicked(event):
            if self.showHumanTggl.selected:
                self.human.show()
            else:
                self.human.hide()
        self.showHumanTggl.setSelected(True)

        self.showJointsTggl = self.displayBox.addWidget(gui.CheckBox("Show joints"))
        @self.showJointsTggl.mhEvent
        def onClicked(event):
            if not self.jointsObj:
                return
            if self.showJointsTggl.selected:
                self.jointsObj.show()
            else:
                self.jointsObj.hide()
        self.showJointsTggl.setSelected(True)
        '''

        self.sysDataPath = getpath.getSysDataPath('rigs')
        self.userDataPath = getpath.getDataPath('rigs')
        if not os.path.exists(self.userDataPath):
            os.makedirs(self.userDataPath)
        self.paths = [self.userDataPath, self.sysDataPath]

        #
        #   Preset box
        #

        self.filechooser = self.addRightWidget(fc.IconListFileChooser( \
                                                    self.paths,
                                                    'json',
                                                    'thumb',
                                                    name='Rig presets',
                                                    notFoundImage = mh.getSysDataPath('notfound.thumb'), 
                                                    noneItem = True, 
                                                    doNotRecurse = True))
        self.filechooser.setIconSize(50,50)

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

        descBox = self.addLeftWidget(gui.GroupBox('Description'))
        self.descrLbl = descBox.addWidget(gui.TextView(''))
        self.descrLbl.setSizePolicy(gui.QtGui.QSizePolicy.Ignored, gui.QtGui.QSizePolicy.Preferred)
        self.descrLbl.setWordWrap(True)

        self.xray_mat = None

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        if gui3d.app.settings.get('cameraAutoZoom', True):
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
        if self.human.getSkeleton():
            self.drawSkeleton(self.human.getSkeleton())
            self.human.refreshPose()
            mh.redraw()


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

        if self.referenceRig is None:
            log.message("Loading reference skeleton for weights remapping.")
            self.referenceRig = skeleton.load(getpath.getSysDataPath('rigs/default.json'), self.human.meshData)

        if not filename:
            if self.human.getSkeleton():
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

        # Load skeleton definition from options
        skel = skeleton.load(filename, self.human.meshData)

        # Ensure vertex weights of skel are initialized
        skel.autoBuildWeightReferences(self.referenceRig)  # correct weights references if only (pose) references were defined
        vertexWeights = skel.getVertexWeights(self.referenceRig.getVertexWeights())
        log.message("Skeleton %s has %s weights per vertex.", skel.name, vertexWeights.getMaxNumberVertexWeights())

        # Update description
        descr = skel.description
        self.descrLbl.setText(descr)
        self.boneCountLbl.setTextFormat(["Bones",": %s"], skel.getBoneCount())

        # (Re-)draw the skeleton (before setting skeleton on human so it is automatically re-posed)
        self.drawSkeleton(skel)

        # Assign to human
        self.human.setSkeleton(skel)

        self.filechooser.selectItem(filename)


    def drawSkeleton(self, skel):
        if self.skelObj:
            # Remove old skeleton mesh
            self.removeObject(self.skelObj)
            self.human.removeBoundMesh(self.skelObj.name)
            self.skelObj = None
            self.skelMesh = None

        if not skel:
            return

        # Create a mesh from the skeleton in rest pose
        skel.setToRestPose() # Make sure skeleton is in rest pose when constructing the skeleton mesh
        self.skelMesh = skeleton_drawing.meshFromSkeleton(skel, "Prism")
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

        mh.redraw()

    def getTags(self, filename=None):
        import filecache
        def _getSkeletonTags(filename):
            return skeleton.peekMetadata(filename)

        if self._skelFileCache is None:
            # Init cache
            self.loadCache()
            self._skelFileCache = filecache.updateFileCache(self.paths, 'mhmat', _getSkeletonTags,self._skelFileCache, False)

        # TODO move most of this (duplicated) logic inside a class in filecache
        result = set()

        if filename:
            fileId = getpath.canonicalPath(filename)
            if fileId not in self._skelFileCache:
                # Lazily update cache
                self._skelFileCache = filecache.updateFileCache(self.paths + [os.path.dirname(fileId)], 'json', _getSkeletonTags,self._skelFileCache, False)

            if fileId in self._skelFileCache:
                metadata = self._skelFileCache[fileId]
                if metadata is not None:
                    mtime, name, desc, tags = metadata

                    if mtime < os.path.getmtime(fileId):
                        # Queried file was updated, update stale cache
                        self._skelFileCache = filecache.updateFileCache(self.paths + [os.path.dirname(fileId)], 'json', _getSkeletonTags,self._skelFileCache, False)
                        metadata = self._skelFileCache[fileId]
                        mtime, name, desc, tags = metadata

                    result = result.union(tags)
            else:
                log.warning('Could not get tags for material file %s. Does not exist in Material library.', filename)
            return result
        else:
            for (path, values) in self._skelFileCache.items():
                _, name, desc, tags = values
                result = result.union(tags)
        return result

    def onUnload(self):
        """
        Called when this library taskview is being unloaded (usually when MH
        is exited).
        Note: make sure you connect the plugin's unload() method to this one!
        """
        self.storeCache()

    def storeCache(self):
        import filecache
        if self._skelFileCache is None or len(self._skelFileCache) == 0:
            return

        filecache.cleanupCache(self._skelFileCache)

        cachedir = getpath.getPath('cache')
        if not os.path.isdir(cachedir):
            os.makedirs(cachedir)
        filecache.saveCache(self._skelFileCache, os.path.join(cachedir, 'skeleton_filecache.mhc'))

    def loadCache(self):
        import filecache
        filename = getpath.getPath('cache/skeleton_filecache.mhc')
        if os.path.isfile(filename):
            self._skelFileCache = filecache.loadCache(filename)

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

    def loadHandler(self, human, values):
        if values[0] == "skeleton":
            skelFile = values[1]

            skelFile = getpath.thoroughFindFile(skelFile, self.paths)
            if not os.path.isfile(skelFile):
                log.warning("Could not load rig %s, file does not exist." % skelFile)
            else:
                self.chooseSkeleton(skelFile)
            return

    def saveHandler(self, human, file):
        if human.getSkeleton():
            rigFile = getpath.getRelativePath(self.selectedRig, self.paths)
            file.write('skeleton %s\n' % rigFile)