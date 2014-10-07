#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

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

Armature options

"""

import os
import log
import io_json
from getpath import getSysDataPath

class ArmatureOptions(object):
    def __init__(self):
        self._setDefaults()

    def _setDefaults(self):
        self.rigtype = "Default"
        self.description = ""
        self.locale = None
        self.scale = 1.0
        self.boneMap = None

        self.useMasterBone = False
        self.useHeadControl = False
        self.useReverseHip = False
        self.useMuscles = False
        self.useTerminators = False
        self.useLocks = False
        self.useRotationLimits = False
        self.addConnectingBones = False
        self.useQuaternionsOnly = False

        self.mergeSpine = False
        self.mergeShoulders = False
        self.mergeFingers = False
        self.mergePalms = False
        self.mergeHead = False
        self.merge = None
        self.terminals = {}

        self.useSplitBones = False
        self.useSplitNames = False
        self.useDeformBones = False
        self.useDeformNames = False
        self.useSockets = False
        self.useIkArms = False
        self.useIkLegs = False
        self.useFingers = False
        self.useElbows = False
        self.useStretchyBones = False

        # Options set by exporters
        self.useCustomShapes = None
        self.useConstraints = False
        self.useBoneGroups = False
        self.useCorrectives = False
        self.useExpressions = False
        self.useTPose = False
        self.useIkHair = False
        self.useLeftRight = False

        # Obsolete options once used by mhx
        self.facepanel = False
        self.advancedSpine = False
        self.clothesRig = False

    def setExportOptions(self,
            useCustomShapes = None,
            useConstraints = False,
            useBoneGroups = False,
            useCorrectives = False,
            useRotationLimits = False,
            useLocks = False,
            useExpressions = False,
            useTPose = False,
            useIkHair = False,
            useLeftRight = False,
            ):
        self.useCustomShapes = useCustomShapes
        self.useConstraints = useConstraints
        self.useBoneGroups = useBoneGroups
        self.useCorrectives = useCorrectives
        self.useRotationLimits = useRotationLimits
        self.useLocks = useLocks
        self.useExpressions = useExpressions
        self.useTPose = useTPose
        self.useIkHair = useIkHair
        self.useLeftRight = useLeftRight


    def __repr__(self):
        return (
            "<ArmatureOptions\n" +
            "   rigtype : %s\n" % self.rigtype +
            "   description : %s\n" % self.description +
            "   scale : %s\n" % self.scale +
            "   boneMap : %s\n" % self.boneMap +
            "   useMuscles : %s\n" % self.useMuscles +
            "   addConnectingBones : %s\n" % self.addConnectingBones +
            "   mergeSpine : %s\n" % self.mergeSpine +
            "   mergeShoulders : %s\n" % self.mergeShoulders +
            "   mergeFingers : %s\n" % self.mergeFingers +
            "   mergePalms : %s\n" % self.mergePalms +
            "   mergeHead : %s\n" % self.mergeHead +
            "   useSplitBones : %s\n" % self.useSplitBones +
            "   useSplitNames : %s\n" % self.useSplitNames +
            "   useDeformBones : %s\n" % self.useDeformBones +
            "   useDeformNames : %s\n" % self.useDeformNames +
            "   useSockets : %s\n" % self.useSockets +
            "   useIkArms : %s\n" % self.useIkArms +
            "   useIkLegs : %s\n" % self.useIkLegs +
            "   useFingers : %s\n" % self.useFingers +
            "   useMasterBone : %s\n" % self.useMasterBone +
            "   useLocks : %s\n" % self.useLocks +
            "   useRotationLimits : %s\n" % self.useRotationLimits +
            "   merge : %s\n" % self.merge +
            "   locale : %s\n" % self.locale +  # TODO currently impossible to serialize
            ">")

    def fromSelector(self, selector):
        if selector is None:
            return

        self.useMuscles = selector.useMuscles.selected
        self.useReverseHip = selector.useReverseHip.selected
        #self.useCorrectives = selector.useCorrectives.selected
        self.addConnectingBones = selector.addConnectingBones.selected

        self.mergeSpine = selector.mergeSpine.selected
        self.mergeShoulders = selector.mergeShoulders.selected
        self.mergeFingers = selector.mergeFingers.selected
        self.mergePalms = selector.mergePalms.selected
        self.mergeHead = selector.mergeHead.selected

        self.useSplitBones = selector.useSplitBones.selected
        self.useSplitNames = selector.useSplitBones.selected
        self.useSockets = selector.useSockets.selected
        self.useIkArms = selector.useIkArms.selected
        self.useIkLegs = selector.useIkLegs.selected
        self.useDeformBones = selector.useDeformBones.selected
        self.useDeformNames = selector.useDeformBones.selected

        self.useMasterBone = selector.useMasterBone.selected


    def reset(self, selector, useMuscles=False):
        self._setDefaults()
        self.useMuscles = useMuscles
        if selector is not None:
            selector.fromOptions(self)


    def loadPreset(self, filepath, selector):
        struct = io_json.loadJson(filepath)
        self._setDefaults()
        try:
            self.rigtype = struct["name"]
        except KeyError:
            pass
        try:
            self.description = struct["description"]
        except KeyError:
            pass
        try:
            self.merge = struct["merge"]
        except KeyError:
            pass
        try:
            self.terminals = struct["terminals"]
        except KeyError:
            pass
        try:
            self.useTerminators = struct["use_terminators"]
        except KeyError:
            pass
        try:
            settings = struct["settings"]
        except KeyError:
            settings = {}
        for key,value in settings.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                log.warning("Unknown property %s defined in armature options file %s" % (key, filepath))

        if selector is not None:
            selector.fromOptions(self)
        try:
            bones = struct["bones"]
        except KeyError:
            bones = None
        if bones:
            self.locale = Locale(bones=bones)
        return self.description


class ArmatureSelector:

    def __init__(self, box):
        self.box = box

        import gui
        self.useMuscles = box.addWidget(gui.CheckBox("Muscle bones (MHX only)"))
        self.useReverseHip = box.addWidget(gui.CheckBox("Reverse hips"))
        self.addConnectingBones = box.addWidget(gui.CheckBox("Connecting bones"))

        self.mergeSpine = box.addWidget(gui.CheckBox("Merge spine"))
        self.mergeShoulders = box.addWidget(gui.CheckBox("Merge shoulders"))
        self.mergeFingers = box.addWidget(gui.CheckBox("Merge fingers"))
        self.mergePalms = box.addWidget(gui.CheckBox("Merge palms"))
        self.mergeHead = box.addWidget(gui.CheckBox("Merge head"))

        self.useSplitBones = box.addWidget(gui.CheckBox("Split forearm (MHX only)"))
        self.useDeformBones = box.addWidget(gui.CheckBox("Deform bones (MHX only)"))
        self.useSockets = box.addWidget(gui.CheckBox("Sockets (MHX only)"))
        self.useIkArms = box.addWidget(gui.CheckBox("Arm IK (MHX only)"))
        self.useIkLegs = box.addWidget(gui.CheckBox("Leg IK (MHX only)"))
        self.useFingers = box.addWidget(gui.CheckBox("Finger controls (MHX only)"))

        self.useMasterBone = box.addWidget(gui.CheckBox("Master bone"))


    def fromOptions(self, options):
        self.useMuscles.setSelected(options.useMuscles)
        self.useReverseHip.setSelected(options.useReverseHip)
        self.addConnectingBones.setSelected(options.addConnectingBones)

        self.mergeSpine.setSelected(options.mergeSpine)
        self.mergeShoulders.setSelected(options.mergeShoulders)
        self.mergeFingers.setSelected(options.mergeFingers)
        self.mergePalms.setSelected(options.mergePalms)
        self.mergeHead.setSelected(options.mergeHead)

        self.useSplitBones.setSelected(options.useSplitBones)
        self.useDeformBones.setSelected(options.useDeformBones)
        self.useSockets.setSelected(options.useSockets)
        self.useIkArms.setSelected(options.useIkArms)
        self.useIkLegs.setSelected(options.useIkLegs)
        self.useFingers.setSelected(options.useFingers)

        self.useMasterBone.setSelected(options.useMasterBone)

        for child in self.box.children:
            child.update()


class Locale:
    def __init__(self, filepath=None, bones=[]):
        self.filepath = filepath
        self.bones = bones


    def __repr__(self):
        string = "<Locale %s:" % (self.filepath)
        #for key,bone in self.bones.items():
        #    string += "\n    %s %s" % (key,bone)
        return string + ">"


    def load(self, filepath=None):
        if self.bones:
            return
        if filepath:
            self.filepath = filepath
        struct = io_json.loadJson(self.filepath)
        #self.language = struct["language"]
        self.bones = struct["bones"]


    def rename(self, bname):
        if bname[0:4] == "DEF-":
            return "DEF-" + self.rename(bname[4:])

        try:
            return self.bones[bname]
        except KeyError:
            #log.debug("Locale: no such bone: %s" % bname)
            pass

        words = bname.split(".", 1)
        try:
            return self.bones[words[0]] + "." + words[1]
        except KeyError:
            return bname

