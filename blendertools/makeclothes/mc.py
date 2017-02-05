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

from maketarget import mh

class CSettings(mh.CSettings):

    def __init__(self, version):
        mh.CSettings.__init__(self, version)

        if version == "alpha7":
            self.topOfSkirt    = range(16691,16707)

            self.bodyPartVerts = {
                "Body" : ((13868, 14308), (881, 13137), (10854, 10981)),
                "Head" : ((4302, 8697), (8208, 8220), (8223, 6827)),
                "Torso" : ((3464, 10305), (6930, 7245), (14022, 14040)),
                "Arm" : ((14058, 14158), (4550, 4555), (4543, 4544)),
                "Hand" : ((14058, 15248), (3214, 3264), (4629, 5836)),
                "Leg" : ((3936, 3972), (3840, 3957), (14165, 14175)),
                "Foot" : ((4909, 4943), (5728, 12226), (4684, 5732)),
                "Eye" : ((142, 197), (76, 141), (169, 225)),
            }

        elif version == "hm08":

            self.topOfSkirt = [
                15773, 16033, 16034, 16035, 16036, 16037, 16038, 16039, 16040, 16042, 16047, 16048,
                16049, 16050, 16056, 16510, 16528, 17090, 17347, 17360, 17361, 17362, 17363, 17364,
                17365, 17366, 17367, 17369, 17374, 17375, 17376, 17377, 17378, 17384, 17844, 17862,
            ]

            self.bottomOfCoatTop = [
                15903, 16021, 16022, 16023, 16024, 16025, 16026, 16027, 16028, 16041, 16043, 16044,
                16045, 16046, 16055, 16487, 16509, 17221, 17346, 17348, 17349, 17350, 17351, 17352,
                17353, 17354, 17355, 17368, 17370, 17371, 17372, 17373, 17383, 17821, 17843, 17957,
            ]

            self.bodyPartVerts = {
                "Body" : ((13868, 14308), (10854, 10981), (881, 13137)),
                "Head" : ((5399, 11998), (962, 5320),  (791,881)),
                "Teeth" : ((15077, 15111), (15061, 15068), (14993, 15061)),
                "Torso" : ((3924, 10589), (1892, 3946), (1524, 4370)),
                "Arm" : ((8300, 10210), (10076, 10543), (10064, 10069)),
                "Hand" : ((8938, 10548), (9864, 10267), (9881, 10318)),
                "Leg" : ((11133, 11141), (11130, 11135), (11025, 11460)),
                "Foot" : ((12839, 12860), (11609, 12442), (12828, 12888)),
                "Eye" : ((14618, 14645), (14650, 14658), (14636, 14663)),
                "Genital" : ((6335, 12932), (4347, 4376), (4335, 6431)),
            }


settings = {
    "alpha7" : CSettings("alpha7"),
    "hm08"   : CSettings("hm08"),
    "None"   : None
}


#
#   File utilities
#

import os
from .error import MHError

def goodName(name):
    newName = name.replace('-','_').replace(' ','_')
    return newName.lower()


def getFileName(pob, folder, ext):
    name = goodName(pob.name)
    outdir = '%s/%s' % (folder, name)
    outdir = os.path.realpath(os.path.expanduser(outdir))
    if not os.path.exists(outdir):
        print("Creating directory %s" % outdir)
        try:
            os.makedirs(outdir)
        except FileNotFoundError:
            raise MHError("Could not create directory %s" % outdir)
    outfile = os.path.join(outdir, "%s.%s" % (name, ext))
    return (outdir, outfile)


def openOutputFile(filepath):
    print("Create file \"%s\"" % filepath)
    try:
        return open(filepath, "w", encoding="utf-8", newline="\n")
    except IOError:
        raise MHError("Could not open\n\"%s\"     \nfor writing" % filepath)


def openInputFile(filepath):
    print("Read file \"%s\"" % filepath)
    try:
        return open(filepath, "rU")
    except IOError:
        raise MHError("Could not open\n\"%s\"     \nfor reading" % filepath)
