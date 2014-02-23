#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers, Glynn Clements, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import weakref

import numpy as np
import unique # Bugfix for numpy.unique on older numpy versions

import matrix
import material

class FaceGroup(object):
    """
    A FaceGroup (a group of faces with a unique name).

    Each Face object can be part of one FaceGroup. Each face object has an
    attribute, *group*, storing the FaceGroup it is a member of.

    The FaceGroup object contains a list of the faces in the group and must be
    kept in sync with the FaceGroup references stored by the individual faces.
    
    .. py:attribute:: name
    
        The name. str
        
    .. py:attribute:: parent
    
        The parent. :py:class:`module3d.Object3D`

    :param name: The name of the group.
    :type name: str
    """

    black = np.zeros(3, dtype=np.uint8)

    def __init__(self, object, name, idx):
        self.object = object
        self.parent = object
        self.name = name
        self.idx = idx
        self.color = None
        self.colorID = self.black

    def __str__(self):
        """
        This method returns a string containing the name of the FaceGroup. This
        method is called when the object is passed to the 'print' function.

        **Parameters:** This method has no parameters.

        """

        return 'facegroup %s' % self.name

    def setColor(self, rgba):
        self.color = np.asarray(rgba, dtype = np.uint8)

    def getObject(self):
        if self.__object:
            return self.__object()
        else:
            return None
        
    def setObject(self, value):
        if value is None:
            self.__object = None
        else:
            # Ensure link to gui3d.object is weak to avoid circular references (which break garbage collection)
            self.__object = weakref.ref(value)
    
    object = property(getObject, setObject)

class Object3D(object):
    def __init__(self, objName, vertsPerPrimitive=4):
        self.clear()

        self.name = objName
        self.vertsPerPrimitive = vertsPerPrimitive
        self._loc = np.zeros(3)
        self.rot = np.zeros(3)
        self.scale = np.ones(3)
        self._faceGroups = []
        self._material = material.Material(objName+"_Material")  # Render material
        self._groups_rev = {}
        self.cameraMode = 0
        self._visibility = True
        self.pickable = False
        self.calculateTangents = True   # TODO disable when not needed by shader
        self.object3d = None
        self._priority = 0
        self.MAX_FACES = 8
        self.lockRotation = False   # Set to true to make the rotation of this object independent of the camera rotation

        # Cache used for retrieving vertex colors multiplied with material diffuse color
        self._old_diff = None
        self._r_color_diff = None

        self.__object = None

    def getLoc(self):
        return self._loc

    def setLoc(self, loc):
        self._loc = loc

    loc = property(getLoc, setLoc)

    def get_x(self):
        return self.loc[0]

    def set_x(self, x):
        self.loc[0] = x

    x = property(get_x, set_x)

    def get_y(self):
        return self.loc[1]

    def set_y(self, y):
        self.loc[1] = y

    y = property(get_y, set_y)

    def get_z(self):
        return self.loc[2]

    def set_z(self, z):
        self.loc[2] = z

    z = property(get_z, set_z)

    def get_rx(self):
        return self.rot[0]

    def set_rx(self, rx):
        self.rot[0] = rx

    rx = property(get_rx, set_rx)

    def get_ry(self):
        return self.rot[1]

    def set_ry(self, ry):
        self.rot[1] = ry

    ry = property(get_ry, set_ry)

    def get_rz(self):
        return self.rot[2]

    def set_rz(self, rz):
        self.rot[2] = rz

    rz = property(get_rz, set_rz)

    def get_sx(self):
        return self.scale[0]

    def set_sx(self, sx):
        self.scale[0] = sx

    sx = property(get_sx, set_sx)

    def get_sy(self):
        return self.scale[1]

    def set_sy(self, sy):
        self.scale[1] = sy

    sy = property(get_sy, set_sy)

    def get_sz(self):
        return self.scale[2]

    def set_sz(self, sz):
        self.scale[2] = sz

    sz = property(get_sz, set_sz)

    def getShaderChanged(self):
        return self.material.shaderChanged

    def setShaderChanged(self, shaderChanged):
        self.material.shaderChanged = shaderChanged

    shaderChanged = property(getShaderChanged, setShaderChanged)

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

    def getCenter(self):
        """
        Get center position of mesh using center of its bounding box.
        """
        bBox = self.calcBBox()
        bmin = np.asarray(bBox[0], dtype=np.float32)
        bmax = np.asarray(bBox[1], dtype=np.float32)
        return -(bmin + ((bmax - bmin)/2))

    def calcFaceNormals(self, ix = None):
        if ix is None:
            ix = np.s_[:]
        fvert = self.coord[self.fvert[ix]]
        v1 = fvert[:,0,:]
        v2 = fvert[:,1,:]
        v3 = fvert[:,2,:]
        va = v1 - v2
        vb = v2 - v3
        self.fnorm[ix] = np.cross(va, vb)

    def calcVertexNormals(self, ix = None):
        self.markCoords(ix, norm=True)
        if ix is None:
            ix = np.s_[:]

        vface = self.vface[ix]
        norms = self.fnorm[vface]
        norms *= np.arange(self.MAX_FACES)[None,:,None] < self.nfaces[ix][:,None,None]
        norms = np.sum(norms, axis=1)
        norms /= np.sqrt(np.sum(norms ** 2, axis=-1))[:,None]
        self.vnorm[ix] = norms

    def calcVertexTangents(self, ix = None):
        """
        Calculate vertex tangents using Lengyel’s Method.
        """
        if not self.has_uv:
            return
        self.markCoords(ix, norm=True)
        if ix is None:
            ix = np.s_[:]
            xLen = self.getVertexCount()
            f_ix = np.s_[:]
        else:
            xLen = len(ix)
            f_ix = np.unique(self.vface[ix])

        # This implementation is based on
        # http://www.terathon.com/code/tangent.html

        tan = np.zeros((xLen, 2, 3), dtype=np.float32)

        fvert = self.coord[self.fvert[f_ix]]
        v1 = fvert[:,0,:]
        v2 = fvert[:,1,:]
        v3 = fvert[:,2,:]

        x1 = v2[:,0] - v1[:,0]
        x2 = v3[:,0] - v1[:,0]
        y1 = v2[:,1] - v1[:,1]
        y2 = v3[:,1] - v1[:,1]
        z1 = v2[:,2] - v1[:,2]
        z2 = v3[:,2] - v1[:,2]

        fuv = self.texco[self.fuvs[f_ix]]
        w1 = fuv[:,0,:]
        w2 = fuv[:,1,:]
        w3 = fuv[:,2,:]

        s1 = w2[:,0] - w1[:,0]
        s2 = w3[:,0] - w1[:,0]
        t1 = w2[:,1] - w1[:,1]
        t2 = w3[:,1] = w1[:,1]

        # Prevent NANs because of borked up UV coordinates
        s1[np.argwhere(np.equal(s1, 0.0))] = 0.0000001
        s2[np.argwhere(np.equal(s2, 0.0))] = 0.0000001
        t1[np.argwhere(np.equal(t1, 0.0))] = 0.0000001
        t2[np.argwhere(np.equal(t2, 0.0))] = 0.0000001

        r = np.repeat(1.0, len(s1)) / ( (s1 * t2) - (s2 * t1) )
        sdir = np.zeros((self.getFaceCount(),3), dtype=np.float32)
        tdir = np.zeros((self.getFaceCount(),3), dtype=np.float32)
        sdir[f_ix] = np.column_stack( [ ( (t2 * x1) - (t1 * x2) ) * r,
                                        ( (t2 * y1) - (t1 * y2) ) * r,
                                        ( (t2 * z1) - (t1 * z2) ) * r  ] )
        tdir[f_ix] = np.column_stack( [ ( (s1 * x2) - (s1 * x2) ) * r,
                                        ( (s1 * y2) - (s2 * y1) ) * r,
                                        ( (s1 * z2) - (s2 * z1) ) * r  ] )

        tan[:,0] = np.sum(sdir[self.vface[ix]])
        tan[:,1] = np.sum(tdir[self.vface[ix]])

        # Gramm-Schmidt orthogonalize
        dotP = dot_v3(self.vnorm[ix], tan[:,0] )
        # Duplicate dot product value in 3 columns because scalar * (n x 3)
        # does not work
        dotP = np.tile(dotP, (3,1)).transpose().reshape(len(tan),3)
        self.vtang[ix,:3] = tan[:,0] - dotP * self.vnorm[ix]
        # Normalize
        self.vtang[ix,:3] /= np.sqrt(np.sum(self.vtang[ix,:3] ** 2, axis=-1))[:,None]

        # Determine Handedness as w parameter
        self.vtang[ix, 3] = 1.0
        indx = np.argwhere(np.less(dot_v3( \
                                     np.cross( \
                                           self.vnorm[ix], \
                                           tan[:,0]), \
                                     tan[:,1]), \
                                   0.0))
        self.vtang[ix,3][indx] = -1.0

    def getObject(self):
        if self.__object:
            return self.__object()
        else:
            return None
        
    def setObject(self, value):
        if value is None:
            self.__object = None
        else:
            # Ensure link to gui3d.object is weak to avoid circular references (which break garbage collection)
            self.__object = weakref.ref(value)
    
    object = property(getObject, setObject)
    
    @property
    def faceGroups(self):
        return iter(self._faceGroups)
        
    @property
    def faceGroupCount(self):
        return len(self._faceGroups)

    def clear(self):
        """
        Clears both local and remote data to repurpose this object
        """
    
        # Clear remote data
        self._faceGroups = []

        self._transparentPrimitives = 0

        self.fvert = []
        self.fnorm = []
        self.fuvs = []
        self.group = []
        self.face_mask = []

        self.coord = []
        self.vnorm = []
        self.vtang = []
        self.color = []
        self.texco = []
        self.vface = []
        self.nfaces = 0

        self.ucoor = False
        self.unorm = False
        self.utang = False
        self.ucolr = False
        self.utexc = False

        self.has_uv = False

        if hasattr(self, 'index'): del self.index
        if hasattr(self, 'grpix'): del self.grpix
        self.vmap = None
        self.tmap = None

        if hasattr(self, 'r_coord'): del self.r_coord
        if hasattr(self, 'r_texco'): del self.r_texco
        if hasattr(self, 'r_vnorm'): del self.r_vnorm
        if hasattr(self, 'r_vtang'): del self.r_vtang
        if hasattr(self, 'r_color'): del self.r_color
        if hasattr(self, 'r_faces'): del self.r_faces

    def setCoords(self, coords):
        nverts = len(coords)
        self.coord = np.asarray(coords, dtype=np.float32)
        self.vnorm = np.zeros((nverts, 3), dtype=np.float32)
        self.vtang = np.zeros((nverts, 4), dtype=np.float32)
        self.color = np.zeros((nverts, 4), dtype=np.uint8) + 255
        self.vface = np.zeros((nverts, self.MAX_FACES), dtype=np.uint32)
        self.nfaces = np.zeros(nverts, dtype=np.uint8)

        self.orig_coord = self.coord.copy()

        self.ucoor = True
        self.unorm = True
        self.utang = True
        self.ucolr = True

        self.markCoords(None, True, True, True)

    def getVertexCount(self):
        #return len(self.vface)
        return len(self.coord)

    def getCoords(self, indices = None):
        if indices is None:
            indices = np.s_[...]
        return self.coord[indices]

    def getNormals(self, indices = None):
        if indices is None:
            indices = np.s_[...]
        return self.vnorm[indices]

    def markCoords(self, indices = None, coor = False, norm = False, colr = False):
        if isinstance(indices, tuple):
            indices = indices[0]

        nverts = len(self.coord)

        if coor:
            if indices is None:
                self.ucoor = True
            else:
                if self.ucoor is False:
                    self.ucoor = np.zeros(nverts, dtype=bool)
                if self.ucoor is not True:
                    self.ucoor[indices] = True

        if norm:
            if indices is None:
                self.unorm = self.utang = True
            else:
                if self.unorm is False:
                    self.unorm = self.utang = np.zeros(nverts, dtype=bool)
                if self.unorm is not True:
                    self.unorm[indices] = True
                    self.utang[indices] = True

        if colr:
            if indices is None:
                self.ucolr = True
            else:
                if self.ucolr is False:
                    self.ucolr = np.zeros(nverts, dtype=bool)
                if self.ucolr is not True:
                    self.ucolr[indices] = True

    def changeCoords(self, coords, indices = None):
        self.markCoords(indices, coor=True)

        if indices is None:
            indices = np.s_[...]
        self.coord[indices] = coords

    def setUVs(self, uvs):
        self.texco = np.asarray(uvs, dtype=np.float32)
        self.utexc = True

    def getUVCount(self):
        return len(self.texco)

    def getUVs(self, indices = None):
        if indices is None:
            indices = np.s_[...]
        return self.texco[indices]

    def markUVs(self, indices = None):
        if isinstance(indices, tuple):
            indices = indices[0]

        ntexco = len(self.texco)

        if indices is None:
            self.utexc = True
        else:
            if self.utexc is False:
                self.utexc = np.zeros(ntexco, dtype=bool)
            if self.utexc is not True:
                self.utexc[indices] = True

    def setFaces(self, verts, uvs = None, groups = None, skipUpdate = False):
        nfaces = len(verts)

        self.fvert = np.empty((nfaces, self.vertsPerPrimitive), dtype=np.uint32)
        self.fnorm = np.zeros((nfaces, 3), dtype=np.float32)
        self.fuvs = np.zeros(self.fvert.shape, dtype=np.uint32)
        self.group = np.zeros(nfaces, dtype=np.uint16)
        self.face_mask = np.ones(nfaces, dtype=bool)

        if nfaces != 0:
            self.fvert[...] = verts
            if uvs is not None:
                self.fuvs[...] = uvs
            if groups is not None:
                self.group[...] = groups

        self.has_uv = uvs is not None

        if not skipUpdate:
            self._update_faces()

    def changeFaceMask(self, mask, indices = None):
        if indices is None:
            indices = np.s_[...]
        self.face_mask[indices] = mask

    def getFaceMask(self, indices = None):
        if indices is None:
            indices = np.s_[...]
        return self.face_mask[indices]

    def hasUVs(self):
        return self.has_uv

    def getFaceCount(self):
        return len(self.fvert)

    def getFaceVerts(self, indices = None):
        if indices is None:
            indices = np.s_[...]
        return self.fvert[indices]

    def getFaceUVs(self, indices = None):
        if indices is None:
            indices = np.s_[...]
        return self.fuvs[indices]

    def _update_faces(self):
        map_ = np.argsort(self.fvert.flat)
        vi = self.fvert.flat[map_]
        fi = np.mgrid[:self.fvert.shape[0],:self.fvert.shape[1]][0].flat[map_].astype(np.uint32)
        del map_
        ix, first = np.unique(vi, return_index=True)
        n = first[1:] - first[:-1]
        n = np.hstack((n, np.array([len(vi) - first[-1]])))
        self.nfaces[ix] = n.astype(np.uint8)
        try:
            for i in xrange(len(ix)):
                self.vface[ix[i],:n[i]] = fi[first[i]:][:n[i]]
        except Exception as e:
            import log
            log.error("Failed to index faces of mesh %s, you are probably loading a mesh with mixed nb of verts per face (do not mix tris and quads). Or your mesh has too many faces attached to one vertex (the maximum is %s-poles). In the second case, either increase MAX_FACES for this mesh, or improve the mesh topology. Original error message: (%s) %s", self.name, self.MAX_FACES, type(e), format(str(e)))
            raise RuntimeError('Incompatible mesh topology.')

    def updateIndexBuffer(self):
        self.updateIndexBufferVerts()
        self.updateIndexBufferFaces()

    def updateIndexBufferVerts(self):
        packed = self.fvert.astype(np.uint64) << 32
        packed |= self.fuvs
        packed = packed.reshape(-1)

        u, rev = np.unique(packed, return_inverse=True)
        del packed

        unwelded = u[:,None] >> np.array([[32,0]], dtype=np.uint64)
        unwelded = unwelded.astype(np.uint32)
        nverts = len(unwelded)
        iverts = rev.reshape(self.fvert.shape)
        del rev, u

        self.vmap = unwelded[:,0]
        self.tmap = unwelded[:,1]
        del unwelded

        self.r_coord = np.empty((nverts, 3), dtype=np.float32)
        self.r_texco = np.empty((nverts, 2), dtype=np.float32)
        self.r_vnorm = np.zeros((nverts, 3), dtype=np.float32)
        self.r_vtang = np.zeros((nverts, 4), dtype=np.float32)
        self.r_color = np.zeros((nverts, 4), dtype=np.uint8) + 255

        self.r_faces = np.array(iverts, dtype=np.uint32)

    def updateIndexBufferFaces(self):
        index = self.r_faces[self.face_mask]
        group = self.group[self.face_mask]

        if len(group) > 0:
            order = np.argsort(group)
            group = group[order]
            index = index[order]

            group, start = np.unique(group, return_index=True)
            count = np.empty(len(start), dtype=np.uint32)
            count[:-1] = start[1:] - start[:-1]
            count[-1] = len(index) - start[-1]

            grpix = np.zeros((max(self.group)+1,2), dtype=np.uint32)
            grpix[group,0] = start
            grpix[group,1] = count
        else:
            grpix = np.zeros((0,2), dtype=np.uint32)

        self.index = index
        self.grpix = grpix

        self.ucoor = True
        self.unorm = True
        self.utang = True
        self.ucolr = True
        self.utexc = True
        self.sync_all()

    def sync_coord(self):
        if self.ucoor is False:
            return
        if self.vmap is None or len(self.vmap) == 0:
            return
        if self.ucoor is True:
            self.r_coord[...] = self.coord[self.vmap]
        else:
            self.r_coord[self.ucoor[self.vmap]] = self.coord[self.vmap][self.ucoor[self.vmap]]
        self.ucoor = False

    def sync_norms(self):
        if self.unorm is False:
            return
        if self.vmap is None or len(self.vmap) == 0:
            return
        if self.unorm is True:
            self.r_vnorm[...] = self.vnorm[self.vmap]
        else:
            self.r_vnorm[self.unorm[self.vmap]] = self.vnorm[self.vmap][self.unorm[self.vmap]]
        self.unorm = False

    def sync_tangents(self):
        if not self.has_uv:
            return
        if self.utang is False:
            return
        if self.vmap is None or len(self.vmap) == 0:
            return
        if self.utang is True:
            self.r_vtang[...] = self.vtang[self.vmap]
        else:
            self.r_vtang[self.utang[self.vmap]] = self.vtang[self.vmap][self.utang[self.vmap]]
        self.utang = False

    def sync_color(self):
        if self.ucolr is False:
            return
        if self.vmap is None or len(self.vmap) == 0:
            return
        if self.ucolr is True:
            self.r_color[...] = self.color[self.vmap]
        else:
            self.r_color[self.ucolr[self.vmap]] = self.color[self.vmap][self.ucolr[self.vmap]]
        self.ucolr = False
        self._r_color_diff = None

    def sync_texco(self):
        if not self.has_uv:
            return
        if self.utexc is False:
            return
        if self.tmap is None or len(self.tmap) == 0:
            return
        if self.utexc is True:
            self.r_texco[...] = self.texco[self.tmap]
        else:
            self.r_texco[self.utexc[self.tmap]] = self.texco[self.tmap][self.utexc[self.tmap]]
        self.utexc = False

    def sync_all(self):
        self.sync_coord()
        self.sync_norms()
        if self.calculateTangents:
            self.sync_tangents()
        self.sync_color()
        self.sync_texco()

    def createFaceGroup(self, name):
        """
        Creates a new module3d.FaceGroup with the given name.

        :param name: The name for the face group.
        :type name: [float, float, float]
        :return: The new face group.
        :rtype: :py:class:`module3d.FaceGroup`
        """
        idx = len(self._faceGroups)
        fg = FaceGroup(self, name, idx)
        self._groups_rev[name] = fg
        self._faceGroups.append(fg)
        return fg

    def setColor(self, color):
        """
        Sets the color for the entire object.

        :param color: The color in rgba.
        :type color: [byte, byte, byte, byte]
        """
        color = np.asarray(color, dtype=np.uint8)
        if len(color.shape) == 1:   # One color for all vertices
            if len(color) == 3:
                # Add alpha component to simple RGB color
                color = list(color) + [255]
            self.color[:] = color
        else:
            self.color[...] = color[None,:]
        self.markCoords(colr=True)
        self.sync_color()

    @property
    def r_color_diff(self):
        """
        Vertex colors multiplied with the diffuse material color.
        """
        if self._r_color_diff is None:
            self._r_color_diff = np.zeros(self.r_color.shape, dtype = np.uint8)
            self._old_diff = None

        diff = self.material.diffuseColor.values + [self.material.opacity]
        if diff != self._old_diff:
            # Update diffuse * vertex colors
            self._r_color_diff[:] = diff * self.r_color
            self._old_diff = diff
        return self._r_color_diff


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

        self.loc[...] = (locx, locy, locz)

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

        self.rot[...] = (rx, ry, rz)

    def setScale(self, sx, sy, sz):
        """
        This method sets the scale of the object in the 3D coordinate space of
        the scene, relative to the initially defined size of the object.

        :param sx: Scale along the x-axis.
        :type sx: float
        :param sy: Scale along the x-axis.
        :type sy: float
        :param sz: Scale along the x-axis.
        :type sz: float
        """

        self.scale[...] = (sx, sy, sz)

    @property
    def visibility(self):
        return self._visibility

    def setVisibility(self, visible):
        self.visibility = visible

    @visibility.setter
    def visibility(self, visible):
        """
        This method sets the visibility of the object.

        :param visible: Whether or not the object is visible.
        :type visible: Boolean
        """
        self._visibility = visible

    def setPickable(self, pickable):
        """
        This method sets the pickable flag of the object.

        :param pickable: Whether or not the object is pickable.
        :type pickable: Boolean
        """

        self.pickable = pickable

    def setTexture(self, path):
        """
        This method is used to specify the path of a file on disk containing the object texture.

        :param path: The path of a texture file.
        :type path: str
        :param cache: The texture cache to use.
        :type cache: dict
        """
        self.material.diffuseTexture = path

    def clearTexture(self):
        """
        This method is used to clear an object's texture.
        """
        self.material.diffuseTexture = None

    @property
    def texture(self):
        return self.material.diffuseTexture

    def hasTexture(self):
        return self.texture is not None

    def setShader(self, shader):
        """
        This method is used to specify the shader.
        
        :param shader: The path to a pair of shader files.
        :type shader: string
        """
        self.material.setShader(shader)

    @property
    def shader(self):
        return self.material.shader

    @property
    def shaderObj(self):
        return self.material.shaderObj

    def configureShading(self, diffuse=None, bump = None, normal=None, displacement=None, spec = None, vertexColors = None):
        """
        Configure shader options and set the necessary properties based on
        the material configuration of this object.
        This can be done without an actual shader being set for this object.
        Call this method when changes are made to the material property.
        """
        self.material.configureShading(diffuse, bump, normal, displacement, spec, vertexColors)

    def getMaterial(self):
        return self._material

    def setMaterial(self, material):
        self._material.copyFrom(material)

    material = property(getMaterial, setMaterial)

    def setShaderParameter(self, name, value):
        self.material.setShaderParameter(name, value)

    @property
    def shaderParameters(self):
        return self.material.shaderParameters

    @property
    def shaderConfig(self):
        return self.material.shaderConfig

    @property
    def shaderDefines(self):
        return self.material.shaderDefines

    def addShaderDefine(self, defineStr):
        self.material.addShaderDefine(defineStr)

    def removeShaderDefine(self, defineStr):
        self.material.removeShaderDefine(defineStr)

    def clearShaderDefines(self):
        self.material.clearShaderDefines()

    def setShadeless(self, shadeless):
        """
        This method is used to specify whether or not the object is affected by lights.
        This is used for certain GUI controls to give them a more 2D type
        appearance (predominantly the top bar of GUI controls).

        NOTE enabling this option disables the use of the shader configured in the material.

        :param shadeless: Whether or not the object is unaffected by lights.
        :type shadeless: Boolean
        """
        self.material.shadeless = shadeless

    def getShadeless(self):
        return self.material.shadeless

    shadeless = property(getShadeless, setShadeless)

    def setCull(self, cull):
        """
        This method is used to specify whether or not the object is back-face culled.

        :param cull: Whether and how to cull
        :type cull: 0 => no culling, >0 => draw front faces, <0 => draw back faces
        """

        # Because we don't really need frontface culling, we simplify to only backface culling
        if (isinstance(cull, bool) and cull) or cull > 0:
            self.material.backfaceCull = True
        else:
            self.material.backfaceCull = False

    def getCull(self):
        # Because we don't really need frontface culling, we simplify to only backface culling
        if self.material.backfaceCull:
            return 1
        else:
            return 0

    cull = property(getCull, setCull)

    def getPriority(self):
        """
        The rendering priority of this object.
        Objects with higher priorities will be drawn later.

        Common priorities used:
        file                                 description       2D/3D priority

        0_modeling_background.py             background          2D    -90
        core/mhmain.py                       human               3D      0
        3_libraries_clothes_chooser.py       clothing            3D     10
        3_libraries_polygon_hair_chooser.py  hair                3D     20
        2_posing_armature.py                 armature            3D     30
        0_modeling_a_measurement.py          measureMesh         2D     50
        5_settings_censor.py                 censor rectangles   2D     80
        apps/gui/guifiles.py                 black frame         2D     90
        """
        return self._priority

    def setPriority(self, priority):
        """
        Set the rendering priority of this object.
        Objects with higher priorities will be drawn later.

        Common priorities used:
        file                                 description       2D/3D priority

        0_modeling_background.py             background          2D    -90
        core/mhmain.py                       human               3D      0
        3_libraries_clothes_chooser.py       clothing            3D     10
        3_libraries_polygon_hair_chooser.py  hair                3D     20
        2_posing_armature.py                 armature            3D     30
        0_modeling_a_measurement.py          measureMesh         2D     50
        5_settings_censor.py                 censor rectangles   2D     80
        apps/gui/guifiles.py                 black frame         2D     90
        """
        self._priority = priority

    priority = property(getPriority, setPriority)

    def setDepthless(self, depthless):
        """
        This method is used to specify whether or not the object occludes or is occluded
        by other objects

        :param depthless: Whether or not the object is occluded or occludes.
        :type depthless: Boolean
        """
        self.material.depthless = depthless

    def getDepthless(self):
        return self.material.depthless

    depthless = property(getDepthless, setDepthless)

    def setSolid(self, solid):
        """
        This method is used to specify whether or not the object is drawn solid or wireframe.

        :param solid: Whether or not the object is drawn solid or wireframe.
        :type solid: Boolean
        """
        self.material.wireframe = not solid

    def getSolid(self):
        return not self.material.wireframe

    solid = property(getSolid, setSolid)
            
    def setTransparentPrimitives(self, transparentPrimitives):
        """
        This method is used to specify the amount of transparent faces.
        This property is overridden if self.material.transparent is set to True.

        :param transparentPrimitives: The amount of transparent faces.
        :type transparentPrimitives: int
        """
        self._transparentPrimitives = transparentPrimitives

    def getTransparentPrimitives(self):
        # Object allows transparency rendering of only a subset (starting from 
        # the first face) of faces of the mesh, but material property transparent
        # set to True overrides this and makes all faces render with transparency technique
        if self.material.transparent:
            return len(self.fvert)
        else:
            return self._transparentPrimitives

    transparentPrimitives = property(getTransparentPrimitives, setTransparentPrimitives)

    def getAlphaToCoverage(self):
        return self.material.alphaToCoverage

    def setAlphaToCoverage(self, a2cEnabled):
        self.material.alphaToCoverage = a2cEnabled

    alphaToCoverage = property(getAlphaToCoverage, setAlphaToCoverage)

    def getFaceGroup(self, name):
        """
        This method searches the list of FaceGroups held for this object, and
        returns the FaceGroup with the specified name. If no FaceGroup is found
        for that name, this method returns None.

        :param name: The name of the FaceGroup to retrieve.
        :type name: str
        :return: The FaceGroup if found, None otherwise.
        :rtype: :py:class:`module3d.FaceGroup`
        """

        return self._groups_rev.get(name, None)

    def getGroupMaskForGroups(self, groupNames):
        groups = np.zeros(len(self._faceGroups), dtype=bool)
        for name in groupNames:
            groups[self._groups_rev[name].idx] = True
        return groups

    def getFaceMaskForGroups(self, groupNames):
        groups = self.getGroupMaskForGroups(groupNames)
        face_mask = groups[self.group]
        return face_mask

    def getFacesForGroups(self, groupNames):
        face_mask = self.getFaceMaskForGroups(groupNames)
        faces = np.argwhere(face_mask)[...,0]
        return faces

    def getVertexMaskForGroups(self, groupNames):
        face_mask = self.getFaceMaskForGroups(groupNames)
        verts = self.fvert[face_mask]
        vert_mask = np.zeros(len(self.coord), dtype = bool)
        vert_mask[verts] = True
        return vert_mask

    def getVerticesForGroups(self, groupNames):
        vert_mask = self.getVertexMaskForGroups(groupNames)
        verts = np.argwhere(vert_mask)[...,0]
        return verts

    def getVerticesForFaceMask(self, face_mask):
        verts = self.fvert[face_mask]
        verts = verts.reshape(-1)
        return verts

    def getVertexMaskForFaceMask(self, face_mask):
        verts = self.getVerticesForFaceMask(face_mask)
        vert_mask = np.zeros(len(self.coord), dtype = bool)
        vert_mask[verts] = True
        return vert_mask

    def getVertexAndFaceMasksForGroups(self, groupNames):
        face_mask = self.getFaceMaskForGroups(groupNames)
        verts = self.fvert[face_mask]
        vert_mask = np.zeros(len(self.coord), dtype = bool)
        vert_mask[verts] = True
        return vert_mask, face_mask

    def getFaceMaskForVertices(self, verts):
        mask = np.zeros(len(self.fvert), dtype = bool)
        valid = np.arange(self.MAX_FACES)[None,:] < self.nfaces[verts][:,None]
        vface = self.vface[verts]
        faces = vface[valid]
        mask[faces] = True
        return mask

    def getFacesForVertices(self, verts):
        return np.argwhere(self.getFaceMaskForVertices(verts))[...,0]

    def setCameraProjection(self, cameraMode):
        """
        This method sets the camera mode used to visualize this object (fixed or movable).
        The 3D engine has two camera modes (both perspective modes).
        The first is moved by the mouse, while the second is fixed.
        The first is generally used to model 3D objects (a human, clothes,
        etc.), while the second is used for 3D GUI controls.

        :param cameraMode: The camera mode. 0 = movable camera (modelCamera);
        1 = static camera (guiCamera).
        :type cameraMode: int
        """

        self.cameraMode = cameraMode

    def update(self):
        """
        This method is used to call the update methods on each of a list of vertices or all vertices that form part of this object.
        """
        self.sync_all()

    def calcNormals(self, recalcVertexNormals=1, recalcFaceNormals=1, verticesToUpdate=None, facesToUpdate=None):
        """
        Updates the given vertex and/or face normals.
        
        :param recalcVertexNormals: A flag to indicate whether or not the vertex normals should be recalculated.
        :type recalcVertexNormals: Boolean
        :param recalcFaceNormals: A flag to indicate whether or not the face normals should be recalculated.
        :type recalcFaceNormals: Boolean
        :param verticesToUpdate: The list of vertices to be updated, if None all vertices are updated.
        :type verticesToUpdate: list of :py:class:`module3d.Vert`
        :param facesToUpdate: The list of faces to be updated, if None all faces are updated.
        :type facesToUpdate: list of :py:class:`module3d.Face`
        """

        if recalcFaceNormals:
            self.calcFaceNormals(facesToUpdate)

        if recalcVertexNormals:
            self.calcVertexNormals(verticesToUpdate)

        if recalcFaceNormals or recalcVertexNormals and self.calculateTangents:
            self.calcVertexTangents(verticesToUpdate)
                
    def calcBBox(self, ix=None, onlyVisible = True, fixedFaceMask = None):
        """
        Calculates the axis aligned bounding box of this object in the object's coordinate system. 
        """
        # TODO maybe cache bounding box
        if ix is None:
            ix = np.s_[:]
        if fixedFaceMask is not None:
            verts = self.getVerticesForFaceMask(fixedFaceMask)
            coord = self.coord[verts]
        elif onlyVisible:
            verts = self.getVerticesForFaceMask(self.getFaceMask())
            coord = self.coord[verts]
        else:
            coord = self.coord[ix]
        if len(coord) == 0:
            return np.zeros((2,3), dtype = np.float32)
        v0 = np.amin(coord, axis=0)
        v1 = np.amax(coord, axis=0)
        return np.vstack((v0, v1))

    def __str__(self):
        x, y, z = self.loc
        return 'object3D named: %s, nverts: %s, nfaces: %s, at |%s,%s,%s|' % (self.name, self.getVertexCount(), self.getFaceCount(), x, y, z)

def dot_v3(v3_arr1, v3_arr2):
    """
    Numpy Ufunc'ed implementation of a series of dot products of two vector3 
    objects.
    """
    return (v3_arr1[:,0] * v3_arr2[:,0]) + \
           (v3_arr1[:,1] * v3_arr2[:,1]) + \
           (v3_arr2[:,2] * v3_arr1[:,2])

