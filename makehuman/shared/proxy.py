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

_A7converter = None
Unit3 = np.identity(3,float)


class Proxy:
    def __init__(self, file, type, human):
        log.debug("Loading proxy file: %s.", file)
        import makehuman

        name = os.path.splitext(os.path.basename(file))[0]
        self.name = name.capitalize().replace(" ","_")
        self.type = type
        self.object = None
        self.human = human
        if not human:
            raise RuntimeError("Proxy constructor expects a valid human object.")
        self.file = file
        if file:
            self.mtime = os.path.getmtime(file)
        else:
            self.mtime = None
        self.uuid = None
        self.basemesh = makehuman.getBasemeshVersion()
        self.tags = []

        self.num_refverts = None

        self.ref_vIdxs = None       # (Vidx1,Vidx2,Vidx3) list with references to human vertex indices, indexed by proxy vert
        self.weights = None         # (w1,w2,w3) list, with weights per human vertex (mapped by ref_vIdxs), indexed by proxy vert
        self.vertWeights = {}       # (proxy-vert, weight) list for each parent vert (reverse mapping of self.weights, indexed by human vertex)
        self.offsets = None         # (x,y,z) list of vertex offsets, indexed by proxy vert

        self.tmatrix = TMatrix()    # Offset transformation matrix. Replaces scale

        self.z_depth = -1       # Render order depth for the proxy object. Also used to determine which proxy object should mask others (delete faces)
        self.max_pole = None    # Signifies the maximum number of faces per vertex on the mesh topology. Set to none for default.

        self.uvLayers = {}

        self.material = material.Material(self.name)

        self._obj_file = None
        self.vertexgroup_file = None    # TODO document
        self.vertexGroups = None
        self.material_file = None
        self.maskLayer = -1     # TODO is this still used?
        self.textureLayer = 0
        self.objFileLayer = 0   # TODO what is this used for?

        self.deleteGroups = []  # TODO is this still used?
        self.deleteVerts = np.zeros(len(human.meshData.coord), bool)

        # TODO are these still used?
        self.wire = False
        self.cage = False
        self.modifiers = []
        self.shapekeys = []


    def __repr__(self):
        return ("<Proxy %s %s %s %s>" % (self.name, self.type, self.file, self.uuid))


    def getSeedMesh(self):
        for pxy in self.human.getProxies():
            if self == pxy:
                return pxy.object.getSeedMesh()

        if self.type == "Proxymeshes":
            if not self.human.proxy:
                return None
            return self.human.getProxyMesh()
        elif self.type in ["Cage", "Converter"]:
            return None
        else:
            raise NameError("Unknown proxy type %s" % self.type)


    def getMesh(self):
        return self.object.mesh

        for pxy in self.human.getProxies():
            if self == pxy:
                return pxy.object.mesh

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
            for pxy in human.getProxies():
                if pxy and uuid == pxy.uuid:
                    mesh = pxy.object.mesh
                    break

        return getpath.formatPath(mesh.texture)


    def loadMeshAndObject(self, human):
        import files3d
        import guicommon

        mesh = files3d.loadMesh(self._obj_file, maxFaces = self.max_pole)
        if not mesh:
            log.error("Failed to load %s", self._obj_file)

        mesh.priority = self.z_depth           # Set render order
        mesh.setCameraProjection(0)             # Set to model camera

        # TODO perhaps other properties should be copied from human to object, such as subdivision state. For other hints, and duplicate code, see guicommon Object.setProxy()

        obj = self.object = guicommon.Object(mesh, human.getPosition())
        obj.material = self.material
        obj.setRotation(human.getRotation())
        obj.setSolid(human.solid)    # Set to wireframe if human is in wireframe

        # TODO why return both obj and mesh if you can access the mesh easily through obj.mesh?
        return mesh,obj


    def _finalize(self, refVerts):
        """
        Final step in parsing/loading a proxy file. Initializes numpy structures
        for performance improvement.
        """
        self.weights = np.asarray([v._weights for v in refVerts], dtype=np.float32)
        self.ref_vIdxs = np.asarray([v._verts for v in refVerts], dtype=np.uint32)
        self.offsets = np.asarray([v._offset for v in refVerts], dtype=np.float32)


    def _reloadReverseMapping(self):
        """
        Reconstruct reverse vertex (and weights) mapping
        """
        self.vertWeights = {}
        if self.num_refverts == 3:
            for pxy_vIdx in xrange(self.ref_vIdxs.shape[0]):
                _addProxyVertWeight(self.vertWeights, self.ref_vIdxs[pxy_vIdx, 0], pxy_vIdx, self.weights[pxy_vIdx, 0])
                _addProxyVertWeight(self.vertWeights, self.ref_vIdxs[pxy_vIdx, 1], pxy_vIdx, self.weights[pxy_vIdx, 1])
                _addProxyVertWeight(self.vertWeights, self.ref_vIdxs[pxy_vIdx, 2], pxy_vIdx, self.weights[pxy_vIdx, 2])
        else:
            for pxy_vIdx in xrange(self.ref_vIdxs.shape[0]):
                _addProxyVertWeight(self.vertWeights, self.ref_vIdxs[pxy_vIdx, 0], pxy_vIdx, 1.0)


    def getCoords(self):
        hmesh = self.human.meshData
        matrix = self.tmatrix.getMatrix(hmesh)

        ref_vIdxs = self.ref_vIdxs
        weights = self.weights

        coord = (
            hmesh.coord[ref_vIdxs[:,0]] * weights[:,0,None] +
            hmesh.coord[ref_vIdxs[:,1]] * weights[:,1,None] +
            hmesh.coord[ref_vIdxs[:,2]] * weights[:,2,None] +
            np.dot(matrix, self.offsets.transpose()).transpose()
            )

        return coord


    def update(self, mesh):
        #log.debug("Updating proxy %s.", self.name)
        coords = self.getCoords()
        mesh.changeCoords(coords)
        mesh.calcNormals()


    def getUuid(self):
        if self.uuid:
            return self.uuid
        else:
            return self.name


    def getWeights(self, rawWeights, amt=None):
        """
        Map armature weights mapped to the human to the proxy mesh through the
        proxy mapping.
        """
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

        return self._getWeights1(rawWeights)

    def _getWeights1(self, rawWeights):
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
                weights[key] = self._fixVertexGroup(vgroup)
        return weights

    def _fixVertexGroup(self, vgroup):
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
        # TODO document

        # TODO dependency on richmesh?
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


doRefVerts = 1
doWeights = 2
doDeleteVerts = 3

def loadProxy(human, path, type="Clothes"):
    try:
        proxy = loadTextProxy(human, path, type)    # TODO perhaps proxy type should be stored in .mhclo file too
    except:
        log.error('Unable to load proxy file: %s', path, exc_info=True)
        return None

    return proxy

def loadTextProxy(human, filepath, type="Clothes"):
    from codecs import open
    try:
        fp = open(filepath, "rU", encoding="utf-8")
    except IOError:
        log.error("*** Cannot open %s", filepath)
        return None

    folder = os.path.realpath(os.path.expanduser(os.path.dirname(filepath)))
    proxy = Proxy(filepath, type, human)
    refVerts = []

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
            proxy._obj_file = _getFileName(folder, words[1], ".obj")

        elif key == 'vertexgroup_file':
            proxy.vertexgroup_file = _getFileName(folder, words[1], ".json")
            proxy.vertexGroups = io_json.loadJson(proxy.vertexgroup_file)

        elif key == 'material':
            matFile = _getFileName(folder, words[1], ".mhmat")
            proxy.material_file = matFile
            proxy.material.fromFile(matFile)

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
            proxy.tmatrix.getScaleData(words, 0)
        elif key == 'y_scale':
            proxy.tmatrix.getScaleData(words, 1)
        elif key == 'z_scale':
            proxy.tmatrix.getScaleData(words, 2)

        elif key == 'shear_x':
            proxy.tmatrix.getShearData(words, 0, None)
        elif key == 'shear_y':
            proxy.tmatrix.getShearData(words, 1, None)
        elif key == 'shear_z':
            proxy.tmatrix.getShearData(words, 2, None)
        elif key == 'l_shear_x':
            proxy.tmatrix.getShearData(words, 0, 'Left')
        elif key == 'l_shear_y':
            proxy.tmatrix.getShearData(words, 1, 'Left')
        elif key == 'l_shear_z':
            proxy.tmatrix.getShearData(words, 2, 'Left')
        elif key == 'r_shear_x':
            proxy.tmatrix.getShearData(words, 0, 'Right')
        elif key == 'r_shear_y':
            proxy.tmatrix.getShearData(words, 1, 'Right')
        elif key == 'r_shear_z':
            proxy.tmatrix.getShearData(words, 2, 'Right')

        elif key == 'uniform_scale':
            proxy.uniformScale = True
            if len(words) > 1:
                proxy.scaleCorrect = float(words[1])
            proxy.uniformizeScale()
        elif key == 'delete':
            proxy.deleteGroups.append(words[1])

        elif key == 'mask_uv_layer':
            if len(words) > 1:
                proxy.maskLayer = int(words[1])
        elif key == 'texture_uv_layer':
            if len(words) > 1:
                proxy.textureLayer = int(words[1])

        # TODO are these still used? otherwise we can issue deprecation warnings
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
            refVert = ProxyRefVert(human)
            refVerts.append(refVert)
            if len(words) == 1:
                proxy.num_refverts = 1
                refVert.fromSingle(words, vnum, proxy.vertWeights)
            else:
                proxy.num_refverts = 3
                refVert.fromTriple(words, vnum, proxy.vertWeights)
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

    proxy._finalize(refVerts)

    return proxy


def saveBinaryProxy(proxy, path):
    fp = open(path, 'wb')
    tagStr, tagIdx = _packStringList(proxy.tags)
    uvStr,uvIdx = _packStringList([ proxy.uvLayers[k] for k in sorted(proxy.uvLayers.keys()) ])

    vars_ = dict(
        #proxyType = np.fromstring(proxy.type, dtype='S1'),     # TODO store proxy type?
        name = np.fromstring(proxy.name, dtype='S1'),
        uuid = np.fromstring(proxy.uuid, dtype='S1'),
        basemesh = np.fromstring(proxy.basemesh, dtype='S1'),
        tags_str = tagStr,
        tags_idx = tagIdx,
        num_refverts = np.asarray(proxy.num_refverts, dtype=np.int32),
        uvLayers_str = uvStr,
        uvLayers_idx = uvIdx,
        obj_file = np.fromstring(proxy._obj_file, dtype='S1'),
    )

    if proxy.material_file:
        vars_["material_file"] = np.fromstring(proxy.material_file, dtype='S1')

    if np.any(proxy.deleteVerts):
        vars_["deleteVerts"] = proxy.deleteVerts

    if proxy.z_depth is not None and proxy.z_depth != -1:
        vars_["z_depth"] = np.asarray(proxy.z_depth, dtype=np.int32)

    if proxy.max_pole:
        vars_["max_pole"] = np.asarray(proxy.max_pole, dtype=np.uint32),

    if proxy.num_refverts == 3:
        vars_["ref_vIdxs"] = proxy.ref_vIdxs
        vars_["offsets"] = proxy.offsets
        vars_["weights"] = proxy.weights
    else:
        vars_["ref_vIdxs"] = proxy.ref_vIdxs[:,0]
        vars_["weights"] = proxy.weights[:,0]

    if proxy.vertexgroup_file:
        vars_['vertexgroup_file'] = np.fromstring(proxy.vertexgroup_file, dtype='S1')

    np.savez_compressed(fp, **vars_)
    fp.close()

def loadBinaryProxy(path, human, type):
    log.debug("Loading binary proxy %s.", path)

    npzfile = np.load(path)
    #if type is None:
    #    proxyType = npzfile['proxyType'].tostring()
    #else:
    proxyType = type

    proxy = Proxy(path, proxyType, human)

    proxy.name = npzfile['name'].tostring()
    proxy.uuid = npzfile['uuid'].tostring()
    proxy.basemesh = npzfile['basemesh'].tostring()

    proxy.tags = set(_unpackStringList(npzfile['tags_str'], npzfile['tags_idx']))

    if 'z_depth' in npzfile:
        proxy.z_depth = int(npzfile['z_depth'])

    if 'max_pole' in npzfile:
        proxy.max_pole = int(npzfile['max_pole'])

    proxy.num_refverts = int(npzfile['num_refverts'])

    if proxy.num_refverts == 3:
        proxy.ref_vIdxs = npzfile['ref_vIdxs']
        proxy.offsets = npzfile['offsets']
        proxy.weights = npzfile['weights']
    else:
        num_refs = npzfile['ref_vIdxs'].shape[0]
        proxy.ref_vIdxs = np.zeros((num_refs,3), dtype=np.uint32)
        proxy.ref_vIdxs[:,0] = npzfile['ref_vIdxs']
        proxy.offsets = np.zeros((num_refs,3), dtype=np.float32)
        proxy.weights = np.zeros((num_refs,3), dtype=np.float32)
        proxy.weights[:,0] = npzfile['weights']

    if "deleteVerts" in npzfile:
        proxy.deleteVerts = npzfile['deleteVerts']

    # Reconstruct reverse vertex (and weights) mapping
    proxy._reloadReverseMapping()

    proxy.tmatrix = TMatrix()

    proxy.uvLayers = {}
    for uvIdx, uvName in enumerate(_unpackStringList(npzfile['uvLayers_str'], npzfile['uvLayers_idx'])):
        uvLayers[uvIdx] = uvName

    proxy.material = material.Material(proxy.name)
    if 'material_file' in npzfile:
        proxy.material_file = npzfile['material_file'].tostring()
    if proxy.material_file:
        proxy.material.fromFile(proxy.material_file)

    proxy._obj_file = npzfile['obj_file'].tostring()

    if 'vertexgroup_file' in npzfile:
        proxy.vertexgroup_file = npzfile['vertexgroup_file'].tostring()
        if proxy.vertexgroup_file:
            proxy.vertexGroups = io_json.loadJson(proxy.vertexgroup_file)

    # Just set the defaults for these, no idea if they are still relevant
    proxy.maskLayer = -1
    proxy.textureLayer = 0
    proxy.objFileLayer = 0
    proxy.deleteGroups = []
    proxy.wire = False
    proxy.cage = False
    proxy.modifiers = []
    proxy.shapekeys = []


    if proxy.z_depth == -1:
        log.warning('Proxy file %s does not specify a Z depth. Using 50.', path)
        proxy.z_depth = 50

    return proxy


#
#   class ProxyRefVert:
#

class ProxyRefVert:

    def __init__(self, human):
        self.human = human

    def fromSingle(self, words, vnum, vertWeights):
        # TODO store the number of reference verts in proxy so that we can efficiently save and load them.
        v0 = int(words[0])
        self._verts = (v0,0,1)
        self._weights = (1.0,0.0,0.0)
        self._offset = np.zeros(3, float)
        _addProxyVertWeight(vertWeights, v0, vnum, 1)
        return self

    def fromTriple(self, words, vnum, vertWeights):
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

        _addProxyVertWeight(vertWeights, v0, vnum, w0)
        _addProxyVertWeight(vertWeights, v1, vnum, w1)
        _addProxyVertWeight(vertWeights, v2, vnum, w2)
        return self

    def getWeights(self):
        return self._weights

    def getCoord(self, matrix):
        return (
            np.dot(self.human.meshData.coord[self._verts], self._weights) +
            np.dot(matrix, self._offset)
            )

def _addProxyVertWeight(vertWeights, v, pv, w):
    try:
        vertWeights[v].append((pv, w))
    except KeyError:
        vertWeights[v] = [(pv,w)]
    return

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


    def getScaleData(self, words, idx):
        vn1 = int(words[1])
        vn2 = int(words[2])
        den = float(words[3])
        if not self.scaleData:
            self.scaleData = [None, None, None]
        self.scaleData[idx] = (vn1, vn2, den)


    def getShearData(self, words, idx, side):
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


    def getMatrix(self, hmesh):
        if self.scaleData:
            matrix = np.identity(3, float)
            for n in range(3):
                (vn1, vn2, den) = self.scaleData[n]
                co1 = hmesh.coord[vn1]
                co2 = hmesh.coord[vn2]
                num = abs(co1[n] - co2[n])
                matrix[n][n] = (num/den)
            return matrix

        elif self.shearData:
            return self.matrixFromShear(self.shearData, hmesh)
        elif self.lShearData:
            return self.matrixFromShear(self.lShearData, hmesh)
        elif self.rShearData:
            return self.matrixFromShear(self.rShearData, hmesh)
        else:
            return Unit3


    def matrixFromShear(self, shear, obj):
        from transformations import affine_matrix_from_points

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



def _getFileName(folder, file, suffix):
    (name, ext) = os.path.split(file)
    if ext:
        return os.path.join(folder, file)
    else:
        return os.path.join(folder, file+suffix)


def transferFaceMaskToProxy(vertsMask, proxy):
    """
    Transfer a vertex mask defined on the parent mesh to a proxie using the
    proxy mapping to this parent mesh.
    A vertex mask defines for each vertex if it should be hidden, only faces
    that have all vertices hidden will be hidden.
    True in vertex mask means: show vertex, false means hide (masked)
    """
    # Convert basemesh vertex mask to local mask for proxy vertices
    proxyVertMask = np.ones(len(proxy.ref_vIdxs), dtype=bool)
    if proxy.num_refverts == 3:
        '''
        for idx,hverts in enumerate(proxy.ref_vIdxs):
            # Body verts to which proxy vertex with idx is mapped
            (v1,v2,v3) = hverts
            # Hide proxy vert if any of its referenced body verts are hidden (most agressive)
            #proxyVertMask[idx] = vertsMask[v1] and vertsMask[v2] and vertsMask[v3]
            # Alternative1: only hide if at least two referenced body verts are hidden (best result)
            proxyVertMask[idx] = np.count_nonzero(vertsMask[[v1, v2, v3]]) > 1
            # Alternative2: Only hide proxy vert if all of its referenced body verts are hidden (least agressive)
            #proxyVertMask[idx] = vertsMask[v1] or vertsMask[v2] or vertsMask[v3]
        '''
        # Faster numpy implementation of the above:
        unmasked_row_col = np.nonzero(vertsMask[proxy.ref_vIdxs])
        unmasked_rows = unmasked_row_col[0]
        unmasked_count = np.bincount(unmasked_rows)
        # only hide/mask a vertex if at least two referenced body verts are hidden/masked
        masked_idxs = np.nonzero(unmasked_count < 2)
        proxyVertMask[masked_idxs] = False
    else:
        proxyVertMask[:] = vertsMask[proxy.ref_vIdxs[:,0]]
    return proxyVertMask


#
# Caching of proxy files in data folders
#

def updateProxyFileCache(paths, fileExts, cache = None):
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
        proxyFiles.extend(getpath.search(folder, fileExts, recursive=True, mutexExtensions=True))
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


def peekMetadata(proxyFilePath):
    """
    Read UUID and tags from proxy file, and return as soon as vertex data
    begins. Reads only the necessary lines of the proxy file from disk, not the
    entire proxy file is loaded in memory.
    """
    #import zipfile
    #if zipfile.is_zipfile(proxyFilePath):
    # Using the extension is faster (and will have to do):
    if os.path.splitext(proxyFilePath)[1][1:].lower() == 'mhpxy':
        # Binary proxy file
        npzfile = np.load(proxyFilePath)

        uuid = npzfile['uuid'].tostring()
        tags = set(_unpackStringList(npzfile['tags_str'], npzfile['tags_idx']))
        return (uuid, tags)
    else:
        # ASCII proxy file
        from codecs import open
        fp = open(proxyFilePath, 'rU', encoding="utf-8")
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


def _packStringList(strings):
    text = ''
    index = []
    for string in strings:
        index.append(len(text))
        text += string
    text = np.fromstring(text, dtype='S1')
    index = np.array(index, dtype=np.uint32)
    return text, index

def _unpackStringList(text, index):
    strings = []
    last = None
    for i in index:
        if last is not None:
            name = text[last:i].tostring()
            strings.append(name)
        last = i
    if last is not None:
        name = text[last:].tostring()
        strings.append(name)

    return strings

