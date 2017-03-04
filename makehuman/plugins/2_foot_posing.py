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

This plugin enables the feature of foot poses automatically adapting to the
type of shoes chosen for the model. There is no visible user interface for
this plugin and it acts completely automatically, based on the foot_pose
property set in the "special_pose foot" property of the clothes proxy.
"""
import os

from core import G
import events3d
import bvh
import getpath
import animation
import log

FOOT_BONES = ['foot', 'toe1-1', 'toe1-2', 'toe2-1', 'toe2-2', 'toe2-3', 'toe3-1', 'toe3-2', 'toe3-3', 'toe4-1',
              'toe4-2', 'toe4-3', 'toe5-1', 'toe5-2', 'toe5-3']
FOOT_BONES = [n + ".L" for n in FOOT_BONES] + [n + ".R" for n in FOOT_BONES]

class FootPoseAdapter(events3d.EventHandler):
    def __init__(self):
        super(FootPoseAdapter, self).__init__()
        self.human = G.app.selectedHuman
        self.selectedFile = None
        self.selectedPose = None

        self._setting_pose = False

        self.sysDataPath = getpath.getSysDataPath('special_poses/foot')
        self.userPath = getpath.getDataPath('special_poses/foot')
        self.paths = [self.userPath, self.sysDataPath]
        if not os.path.exists(self.userPath):
            os.makedirs(self.userPath)

        skel = self.human.getBaseSkeleton()
        self.affected_bone_idxs = [skel.getBone(bone_name).index for bone_name in FOOT_BONES]

    def _get_current_pose(self):
        return self.human.getActiveAnimation()

    def _get_current_unmodified_pose(self):
        pose = self._get_current_pose()
        if pose and hasattr(pose, 'pose_foot_backref'):
            return pose.pose_foot_backref
        return pose

    def applyToPose(self, pose):
        self._setting_pose = True

        if self._get_current_pose() is None:
            # No pose set, simply set this one
            pose_ = pose
            pose_.pose_foot_backref = None
        else:
            # If the current pose was already modified by foot pose library, use the original one
            org_pose = self._get_current_unmodified_pose()
            pose_ = animation.mixPoses(org_pose, pose, self.affected_bone_idxs)
            pose_.pose_foot_backref = org_pose

        pose_.name = 'special-foot-pose'
        self.human.addAnimation(pose_)
        self.human.setActiveAnimation('special-foot-pose')

        self.human.setPosed(True)
        self.human.refreshPose()

        self._setting_pose = False

    def loadFootPose(self, filename):
        log.debug("Loading special foot pose from %s", filename)
        self.selectedFile = filename
        if not filename:
            # Unload current pose
            self.selectedFile = None
            self.selectedPose = None
            # Remove the special pose from existing pose by restoring the original
            org_pose = self._get_current_unmodified_pose()
            if org_pose is None:
                self.human.setActiveAnimation(None)
            elif self.human.hasAnimation(org_pose.name):
                self.human.setActiveAnimation(org_pose.name)
            else:
                self.human.addAnimation(org_pose)
                self.human.setActiveAnimation(org_pose.name)

            # Remove pose reserved for foot pose library from human
            if self.human.hasAnimation('special-foot-pose'):
                self.human.removeAnimation('special-foot-pose')
            self.human.refreshPose(updateIfInRest=True)
            return

        # Load pose
        bvh_file = bvh.load(filename, convertFromZUp="auto")
        anim = bvh_file.createAnimationTrack(self.human.getBaseSkeleton())
        self.applyFootPose(anim)

    def applyFootPose(self, anim):
        self.selectedPose = anim
        if anim is None:
            self.selectedFile = None

        # Assign to human
        if anim:
            self.applyToPose(self.selectedPose)  # TODO override or add?
        self.human.refreshPose()

    def onHumanChanging(self, event):
        if event.change == 'reset':
            self._setting_pose = True
            self.selectedFile = None
            self.selectedPose = None

    def onHumanChanged(self, event):
        if event.change == 'proxyChange':
            if event.proxy != 'clothes':
                return
            proxy = event.proxy_obj
            if not proxy:
                return
            foot_pose = proxy.special_pose.get("foot", None)
            if not foot_pose:
                return
            filename = getpath.thoroughFindFile(foot_pose, self.paths)
            if not os.path.isfile(filename):
                log.error("Could not find a file for special_pose foot %s, file does not exist.", filename)
                return
            if event.action == 'add':
                self.loadFootPose(filename)
            elif event.action == 'remove':
                if self.selectedFile and getpath.isSamePath(filename, self.selectedFile):
                    self.loadFootPose(None)

        if event.change == 'poseChange' and not self._setting_pose:
            if self.selectedPose:
                self.applyFootPose(self.selectedPose)
        if event.change == 'reset':
            # Update GUI after reset (if tab is currently visible)
            self._setting_pose = False
            self.loadFootPose(None)


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements

def load(app):
    eventhandler = FootPoseAdapter()
    app.addEventHandler(eventhandler, 4310) # After pose and expression


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements

def unload(app):
    pass
