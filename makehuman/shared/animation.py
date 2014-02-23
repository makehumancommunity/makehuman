#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Data handlers for skeletal animation.
"""

import math
import numpy as np


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
            as a list of 4x4 pose matrices
            with n = nBones*nFrames
            pose matrices should be ordered per frame - per bone
            eg: poseData = [ B0F0, B1F0, B2F0, B0F1, B1F1, B2F1]
                with each BxFy a 4x4 pose matrix for one bone in one frame
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
        if poseData.shape != (self.dataLen, 4, 4):
            raise RuntimeError("The specified pose data does not have the proper dimensions. Is %s, expected (%s, 4, 4)" % (poseData.shape, self.dataLen))

        self.data = poseData
        self.frameRate = float(framerate)      # Numer of frames per second
        self.loop = True
        
        # Type of interpolation between animation frames
        #   0  no interpolation
        #   1  linear
        #   2  logarithmic   # TODO!
        self.interpolationType = 0

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
        self.addMesh(mesh, vertexToBoneMapping)

        self.__animations = {}
        self.__currentAnim = None
        self.__playTime = 0.0

        self.__inPlace = False
        self.onlyAnimateVisible = True

    def addAnimation(self, anim):
        self.__animations[anim.name] = anim

    def getAnimation(self, name):
        return self.__animations[name]

    def hasAnimation(self, name):
        return name in self.__animations.keys()

    def getAnimations(self):
        return self.__animations.keys()

    def removeAnimations(self):
        self.__animations = {}
        self.__currentAnim = None

    def removeAnimation(self, name):
        del self.__animations[name]
        if self.__currentAnim and self.__currentAnim.name == name:
            self.__currentAnim = None

    def setActiveAnimation(self, name):   # TODO maybe allow blending of several activated animations
        if not name:
            self.__currentAnim = None
        else:
            self.__currentAnim = self.__animations[name]

    def setAnimateInPlace(self, enable):
        self.__inPlace = enable

    def getSkeleton(self):
        return self.__skeleton

    def addMesh(self, mesh, vertexToBoneMapping):
        # allows multiple meshes (also to allow to animate one model consisting of multiple meshes)
        originalMeshCoords = np.zeros((mesh.getVertexCount(),4), np.float32)
        originalMeshCoords[:,3] = 1
        originalMeshCoords[:,:3] = mesh.coord[:,:3]        
        self.__originalMeshCoords.append(originalMeshCoords)
        self.__vertexToBoneMaps.append(vertexToBoneMapping)
        self.__meshes.append(mesh)

    def removeMesh(self, name):
        rIdx = -1
        for idx,m in enumerate(self.__meshes):
            if name == m.name:
                rIdx = idx
                break

        if rIdx > -1:
            # First restore rest coords of mesh, then remove it
            try:
                self._updateMeshVerts(self.__meshes[rIdx], self.__originalMeshCoords[rIdx][:,:3])
            except:
                pass    # Don't fail if the mesh was already detached/destroyed
            del self.__meshes[rIdx]
            del self.__originalMeshCoords[rIdx]
            del self.__vertexToBoneMaps[rIdx]

    def containsMesh(self, mesh):
        mesh2, _ = self.getMesh(mesh.name)
        return mesh2 == mesh

    def getMesh(self, name):
        rIdx = -1
        for idx, mesh in enumerate(self.__meshes):
            if mesh.name == name:
                rIdx = idx
                break

        if rIdx > -1:
            return self.__meshes[rIdx], self.__vertexToBoneMaps[rIdx]
        else:
            return None, None

    def getMeshes(self):
        return [mesh.name for mesh in self.__meshes]

    def update(self, timeDeltaSecs):
        self.__playTime = self.__playTime + timeDeltaSecs
        self._pose()

    def resetTime(self):
        self.__playTime = 0.0
        self._pose()

    def setToTime(self, time):
        self.__playTime = float(time)
        self._pose()

    def setToFrame(self, frameNb):
        if not self.__currentAnim:
            return
        frameNb = int(frameNb)
        self.__playTime = float(frameNb)/self.__currentAnim.frameRate
        self._pose()

    def setToRestPose(self):
        self.setActiveAnimation(None)
        self.resetTime()

    def getTime(self):
        return self.__playTime

    def _pose(self):
        if self.__currentAnim:
            poseState = self.__currentAnim.getAtTime(self.__playTime)
            if self.__inPlace:
                poseState = poseState.copy()
                # Remove translation from matrix
                poseState[:,:3,3] = np.zeros((poseState.shape[0],3), dtype=np.float32)
            # TODO pass poseVerts matrices immediately from animation track for performance improvement (cache them)
            self.__skeleton.setPose(poseState)
            for idx,mesh in enumerate(self.__meshes):
                if self.onlyAnimateVisible and not mesh.visibility:
                    continue
                posedCoords = self.__skeleton.skinMesh(self.__originalMeshCoords[idx], self.__vertexToBoneMaps[idx])
                # TODO you could avoid an array copy by passing the mesh.coord list directly and modifying it in place
                self._updateMeshVerts(mesh, posedCoords[:,:3])
        else:
            self.__skeleton.setToRestPose() # TODO not strictly necessary if you only want to skin the mesh
            for idx,mesh in enumerate(self.__meshes):
                self._updateMeshVerts(mesh, self.__originalMeshCoords[idx][:,:3])

    def _updateMeshVerts(self, mesh, verts):
        mesh.changeCoords(verts)
        mesh.calcNormals()
        mesh.update()

def emptyTrack(nFrames, nBones=1):
    """
    Create an empty (rest pose) animation track pose data array.
    """
    nMats = nFrames*nBones
    return np.tile(np.identity(4), nMats).transpose().reshape((nMats,4,4))

def emptyPose(nBones=1):
    """
    Create an empty animation containing one frame. 
    """
    return emptyTrack(1, nBones)
