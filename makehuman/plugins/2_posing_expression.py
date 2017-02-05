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

Library for facial expression poses, these poses are set as rest pose and override
the orientation of the face bones of the human's base skeleton over the orientations
set by the (body) pose.
"""

import os
import json

import gui3d
import bvh
import getpath
import animation
import log
import filecache
import filechooser as fc


class ExpressionAction(gui3d.Action):
    def __init__(self, msg, before, filename, taskView):
        super(ExpressionAction, self).__init__(msg)
        self.filename = filename
        self.taskView = taskView
        self.before = before

    def do(self):
        self.taskView.chooseExpression(self.filename)
        return True

    def undo(self):
        self.taskView.chooseExpression(self.before)
        return True


class ExpressionTaskView(gui3d.TaskView, filecache.MetadataCacher):
    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Expressions')
        self.extension = 'mhpose'
        filecache.MetadataCacher.__init__(self, self.extension, 'expression_filecache.mhc')

        self.human = gui3d.app.selectedHuman
        self.selectedFile = None
        self.selectedPose = None
        self.face_bone_idxs = None

        self.base_bvh = None
        self.base_anim = None

        self._setting_pose = False

        self.sysDataPath = getpath.getSysDataPath('expressions')
        self.userPath = getpath.getDataPath('expressions')
        self.paths = [self.userPath, self.sysDataPath]
        if not os.path.exists(self.userPath):
            os.makedirs(self.userPath)

        self.filechooser = self.addRightWidget(fc.IconListFileChooser( \
                                                    self.paths,
                                                    self.extension,
                                                    'thumb',
                                                    name='Expression',
                                                    notFoundImage = getpath.getSysDataPath('notfound.thumb'),
                                                    noneItem = True,
                                                    doNotRecurse = True))
        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(False)

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            if filename:
                msg = 'Load expression'
            else:
                msg = "Clear expression"
            gui3d.app.do(ExpressionAction(msg, self.selectedFile, filename, self))

        self.filechooser.setFileLoadHandler(fc.TaggedFileLoader(self))
        self.addLeftWidget(self.filechooser.createTagFilter())

    def _load_pose_units(self):
        from collections import OrderedDict
        self.base_bvh = bvh.load(getpath.getSysDataPath('poseunits/face-poseunits.bvh'), allowTranslation="none")
        self.base_anim = self.base_bvh.createAnimationTrack(self.human.getBaseSkeleton(), name="Expression-Face-PoseUnits")

        poseunit_json = json.load(open(getpath.getSysDataPath('poseunits/face-poseunits.json'),'rb'), object_pairs_hook=OrderedDict)
        self.poseunit_names = poseunit_json['framemapping']

        if len(self.poseunit_names) != self.base_bvh.frameCount:
            self.base_anim = None
            raise RuntimeError("Face units BVH has wrong number of frames (%s) while face-poseunits.json defines %s poses, they should be equal." % (self.base_bvh.frameCount, len(self.poseunit_names)))
        self.base_anim = animation.PoseUnit(self.base_anim.name, self.base_anim._data, self.poseunit_names)
        log.message('unit pose frame count:%s', len(self.poseunit_names))

        # Store indexes of all bones affected by face unit poses, should be all face bones
        self.face_bone_idxs = sorted(list(set([bIdx for l in self.base_anim.getAffectedBones() for bIdx in l])))

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        self.filechooser.refresh()
        self.filechooser.selectItem(self.selectedFile)

        if self.base_bvh is None:
            self._load_pose_units()

        if gui3d.app.getSetting('cameraAutoZoom'):
            gui3d.app.setFaceCamera()

    def _get_current_pose(self):
        return self.human.getActiveAnimation()

    def _get_current_unmodified_pose(self):
        pose = self._get_current_pose()
        if pose and hasattr(pose, 'pose_backref'):
            return pose.pose_backref
        return pose

    def applyToPose(self, pose):
        if self.base_bvh is None:
            self._load_pose_units()
        self._setting_pose = True

        if self._get_current_pose() is None:
            # No pose set, simply set this one
            pose_ = pose
            pose_.pose_backref = None
        else:
            # If the current pose was already modified by expression library, use the original one
            org_pose = self._get_current_unmodified_pose()
            if org_pose is None:
                org_pose = self._get_current_pose()
            pose_ = animation.mixPoses(org_pose, pose, self.face_bone_idxs)
            pose_.pose_backref = org_pose

        pose_.name = 'expr-lib-pose'
        self.human.addAnimation(pose_)
        self.human.setActiveAnimation('expr-lib-pose')

        self.human.setPosed(True)
        self.human.refreshPose()

        self._setting_pose = False

    def chooseExpression(self, filename):
        log.debug("Loading expression from %s", filename)
        self.selectedFile = filename

        if not filename:
            # Unload current expression
            self.selectedPose = None
            # Remove the expression from existing pose by restoring the original
            org_pose = self._get_current_unmodified_pose()
            if org_pose is None:
                self.human.setActiveAnimation(None)
            elif self.human.hasAnimation(org_pose.name):
                self.human.setActiveAnimation(org_pose.name)
            else:
                self.human.addAnimation(org_pose)
                self.human.setActiveAnimation(org_pose.name)

            # Remove pose reserved for expression library from human
            if self.human.hasAnimation('expr-lib-pose'):
                self.human.removeAnimation('expr-lib-pose')
            self.filechooser.selectItem(None)
            self.human.refreshPose(updateIfInRest=True)
            return

        # Assign to human
        self.selectedPose = animation.poseFromUnitPose('expr-lib-pose', filename, self.base_anim)
        self.applyToPose(self.selectedPose)
        self.human.refreshPose()

        self.filechooser.selectItem(filename)

    def getMetadataImpl(self, filename):
        import json
        posedata = json.load(open(filename, 'rb'))
        name = posedata['name']
        description = posedata.get('description', '')
        tags = set([t.lower() for t in posedata.get('tags', [])])
        return (tags, name, description)

    def getTagsFromMetadata(self, metadata):
        tags = metadata[0]
        return tags

    def getSearchPaths(self):
        return self.paths

    def onHumanChanging(self, event):
        if event.change == 'reset':
            self._setting_pose = True
            self.selectedFile = None
            self.selectedPose = None

    def onHumanChanged(self, event):
        if event.change == 'poseChange' and not self._setting_pose:
            if self.selectedPose:
                self.applyToPose(self.selectedPose)
        if event.change == 'reset':
            # Update GUI after reset (if tab is currently visible)
            if self.isShown():
                self.onShow(event)
            self._setting_pose = False
            self.chooseExpression(None)

    def loadHandler(self, human, values, strict):
        if values[0] == 'status':
            return

        if values[0] == 'expression' and len(values) > 1:
            if self.base_bvh is None:
                self._load_pose_units()
            poseFile = values[1]
            poseFile = getpath.thoroughFindFile(poseFile, self.paths)
            if not os.path.isfile(poseFile):
                if strict:
                    raise RuntimeError("Could not load expression pose %s, file does not exist." % poseFile)
                log.warning("Could not load expression pose %s, file does not exist.", poseFile)
            else:
                self.chooseExpression(poseFile)
            return

    def saveHandler(self, human, file):
        if self.selectedFile:
            poseFile = getpath.getRelativePath(self.selectedFile, self.paths)
            file.write('expression %s\n' % poseFile)


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements

taskview = None
def load(app):
    global taskview
    category = app.getCategory('Pose/Animate')
    taskview = ExpressionTaskView(category)
    taskview.sortOrder = 4
    category.addTask(taskview)

    app.addLoadHandler('expression', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler, priority=8) # After pose library (even though it does not really matter)


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements

def unload(app):
    taskview.onUnload()
