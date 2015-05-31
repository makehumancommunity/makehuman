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

# TODO viseme poses can simply be added to this library and assigned a 'visemes' tag

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
        self.extension = 'mhupb'  # MH unit-pose blend (preliminary name)
        filecache.MetadataCacher.__init__(self, self.extension, 'expression_filecache.mhc')

        self.human = gui3d.app.selectedHuman
        self.selectedFile = None
        self.selectedPose = None

        self.base_bvh = None
        self.base_anim = None

        self.sysDataPath = getpath.getSysDataPath('expressions')
        self.userPath = getpath.getSysDataPath('expressions')
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

        self.base_anim = animation.PoseUnit(self.base_anim.name, self.base_anim._data, self.poseunit_names)
        log.message('unit pose frame count:%s', len(self.poseunit_names))

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        self.filechooser.refresh()
        self.filechooser.selectItem(self.selectedFile)

        if self.base_bvh is None:
            self._load_pose_units()

        if gui3d.app.getSetting('cameraAutoZoom'):
            gui3d.app.setFaceCamera()

    def applyToPose(self, pose):
        self.human.addAnimation(pose)
        self.human.setActiveAnimation(pose.name)

        # TODO if old pose still set on human, remove it ('expr-lib-pose')

        # TODO blend with current pose on human
        '''
        if self.human.getActiveAnimation() is None:
            # No pose set, simply set this one
            self.human.addAnimation(pose)
            self.human.setActiveAnimation(pose.name)
        else:
            pose_ = self.human.getAnimation(self.human.getActiveAnimation())
            pose_.override(pose)
        '''

        self.human.setPosed(True)
        self.human.refreshPose()
        # TODO fix interaction when another pose is set, implement onHumanChanging handler

    def chooseExpression(self, filename):
        log.debug("Loading expression from %s", filename)
        self.selectedFile = filename

        if not filename:
            # Unload current expression
            self.selectedPose = None
            # TODO remove the expression from existing pose
            self.filechooser.selectItem(None)
            self.human.setActiveAnimation(None)
            self.human.refreshPose()
            return

        # Assign to human
        pose = animation.poseFromUnitPose('expr-lib-pose', filename, self.base_anim)
        self.applyToPose(pose)

        self.filechooser.selectItem(filename)

    def getMetadataImpl(self, filename):
        import json
        mhupb = json.load(open(filename, 'rb'))
        name = mhupb['name']
        description = mhupb.get('description', '')
        tags = set([t.lower() for t in mhupb.get('tags', [])])
        return (tags, name, description)

    def getTagsFromMetadata(self, metadata):
        tags = metadata[0]
        return tags

    def getSearchPaths(self):
        return self.paths

    def onHumanChanging(self, event):
        if event.change not in ['expression', 'material']:
            pass  # TODO

    def onHumanChanged(self, event):
        # TODO
        pass

    def loadHandler(self, human, values, strict):
        if values[0] == 'status':
            return

        if values[0] == 'expression' and len(values) > 1:
            if self.base_bvh is None:
                self._load_pose_units()
            # TODO catch error when expression does not exist
            # TODO

    def saveHandler(self, human, file):
        pass


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
    app.addSaveHandler(taskview.saveHandler)


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements

def unload(app):
    taskview.onUnload()
