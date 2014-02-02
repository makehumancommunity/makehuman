#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Manuel Bastioni, Marc Flerackers, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import numpy as np
import algos3d
import guicommon
from core import G
import os
import events3d
from getpath import getSysDataPath, canonicalPath
import log
import material

from makehuman import getBasemeshVersion, getShortVersion, getVersionStr, getVersion

class Human(guicommon.Object):

    def __init__(self, mesh, hairObj=None, eyesObj=None, genitalsObj=None):

        guicommon.Object.__init__(self, mesh)

        self.hasWarpTargets = False

        self.MIN_AGE = 1.0
        self.MAX_AGE = 90.0
        self.MID_AGE = 25.0

        self.mesh.setCameraProjection(0)
        self.mesh.setPickable(True)
        self.mesh.setShadeless(0)
        self.mesh.setCull(1)
        self.meshData = self.mesh

        self._staticFaceMask = None
        self.maskFaces()

        self._hairObj = hairObj
        self._hairProxy = None
        self._eyesObj = eyesObj
        self._eyesProxy = None
        self._genitalsObj = genitalsObj
        self._genitalsProxy = None
        self.eyebrowsObj = None
        self.eyebrowsProxy = None
        self.eyelashesObj = None
        self.eyelashesProxy = None
        self.teethObj = None
        self.teethProxy = None
        self.tongueObj = None
        self.tongueProxy = None

        self.clothesObjs = {}
        self.clothesProxies = {}

        self.targetsDetailStack = {}  # All details targets applied, with their values
        self.symmetryModeEnabled = False

        self.setDefaultValues()

        self.bodyZones = ['l-eye','r-eye', 'jaw', 'nose', 'mouth', 'head', 'neck', 'torso', 'hip', 'pelvis', 'r-upperarm', 'l-upperarm', 'r-lowerarm', 'l-lowerarm', 'l-hand',
                          'r-hand', 'r-upperleg', 'l-upperleg', 'r-lowerleg', 'l-lowerleg', 'l-foot', 'r-foot', 'ear']

        self.material = material.fromFile(getSysDataPath('skins/default.mhmat'))
        self._defaultMaterial = material.Material().copyFrom(self.material)

        self._modifiers = dict()
        self._modifier_varMapping = dict()              # Maps macro variable to the modifier group that modifies it
        self._modifier_dependencyMapping = dict()       # Maps a macro variable to all the modifiers that depend on it
        self._modifier_groups = dict()


    # TODO introduce better system for managing proxies, nothing done for clothes yet
    def setHairProxy(self, proxy):
        self._hairProxy = proxy
        event = events3d.HumanEvent(self, 'proxy')
        event.proxy = 'hair'
        self.callEvent('onChanged', event)
    def getHairProxy(self):
        return self._hairProxy

    hairProxy = property(getHairProxy, setHairProxy)

    def setHairObj(self, obj):
        self._hairObj = obj
        event = events3d.HumanEvent(self, 'proxyObj')
        event.obj = 'hair'
        self.callEvent('onChanged', event)
    def getHairObj(self):
        return self._hairObj

    hairObj = property(getHairObj, setHairObj)

    def setEyesProxy(self, proxy):
        self._eyesProxy = proxy
        event = events3d.HumanEvent(self, 'proxy')
        event.proxy = 'eyes'
        self.callEvent('onChanged', event)
    def getEyesProxy(self):
        return self._eyesProxy

    eyesProxy = property(getEyesProxy, setEyesProxy)

    def setEyesObj(self, obj):
        self._eyesObj = obj
        event = events3d.HumanEvent(self, 'proxyObj')
        event.obj = 'eyes'
        self.callEvent('onChanged', event)
    def getEyesObj(self):
        return self._eyesObj

    eyesObj = property(getEyesObj, setEyesObj)

    def setGenitalsProxy(self, proxy):
        self._genitalsProxy = proxy
        event = events3d.HumanEvent(self, 'proxy')
        event.proxy = 'genitals'
        self.callEvent('onChanged', event)
    def getGenitalsProxy(self):
        return self._genitalsProxy

    genitalsProxy = property(getGenitalsProxy, setGenitalsProxy)

    def setGenitalsObj(self, obj):
        self._genitalsObj = obj
        # TODO better to let proxy libraries emit these events instead of human
        event = events3d.HumanEvent(self, 'proxyObj')
        event.obj = 'genitals'
        self.callEvent('onChanged', event)
    def getGenitalsObj(self):
        return self._genitalsObj

    genitalsObj = property(getGenitalsObj, setGenitalsObj)


    def getFaceMask(self):
        """
        Get initial (static) face mask for the human basemesh that hides all
        the faces associated with helper geometry.
        """
        if self._staticFaceMask is not None:
            # Return cached copy for performance (this mask never changes anyway)
            return self._staticFaceMask

        mesh = self.meshData
        group_mask = np.ones(len(mesh._faceGroups), dtype=bool)
        for g in mesh._faceGroups:
            if g.name.startswith('joint-') or g.name.startswith('helper-'):
                group_mask[g.idx] = False
        face_mask = group_mask[mesh.group]
        self._staticFaceMask = face_mask

        return face_mask

    def maskFaces(self):
        self.meshData.changeFaceMask(self.getFaceMask())
        self.meshData.updateIndexBufferFaces()


    def traceStack(self, all=True):
        import warpmodifier
        log.debug("human.targetsDetailStack:")
        for path,value in self.targetsDetailStack.items():
            try:
                target = algos3d._targetBuffer[canonicalPath(path)]
            except KeyError:
                target = None
            if target is None:
                stars = " ??? "
            elif isinstance(target, warpmodifier.WarpTarget):
                stars = " *** "
            else:
                stars = " "
            if all or path[0:4] != "data":
                log.debug("  %s%s: %s" % (stars, path, value))

    def traceBuffer(self, all=True, vertsToList=0):
        import warpmodifier
        log.debug("algos3d.targetBuffer:")
        for path,target in algos3d._targetBuffer.items():
            if isinstance(target, warpmodifier.WarpTarget):
                stars = " *** "
            else:
                stars = " "
            if all or path[0:4] != "data":
                log.debug("  %s%s:%s %d" % (stars, path, target, vertsToList))
                for n,vn in enumerate(target.verts[0:vertsToList]):
                    log.debug("   %d : %s %s" % (vn, target.data[n], self.mesh.coord[vn]))

    # Proxy and object getters.
    # Returns only existing proxies

    def getProxyObjects(self):
        objs = []
        for obj in [
            self.hairObj,
            self.eyesObj,
            self.genitalsObj,
            self.eyebrowsObj,
            self.eyelashesObj,
            self.teethObj,
            self.tongueObj,
            ]:
            if obj != None:
                objs.append(obj)
        for obj in self.clothesObjs.values():
            objs.append(obj)
        return objs

    def getProxies(self, includeHumanProxy = True):
        proxies = []
        for pxy in [
            self.hairProxy,
            self.eyesProxy,
            self.genitalsProxy,
            self.eyebrowsProxy,
            self.eyelashesProxy,
            self.teethProxy,
            self.tongueProxy,
            ]:
            if pxy != None:
                proxies.append(pxy)
        if includeHumanProxy and self.proxy:
            proxies.append(self.proxy)
        for pxy in self.clothesProxies.values():
            proxies.append(pxy)
        return proxies

    def getProxiesAndObjects(self):
        pairs = []
        for pxy,obj in [
            (self.hairProxy, self.hairObj),
            (self.eyesProxy, self.eyesObj),
            (self.genitalsProxy, self.genitalsObj),
            (self.eyebrowsProxy, self.eyebrowsObj),
            (self.eyelashesProxy, self.eyelashesObj),
            (self.teethProxy, self.teethObj),
            (self.tongueProxy, self.tongueObj)]:
            if pxy != None and obj != None:
                pairs.append((pxy,obj))
        for uuid,pxy in self.clothesProxies.items():
            pairs.append((pxy, self.clothesObjs[uuid]))
        return pairs

    def getTypedSimpleProxiesAndObjects(self, ptype):
        ptype = ptype.capitalize()
        table = {
            'Hair' :     (self.hairProxy, self.hairObj),
            'Eyes' :     (self.eyesProxy, self.eyesObj),
            'Genitals' : (self.genitalsProxy, self.genitalsObj),
            'Eyebrows' : (self.eyebrowsProxy, self.eyebrowsObj),
            'Eyelashes': (self.eyelashesProxy, self.eyelashesObj),
            'Teeth':     (self.teethProxy, self.teethObj),
            'Tongue':    (self.tongueProxy, self.tongueObj),
            }
        try:
            return table[ptype]
        except KeyError:
            return None,None

    # Overriding hide and show to account for both human base and the hairs!

    def show(self):
        self.visible = True
        for obj in self.getProxyObjects():
            if obj:
                obj.show()
        self.setVisibility(True)
        self.callEvent('onShown', self)

    def hide(self):

        self.visible = False
        for obj in self.getProxyObjects():
            if obj:
                obj.hide()
        self.setVisibility(False)
        self.callEvent('onHidden', self)

    # Overriding methods to account for both hair and base object

    def setPosition(self, position):
        dv = [x-y for x, y in zip(position, self.getPosition())]
        guicommon.Object.setPosition(self, position)
        for obj in self.getProxyObjects():
            if obj:
                obj.setPosition([x+y for x, y in zip(obj.getPosition(), dv)])

        self.callEvent('onTranslated', self)

    def setRotation(self, rotation):
        guicommon.Object.setRotation(self, rotation)
        for obj in self.getProxyObjects():
            if obj:
                obj.setRotation(rotation)

        self.callEvent('onRotated', self)

    def setSolid(self, *args, **kwargs):
        guicommon.Object.setSolid(self, *args, **kwargs)
        for obj in self.getProxyObjects():
            if obj:
                obj.setSolid(*args, **kwargs)

    def setSubdivided(self, *args, **kwargs):
        if not guicommon.Object.setSubdivided(self, *args, **kwargs):
            return
        for obj in self.getProxyObjects():
            if obj:
                obj.setSubdivided(*args, **kwargs)
        self.callEvent('onChanged', events3d.HumanEvent(self, 'smooth'))

    def setGender(self, gender, updateModifier = True):
        """
        Sets the gender of the model. 0 is female, 1 is male.

        Parameters
        ----------

        amount:
            *float*. An amount, usually between 0 and 1, specifying how much
            of the attribute to apply.
        """
        if updateModifier:
            modifier = self.getModifier('macrodetails/Gender')
            modifier.setValue(gender)
            self.applyAllTargets()
            return

        gender = min(max(gender, 0.0), 1.0)
        if self.gender == gender:
            return
        self.gender = gender
        self._setGenderVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'gender'))

    def getGender(self):
        """
        The gender of this human as a float between 0 and 1.
        0 for completely female, 1 for fully male.
        """
        return self.gender

    def _setGenderVals(self):
        self.maleVal = self.gender
        self.femaleVal = 1 - self.gender

    def setAge(self, age, updateModifier = True):
        """
        Sets the age of the model. 0 for 0 years old, 1 is 70. To set a
        particular age in years, use the formula age_value = age_in_years / 70.

        Parameters
        ----------

        amount:
            *float*. An amount, usually between 0 and 1, specifying how much
            of the attribute to apply.
        """
        if updateModifier:
            modifier = self.getModifier('macrodetails/Age')
            modifier.setValue(age)
            self.applyAllTargets()
            return

        age = min(max(age, 0.0), 1.0)
        if self.age == age:
            return
        self.age = age
        self._setAgeVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'age'))

    def getAge(self):
        """
        Age of this human as a float between 0 and 1.
        """
        return self.age

    def getAgeYears(self):
        """
        Return the approximate age of the human in years.
        """
        if self.getAge() < 0.5:
            return self.MIN_AGE + ((self.MID_AGE - self.MIN_AGE) * 2) * self.getAge()
        else:
            return self.MID_AGE + ((self.MAX_AGE - self.MID_AGE) * 2) * (self.getAge() - 0.5)

    def setAgeYears(self, ageYears):
        """
        Set age in amount of years.
        """
        ageYears = float(ageYears)
        if ageYears < self.MIN_AGE or ageYears > self.MAX_AGE:
            raise RuntimeError("Invalid age specified, should be minimum %s and maximum %s." % (self.MIN_AGE, self.MAX_AGE))
        if ageYears < self.MID_AGE:
            age = (ageYears - self.MIN_AGE) / ((self.MID_AGE - self.MIN_AGE) * 2)
        else:
            age = ( (ageYears - self.MID_AGE) / ((self.MAX_AGE - self.MID_AGE) * 2) ) + 0.5
        self.setAge(age)

    def _setAgeVals(self):
        """
        New system (A8):
        ----------------

        1y       10y       25y            90y
        baby    child     young           old
        |---------|---------|--------------|
        0      0.1875      0.5             1  = age [0, 1]

        val ^     child young     old
          1 |baby\ / \ /   \    /
            |     \   \      /
            |    / \ / \  /    \ young
          0 ______________________________> age
               0  0.1875 0.5      1
        """
        if self.age < 0.5:
            self.oldVal = 0.0
            self.babyVal = max(0.0, 1 - self.age * 5.333)  # 1/0.1875 = 5.333
            self.youngVal = max(0.0, (self.age-0.1875) * 3.2) # 1/(0.5-0.1875) = 3.2
            self.childVal = max(0.0, min(1.0, 5.333 * self.age) - self.youngVal)
        else:
            self.childVal = 0.0
            self.babyVal = 0.0
            self.oldVal = max(0.0, self.age * 2 - 1)
            self.youngVal = 1 - self.oldVal

    def setWeight(self, weight, updateModifier = True):
        """
        Sets the amount of weight of the model. 0 for underweight, 1 for heavy.

        Parameters
        ----------

        amount:
            *float*. An amount, usually between 0 and 1, specifying how much
            of the attribute to apply.
        """
        if updateModifier:
            modifier = self.getModifier('macrodetails-universal/Weight')
            modifier.setValue(weight)
            self.applyAllTargets()
            return

        weight = min(max(weight, 0.0), 1.0)
        if self.weight == weight:
            return
        self.weight = weight
        self._setWeightVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'weight'))

    def getWeight(self):
        return self.weight

    def _setWeightVals(self):
        self.maxweightVal = max(0.0, self.weight * 2 - 1)
        self.minweightVal = max(0.0, 1 - self.weight * 2)
        self.averageweightVal = 1 - (self.maxweightVal + self.minweightVal)

    def setMuscle(self, muscle, updateModifier = True):
        """
        Sets the amount of muscle of the model. 0 for flacid, 1 for muscular.

        Parameters
        ----------

        amount:
            *float*. An amount, usually between 0 and 1, specifying how much
            of the attribute to apply.
        """
        if updateModifier:
            modifier = self.getModifier('macrodetails-universal/Muscle')
            modifier.setValue(muscle)
            self.applyAllTargets()
            return

        muscle = min(max(muscle, 0.0), 1.0)
        if self.muscle == muscle:
            return
        self.muscle = muscle
        self._setMuscleVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'muscle'))

    def getMuscle(self):
        return self.muscle

    def _setMuscleVals(self):
        self.maxmuscleVal = max(0.0, self.muscle * 2 - 1)
        self.minmuscleVal = max(0.0, 1 - self.muscle * 2)
        self.averagemuscleVal = 1 - (self.maxmuscleVal + self.minmuscleVal)

    def setHeight(self, height, updateModifier = True):
        if updateModifier:
            modifier = self.getModifier('macrodetails-height/Height')
            modifier.setValue(height)
            self.applyAllTargets()
            return

        height = min(max(height, 0.0), 1.0)
        if self.height == height:
            return
        self.height = height
        self._setHeightVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'height'))

    def getHeight(self):
        return self.height

    def getHeightCm(self):
        """
        The height in cm.
        """
        bBox = self.getBoundingBox()
        return 10*(bBox[1][1]-bBox[0][1])

    def getBoundingBox(self):
        """
        Returns the bounding box of the basemesh without the helpers, ignoring
        any other facemask.
        """
        return self.meshData.calcBBox(fixedFaceMask = self.getFaceMask())

    def _setHeightVals(self):
        self.maxheightVal = max(0.0, self.height * 2 - 1)
        self.minheightVal = max(0.0, 1 - self.height * 2)
        if self.maxheightVal > self.minheightVal:
            self.averageheightVal = 1 - self.maxheightVal
        else:
            self.averageheightVal = 1 - self.minheightVal

    def setBreastSize(self, size, updateModifier = True):
        if updateModifier:
            modifier = self.getModifier('breast/BreastSize')
            modifier.setValue(size)
            self.applyAllTargets()
            return

        size = min(max(size, 0.0), 1.0)
        if self.breastSize == size:
            return
        self.breastSize = size
        self._setBreastSizeVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'breastSize'))

    def getBreastSize(self):
        return self.breastSize

    def _setBreastSizeVals(self):
        self.maxcupVal = max(0.0, self.breastSize * 2 - 1)
        self.mincupVal = max(0.0, 1 - self.breastSize * 2)
        if self.maxcupVal > self.mincupVal:
            self.averagecupVal = 1 - self.maxcupVal
        else:
            self.averagecupVal = 1 - self.mincupVal

    def setBreastFirmness(self, firmness, updateModifier = True):
        if updateModifier:
            modifier = self.getModifier('breast/BreastFirmness')
            modifier.setValue(firmness)
            self.applyAllTargets()
            return

        firmness = min(max(firmness, 0.0), 1.0)
        if self.breastFirmness == firmness:
            return
        self.breastFirmness = firmness
        self._setBreastFirmnessVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'breastFirmness'))

    def getBreastFirmness(self):
        return self.breastFirmness

    def _setBreastFirmnessVals(self):
        self.maxfirmnessVal = max(0.0, self.breastFirmness * 2 - 1)
        self.minfirmnessVal = max(0.0, 1 - self.breastFirmness * 2)

        if self.maxfirmnessVal > self.minfirmnessVal:
            self.averagefirmnessVal = 1 - self.maxfirmnessVal
        else:
            self.averagefirmnessVal = 1 - self.minfirmnessVal

    def setBodyProportions(self, proportion, updateModifier = True):
        if updateModifier:
            modifier = self.getModifier('macrodetails-proportions/BodyProportions')
            modifier.setValue(proportion)
            self.applyAllTargets()
            return

        proportion = min(1.0, max(0.0, proportion))
        if self.bodyProportions == proportion:
            return
        self.bodyProportions = proportion
        self._setBodyProportionVals()
        self.callEvent('onChanging', events3d.HumanEvent(self, 'bodyProportions'))

    def _setBodyProportionVals(self):
        self.idealproportionsVal = max(0.0, self.bodyProportions * 2 - 1)
        self.uncommonproportionsVal = max(0.0, 1 - self.bodyProportions * 2)

        if self.idealproportionsVal > self.uncommonproportionsVal:
            self.regularproportionsVal = 1 - self.idealproportionsVal
        else:
            self.regularproportionsVal = 1 - self.uncommonproportionsVal

    def getBodyProportions(self):
        return self.bodyProportions

    def setCaucasian(self, caucasian, sync=True, updateModifier = True):
        if updateModifier:
            modifier = self.getModifier('macrodetails/Caucasian')
            modifier.setValue(caucasian)
            self.applyAllTargets()
            return

        caucasian = min(max(caucasian, 0.0), 1.0)
        old = 1 - self.caucasianVal
        self.caucasianVal = caucasian
        if not sync:
            return
        new = 1 - self.caucasianVal
        if old < 1e-6:
            self.asianVal = new / 2
            self.africanVal = new / 2
        else:
            self.asianVal *= new / old
            self.africanVal *= new / old
        self.callEvent('onChanging', events3d.HumanEvent(self, 'caucasian'))

    def getCaucasian(self):
        return self.caucasianVal

    def setAfrican(self, african, sync=True, updateModifier = True):
        if updateModifier:
            modifier = self.getModifier('macrodetails/African')
            modifier.setValue(african)
            self.applyAllTargets()
            return

        african = min(max(african, 0.0), 1.0)
        old = 1 - self.africanVal
        self.africanVal = african
        if not sync:
            return
        new = 1 - self.africanVal
        if old < 1e-6:
            self.caucasianVal = new / 2
            self.asianVal = new / 2
        else:
            self.caucasianVal *= new / old
            self.asianVal *= new / old
        self.callEvent('onChanging', events3d.HumanEvent(self, 'african'))

    def getAfrican(self):
        return self.africanVal

    def setAsian(self, asian, sync=True, updateModifier = True):
        if updateModifier:
            modifier = self.getModifier('macrodetails/Asian')
            modifier.setValue(asian)
            self.applyAllTargets()
            return

        asian = min(max(asian, 0.0), 1.0)
        old = 1 - self.asianVal
        self.asianVal = asian
        if not sync:
            return
        new = 1 - self.asianVal
        if old < 1e-6:
            self.caucasianVal = new / 2
            self.africanVal = new / 2
        else:
            self.caucasianVal *= new / old
            self.africanVal *= new / old
        self.callEvent('onChanging', events3d.HumanEvent(self, 'asian'))

    def getAsian(self):
        return self.asianVal

    def syncRace(self):
        total = self.caucasianVal + self.asianVal + self.africanVal
        if total < 1e-6:
            self.caucasianVal = self.asianVal = self.africanVal = 1.0/3
        else:
            scale = 1.0 / total
            self.caucasianVal *= scale
            self.asianVal *= scale
            self.africanVal *= scale

    def setDetail(self, name, value):
        name = canonicalPath(name)
        if value:
            self.targetsDetailStack[name] = value
        elif name in self.targetsDetailStack:
            del self.targetsDetailStack[name]

    def getDetail(self, name):
        name = canonicalPath(name)
        return self.targetsDetailStack.get(name, 0.0)

    @property
    def modifiers(self):
        return self._modifiers.values()

    @property
    def modifierNames(self):
        return self._modifiers.keys()

    def getModifier(self, name):
        return self._modifiers[name]

    @property
    def modifierGroups(self):
        return self._modifier_groups.keys()

    def getModifiersByGroup(self, groupName):
        """
        Get all modifiers for this human belonging to the same modifier group.
        NOTE: do not confuse groupName with facegroup names!
        """
        try:
            return self._modifier_groups[groupName]
        except:
            log.warning('Modifier group %s does not exist.', groupName)
            return []

    def addModifier(self, modifier):
        #log.debug("Adding modifier of type %s: %s", type(modifier), modifier.fullName)

        if modifier.fullName in self.modifiers:
            log.error("Modifier with name %s is already attached to human.", modifier.fullName)
            raise RuntimeError("Modifier with name %s is already attached to human." % modifier.fullName)

        self._modifiers[modifier.fullName] = modifier

        if modifier.groupName not in self._modifier_groups:
            self._modifier_groups[modifier.groupName] = []
        self._modifier_groups[modifier.groupName].append(modifier)

        # Update dependency mapping
        if modifier.macroVariable and modifier.macroVariable != 'None':
            if modifier.macroVariable in self._modifier_varMapping and \
               self._modifier_varMapping[modifier.macroVariable] != modifier.groupName:
                log.error("Error, multiple modifier groups setting var %s (%s and %s)", modifier.macroVariable, modifier.groupName, self._modifier_varMapping[modifier.macroVariable])
            else:
                self._modifier_varMapping[modifier.macroVariable] = modifier.groupName
                # Update any new backwards references that might be influenced by this change (to make it independent of order of adding modifiers)
                toRemove = set()  # Modifiers to remove again from backwards map because they belogn to the same group as the modifier controlling the var
                dep = modifier.macroVariable
                for affectedModifierGroup in self._modifier_dependencyMapping.get(dep, []):
                    if affectedModifierGroup == modifier.groupName:
                        toRemove.add(affectedModifierGroup)
                        #log.debug('REMOVED from backwards map again %s', affectedModifierGroup)
                if len(toRemove) > 0:
                    if len(toRemove) == len(self._modifier_dependencyMapping[dep]):
                        del self._modifier_dependencyMapping[dep]
                    else:
                        for t in toRemove:
                            self._modifier_dependencyMapping[dep].remove(t)

        for dep in modifier.macroDependencies:
            groupName = self._modifier_varMapping.get(dep, None)
            if groupName and groupName == modifier.groupName:
                # Do not include dependencies within the same modifier group 
                # (this step might be omitted if the mapping is still incomplete (dependency is not yet mapped to a group), and can later be fixed by removing the entry again from the reverse mapping)
                continue
            if dep not in self._modifier_dependencyMapping:
                self._modifier_dependencyMapping[dep] = []
            if modifier.groupName not in self._modifier_dependencyMapping[dep]:
                self._modifier_dependencyMapping[dep].append(modifier.groupName)

    def getModifierDependencies(self, modifier, filter = None):
        result = set()

        if len(modifier.macroDependencies) > 0:
            for var in modifier.macroDependencies:
                if var not in self._modifier_varMapping:
                    log.error("Error var %s not mapped", var)
                    continue
                depMGroup = self._modifier_varMapping[var]

                if depMGroup != modifier.groupName:
                    if filter is not None:
                        if depMGroup in filter:
                            result.add(depMGroup)
                            if len(result) == len(filter):
                                return result   # Early out
                    else:
                        result.add(depMGroup)
        return result

    def getModifiersAffectedBy(self, modifier, filter = None):
        """
        Reverse dependency search. Returns all modifier groups to update that
        are affected by the change in the specified modifier.
        """
        result = self._modifier_dependencyMapping.get(modifier.macroVariable, [])
        if filter is None:
            return result
        else:
            return [e for e in result if e in filter]

    def removeModifier(self, modifier):
        try:
            del self._modifiers[modifier.fullName]
            self._modifier_groups[modifier.groupName].remove(modifier)

            # Clean up empty modifier groups
            if len(self._modifier_groups[modifier.groupName]) == 0:
                del self._modifier_groups[modifier.groupName]

                # Update dependency map
                reverseMapping = dict()
                for k,v in self._modifier_varMapping.items():
                    if v not in reverseMapping:
                        reverseMapping[v] = []
                    reverseMapping[v].append(k)

                for dep in reverseMapping.get(modifier.groupName, []):
                    del self._modifier_varMapping[dep]

            for dep in modifier.macroDependencies:
                self._modifier_dependencyMapping[dep].remove(modifier)
                if len(self._modifier_dependencyMapping[dep]) == 0:
                    del self._modifier_dependencyMapping[dep]
        except:
            log.debug('Failed to remove modifier % from human.', modifier.fullName)
            pass

    def getSymmetryGroup(self, group):
        if group.name.find('l-', 0, 2) != -1:
            return self.mesh.getFaceGroup(group.name.replace('l-', 'r-', 1))
        elif group.name.find('r-', 0, 2) != -1:
            return self.mesh.getFaceGroup(group.name.replace('r-', 'l-', 1))
        else:
            return None

    def getSymmetryPart(self, name):
        if name.find('l-', 0, 2) != -1:
            return name.replace('l-', 'r-', 1)
        elif name.find('r-', 0, 2) != -1:
            return name.replace('r-', 'l-', 1)
        else:
            return None

    def applyAllTargets(self, progressCallback=None, update=True):
        """
        This method applies all targets, in function of age and sex

        **Parameters:** None.

        progressCallback will automatically be set to G.app.progress if the
        progressCallback parameter is left to None. Set it to False to disable
        progress reporting.
        """
        if progressCallback is None:
            progressCallback = G.app.progress

        if progressCallback:
            progressCallback(0.0)

        # First call progressCalback (which often processes events) before resetting mesh
        # so that mesh is not drawn in its reset state
        algos3d.resetObj(self.meshData)

        progressVal = 0.0
        progressIncr = 0.5 / (len(self.targetsDetailStack) + 1)

        for (targetPath, morphFactor) in self.targetsDetailStack.iteritems():
            algos3d.loadTranslationTarget(self.meshData, targetPath, morphFactor, None, 0, 0)

            progressVal += progressIncr
            if progressCallback:
                progressCallback(progressVal)


        # Update all verts
        self.getSeedMesh().update()
        self.updateProxyMesh()
        if self.isSubdivided():
            self.updateSubdivisionMesh()
            if progressCallback:
                progressCallback(0.7)
            self.mesh.calcNormals()
            if progressCallback:
                progressCallback(0.8)
            if update:
                self.mesh.update()
        else:
            self.meshData.calcNormals(1, 1)
            if progressCallback:
                progressCallback(0.8)
            if update:
                self.meshData.update()

        if progressCallback:
            progressCallback(1.0)

        #self.traceStack(all=True)
        #self.traceBuffer(all=True, vertsToList=0)

        self.callEvent('onChanged', events3d.HumanEvent(self, 'targets'))

    def getPartNameForGroupName(self, groupName):
        # TODO is this still used anywhere
        for k in self.bodyZones:
            if k in groupName:
                return k
        return None

    def applySymmetryLeft(self):
        """
        This method applies right to left symmetry to the currently selected
        body parts.

        **Parameters:** None.

        """

        self.symmetrize('l')

    def applySymmetryRight(self):
        """
        This method applies left to right symmetry to the currently selected
        body parts.

        **Parameters:** None.

        """

        self.symmetrize('r')

    def symmetrize(self, direction='r'):
        """
        This method applies either left to right or right to left symmetry to
        the currently selected body parts.


        Parameters
        ----------

        direction:
            *string*. A string indicating whether to apply left to right
            symmetry (\"r\") or right to left symmetry (\"l\").

        """

        if direction == 'l':
            prefix1 = 'l-'
            prefix2 = 'r-'
        else:
            prefix1 = 'r-'
            prefix2 = 'l-'

        # Remove current values

        for target in self.targetsDetailStack.keys():
            targetName = os.path.basename(target)

            # Reset previous targets on symm side

            if targetName[:2] == prefix2:
                targetVal = self.targetsDetailStack[target]
                algos3d.loadTranslationTarget(self.meshData, target, -targetVal, None, 1, 0)
                del self.targetsDetailStack[target]

        # Apply symm target. For horiz movement the value must be inverted

        for target in self.targetsDetailStack.keys():
            targetName = os.path.basename(target)
            if targetName[:2] == prefix1:
                targetSym = os.path.join(os.path.dirname(target), prefix2 + targetName[2:])
                targetSymVal = self.targetsDetailStack[target]
                if 'trans-in' in targetSym:
                    targetSym = targetSym.replace('trans-in', 'trans-out')
                elif 'trans-out' in targetSym:
                    targetSym = targetSym.replace('trans-out', 'trans-in')
                algos3d.loadTranslationTarget(self.meshData, targetSym, targetSymVal, None, 1, 1)
                self.targetsDetailStack[targetSym] = targetSymVal

        self.updateProxyMesh()
        if self.isSubdivided():
            self.getSubdivisionMesh()

    def setDefaultValues(self):
        self.age = 0.5
        self.gender = 0.5
        self.weight = 0.5
        self.muscle = 0.5
        self.height = 0.5
        self.breastSize = 0.5
        self.breastFirmness = 0.5
        self.bodyProportions = 0.5

        self._setGenderVals()
        self._setAgeVals()
        self._setWeightVals()
        self._setMuscleVals()
        self._setHeightVals()
        self._setBreastSizeVals()
        self._setBreastFirmnessVals()
        self._setBodyProportionVals()

        self.caucasianVal = 1.0/3
        self.asianVal = 1.0/3
        self.africanVal = 1.0/3

    def resetMeshValues(self):
        self.setDefaultValues()

        self.targetsDetailStack = {}

        self.setMaterial(self._defaultMaterial)

        self.callEvent('onChanging', events3d.HumanEvent(self, 'reset'))
        self.callEvent('onChanged', events3d.HumanEvent(self, 'reset'))

    def getMaterial(self):
        return super(Human, self).getMaterial()

    def setMaterial(self, mat):
        self.callEvent('onChanging', events3d.HumanEvent(self, 'material'))
        super(Human, self).setMaterial(mat)
        self.callEvent('onChanged', events3d.HumanEvent(self, 'material'))

    material = property(getMaterial, setMaterial)

    def getJointPosition(self, jointName):
        """
        Get the position of a joint from the human mesh.
        This position is determined by the center of the joint helper with the
        specified name.
        """
        fg = self.meshData.getFaceGroup("joint-"+jointName)
        if not fg:
            raise RuntimeError("Human does not contain a joint helper with name %s" % ("joint-"+jointName))
        verts = self.meshData.getCoords(self.meshData.getVerticesForGroups([fg.name]))
        return verts.mean(axis=0)

    def load(self, filename, update=True, progressCallback=None):

        log.message("Loading human from MHM file %s.", filename)

        self.resetMeshValues()

        # TODO perhaps create progress indicator that depends on line count of mhm file?
        f = open(filename, 'r')

        for lh in G.app.loadHandlers.values():
            lh(self, ['status', 'started'])

        for data in f.readlines():
            lineData = data.split()

            if len(lineData) > 0 and not lineData[0] == '#':
                if lineData[0] == 'version':
                    log.message('Version %s', lineData[1])
                elif lineData[0] == 'tags':
                    for tag in lineData:
                        log.debug('Tag %s', tag)
                elif lineData[0] in G.app.loadHandlers:
                    G.app.loadHandlers[lineData[0]](self, lineData)
                else:
                    log.debug('Could not load %s', lineData)

        log.debug("Finalizing MHM loading.")
        for lh in set(G.app.loadHandlers.values()):
            lh(self, ['status', 'finished'])
        f.close()

        self.syncRace()

        self.callEvent('onChanged', events3d.HumanEvent(self, 'load'))

        if update:
            self.applyAllTargets(progressCallback)

        log.message("Done loading MHM file.")

    def save(self, filename, tags):

        f = open(filename, 'w')
        f.write('# Written by MakeHuman %s\n' % getVersionStr())
        f.write('version %s\n' % getShortVersion())
        f.write('tags %s\n' % tags)

        for handler in G.app.saveHandlers:
            handler(self, f)

        f.close()

