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

Data handlers for skeletal animation.
"""

# TODO perhaps do not adapt camera to posed position, always use rest coordinates

import math
import numpy as np
import numpy.linalg as la
import log


INTERPOLATION = {
    'NONE'  : 0,
    'LINEAR': 1,
    'LOG':    2
}

class AnimationTrack(object):

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
        self.dataLen = len(poseData)
        self.nFrames = nFrames
        self.nBones = self.dataLen/nFrames

        if self.nBones*self.nFrames != self.dataLen:
            raise RuntimeError("The specified pose data does not have the proper length. Is %s, expected %s (nBones*nFrames)." % (self.dataLen, self.nBones*self.nFrames))
        if not (poseData.shape == (self.dataLen, 3, 4) or poseData.shape == (self.dataLen, 4, 4)):
            raise RuntimeError("The specified pose data does not have the proper dimensions. Is %s, expected (%s, 4, 4) or (%s, 3, 4)" % (poseData.shape, self.dataLen, self.dataLen))

        self._data = poseData[:self.dataLen,:3,:4]  # We do not store the last row to save memory
        self.frameRate = float(framerate)      # Numer of frames per second
        self.loop = True

        self._data_baked = None
        
        # Type of interpolation between animation frames
        #   0  no interpolation
        #   1  linear
        #   2  logarithmic   # TODO!
        self.interpolationType = 0

    @property
    def data(self):
        if self.isBaked():
            return self._data_baked
        else:
            return self._data

    def isBaked(self):
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

    def getAtTime(self, time):
        """
        Returns the animation state at the specified time.
        When time is between two stored frames the animation values will be
        interpolated.
        """
        frameIdx, fraction = self.getFrameIndexAtTime(time)
        if fraction == 0 or self.interpolationType == 0:
            # Discrete animation
            idx = frameIdx*self.nBones
            return self.data[idx:idx+self.nBones]
        elif self.interpolationType == 1:
            # Linear interpolation
            idx1 = frameIdx*self.nBones
            idx2 = ((frameIdx+1) % self.nFrames) * self.nBones
            return self.data[idx1:idx1+self.nBones] * (1-fraction) + \
                   self.data[idx2:idx2+self.nBones] * fraction
        elif self.interpolationType == 2:
            # Logarithmic interpolation
            pass # TODO

    def getAtFramePos(self, frame):
        frame = int(frame)
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

        return frameIdx, fraction

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

    def fromPoseUnit(self, unitPoseData):
        # TODO
        pass

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

        self._affectedBones = None  # Stores for every frame which bones are posed

    def sparsify(self, newFrameRate):
        raise NotImplementedError("sparsify() does not exist for poseunits")

    def getPoseNames(self):
        return self._poseNames

    def getUnitPose(self, name):
        if isinstance(name, basestring):
            frame_idx = poseNames.index(name)
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
        IDENT = emptyPose()

        for f_idx in xrange(self.nFrames):
            frameData = self.getAtFramePos(f_idx)
            self._affectedBones.append( [] )
            for b_idx in xrange(self.nBones):
                if not (frameData[b_idx] == IDENT).all():
                    self._affectedBones[f_idx].append(b_idx)

    def getBlendedPose(self, poses, weights):
        # TODO normalize weights?
        if isinstance(poses[0], basestring):
            f_idxs = [self.getPoseNames().index(pname) for pname in poses]
        else:
            f_idxs = poses

        if not isinstance(weights, np.ndarray):
            weights = np.asarray(weights, dtype=np.float32)

        if len(f_idxs) == 1:
            return float(weights[0]) * self.getAtFramePos(f_idxs[0])
        else:
            result = float(weights[0]) * self.getAtFramePos(f_idxs[0]) + \
                     float(weights[1]) * self.getAtFramePos(f_idxs[1])

        for i,f_idx in enumerate(f_idxs[2:]):
            result = result + float(weights[i]) * self.getAtFramePos(f_idx)

        return result


def poseFromUnitPose(name, unitPoseData):
    # TODO
    pass

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
        poseData += w * pose

    return poseData


class VertexBoneWeights(object):
    """
    Weighted vertex to bone assignments.
    """
    def __init__(self, data, vertexCount=None):
        """
        Note: specifiying vertexCount is just for speeding up loading, if not 
        specified, vertexCount will be calculated automatically (taking a little
        longer to load).
        """
        self._vertexCount = None    # The number of vertices that are mapped
        self._wCounts = None        # Per vertex, the number of weights attached
        self._nWeights = None       # The maximum number of weights per vertex

        self._data = self._build_vertex_weights_data(data, vertexCount)
        self._calculate_num_weights()

        self._compiled = {}

    @staticmethod
    def fromFile(filename, vertexCount=None):
        """
        Load vertex to bone weights from file
        """
        from collections import OrderedDict
        import json
        weightsData = json.load(open(filename, 'rb'), object_pairs_hook=OrderedDict)
        log.message("Loaded vertex weights %s from file %s", weightsData.get('name', 'unnamed'), filename)
        return VertexBoneWeights(weightsData['weights'], vertexCount)

    def create(self, data, vertexCount=None):
        """
        Create new VertexBoneWeights object with specified weights data
        """
        return type(self)(data, vertexCount)

    @property
    def data(self):
        return self._data
    
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
                log.debug("Adding trivial bone weights to bone %s for %s unweighted vertices. [%s]", rootBone, len(rw_i), ', '.join([str(s) for s in rw_i]))
            else:
                log.debug("Adding trivial bone weights to bone %s for %s unweighted vertices.", rootBone, len(rw_i))
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

    def setSkeleton(self, skel):
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

    def getSkeleton(self):
        return self.__skeleton

    def addBoundMesh(self, mesh, vertexToBoneMapping):
        if mesh.name in self.getBoundMeshes():
            log.warning("Replacing bound mesh with same name %s" % mesh.name)
            m, _ = self.getBoundMesh(mesh.name)
            if m == mesh:
                log.warning("Attempt to add the same bound mesh %s twice" % mesh.name)
            self.removeBoundMesh(mesh.name)

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
            pass

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
        self.refreshPose(True)

    def isPosed(self):
        return self._posed and self.isPoseable()

    def isPoseable(self):
        return bool(self.__currentAnim and self.getSkeleton())

    @property
    def posed(self):
        return self.isPosed()

    def resetToRestPose(self, update=True):
        """
        Remove the currently set animation/pose and reset the mesh in rest pose.
        Does not affect posed state.
        """
        self.setActiveAnimation(None)
        if update:
            self.resetTime()
        else:
            self.__playTime = 0.0

    def getTime(self):
        return self.__playTime

    def getPoseState(self):
        """
        Get the pose matrices of the active animation at the current play time.
        Returned matrices are baked (they are skin matrices, relative to bone 
        rest pose in object space) if the active animation is baked, otherwise
        they are plain pose matrices in local bone space.
        """
        poseState = self.__currentAnim.getAtTime(self.__playTime)
        if self.__inPlace:
            poseState = poseState.copy()
            # Remove translation from matrix
            poseState[:,:3,3] = np.zeros((poseState.shape[0],3), dtype=np.float32)
        return poseState

    def _pose(self):
        if self.isPosed():
            if not self.getSkeleton():
                return

            if not self.__currentAnim.isBaked():
                #self.getSkeleton().setPose(poseState)  # Old slow way of skinning

                # Ensure animation is baked for fast skinning
                self.__currentAnim.bake(self.getSkeleton())

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
                    if not self.__vertexToBoneMaps[idx].isCompiled(4):
                        log.debug("Compiling vertex bone weights for %s", mesh.name)
                        self.__vertexToBoneMaps[idx].compileData(self.getSkeleton(), 4)

                    # Old slow way of skinning
                    #posedCoords = self.getSkeleton().skinMesh(self.__originalMeshCoords[idx], self.__vertexToBoneMaps[idx].data)

                    # New fast skinnig approach
                    posedCoords = skinMesh(self.__originalMeshCoords[idx], self.__vertexToBoneMaps[idx].compiled(4), poseState)
                except Exception as e:
                    log.error("Error skinning mesh %s", mesh.name, exc_info=True)
                    raise e
                # TODO you could avoid an array copy by passing the mesh.coord list directly and modifying it in place
                self._updateMeshVerts(mesh, posedCoords[:,:3])
        else:
            if self.getSkeleton():
                self.getSkeleton().setToRestPose() # TODO not strictly necessary if you only want to skin the mesh
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

    def refreshPose(self, updateIfInRest=False):
        if not self.getSkeleton():
            self.resetToRestPose()
        if updateIfInRest or self.isPosed():
            self._pose()

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
