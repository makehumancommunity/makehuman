#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/external_tools_license.html)

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
Utility for making clothes to MH characters.

"""

import bpy
import os

#----------------------------------------------------------
#
#----------------------------------------------------------

def defineBoundingBox(context):
    hum, box = getObjectPair(context)
    checkObjectOK(hum, context, False)
    corners = getBoundingBox(hum, box, context)
    hum.MCBoundingBox = box.name
    print("Corners:")
    for hv in corners:
        co = hv.co
        print("%6d: %.5f %.5f %.5f" % (hv.index, co[0], co[1], co[2]))


def getBoundingBox(hum, box, context):
    if len(box.data.vertices) != 8:
        raise MHError("Box %s must have exactly eight vertices" % box.name)
    checkObjectOK(box, context, False)

    corners = []
    offs = box.location - hum.location
    for bv in box.data.vertices:
        for hv in hum.data.vertices:
            vec = bv.co - hv.co + offs
            if vec.length < Epsilon:
                corners.append(hv)
                break
    print(corners)
    if len(corners) != 8:
        raise MHError("Some box vertices do not match human vertices")

    return corners


def fitRigidly(context, hum, clo):
    scn = context.scene
    box = scn.objects[hum.MCBoundingBox]
    corners = getBoundingBox(hum, box, context)
    if scn.MCUseRigidSymmetry:
        lcorners = corners
        rcorners = mirrorCorners(corners)
    data = []

    for pv in clo.data.vertices:
        verts = []
        rawWts = []
        wtsSum = 0
        exact = False
        if scn.MCUseRigidSymmetry:
            if pv.co[0] < 0:
                corners = rcorners
            else:
                corners = lcorners

        for hv in corners:
            vec = pv.co - hv.co
            if len(vec) < Epsilon:
                exact = True
                exactVert = hv
                break
            w = 1/vec.length
            rawWts.append(w)
            wtsSum += w
            verts.append(hv.index)
        if exact:
            data.append((pv, True, [(exactVert, 0)], [1.0], []))
        else:
            wts = []
            for w in rawWts:
                wts.append(w/wtsSum)
            data.append((pv, False, verts, wts, []))
    return data
