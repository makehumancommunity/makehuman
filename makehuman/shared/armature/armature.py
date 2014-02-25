#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Base armature
"""

import math
import log
from collections import OrderedDict

import numpy as np
import numpy.linalg as la
import transformations as tm

import makehuman
from .flags import *
from .utils import *

#-------------------------------------------------------------------------------
#   Setup Armature
#-------------------------------------------------------------------------------

def setupArmature(name, human, options):
    from .parser import Parser
    if options is None:
        return None
    else:
        log.message("Setup rig %s" % name)
        amt = Armature(name, options)
        amt.parser = Parser(amt, human)
        amt.setup()
        log.message("Using rig with options %s" % options)
        return amt

#-------------------------------------------------------------------------------
#   Armature base class.
#-------------------------------------------------------------------------------

class Armature:

    def __init__(self, name, options):
        self.name = name
        self.options = options
        self.parser = None
        self.origin = None
        self.roots = []
        self.bones = OrderedDict()
        self.hierarchy = []
        self.locale = None
        self._tposes = None

        self.objectProps = [
            ("MhVersion", '"%s"' % makehuman.getVersionStr().replace(" ","_")),
            ("MhBaseMesh", '"%s"' % makehuman.getBasemeshVersion().replace(" ","_")),
            ]
        self.armatureProps = [('MhxScale', options.scale)]

        self.done = False

        self.vertexWeights = OrderedDict([])
        self.isNormalized = False


    def __repr__(self):
        return ("  <BaseArmature %s %s>" % (self.name, self.options.rigtype))


    def setup(self):
        self.parser.setup()
        self.origin = self.parser.origin
        self.rename(self.options.locale)


    def rescale(self, scale):
        # OK to overwrite bones, because they are not used elsewhere
        for bone in self.bones.values():
            bone.rescale(scale)


    def rename(self, locale):
        if self.locale == locale:
            return
        self.locale = locale
        if locale:
            locale.load()

        newbones = OrderedDict()
        for bone in self.bones.values():
            bname = bone.name
            bone.rename(locale, newbones)

        self.bones = newbones

        for bname,vgroup in self.vertexWeights.items():
            newname = locale.rename(bname)
            if newname != bname:
                self.vertexWeights[newname] = vgroup
                del self.vertexWeights[bname]


    def normalizeVertexWeights(self, human):
        if self.isNormalized:
            return

        nVerts = len(human.meshData.coord)
        wtot = np.zeros(nVerts, float)
        for vgroup in self.vertexWeights.values():
            for vn,w in vgroup:
                wtot[vn] += w

        for bname in self.vertexWeights.keys():
            vgroup = self.vertexWeights[bname]
            weights = np.zeros(len(vgroup), float)
            verts = []
            n = 0
            for vn,w in vgroup:
                verts.append(vn)
                weights[n] = w/wtot[vn]
                n += 1
            self.vertexWeights[bname] = (verts, weights)

        self.isNormalized = True


    def getBindMatrix(self, config):
        bmat = tm.rotation_matrix(math.pi/2, (1,0,0))
        return bmat
        restmat = subtractOffset(_Identity, config)
        return np.dot(restmat, bmat)


    def _getTPoses(self):
        if self._tposes:
            return self._tposes
        else:
            self._tposes = readMhpFile("data/mhx/tpose.mhp")
            return self._tposes


    def getTPose(self):
        pose = {}
        for bone in self.bones.values():
            bone.calcRestMatrix()
            tpose = bone._getTPoseMatrix()
            #tpose = bone.matrixRest
            pose[bone.name] = np.dot(tpose, la.inv(bone.matrixRest))
        return pose


#-------------------------------------------------------------------------------
#   Loader for the modern mhp format that uses matrices only
#-------------------------------------------------------------------------------

def readMhpFile(filepath):
    log.message("Loading MHP file %s", filepath)
    poses = {}
    with open(filepath, "rU") as fp:
        for line in fp:
            words = line.split()
            if len(words) < 10:
                continue
            elif words[1] == "matrix":
                bname = words[0]
                rows = []
                n = 2
                for i in range(4):
                    rows.append((float(words[n]), float(words[n+1]), float(words[n+2]), float(words[n+3])))
                    n += 4
                poses[bname] = np.array(rows)
    return poses

#-------------------------------------------------------------------------------
#   Bone class
#-------------------------------------------------------------------------------

class Bone:
    def __init__(self, amt, name):
        self.name = name
        self.origName = name
        self.type = "LimbNode"
        self.armature = amt
        self.head = None
        self.tail = None
        self.roll = 0
        self.parent = None
        self.setFlags(0)
        self.poseFlags = 0
        self.layers = L_MAIN
        self.length = 0
        self.customShape = None
        self.children = []

        self.location = (0,0,0)
        self.lockLocation = (0,0,0)
        self.lockRotation = (0,0,0)
        self.lockScale = (1,1,1)
        self.ikDof = (1,1,1)
        #self.lock_rotation_w = False
        #self.lock_rotations_4d = False

        self.constraints = []
        self.drivers = []

        # Matrices:
        # matrixRest:       4x4 rest matrix, relative world
        # matrixRelative:   4x4 rest matrix, relative parent
        # matrixPose:       4x4 pose matrix, relative parent and own rest pose
        # matrixGlobal:     4x4 matrix, relative world
        # matrixVerts:      4x4 matrix, relative world and own rest pose

        self.matrixRest = None
        self.matrixRelative = None
        self.matrixTPose = None
        self.matrixGlobal = None


    def __repr__(self):
        return "<Bone %s %s %s>" % (self.name, self.parent, self.children)


    def fromInfo(self, info):
        if len(info) == 5:
            self.roll, self.parent, flags, self.layers, self.poseFlags = info
        else:
            self.roll, self.parent, flags, self.layers = info
            self.poseFlags = 0
        if self.parent and not flags & F_NOLOCK:
            self.lockLocation = (1,1,1)
        if flags & F_LOCKY:
            self.lockRotation = (0,1,0)
        if flags & F_LOCKROT:
            self.lockRotation = (1,1,1)
        self.setFlags(flags)
        if self.roll == None:
            halt


    def setFlags(self, flags):
        self.flags = flags
        self.conn = (flags & F_CON != 0)
        self.deform = (flags & F_DEF != 0)
        self.restr = (flags & F_RES != 0)
        self.wire = (flags & F_WIR != 0)
        self.lloc = (flags & F_NOLOC == 0)
        self.lock = (flags & F_LOCK != 0)
        self.cyc = (flags & F_NOCYC == 0)
        self.hide = (flags & F_HID)
        self.norot = (flags & F_NOROT)
        self.scale = (flags & F_SCALE)


    def setBone(self, head, tail):
        self.head = head
        self.tail = tail
        vec = tail - head
        self.length = math.sqrt(np.dot(vec,vec))

        if isinstance(self.roll, str):
            if self.roll[0:5] == "Plane":
                normal = m2b(self.armature.parser.normals[self.roll])
                self.roll = computeRoll(self.head, self.tail, normal, bone=self)


    def rescale(self, scale):
        self.head = scale*self.head
        self.tail = scale*self.tail
        self.length = scale*self.length

        self.matrixRest = None
        self.matrixRelative = None
        self.matrixTPose = None


    def rename(self, locale, newbones):
        amt = self.armature
        self.name = renameBone(self, locale)
        if self.parent:
            self.parent = renameBone(amt.bones[self.parent], locale)
        for cns in self.constraints:
            if cns.type in ["Transform", "StretchTo", "TrackTo", "IK", "CopyTrans"]:
                cns.subtar = renameBone(amt.bones[cns.subtar], locale)
        newbones[self.name] = self


    def calcRestMatrix(self):
        if self.matrixRest is not None:
            return

        _,self.matrixRest = getMatrix(self.head, self.tail, self.roll)

        if self.parent:
            parbone = self.armature.bones[self.parent]
            self.matrixRelative = np.dot(la.inv(parbone.matrixRest), self.matrixRest)
        else:
            self.matrixRelative = self.matrixRest


    def _getTPoseMatrix(self):
        tposes = self.armature._getTPoses()
        try:
            tmat = tposes[self.origName]
        except KeyError:
            tmat = _Identity

        self.calcRestMatrix()
        if self.parent:
            parbone = self.armature.bones[self.parent]
            self.matrixTPose = np.dot(parbone.matrixTPose, np.dot(self.matrixRelative, tmat))
        else:
            self.matrixTPose = np.dot(self.matrixRest, tmat)

        return self.matrixTPose


    def _getRestOrTPoseMat(self, config):
        if config.useTPose:
            return self._getTPoseMatrix()
        else:
            return self.matrixRest


    def getRestMatrix(self, config):
        self.calcRestMatrix()
        return transformBoneMatrix(self.matrixRest, config)


    def getRestOrTPoseMatrix(self, config):
        self.calcRestMatrix()
        mat = self._getRestOrTPoseMat(config)
        return transformBoneMatrix(mat, config)


    def getRelativeMatrix(self, config):
        restmat = self.getRestMatrix(config)
        #restmat = self.getRestOrTPoseMatrix(config)

        if self.parent:
            parent = self.armature.bones[self.parent]
            parmat = parent.getRestMatrix(config)
            return np.dot(la.inv(parmat), restmat)
        else:
            return restmat


    def getBindMatrix(self, config):
        self.calcRestMatrix()
        restmat = subtractOffset(self.matrixRest, config)
        bindinv = np.transpose(restmat)
        bindmat = la.inv(bindinv)
        return bindmat,bindinv


#-------------------------------------------------------------------------------
#   Global variables and utilities
#-------------------------------------------------------------------------------

_Identity = np.identity(4, float)
_RotX = tm.rotation_matrix(math.pi/2, (1,0,0))
_RotY = tm.rotation_matrix(math.pi/2, (0,1,0))
_RotNegX = tm.rotation_matrix(-math.pi/2, (1,0,0))
_RotZ = tm.rotation_matrix(math.pi/2, (0,0,1))
_RotZUpFaceX = np.dot(_RotZ, _RotX)
_RotXY = np.dot(_RotNegX, _RotY)


def subtractOffset(mat, config):
    mat = mat.copy()
    mat[:3,3] -= config.scale*config.offset
    return mat


def transformBoneMatrix(mat, config):

    mat = subtractOffset(mat, config)

    if config.yUpFaceZ:
        rot = _Identity
    elif config.yUpFaceX:
        rot = _RotY
    elif config.zUpFaceNegY:
        rot = _RotX
    elif config.zUpFaceX:
        rot = _RotZUpFaceX

    if config.localY:
        # Y along self, X bend
        return np.dot(rot, mat)

    elif config.localX:
        # X along self, Y bend
        return np.dot(rot, np.dot(mat, _RotXY) )

    elif config.localG:
        # Global coordinate system
        tmat = np.identity(4, float)
        tmat[:,3] = np.dot(rot, mat[:,3])
        return tmat


def renameBone(self, locale):
    if locale:
        return locale.rename(self.name)
    else:
        return self.origName





