#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

""" 
Mesh Subdivision Plugin.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers, Glynn Clements

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

__docformat__ = 'restructuredtext'

import numpy as np

from module3d import Object3D
from progress import Progress
import log

class SubdivisionObject(Object3D):
    def __init__(self, object, staticFaceMask=None):
        """
        If staticFaceMask is specified (which is a face mask valid on object), 
        the masked faces and their vertices are not included as geometry in
        this subdivision object (higher performance).
        After building a subdivision object, a (dynamic) face mask can still be
        set on the faces of the subdiv mesh.
        """
        name = object.name + '.sub'
        super(SubdivisionObject, self).__init__(name, 4)

        self.MAX_FACES = object.MAX_FACES
        self.cameraMode = object.cameraMode
        self.visibility = object.visibility
        self.pickable = object.pickable
        self.transparentPrimitives = object.transparentPrimitives * 4
        self.object = object.object
        self.parent = object    # TODO avoid conflicts with clone()'s parent
        self.priority = object.priority
        if staticFaceMask is None:
            self._staticFaceMask = np.ones(object.getFaceCount(), dtype=bool)
        else:
            self._staticFaceMask = staticFaceMask

    def create(self):
        log.debug('Applying Catmull-Clark subdivision on %s.', self.parent.name)

        # Progress bar will be updated only through the parent Progress.
        progress = Progress([0, 0, 16, 0, 15, 63, 0, 0, 0, 93,
            16, 0, 0, 343, 141, 15, 109, 328, 31, 281],
            None, logging=True, timing=True)

        progress.firststep()

        parent = self.parent
        nverts = len(parent.coord)
        ntexco = len(parent.texco)
        nfaces = len(parent.fvert)

        for g in parent._faceGroups:
            fg = self.createFaceGroup(g.name)

        progress.step()

        face_mask = self.staticFaceMask
        self.face_map = np.argwhere(face_mask)[...,0]
        self.face_rmap = np.zeros(nfaces, dtype=int) - 1
        nfaces = len(self.face_map)
        self.face_rmap[self.face_map] = np.arange(nfaces)

        progress.step()

        verts = parent.fvert[face_mask]
        vert_mask = np.zeros(nverts, dtype = bool)
        vert_mask[verts] = True
        self.vtx_map = np.argwhere(vert_mask)[...,0]
        vtx_rmap = np.zeros(nverts, dtype=int) - 1
        nverts = len(self.vtx_map)
        vtx_rmap[self.vtx_map] = np.arange(nverts)
        self.vtx_rmap = vtx_rmap

        progress.step()

        uvs = parent.fuvs[face_mask]
        uv_mask = np.zeros(ntexco, dtype = bool)
        uv_mask[uvs] = True
        self.uv_map = np.argwhere(uv_mask)[...,0]
        uv_rmap = np.zeros(ntexco, dtype=int) - 1
        ntexco = len(self.uv_map)
        uv_rmap[self.uv_map] = np.arange(ntexco)

        progress.step()

        fvert = vtx_rmap[parent.fvert[self.face_map]]
        vedges = np.dstack((fvert,np.roll(fvert,-1,axis=1)))  # All 4 edges belonging to each face

        fuv = uv_rmap[parent.fuvs[self.face_map]]
        tedges = np.dstack((fuv,np.roll(fuv,-1,axis=1)))

        self.cbase = nverts            # Index of first subdivided vert
        self.ebase = nverts + nfaces   # Edge base index 

        self.tcbase = ntexco
        self.tebase = ntexco + nfaces

        progress.step()

        vedges = vedges.astype(np.uint64)
        va = np.min(vedges, axis=-1)
        vb = np.max(vedges, axis=-1)
        p = (va << 32) | vb
        p = p.reshape(-1)
        del va, vb
        vedgelist, fvedges2 = np.unique(p, return_inverse=True)
        del p
        vedgelist = vedgelist[:,None] >> np.array([[32,0]], dtype=np.uint64)
        vedgelist = vedgelist.astype(np.uint32)
        fvedges2 = fvedges2.reshape(vedges[...,0].shape)

        _, x0 = np.unique(fvedges2, return_index=True)
        _, x1 = np.unique(fvedges2[::-1], return_index=True)
        xmap = np.hstack((x0[:,None]/4, len(fvedges2) - 1 - x1[:,None]/4))
        vedgelist = np.hstack((vedgelist, xmap)).reshape((-1,2,2))
        del xmap

        tedges = tedges.astype(np.uint64)
        ta = np.min(tedges, axis=-1)
        tb = np.max(tedges, axis=-1)
        q = (ta << 32) | tb
        q = q.reshape(-1)
        del ta, tb
        tedgelist, ftedges2 = np.unique(q, return_inverse=True)
        del q
        tedgelist = tedgelist[:,None] >> np.array([[32,0]], dtype=np.uint64)
        tedgelist = tedgelist.astype(np.uint32)
        ftedges2 = ftedges2.reshape(tedges[...,0].shape)

        progress.step()

        nfaces = len(self.face_map)

        self.fvert = np.empty((nfaces,4,4), dtype=np.uint32)
        self.fuvs  = np.empty((nfaces,4,4), dtype=np.uint32)
        self.group = np.empty((nfaces,4), dtype=np.uint16)
        self.face_mask = np.empty((nfaces,4), dtype=bool)

        # Create faces
        # v0  e0  v1
        # 
        # e3  c   e1
        #
        # v3  e2  v2

        self.fvert[:,:,0] = fvert
        self.fvert[:,:,2] = np.arange(nfaces)[:,None] + self.cbase

        self.fuvs[:,:,0] = fuv
        self.fuvs[:,:,2] = np.arange(nfaces)[:,None] + self.tcbase

        self.group[...] = parent.group[self.face_map][:,None]
        self.face_mask[...] = parent.face_mask[self.face_map][:,None]

        progress.step()

        fvedges2 = np.asarray(fvedges2, dtype=np.uint32) + self.ebase

        self.fvert[:,:,1] = fvedges2
        self.fvert[:,:,3] = np.roll(fvedges2,1,axis=-1)

        ftedges2 = np.asarray(ftedges2, dtype=np.uint32) + self.tebase

        self.fuvs[:,:,1] = ftedges2
        self.fuvs[:,:,3] = np.roll(ftedges2,1,axis=-1)

        progress.step()

        # self.evert[i,0] contains the two vertices that define the edge which
        # is divided in half by edge vertex with index i
        # self.evert[i,1] contains the two center vertices in the faces
        # that border on the edge [i,0]
        self.evert = np.asarray(vedgelist, dtype = np.uint32)
        self.etexc = np.asarray(tedgelist, dtype = np.uint32)

        # TODO document
        self.vedge = np.zeros((nverts, self.MAX_FACES), dtype=np.uint32)
        self.nedges = np.zeros(nverts, dtype=np.uint8)

        progress.step()

        map_ = np.argsort(self.evert[:,0,:].flat)
        vi = self.evert[:,0,:].flat[map_]
        ei = np.mgrid[:len(self.evert),:2][0].flat[map_].astype(np.uint32)
        del map_
        ix, first = np.unique(vi, return_index=True)
        n = first[1:] - first[:-1]
        n = np.hstack((n, np.array([len(vi) - first[-1]])))
        self.nedges[ix] = n.astype(np.uint8)
        try:
            for i in xrange(len(ix)):
                self.vedge[ix[i],:n[i]] = ei[first[i]:][:n[i]]
        except ValueError as e:
            raise RuntimeError("Pole-count too low, try increasing max_pole: %s" % e)
        del vi, ei, ix, n, first

        progress.step()

        nverts = self.ebase + len(vedgelist)

        self.coord = np.zeros((nverts, 3), dtype=np.float32)
        self.vnorm = np.zeros((nverts, 3), dtype=np.float32)
        self.vtang = np.zeros((nverts, 4), dtype=np.float32)
        self.color = np.zeros((nverts, 4), dtype=np.uint8) + 255
        self.vface = np.zeros((nverts, self.MAX_FACES), dtype=np.uint32)
        self.nfaces = np.zeros(nverts, dtype=np.uint8)

        self.ucoor = False
        self.unorm = False
        self.utang = False
        self.ucolr = False

        progress.step()

        ntexco = self.tebase + len(tedgelist)

        self.texco = np.zeros((ntexco, 2), dtype=np.float32)

        self.utexc = False

        progress.step()

        nfaces *= 4

        self.fvert = self.fvert.reshape((nfaces,4))
        self.fuvs  = self.fuvs.reshape((nfaces,4))
        self.group = self.group.reshape(nfaces)
        self.face_mask = self.face_mask.reshape(nfaces)
        self.fnorm = np.zeros((nfaces,3))

        progress.step()

        self._update_faces()

        progress.step()

        self.updateIndexBuffer()

        progress.step()

        self.update_uvs()

        progress.step()

        self.update_coords()

        progress.step()

        self.calcNormals()

        progress.step()

        self.sync_all()

        progress.step()


        # VERTEX MAPPING _parent_map: (subdiv -> parent)
        # [[v0 -1 -1 -1]                (1 reference vert,  weight == 1)
        #  [v1 -1 -1 -1]
        #  ...
        #  [vn -1 -1 -1]
        #  [c0  c  c  c]  index: cbase  (4 reference verts, weight == 1/4)
        #  [c1  c  c  c]
        #  ...
        #  [cn  c  c  c]
        #  [e0  e -1 -1]  index: ebase  (2 reference verts, weight == 1/2)
        #  [e1  e -1 -1]
        #  ...
        #  [en  e -1 -1]]  with n == self.getVertexCount()

        self._parent_map = - np.ones((self.getVertexCount(), 4), dtype=np.int32)
        # Map base verts onto themselves
        self._parent_map[:self.cbase, 0] = self.vtx_map[:]
        # Face-center verts are mapped to the 4 base verts connected to the face
        self._parent_map[self.cbase:self.ebase, :4] = self.vtx_map[parent.fvert[self.face_map]]
        # Edge-center verts are mapped to the 2 base verts that are endpoints of the edge
        self._parent_map[self.ebase:, :2] = self.evert[:,0,:]

        self._parent_map_weights = np.zeros(self._parent_map.shape[0], dtype=np.float32)
        self._parent_map_weights[:self.cbase] = 1.0
        self._parent_map_weights[self.cbase:self.ebase] = 1.0/4
        self._parent_map_weights[self.ebase:] = 1.0/2


        # VERTEX MAPPING _inverse_parent_map: (parent -> subdiv)
        # [[v0 c0 c1 c2 ... cM e0 e1 e2 ... eM]   with M == parent.MAX_FACES
        #  [v1 c0 c1 c2 ... cM e0 e1 e2 ... eM]
        #  ...
        #  [vn c0 c1 c2 ... cM e0 e1 e2 ... eM]]  with n == parent.getVertexCount()
        #
        # Invalid columns have index value -1

        self._inverse_parent_map = - np.ones((self.parent.getVertexCount(), 1+2*parent.MAX_FACES), dtype=np.int32)
        # Inverse map base verts
        self._inverse_parent_map[:, 0] = self.vtx_rmap[:]

        # Inverse map center verts
        cvert = self._parent_map[self.cbase:self.ebase, :4]
        _reverse_n_to_m_map(cvert,
                            self._inverse_parent_map[:, 1:1+parent.MAX_FACES],
                            offset=self.cbase)

        # Inverse map edge verts
        evert = self._parent_map[self.ebase:, :2]
        col_offset = 1 + parent.MAX_FACES
        _reverse_n_to_m_map(evert,
                            self._inverse_parent_map[:, col_offset:col_offset+parent.MAX_FACES],
                            offset=self.ebase)

        # TODO defer calculation of mapping until it is requested

        progress.step()

    @property
    def parent_map_weights(self):
        # TODO populate in deferred form, make this a getter (and retrieve recursively)
        return self._parent_map_weights

    def update_uvs(self):
        parent = self.parent

        btexc = self.texco[:self.tcbase]
        ctexc = self.texco[self.tcbase:self.tebase]
        etexc = self.texco[self.tebase:]

        ctexc[...] = np.sum(parent.texco[parent.fuvs[self.face_map]], axis=1) / 4

        iva = self.etexc[:,0]
        ivb = self.etexc[:,1]

        ptexco = parent.texco[self.uv_map]

        ta = ptexco[iva]
        tb = ptexco[ivb]
        etexc[...] = (ta + tb) / 2
        del iva, ivb, ta, tb

        # TODO these UVs should be averaged in the same way as bvert in update_coords
        btexc[...] = ptexco

        self.markUVs()

        self.has_uv = parent.has_uv

    def update_coords(self):
        """
        Recalculate positions of subdiv coordinates
        
         v0  e0  v1
         
         e3  c   e1
        
         v3  e2  v2

        with vi base verts at interpolated positions (bvert)
        with c newly introduced center verts in the center of each face (cvert)
        with ei newly introduced verts at the centers of the poly edges (evert)
        """
        parent = self.parent

        bvert = self.coord[:self.cbase]            # Base verts
        cvert = self.coord[self.cbase:self.ebase]  # Poly center verts
        evert = self.coord[self.ebase:]            # Edge verts

        cvert[...] = np.sum(parent.coord[parent.fvert[self.face_map]], axis=1) / 4

        pcoord = parent.coord[self.vtx_map]

        iva = self.evert[:,0,0]  # References to base verts
        ivb = self.evert[:,0,1]
        ic1 = self.evert[:,1,0]  # References to center verts
        ic2 = self.evert[:,1,1]

        va = pcoord[iva]
        vb = pcoord[ivb]
        mvert = va + vb
        del iva, ivb, va, vb

        vc1 = cvert[ic1]
        vc2 = cvert[ic2]
        vc = vc1 + vc2
        del vc1, vc2

        inedge = (ic1 == ic2)

        # Calculate edge vert coordinates: average two e verts when at edge, else average over 4
        evert[...] = np.where(inedge[:,None], mvert / 2, (mvert + vc) / 4)
        del ic1, ic2, vc

        nvface = parent.nfaces[self.vtx_map]

        # comment: this code could really do with some comments
        edgewt = np.arange(self.MAX_FACES)[None,:,None] < self.nedges[:,None,None]
        edgewt2 = edgewt * inedge[self.vedge][:,:,None]
        edgewt = edgewt / self.nedges.astype(np.float32)[:,None,None]
        nvedge = np.sum(edgewt2, axis=1)
        oevert = np.sum(mvert[self.vedge] * edgewt / 2, axis=1)
        oevert2 = np.sum(mvert[self.vedge] * edgewt2 / 2, axis=1)
        facewt = np.arange(self.MAX_FACES)[None,:,None] < nvface[:,None,None]
        facewt = facewt / nvface.astype(np.float32)[:,None,None]
        ofvert = np.sum(cvert[self.face_rmap[parent.vface[self.vtx_map]]] * facewt, axis=1)
        opvert = pcoord

        valid = nvface >= 3

        bvert[...] = np.where(valid[:,None],
                              np.where((self.nedges == nvface)[:,None],
                                       (ofvert + 2 * oevert + (nvface[:,None] - 3) * opvert) / nvface[:,None],
                                       (oevert2 + opvert) / (nvedge + 1)),
                              (3 * oevert - ofvert) / 2)

        self.markCoords(coor=True)

    def update(self):
        self.update_coords()
        super(SubdivisionObject, self).update()

    def changeFaceMask(self, mask, indices=None, remapFromUnsubdivided=True):
        """
        Change face mask of subdivided mesh.
        If remapFromUnsubdivided is True (default), the mask parameter is
        expected to be a face mask for the original mesh (self.parent).
        In this case a remapping to the subdivided faces will occur (indices 
        parameter is ignored).

        If remapFromUnsubdivided is False, a facemask can be applied directly
        on the subdivided mesh faces.
        """
        if remapFromUnsubdivided:
            nBaseFaces = len(self.face_map)

            # Duplicate the facemask to 4 faces per seedmesh face
            subdiv_face_mask = np.zeros((nBaseFaces, 4), dtype=bool)
            subdiv_face_mask[:] = mask[self.face_map][:,None]
            subdiv_face_mask = subdiv_face_mask.reshape(4*nBaseFaces)

            super(SubdivisionObject, self).changeFaceMask(subdiv_face_mask)
        else:
            super(SubdivisionObject, self).changeFaceMask(mask)

    @property
    def staticFaceMask(self):
        return self._staticFaceMask

    def clone(self, scale=1.0, filterMaskedVerts=False):
        # First clone the seed mesh
        otherSeed = self.parent.clone(scale, filterMaskedVerts)
        # Then generate a subdivision for it
        if filterMaskedVerts:
            # All masked vertices, static and dynamic are filtered out from parent
            staticFaceMask = None
        else:
            staticFaceMask = self.staticFaceMask
        return createSubdivisionObject(otherSeed, staticFaceMask)


def _reverse_n_to_m_map(input, output, offset=0):
    # Using same algorithm as module3d._update_faces to construct inverse 
    # mapping with variable number of valid columns
    map_ = np.argsort(input.flat)
    vi = input.flat[map_]
    fi = np.mgrid[:input.shape[0],:input.shape[1]][0].flat[map_].astype(np.uint32)
    del map_
    ix, first = np.unique(vi, return_index=True)
    n = first[1:] - first[:-1]
    n_last = len(vi) - first[-1]
    n = np.hstack((n, np.array([n_last])))
    for i in xrange(len(ix)):
        output[ix[i], :n[i]] = offset + fi[first[i]:][:n[i]]


def createSubdivisionObject(object, staticFaceMask=None):
    obj = SubdivisionObject(object, staticFaceMask)
    obj.create()
    return obj

def updateSubdivisionObject(object):
    object.update()
    object.calcNormals()
    object.sync_all()
