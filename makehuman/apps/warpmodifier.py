#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

__docformat__ = 'restructuredtext'

import numpy as np
from operator import mul
from getpath import getPath, getSysDataPath, canonicalPath, localPath
import os

import algos3d
import meshstat
import humanmodifier
import targets
import log
from core import G


debug = False

#----------------------------------------------------------
#   class WarpTarget
#----------------------------------------------------------

class WarpTarget(algos3d.Target):

    def __init__(self, name, vertIndices, vertData, modifier, human):
        self.name = name
        self.morphFactor = -1

        self.human = human
        self.modifier = modifier

        self.verts = vertIndices
        self.data = vertData

        self.faces = self.human.meshData.getFacesForVertices(self.verts)

    def apply(self, obj, morphFactor, faceGroupToUpdateName=None, update=1, calcNorm=1, scale=[1.0,1.0,1.0]):
        super(WarpTarget, self).apply(obj, morphFactor, faceGroupToUpdateName, update, calcNorm, scale)

    def __repr__(self):
        return ( "<WarpTarget %s>" % (self.name) )


#----------------------------------------------------------
#   class WarpModifier
#----------------------------------------------------------

class WarpModifier (humanmodifier.UniversalModifier):

    def __init__(self, groupName, targetName, bodypart, referenceVariables):
        super(WarpModifier, self).__init__(groupName, targetName)

        self.eventType = 'warp'
        self.bodypart = bodypart
        self.slider = None
        self.referenceVariables = referenceVariables

        self.nonfixedDependencies = list(self.macroDependencies)
        self.macroDependencies.extend(self.referenceVariables.keys())

        self.refTargetVerts = {}

    def setHuman(self, human):
        super(WarpModifier, self).setHuman(human)
        self.setupReferences()

    def setupReferences(self):
        self.referenceGroups = []

        # Gather all dependent targets
        groups = self.human.getModifierDependencies(self)
        targets = []
        for g in groups:
            m = self.human.getModifiersByGroup(g)[0]
            targets.extend(m.targets)
        factors = self.getFixedFactors().values()

        # Gather reference targets
        self.referenceTargets = []
        for tpath, tfactors in targets:
            # Reference targets are targets whose macro variables match the fixed variables for this warpmodifier
            # When all is correct, only the variables in self.nonfixedDependencies should still be free in this set of targets.
            if all([bool(f in tfactors) for f in factors]):
                self.referenceTargets.append( (tpath, tfactors) )

        self.refTargetPaths = {}
        self.refCharPaths = {}

    def getFixedFactors(self):
        """
        Get the macro variables for which this warpmodifier has no explicitly
        defined varieties of source warp targets. Instead those are the variables
        fixed to a certain value on which the source warp targets were modeled.
        These are the variables over which the actual warping will happen.

        Returns a dict of (var category, var name) tuples.
        """
        return self.referenceVariables

    def getDependentFactors(self, factors):
        """
        Get the macro variables for which this warpmodifier has varieties of
        source warp target files.

        Factors should either be a dict of (var category, var name) tuples, or
        should be a list with variable names.

        Returns either a dict of (var category, var name) tuples, when input was
        a dict, or a list.
        """
        if isinstance(factors, list):
            # Factors is a list of variable names
            return [f for f in factors if targets._value_cat.get(f, 'unknown') not in self.getFixedFactors()]
        else:
            # Factors is a dict of (macro variable category, variable name paris)
            return dict([(v,f) for v,f in factors.items() if v not in self.getFixedFactors()])

    # TODO add extended debug printing for warpmodifiers

    def setValue(self, value, skipDependencies = False):
        value = self.clampValue(value)

        if value != 0:
            self.compileTargetIfNecessary()

        self.human.setDetail(canonicalPath(self.fullName), value)

        #super(WarpModifier, self).setValue(value, skipDependencies)


    def updateValue(self, value, updateNormals=1, skipUpdate=False):
        if value == 0:
            return
        return  # TODO allow updating while dragging slider (but dont recompile warp targets while dragging)

        self.compileTargetIfNecessary()
        #super(WarpModifier, self).updateValue(value, updateNormals, skipUpdate)


    def clampValue(self, value):
        return max(0.0, min(1.0, value))

    def compileTargetIfNecessary(self):
        # TODO find out when compile is needed
        #if alreadyCompiled:
        #    return

        target = self.compileWarpTarget()
        algos3d._targetBuffer[canonicalPath(self.fullName)] = target    # TODO remove direct use of the target buffer?
        self.human.hasWarpTargets = True

        if debug:
            log.debug("DONE %s" % target)
        #self.human.traceStack()


    def compileWarpTarget(self):
        log.message("Compile warp target %s", self)
        srcTargetCoord, srcPoints, trgPoints = self.getReferences()
        if srcTargetCoord is not None:
            #shape = srcTargetCoord
            warpData = self._scaleTarget(srcTargetCoord, srcPoints, trgPoints)
        else:
            warpData = np.asarray([])

        # Maintain vertices with non-zero offset in warp target
        verts = np.unique(np.argwhere(warpData)[...,0])
        data = warpData[verts]

        target = WarpTarget(self.targetName, verts, data, self, self.human)
        return target


    def _scaleTarget(self, morph, srcPoints, trgPoints):
        scale = np.array((1.0,1.0,1.0))
        for n in range(3):
            tvec = trgPoints[2*n] - trgPoints[2*n+1]
            svec = srcPoints[2*n] - srcPoints[2*n+1]
            scale[n] = abs(tvec[n]/svec[n])
        if debug:
            log.debug("Scale %s" % scale)
        morph = scale*morph
        return morph


    def traceReference(self):
        log.debug("self.refCharPaths:")
        for key,value in self.refCharPaths.items():
            log.debug("  %s: %s" % (key, value))

    # Reference keypoints
    BodySizes = {
        "face" : [
            (5399, 11998, 1.4800),
            (791, 881, 2.3298),
            (962, 5320, 1.9221),
        ],
        "body" : [
            (13868, 14308, 9.6806),
            (881, 13137, 16.6551),
            (10854, 10981, 2.4356),
        ],
    }

    def getKeypoints(self):
        """
        Get landmark points used for warping
        """
        keypoints = []
        for n in range(3):
            keypoints += self.BodySizes[self.bodypart][n][0:2]
        return keypoints

    def getReferences(self):
        """
        Building source and target characters from scratch.
        The source character is the sum of reference characters.
        The target character is the sum of all non-warp targets.
        Cannot use human.getSeedMesh() which returns sum of all targets.
        """
        srcCharCoord = self.human.meshData.orig_coord.copy()
        trgCharCoord = srcCharCoord.copy()
        srcTargetCoord = np.zeros(srcCharCoord.shape, dtype=np.float32)

        keypoints = self.getKeypoints()
        trgPoints = np.zeros(6, float)
        srcPoints = np.zeros(6, float)


        # Traverse targets on stack
        for charpath,value in self.human.targetsDetailStack.items():
            if 'expression' in charpath:
                # TODO remove this stupid hack
                continue

            # The original target
            try:
                trgChar = algos3d.getTarget(self.human.meshData, charpath)
            except KeyError:
                continue    # Warp target? - ignore
            if isinstance(trgChar, WarpTarget):
                continue

            # TODO This is very wasteful, because we only need trgCharCoord and
            # srcCharCoord at the six keypoints

            srcVerts = np.s_[...]
            dstVerts = trgChar.verts[srcVerts]
            trgCharCoord[dstVerts] += value * trgChar.data[srcVerts]    # TODO replace with getting whole stack
        del charpath
        del value


        # The reference target (from reference variables)
        factors = self.getFactors(1.0)  # Calculate the fully applied warp target (weight = 1.0)
        factors = self.toReferenceFactors(factors)

        refTargets = self.referenceTargets
        tWeights = humanmodifier.getTargetWeights(refTargets, factors, ignoreNotfound = True)
        for tpath, tweight in tWeights.items():
            srcChar = algos3d.getTarget(self.human.meshData, tpath)
            dstVerts = srcChar.verts[srcVerts]
            srcCharCoord[dstVerts] += tweight * srcChar.data[srcVerts]


        # The warp target
        warpTargets = self.targets
        tWeights = humanmodifier.getTargetWeights(warpTargets, factors, ignoreNotfound = True)
        for tpath, tweight in tWeights.items():
            srcTrg = readTarget(tpath)
            addTargetVerts(srcTargetCoord, tweight, srcTrg)

        # Aggregate the keypoints differences
        trgPoints = trgCharCoord[keypoints]
        srcPoints = srcCharCoord[keypoints]
        return srcTargetCoord, srcPoints, trgPoints

    def toReferenceFactors(self, factors):
        vars_per_cat = dict()
        for (varName, varValue) in factors.items():
            varCateg = targets._value_cat.get(varName, 'unknown')
            if varCateg not in vars_per_cat:
                vars_per_cat[varCateg] = []
            vars_per_cat[varCateg].append(varName)

        result = dict()
        for (varCateg, varList) in vars_per_cat.items():
            if varCateg in self.getFixedFactors():
                # Replace fixed variables to reference target
                value = sum([factors[v] for v in varList])
                result[self.getFixedFactors()[varCateg]] = value
            else:
                for v in varList:
                    result[v] = factors[v]
        return result

#----------------------------------------------------------
#   Reset warp buffer
#----------------------------------------------------------

def resetWarpBuffer():
    human = G.app.selectedHuman
    if human.hasWarpTargets:
        if debug:
            log.debug("WARP RESET")
        for path,target in algos3d._targetBuffer.items():
            if isinstance(target, WarpTarget):
                if debug:
                    log.debug("  DEL %s" % path)
                human.setDetail(localPath(path), 0)
                del algos3d._targetBuffer[path]
        human.applyAllTargets()
        human.hasWarpTargets = False

#----------------------------------------------------------
#   Call from exporter
#----------------------------------------------------------

def compileWarpTarget(groupName, targetName, human, bodypart, referenceVariables):
    mod = WarpModifier(groupName, targetName, bodypart, referenceVariables)
    mod.setHuman(human)
    trg = mod.compileWarpTarget()
    return trg

#----------------------------------------------------------
#   Add verts
#----------------------------------------------------------

def addTargetVerts(targetVerts, value, target):
    dstVerts = target.verts[:]
    targetVerts[dstVerts] += value * target.data[:]

#----------------------------------------------------------
#   Read target
#----------------------------------------------------------

def readTarget(filepath):
    target = algos3d.getTarget(G.app.selectedHuman.meshData, filepath)
    if target is None:
        raise IOError("Can't find target %s" % filepath)

    return target
