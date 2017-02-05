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

Data handlers for skeletal animation.
"""

# TODO perhaps do not adapt camera to posed position, always use rest coordinates

import math
import numpy as np
import log
import makehuman


INTERPOLATION = {
    'NONE'  : 0,
    'LINEAR': 1,
    'LOG':    2
}

# TODO allow saving AnimationTrack to binary file
# TODO allow saving VertexBoneWeights to binary file

class AnimationTrack(object):
    """Baseclass for all animations and poses that can be applied to a
    MakeHuman (base) skeleton."""

    # TODO it might be a good idea to store the bone names in the animationtrack (eg in bvh.createAnimationTrack), or at least store the name of the skeleton it was created for

    def __init__(self, name, poseData, nFrames, framerate):
        """
        Create a skeletal animation track with specified name from given pose
        data. An animation track usually represents one discrete animation.

        poseData    np.array((n,4,4), dtype=np.float32)
            as a list of 4x4 pose matrices or 3x4 (the final row is always 0 0 0 1 anyway)
            with n = nBones*nFrames
            pose matrices should be ordered per frame - per bone
            eg: poseData = [ B0F0, B1F0, B2F0, B0F1, B1F1, B2F1]
                with each BxFy a 4x4 or 3x4 pose matrix for one bone in one frame
                with x the bone index, and y the frame index
            Bones should always appear in the same order and are usually
            ordered in breadth-first fashion.
        """
        self.name = name
        self.description = "%s animation" % name
        self.license = makehuman.getAssetLicense()
        self.dataLen = len(poseData)
        self.nFrames = nFrames
        self.nBones = int(self.dataLen/nFrames)

        if self.nBones == 0:
            raise RuntimeError("Cannot create AnimationTrack %s: contains no or not enough data." % self.name)
        if self.nBones*self.nFrames != self.dataLen:
            raise RuntimeError("Cannot create AnimationTrack %s: The specified pose data does not have the proper length. Is %s, expected %s (nBones*nFrames)." % (self.name, self.dataLen, self.nBones*self.nFrames))
        if not (poseData.shape == (self.dataLen, 3, 4) or poseData.shape == (self.dataLen, 4, 4)):
            raise RuntimeError("Cannot create AnimationTrack %s: The specified pose data does not have the proper dimensions. Is %s, expected (%s, 4, 4) or (%s, 3, 4)" % (self.name, poseData.shape, self.dataLen, self.dataLen))

        self._data = poseData[:self.dataLen,:3,:4]  # We do not store the last row to save memory
        self.frameRate = float(framerate)      # Numer of frames per second
        self.loop = True

        self._data_baked = None
        
        # Type of interpolation between animation frames
        #   0  no interpolation
        #   1  linear
        #   2  logarithmic   # TODO!
        self.interpolationType = 0

        self.disableBaking = False  # Set to true to avoid animation being baked

    @property
    def data(self):
        if self.isBaked():
            return self._data_baked
        else:
            return self._data

    def isBaked(self):
        if self.disableBaking:
            return False
        return self._data_baked is not None

    def resetBaked(self):
        self._data_baked = None

    def bake(self, skel):
        """
        Bake animation as skinning matrices for the specified skeleton.
        Results in significant performance gain when skinning.
        We do skinning with 3x4 matrixes, as suggested in http://graphics.ucsd.edu/courses/cse169_w05/2-Skeleton.htm
        Section 2.3 (We assume the 4th row contains [0 0 0 1])
        """
        if self.disableBaking:
            return

        from progress import Progress

        log.debug('Updating baked animation %s (%s frames)', self.name, self.nFrames)
        progress = Progress(self.nFrames)

        bones = skel.getBones()
        if len(bones) != self.nBones:
            raise RuntimeError("Error baking animation %s: number of bones in animation data differs from bone count of skeleton %s" % (self.name, skel.name))

        old_pose = skel.getPose()
        self._data_baked = np.zeros((self.dataLen, 3, 4))

        for f_idx in xrange(self.nFrames):
            i = f_idx * self.nBones
            skel.setPose(self._data[i:i+self.nBones])
            for b_idx in xrange(self.nBones):
                idx = i + b_idx
                self._data_baked[idx,:,:] = bones[b_idx].matPoseVerts[:3,:4]
            progress.step("Baking animation frame %s", f_idx+1)

        skel.setPose(old_pose)

    def scale(self, scale):
        """
        Scale the animation with the specified scale.
        This means scaling the transformation portion of this animation.
        """
        for f_idx in xrange(self.nFrames):
            frameData = self.getAtFramePos(f_idx, noBake=True)
            frameData[:,:3,3] *= scale
            self.resetBaked()

    def isPose(self):
        """
        Returns true if this animationtrack is a pose,
        meaning that it contains only one frame.
        """
        return self.nFrames == 1

    def getAtTime(self, time, noBake=False):
        """
        Returns the animation state at the specified time.
        When time is between two stored frames the animation values will be
        interpolated.

        If noBake is True will always return the original non-baked data.
        Else, if baked data is available, it will be used, and will fall back
        to non-baked animation data otherwise.
        """
        if noBake:
            data = self._data
        else:
            data = self.data

        frameIdx, fraction = self.getFrameIndexAtTime(time)
        if fraction == 0 or self.interpolationType == 0:
            # Discrete animation
            idx = frameIdx*self.nBones
            return data[idx:idx+self.nBones]
        elif self.interpolationType == 1:
            # Linear interpolation
            idx1 = frameIdx*self.nBones
            idx2 = ((frameIdx+1) % self.nFrames) * self.nBones
            return data[idx1:idx1+self.nBones] * (1-fraction) + \
                   data[idx2:idx2+self.nBones] * fraction
        elif self.interpolationType == 2:
            # Logarithmic interpolation
            pass # TODO

    def getAtFramePos(self, frame, noBake=False):
        """
        If noBake is True will always return the original non-baked data.
        Else, if baked data is available, it will be used, and will fall back
        to non-baked animation data otherwise.
        """
        frame = int(frame)
        if noBake:
            return self._data[frame*self.nBones:(frame+1)*self.nBones]
        return self.data[frame*self.nBones:(frame+1)*self.nBones]

    def getFrameIndexAtTime(self, time):
        """
        Time should be in seconds (float).
        Returns     (frameIdx, fraction)
        With fraction a number between 0 and 1 (exclusive) indicating the
        fraction of progression towards the next frame. A fraction of 0 means
        position at an exact frame.
        """
        frameIdx = float(self.frameRate) * time
        fraction, frameIdx = math.modf(frameIdx)

        if self.loop:
            # Loop from beginning
            frameIdx = frameIdx % self.nFrames
        elif frameIdx >= self.nFrames:
            # Stop at last frame
            frameIdx = self.nFrames-1
            fraction = 0

        return int(frameIdx), float(fraction)

    def isLooping(self):
        return self.loop

    def setLooping(self, enabled):
        self.looping = enabled

    def getPlaytime(self):
        """
        Playtime (duration) of animation in seconds.
        """
        return float(self.nFrames)/self.frameRate

    def sparsify(self, newFrameRate):
        if newFrameRate > self.frameRate:
            raise RuntimeError("Cannot sparsify animation: new framerate %s is higher than old framerate %s." % (newFrameRate, self.frameRate))

        # Number of frames to drop
        dropFrames = int(float(self.frameRate)/float(newFrameRate))
        if dropFrames <= 0:
            return
        indxs = []
        count = 0
        for frameI in range(0,self.dataLen,self.nBones):
            if count == 0:
                indxs.extend(range(frameI,frameI+self.nBones))
            count = (count + 1) % dropFrames
        data = self.data[indxs]
        self.data = data
        self.frameRate = newFrameRate
        self.dataLen = len(self.data)
        self.nFrames = self.dataLen/self.nBones

class Pose(AnimationTrack):
    """
    A pose is an animation track with only one frame, and is not affected by
    playback time.

    It's possible to convert a frame from an animation to a pose using:
        Pose(anim.name, anim.getAtTime(t))
    or
        Pose(anim.name, anim.getAtFramePos(i))
    """

    def __init__(self, name, poseData):
        super(Pose, self).__init__(name, poseData, nFrames=1, framerate=1)

    def sparsify(self, newFrameRate):
        raise NotImplementedError("sparsify() does not exist for poses")

    def getData(self):
        """
        Structured pose data
        """
        return self.getAtFramePos(0)

    def fromPoseUnit(self, filename, poseUnit):
        """
        Parse a .mhupb file and construct a pose by blending the
        weighted sum of unit poses as specified in the mhupb file.
        :param filename: path to .mhupb file that defines which unit poses to blend
        :param poseUnit: a PoseUnit containing all unit poses referenced by the .mhupb file
        """
        from collections import OrderedDict
        import json
        mhupb = json.load(open(filename, 'rb'), object_pairs_hook=OrderedDict)
        self.name = mhupb['name']
        self.description = mhupb.get('description', '')
        self.tags = set([t.lower() for t in mhupb.get('tags', [])])
        self.license.fromJson(mhupb)
        self.unitposes = mhupb['unit_poses']  # Expected to be a dict with posename: weight pairs
        if len(self.unitposes) == 0:
            raise RuntimeError("Cannot load pose: unit_poses dict needs to contain at least one entry")

        self._data = poseUnit.getBlendedPose(self.unitposes.keys(), self.unitposes.values(), only_data=True)
        self.dataLen = len(self._data)
        self.nFrames = 1
        self.nBones = self.dataLen

        return self

class PoseUnit(AnimationTrack):
    """
    A poseunit is an animation track where each frame contains a named unit pose.
    These poses can be blended together with a certain weight to form a new
    composite pose.
    """

    # TODO allow selectively applying poses, eg only on face bones >> could be achieved by an extra blend with another pose
    # TODO track for each frame which bones are effectively posed

    def __init__(self, name, poseData, poseNames):
        super(PoseUnit, self).__init__(name, poseData, nFrames=len(poseNames), framerate=1)
        self._poseNames = poseNames

        self._affectedBones = None  # Stores for every frame which bones (index) are posed

    def sparsify(self, newFrameRate):
        raise NotImplementedError("sparsify() does not exist for poseunits")

    def getPoseNames(self):
        return self._poseNames

    def getUnitPose(self, name):
        if isinstance(name, basestring):
            frame_idx = self._poseNames.index(name)
        else:
            frame_idx = name
        return self.getAtFramePos(frame_idx)

    def getAffectedBones(self, frame_idx=None):
        """
        Return the (breadth-first) indices of the bones affected in the frame
        with specified frame number. Specify no frame number to get a list for
        all frames.
        """
        if self._affectedBones is None:
            self._cacheAffectedBones()
        if frame_idx is None:
            return self._affectedBones
        else:
            return self._affectedBones[frame_idx]

    def _cacheAffectedBones(self):
        self._affectedBones = []

        for f_idx in xrange(self.nFrames):
            frameData = self.getAtFramePos(f_idx)
            self._affectedBones.append( [] )
            for b_idx in xrange(self.nBones):
                if not isRest(frameData[b_idx]):
                    self._affectedBones[f_idx].append(b_idx)

    def getBlendedPose(self, poses, weights, additiveBlending=True, only_data=False):
        """Create a new pose by blending multiple poses together with a specified
        weight.
        poses is expected to be a list of poseunit (frame) names
        weights is expected to be a list of float values between 0 and 1
        """
        import transformations as tm

        REST_QUAT = np.asarray([1,0,0,0], dtype=np.float32)

        if isinstance(poses[0], basestring):
            f_idxs = [self.getPoseNames().index(pname) for pname in poses]
        else:
            f_idxs = poses

        if not additiveBlending:
            # normalize weights
            if not isinstance(weights, np.ndarray):
                weights = np.asarray(weights, dtype=np.float32)
            t = sum(weights)
            if t < 1:
                # Fill up rest with neutral pose (neutral pose is assumed to be first frame)
                weights = np.asarray(weights + [1.0-t], dtype=np.float32)
                f_idxs.append(0)
            weights /= t

        #print zip([self.getPoseNames()[_f] for _f in f_idxs],weights)

        result = emptyPose(self.nBones)
        m = np.identity(4, dtype=np.float32)
        m1 = np.identity(4, dtype=np.float32)
        m2 = np.identity(4, dtype=np.float32)

        if len(f_idxs) == 1:
            for b_idx in xrange(self.nBones):
                m[:3, :4] = self.getAtFramePos(f_idxs[0], True)[b_idx]
                q = tm.quaternion_slerp(REST_QUAT, tm.quaternion_from_matrix(m, True), float(weights[0]))
                result[b_idx] = tm.quaternion_matrix( q )[:3,:4]
        else:
            for b_idx in xrange(self.nBones):
                m1[:3, :4] = self.getAtFramePos(f_idxs[0], True)[b_idx]
                m2[:3, :4] = self.getAtFramePos(f_idxs[1], True)[b_idx]
                q1 = tm.quaternion_slerp(REST_QUAT, tm.quaternion_from_matrix(m1, True), float(weights[0]))
                q2 = tm.quaternion_slerp(REST_QUAT, tm.quaternion_from_matrix(m2, True), float(weights[1]))
                quat = tm.quaternion_multiply(q2, q1)

                for i,f_idx in enumerate(f_idxs[2:]):
                    i += 2
                    m[:3, :4] = self.getAtFramePos(f_idx, True)[b_idx]
                    q = tm.quaternion_slerp(REST_QUAT, tm.quaternion_from_matrix(m, True), float(weights[i]))
                    quat = tm.quaternion_multiply(q, quat)

                result[b_idx] = tm.quaternion_matrix( quat )[:3,:4]

        if only_data:
            return result
        return Pose(self.name+'-blended', result)

def poseFromUnitPose(name, filename, poseUnit):
    """
    Parse a .mhupb file and construct a pose by blending the
    weighted sum of unit poses as specified in the mhupb file.
    :param name:     The name to assign to the created pose
    :param filename: path to .mhupb file that defines which unit poses to blend
    :param poseUnit: a PoseUnit containing all unit poses referenced by the .mhupb file
    :return: a Pose object that contains the end result of blending the unit poses together
    """
    return Pose(name, emptyPose()).fromPoseUnit(filename, poseUnit)

def blendPoses(poses, weights):
    """
    Blend multiple poses (or pose data constructed from an animation frame).
    """
    if len(weights) < 1:
        return None

    if len(weights) == 1:
        return poses[0].getData()

    poseData = weights[0] * poses[0]
    for pIdx, pose in poses[1:]:
        w = weights[pIdx]
        poseData += w * pose    # TODO does not work as it adds a scale transformation too

    return poseData

def mixPoses(pose1, pose2, bonesList):
    """
    Combine two poses into one by taking pose1 and replacing
    the orientations of the bones in bonesList with the orientations
    of pose 2. bonesList is a list of bone indices (integers) that
    should be replaced in pose1 with the orientations in pose2
    Returns a new Pose object and does not modify the original
    poses.
    We assume that pose1 and pose2 are created for the same
    skeleton, meaning that they contain motions for the same
    bones.
    If pose1 or pose2 is an animation, its first frame will be
    used.
    """
    if pose1.nBones != pose2.nBones:
        raise RuntimeError("Pose %s and %s are not compatible and cannot be mixed: they are for different skeletons and do not contain the same number of bones (%s and %s)." % (pose1.name, pose2.name, pose1.nBones, pose2.nBones))
    data = pose1.getAtFramePos(0, noBake=True).copy()
    data[bonesList] = pose2.getAtFramePos(0, noBake=True)[[bonesList]]
    return Pose(pose1.name+"_mix_"+pose2.name, data)

def joinAnimations(anim1, anim2):
    """
    Create a new animation by appending anim2 at the end of anim1.
    Missing channels get filled with identity matrices.
    Data such as framerate is taken from the first animation, the framerate of
    both animations is expected to be identical.
    """
    if anim1.nBones != anim2.nBones:
        raise RuntimeError("Cannot join animations %s and %s, they don't have the same bone count." % (anim1.nBones, anim2.nBones))
    if anim1.data.shape[1] != anim2.data.shape[1] or anim1.data.shape[2] != anim2.data.shape[2]:
        raise RuntimeError("Cannot join animations %s (%sx%s) and %s (%sx%s). Ensure that you are not joining baked and unbaked animations." % (anim1.name, anim1.data.shape[1], anim1.data.shape[2], anim2.name, anim2.data.shape[1], anim2.data.shape[2]))

    if anim1.frameRate != anim2.frameRate:
        log.warning("Joining animations %s (%.2fFPS) and %s (%.2fFPS) together but their framerates differ!" % (anim1.name, anim1.frameRate, anim2.name, anim2.frameRate))
    # TODO would be more efficient if this method allowed to join multiple animations at once
    nFrames = anim1.nFrames + anim2.nFrames
    framerate = anim1.frameRate
    name = anim1.name + '_' + anim2.name
    shape = anim1.data.shape
    dataLen = anim1.dataLen + anim2.dataLen

    poseData = np.concatenate((anim1.data,anim2.data)).reshape((dataLen,shape[1],shape[2]))

    return AnimationTrack(name, poseData, nFrames, framerate)

class VertexBoneWeights(object):
    """
    Weighted vertex to bone assignments.
    """
    def __init__(self, data, vertexCount=None, rootBone="root"):
        """
        Note: specifiying vertexCount is just for speeding up loading, if not 
        specified, vertexCount will be calculated automatically (taking a little
        longer to load).
        """
        self._vertexCount = None    # The number of vertices that are mapped
        self._wCounts = None        # Per vertex, the number of weights attached
        self._nWeights = None       # The maximum number of weights per vertex

        self.rootBone = rootBone

        self._data = self._build_vertex_weights_data(data, vertexCount, rootBone)
        self._calculate_num_weights()

        self._compiled = {}

        self.name = ""
        self.version = ""
        self.license = makehuman.getAssetLicense()
        self.description = ""

    @staticmethod
    def fromFile(filename, vertexCount=None, rootBone="root"):
        """
        Load vertex to bone weights from file
        """
        from collections import OrderedDict
        import json
        weightsData = json.load(open(filename, 'rb'), object_pairs_hook=OrderedDict)
        log.message("Loaded vertex weights %s from file %s", weightsData.get('name', 'unnamed'), filename)
        result = VertexBoneWeights(weightsData['weights'], vertexCount, rootBone)
        result.license.fromJson(weightsData)
        result.name = weightsData.get('name', result.name)
        result.version = weightsData.get('version', result.version)
        result.description = weightsData.get('description', result.description)
        return result

    def toFile(self, filename):
        """
        Save vertex to bone weights to a file.
        """
        import json

        def _format_output(data):
            """
            Conversion from internal dict format to the format used in the JSON
            data files, the opposite transformation of _build_vertex_weights_data

            Input format:
                { "bone_name": ([v_idx, ...], [v_weight, ...]), ... }

            Output format:
                { "bone_name": [(v_idx, v_weight), ...], ... }
            """
            from collections import OrderedDict
            result = OrderedDict()
            for bone_name, (v_idxs, v_wghts) in data.items():
                result[bone_name] = zip(v_idxs.tolist(), v_wghts.tolist())
            return result

        jsondata = {'weights': _format_output(self.data),
                    'name': self.name,
                    'description': self.description,
                    'version': self.version
                   }
        jsondata.update(self.license.asDict())

        f = open(filename, 'w')
        json.dump(jsondata, f, indent=4, separators=(',', ': '))
        f.close()

    def create(self, data, vertexCount=None, rootBone=None):
        """
        Create new VertexBoneWeights object with specified weights data
        """
        if rootBone is None:
            rootBone = self.rootBone
        return type(self)(data, vertexCount, rootBone)

    @property
    def data(self):
        return self._data

    @property
    def vertexCount(self):
        return self._vertexCount

    def getMaxNumberVertexWeights(self):
        return self._nWeights
    
    def compiled(self, nWeights=None, skel=None):
        if nWeights is None:
            nWeights = self._nWeights
        elif nWeights > self._nWeights:
            nWeights = self._nWeights

        if nWeights in self._compiled:
            return self._compiled[nWeights]
        elif skel is not None:
            self.compileData(skel, nWeights)
            return self._compiled[nWeights]
        else:
            return None

    def isCompiled(self, nWeights=None):
        if nWeights is None:
            nWeights = self._nWeights
        elif nWeights > self._nWeights:
            nWeights = self._nWeights

        return nWeights in self._compiled

    def compileData(self, skel, nWeights=None):
        if nWeights is None:
            nWeights = self._nWeights
        elif nWeights > self._nWeights:
            nWeights = self._nWeights

        self._compiled[nWeights] = self._compileVertexWeights(self.data, skel, nWeights, vertexCount=self._vertexCount)

    def clearCompiled(self):
        self._compiled = {}

    def _calculate_num_weights(self):
        self._wCounts = np.zeros(self._vertexCount, dtype=np.uint32)
        for bname, wghts in self._data.items():
            vs, _ = wghts
            self._wCounts[vs] += 1
        self._nWeights = max(self._wCounts)
            
    def _build_vertex_weights_data(self, vertexWeightsDict, vertexCount=None, rootBone="root"):
        """
        Build a consistent set of per-bone vertex weights from a dictionary loaded
        from (json) data file.
        The format of vertexWeightsDict is expected to be: 
            { "bone_name": [(v_idx, v_weight), ...], ... }

        The output format is of the form:
            { "bone_name": ([v_idx, ...], [v_weight, ...]), ... }
        With weights normalized, doubles merged, and unweighted vertices
        assigned to the root bone.
        """
        WEIGHT_THRESHOLD = 1e-4  # Threshold for including bone weight

        first_entry = vertexWeightsDict.keys()[0] if len(vertexWeightsDict) > 0 else None
        if len(vertexWeightsDict) > 0 and \
           len(vertexWeightsDict[first_entry]) == 2 and \
           isinstance(vertexWeightsDict[first_entry], tuple) and \
           isinstance(vertexWeightsDict[first_entry][1], np.ndarray) and \
           isinstance(vertexWeightsDict[first_entry][2], np.ndarray):
            # Input dict is already in the expected format, presume it does not
            # need to be built again
            if vertexCount is not None:
                self._vertexCount = vertexCount
            else:
                self._vertexCount = max([vn for vg in vertexWeightsDict.values() for vn in vg[0]])+1
            return vertexWeightsDict

        if vertexCount is not None:
            vcount = vertexCount
        else:
            vcount = max([vn for vg in vertexWeightsDict.values() for vn,_ in vg])+1
        self._vertexCount = vcount

        # Normalize weights and put them in np format
        wtot = np.zeros(vcount, np.float32)
        for vgroup in vertexWeightsDict.values():
            for item in vgroup:
                vn,w = item
                # Calculate total weight per vertex
                wtot[vn] += w

        from collections import OrderedDict
        boneWeights = OrderedDict()
        for bname,vgroup in vertexWeightsDict.items():
            if len(vgroup) == 0:
                continue
            weights = []
            verts = []
            v_lookup = {}
            n = 0
            for vn,w in vgroup:
                if vn in v_lookup:
                    # Merge doubles
                    v_idx = v_lookup[vn]
                    weights[v_idx] += w/wtot[vn]
                else:
                    v_lookup[vn] = len(verts)
                    verts.append(vn)
                    weights.append(w/wtot[vn])
            verts = np.asarray(verts, dtype=np.uint32)
            weights = np.asarray(weights, np.float32)
            # Sort by vertex index
            i_s = np.argsort(verts)
            verts = verts[i_s]
            weights = weights[i_s]
            # Filter out weights under the threshold
            i_s = np.argwhere(weights > WEIGHT_THRESHOLD)[:,0]
            verts = verts[i_s]
            weights = weights[i_s]
            boneWeights[bname] = (verts, weights)

        # Assign unweighted vertices to root bone with weight 1
        if rootBone not in boneWeights.keys():
            vs = []
            ws = []
        else:
            vs,ws = boneWeights[rootBone]
            vs = list(vs)
            ws = list(ws)
        rw_i = np.argwhere(wtot == 0)[:,0]
        vs.extend(rw_i)
        ws.extend(np.ones(len(rw_i), dtype=np.float32))
        if len(rw_i) > 0:
            if len(rw_i) < 100:
                # To avoid spamming the log, only print vertex indices if there's less than 100
                log.debug("Adding trivial bone weights to root bone %s for %s unweighted vertices. [%s]", rootBone, len(rw_i), ', '.join([str(s) for s in rw_i]))
            else:
                log.debug("Adding trivial bone weights to root bone %s for %s unweighted vertices.", rootBone, len(rw_i))
        if len(vs) > 0:
            boneWeights[rootBone] = (np.asarray(vs, dtype=np.uint32), np.asarray(ws, dtype=np.float32))

        return boneWeights

    def _compileVertexWeights(self, vertBoneMapping, skel, nWeights, vertexCount=None):
        """
        Compile vertex weights data to a more performant per-vertex format.
        """
        if vertexCount is None:
            vertexCount = 0
            for bname, mapping in vertBoneMapping.items():
                verts,weights = mapping
                vertexCount = max(max(verts), vertexCount)
            if vertexCount:
                vertexCount += 1

        # TODO use simple array columns instead of structured arrays (they are array of structs, not struct of arrays)
        if nWeights == 3:
            dtype = [('b_idx1', np.uint32), ('b_idx2', np.uint32), ('b_idx3', np.uint32), 
                     ('wght1', np.float32), ('wght2', np.float32), ('wght3', np.float32)]
        elif nWeights == 4:
            dtype = [('b_idx1', np.uint32), ('b_idx2', np.uint32), ('b_idx3', np.uint32), ('b_idx4', np.uint32),
                     ('wght1', np.float32), ('wght2', np.float32), ('wght3', np.float32), ('wght4', np.float32)]
        elif nWeights == 6:
            dtype = [('b_idx1', np.uint32), ('b_idx2', np.uint32), ('b_idx3', np.uint32), 
                     ('b_idx4', np.uint32), ('b_idx5', np.uint32), ('b_idx6', np.uint32), 
                     ('wght1', np.float32), ('wght2', np.float32), ('wght3', np.float32), 
                     ('wght4', np.float32), ('wght5', np.float32), ('wght6', np.float32)]
        elif nWeights == 5:
            dtype = [('b_idx1', np.uint32), ('b_idx2', np.uint32), ('b_idx3', np.uint32),
                     ('b_idx4', np.uint32), ('b_idx5', np.uint32),
                     ('wght1', np.float32), ('wght2', np.float32), ('wght3', np.float32),
                     ('wght4', np.float32), ('wght5', np.float32)]
        elif nWeights == 13:
            dtype = [('b_idx1', np.uint32), ('b_idx2', np.uint32), ('b_idx3', np.uint32), 
                     ('b_idx4', np.uint32), ('b_idx5', np.uint32), ('b_idx6', np.uint32), 
                     ('b_idx7', np.uint32), ('b_idx8', np.uint32), ('b_idx9', np.uint32), 
                     ('b_idx10', np.uint32), ('b_idx11', np.uint32), ('b_idx12', np.uint32), 
                     ('b_idx13', np.uint32),
                     ('wght1', np.float32), ('wght2', np.float32), ('wght3', np.float32), 
                     ('wght4', np.float32), ('wght5', np.float32), ('wght6', np.float32), 
                     ('wght7', np.float32), ('wght8', np.float32), ('wght9', np.float32), 
                     ('wght10', np.float32), ('wght11', np.float32), ('wght12', np.float32), 
                     ('wght13', np.float32)]
        elif nWeights == 2:
            dtype = [('b_idx1', np.uint32), ('b_idx2', np.uint32), 
                     ('wght1', np.float32), ('wght2', np.float32)]
        else:
            dtype = [('b_idx1', np.uint32), ('wght1', np.float32)]
        compiled_vertweights = np.zeros(vertexCount, dtype=dtype)

        # Convert weights from indexed by bone to indexed by vertex index
        _ws = dict()
        b_lookup = dict([(b.name,b_idx) for b_idx,b in enumerate(skel.getBones())])
        for bname, mapping in vertBoneMapping.items():
            try:
                b_idx = b_lookup[bname]
                verts,weights = mapping
                for v_idx, wght in zip(verts, weights):
                    if v_idx not in _ws:
                        _ws[v_idx] = []

                    # TODO not needed for now (no remapping yet), and perhaps doubles should be removed upon merge, not when compiling
                    # also in case of proxy remapping doubles need to be prevented
                    '''
                    b_idxs = [bidx for (_,bidx) in _ws[v_idx]]
                    if b_idx in b_idxs:
                        # Merge doubles (this needs to happen even if the _build_vertex_weights_data()
                        # step already performs double removal, in the case where
                        # weights were remapped to another rig and bones merged)
                        _i = b_idxs.index(b_idx)
                        _ws[v_idx][_i] = (_ws[v_idx][_i][0] + wght, b_idx)
                    else:
                        _ws[v_idx].append( (wght, b_idx) )
                    '''
                    _ws[v_idx].append( (wght, b_idx) )  # For now, assume there are no doubles
            except KeyError as e:
                log.warning("Bone %s not found in skeleton: %s" % (bname, e))
        for v_idx in _ws:
            # Sort by weight and keep only nWeights most significant weights
            if len(_ws[v_idx]) > nWeights:
                #log.debug("Vertex %s has too many weights (%s): %s" % (v_idx, len(_ws[v_idx]), str(sorted(_ws[v_idx], reverse=True))))
                _ws[v_idx] = sorted(_ws[v_idx], reverse=True)[:nWeights]
                # Re-normalize weights
                weightvals = np.asarray( [e[0] for e in _ws[v_idx]], dtype=np.float32)
                weightvals /= np.sum(weightvals)
                for i in xrange(nWeights):
                    _ws[v_idx][i] = (weightvals[i], _ws[v_idx][i][1])
            else:
                _ws[v_idx] = sorted(_ws[v_idx], reverse=True)

        for v_idx, wghts in _ws.items():
            for i, (w, bidx) in enumerate(wghts):
                compiled_vertweights[v_idx]['wght%s' % (i+1)] = w
                compiled_vertweights[v_idx]['b_idx%s' % (i+1)] = bidx

        return compiled_vertweights

class AnimatedMesh(object):
    """
    Manages skeletal animation for a mesh or multiple meshes.
    Multiple meshes can be added each with their specific bone-to-vertex mapping
    to make it possible to play back the same animation on a skeleton attached
    to multiple meshes.
    """

    def __init__(self, skel, mesh, vertexToBoneMapping):
        self.__skeleton = skel
        self.__meshes = []
        self.__vertexToBoneMaps = []
        self.__originalMeshCoords = []
        self.addBoundMesh(mesh, vertexToBoneMapping)

        self._posed = True
        self.__animations = {}
        self.__currentAnim = None
        self.__playTime = 0.0

        self.__inPlace = False  # Animate in place (ignore translation component of animation)
        self.onlyAnimateVisible = False  # Only animate visible meshes (note: enabling this can have undesired consequences!)

    def setBaseSkeleton(self, skel):
        self.__skeleton = skel
        self.removeAnimations(update=False)
        self.resetCompiledWeights()

    def resetCompiledWeights(self):
        for i, vmap in enumerate(self.__vertexToBoneMaps):
            if vmap is not None:
                vmap.clearCompiled()

    def addAnimation(self, anim):
        """
        Add an animation to this animated mesh.
        Note: poses are simply animations with only one frame.
        """
        self.__animations[anim.name] = anim

    def resetBakedAnimations(self):
        """
        Call to invalidate baked animations when they should be re-baked after
        modifying skeleton joint positions.
        """
        for anim_name in self.getAnimations():
            anim = self.getAnimation(anim_name)
            anim.resetBaked()
        log.debug('Done baking animations')

    def getAnimation(self, name):
        return self.__animations[name]

    def hasAnimation(self, name):
        return name in self.__animations.keys()

    def getAnimations(self):
        return self.__animations.keys()

    def removeAnimations(self, update=True):
        self.resetToRestPose(update)
        self.__animations = {}

    def removeAnimation(self, name):
        del self.__animations[name]
        if self.__currentAnim and self.__currentAnim.name == name:
            self.__currentAnim = None

    def setActiveAnimation(self, name):   # TODO maybe allow blending of several activated animations
        if not name:
            self.__currentAnim = None
        else:
            self.__currentAnim = self.__animations[name]

    def getActiveAnimation(self):
        if self.__currentAnim is None:
            return None
        else:
            return self.__currentAnim

    def setAnimateInPlace(self, enable):
        self.__inPlace = enable

    def getBaseSkeleton(self):
        return self.__skeleton

    def addBoundMesh(self, mesh, vertexToBoneMapping):
        if mesh.name in self.getBoundMeshes():
            log.warning("Replacing bound mesh with same name %s" % mesh.name)
            m, _ = self.getBoundMesh(mesh.name)
            if m == mesh:
                log.warning("Attempt to add the same bound mesh %s twice" % mesh.name)
            self.removeBoundMesh(mesh.name)

        if vertexToBoneMapping and mesh.getVertexCount() != vertexToBoneMapping.vertexCount:
            log.warning('Vertex count of bound mesh %s (%s) and vertex its weights (%s) differs, this might cause errors when skinning.', mesh.name, mesh.getVertexCount(), vertexToBoneMapping.vertexCount)

        # allows multiple meshes (also to allow to animate one model consisting of multiple meshes)
        originalMeshCoords = np.zeros((mesh.getVertexCount(),4), np.float32)
        originalMeshCoords[:,:3] = mesh.coord[:,:3]
        originalMeshCoords[:,3] = 1.0
        self.__originalMeshCoords.append(originalMeshCoords)
        self.__vertexToBoneMaps.append(vertexToBoneMapping)
        self.__meshes.append(mesh)

    def updateVertexWeights(self, meshName, vertexToBoneMapping):
        rIdx = self._getBoundMeshIndex(meshName)
        self.__vertexToBoneMaps[rIdx] = vertexToBoneMapping

    def removeBoundMesh(self, name):
        try:
            rIdx = self._getBoundMeshIndex(name)

            # First restore rest coords of mesh, then remove it
            try:
                self._updateMeshVerts(self.__meshes[rIdx], self.__originalMeshCoords[rIdx][:,:3])
            except:
                pass    # Don't fail if the mesh was already detached/destroyed
            del self.__meshes[rIdx]
            del self.__originalMeshCoords[rIdx]
            del self.__vertexToBoneMaps[rIdx]
        except:
            log.warning('Cannot remove bound mesh %s, no such mesh bound.', name)

    def getRestCoordinates(self, name):
        rIdx = self._getBoundMeshIndex(name)
        return self.__originalMeshCoords[rIdx][:,:3]

    def containsBoundMesh(self, mesh):
        mesh2, _ = self.getBoundMesh(mesh.name)
        return mesh2 == mesh

    def getBoundMesh(self, name):
        try:
            rIdx = self._getBoundMeshIndex(name)
        except:
            return None, None

        return self.__meshes[rIdx], self.__vertexToBoneMaps[rIdx]

    def getBoundMeshes(self):
        return [mesh.name for mesh in self.__meshes]

    def _getBoundMeshIndex(self, meshName):
        for idx, mesh in enumerate(self.__meshes):
            if mesh.name == meshName:
                return idx
        raise RuntimeError("No mesh with name %s bound to this animatedmesh" % meshName)

    def update(self, timeDeltaSecs):
        self.__playTime = self.__playTime + timeDeltaSecs
        self._pose()

    def resetTime(self):
        self.__playTime = 0.0
        self._pose()

    def setToTime(self, time, update=True):
        self.__playTime = float(time)
        if update:
            self._pose()

    def setToFrame(self, frameNb, update=True):
        if not self.__currentAnim:
            return
        frameNb = int(frameNb)
        self.__playTime = float(frameNb)/self.__currentAnim.frameRate
        if update:
            self._pose()

    def setPosed(self, posed):
        """
        Set mesh posed (True) or set to rest pose (False), changes pose state.
        """
        self._posed = posed
        self.refreshPose(updateIfInRest=True)

    def isPosed(self):
        return self._posed and self.isPoseable()

    def isPoseable(self):
        return bool(self.__currentAnim and self.getBaseSkeleton())

    @property
    def posed(self):
        return self.isPosed()

    def resetToRestPose(self, update=True):
        """
        Remove the currently set animation/pose and reset the mesh in rest pose.
        Does not affect posed state.
        """
        self.setActiveAnimation(None)
        self.__playTime = 0.0
        if self.getBaseSkeleton():
            self.refreshPose(updateIfInRest=update)
        elif update:
            self.resetTime()

    def getTime(self):
        return self.__playTime

    def getPoseState(self, noBake=False):
        """
        Get the pose matrices of the active animation at the current play time.
        Returned matrices are baked (they are skin matrices, relative to bone 
        rest pose in object space) if the active animation is baked, otherwise
        they are plain pose matrices in local bone space.
        """
        poseState = self.__currentAnim.getAtTime(self.__playTime, noBake)
        if self.__inPlace:
            poseState = poseState.copy()  # TODO this probably doesntt work with baked skinning matrices
            # Remove translation from matrix
            poseState[:,:3,3] = np.zeros((poseState.shape[0],3), dtype=np.float32)
        return poseState

    def _pose(self, syncSkeleton=True):
        """
        If syncSkeleton is True, even when baked animations are used, that do not require
        applying motion to the skeleton to calculate the skinning matrices, the pose
        state of the skeleton is updated. Thus setting this to True is slower and
        is advised for static poses only.
        """
        if self.isPosed():
            if not self.getBaseSkeleton():
                return

            if not self.__currentAnim.isBaked():
                # Ensure animation is baked for fast skinning
                self.__currentAnim.bake(self.getBaseSkeleton())

            poseState = self.getPoseState()

            # Else we pass poseVerts matrices immediately from animation track for performance improvement (cached or baked)
            for idx,mesh in enumerate(self.__meshes):
                # TODO make onlyAnimateVisible work by excluding some meshes from the filter that should always be animated
                if self.onlyAnimateVisible and not mesh.visibility:
                    continue

                if self.__vertexToBoneMaps[idx] is None:
                    log.warning('No weights assigned to bound mesh %s, skip posing it.', mesh.name)
                    continue

                try:
                    if not self.__currentAnim.isBaked():
                        # Old slow way of skinning
                        self.getBaseSkeleton().setPose(poseState)
                        posedCoords = self.getBaseSkeleton().skinMesh(self.__originalMeshCoords[idx], self.__vertexToBoneMaps[idx].data)
                    else:
                        if not self.__vertexToBoneMaps[idx].isCompiled(6):
                            log.debug("Compiling vertex bone weights for %s", mesh.name)
                            self.__vertexToBoneMaps[idx].compileData(self.getBaseSkeleton(), 6)

                        # New fast skinnig approach
                        posedCoords = skinMesh(self.__originalMeshCoords[idx], self.__vertexToBoneMaps[idx].compiled(6), poseState)
                except Exception as e:
                    log.error("Error skinning mesh %s", mesh.name, exc_info=True)
                    raise e
                # TODO you could avoid an array copy by passing the mesh.coord list directly and modifying it in place
                self._updateMeshVerts(mesh, posedCoords[:,:3])

            # Adapt the bones of the skeleton to match current skinned pose (slower, should only be used for static poses)
            if syncSkeleton and self.__currentAnim.isBaked():
                self.getBaseSkeleton().setPose(self.getPoseState(noBake=True))
        else:
            if self.getBaseSkeleton() and syncSkeleton:
                self.getBaseSkeleton().setToRestPose()
            for idx,mesh in enumerate(self.__meshes):
                self._updateMeshVerts(mesh, self.__originalMeshCoords[idx])

    def _updateMeshVerts(self, mesh, verts):
        # TODO this is way too slow for realtime animation, but good for posing. For animation, update the r_ verts directly, as well as the r_vnorm members
        # TODO use this mapping to directly update the opengl data for animation
        # Remap vertex weights to the unwelded vertices of the object (mesh.coord to mesh.r_coord)
        #originalToUnweldedMap = mesh.inverse_vmap

        mesh.changeCoords(verts[:,:3])
        mesh.calcNormals()  # TODO this is too slow for animation
        mesh.update()

    def refreshStaticMeshes(self, refresh_pose=True):
        """
        Invoke this method after the static (rest pose) meshes were changed.
        Updates the shadow copies with original vertex coordinates and re-applies
        the pose if this animated object was in posed mode.
        """
        for mIdx, mesh in enumerate(self.__meshes):
            self.__originalMeshCoords[mIdx][:,:3] = mesh.coord[:,:3]
        if refresh_pose:
            self.refreshPose(updateIfInRest=False)

    def _updateOriginalMeshCoords(self, name, coord):
        rIdx = self._getBoundMeshIndex(name)
        self.__originalMeshCoords[rIdx][:,:3] = coord[:,:3]

    def refreshPose(self, updateIfInRest=False, syncSkeleton=True):
        if not self.getBaseSkeleton():
            self.resetToRestPose()
        if updateIfInRest or self.isPosed():
            self._pose(syncSkeleton=syncSkeleton)
        elif syncSkeleton and self.getBaseSkeleton():
            # Do not do the skinning (which is trivial), but nonetheless ensure that the skeleton's
            # pose state is restored to rest
            self.getBaseSkeleton().setToRestPose()

def skinMesh(coords, compiledVertWeights, poseData):
    """
    More efficient way of linear blend skinning or smooth skinning.
    As proposed in http://graphics.ucsd.edu/courses/cse169_w05/3-Skin.htm we use
    a vertex-major loop.
    We also use a fixed number of weights per vertex.
    Uses accumulated matrix skinning (http://http.developer.nvidia.com/GPUGems/gpugems_ch04.html)

    Care should be taken to supply coords with the right dimensions. This method
    accepts both coords[nverts, 3] and coords[nverts, 4] dimensions. The fourth
    member being the homogenous coordinate, which should be 1 if translations
    should affect the vertex position (eg for mesh coordinates), and 0 for
    rotations only (for directions such as normals, tangents and targets).
    If coords is nx3 size, this method will perform faster as only 3x3 matrix
    multiplies are performed, otherwise 3x4 matrices are multiplied.
    """
    # TODO allow skinning only the visible (not statically hidden) vertices, for performance reasons (eg if an alt. topology is set, do we animate both basemesh and topology?)

    if coords.shape[1] == 4:
        # Vertices contain homogenous coordinate (1 if translation affects position,
        # 0 if vertex should not be affected by translation (only direction) )
        c = 4
    else:
        # Translations do not affect vertices (faster as this requires only 3x3 matrix multiplies)
        c = 3

    W = compiledVertWeights
    P = poseData
    if len(compiledVertWeights.dtype) == 4*2:
        # nWeights = 4
        accum = W['wght1'][:,None,None] * P[W['b_idx1']][:,:3,:c] + \
                W['wght2'][:,None,None] * P[W['b_idx2']][:,:3,:c] + \
                W['wght3'][:,None,None] * P[W['b_idx3']][:,:3,:c] + \
                W['wght4'][:,None,None] * P[W['b_idx4']][:,:3,:c]
    elif len(compiledVertWeights.dtype) == 2:
        # nWeights = 1
        accum = W['wght1'][:,None,None] * P[W['b_idx1']][:,:3,:c]
    elif len(compiledVertWeights.dtype) == 6*2:
        # nWeights = 13
        accum = W['wght1'][:,None,None] * P[W['b_idx1']][:,:3,:c] + \
                W['wght2'][:,None,None] * P[W['b_idx2']][:,:3,:c] + \
                W['wght3'][:,None,None] * P[W['b_idx3']][:,:3,:c] + \
                W['wght4'][:,None,None] * P[W['b_idx4']][:,:3,:c] + \
                W['wght5'][:,None,None] * P[W['b_idx5']][:,:3,:c] + \
                W['wght6'][:,None,None] * P[W['b_idx6']][:,:3,:c]
    elif len(compiledVertWeights.dtype) == 5*2:
        # nWeights = 5
        accum = W['wght1'][:,None,None] * P[W['b_idx1']][:,:3,:c] + \
                W['wght2'][:,None,None] * P[W['b_idx2']][:,:3,:c] + \
                W['wght3'][:,None,None] * P[W['b_idx3']][:,:3,:c] + \
                W['wght4'][:,None,None] * P[W['b_idx4']][:,:3,:c] + \
                W['wght5'][:,None,None] * P[W['b_idx5']][:,:3,:c]
    elif len(compiledVertWeights.dtype) == 13*2:
        # nWeights = 13
        accum = W['wght1'][:,None,None] * P[W['b_idx1']][:,:3,:c] + \
                W['wght2'][:,None,None] * P[W['b_idx2']][:,:3,:c] + \
                W['wght3'][:,None,None] * P[W['b_idx3']][:,:3,:c] + \
                W['wght4'][:,None,None] * P[W['b_idx4']][:,:3,:c] + \
                W['wght5'][:,None,None] * P[W['b_idx5']][:,:3,:c] + \
                W['wght6'][:,None,None] * P[W['b_idx6']][:,:3,:c] + \
                W['wght7'][:,None,None] * P[W['b_idx7']][:,:3,:c] + \
                W['wght8'][:,None,None] * P[W['b_idx8']][:,:3,:c] + \
                W['wght9'][:,None,None] * P[W['b_idx9']][:,:3,:c] + \
                W['wght10'][:,None,None] * P[W['b_idx10']][:,:3,:c] + \
                W['wght11'][:,None,None] * P[W['b_idx11']][:,:3,:c] + \
                W['wght12'][:,None,None] * P[W['b_idx12']][:,:3,:c] + \
                W['wght13'][:,None,None] * P[W['b_idx13']][:,:3,:c]
    elif len(compiledVertWeights.dtype) == 2*2:
        # nWeights = 2
        accum = W['wght1'][:,None,None] * P[W['b_idx1']][:,:3,:c] + \
                W['wght2'][:,None,None] * P[W['b_idx2']][:,:3,:c]
    else:
        # nWeights = 3
        accum = W['wght1'][:,None,None] * P[W['b_idx1']][:,:3,:c] + \
                W['wght2'][:,None,None] * P[W['b_idx2']][:,:3,:c] + \
                W['wght3'][:,None,None] * P[W['b_idx3']][:,:3,:c]

    # Note: np.sum(M * vs, axis=-1) is a matrix multiplication of mat M with
    # a series of vertices vs
    # Good resource: http://jameshensman.wordpress.com/2010/06/14/multiple-matrix-multiplication-in-numpy
    #return np.sum(accum[:,:3,:4] * coords[:,None,:], axis=-1)

    # Using einstein summation for matrix * vertex multiply, appears to be
    # slightly faster
    return np.einsum('ijk,ikl -> ij', accum[:,:3,:c], coords[:,:c,None])

def emptyTrack(nFrames, nBones=1):
    """
    Create an empty (rest pose) animation track pose data array.
    """
    nMats = nFrames*nBones
    matData = np.zeros((nMats,3,4), dtype=np.float32)
    matData[:,:3,:3] = np.identity(3, dtype=np.float32)
    return matData

def emptyPose(nBones=1):
    """
    Create an empty animation containing one frame. 
    """
    return emptyTrack(1, nBones)

IDENT_POSE = emptyPose()
IDENT_4 = np.identity(4, dtype=np.float32)
def isRest(poseMat):
    """
    Determine whether specified pose matrix is a trivial rest pose (identity)
    """
    global IDENT_POSE
    global IDENT_4
    delta = 1e-05

    if poseMat.shape == IDENT_POSE.shape:
        return np.allclose(poseMat, IDENT_POSE, atol=delta)
    elif poseMat.shape == (4,4):
        return np.allclose(poseMat, IDENT_4, atol=delta)
    else:
        return np.allclose(poseMat, IDENT_4[:3,:4], atol=delta)

def animationRelativeToPose(animation, restpose):
    # TODO create animation track copy that is relative to restpose
    pass

def loadPoseFromMhpFile(filepath, skel):
    """
    Load a MHP pose file that contains a static pose. Posing data is defined
    with quaternions to indicate rotation angles.
    Creates a single frame animation track (a pose).
    """
    import log
    import os
    from codecs import open

    log.message("Loading MHP file %s", filepath)
    fp = open(filepath, "rU", encoding="utf-8")
    valid_file = False

    boneMap = skel.getBoneToIdxMapping()
    nBones = len(boneMap.keys())
    poseMats = np.zeros((nBones,4,4),dtype=np.float32)
    poseMats[:] = np.identity(4, dtype=np.float32)

    mats = dict()
    for line in fp:
        words = line.split()
        if len(words) > 0 and words[0].startswith('#'):
            # comment
            continue
        if len(words) < 10:
            log.warning("Too short line in mhp file: %s" % " ".join(words))
            continue
        elif words[1] == "matrix":
            bname = words[0]
            boneIdx = boneMap[bname]
            rows = []
            n = 2
            for i in range(4):
                rows.append([float(words[n]), float(words[n+1]), float(words[n+2]), float(words[n+3])])
                n += 4
            # Invert Z rotation (for some reason this is required to make MHP orientations work)
            rows[0][1] = -rows[0][1]
            rows[1][0] = -rows[1][0]
            # Invert X rotation
            #rows[1][2] = -rows[1][2]
            #rows[2][1] = -rows[2][1]
            # Invert Y rotation
            rows[0][2] = -rows[0][2]
            rows[2][0] = -rows[2][0]

            mats[boneIdx] = np.array(rows)
        else:
            log.warning("Unknown keyword in mhp file: %s" % words[1])

    if not valid_file:
        log.error("Loading of MHP file %s failed, probably a bad file." % filepath)

    '''
    # Apply pose to bones in breadth-first order (parent to child bone)
    for boneIdx in sorted(mats.keys()):
        bone = skel.boneslist[boneIdx]
        mat = mats[boneIdx]
        if bone.parent:
            mat = np.dot(poseMats[bone.parent.index], np.dot(bone.matRestRelative, mat))
        else:
            mat = np.dot(self.matRestGlobal, mat)
        poseMats[boneIdx] = mat

    for boneIdx in sorted(mats.keys()):
        bone = skel.boneslist[boneIdx]
        poseMats[boneIdx] = np.dot(poseMats[boneIdx], la.inv(bone.matRestGlobal))
    '''
    for boneIdx in sorted(mats.keys()):
        poseMats[boneIdx] = mats[boneIdx]

    fp.close()

    name = os.path.splitext(os.path.basename(filepath))[0]
    result = Pose(name, poseMats)

    return result
