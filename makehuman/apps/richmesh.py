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

A rich mesh, with vertex weights, shapes and an armature

TODO
"""

import os
from collections import OrderedDict
import numpy as np
import log
import module3d
from core import G

from material import Material, Color

class RichMesh(object):

    def __init__(self, name, amt):
        self.name = os.path.basename(name)
        self.object = None
        self.setPose({})
        self.setVertexGroups({})
        self.shapes = []
        self.armature = amt
        self._material = None
        self._proxy = None

        self.vertexMask = None
        self.faceMask = None
        self.vertexMapping = None   # Maps vertex index of original object to the attached filtered object


    def getPose(self):
        return self._pose

    def setPose(self, pose):
        self._pose = pose
        self._coord = None
        self._vnorm = None

    pose = property(getPose, setPose)


    def getType(self):
        if self._proxy:
            return self._proxy.type
        else:
            return None

    def setType(self, type):
        log.debug("RichMesh setType not implemented")

    type = property(getType, setType)


    def setVertexGroups(self, weights):
        self.weights = weights
        self.normalizeVertexWeights()
        self.vertexGroups = OrderedDict()
        for index,name in enumerate(weights):
            self.vertexGroups[name] = VertexGroup(name, index, self.weights[name])
            #log.debug(self.vertexGroups[name])


    def getProxy(self):
        log.debug((self, self._proxy))
        return self._proxy

    def setProxy(self, proxy):
        self._proxy = proxy
        self._material = proxy.material

    proxy = property(getProxy, setProxy)


    def getMaterial(self):
        if self.type == 'Proxymeshes':
            return G.app.selectedHuman.material
        elif self.object:
            return self.object.material
        else:
            return self._material

    def setMaterial(self, material):
        if self.object:
            self.object.material == material
        self._material = material

    material = property(getMaterial, setMaterial)


    def fromData(self, coords, texVerts, faceVerts, faceUvs, weights, shapes, material):
        for fv in faceVerts:
            if len(fv) != 4:
                raise NameError("Mesh %s has non-quad faces and can not be handled by MakeHuman" % self.name)

        obj = self.object = module3d.Object3D(self.name)
        obj.setCoords(coords)
        obj.setUVs(texVerts)
        obj.createFaceGroup("Full Object")
        obj.setFaces(faceVerts, faceUvs)
        obj.calcNormals(True, True)
        obj.updateIndexBuffer()
        self.setVertexGroups(weights)
        self.shapes = shapes
        self._material = obj.material = material
        return self


    def fromMesh(self, mesh, proxy, weights={}, shapes=[]):
        self.object = mesh
        self._proxy = proxy
        self.setVertexGroups(weights)
        self.shapes = shapes
        self._material = mesh.material
        return self


    def normalizeVertexWeights(self):
        if not self.weights:
            return

        nverts = len(self.object.coord)
        sums = np.zeros(nverts, float)
        for group in self.weights.values():
            for vn,w in group:
                sums[vn] += w

        factors = np.zeros(nverts, float)
        for vn in range(nverts):
            if sums[vn] > 0.1:
                factors[vn] = 1.0/sums[vn]

        normWeights = {}
        for gname,group in self.weights.items():
            normGroup = normWeights[gname] = []
            for vn,w in group:
                normGroup.append((vn,w*factors[vn]))

        self.weights = normWeights


    def __repr__(self):
        return ("<RichMesh %s w %d t %d>" % (self.object, len(self.weights), len(self.shapes)))

    '''
    def calculateSkinWeights(self, amt):
        if self.object is None:
            raise NameError("%s has no object. Cannot calculate skin weights" % self)

        self.vertexWeights = [list() for _ in xrange(len(self.object.coord))]
        self.skinWeights = []

        wn = 0
        for (bn,b) in enumerate(amt.bones):
            try:
                wts = self.weights[b]
            except KeyError:
                wts = []
            for (vn,w) in wts:
                self.vertexWeights[int(vn)].append((bn,wn))
                wn += 1
            self.skinWeights.extend(wts)
    '''

class VertexGroup:
    def __init__(self, name, index, weights):
        self.name = name
        self.index = index
        self.verts = [data[0] for data in weights]
        self.weights = [data[1] for data in weights]

    def __repr__(self):
        return ("<VertexGroup %s %d %d>" % (self.name, self.index, len(self.verts)))


def getRichMesh(human, proxy, useCurrentMeshes, rawWeights, rawShapes, amt, scale=1.0):
    if proxy:
        if useCurrentMeshes:
            mesh = proxy.getMesh()
            rmesh = RichMesh(proxy.name, amt).fromMesh(mesh, proxy)
            return rmesh
        else:
            mesh = proxy.getSeedMesh()
            weights = proxy.getWeights(rawWeights, amt)
            shapes = proxy.getShapes(rawShapes, scale)
            rmesh = RichMesh(proxy.name, amt).fromMesh(mesh, proxy, weights, shapes)
            return rmesh
    else:
        if useCurrentMeshes:
            mesh = human.mesh
            return RichMesh(mesh.name, amt).fromMesh(mesh, None)
        else:
            mesh = human.getSeedMesh()
            return RichMesh(mesh.name, amt).fromMesh(mesh, None, rawWeights, rawShapes)


#
#   class FakeTarget
#   A temporary class that exporters can access in the same way as a real Target.
#

class FakeTarget:
    def __init__(self, name, verts, data):
        self.name = name
        self.verts = np.array(verts, int)
        self.data = np.array(data, float)
        if len(verts) != len(data):
            log.debug("FakeTarget %s %s %s" % (name, verts, data))
            halt

    def __repr__(self):
        return ("<FakeTarget %s %d %d>" % (self.name, len(self.verts), len(self.data)))

