#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

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

"""


#----------------------------------------------------------
#  Setting
#----------------------------------------------------------

class CSettings:

    def __init__(self, version):
        self.version = version

        if version == "alpha7":
            self.vertices = {
                "Body"      : (0, 15340),
                "Skirt"     : (15340, 16096),
                "Tights"    : (16096, 18528),
            }

            self.clothesVerts   = (self.vertices["Skirt"][0], self.vertices["Tights"][1])
            self.nTotalVerts    = self.vertices["Tights"][1]
            self.nBodyVerts     = self.vertices["Body"][1]
            self.nBodyFaces     = 14812
            self.baseMesh       = "alpha7"

        elif version == "alpha8a":
            self.vertices = {
                "Body"      : (0, 13380),
                "Tongue"    : (13380, 13606),
                "Joints"    : (13606, 14614),
                "Eyes"      : (14614, 14758),
                "EyeLashes" : (14758, 15008),
                "LoTeeth"   : (15008, 15076),
                "UpTeeth"   : (15076, 15144),
                "Penis"     : (15144, 15344),
                "Tights"    : (15344, 18018),
                "Skirt"     : (18018, 18738),
                "Hair"      : (18738, 19166),
            }

            self.clothesVerts   = (self.vertices["Tights"][0], self.vertices["Skirt"][1])
            self.nTotalVerts    = 19174
            self.nBodyVerts     = self.vertices["Body"][1]
            self.nBodyFaces     = 13606
            self.baseMesh       = "hm08-obsolete"

        elif version in ["alpha8b", "hm08"]:
            self.vertices = {
                "Body"      : (0, 13380),
                "Tongue"    : (13380, 13606),
                "Joints"    : (13606, 14598),
                "Eyes"      : (14598, 14742),
                "EyeLashes" : (14742, 14992),
                "LoTeeth"   : (14992, 15060),
                "UpTeeth"   : (15060, 15128),
                "Penis"     : (15128, 15328),
                "Tights"    : (15328, 18002),
                "Skirt"     : (18002, 18722),
                "Hair"      : (18722, 19150),
            }
            self.clothesVerts   = (self.vertices["Tights"][0], self.vertices["Skirt"][1])
            self.nTotalVerts    = 19158
            self.nBodyVerts     = self.vertices["Body"][1]
            self.nBodyFaces     = 13606
            self.firstHelperFace = 13378
            self.baseMesh       = "hm08"


#----------------------------------------------------------
#   Global variables
#----------------------------------------------------------

proxy = None
