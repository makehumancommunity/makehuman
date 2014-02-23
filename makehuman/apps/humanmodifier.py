#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers, Glynn Clements, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

__docformat__ = 'restructuredtext'

import algos3d
import guicommon
from core import G
import events3d
import operator
import numpy as np
import log
import targets


# Gender
# -
# female          1.0  0.5  1.0
# male            0.0  0.5  1.0

# Age
# -
# baby            1.0  0.0  0.0  0.0
# child           0.0  1.0  0.0  0.0
# young           0.0  0.0  1.0  0.0
# old             0.0  0.0  0.0  1.0

# Weight
# -
# light           1.0  0.0  0.0
# averageWeight   0.0  1.0  0.0
# heavy           0.0  0.0  1.0

# Muscle
# -
# flaccid         1.0  0.0  0.0
# averageTone     0.0  1.0  0.0
# muscle          0.0  0.0  1.0

# Height
# -
# dwarf           1.0  0.0  0.0
# giant           0.0  0.0  1.0

# BreastFirmness
# -
# firmness0       1.0  0.5  1.0
# firmness1       0.0  0.5  1.0

# BreastSize
# -
# cup1            1.0  0.0  0.0
# cup2            0.0  0.0  1.0

# African

# Asian

# Caucasian


# The modifier groups that have to be updated in realtime (during slider dragging)
# when a value they depend on changes. After dragged slider is released, all
# dependencies will be updated (this is a performance feature)
realtimeDependencyUpdates = ['macrodetails', 'macrodetails-universal']

class DetailAction(guicommon.Action):
    def __init__(self, human, before, after, update=True):
        super(DetailAction, self).__init__('Change detail')
        self.human = human
        self.before = before
        self.after = after
        self.update = update

    def do(self):
        for (target, value) in self.after.iteritems():
            self.human.setDetail(target, value)
        self.human.applyAllTargets(G.app.progress, update=self.update)
        return True

    def undo(self):
        for (target, value) in self.before.iteritems():
            self.human.setDetail(target, value)
        self.human.applyAllTargets()
        return True

class ModifierAction(guicommon.Action):
    def __init__(self, modifier, before, after, postAction):
        super(ModifierAction, self).__init__('Change modifier')
        self.human = modifier.human
        self.modifier = modifier
        self.before = before
        self.after = after
        self.postAction = postAction

    def do(self):
        self.modifier.setValue(self.after)
        self.human.applyAllTargets(G.app.progress)
        self.postAction()
        return True

    def undo(self):
        self.modifier.setValue(self.before)
        self.human.applyAllTargets(G.app.progress)
        self.postAction()
        return True

class BaseModifier(object):

    def __init__(self, groupName, name):
        self.groupName = groupName.replace('/', '-')
        self.name = name.replace('/', '-')

        self.verts = None
        self.faces = None
        self.eventType = 'modifier'
        self.targets = []

        # Macro variable controlled by this modifier
        self.macroVariable = None
        # Macro variables on which the targets controlled by this modifier depend
        self.macroDependencies = []

        self._defaultValue = 0

        self.human = None

    def setHuman(self, human):
        human.addModifier(self)
        self.human = human

    @property
    def fullName(self):
        return self.groupName+"/"+self.name

    def setValue(self, value, skipDependencies = False):
        value = self.clampValue(value)
        factors = self.getFactors(value)

        tWeights = getTargetWeights(self.targets, factors, value)
        for tpath, tWeight in tWeights.items():
            self.human.setDetail(tpath, tWeight)

        if skipDependencies:
            return

        # Update dependent modifiers
        self.propagateUpdate(realtime = False)

    def propagateUpdate(self, realtime = False):
        """
        Propagate modifier update to dependent modifiers
        """
        if realtime:
            f=realtimeDependencyUpdates
        else:
            f = None

        for dependentModifierGroup in self.human.getModifiersAffectedBy(self, filter = f):
            # Only updating one modifier in a group should suffice to update the
            # targets affected by the entire group.
            m = self.human.getModifiersByGroup(dependentModifierGroup)[0]
            if realtime:
                m.updateValue(m.getValue(), skipUpdate = True)
            else:
                m.setValue(m.getValue(), skipDependencies = True)

    def clampValue(self, value):
        raise NotImplementedError()

    def getFactors(self, value):
        raise NotImplementedError()

    def getValue(self):
        return sum([self.human.getDetail(target[0]) for target in self.targets])

    def getDefaultValue(self):
        return self._defaultValue

    def buildLists(self):
        # Collect vertex and face indices if we didn't yet
        if self.verts is None and self.faces is None:
            # Collect verts
            vmask = np.zeros(self.human.meshData.getVertexCount(), dtype=bool)
            for target in self.targets:
                t = algos3d.getTarget(self.human.meshData, target[0])
                vmask[t.verts] = True
            self.verts = np.argwhere(vmask)[...,0]
            del vmask

            # collect faces
            self.faces = self.human.meshData.getFacesForVertices(self.verts)

    def updateValue(self, value, updateNormals=1, skipUpdate=False):
        if self.verts is None and self.faces is None:
            self.buildLists()

        # Update detail state
        old_detail = [self.human.getDetail(target[0]) for target in self.targets]
        self.setValue(value, skipDependencies = True)
        new_detail = [self.human.getDetail(target[0]) for target in self.targets]

        # Apply changes
        for target, old, new in zip(self.targets, old_detail, new_detail):
            if new == old:
                continue
            algos3d.loadTranslationTarget(self.human.meshData, target[0], new - old, None, 0, 0)

        if skipUpdate:
            # Used for dependency updates (avoid dependency loops and double updates to human)
            return

        # Update dependent modifiers
        self.propagateUpdate(realtime = True)

        # Update vertices
        if updateNormals:
            self.human.meshData.calcNormals(1, 1, self.verts, self.faces)
        self.human.meshData.update()
        event = events3d.HumanEvent(self.human, self.eventType)
        event.modifier = self.fullName
        self.human.callEvent('onChanging', event)

    def __str__(self):
        return "%s %s" % (type(self).__name__, self.fullName)

    def __repr__(self):
        return self.__str__()

class Modifier(BaseModifier):
    # TODO what is the difference between this and UniversalModifier (this appears only used by the measurement plugin) -- might perhaps be useful for ad-hoc target applications, by directly specifying the file

    def __init__(self, left, right):
        lpath = Modifier.split_path(left)
        rpath = Modifier.split_path(right)
        common = Modifier.longest_subpath(lpath, rpath)
        lExt = '-'.join(lpath[len(common):])
        rExt = '-'.join(rpath[len(common):])
        name = '-'.join(common) + '-' + lExt + "|" + rExt

        super(Modifier, self).__init__("targetfile-modifier", name)

        #log.debug("Modifier(%s,%s)  :             %s", left, right, self.fullName)

        self.left = left
        self.right = right
        self.targets = [[self.left], [self.right]]

    @staticmethod
    def split_path(pathStr):
        pathStr = pathStr.replace('\\', '-')
        pathStr = pathStr.replace('/', '-')
        pathStr = pathStr.replace('.target', '')

        components = pathStr.split('-')
        return components

    @staticmethod
    def longest_subpath(p1, p2):
        """
        Longest common sequence of components of two paths starting at position 0.
        """
        subp = []
        for idx, component in enumerate(p1):
            if idx >= len(p2):
                return subp
            if component == p2[idx]:
                subp.append(component)
        return subp

    def setValue(self, value, skipDependencies = False):

        value = max(-1.0, min(1.0, value))

        left = -value if value < 0.0 else 0.0
        right = value if value > 0.0 else 0.0

        self.human.setDetail(self.left, left)
        self.human.setDetail(self.right, right)

        if skipDependencies:
            return

        # Update dependent modifiers
        self.propagateUpdate(realtime = False)

    def getValue(self):

        value = self.human.getDetail(self.left)
        if value:
            return -value
        value = self.human.getDetail(self.right)
        if value:
            return value
        else:
            return 0.0

class SimpleModifier(BaseModifier):
    # TODO do we need SimpleModifier and Modifier?

    def __init__(self, groupName, template):
        name = template.replace('.target', '')
        name = name.replace('/', '-')
        name = name.replace('\\', '-')
        super(SimpleModifier, self).__init__(groupName, name)
        self.template = template
        self.targets = self.expandTemplate([(self.template, [])])

        # TODO resolve macro dependencies as well?

        #log.debug("SimpleModifier(%s,%s)  :             %s", groupName, template, self.fullName)

    def expandTemplate(self, targets):

        targets = [(target[0], target[1] + ['dummy']) for target in targets]

        return targets

    def getFactors(self, value):
        # TODO this is useless
        factors = {
            'dummy': 1.0
        }

        return factors

    def clampValue(self, value):
        return max(0.0, min(1.0, value))

class GenericModifier(BaseModifier):
    def __init__(self, groupName, name):
        super(GenericModifier, self).__init__(groupName, name)

    @staticmethod
    def findTargets(path):
        """
        Retrieve a list of targets grouped under the specified target path
        (which is not directly a filesystem path but rather an abstraction
        with a path being a hierarchic string of atoms separated by a - symbol).

        The result is a list of tuples, with each tuple as: 
            (targetpath, factordependencies)
        With targetpath referencing the filepath of the .target file,
        and factordependencies a list with the names of variables or factors 
        that influence the weight with how much the target file is applied.
        The resulting weight with which a target is applied is the 
        multiplication of all the factor values declared in the 
        factorDependencies list.

        Some of these factordependencies come from predeclared macro parameters
        (such as age, race, weight, gender, ...) and are already supplied by the
        targets module which automatically extracts known parameters from the
        target path or filename.
        Additional factordependencies can be added at will to control the
        weighting of a target directly (for example to apply the value of this
        modifier to its targets).
        The other way of setting modifier values to factors to eventually set 
        the weight of targets (which is used by macro modifiers) is to make sure
        the xVal variables of the human object are updated, by calling 
        corresponding setters on the human object. getFactors() will by default
        resolve the values of known xVal variables to known factor variable 
        names.

        factordependencies can be any name and are not restricted to tokens that
        occur in the target path. Though for each factordependency, getFactors()
        will have to return a matching value.
        """
        if path is None:
            return []
        path = tuple(path.split('-'))
        result = []
        if path not in targets.getTargets().groups:
            log.debug('missing target %s', path)
        for target in targets.getTargets().groups.get(path, []):
            keys = [var
                    for var in target.data.itervalues()
                    if var is not None]
            keys.append('-'.join(target.key))
            result.append((target.path, keys))
        return result

    @staticmethod
    def findMacroDependencies(path):
        result = set()
        if path is None:
            return result
        path = tuple(path.split('-'))
        for target in targets.getTargets().groups.get(path, []):
            keys = [key
                    for key, var in target.data.iteritems()
                    if var is not None]
            result.update(keys)
        return result

    def clampValue(self, value):
        value = min(1.0, value)
        if self.left is not None:
            value = max(-1.0, value)
        else:
            value = max( 0.0, value)
        return value

    def setValue(self, value, skipDependencies = False):
        value = self.clampValue(value)
        factors = self.getFactors(value)

        tWeights = getTargetWeights(self.targets, factors)
        for tpath, tWeight in tWeights.items():
            self.human.setDetail(tpath, tWeight)

        if skipDependencies:
            return

        # Update dependent modifiers
        self.propagateUpdate(realtime = False)

    @staticmethod
    def parseTarget(target):
        return target[0].split('/')[-1].split('.')[0].split('-')

    def getValue(self):
        right = sum([self.human.getDetail(target[0]) for target in self.r_targets])
        if right:
            return right
        else:
            return -sum([self.human.getDetail(target[0]) for target in self.l_targets])

    _variables = targets._value_cat.keys()

    def getFactors(self, value):
        #print 'genericModifier: getFactors'
        return dict((name, getattr(self.human, name + 'Val'))
                    for name in self._variables)

class UniversalModifier(GenericModifier):
    def __init__(self, groupName, targetName, leftExt=None, rightExt=None, centerExt=None):
        self.targetName = groupName + "-" + targetName
        if leftExt and rightExt:
            self.left = self.targetName + "-" + leftExt
            self.right = self.targetName + "-" + rightExt

            if centerExt:
                self.center = self.targetName + "-" + centerExt

                self.targetName = self.targetName + "-" + leftExt + "|" + centerExt + "|" + rightExt
                name = targetName + "-" + leftExt + "|" + centerExt + "|" + rightExt
            else:
                self.center = None

                self.targetName = self.targetName + "-" + leftExt + "|" + rightExt
                name = targetName + "-" + leftExt + "|" + rightExt
        else:
            self.left = None
            self.right = self.targetName
            self.center = None
            name = targetName

        super(UniversalModifier, self).__init__(groupName, name)

        #log.debug("UniversalModifier(%s, %s, %s, %s)  :  %s", self.groupName, targetName, leftExt, rightExt, self.fullName)

        self.l_targets = self.findTargets(self.left)
        self.r_targets = self.findTargets(self.right)
        self.c_targets = self.findTargets(self.center)

        self.macroDependencies = self.findMacroDependencies(self.left)
        self.macroDependencies.update(self.findMacroDependencies(self.right))
        self.macroDependencies.update(self.findMacroDependencies(self.center))
        self.macroDependencies = list(self.macroDependencies)

        self.targets = self.l_targets + self.r_targets + self.c_targets

    def getFactors(self, value):
        #print "UniversalModifier factors:"
        factors = super(UniversalModifier, self).getFactors(value)

        if self.left is not None:
            factors[self.left] = -min(value, 0.0)
        if self.center is not None:
            factors[self.center] = 1.0 - abs(value)
        factors[self.right] = max(0.0, value)

        #print 'factors:'
        #print factors

        return factors

class MacroModifier(GenericModifier):
    def __init__(self, groupName, variable):
        super(MacroModifier, self).__init__(groupName, variable)
        self._defaultValue = 0.5

        #log.debug("MacroModifier(%s, %s)  :  %s", self.groupName, self.name, self.fullName)

        self.setter = 'set' + self.variable
        self.getter = 'get' + self.variable

        self.targets = self.findTargets(self.groupName)

        # log.debug('macro modifier %s.%s(%s): %s', base, name, variable, self.targets)

        self.macroDependencies = self.findMacroDependencies(self.groupName)
        var = self.getMacroVariable()
        if var:
            # Macro modifier is not dependent on variable it controls itself
            self.macroDependencies.remove(var)
        self.macroDependencies = list(self.macroDependencies)

        self.macroVariable = var

    @property
    def variable(self):
        return self.name

    def getMacroVariable(self):
        """
        The macro variable modified by this modifier.
        """
        if self.variable:
            var = self.variable.lower()
            if var in targets._categories:
                return var
            elif var in targets._value_cat:
                # necessary for caucasian, asian, african
                return targets._value_cat[var]
        return None

    def getValue(self):
        return getattr(self.human, self.getter)()

    def setValue(self, value, skipDependencies = False):
        value = self.clampValue(value)
        getattr(self.human, self.setter)(value, updateModifier=False)
        super(MacroModifier, self).setValue(value, skipDependencies)

    def clampValue(self, value):
        return max(0.0, min(1.0, value))

    def getFactors(self, value):
        factors = super(MacroModifier, self).getFactors(value)
        factors[self.groupName] = 1.0
        return factors

    def buildLists(self):
        pass

def getTargetWeights(targets, factors, value = 1.0, ignoreNotfound = False):
    result = dict()
    if ignoreNotfound:
        for (tpath, tfactors) in targets:
            result[tpath] = value * reduce(operator.mul, [factors.get(factor, 1.0) for factor in tfactors])
    else:
        for (tpath, tfactors) in targets:
            result[tpath] = value * reduce(operator.mul, [factors[factor] for factor in tfactors])
    return result


def debugModifiers():
    human = G.app.selectedHuman
    modifierNames = sorted(human.modifierNames)
    for mName in modifierNames:
        m = human.getModifier(mName)
        log.debug("%s:", m)
        log.debug("    controls: %s", m.macroVariable)
        log.debug("    dependencies (variables): %s", str(m.macroDependencies))
        log.debug("    dependencies (modifier groups): %s", str(list(human.getModifierDependencies(m))))
        log.debug("    influences (modifier groups): %s", str(list(human.getModifiersAffectedBy(m))))
        log.debug("\n")

