#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

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

TODO
"""

import log
from core import G

class Object3D(object):
    """
    Represents an object renderable by OpenGL (glmodule)
    """
    def __init__(self, parent):
        """
        Initialize an OpenGL object for the specified parent mesh.
        Parent should be an object of type module3d.Object3D.
        """
        self.parent = parent
        self._texturePath = None
        self._textureTex = None
        self._shaderPath = None
        self._shaderObj = None

        self.shader_mtime = -1

    @property
    def name(self):
        return self.parent.name

    @property
    def verts(self):
        return self.parent.r_coord

    @property
    def norms(self):
        return self.parent.r_vnorm

    @property
    def color(self):
        return self.parent.r_color

    @property
    def color_diff(self):
        return self.parent.r_color_diff

    @property
    def hasUVs(self):
        return self.parent.hasUVs()

    @property
    def UVs(self):
        return self.parent.r_texco

    @property
    def tangents(self):
        return self.parent.r_vtang

    @property
    def primitives(self):
        return self.parent.index

    @property
    def nPrimitives(self):
        return len(self.primitives)

    @property
    def groups(self):
        return self.parent.grpix

    @property
    def shadeless(self):
        return self.object.shadeless

    @property
    def depthless(self):
        return self.object.depthless

    @property
    def vertsPerPrimitive(self):
        return self.parent.vertsPerPrimitive

    @property
    def shaderParameters(self):
        return self.object.shaderParameters

    @property
    def visibility(self):
        return self.parent.visibility

    @property
    def excludeFromProduction(self):
        """
        Whether or not to exclude this object from production renders 
        (rendering plugin).
        """
        return self.object.excludeFromProduction

    @property
    def object(self):
        return self.parent.object

    @property
    def cameraMode(self):
        return self.parent.cameraMode

    @property
    def pickable(self):
        return self.parent.pickable

    @property
    def solid(self):
        return self.object.solid

    @property
    def translation(self):
        return self.object.loc[:]

    @property
    def rotation(self):
        return self.object.rot[:]

    @property
    def scale(self):
        return self.object.scale[:]

    @property
    def nTransparentPrimitives(self):
        return self.parent.transparentPrimitives

    @property
    def alphaToCoverage(self):
        return self.object.alphaToCoverage

    @property
    def transform(self):
        return self.object.transform

    @property
    def lockRotation(self):
        return self.object.lockRotation

    @property
    def x(self):
        return self.object.x

    @property
    def y(self):
        return self.object.y

    @property
    def z(self):
        return self.object.z

    @property
    def rx(self):
        return self.object.rx

    @property
    def ry(self):
        return self.object.ry

    @property
    def rz(self):
        return self.object.rz

    @property
    def sx(self):
        return self.object.sx

    @property
    def sy(self):
        return self.object.sy

    @property
    def sz(self):
        return self.object.sz

    def __str__(self):
        return "<Object3D %s>" % self.name

    def getShaderChanged(self):
        return self.shader_mtime != self.material.shaderChanged

    def setShaderChanged(self, shaderChanged):
        if not shaderChanged:
            self.shader_mtime = self.material.shaderChanged
        else:
            self.shader_mtime = -1

    shaderChanged = property(getShaderChanged, setShaderChanged)


    @property
    def shaderObj(self):
        import shader
        if not shader.Shader.supported():
            return None
        if self._shaderPath != self.object.shader:
            self._shaderObj = None
        if self._shaderObj is False:
            return None

        if self._shaderObj is None or self.shaderChanged:
            self._shaderPath = self.object.shader
            if self._shaderPath is None:
                self._shaderObj = None
            else:
                try:
                    self._shaderObj = self.object.shaderObj
                except (Exception, RuntimeError), e:
                    self._shaderObj = False
                    log.error(e, exc_info=True)
                    log.warning("Failed to initialize shader (%s), falling back to fixed function shading.", self._shaderPath)
            self.shaderChanged = False
        if self._shaderObj is False:
            return None
        return self._shaderObj

    @property
    def shader(self):
        if self.shaderObj is None:
            return 0
        return self.shaderObj.shaderId

    @property
    def priority(self):
        return self.parent.priority

    @property
    def useVertexColors(self):
        return self.object.shaderConfig['vertexColors']

    @property
    def isTextured(self):
        return self.object.shaderConfig['diffuse']

    @property
    def material(self):
        return self.object.material

    @property
    def cull(self):
        return self.object.cull

    def clrid(self, idx):
        return self.parent._faceGroups[idx].colorID

    def gcolor(self, idx):
        return self.parent._faceGroups[idx].color

    def draw(self, *args, **kwargs):
        import glmodule
        return glmodule.drawMesh(self, *args, **kwargs)

    def pick(self, *args, **kwargs):
        import glmodule
        return glmodule.pickMesh(self, *args, **kwargs)

    def sortFaces(self):
        import numpy as np
        import matrix
        camera = G.cameras[0]

        indices = self.primitives[self.nPrimitives - self.nTransparentPrimitives:]
        if len(indices) == 0:
            return

        m = matrix.translate(-self.translation)
        m = matrix.rotx(-self.rx) * m
        m = matrix.roty(-self.ry) * m
        m = matrix.rotz(-self.rz) * m
        m = matrix.translate(self.translation) * m
        cxyz = matrix.transform3(m, camera.eye)

        # Prepare sorting data
        verts = self.verts[indices] - cxyz
        distances = np.sum(verts ** 2, axis = -1)
        distances = np.amin(distances, axis = -1)
        distances = -distances
        # Sort
        order = np.argsort(distances)
        indices2 = indices[order,:]

        indices[...] = indices2

    @property
    def texture(self):
        return self.object.texture

    @classmethod
    def attach(cls, mesh):
        if mesh.object3d:
            log.debug('mesh is already attached')
            return

        # Create an Object3D for the mesh
        mesh.object3d = cls(mesh)
        G.world.append(mesh.object3d)

    @classmethod
    def detach(cls, mesh):
        if not mesh.object3d:
            log.debug('mesh is not attached')
            return

        G.world.remove(mesh.object3d)
        mesh.object3d = None
