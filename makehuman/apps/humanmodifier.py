#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers, Glynn Clements, Jonas Hauquier

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

class ModifierAction(guicommon.Action):
    def __init__(self, modifier, before, after, postAction):
        super(ModifierAction, self).__init__('Change modifier')
        self.human = modifier.human
        self.modifier = modifier
        self.before = before
        self.after = after
        self.postAction = postAction

    def do(self):
        if self.after is None:
            # Reset modifier to default value, store old values of other modifiers
            # possibly involved
            self.before = self.modifier.resetValue()
        else:
            self.modifier.setValue(self.after)

        # Handle symmetry
        if self.human.symmetryModeEnabled and self.modifier.getSymmetricOpposite():
            opposite = self.human.getModifier( self.modifier.getSymmetricOpposite() )
            if self.after is None:
                # Reset modifier to default value
                oldV = opposite.resetValue()
                if isinstance(oldV, dict):
                    self.before.update(oldV)
            else:
                opposite.setValue( self.modifier.getValue() )

        self.human.applyAllTargets()
        self.postAction()
        return True

    def undo(self):
        if isinstance(self.before, dict):
            # Undo reset of multiple modifiers
            for mName, mVal in self.before.items():
                self.human.getModifier(mName).setValue(mVal)
        else:
            self.modifier.setValue(self.before)

            # Handle symmetry
            if self.human.symmetryModeEnabled and self.modifier.getSymmetricOpposite():
                opposite = self.human.getModifier( self.modifier.getSymmetricOpposite() )
                opposite.setValue( self.modifier.getValue() )

        self.human.applyAllTargets()
        self.postAction()
        return True


class Modifier(object):
    """
    The most basic modifier. All modifiers should inherit from this, directly or
    indirectly.
    A modifier manages a set of targets applied with a certain weight that
    influence the human model.
    """

    def __init__(self, groupName, name):
        self.groupName = groupName.replace('/', '-')
        self.name = name.replace('/', '-')

        self._symmSide = 0
        self._symmModifier = None
        self.verts = None
        self.faces = None
        self.eventType = 'modifier'
        self.targets = []
        self.description = ""

        # Macro variable controlled by this modifier
        self.macroVariable = None
        # Macro variables on which the targets controlled by this modifier depend
        self.macroDependencies = []

        self._defaultValue = 0

        self.human = None

    def setHuman(self, human):
        self.human = human
        human.addModifier(self)

    @property
    def fullName(self):
        return self.groupName+"/"+self.name

    def getMin(self):
        return 0.0

    def getMax(self):
        return 1.0

    def setValue(self, value, skipDependencies=False):
        value = self.clampValue(value)
        factors = self.getFactors(value)

        tWeights = getTargetWeights(self.targets, factors, value)
        for tpath, tWeight in tWeights.items():
            self.human.setDetail(tpath, tWeight)

        if skipDependencies:
            return

        # Update dependent modifiers
        self.propagateUpdate(realtime = False)

    def resetValue(self):
        oldVal = self.getValue()
        self.setValue(self.getDefaultValue())
        return oldVal

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
            if self.human.isPosed():
                # Apply target with pose transformation
                animatedMesh = self.human
            else:
                animatedMesh = None
            algos3d.loadTranslationTarget(self.human.meshData, target[0], new - old, None, 0, 0, animatedMesh=animatedMesh)

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

    def getSymmetrySide(self):
        """
        The side this modifier takes in a symmetric pair of two modifiers.
        Returns 'l' for left, 'r' for right.
        Returns None if symmetry does not apply to this modifier.
        """
        if self._symmSide != 0:
            # Cache this const value for performance
            return self._symmSide

        path = self.name.split('-')
        if 'l' in path:
            self._symmSide = 'l'
        elif 'r' in path:
            self._symmSide = 'r'
        else:
            self._symmSide = None
            return self._symmSide

        self._symmModifier = '-'.join(['l' if p == 'r' else 'r' if p == 'l' else p for p in path])
        return self._symmSide

    def getSymmetricOpposite(self):
        """
        The name of the modifier symmetric to this one. None if there is no
        symmetric opposite of this modifier.
        """
        if self._symmSide == 0:
            # Cache const value for performance
            self.getSymmetrySide()
        if self._symmModifier:
            return self.groupName+"/"+self._symmModifier
        else:
            return None

    def getSimilar(self):
        """
        Retrieve the other modifiers of the same type on the human.
        """
        return [m for m in self.human.getModifiersByType(type(self)) if m != self]

    def isMacro(self):
        return self.macroVariable is not None

    def __str__(self):
        return "%s %s" % (type(self).__name__, self.fullName)

    def __repr__(self):
        return self.__str__()


class SimpleModifier(Modifier):
    """
    Simple modifier constructed from a path to a target file.
    """

    def __init__(self, groupName, basepath, targetpath):  #template):
        import os
        name = targetpath.replace('.target', '')
        name = name.replace('/', '-')
        name = name.replace('\\', '-')
        super(SimpleModifier, self).__init__(groupName, name)

        self.filename = os.path.join(basepath, targetpath)
        self.targets = self.expandTemplate([(self.filename, [])])

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

class ManagedTargetModifier(Modifier):
    """
    Modifier that uses the targets module for managing its targets.
    Abstract baseclass
    """

    def __init__(self, groupName, name):
        super(ManagedTargetModifier, self).__init__(groupName, name)

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

        try:
            targetsList = targets.getTargets().getTargetsByGroup(path)
        except KeyError:
            log.debug('missing target %s', path)
            targetsList = []

        result = []
        for component in targetsList:
            targetgroup = '-'.join(component.key)
            factordependencies = component.getVariables() + [targetgroup]
            result.append( (component.path, factordependencies) )

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

    def setValue(self, value, skipDependencies=False):
        value = self.clampValue(value)
        factors = self.getFactors(value)

        tWeights = getTargetWeights(self.targets, factors)
        for tpath, tWeight in tWeights.items():
            self.human.setDetail(tpath, tWeight)

        if skipDependencies:
            return

        # Update dependent modifiers
        self.propagateUpdate(realtime = False)

    def getValue(self):
        right = sum([self.human.getDetail(target[0]) for target in self.r_targets])
        if right:
            return right
        else:
            return -sum([self.human.getDetail(target[0]) for target in self.l_targets])

    _variables = targets._value_cat.keys()

    def getFactors(self, value):
        return dict((name, getattr(self.human, name + 'Val'))
                    for name in self._variables)

class UniversalModifier(ManagedTargetModifier):
    """
    Simple target-based modifier that controls 1, 2 or 3 targets, managed by
    the targets module.
    """
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

    def getMin(self):
        if self.left:
            return -1.0
        else:
            return 0.0

    def getFactors(self, value):
        factors = super(UniversalModifier, self).getFactors(value)

        if self.left is not None:
            factors[self.left] = -min(value, 0.0)
        if self.center is not None:
            factors[self.center] = 1.0 - abs(value)
        factors[self.right] = max(0.0, value)

        return factors

class MacroModifier(ManagedTargetModifier):
    """
    More complex modifier that controls many targets, managed by the targets
    module. Macro modifiers don't influence target weights directly, but instead
    control the value of macro variables on the human, which determine the final
    combination of the group of macro targets.
    Because macro modifiers don't control targets directly, it's possible to
    have many macro modifiers that control the same group of targets, but do so
    by influencing a different macro variable.
    """
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

class EthnicModifier(MacroModifier):
    """
    Specialisation of macro modifier to manage three closely connected modifiers
    whose total sum of values has to sum to 1.
    """
    def __init__(self, groupName, variable):
        super(EthnicModifier, self).__init__(groupName, variable)

        # We assume there to be only 3 ethnic modifiers
        self._defaultValue = 1.0/3

    def resetValue(self):
        """
        Resetting one ethnic modifier restores all ethnic modifiers to their
        default position.
        """
        _tmp = self.human.blockEthnicUpdates
        self.human.blockEthnicUpdates = True

        oldVals = {}
        oldVals[self.fullName] = self.getValue()
        self.setValue(self.getDefaultValue())
        for modifier in self.getSimilar():
            oldVals[modifier.fullName] = modifier.getValue()
            modifier.setValue(modifier.getDefaultValue())

        self.human.blockEthnicUpdates = _tmp
        return oldVals

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
        log.debug("    description: %s\n", m.description)

def loadModifiers(filename, human):
    """
    Load modifiers from a modifier definition file.
    """
    log.debug("Loading modifiers from %s", filename)
    import json
    import os
    from collections import OrderedDict
    modifiers = []
    lookup = OrderedDict()
    data = json.load(open(filename, 'rb'), object_pairs_hook=OrderedDict)
    for modifierGroup in data:
        groupName = modifierGroup['group']
        for mDef in modifierGroup['modifiers']:
            # Construct modifier
            if "modifierType" in mDef:
                modifierClass = globals()[ mDef["modifierType"] ]
            elif 'macrovar' in mDef:
                modifierClass = MacroModifier
            else:
                modifierClass = UniversalModifier

            if 'macrovar' in mDef:
                modifier = modifierClass(groupName, mDef['macrovar'])
                if not modifier.isMacro():
                    log.warning("Expected modifier %s to be a macro modifier, but identifies as a regular one. Check variable category definitions in targets.py" % modifier.fullName)
            else:
                modifier = modifierClass(groupName, mDef['target'], mDef.get('min',None), mDef.get('max',None), mDef.get('mid',None))

            if "defaultValue" in mDef:
                modifier._defaultValue = mDef["defaultValue"]

            modifiers.append(modifier)
            lookup[modifier.fullName] = modifier
    if human is not None:
        for modifier in modifiers:
            modifier.setHuman(human)
    log.message('Loaded %s modifiers from file %s', len(modifiers), filename)

    # Attempt to load modifier descriptions
    _tmp = os.path.splitext(filename)
    descFile = _tmp[0]+'_desc'+_tmp[1]
    hasDesc = OrderedDict([(key,False) for key in lookup.keys()])
    if os.path.isfile(descFile):
        data = json.load(open(descFile, 'rb'), object_pairs_hook=OrderedDict)
        dCount = 0
        for mName, mDesc in data.items():
            try:
                mod = lookup[mName]
                mod.description = mDesc
                dCount += 1
                hasDesc[mName] = True
            except:
                log.warning("Loaded description for %s but modifier does not exist!", mName)
        log.message("Loaded %s modifier descriptions from file %s", dCount, descFile)
    for mName, mHasDesc in hasDesc.items():
        if not mHasDesc:
            log.warning("No description defined for modifier %s!", mName)

    return modifiers

