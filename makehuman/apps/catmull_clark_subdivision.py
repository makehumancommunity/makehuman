#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Mesh Subdivision Plugin.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers, Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

__docformat__ = 'restructuredtext'

import time
import numpy as np

from module3d import Object3D
import log

class SubdivisionObject(Object3D):
    def __init__(self, object):
        name = object.name + '.sub'
        super(SubdivisionObject, self).__init__(name, 4)

        self.MAX_FACES = object.MAX_FACES
        self.loc = object.loc.copy()
        self.rot = object.rot.copy()
        self.scale = object.scale.copy()
        self.cameraMode = object.cameraMode
        self.visibility = object.visibility
        self.pickable = object.pickable
        self.material = object.material
        self.shadeless = object.shadeless
        self.solid = object.solid
        self.transparentPrimitives = object.transparentPrimitives * 4
        self.object = object.object
        self.parent = object
        self.priority = object.priority
        self.cull = object.cull

    def create(self, progressCallback):
        log.debug('Applying Catmull-Clark subdivision on %s.', self.parent.name)
        total = 19
        now = [time.time()]
        def progress(x):
            last = now[0]
            now[0] = time.time()
            log.debug('Step %d: %f seconds processed', x, now[0] - last)
            if progressCallback:
                progressCallback(float(x)/total)

        progress(0)
        
        parent = self.parent
        nverts = len(parent.coord)
        ntexco = len(parent.texco)
        nfaces = len(parent.fvert)

        group_mask = np.ones(len(parent._faceGroups), dtype=bool)

        for g in parent._faceGroups:
            fg = self.createFaceGroup(g.name)
            if ('joint' in fg.name or 'helper' in g.name):
                group_mask[fg.idx] = False

        progress(1)

        face_mask = group_mask[parent.group]
        self.face_map = np.argwhere(face_mask)[...,0]
        self.face_rmap = np.zeros(nfaces, dtype=int) - 1
        nfaces = len(self.face_map)
        self.face_rmap[self.face_map] = np.arange(nfaces)

        progress(2)

        verts = parent.fvert[face_mask]
        vert_mask = np.zeros(nverts, dtype = bool)
        vert_mask[verts] = True
        self.vtx_map = np.argwhere(vert_mask)[...,0]
        vtx_rmap = np.zeros(nverts, dtype=int) - 1
        nverts = len(self.vtx_map)
        vtx_rmap[self.vtx_map] = np.arange(nverts)

        progress(3)

        uvs = parent.fuvs[face_mask]
        uv_mask = np.zeros(ntexco, dtype = bool)
        uv_mask[uvs] = True
        self.uv_map = np.argwhere(uv_mask)[...,0]
        uv_rmap = np.zeros(ntexco, dtype=int) - 1
        ntexco = len(self.uv_map)
        uv_rmap[self.uv_map] = np.arange(ntexco)

        progress(4)

        fvert = vtx_rmap[parent.fvert[self.face_map]]
        vedges = np.dstack((fvert,np.roll(fvert,-1,axis=1)))

        fuv = uv_rmap[parent.fuvs[self.face_map]]
        tedges = np.dstack((fuv,np.roll(fuv,-1,axis=1)))

        self.cbase = nverts
        self.ebase = nverts + nfaces

        self.tcbase = ntexco
        self.tebase = ntexco + nfaces

        progress(5)

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

        progress(6)

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

        progress(7)

        fvedges2 = np.asarray(fvedges2, dtype=np.uint32) + self.ebase

        self.fvert[:,:,1] = fvedges2
        self.fvert[:,:,3] = np.roll(fvedges2,1,axis=-1)

        ftedges2 = np.asarray(ftedges2, dtype=np.uint32) + self.tebase

        self.fuvs[:,:,1] = ftedges2
        self.fuvs[:,:,3] = np.roll(ftedges2,1,axis=-1)

        progress(8)

        self.evert = np.asarray(vedgelist, dtype = np.uint32)
        self.etexc = np.asarray(tedgelist, dtype = np.uint32)

        self.vedge = np.zeros((nverts, self.MAX_FACES), dtype=np.uint32)
        self.nedges = np.zeros(nverts, dtype=np.uint8)

        progress(9)

        map_ = np.argsort(self.evert[:,0,:].flat)
        vi = self.evert[:,0,:].flat[map_]
        ei = np.mgrid[:len(self.evert),:2][0].flat[map_].astype(np.uint32)
        del map_
        ix, first = np.unique(vi, return_index=True)
        n = first[1:] - first[:-1]
        n = np.hstack((n, np.array([len(vi) - first[-1]])))
        self.nedges[ix] = n.astype(np.uint8)
        for i in xrange(len(ix)):
            self.vedge[ix[i],:n[i]] = ei[first[i]:][:n[i]]
        del vi, ei, ix, n, first

        progress(10)

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

        progress(11)

        ntexco = self.tebase + len(tedgelist)

        self.texco = np.zeros((ntexco, 2), dtype=np.float32)

        self.utexc = False

        progress(12)

        nfaces *= 4

        self.fvert = self.fvert.reshape((nfaces,4))
        self.fuvs  = self.fuvs.reshape((nfaces,4))
        self.group = self.group.reshape(nfaces)
        self.face_mask = self.face_mask.reshape(nfaces)
        self.fnorm = np.zeros((nfaces,3))

        progress(13)

        self._update_faces()

        progress(14)

        self.updateIndexBuffer()

        progress(15)

        self.update_uvs()

        progress(16)

        self.update_coords()

        progress(17)

        self.calcNormals()

        progress(18)

        self.sync_all()

        progress(19)

    def dump(self):
        for k in dir(self):
            v = getattr(self, k)
            if isinstance(v, type(self.fvert)):
                fmt = '%.6f' if v.dtype in (np.float32, float) else '%d'
                if len(v.shape) > 2:
                    v = v.reshape((-1,v.shape[-1]))
                np.savetxt('dump/%s.txt' % k, v, fmt=fmt)

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

        btexc[...] = ptexco

        self.markUVs()

        self.has_uv = parent.has_uv

    def update_coords(self):
        parent = self.parent

        bvert = self.coord[:self.cbase]
        cvert = self.coord[self.cbase:self.ebase]
        evert = self.coord[self.ebase:]

        cvert[...] = np.sum(parent.coord[parent.fvert[self.face_map]], axis=1) / 4

        pcoord = parent.coord[self.vtx_map]

        iva = self.evert[:,0,0]
        ivb = self.evert[:,0,1]
        ic1 = self.evert[:,1,0]
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

def createSubdivisionObject(object, progressCallback=None):
    obj = SubdivisionObject(object)
    obj.create(progressCallback)
    # obj.dump()
    return obj

def updateSubdivisionObject(object, progressCallback=None):
    object.update()
    object.calcNormals()
    object.sync_all()
