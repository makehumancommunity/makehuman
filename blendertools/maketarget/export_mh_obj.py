#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

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

Custom obj exporter for MakeHuman Maketarget
"""

import bpy, os, mathutils
import math
from mathutils import *

from . import maketarget

#
#   GroupZOrderSuffix
#   Determines the Z-order of face groups.
#   Faces with lower Z-order are exported first
#   Only looks at the last part of the group name
#   Groups not listed have Z-order 0.
#   Faces within a given Z-order are exported with lower face number first.
#   Preferably add new groups with higher Z-order, to not ruin numbering
#   of existing faces. It is not a disaster to change face numbers, but
#   it does require some changes in MHX export.
#

GroupZOrderSuffix = {
    1: ["lash","eyebrown","cornea"],
    2: ["tights","skirt"]
}

#
#   When materials represent face groups, we must figure out the real materials
#   in some other way. Use this dict.
#   If the group name contains the key string, assign it to the value material.
#   If not, material is "skin".
#
#   Ignored when object has real materials.
#

GroupMaterials = {
    "nail" : "nail",
    "eye-ball" : "eye",
    "teeth" : "teeth",
    "cornea" : "cornea",
    "joint" : "joint",
    "skirt" : "joint",
    "tights" : "joint",
}

# Minimal distance for merging tex verts

Epsilon = 1e-4

#
#   exportObjFile(path, groupsAsMaterials, context):
#

def exportObjFile(path, groupsAsMaterials, context):
    ob = context.object
    me = ob.data
    if (not me) or (len(me.materials) < 2):
        raise MHError("Mesh must have materials")

    orderedFaces = zOrderFaces(me, me.polygons)

    (name,ext) = os.path.splitext(path)
    if ext.lower() != ".obj":
        path = path + ".obj"
    fp = open(path, "w", encoding="utf-8", newline="\n")
    scn = context.scene

    for v in me.vertices:
        fp.write("v %.4f %.4f %.4f\n" % (v.co[0], v.co[2], -v.co[1]))

    for v in me.vertices:
        fp.write("vn %.4f %.4f %.4f\n" % (v.normal[0], v.normal[2], -v.normal[1]))

    info =  (-2, None)
    if me.uv_textures:
        (uvFaceVerts, texVerts, nTexVerts) = setupTexVerts(me, faces)
        for vtn in range(nTexVerts):
            vt = texVerts[vtn]
            fp.write("vt %.4f %.4f\n" % (vt[0], vt[1]))
        for f in orderedFaces:
            info = writeNewGroup(fp, f,info, me, ob, groupsAsMaterials)
            uvVerts = uvFaceVerts[f.index]
            faceLine = []
            for n,v in enumerate(f.vertices):
                (vt, uv) = uvVerts[n]
                faceLine.append("%d/%d" % (v+1, vt+1))
            fp.write("f "+ (" ".join(faceLine)) +"\n")
    else:
        for f in orderedFaces:
            info = writeNewGroup(fp, f, info, me, ob, groupsAsMaterials)
            fp.write("f ")
            faceLine = []
            for vn in f.vertices:
                faceLine.append("%d" % (vn+1))
            fp.write("f "+ (" ".join(faceLine)) +"\n")

    fp.close()
    print("%s written" % path)
    return


def writeNewGroup(fp, f, info, me, ob, groupsAsMaterials):
    (gnum, mname) = info
    if groupsAsMaterials:
        if f.material_index != gnum:
            gnum = f.material_index
            gname = me.materials[gnum].name
            mname1 = "skin"
            for key in GroupMaterials.keys():
                if key in gname:
                    mname1 = GroupMaterials[key]
                    break
            if mname != mname1:
                mname = mname1
                fp.write("usemtl %s\n" % mname)
            fp.write("g %s\n" % gname)
            info = (gnum, mname)
    else:
        nhits = {}
        for vn in f.vertices:
            v = me.vertices[vn]
            for grp in v.groups:
                try:
                    nhits[grp.group] += 1
                except:
                    nhits[grp.group] = 1

        gn = -1
        nverts = len(f.vertices)
        for (gn1,n) in nhits.items():
            if n == nverts:
                gn = gn1
                break

        if gn != gnum:
            mat = me.materials[f.material_index]
            if mname != mat.name:
                mname = mat.name
                #fp.write("usemtl %s\n" % mname)
            gnum = gn
            if gnum < 0:
                fp.write("g body\n")
            else:
                for vgrp in ob.vertex_groups:
                    if vgrp.index == gnum:
                        fp.write("g %s\n" % vgrp.name)
                        break
            info = (gnum, mname)
    return info

#
#   zOrderFaces(me, faces):
#

def zOrderFaces(me, faces):
    zGroupFaces = {}
    zGroupFaces[0] = []
    for n in GroupZOrderSuffix.keys():
        zGroupFaces[n] = []
    for f in faces:
        group = me.materials[f.material_index].name
        suffix = group.split("-")[-1]
        zgroup = zGroupFaces[0]
        for (prio,suffices) in GroupZOrderSuffix.items():
            if suffix in suffices:
                zgroup = zGroupFaces[prio]
                break
        zgroup.append(f)
    zlist = list(zGroupFaces.items())
    zlist.sort()
    zfaces = []
    for (key, zflist) in zlist:
        zfaces += zflist
    return zfaces

#
#   setupTexVerts(me, faces):
#

def setupTexVerts(me, faces):
    vertEdges = {}
    vertFaces = {}

    for v in me.vertices:
        vertEdges[v.index] = []
        vertFaces[v.index] = []
    for e in me.edges:
        for vn in e.vertices:
            vertEdges[vn].append(e)
    for f in faces:
        for vn in f.vertices:
            vertFaces[vn].append(f)

    edgeFaces = {}
    for e in me.edges:
        edgeFaces[e.index] = []
    faceEdges = {}
    for f in faces:
        faceEdges[f.index] = []
    for f in faces:
        for vn in f.vertices:
            for e in vertEdges[vn]:
                v0 = e.vertices[0]
                v1 = e.vertices[1]
                if (v0 in f.vertices) and (v1 in f.vertices):
                    if f not in edgeFaces[e.index]:
                        edgeFaces[e.index].append(f)
                    if e not in faceEdges[f.index]:
                        faceEdges[f.index].append(e)

    faceNeighbors = {}
    uvFaceVerts = {}
    for f in faces:
        faceNeighbors[f.index] = []
        uvFaceVerts[f.index] = []
    for f in faces:
        for e in faceEdges[f.index]:
            for f1 in edgeFaces[e.index]:
                if f1 != f:
                    faceNeighbors[f.index].append((e,f1))

    vtn = 0
    texVerts = {}

    uvloop = me.uv_layers[0]
    n = 0
    for f in faces:
        for vn in f.vertices:
            vtn = findTexVert(uvloop.data[n].uv, vtn, f, faceNeighbors, uvFaceVerts, texVerts)
            n += 1

    return (uvFaceVerts, texVerts, vtn)

#
#   findTexVert(uv, vtn, f, faceNeighbors, uvFaceVerts, texVerts):
#

def findTexVert(uv, vtn, f, faceNeighbors, uvFaceVerts, texVerts):
    for (e,f1) in faceNeighbors[f.index]:
        for (vtn1,uv1) in uvFaceVerts[f1.index]:
            vec = uv - uv1
            if vec.length < Epsilon:
                uvFaceVerts[f.index].append((vtn1,uv))
                return vtn
    uvFaceVerts[f.index].append((vtn,uv))
    texVerts[vtn] = uv
    return vtn+1



