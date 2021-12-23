#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import gui3d
import gui
from core import G
from .modifiergroups import ModifierInfo
import re
import material

from .randomizeaction import RandomizeAction
from .modifiergroups import MACROGROUPS

mhapi = gui3d.app.mhapi

from PyQt5.QtWidgets import *

import pprint
pp = pprint.PrettyPrinter(indent=4)

class HumanState():

    def __init__(self, settings = None):

        self.settings = settings
        self.human = G.app.selectedHuman
        self.macroModifierValues = dict()
        self.appliedTargets = dict(self.human.targetsDetailStack)

        self.skin = material.Material().copyFrom(self.human.material)
        self.hair = mhapi.assets.getEquippedHair()
        self.eyebrows = mhapi.assets.getEquippedEyebrows()
        self.eyelashes = mhapi.assets.getEquippedEyelashes()
        self.clothes = mhapi.assets.getEquippedClothes()

        self._fillMacroModifierValues()

        self.modifierInfo = ModifierInfo()

        if not settings is None:
            self._randomizeMacros()
            if settings.getValue("materials", "randomizeSkinMaterials"):
                self._randomizeSkin()
            self._randomizeProxies()
            self._randomizeDetails()

    def _fillMacroModifierValues(self):
        for group in MACROGROUPS.keys():
            for n in MACROGROUPS[group]:
                mod = self.human.getModifier(n)
                v = mod.getValue()
                self.macroModifierValues[n] = v

    def _randomizeOneSidedMaxMin(self, valuesHash, modifierList, maximumValue, minimumValue):

        max = maximumValue
        min = minimumValue

        if(min > max):
            min = maximumValue
            max = minimumValue

        avg = (max - min) / 2.0

        for name in modifierList:
            val = self.getRandomValue(min, max)
            valuesHash[name] = val

    def _pickOne(self, valuesHash, modifierList):
        for n in modifierList:
            valuesHash[n] = 0.0
        num = len(modifierList)
        pickedVal = random.randrange(num)
        pickedName = modifierList[pickedVal]
        valuesHash[pickedName] = 1.0

    def _pickOneFromArray(self, values):
        num = len(values)
        pickedVal = random.randrange(num)
        return values[pickedVal]

    def _dichotomous(self, valuesHash, modifierList):
        for n in modifierList:
            valuesHash[n] = float(random.randrange(2))

    def _randomizeModifierGroup(self, modifierGroup, debug=False):
        if debug:
            print("RANDOMIZING " + modifierGroup)
        mfi = self.modifierInfo.getModifierInfoForGroup(modifierGroup)
        maxdev = self.settings.getValue("modeling","maxdev")
        for mi in mfi:
            print(mi)
            modifier = mi["modifier"]
            default = float(mi["defaultValue"])
            twosided = mi["twosided"]

            min = default - maxdev
            max = default + maxdev
            newval = self.getNormalRandomValue(min, max, default)

            if debug:
                print("DEFAULT: " + str(default))
                print("MAXDEV: " + str(maxdev))
                print("MIN: " + str(min))
                print("MAX: " + str(max))
                print("NEWVAL: " + str(newval))

            if newval > 1.0:
                newval = 1.0

            if twosided:
                if newval < -1.0:
                    newval = -1.0
            else:
                if newval < 0.0:
                    newval = 0.0

            modifier.setValue(newval)

            if debug:
                print("SETTING " + str(modifier) + " to " + str(newval))

            if mi["leftright"]:
                sname = modifier.getSymmetricOpposite()
                smod = self.human.getModifier(sname)
                smod.setValue(newval)


    def _randomizeDetails(self):
        names = self.settings.getNames("modeling")
        nondetail = ["maxdev","symmetry"]
        for name in names:
            if not name in nondetail and self.settings.getValue("modeling",name):
                if name == "breast":
                    self._randomizeBreasts()
                else:
                    self._randomizeModifierGroup(name)

    def _randomizeBreasts(self):
        if self._getCurrentGender() == "female":
            self._randomizeModifierGroup("breast",False)

    def _randomizeMacros(self):

        if self.settings.getValue("macro","randomizeAge"):
            min = self.settings.getValue("macro", "ageMinimum")
            max = self.settings.getValue("macro", "ageMaximum")
            self._randomizeOneSidedMaxMin(self.macroModifierValues, MACROGROUPS["age"], min, max)

        if self.settings.getValue("macro", "randomizeWeight"):
            min = self.settings.getValue("macro", "weightMinimum")
            max = self.settings.getValue("macro", "weightMaximum")
            self._randomizeOneSidedMaxMin(self.macroModifierValues, MACROGROUPS["weight"], min, max)

        if self.settings.getValue("macro", "randomizeHeight"):
            min = self.settings.getValue("macro", "heightMinimum")
            max = self.settings.getValue("macro", "heightMaximum")
            self._randomizeOneSidedMaxMin(self.macroModifierValues, MACROGROUPS["height"], min, max)

        if self.settings.getValue("macro", "randomizeMuscle"):
            min = self.settings.getValue("macro", "muscleMinimum")
            max = self.settings.getValue("macro", "muscleMaximum")
            self._randomizeOneSidedMaxMin(self.macroModifierValues, MACROGROUPS["muscle"], min, max)

        if self.settings.getValue("macro", "ethnicity"):
            if self.settings.getValue("macro", "ethnicityabsolute"):
                self._pickOne(self.macroModifierValues, MACROGROUPS["ethnicity"])
            else:
                self._randomizeOneSidedMaxMin(self.macroModifierValues, MACROGROUPS["ethnicity"], 0.0, 1.0)

        if self.settings.getValue("macro", "gender"):
            key = MACROGROUPS["gender"][0]
            if self.settings.getValue("macro", "genderabsolute"):
                self.macroModifierValues[key] = float(random.randrange(2))
            else:
                self.macroModifierValues[key] = random.random()

    def _getCurrentEthnicity(self):
        for ethn in MACROGROUPS["ethnicity"]:
            value = self.macroModifierValues[ethn]
            name = ethn.split("/")[1].lower()
            if value > 0.9:
                return name
        return "mixed"

    def _getCurrentGender(self):
        key = MACROGROUPS["gender"][0]
        value = self.macroModifierValues[key]
        gender = "mixed"

        if value < 0.3:
            gender = "female"
        if value > 0.7:
            gender = "male"

        return gender

    def _findSkinForEthnicityAndGender(self,ethnicity,gender):

        skinHash = None
        if gender == "female":
            category = "allowedFemaleSkins"
        else:
            category = "allowedMaleSkins"

        matchingSkins = []
        for name in self.settings.getNames(category):
            skin = self.settings.getValueHash(category, name)
            if skin[ethnicity]:
                matchingSkins.append(skin["fullPath"])

        pick = random.randrange(len(matchingSkins))
        self.skin = material.fromFile(matchingSkins[pick])

    def _randomizeSkin(self):

        gender = self._getCurrentGender()
        ethnicity = self._getCurrentEthnicity()

        self._findSkinForEthnicityAndGender(ethnicity,gender)

    def _findHairForGender(self, gender):

        hairNames = self.settings.getNames("allowedHair")
        allowedHair = []
        for hairName in hairNames:
            allowed = self.settings.getValue("allowedHair", hairName, gender)
            if allowed:
                allowedHair.append(hairName)

        pick = random.randrange(len(allowedHair))
        return self.settings.getValue("allowedHair",allowedHair[pick],"fullPath")

    def _randomizeHair(self):
        gender = self._getCurrentGender()
        fullPath = self._findHairForGender(gender)
        self.hair = fullPath

    def _findEyebrowsForGender(self, gender):

        eyebrowsNames = self.settings.getNames("allowedEyebrows")
        allowedEyebrows = []
        for eyebrowsName in eyebrowsNames:
            allowed = self.settings.getValue("allowedEyebrows", eyebrowsName, gender)
            if allowed:
                allowedEyebrows.append(eyebrowsName)

        pick = random.randrange(len(allowedEyebrows))
        return self.settings.getValue("allowedEyebrows",allowedEyebrows[pick],"fullPath")

    def _randomizeEyebrows(self):
        gender = self._getCurrentGender()
        fullPath = self._findEyebrowsForGender(gender)
        self.eyebrows = fullPath


    def _findEyelashesForGender(self, gender):

        eyelashesNames = self.settings.getNames("allowedEyelashes")
        allowedEyelashes = []
        for eyelashesName in eyelashesNames:
            allowed = self.settings.getValue("allowedEyelashes", eyelashesName, gender)
            if allowed:
                allowedEyelashes.append(eyelashesName)

        pick = random.randrange(len(allowedEyelashes))
        return self.settings.getValue("allowedEyelashes",allowedEyelashes[pick],"fullPath")

    def _randomizeEyelashes(self):
        gender = self._getCurrentGender()
        fullPath = self._findEyelashesForGender(gender)
        self.eyelashes = fullPath

    def _getAllowedClothesForPartAndGender(self,part,gender):

        gender = gender.lower()
        part = part.lower().capitalize()

        if "shoes" not in part.lower():
            part = part + "Clothes"

        setName = "allowed" + part
        allNames = list(self.settings.getNames(setName))

        allowedPaths = []
        for name in allNames:
            if self.settings.getValue(setName,name,gender):
                allowedPaths.append(self.settings.getValue(setName,name,"fullPath"))
        return allowedPaths

    def _randomizeFullClothes(self):
        allowed = self._getAllowedClothesForPartAndGender("full", self._getCurrentGender())
        picked = self._pickOneFromArray(allowed)
        self.clothes.append(picked)

    def _randomizeUpperClothes(self):
        allowed = self._getAllowedClothesForPartAndGender("upper", self._getCurrentGender())
        picked = self._pickOneFromArray(allowed)
        self.clothes.append(picked)

    def _randomizeLowerClothes(self):
        allowed = self._getAllowedClothesForPartAndGender("lower", self._getCurrentGender())
        picked = self._pickOneFromArray(allowed)
        self.clothes.append(picked)

    def _randomizeShoes(self):
        allowed = self._getAllowedClothesForPartAndGender("shoes", self._getCurrentGender())
        picked = self._pickOneFromArray(allowed)
        self.clothes.append(picked)

    def _randomizeProxies(self):
        if self.settings.getValue("proxies","hair"):
            self._randomizeHair()
        if self.settings.getValue("proxies","eyebrows"):
            self._randomizeEyebrows()
        if self.settings.getValue("proxies","eyelashes"):
            self._randomizeEyelashes()

        for k in ["fullClothes","upperClothes","lowerClothes","shoes"]:
            if self.settings.getValue("proxies",k):
                self.clothes = []

        if self.settings.getValue("proxies","fullClothes"):
            self._randomizeFullClothes()

        if self.settings.getValue("proxies","upperClothes"):
            self._randomizeUpperClothes()

        if self.settings.getValue("proxies","lowerClothes"):
            self._randomizeLowerClothes()

        if self.settings.getValue("proxies","shoes"):
            self._randomizeShoes()

    def equipClothes(self):
        mhapi.assets.unequipAllClothes()
        for c in self.clothes:
            mhapi.assets.equipClothes(c)

    def applyState(self, assumeBodyReset=False):

        self._applyMacroModifiers()
        if assumeBodyReset:
            self.human.targetsDetailStack = self.appliedTargets
        self.human.material = self.skin
        mhapi.assets.equipHair(self.hair)
        mhapi.assets.equipEyebrows(self.eyebrows)
        mhapi.assets.equipEyelashes(self.eyelashes)

        mhapi.modifiers._threadSafeApplyAllTargets()

        self.equipClothes()

    def _applyMacroModifiers(self):
        for group in MACROGROUPS.keys():
            for n in MACROGROUPS[group]:
                mod = self.human.getModifier(n)
                v = self.macroModifierValues[n]
                mod.setValue(v)

    def getRandomValue(self, minValue, maxValue):
        size = maxValue - minValue
        val = random.random() * size
        return minValue + val

    def getNormalRandomValue(self, minValue, maxValue, middleValue, sigmaFactor=0.2):
        rangeWidth = float(abs(maxValue - minValue))
        sigma = sigmaFactor * rangeWidth
        randomVal = random.gauss(middleValue, sigma)
        if randomVal < minValue:
            randomVal = minValue + abs(randomVal - minValue)
        elif randomVal > maxValue:
            randomVal = maxValue - abs(randomVal - maxValue)
        return max(minValue, min(randomVal, maxValue))


