#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

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

TODO
"""

import os
import math
import numpy as np
import guicommon
from core import G
import getpath
import log
from collections import OrderedDict

import material
import io_json


#
#   Proxy types. Loop over simple proxy types to do all proxies.
#   Some code use lowercase proxy types instead.
#

SimpleProxyTypes = ['Hair', 'Eyes', 'Genitals', 'Eyebrows', 'Eyelashes', 'Teeth', 'Tongue']
ProxyTypes = ['Proxymeshes', 'Clothes'] + SimpleProxyTypes

SimpleProxyTypesLower = []
for name in SimpleProxyTypes:
    SimpleProxyTypesLower.append(name.lower())

#
#
#

_A7converter = None
Unit3 = np.identity(3,float)

#
#   class ProxyRefVert:
#

class ProxyRefVert:

    def __init__(self, parent):
        self._parent = parent


    def fromSingle(self, words, vnum, proxy):
        self._exact = True
        v0 = int(words[0])
        self._verts = [v0]
        self._weights = [1]
        self._offset = np.zeros(3, float)
        self.addProxyVertWeight(proxy, v0, vnum, 1)
        return self


    def fromTriple(self, words, vnum, proxy):
        self._exact = False
        v0 = int(words[0])
        v1 = int(words[1])
        v2 = int(words[2])
        w0 = float(words[3])
        w1 = float(words[4])
        w2 = float(words[5])
        if len(words) > 6:
            d0 = float(words[6])
            d1 = float(words[7])
            d2 = float(words[8])
        else:
            (d0,d1,d2) = (0,0,0)

        self._verts = (v0,v1,v2)
        self._weights = (w0,w1,w2)
        self._offset = np.array((d0,d1,d2), float)

        self.addProxyVertWeight(proxy, v0, vnum, w0)
        self.addProxyVertWeight(proxy, v1, vnum, w1)
        self.addProxyVertWeight(proxy, v2, vnum, w2)
        return self


    def addProxyVertWeight(self, proxy, v, pv, w):
        try:
            proxy.vertWeights[v].append((pv, w))
        except KeyError:
            proxy.vertWeights[v] = [(pv,w)]
        return

    def getHumanVerts(self):
        return self._verts

    def getWeights(self):
        return self._weights

    def getCoord(self, matrix):
        coord = np.dot(matrix, self._offset)
        for n,rvn in enumerate(self._verts):
            xn = self._parent.coord[rvn]
            wn = self._weights[n]
            coord += xn*wn
        return coord


    def getConvertedCoord(self, converter, matrix):
        coord = np.dot(matrix, self._offset)
        for n,rvn in enumerate(self._verts):
            xn = converter.refVerts[rvn].getCoord(Unit3)
            wn = self._weights[n]
            coord += xn*wn
        return coord

#
#   class TMatrix:
#   Transformation matrix. Replaces previous scale
#

class TMatrix:
    def __init__(self):
        self.scaleData = None
        self.shearData = None
        self.lShearData = None
        self.rShearData = None


    def getScaleData(self, words, obj, idx):
        vn1 = int(words[1])
        vn2 = int(words[2])
        den = float(words[3])
        if not self.scaleData:
            self.scaleData = [None, None, None]
        self.scaleData[idx] = (vn1, vn2, den)


    def getShearData(self, words, obj, idx, side):
        vn1 = int(words[1])
        vn2 = int(words[2])
        x1 = float(words[3])
        x2 = float(words[4])
        bbdata = (vn1, vn2, x1, x2, side)
        if side == "Left":
            if not self.lShearData:
                self.lShearData = [None, None, None]
            self.lShearData[idx] = bbdata
        elif side == "Right":
            if not self.rShearData:
                self.rShearData = [None, None, None]
            self.rShearData[idx] = bbdata
        else:
            if not self.shearData:
                self.shearData = [None, None, None]
            self.shearData[idx] = bbdata


    def getMatrix(self, refvert=None, converter=None):
        obj = G.app.selectedHuman.meshData  # TODO human object to use is hardcoded, pass as arg instead
        if self.scaleData:
            matrix = np.identity(3, float)
            for n in range(3):
                (vn1, vn2, den) = self.scaleData[n]
                if converter:
                    co1 = converter.refVerts[vn1].getCoord(Unit3)
                    co2 = converter.refVerts[vn2].getCoord(Unit3)
                else:
                    co1 = obj.coord[vn1]
                    co2 = obj.coord[vn2]
                num = abs(co1[n] - co2[n])
                matrix[n][n] = (num/den)
            return matrix

        elif self.shearData:
            return self.matrixFromShear(self.shearData, obj)
        elif self.lShearData:
            return self.matrixFromShear(self.lShearData, obj)
        elif self.rShearData:
            return self.matrixFromShear(self.rShearData, obj)
        else:
            return Unit3


    def matrixFromShear(self, shear, obj):

        # sfaces and tfaces are the face coordinates
        sfaces = np.zeros((3,2), float)
        tfaces = np.zeros((3,2), float)
        for n in range(3):
            (vn1, vn2, sfaces[n,0], sfaces[n,1], side) = shear[n]
            tfaces[n,0] = obj.coord[vn1][n]
            tfaces[n,1] = obj.coord[vn2][n]

        # sverts and tverts are the vertex coordinates
        sverts = []
        tverts = []
        for i in [0,1]:
            for j,k in [(0,0),(0,1),(1,1),(1,0)]:
                sverts.append( np.array((sfaces[0,i], sfaces[1,j], sfaces[2,k])) )
                tverts.append( np.array((tfaces[0,i], tfaces[1,j], tfaces[2,k])) )

        sbox = vertsToNumpy(sverts)
        tbox = vertsToNumpy(tverts)
        mat = affine_matrix_from_points(sbox, tbox)
        return mat[:3,:3]


def vertsToNumpy(verts):
    result = np.asarray(verts)
    return np.asarray([result[:,0], result[:,1], result[:,2]], dtype=np.float32)


# TODO is there a reason this method is copied from transformations.py ?
def affine_matrix_from_points(v0, v1, shear=True, scale=True, usesvd=True):
    """Return affine transform matrix to register two point sets.

    v0 and v1 are shape (ndims, \*) arrays of at least ndims non-homogeneous
    coordinates, where ndims is the dimensionality of the coordinate space.

    If shear is False, a similarity transformation matrix is returned.
    If also scale is False, a rigid/Euclidean transformation matrix
    is returned.

    By default the algorithm by Hartley and Zissermann [15] is used.
    If usesvd is True, similarity and Euclidean transformation matrices
    are calculated by minimizing the weighted sum of squared deviations
    (RMSD) according to the algorithm by Kabsch [8].
    Otherwise, and if ndims is 3, the quaternion based algorithm by Horn [9]
    is used, which is slower when using this Python implementation.

    The returned matrix performs rotation, translation and uniform scaling
    (if specified).

    >>> v0 = [[0, 1031, 1031, 0], [0, 0, 1600, 1600]]
    >>> v1 = [[675, 826, 826, 677], [55, 52, 281, 277]]
    >>> affine_matrix_from_points(v0, v1)
    array([[   0.14549,    0.00062,  675.50008],
           [   0.00048,    0.14094,   53.24971],
           [   0.     ,    0.     ,    1.     ]])
    >>> T = translation_matrix(np.random.random(3)-0.5)
    >>> R = random_rotation_matrix(np.random.random(3))
    >>> S = scale_matrix(random.random())
    >>> M = concatenate_matrices(T, R, S)
    >>> v0 = (np.random.rand(4, 100) - 0.5) * 20
    >>> v0[3] = 1
    >>> v1 = np.dot(M, v0)
    >>> v0[:3] += np.random.normal(0, 1e-8, 300).reshape(3, -1)
    >>> M = affine_matrix_from_points(v0[:3], v1[:3])
    >>> np.allclose(v1, np.dot(M, v0))
    True

    More examples in superimposition_matrix()

    """
    v0 = np.array(v0, dtype=np.float64, copy=True)
    v1 = np.array(v1, dtype=np.float64, copy=True)

    ndims = v0.shape[0]
    if ndims < 2 or v0.shape[1] < ndims or v0.shape != v1.shape:
        raise ValueError("input arrays are of wrong shape or type")

    # move centroids to origin
    t0 = -np.mean(v0, axis=1)
    M0 = np.identity(ndims+1)
    M0[:ndims, ndims] = t0
    v0 += t0.reshape(ndims, 1)
    t1 = -np.mean(v1, axis=1)
    M1 = np.identity(ndims+1)
    M1[:ndims, ndims] = t1
    v1 += t1.reshape(ndims, 1)

    if shear:
        # Affine transformation
        A = np.concatenate((v0, v1), axis=0)
        u, s, vh = np.linalg.svd(A.T)
        vh = vh[:ndims].T
        B = vh[:ndims]
        C = vh[ndims:2*ndims]
        t = np.dot(C, np.linalg.pinv(B))
        t = np.concatenate((t, np.zeros((ndims, 1))), axis=1)
        M = np.vstack((t, ((0.0,)*ndims) + (1.0,)))
    elif usesvd or ndims != 3:
        # Rigid transformation via SVD of covariance matrix
        u, s, vh = np.linalg.svd(np.dot(v1, v0.T))
        # rotation matrix from SVD orthonormal bases
        R = np.dot(u, vh)
        if np.linalg.det(R) < 0.0:
            # R does not constitute right handed system
            R -= np.outer(u[:, ndims-1], vh[ndims-1, :]*2.0)
            s[-1] *= -1.0
        # homogeneous transformation matrix
        M = np.identity(ndims+1)
        M[:ndims, :ndims] = R
    else:
        # Rigid transformation matrix via quaternion
        # compute symmetric matrix N
        xx, yy, zz = np.sum(v0 * v1, axis=1)
        xy, yz, zx = np.sum(v0 * np.roll(v1, -1, axis=0), axis=1)
        xz, yx, zy = np.sum(v0 * np.roll(v1, -2, axis=0), axis=1)
        N = [[xx+yy+zz, 0.0,      0.0,      0.0],
             [yz-zy,    xx-yy-zz, 0.0,      0.0],
             [zx-xz,    xy+yx,    yy-xx-zz, 0.0],
             [xy-yx,    zx+xz,    yz+zy,    zz-xx-yy]]
        # quaternion: eigenvector corresponding to most positive eigenvalue
        w, V = np.linalg.eigh(N)
        q = V[:, np.argmax(w)]
        q /= vector_norm(q)  # unit quaternion
        # homogeneous transformation matrix
        M = quaternion_matrix(q)

    if scale and not shear:
        # Affine transformation; scale is ratio of RMS deviations from centroid
        v0 *= v0
        v1 *= v1
        M[:ndims, :ndims] *= math.sqrt(np.sum(v1) / np.sum(v0))

    # move centroids back
    M = np.dot(np.linalg.inv(M1), np.dot(M, M0))
    M /= M[ndims, ndims]
    return M

#
#    class Proxy
#

class Proxy:
    def __init__(self, file, type):
        log.debug("Loading proxy file: %s.", file)
        import makehuman

        name = os.path.splitext(os.path.basename(file))[0]
        self.name = name.capitalize().replace(" ","_")
        self.type = type
        self.file = file
        if file:
            self.mtime = os.path.getmtime(file)
        else:
            self.mtime = None
        self.uuid = None
        self.basemesh = makehuman.getBasemeshVersion()
        self.tags = []

        self.vertWeights = {}       # (proxy-vert, weight) list for each parent vert
        self.refVerts = []

        self.tmatrix = TMatrix()    # Offset transformation matrix. Replaces scale

        self.z_depth = 50
        self.max_pole = None    # Signifies the maximum number of faces per vertex on the mesh topology. Set to none for default.
        self.cull = False

        self.uvLayers = {}

        self.useBaseMaterials = False
        self.rig = None
        self.mask = None

        self.material = material.Material(self.name)

        self.obj_file = None
        self.vertexgroup_file = None
        self.vertexGroups = None
        self.material_file = None
        self.mhxMaterial_file = None
        self.maskLayer = -1
        self.textureLayer = 0
        self.objFileLayer = 0   # TODO what is this used for?
        self.texVertsLayers = {}
        self.texFacesLayers = {}

        self.deleteGroups = []
        self.deleteVerts = None

        self.wire = False
        self.cage = False
        self.modifiers = []
        self.shapekeys = []
        self.weights = None
        self.clothings = []
        self.transparencies = dict()
        return


    def __repr__(self):
        return ("<Proxy %s %s %s %s>" % (self.name, self.type, self.file, self.uuid))


    def getSeedMesh(self):
        human = G.app.selectedHuman
        for proxy,obj in human.getProxiesAndObjects():
            if self == proxy:
                return obj.getSeedMesh()

        if self.type == "Proxymeshes":
            if not human.proxy:
                return None
            #return human.mesh
            return human.getProxyMesh()
        elif self.type in ["Cage", "Converter"]:
            return None
        else:
            raise NameError("Unknown proxy type %s" % self.type)


    def getMesh(self):
        human = G.app.selectedHuman
        for proxy,obj in human.getProxiesAndObjects():
            if self == proxy:
                return obj.mesh

        if self.type == "Proxymeshes":
            if not human.proxy:
                return None
            return human.mesh
        elif self.type in ["Cage", "Converter"]:
            return None
        else:
            raise NameError("Unknown proxy type %s" % self.type)


    def getActualTexture(self, human):
        uuid = self.getUuid()
        mesh = None

        if human.proxy and uuid == human.proxy.uuid:
            mesh = human.mesh
        else:
            for proxy,obj in human.getProxiesAndObjects():
                if proxy and uuid == proxy.uuid:
                    mesh = obj.mesh
                    break

        return getpath.formatPath(mesh.texture)

    def _finalize(self, obj):
        """
        Final step in parsing/loading a proxy file. Initializes numpy structures
        for performance improvement.
        """
        self.n_refpoints = len(self.refVerts[0]._verts)
        self.obj = obj
        self.weights = np.asarray([v._weights for v in self.refVerts], dtype=np.float32)
        self.ref_vIdxs = np.asarray([v._verts for v in self.refVerts], dtype=np.uint32)
        self.offsets = np.asarray([v._offset for v in self.refVerts], dtype=np.float32)

    def getCoords(self):
        converter = self.getConverter()
        matrix = self.tmatrix.getMatrix(refvert=self.refVerts[0], converter=converter)
        if converter:
            return [refVert.getConvertedCoord(converter, matrix) for refVert in self.refVerts]
        else:
            obj = self.obj
            ref_vIdxs = self.ref_vIdxs
            weights = self.weights

            if self.n_refpoints == 3:
                coord = obj.coord[ref_vIdxs[:,0]] * weights[:,0,None] + \
                        obj.coord[ref_vIdxs[:,1]] * weights[:,1,None] + \
                        obj.coord[ref_vIdxs[:,2]] * weights[:,2,None]
            else:
                coord = obj.coord[ref_vIdxs[:,0]] * weights[:,0,None]

            coord += np.dot(matrix, self.offsets.transpose()).transpose()

            return coord


    def update(self, obj):
        log.debug("Updating proxy %s.", self.name)
        coords = self.getCoords()
        obj.changeCoords(coords)
        obj.calcNormals()


    def getUuid(self):
        if self.uuid:
            return self.uuid
        else:
            return self.name


    def getConverter(self):
        import makehuman
        if self.basemesh in ["alpha_7", "alpha7"]:
            global _A7converter
            if _A7converter is None:
                _A7converter = readProxyFile(G.app.selectedHuman.meshData, getpath.getSysDataPath("3dobjs/a7_converter.proxy"), type="Converter")
            log.debug("Converting %s with %s", self.name, _A7converter)
            return _A7converter
        elif self.basemesh == makehuman.getBasemeshVersion():
            return None
        else:
            raise NameError("Unknown basemesh for mhclo file: %s" % self.basemesh)


    def getWeights(self, rawWeights, amt=None):
        if amt and self.vertexGroups:
            weights = OrderedDict()
            for name,data in self.vertexGroups:
                for bone in amt.bones.values():
                    if bone.origName == name:
                        name1 = bone.name
                        break
                for name2 in [
                    "DEF-"+name1,
                    "DEF-"+name1.replace(".L", ".03.L"),
                    "DEF-"+name1.replace(".R", ".03.R"),
                    name1]:
                    if name2 in rawWeights:
                        weights[name2] = data
                        break
            return weights

        converter = self.getConverter()
        if converter:
            rawWeights = converter.getWeights1(rawWeights)
        return self.getWeights1(rawWeights)


    def getWeights1(self, rawWeights):
        weights = OrderedDict()
        if not rawWeights:
            return weights

        for key in rawWeights.keys():
            vgroup = []
            empty = True
            for (v,wt) in rawWeights[key]:
                try:
                    vlist = self.vertWeights[v]
                except KeyError:
                    vlist = []
                for (pv, w) in vlist:
                    pw = w*wt
                    if (pw > 1e-4):
                        vgroup.append((pv, pw))
                        empty = False
            if not empty:
                weights[key] = self.fixVertexGroup(vgroup)
        return weights


    def fixVertexGroup(self, vgroup):
        fixedVGroup = []
        vgroup.sort()
        pv = -1
        while vgroup:
            (pv0, wt0) = vgroup.pop()
            if pv0 == pv:
                wt += wt0
            else:
                if pv >= 0 and wt > 1e-4:
                    fixedVGroup.append((pv, wt))
                (pv, wt) = (pv0, wt0)
        if pv >= 0 and wt > 1e-4:
            fixedVGroup.append((pv, wt))
        return fixedVGroup


    def getShapes(self, rawShapes, scale):
        from richmesh import FakeTarget

        targets = []
        if (not rawShapes) or (self.type not in ['Proxymeshes', 'Clothes']):
            return targets

        for (key, rawShape) in rawShapes:
            shape = {}
            for n,vn in enumerate(rawShape.verts):
                try:
                    pvlist = self.vertWeights[vn]
                except KeyError:
                    pvlist = []
                for (pv, w) in pvlist:
                    dr = scale*w*rawShape.data[n]
                    try:
                        shape[pv] += dr
                    except KeyError:
                        shape[pv] = dr

            verts = []
            data = []
            for pv,dr in shape.items():
                if np.dot(dr,dr) > 1e-8:
                    verts.append(pv)
                    data.append(dr)
            targets.append((key, FakeTarget(rawShape.name, verts, data)))
        return targets

#
#    readProxyFile(obj, filepath, type="Clothes"):
#

doRefVerts = 1
doWeights = 2
doDeleteVerts = 3

def readProxyFile(obj, filepath, type="Clothes"):
    try:
        fp = open(filepath, "rU")
    except IOError:
        log.error("*** Cannot open %s", filepath)
        return None

    folder = os.path.realpath(os.path.expanduser(os.path.dirname(filepath)))

    proxy = Proxy(filepath, type)
    proxy.deleteVerts = np.zeros(len(obj.coord), bool)

    proxy.z_depth = -1
    proxy.max_pole = None
    proxy.useProjection = True
    proxy.ignoreOffset = False
    status = 0
    vnum = 0
    for line in fp:
        words = line.split()

        if len(words) == 0:
            # Reset status on empty line
            #status = 0
            continue

        if words[0].startswith('#') or words[0].startswith('//'):
            # Comment
            continue

        key = words[0]

        if key == 'name':
            proxy.name = " ".join(words[1:])
        elif key == 'uuid':
            proxy.uuid = " ".join(words[1:])
        elif key == 'tag':
            proxy.tags.append( " ".join(words[1:]).lower() )
        elif key == 'z_depth':
            proxy.z_depth = int(words[1])
        elif key == 'max_pole':
            proxy.max_pole = int(words[1])

        elif key == 'verts':
            status = doRefVerts
        elif key == 'weights':
            status = doWeights
            if proxy.weights == None:
                proxy.weights = {}
            weights = []
            proxy.weights[words[1]] = weights
        elif key == "delete_verts":
            status = doDeleteVerts

        elif key == 'obj_file':
            proxy.obj_file = _getFileName(folder, words[1], ".obj")

        elif key == 'vertexgroup_file':
            proxy.vertexgroup_file = _getFileName(folder, words[1], ".json")
            proxy.vertexGroups = io_json.loadJson(proxy.vertexgroup_file)

        elif key == 'material':
            matFile = _getFileName(folder, words[1], ".mhmat")
            proxy.material_file = matFile
            proxy.material.fromFile(matFile)

        elif key == 'mhx_material':
            # Read .mhx material file (or only set a filepath reference to it)
            # MHX material file is supposed to contain only shading parameters that are specific for blender export that are not stored in the .mhmat file
            matFile = _getFileName(folder, words[1], ".mhx")
            proxy.mhxMaterial_file = matFile
            #readMaterial(line, material, proxy, False)
            pass
        elif key == 'useBaseMaterials':
            # TODO deprecated?
            proxy.useBaseMaterials = True

        elif key == 'backface_culling':
            # TODO remove in future
            log.warning('Deprecated parameter "backface_culling" used in proxy file. Set property backfaceCull in material instead.')
        elif key == 'transparent':
            # TODO remove in future
            log.warning('Deprecated parameter "transparent" used in proxy file. Set property in material file instead.')

        elif key == 'uvLayer':
            if len(words) > 2:
                layer = int(words[1])
                uvFile = words[2]
            else:
                layer = 0
                uvFile = words[1]
            #uvMap = material.UVMap(proxy.name+"UV"+str(layer))
            #uvMap.read(proxy.mesh, _getFileName(folder, uvFile, ".mhuv"))
            # Delayed load, only store path here
            proxy.uvLayers[layer] = _getFileName(folder, uvFile, ".mhuv")

        elif key == 'x_scale':
            proxy.tmatrix.getScaleData(words, obj, 0)
        elif key == 'y_scale':
            proxy.tmatrix.getScaleData(words, obj, 1)
        elif key == 'z_scale':
            proxy.tmatrix.getScaleData(words, obj, 2)

        elif key == 'shear_x':
            proxy.tmatrix.getShearData(words, obj, 0, None)
        elif key == 'shear_y':
            proxy.tmatrix.getShearData(words, obj, 1, None)
        elif key == 'shear_z':
            proxy.tmatrix.getShearData(words, obj, 2, None)
        elif key == 'l_shear_x':
            proxy.tmatrix.getShearData(words, obj, 0, 'Left')
        elif key == 'l_shear_y':
            proxy.tmatrix.getShearData(words, obj, 1, 'Left')
        elif key == 'l_shear_z':
            proxy.tmatrix.getShearData(words, obj, 2, 'Left')
        elif key == 'r_shear_x':
            proxy.tmatrix.getShearData(words, obj, 0, 'Right')
        elif key == 'r_shear_y':
            proxy.tmatrix.getShearData(words, obj, 1, 'Right')
        elif key == 'r_shear_z':
            proxy.tmatrix.getShearData(words, obj, 2, 'Right')

        elif key == 'uniform_scale':
            proxy.uniformScale = True
            if len(words) > 1:
                proxy.scaleCorrect = float(words[1])
            proxy.uniformizeScale()
        elif key == 'use_projection':
            # TODO still used?
            proxy.useProjection = int(words[1])
        elif key == 'ignoreOffset':
            # TODO still used?
            proxy.ignoreOffset = int(words[1])
        elif key == 'delete':
            proxy.deleteGroups.append(words[1])

        elif key == 'mask_uv_layer':
            if len(words) > 1:
                proxy.maskLayer = int(words[1])
        elif key == 'texture_uv_layer':
            if len(words) > 1:
                proxy.textureLayer = int(words[1])

        # TODO keep this costume stuff?
        elif key == 'clothing':
            if len(words) > 2:
                clothingPiece = (words[1], words[2])
            else:
                clothingPiece = (words[1], None)
            proxy.clothings.append(clothingPiece)
        elif key == 'transparencies':
            uuid = words[1]
            proxy.transparencies[uuid] = words[2].lower() in ["1", "yes", "true", "enable", "enabled"]

        # Blender-only properties
        elif key == 'wire':
            proxy.wire = True
        elif key == 'cage':
            proxy.cage = True
        elif key == 'subsurf':
            levels = int(words[1])
            if len(words) > 2:
                render = int(words[2])
            else:
                render = levels+1
            proxy.modifiers.append( ['subsurf', levels, render] )
        elif key == 'shrinkwrap':
            offset = float(words[1])
            proxy.modifiers.append( ['shrinkwrap', offset] )
        elif key == 'solidify':
            thickness = float(words[1])
            offset = float(words[2])
            proxy.modifiers.append( ['solidify', thickness, offset] )
        elif key == 'shapekey':
            proxy.shapekeys.append( _getFileName(folder, words[1], ".target") )
        elif key == 'basemesh':
            proxy.basemesh = words[1]

        elif key in ['objfile_layer', 'uvtex_layer']:
            pass


        elif status == doRefVerts:
            refVert = ProxyRefVert(obj)
            proxy.refVerts.append(refVert)
            if len(words) == 1:
                refVert.fromSingle(words, vnum, proxy)
            elif len(words) == 16:
                refVert.fromSixteen(words, vnum, proxy)
            else:
                refVert.fromTriple(words, vnum, proxy)
            vnum += 1

        elif status == doWeights:
            v = int(words[0])
            w = float(words[1])
            weights.append((v,w))

        elif status == doDeleteVerts:
            sequence = False
            for v in words:
                if v == "-":
                    sequence = True
                else:
                    v1 = int(v)
                    if sequence:
                        for vn in range(v0,v1+1):
                            proxy.deleteVerts[vn] = True
                        sequence = False
                    else:
                        proxy.deleteVerts[v1] = True
                    v0 = v1

        else:
            log.warning('Unknown keyword %s found in proxy file %s', key, filepath)

    if proxy.z_depth == -1:
        log.warning('Proxy file %s does not specify a Z depth. Using 50.', filepath)
        proxy.z_depth = 50

    proxy._finalize(obj)

    return proxy


def _getFileName(folder, file, suffix):
    (name, ext) = os.path.split(file)
    if ext:
        return os.path.join(folder, file)
    else:
        return os.path.join(folder, file+suffix)



#
# Caching of proxy files in data folders
#

def updateProxyFileCache(paths, fileExt, cache = None):
    """
    Update cache of proxy files in the specified paths. If no cache is given as
    parameter, a new cache is created.
    This cache contains per canonical filename (key) the UUID and tags of that
    proxy file.
    Cache entries are invalidated if their modification time has changed, or no
    longer exist on disk.
    """
    if cache is None:
        cache = dict()
    proxyFiles = []
    entries = dict((key, True) for key in cache.keys()) # lookup dict for old entries in cache
    for folder in paths:
        proxyFiles.extend(_findProxyFiles(folder, fileExt, 6))
    for proxyFile in proxyFiles:
        proxyId = getpath.canonicalPath(proxyFile)

        mtime = os.path.getmtime(proxyFile)
        if proxyId in cache:
            try: # Guard against doubles
                del entries[proxyId]    # Mark that old cache entry is still valid
            except:
                pass
            cached_mtime = cache[proxyId][0]
            if not (mtime > cached_mtime):
                continue

        (uuid, tags) = peekMetadata(proxyFile)
        cache[proxyId] = (mtime, uuid, tags)
    # Remove entries from cache that no longer exist
    for key in entries.keys():
        try:
            del cache[key]
        except:
            pass
    return cache


def _findProxyFiles(folder, fileExt = "mhclo", depth = 6):
    if depth < 0:
        return []
    try:
        files = os.listdir(folder)
    except OSError:
        return []
    result = []
    for pname in files:
        path = os.path.join(folder, pname)
        if os.path.isfile(path):
            if os.path.splitext(path)[1] == "."+fileExt:
                result.append(path)
        elif os.path.isdir(path):
            result.extend(_findProxyFiles(path, fileExt, depth-1))
    return result


def peekMetadata(proxyFilePath):
    """
    Read UUID and tags from proxy file, and return as soon as vertex data
    begins. Reads only the necessary lines of the proxy file from disk, not the
    entire proxy file is loaded in memory.
    """
    fp = open(proxyFilePath)
    uuid = None
    tags = set()
    for line in fp:
        words = line.split()
        if len(words) == 0:
            pass
        elif words[0] == 'uuid':
            uuid = words[1]
        elif words[0] == 'tag':
            tags.add(words[1].lower())
        elif words[0] == 'verts':
            break
    fp.close()
    return (uuid, tags)

