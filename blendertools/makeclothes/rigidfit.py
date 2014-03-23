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
import math
from .makeclothes import *

#----------------------------------------------------------
#
#----------------------------------------------------------

def getNumpy():
    try:
        import numpy
    except KeyError:
        numpy = None

    if numpy is None:
        raise MHError(
"""Cannot import numpy.

Rigid fitting only works if numpy is installed in Blender's addons directory.
Download numpy for Python 3.3. Make sure to use the right version

Python 3.3, Windows 32 bits, Linux, Mac:
https://pypi.python.org/pypi/numpy

Python 3.3, Windows 64 bits:
http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
Scipy-0.8.0.win-amd64-py3.3.exe requires
numpy-1.5.0.win-amd64-py3.3-mkl.exe.

On Windows, copy or link
C:\\Python33\\Lib\\site-packages\\numpy
to Blender's addon directory.
Instructions for Linux and Mac users later.
""")

    try:
        import scipy
    except ImportError:
        scipy = None

    if scipy is None:
        raise MHError(
"""Cannot import scipy.

Rigid fitting only works if scipy is installed in Blender's addons directory.
Download scipy for Python 3.3. Make sure to use the right version

Python 3.3, Windows 32 bits, Linux, Mac:
https://pypi.python.org/pypi/scipy

Python 3.3, Windows 64 bits:
http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy

On Windows, copy or link
C:\\Python33\\Lib\\site-packages\\scipy
to Blender's addon directory.
Instructions for Linux and Mac users later.
""")

    return scipy

#----------------------------------------------------------
#
#----------------------------------------------------------

def defineBoundingBox(context):
    hum, box = getObjectPair(context)
    checkObjectOK(hum, context, False)
    corners = getBoundingBox(hum, box, context)
    hum.MCBoundingBox = box.name


def getBoundingBox(hum, box, context):
    np = getNumpy()

    if len(box.data.vertices) != 8:
        raise MHError("Box %s must have exactly eight vertices" % box.name)
    checkObjectOK(box, context, False)

    BoxOrder = [ 0, 4, 1, 5, 3, 7, 2, 6]

    offs = box.location - hum.location
    n = 0
    ix = []
    cx = []
    for i in range(2):
        iy = []
        cy = []
        for j in range(2):
            iz = []
            cz = []
            for k in range(2):
                bv = box.data.vertices[n]
                n += 1
                idx = co = None
                for hv in hum.data.vertices:
                    vec = bv.co - hv.co + offs
                    if vec.length < Epsilon:
                        idx = hv.index
                        co = hv.co
                        hv.select = True
                        break

                if idx is None:
                    idx = bv.index
                    raise MHError(
                        "Box vertex %d%d%d at %s\n does not match any human vertex"
                        % (idx[0], idx[1], idx[2], tuple(bv.co)))

                iz.append(idx)
                cz.append(co)
            iy.append(iz)
            cy.append(cz)
        ix.append(iy)
        cx.append(cy)

    indices = np.array(ix)
    coords = np.array(cx)
    return indices, coords

    print(ix)
    print(indices)
    print(cx)
    print(coords)
    return indices, coords


def fitRigidly(context, hum, clo):
    scn = context.scene
    box = scn.objects[hum.MCBoundingBox]
    indices,coords = getBoundingBox(hum, box, context)
    if scn.MCUseRigidSymmetry:
        lcorners = corners
        rcorners = mirrorCorners(corners)
    data = []

    verts = getVerts(indices)
    for pv in clo.data.vertices:
        if scn.MCUseRigidSymmetry:
            if pv.co[0] < 0:
                corners = rcorners
            else:
                corners = lcorners

        wts = getWeights(pv, coords)
        if False and exact:
            vert = hum.data.vertices[verts]
            data.append((pv, True, [(vert, 0)], [1.0], []))
        else:
            data.append((pv, False, verts, wts, []))
    return data


def getVerts(indices):
    verts = []
    for i in range(2):
        for j in range(2):
            for k in range(2):
                idx = indices[i,j,k]
                verts.append(idx)
    return verts


def equations(alpha, pco, coords):
    f = pco.copy()
    a = aFromAlpha(alpha)
    for i in range(2):
        for j in range(2):
            for k in range(2):
                f -= a[i,0]*a[j,1]*a[k,2]*coords[i,j,k]
    return f


def aFromAlpha(alpha):
    np = getNumpy()
    a = np.zeros((2,3), float)
    a[0] = alpha
    a[1] = 1-alpha
    return a


def getCost(alpha):
    cost = 0
    for n in range(3):
        if alpha[n] > 1:
            cost += alpha[n]-1
        elif alpha[n] < 0:
            cost -= alpha[n]
    return cost


def getWeights(pv, coords):
    import numpy as np
    from scipy.optimize import fsolve
    from random import random

    pco = np.array(pv.co)
    minCost = 1e6
    best = None
    nTries = 5
    print("\nSolve", pv.index)
    while minCost > Epsilon and nTries > 0:
        nTries -= 1
        alpha0 = np.array((random(), random(), random()))
        alpha = fsolve(equations, alpha0, args=(pco, coords))
        cost = getCost(alpha)
        if cost < minCost:
            minCost = cost
            bestAlpha = alpha
        print(cost, minCost, alpha)

    a = aFromAlpha(bestAlpha)
    wts = []
    for i in range(2):
        for j in range(2):
            for k in range(2):
                w = a[i,0]*a[j,1]*a[k,2]
                wts.append(w)
    return wts