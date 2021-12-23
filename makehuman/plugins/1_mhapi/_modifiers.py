#!/usr/bin/python

from .namespace import NameSpace

import mh
import humanmodifier
import material
import gui
import gui3d
import log
import os
import algos3d
import events3d
from core import G
from codecs import open

class Modifiers(NameSpace):
    """This namespace wraps calls concerning modifiers and targets."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.human = api.internals.getHuman()
        self.trace()

    def _threadSafeApplyAllTargets(self):
        algos3d.resetObj(self.human.meshData)
        for (targetPath, morphFactor) in self.human.targetsDetailStack.items():
            algos3d.loadTranslationTarget(self.human.meshData, targetPath, morphFactor, None, 0, 0)
        self.human._updateOriginalMeshCoords(self.human.meshData.name, self.human.meshData.coord)
        self.human.updateProxyMesh()
        self.human.callEvent('onChanged', events3d.HumanEvent(self.human, 'targets'))
        self.human.refreshStaticMeshes()
        if self.human.isSubdivided():
            self.human.updateSubdivisionMesh()
            self.human.mesh.calcNormals()
            self.human.mesh.update()
        else:
            self.human.meshData.calcNormals(1, 1)
            self.human.meshData.update()
        pass

    def applyModifier(self, modifierName, power, assumeThreading = False):
        modifier = self.human.getModifier(modifierName)
        modifier.setValue(power)
        if assumeThreading:
            self._threadSafeApplyAllTargets()
        else:
            self.human.applyAllTargets()
        mh.redraw()

    def applyTarget(self,targetName,power, assumeThreading = False):
        self.human.setDetail(mh.getSysDataPath("targets/" + targetName + ".target"), power)
        if assumeThreading:
            self._threadSafeApplyAllTargets()
        else:
            self.human.applyAllTargets()
        mh.redraw()

    def getAppliedTargets(self):
        targets = dict()
        for target in self.human.targetsDetailStack.keys():
            paths = target.split('/data/targets/')
            targets[paths[1]] = self.human.targetsDetailStack[target]
        return targets

    def setAge(self,age):
        self.human.setAge(age)
        mh.redraw()

    def setWeight(self,weight):
        self.human.setWeight(weight)
        mh.redraw()

    def setMuscle(self,muscle):
        self.human.setMuscle(muscle)
        mh.redraw()

    def setHeight(self,height):
        self.human.setHeight(height)
        mh.redraw()

    def setGender(self,gender):
        self.human.setGender(gender)
        mh.redraw()

    def getAvailableModifierNames(self):
        return sorted( self.human.getModifierNames() )

    def applySymmetryLeft(self):
        self.human.applySymmetryLeft()

    def applySymmetryRight(self):
        self.human.applySymmetryRight()



