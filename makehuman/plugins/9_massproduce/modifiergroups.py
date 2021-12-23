#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

MACROGROUPS = dict()
MACROGROUPS["age"] = ["macrodetails/Age"]
MACROGROUPS["height"] = ["macrodetails-height/Height"]
MACROGROUPS["weight"] = ["macrodetails-universal/Weight"]
MACROGROUPS["muscle"] = ["macrodetails-universal/Muscle"]
MACROGROUPS["gender"] = ["macrodetails/Gender"]
MACROGROUPS["proportion"] = ["macrodetails-proportions/BodyProportions"]
MACROGROUPS["ethnicity"] = ["macrodetails/African", "macrodetails/Asian", "macrodetails/Caucasian"]

from core import G
mhapi = G.app.mhapi

class _ModifierInfo():

    def __init__(self):

        self.human = mhapi.internals.getHuman()
        self.nonMacroModifierGroupNames = []
        self.modifierInfo = dict()

        for modgroup in self.human.modifierGroups:
            #print("MODIFIER GROUP: " + modgroup)
            if not "macro" in modgroup and not "genitals" in modgroup and not "armslegs" in modgroup:
                self.nonMacroModifierGroupNames.append(modgroup)
                self.modifierInfo[modgroup] = []
                for mod in self.human.getModifiersByGroup(modgroup):
                    if not mod.name.startswith("r-"):
                        self.modifierInfo[modgroup].append(self._deduceModifierInfo(modgroup, mod))

        self.nonMacroModifierGroupNames.append("arms")
        self.modifierInfo["arms"] = []

        self.nonMacroModifierGroupNames.append("hands")
        self.modifierInfo["hands"] = []

        self.nonMacroModifierGroupNames.append("legs")
        self.modifierInfo["legs"] = []

        self.nonMacroModifierGroupNames.append("feet")
        self.modifierInfo["feet"] = []

        for mod in self.human.getModifiersByGroup("armslegs"):
            name = mod.name
            if not name.startswith("r-"):
                if "hand" in name:
                    self.modifierInfo["hands"].append(self._deduceModifierInfo("hands", mod))
                if "foot" in name or "feet" in name:
                    self.modifierInfo["feet"].append(self._deduceModifierInfo("feet", mod))
                if "arm" in name:
                    self.modifierInfo["arms"].append(self._deduceModifierInfo("arms", mod))
                if "leg" in name:
                    self.modifierInfo["legs"].append(self._deduceModifierInfo("legs", mod))

        self.nonMacroModifierGroupNames.sort()

    def _deduceModifierInfo(self,groupName,modifier):
        modi = dict()
        modi["modifier"] = modifier
        modi["name"] = modifier.name
        modi["actualGroupName"] = modifier.groupName
        modi["groupName"] = groupName
        # This is the value set at the point when the user starts producing,
        # rather than makehuman's standard default value
        modi["defaultValue"] = modifier.getValue()
        modi["twosided"] = modifier.getMin() < -0.05
        modi["leftright"] = modifier.name.startswith('l-')
        return modi

    def getModifierGroupNames(self):
        return list(self.nonMacroModifierGroupNames)

    def getModifierInfoForGroup(self, groupName):
        return list(self.modifierInfo[groupName])

_mfinstance = None

def ModifierInfo():
    global _mfinstance
    if _mfinstance is None:
        _mfinstance = _ModifierInfo()
    return _mfinstance
