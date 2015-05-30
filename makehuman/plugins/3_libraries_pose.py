#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2015

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
import getpath
import filecache

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

        self.paths = [mh.getDataPath('poses'), mh.getSysDataPath('poses')]

        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.paths, ['bvh'], 'thumb', mh.getSysDataPath('poses/notfound.thumb'), name='Pose', noneItem=True))
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
        from codecs import open
        f = open(filename, encoding='utf-8')
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
            return

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
        return animation.loadPoseFromMhpFile(filepath, self.human.getBaseSkeleton())

    def loadBvh(self, filepath, convertFromZUp="auto"):
        bvh_file = bvh.load(filepath, convertFromZUp)
        self.autoScaleBVH(bvh_file)  # TODO scaling once is probably not enough, every time the height of the human changes significantly the animation needs to be rescaled
        anim = bvh_file.createAnimationTrack(self.human.getBaseSkeleton())
        _, _, _, license = self.getMetadata(filepath)
        anim.license = license
        return anim

    def autoScaleBVH(self, bvh_file):
        """
        Auto scale BVH translations by comparing upper leg length
        """
        import numpy.linalg as la
        COMPARE_BONE = "upperleg02.L"
        if COMPARE_BONE not in bvh_file.joints:
            raise RuntimeError('Failed to auto scale BVH file %s, it does not contain a joint for "%s"' % (bvh_file.name, COMPARE_BONE))
        bvh_joint = bvh_file.joints[COMPARE_BONE]
        bone = self.human.getBaseSkeleton().getBoneByReference(COMPARE_BONE)
        if bone is not None:
            joint_length = la.norm(bvh_joint.children[0].position - bvh_joint.position)
            scale_factor = bone.length / joint_length
            log.message("Scaling BVH file %s with factor %s" % (bvh_file.name, scale_factor))
            bvh_file.scale(scale_factor)
        else:
            log.warning("Could not find bone or bone reference with name %s in skeleton %s, cannot auto resize BVH file %s", COMPARE_BONE, self.human.getBaseSkeleton().name, bvh_file.name)

    def onShow(self, event):
        self.filechooser.refresh()
        self.filechooser.selectItem(self.currentPose)
        self.human.refreshPose()

    def onHide(self, event):
        gui3d.app.statusPersist('')

    def onHumanChanging(self, event):
        if event.change == 'reset':
            self.human.removeAnimations(update=False)
            self.currentPose = None

    def onHumanChanged(self, event):
        if event.change == 'skeleton':
            if self.currentPose:
                self.loadPose(self.currentPose, apply_pose=False)
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
