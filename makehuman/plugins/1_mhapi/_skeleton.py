#!/usr/bin/python

from .namespace import NameSpace

import getpath
import bvh
import json
import animation

from collections import OrderedDict

class Skeleton(NameSpace):
    """This namespace wraps call which work with skeleton, rig, poses and expressions."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()
        self.human = self.api.internals.getHuman()

    def getSkeleton(self):
        """Get the current skeleton, or None if no skeleton is assigned"""
        return self.human.getSkeleton()

    def getBaseSkeleton(self):
        """Get the internal default skeleton, which is independent on selected rig"""
        return self.human.getBaseSkeleton()

    def getPoseAsBoneDict(self):
        """Return a dict containing all bone rotations"""
        skeleton = self.getSkeleton()
        if skeleton is None:
            # No rig is set
            return None
        return None

    def getPoseAsBVH(self):
        """Return a BVH object describing the current pose"""
        skeleton = self.getSkeleton()
        if skeleton is None:
            # No rig is set
            return None
        b = BVH()
        b.fromSkeleton(skeleton)

        return b

    def getPoseAsAnimation(self):
        return self.human.getActiveAnimation()
 
    def clearPoseAndExpression(self):
        """Put skeleton back into rest pose"""
        human.resetToRestPose()
        human.removeAnimations()

    def setPoseFromFile(self, bvh_file_name):
        """Set the pose from a BVH file"""
        skeleton = self.getSkeleton()
        pass

    def setExpressionFromFile(self, mhposeFile):
        """Set the expression from a mhpose file"""

        if mhposeFile is None:
            # clear expression

            original_pose = self.getPoseAsAnimation()
            if original_pose and hasattr(original_pose, 'pose_backref'):
                original_pose = original_pose.pose_backref
    
            if original_pose is None:
                self.human.setActiveAnimation(None)
            else:
                if self.human.hasAnimation(original_pose.name):
                    self.human.setActiveAnimation(original_pose.name)
                else:
                    self.human.addAnimation(original_pose)
                    self.human.setActiveAnimation(orgiginal_pose.name)
    
            if self.human.hasAnimation('expr-lib-pose'):
                self.human.removeAnimation('expr-lib-pose')
        else:
            # Assign expression
            
            base_bvh = bvh.load(getpath.getSysDataPath('poseunits/face-poseunits.bvh'), allowTranslation="none")
            base_anim = base_bvh.createAnimationTrack(self.human.getBaseSkeleton(), name="Expression-Face-PoseUnits")

            poseunit_json = json.load(open(getpath.getSysDataPath('poseunits/face-poseunits.json'), 'r', encoding='utf-8'), object_pairs_hook=OrderedDict)
            poseunit_names = poseunit_json['framemapping']

            base_anim = animation.PoseUnit(base_anim.name, base_anim._data, poseunit_names)

            face_bone_idxs = sorted(list(set([bIdx for l in base_anim.getAffectedBones() for bIdx in l])))

            new_pose = animation.poseFromUnitPose('expr-lib-pose', mhposeFile, base_anim)

            current_pose = self.getPoseAsAnimation()

            if current_pose is None:
                current_pose = new_pose
                current_pose.pose_backref = None
            else:
                if hasattr(current_pose,'pose_backref') and not current_pose.pose_backref is None:
                    current_pose = current_pose.pose_backref
                org_pose = current_pose
                current_pose = animation.mixPoses(org_pose, new_pose, face_bone_idxs)

            current_pose.name = 'expr-lib-pose'
            self.human.addAnimation(current_pose)
            self.human.setActiveAnimation(current_pose.name)
            self.human.setPosed(True)
            self.human.refreshPose()

    def _loadBvh(self, bvh_file_name):
        pass

    def _createAnimationTrack(self, skeleton):
        pass

    def _calculateBVHBoneLength(self):
        pass

