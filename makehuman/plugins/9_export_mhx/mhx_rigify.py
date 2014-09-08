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

Definitions for the Rigify rig, which is intended for use with Blender's Rigify plugin.
Only works with MHX export.

"""

from armature.flags import *
from armature.parser import Parser
from armature.options import ArmatureOptions, Locale
from .mhx_armature import ExportArmature
from armature import rig_bones, utils
import log
from collections import OrderedDict


Joints = [
    ('l-ball-1',            'vo', (12889, -0.5, 0, 0)),
    ('l-ball-2',            'vo', (12889, 0.5, 0, 0)),
    ('r-ball-1',            'vo', (6292, 0.5, 0, 0)),
    ('r-ball-2',            'vo', (6292, -0.5, 0, 0)),
]

HeadsTails = {
    'heel.L' :              ('l-ankle', 'l-heel'),
    'heel1.L' :             ('l-ankle', 'l-heel'),
    'heel.02.L' :           ('l-ball-1', 'l-ball-2'),

    'heel.R' :              ('r-ankle', 'r-heel'),
    'heel1.R' :             ('r-ankle', 'r-heel'),
    'heel.02.R' :           ('r-ball-1', 'r-ball-2'),
}

OldArmature = {
    'heel.L' :              (180*D, 'shin.L', F_CON, L_HELP2),
    'heel.02.L' :           (0, 'heel.L', 0, L_HELP2),
    'heel.R' :              (180*D, 'shin.R', F_CON, L_HELP2),
    'heel.02.R' :           (0, 'heel.R', 0, L_HELP2),
}

NewArmature = {
    'heel1.L' :             (180*D, 'shin.L', F_CON, L_HELP2),
    'heel.02.L' :           (0, 'heel1.L', 0, L_HELP2),
    'heel1.R' :             (180*D, 'shin.R', F_CON, L_HELP2),
    'heel.02.R' :           (0, 'heel1.R', 0, L_HELP2),
}


class RigifyArmature(ExportArmature):

    def __init__(self, name, options, config):
        ExportArmature.__init__(self, name, options, config)
        self.visibleLayers = "08a80caa"
        self.objectProps += [("MhxRig", '"Rigify"')]
        self.useLayers = True


    def setup(self):
        ExportArmature.setup(self)

        if self.options.useMakeHumanRig:
            renames = {
                "heel1.L" : "heel.L",
                "heel1.R" : "heel.R",
                #"shoulder.01.L" : "deltoid.L",
                #"shoulder.01.R" : "deltoid.R",
                "clavicle.L" : "shoulder.L",
                "clavicle.R" : "shoulder.R",
            }

            nbones = OrderedDict()
            for bname,bone in self.bones.items():
                if bname in renames.keys():
                    nname = renames[bname]
                    nbones[nname] = bone
                    bone.name = nname
                    log.debug("R %s %s" % (bname, nname))
                else:
                    nbones[bname] = bone

            self.bones = nbones
            for bone in self.bones.values():
                for bname,nname in renames.items():
                    if bone.parent == bname:
                        log.debug("P %s %s %s" % (bone.name, bname, nname))
                        bone.parent = nname

            for bname,nname in renames.items():
                vname = "DEF-" + bname
                try:
                    vgroup = self.vertexWeights[vname]
                except KeyError:
                    vgroup = None
                if vgroup is not None:
                    self.vertexWeights["DEF-" + nname] = vgroup


    def writeFinal(self, fp):
        fp.write('Rigify %s ;\n' % self.name)


class RigifyParser(Parser):

    def __init__(self, amt, human):
        Parser.__init__(self, amt, human)

        if amt.options.useMakeHumanRig:
            self.splitBones = {
                "thumb.01" :    (2, "thumb.02", True, True),
                "f_index.01" :  (2, "f_index.02", True, True),
                "f_middle.01" : (2, "f_middle.02", True, True),
                "f_ring.01" :   (2, "f_ring.02", True, True),
                "f_pinky.01" :  (2, "f_pinky.02", True, True),
            }
        else:
            self.splitBones = {
                "upper_arm" :   (2, "forearm", False, True),
                "forearm" :     (2, "hand", False, True),
                "thigh" :       (2, "shin", False, True),
                "shin" :        (2, "foot", False, True),

                "thumb.01" :    (2, "thumb.02", True, True),
                "f_index.01" :  (2, "f_index.02", True, True),
                "f_middle.01" : (2, "f_middle.02", True, True),
                "f_ring.01" :   (2, "f_ring.02", True, True),
                "f_pinky.01" :  (2, "f_pinky.02", True, True),
            }


        self.joints += Joints
        utils.addDict(HeadsTails, self.headsTails)


    def createBones(self, boneInfo):
        amt = self.armature
        options = amt.options

        if options.useMakeHumanRig:
            self.addBones(NewArmature, boneInfo)
        else:
            self.addBones(OldArmature, boneInfo)
        Parser.createBones(self, boneInfo)


        if options.useMakeHumanRig:
            renames = {
                "shoulder02.L" : "DEF-upper_arm.01.L",
                "upperarm02.L" : "DEF-upper_arm.02.L",
                "lowerarm01.L" : "DEF-forearm.01.L",
                "lowerarm02.L" : "DEF-forearm.02.L",
                "upperleg01.L" : "DEF-thigh.01.L",
                "upperleg02.L" : "DEF-thigh.02.L",
                "lowerleg01.L" : "DEF-shin.01.L",
                "lowerleg02.L" : "DEF-shin.02.L",

                "shoulder02.R" : "DEF-upper_arm.01.R",
                "upperarm02.R" : "DEF-upper_arm.02.R",
                "lowerarm01.R" : "DEF-forearm.01.R",
                "lowerarm02.R" : "DEF-forearm.02.R",
                "upperleg01.R" : "DEF-thigh.01.R",
                "upperleg02.R" : "DEF-thigh.02.R",
                "lowerleg01.R" : "DEF-shin.01.R",
                "lowerleg02.R" : "DEF-shin.02.R",
            }
            for bname,nname in renames.items():
                vname = "DEF-" + bname
                amt.vertexWeights[nname] = amt.vertexWeights[vname]
                del amt.vertexWeights[vname]
                del amt.bones[bname]

