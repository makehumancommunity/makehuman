#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2019

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
import getpath
import filecache
import numpy as np


# Bone used for determining the pose scaling (root bone translation scale)
COMPARE_BONE = "upperleg02.L"


class PoseAction(gui3d.Action):
    def __init__(self, name, library, before, after):
        super(PoseAction, self).__init__(name)
        self.library = library
        self.before = before
        self.after = after

    def do(self):
        self.library.loadPose(self.after)
        return True

    def undo(self):
        self.library.loadPose(self.before)
        return True


class PoseLibraryTaskView(gui3d.TaskView, filecache.MetadataCacher):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Pose')
        filecache.MetadataCacher.__init__(self, ['bvh'], 'pose_filecache.mhc')
        self.cache_format_version = '1c'  # Bump cacher version for updated format of pose metadata

        self.human = G.app.selectedHuman
        self.currentPose = None
        self.bvh_bone_length = None
        self.bvh_root_translation = None

        self.sysDataPath = getpath.getSysDataPath('poses')
        self.userDataPath = getpath.getDataPath('poses')
        if not os.path.exists(self.userDataPath):
            os.makedirs(self.userDataPath)
        self.paths = [self.userDataPath, self.sysDataPath]

        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.paths, ['bvh'],
          'thumb', mh.getSysDataPath('poses/notfound.thumb'), name='Pose', noneItem=True, stickyTags=gui3d.app.getSetting('makehumanTags')))
        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(False)

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            gui3d.app.do(PoseAction("Change pose", self, self.currentPose, filename))

        self.filechooser.setFileLoadHandler(fc.TaggedFileLoader(self))
        self.addLeftWidget(self.filechooser.createTagFilter())

        self.skelObj = None

    def getMetadataFile(self, filename):
        metafile = os.path.splitext(filename)[0] + '.meta'
        if os.path.isfile(metafile):
            return metafile
        return filename

    def getMetadataImpl(self, filename):
        tags = set()
        if not os.path.isfile(filename):
            return (tags, )
        name = os.path.splitext(os.path.basename(filename))[0]
        description = ""
        license = mh.getAssetLicense()
        import io
        f = io.open(filename, encoding='utf-8')
        for l in f.read().split('\n'):
            l = l.strip()
            l = l.split()
            if len(l) == 0:
                continue
            if l[0].lower() == 'tag':
                tags.add((' '.join(l[1:])).lower())
            elif l[0].lower() == 'name':
                name = ' '.join(l[1:])
            elif l[0].lower() == 'description':
                description = ' '.join(l[1:])
            elif l[0].lower() == 'author':
                license.author = ' '.join(l[1:])
            elif l[0].lower() == 'license':
                license.license = ' '.join(l[1:])
            elif l[0].lower() == 'copyright':
                license.copyright = ' '.join(l[1:])
            elif l[0].lower() == 'homepage':
                license.homepage = ' '.join(l[1:])
        return (tags, name, description, license)

    def getTagsFromMetadata(self, metadata):
        return metadata[0]

    def getSearchPaths(self):
        return self.paths

    def loadPose(self, filepath, apply_pose=True):
        self.currentPose = filepath

        if not filepath:
            self.human.resetToRestPose()
            self.bvh_bone_length = None
            self.bvh_root_translation = None
            return

        if os.path.splitext(filepath)[1].lower() == '.mhp':
            anim = self.loadMhp(filepath)
        elif os.path.splitext(filepath)[1].lower() == '.bvh':
            anim = self.loadBvh(filepath, convertFromZUp="auto")
            if not anim:
                log.error('Cannot load animation from %s' % filepath)
                return
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
        return animation.loadPoseFromMhpFile(filepath, self.human.getBaseSkeleton())

    def loadBvh(self, filepath, convertFromZUp="auto"):
        bvh_file = bvh.load(filepath, convertFromZUp)
        if COMPARE_BONE not in bvh_file.joints:
            msg = 'The pose file cannot be loaded. It uses a different rig then MakeHuman\'s default rig'
            G.app.prompt('Error', msg, 'OK')
            log.error('Pose file %s does not use the default rig.' % filepath)
            return None
        anim = bvh_file.createAnimationTrack(self.human.getBaseSkeleton())
        if "root" in bvh_file.joints:
            posedata = anim.getAtFramePos(0, noBake=True)
            root_bone_idx = 0
            self.bvh_root_translation = posedata[root_bone_idx, :3, 3].copy()
        else:
            self.bvh_root_translation = np.asarray(3*[0.0], dtype=np.float32)
        self.bvh_bone_length = self.calculateBvhBoneLength(bvh_file)
        self.autoScaleAnim(anim)
        _, _, _, license = self.getMetadata(filepath)
        anim.license = license
        return anim

    def calculateBvhBoneLength(self, bvh_file):
        import numpy.linalg as la
        if COMPARE_BONE not in bvh_file.joints:
            raise RuntimeError('Failed to auto scale BVH file %s, it does not contain a joint for "%s"' % (bvh_file.name, COMPARE_BONE))

        bvh_joint = bvh_file.joints[COMPARE_BONE]
        joint_length = la.norm(bvh_joint.children[0].position - bvh_joint.position)
        return joint_length

    def autoScaleAnim(self, anim):
        """
        Auto scale BVH translations by comparing upper leg length to make the
        human stand on the ground plane, independent of body length.
        """
        import numpy.linalg as la
        bone = self.human.getBaseSkeleton().getBone(COMPARE_BONE)
        scale_factor = float(bone.length) / self.bvh_bone_length
        trans = scale_factor * self.bvh_root_translation
        log.message("Scaling animation %s with factor %s" % (anim.name, scale_factor))
        # It's possible to use anim.scale() as well, but by repeated scaling we accumulate error
        # It's easier to simply set the translation, as poses only have a translation on
        # root joint

        # Set pose root bone translation
        root_bone_idx = 0
        posedata = anim.getAtFramePos(0, noBake=True)
        posedata[root_bone_idx, :3, 3] = trans
        anim.resetBaked()

    def onShow(self, event):
        self.filechooser.refresh()
        self.filechooser.selectItem(self.currentPose)
        self.human.refreshPose()

    def onHide(self, event):
        gui3d.app.statusPersist('')

    def onHumanChanging(self, event):
        if event.change == 'reset':
            self.human.removeAnimations(update=False)  # TODO the human object now also does this, so not strictly needed
            self.currentPose = None

    def onHumanChanged(self, event):
        if event.change == 'skeleton':
            # TODO still needed?
            if self.currentPose:
                self.loadPose(self.currentPose, apply_pose=False)
        elif event.change in ['modifier', 'targets']:
            # TODO do we need to react on 'targets' event as well?
            anim = self.human.getActiveAnimation()
            if anim:
                self.autoScaleAnim(anim)
        elif event.change == 'reset':
            # Update GUI after reset (if tab is currently visible)
            if self.isShown():
                self.onShow(event)

    def loadHandler(self, human, values, strict):
        if values[0] == "pose":
            poseFile = values[1]
            poseFile = getpath.thoroughFindFile(poseFile, self.paths)
            if not os.path.isfile(poseFile):
                if strict:
                    raise RuntimeError("Could not load pose %s, file does not exist." % poseFile)
                log.warning("Could not load pose %s, file does not exist.", poseFile)
            else:
                self.loadPose(poseFile)
            return

    def saveHandler(self, human, file):
        if self.currentPose:
            poseFile = getpath.getRelativePath(self.currentPose, self.paths)
            file.write('pose %s\n' % poseFile)


category = None
taskview = None

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    global taskview
    category = app.getCategory('Pose/Animate')
    taskview = PoseLibraryTaskView(category)
    taskview.sortOrder = 2
    category.addTask(taskview)

    app.addLoadHandler('pose', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler, priority=6) # After skeleton library


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    taskview.onUnload()
