#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Manuel Bastioni, Marc Flerackers

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

Common GUI elements extracted from gui3d to minimize coupling with gui backend.
"""

import events3d

import numpy as np
import matrix

class Action(object):
    def __init__(self, name):
        self.name = name

    def do(self):
        return True

    def undo(self):
        return True

# Wrapper around Object3D
class Object(events3d.EventHandler):

    """
    An object on the screen.

    :param position: The position in 3d space.
    :type position: list or tuple
    :param mesh: The mesh object.
    :param visible: Wether the object should be initially visible.
    :type visible: Boolean
    """

    def __init__(self, mesh, position=[0.0, 0.0, 0.0], visible=True):

        if mesh.object:
            raise RuntimeError('This mesh is already attached to an object')

        self.mesh = mesh
        self.mesh.object = self
        self.mesh.setVisibility(visible)

        self._loc = np.zeros(3, dtype=np.float32)
        self._rot = np.zeros(3, dtype=np.float32)
        self._scale = np.ones(3, dtype=np.float32)

        self.setLoc(*position)

        self.lockRotation = False   # Set to true to make the rotation of this object independent of the camera rotation
        self.placeAtFeet = False    # Set to true to automatically set Y loc (position) to height of ground helper joint of the human

        self._view = None

        self.visible = visible
        self.excludeFromProduction = False  # Set to true to exclude from production renders

        self.proxy = None

        self.__seedMesh = self.mesh
        self.__proxyMesh = None
        self.__subdivisionMesh = None
        self.__proxySubdivisionMesh = None

        self.setUVMap(mesh.material.uvMap)

    # TODO
    def clone(self):
        pass

    def _attach(self):

        if self.view.isVisible() and self.visible:
            self.mesh.setVisibility(1)
        else:
            self.mesh.setVisibility(0)

        for mesh in self._meshes():
            self.attachMesh(mesh)

    def _detach(self):
        for mesh in self._meshes():
            self.detachMesh(mesh)

    @staticmethod
    def attachMesh(mesh):
        import object3d
        import selection
        selection.selectionColorMap.assignSelectionID(mesh)
        object3d.Object3D.attach(mesh)

    @staticmethod
    def detachMesh(mesh):
        import object3d
        object3d.Object3D.detach(mesh)

    def _meshes(self):
        for mesh in (self.__seedMesh,
                     self.__proxyMesh,
                     self.__subdivisionMesh,
                     self.__proxySubdivisionMesh):
            if mesh is not None:
                yield mesh

    @property
    def view(self):
        if not self._view or not callable(self._view):
            return None
        return self._view()

    def show(self):
        self.visible = True
        self.setVisibility(True)

    def hide(self):
        self.visible = False
        self.setVisibility(False)

    def isVisible(self):
        return self.visible

    @property
    def name(self):
        return self.mesh.name

    def setVisibility(self, visibility):
        if not self.view:
            self.mesh.setVisibility(0)
        if self.view.isVisible() and self.visible and visibility:
            self.mesh.setVisibility(1)
        else:
            self.mesh.setVisibility(0)

    ##
    # Orientation properties
    ##

    def getLoc(self):
        result = np.zeros(3, dtype=np.float32)
        result[:] = self._loc[:]
        if self.placeAtFeet:
            from core import G
            human = G.app.selectedHuman
            result[1] = human.getJointPosition('ground')[1]
        return result

    def setLoc(self, locx, locy, locz):
        """
        This method is used to set the location of the object in the 3D coordinate space of the scene.

        :param locx: The x coordinate of the object.
        :type locx: float
        :param locy: The y coordinate of the object.
        :type locy: float
        :param locz: The z coordinate of the object.
        :type locz: float
        """
        self._loc[...] = (locx, locy, locz)

    loc = property(getLoc, setLoc)

    def get_x(self):
        return self.loc[0]

    def set_x(self, x):
        self._loc[0] = x

    x = property(get_x, set_x)

    def get_y(self):
        return self.loc[1]

    def set_y(self, y):
        self._loc[1] = y

    y = property(get_y, set_y)

    def get_z(self):
        return self.loc[2]

    def set_z(self, z):
        self._loc[2] = z

    z = property(get_z, set_z)

    def get_rx(self):
        return self._rot[0]

    def set_rx(self, rx):
        self._rot[0] = rx

    rx = property(get_rx, set_rx)

    def get_ry(self):
        return self._rot[1]

    def set_ry(self, ry):
        self._rot[1] = ry

    ry = property(get_ry, set_ry)

    def get_rz(self):
        return self._rot[2]

    def set_rz(self, rz):
        self._rot[2] = rz

    rz = property(get_rz, set_rz)

    def get_sx(self):
        return self._scale[0]

    def set_sx(self, sx):
        self._scale[0] = sx

    sx = property(get_sx, set_sx)

    def get_sy(self):
        return self._scale[1]

    def set_sy(self, sy):
        self._scale[1] = sy

    sy = property(get_sy, set_sy)

    def get_sz(self):
        return self._scale[2]

    def set_sz(self, sz):
        self._scale[2] = sz

    sz = property(get_sz, set_sz)

    def getPosition(self):
        return [self.x, self.y, self.z]

    def setPosition(self, position):
        self.setLoc(position[0], position[1], position[2])

    def getRotation(self):
        return [self.rx, self.ry, self.rz]

    def setRotation(self, rotation):
        rotation[0] = rotation[0] % 360
        rotation[1] = rotation[1] % 360

        if rotation[2] != 0.0:
            log.warning('Setting a non-zero rotation around Z axis is not supported!')
            rotation[2] = 0.0

        self.setRot(rotation[0], rotation[1], rotation[2])

    def setRot(self, rx, ry, rz):
        """
        This method sets the orientation of the object in the 3D coordinate space of the scene.

        :param rx: Rotation around the x-axis.
        :type rx: float
        :param ry: Rotation around the y-axis.
        :type ry: float
        :param rz: Rotation around the z-axis.
        :type rz: float
        """
        self._rot[...] = (rx, ry, rz)

    def getRotation(self):
        return self._rot

    rot = property(getRotation, setRotation)

    def setScale(self, scale, scaleY=None, scaleZ=1):
        """
        This method sets the scale of the object in the 3D coordinate space of
        the scene, relative to the initially defined size of the object.

        :param scale: Scale along the x-axis, uniform scale if other params not
                      specified.
        :type scale: float
        :param scaleY: Scale along the x-axis.
        :type scaleY: float
        :param scaleZ: Scale along the x-axis.
        :type scaleZ: float
        """
        if scaleY is None:
            scaleY = scale
            scaleZ = scale
        self._scale[...] = (scale, scaleY, scaleZ)

    def getScale(self):
        return list(self._scale)

    scale = property(getScale, setScale)

    @property
    def transform(self):
        m = matrix.translate(self.loc)
        if any(x != 0 for x in self.rot):
            m = m * matrix.rotx(self.rx)
            m = m * matrix.roty(self.ry)
            m = m * matrix.rotz(self.rz)
        if any(x != 1 for x in self.scale):
            m = m * matrix.scale(self.scale)
        return m


    def setTexture(self, texture):
        self.mesh.setTexture(texture)

    def getTexture(self):
        return self.mesh.texture

    def clearTexture(self):
        self.mesh.setTexture(None)

    def hasTexture(self):
        return self.mesh.hasTexture()

    def setSolid(self, solid):
        for mesh in self._meshes():
            mesh.setSolid(solid)

    def isSolid(self):
        return self.__seedMesh.solid

    def getSeedMesh(self):
        return self.__seedMesh

    def getProxyMesh(self):
        return self.__proxyMesh

    def updateProxyMesh(self):
        if self.proxy and self.__proxyMesh:
            self.proxy.update(self.__proxyMesh)
            self.__proxyMesh.update()

    def isProxied(self):
        return self.mesh == self.__proxyMesh or self.mesh == self.__proxySubdivisionMesh

    def setProxy(self, proxy):
        isSubdivided = self.isSubdivided()

        if self.proxy:
            # Copy proxy mesh material settings back to original mesh
            self.__seedMesh.material = self.mesh.material
            self.proxy = None
            self.detachMesh(self.__proxyMesh)
            self.__proxyMesh.clear()
            self.__proxyMesh = None
            if self.__proxySubdivisionMesh:
                self.detachMesh(self.__proxySubdivisionMesh)
                self.__proxySubdivisionMesh.clear()
                self.__proxySubdivisionMesh = None
            self.mesh = self.__seedMesh
            self.mesh.setVisibility(1)

        if proxy:
            import files3d
            self.proxy = proxy

            self.__proxyMesh = proxy.object.mesh
            proxy.object = self

            # Copy attributes from human mesh to proxy mesh
            for attr in ('x', 'y', 'z', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz',
                         'visibility', 'shadeless', 'pickable', 'cameraMode', 'material'):
                setattr(self.__proxyMesh, attr, getattr(self.mesh, attr))

            # Connect the proxy to this object directly
            self.__proxyMesh.object = self.mesh.object

            self.proxy.update(self.__proxyMesh)

            # Attach to GL object if this object is attached to viewport
            if self.__seedMesh.object3d:
                self.attachMesh(self.__proxyMesh)

            self.mesh.setVisibility(0)
            self.mesh = self.__proxyMesh
            self.mesh.setVisibility(1)
            self.__proxyMesh.setSolid(self.__seedMesh.solid)

        self.setSubdivided(isSubdivided)

    def getSubdivisionMesh(self, update=True, progressCallback=None):
        """
        Create or update the Catmull-Clark subdivided (or smoothed) mesh for
        this mesh.
        This does not change the status of isSubdivided(), use setSubdivided()
        for that.

        If this mesh is doubled by a proxy, when isProxied() is true, a
        subdivision mesh for the proxy is used.

        Returns the subdivided mesh data.

        """
        import catmull_clark_subdivision as cks

        if self.isProxied():
            if not self.__proxySubdivisionMesh:
                self.__proxySubdivisionMesh = cks.createSubdivisionObject(self.__proxyMesh, progressCallback)
                if self.__seedMesh.object3d:
                    self.attachMesh(self.__proxySubdivisionMesh)
            elif update:
                cks.updateSubdivisionObject(self.__proxySubdivisionMesh, progressCallback)

            return self.__proxySubdivisionMesh
        else:
            if not self.__subdivisionMesh:
                self.__subdivisionMesh = cks.createSubdivisionObject(self.__seedMesh, progressCallback)
                if self.__seedMesh.object3d:
                    self.attachMesh(self.__subdivisionMesh)
            elif update:
                cks.updateSubdivisionObject(self.__subdivisionMesh, progressCallback)

            return self.__subdivisionMesh

    def isSubdivided(self):
        """
        Returns whether this mesh is currently set to be subdivided
        (or smoothed).

        """
        return self.mesh == self.__subdivisionMesh or self.mesh == self.__proxySubdivisionMesh

    def setSubdivided(self, flag, update=True, progressCallback=None):
        """
        Set whether this mesh is to be subdivided (or smoothed).
        When set to true, the subdivision mesh is automatically created or
        updated.

        """
        if flag == self.isSubdivided():
            return False

        if flag:
            self.mesh.setVisibility(0)
            originalMesh = self.mesh
            self.mesh = self.getSubdivisionMesh(update, progressCallback)
            self.mesh.setVisibility(1)

            # Copy material
            self.mesh.setMaterial(originalMesh.material)

        else:
            originalMesh = self.__seedMesh if self.mesh == self.__subdivisionMesh else self.__proxyMesh

            # Copy material
            originalMesh.material = self.mesh.material

            self.mesh.setVisibility(0)
            self.mesh = originalMesh
            if update:
                self.mesh.calcNormals()
                self.mesh.update()
            self.mesh.setVisibility(1)
        return True

    def updateSubdivisionMesh(self, rebuildIndexBuffer=False, progressCallback=None):
        if rebuildIndexBuffer:
            # Purge old subdivision mesh and recalculate entirely
            self.setSubdivided(False)
            self.__subdivisionMesh = self.__proxySubdivisionMesh = None
            self.setSubdivided(True, progressCallback=progressCallback)
        else:
            self.getSubdivisionMesh(True)

    def _setMeshUVMap(self, filename, mesh):
        import material

        if filename == mesh.material.uvMap:
            # No change, do nothing
            return

        if not hasattr(mesh, "_originalUVMap") or not mesh._originalUVMap:
            # Backup original mesh UVs
            mesh._originalUVMap = dict()
            mesh._originalUVMap['texco'] = mesh.texco
            mesh._originalUVMap['fuvs'] = mesh.fuvs
            #self._originalUVMap['fvert'] = mesh.fvert
            #self._originalUVMap['group'] = mesh.group

        faceMask = mesh.getFaceMask()
        faceGroups = mesh.group

        mesh.material.uvMap = filename

        if not filename:
            # Restore original UVs
            mesh.setUVs(mesh._originalUVMap['texco'])
            mesh.setFaces(mesh.fvert, mesh._originalUVMap['fuvs'], faceGroups)
            mesh._originalUVMap = None
        else:
            uvset = material.UVMap(filename)
            uvset.read(mesh, filename)

            if len(uvset.fuvs) != len(mesh.fuvs):
                raise NameError("The UV file %s is not valid for mesh %s. \
                Number of faces %d != %d" % (filename, mesh.name, \
                len(uvset.fuvs), len(mesh.fuvs)))

            mesh.setUVs(uvset.uvs)
            mesh.setFaces(mesh.fvert, uvset.fuvs, faceGroups)

        mesh.changeFaceMask(faceMask)
        mesh.updateIndexBuffer()

    def setShader(self, path):
        """
        Set shader
        Make sure the seed mesh is updated as well, so that visual appearence
        of the mesh remains consistent during dragging of target sliders.
        Because while dragging sliders, the original seed mesh is shown.
        """
        self.mesh.setShader(path)
        if self.isSubdivided() or self.isProxied():
            # Update seed mesh
            self.getSeedMesh().setShader(path)

    def setShaderParameter(self, name, value):
        """
        This method updates the shader parameters for the currently shown mesh
        object, but also that of the original seed mesh if it is subdivided or
        proxied.
        Use this method when you want to stream in shader parameters to human
        while sliders are being moved, because while dragging only the seed mesh
        is shown.
        """
        self.mesh.setShaderParameter(name, value)
        if self.isSubdivided() or self.isProxied():
            # Update seed mesh
            self.getSeedMesh().setShaderParameter(name, value)

    def setUVMap(self, filename):
        subdivided = self.isSubdivided()

        if subdivided:
            # Re-generate the subdivided mesh
            self.setSubdivided(False)

        # Remove stale subdivision cache if present
        self.__subdivisionMesh = None

        # Set uv map on original, unsubdivided, unproxied mesh
        self._setMeshUVMap(filename, self.__seedMesh)

        if self.isProxied():
            # TODO transfer UV coordinates to proxy mesh
            pass

        if subdivided:
            # Re-generate the subdivided mesh with new UV coordinates
            self.setSubdivided(True)

    # TODO store material in this object instead of in mesh
    def setMaterial(self, material):
        self.setUVMap(material.uvMap)
        self.mesh.setMaterial(material)
        self.__seedMesh.setMaterial(material)

    def getMaterial(self):
        return self.mesh.getMaterial()

    material = property(getMaterial, setMaterial)

    def onMouseDown(self, event):
        if self.view:
            self.view.callEvent('onMouseDown', event)
        else:
            import log
            log.debug('FAILED: mouseDown')

    def onMouseMoved(self, event):
        if self.view:
            self.view.callEvent('onMouseMoved', event)
        else:
            import log
            log.debug('FAILED: mouseMoved')

    def onMouseDragged(self, event):
        if self.view:
            self.view.callEvent('onMouseDragged', event)
        else:
            import log
            log.debug('FAILED: mouseDragged')

    def onMouseUp(self, event):
        if self.view:
            self.view.callEvent('onMouseUp', event)

    def onMouseEntered(self, event):
        if self.view:
            self.view.callEvent('onMouseEntered', event)
        else:
            import log
            log.debug('FAILED: mouseEntered')

    def onMouseExited(self, event):
        if self.view:
            self.view.callEvent('onMouseExited', event)
        else:
            import log
            log.debug('FAILED: mouseExited')

    def onClicked(self, event):
        if self.view:
            self.view.callEvent('onClicked', event)
        else:
            import log
            log.debug('FAILED: clicked')

    def onMouseWheel(self, event):
        if self.view:
            self.view.callEvent('onMouseWheel', event)

