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

HeadMergers = {
    "head" : ("head", "uplid.L", "uplid.R", "lolid.L", "lolid.R", "tongue_base", "tongue_mid", "tongue_tip"),
}

SpineMergers = {
    "chest" : ("chest", "chest-1"),
    "spine" : ("spine", "spine-1"),
}

ShoulderMergers = {
    "clavicle.L" : ("clavicle.L", "deltoid.L"),
    "clavicle.R" : ("clavicle.R", "deltoid.R"),
}


