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

Bone mergers
"""

from .flags import *
from . import rig_makehuman

PalmMergers = {
    "hand.L" : ("palm_index.L", "palm_middle.L", "palm_ring.L", "palm_pinky.L", "thumb.01.L"),
    "hand.R" : ("palm_index.R", "palm_middle.R", "palm_ring.R", "palm_pinky.R", "thumb.01.R"),
}

FingerMergers = {
    "f_index.01.L" : ("f_index.01.L", "f_index.02.L", "f_index.03.L"),
    "f_ring.01.L" : ("f_middle.01.L", "f_middle.02.L", "f_middle.03.L", "f_ring.01.L", "f_ring.02.L", "f_ring.03.L", "f_pinky.01.L", "f_pinky.02.L", "f_pinky.03.L"),
    "f_index.01.R" : ("f_index.01.R", "f_index.02.R", "f_index.03.R"),
    "f_ring.01.R" : ("f_middle.01.R", "f_middle.02.R", "f_middle.03.R", "f_ring.01.R", "f_ring.02.R", "f_ring.03.R", "f_pinky.01.R", "f_pinky.02.R", "f_pinky.03.R"),
}

OldHeadMergers = {
    "head" : ("head", "uplid.L", "uplid.R", "lolid.L", "lolid.R", "tongue_base", "tongue_mid", "tongue_tip"),
}

NewHeadMergers = {}
hlist = NewHeadMergers["head"] = ["head"]
#hlist.append("jaw")
for bname,data in rig_makehuman.Armature.items():
    if data[3] & L_FACE and bname[0:8] != "platysma":
        hlist.append(bname)


NeckMergers = {}
nlist = NeckMergers["neck"] = ["neck", "neck2"]
for bname in rig_makehuman.Armature.keys():
    if bname[0:8] == "platysma":
        nlist.append(bname)


TwistMergers = {
    "upper_arm.L" : ["upper_arm.L", "shoulder02.L", "upperarm02.L"],
    "forearm.L" :   ["forearm.L", "lowerarm01.L", "lowerarm02.L"],
    "thigh.L" :     ["thigh.L", "upperleg01.L", "upperleg02.L"],
    "shin.L" :      ["shin.L", "lowerleg01.L", "lowerleg02.L"],
    "upper_arm.R" : ["upper_arm.R", "shoulder02.R", "upperarm02.R"],
    "forearm.R" :   ["forearm.R", "lowerarm01.R", "lowerarm02.R"],
    "thigh.R" :     ["thigh.R", "upperleg01.R", "upperleg02.R"],
    "shin.R" :      ["shin.R", "lowerleg01.R", "lowerleg02.R"],
}

SpineMergers = {
    "chest" : ("chest", "chest-1"),
    "spine" : ("spine", "spine-1"),
}

ShoulderMergers = {
    "clavicle.L" : ("clavicle.L", "deltoid.L"),
    "clavicle.R" : ("clavicle.R", "deltoid.R"),
}

NewFeetMergers = {}
for suffix in [".L", ".R"]:
    foot = "foot"+suffix
    NewFeetMergers[foot] = [foot, "heel"+suffix]
    for n in range(1,6):
        NewFeetMergers[foot].append("metatarsal%d%s" % (n,suffix))

NewToeMergers = {}
for suffix in [".L", ".R"]:
    toe = "toe"+suffix
    NewToeMergers[toe] = [toe]
    for k in range(1,3):
        NewToeMergers[toe].append("toe1-%d%s" % (k, suffix))
    for n in range(2,6):
        for k in range(1,4):
            NewToeMergers[toe].append("toe%d-%d%s" % (n, k, suffix))



