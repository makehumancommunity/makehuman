#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

"""

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2014
# Coding Standards:    See http://www.makehuman.org/node/165
#
# Abstract
# Utility for making UVs to MH characters.
#

import bpy
import os
import random
from bpy.props import *
from mathutils import Vector
from . import mc
from .makeclothes import *
from .error import MHError

#
#   Global variables
#

Epsilon = 1e-4

theSettings = mc.settings["hm08"]


def exportUVs(context):
    scn = context.scene
    ob = context.object
    (outpath, outfile) = mc.getFileName(ob, scn.MhUvsDir, "mhuv")
    print("Creating UV file %s" % outfile)
    fp= open(outfile, "w", encoding="utf-8", newline="\n")
    printClothesHeader(fp, scn)
    fp.write("name %s\n" % ob.name.replace(" ","_"))

    matfile = makeclothes.materials.writeMaterial(fp, ob, scn.MhUvsDir)
    if matfile:
        fp.write("material %s\n" % matfile)
    printMhcloUvLayers(fp, ob, scn, False, offset=1)
    fp.close()
    print("File %s written" % outfile)


def exportHelperUVs(context):
    filepath = os.path.join(os.path.dirname(__file__), "helpers.py")
    pob = context.object
    fp = open(filepath, "w", encoding="utf-8", newline="\n")
    fp.write(
        "from mathutils import Vector as V\n\n" +
        "TexFaces = {\n")
    n = 0
    uvlayer = pob.data.uv_layers[0]
    for f in pob.data.polygons:
        if f.select:
            fp.write("    %d: (" % f.index)
            for vn in f.vertices:
                fp.write("V((%.4f, %4f)), " % tuple(uvlayer.data[n].uv))
                n += 1
            fp.write("),\n")
        else:
            n += 4
    fp.write("}\n")
    fp.close()


#
#   unwrapObject(ob, context):
#

def unwrapObject(ob, context):
    scn = context.scene
    old = scn.objects.active
    scn.objects.active = ob

    n = len(ob.data.uv_textures)-1
    if n < scn.MCMaskLayer:
        while n < scn.MCMaskLayer:
            ob.data.uv_textures.new()
            n += 1
        ob.data.uv_textures[n].name = "Mask"
    ob.data.uv_textures.active_index = scn.MCMaskLayer

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', fill_holes=True, correct_aspect=True)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    scn.objects.active = old
    return

#
#   projectUVs(bob, pob, context):
#

def printItems(struct):
    for (key,value) in struct.items():
        print(key, value)


def projectUVs(bob, pob, context):
    print("Projecting %s => %s" % (bob.name, pob.name))
    (bob1, data) = restoreData(context)
    scn = context.scene

    (bVertEdges, bVertFaces, bEdgeFaces, bFaceEdges, bFaceNeighbors, bUvFaceVertsList, bTexVertsList) = setupTexVerts(bob)
    bUvFaceVerts = bUvFaceVertsList[0]
    bTexVerts = bTexVertsList[0]
    bNTexVerts = len(bTexVerts)
    table = {}
    bFaces = getFaces(bob.data)
    bTexFaces = getTexFaces(bob.data, 0)
    if (scn.MCMHVersion != "None" and
        len(bob.data.vertices) > theSettings.vertices["Penis"][0]):
        modifyTexFaces(bFaces, bTexFaces)
    for (pv, exact, verts, wts, diff) in data:
        if exact:
            (v0, x) = verts[0]
            vn0 = v0.index
            for f0 in bVertFaces[vn0]:
                uvf = bTexFaces[f0.index].uvs
                uv0 = getUvLoc(vn0, f0, uvf)
                table[pv.index] = (1, uv0, 1)
                break
        else:
            vn0 = verts[0]
            vn1 = verts[1]
            vn2 = verts[2]
            if (vn1 == 0) and (vn2 == 1) and (abs(wts[0]-1) < Epsilon):
                uvVerts = []
                for f0 in bVertFaces[vn0]:
                    uvf = bTexFaces[f0.index].uvs
                    uv0 = getUvLoc(vn0, f0, uvf)
                    uvVerts.append(uv0)
                table[pv.index] = (2, uvVerts, wts)
                continue
            for f0 in bVertFaces[vn0]:
                for f1 in bVertFaces[vn1]:
                    if (f1 == f0):
                        for f2 in bVertFaces[vn2]:
                            if (f2 == f0):
                                uvf = bTexFaces[f0.index].uvs
                                uv0 = getUvLoc(vn0, f0, uvf)
                                uv1 = getUvLoc(vn1, f0, uvf)
                                uv2 = getUvLoc(vn2, f0, uvf)
                                table[pv.index] = (0, [uv0,uv1,uv2], wts)

    (pVertEdges, pVertFaces, pEdgeFaces, pFaceEdges, pFaceNeighbors, pUvFaceVertsList, pTexVertsList) = setupTexVerts(pob)
    maskLayer = context.scene.MCMaskLayer
    pUvFaceVerts = pUvFaceVertsList[maskLayer]
    pTexVerts = pTexVertsList[maskLayer]
    pNTexVerts = len(pTexVerts)
    (pSeamEdgeFaces, pSeamVertEdges, pBoundaryVertEdges, pVertTexVerts) = getSeamData(pob.data, pUvFaceVerts, pEdgeFaces)
    pTexVertUv = {}
    for vtn in range(pNTexVerts):
        pTexVertUv[vtn] = None

    pTexFaces = getTexFaces(pob.data, maskLayer)
    pverts = pob.data.vertices
    bverts = bob.data.vertices
    bedges = bob.data.edges
    remains = {}
    zero = (0,0)
    uvIndex = 0
    pMeFaces = getFaces(pob.data)
    for pf in pMeFaces:
        fn = pf.index
        rmd = {}
        rmd[0] = None
        rmd[1] = None
        rmd[2] = None
        rmd[3] = None
        remains[fn] = rmd

        uvf = pTexFaces[fn]
        for n,pvn in enumerate(pf.vertices):
            uv = getSingleUvLoc(pvn, table)
            uv = trySetUv(pvn, fn, uvf, rmd, n, uv, pVertTexVerts, pTexVertUv, pSeamVertEdges)
            if uv:
                uvf.set(n, uv)

    (bVertList, bPairList, bEdgeList) = getSeams(bob, bTexFaces, context.scene)
    for (en,fcs) in pSeamEdgeFaces.items():
        pe = pob.data.edges[en]
        for m in range(2):
            pv = pverts[pe.vertices[m]]
            be = findClosestEdge(pv, bEdgeList, bverts, bedges)
            for pf in fcs:
                fn = pf.index
                for (n, rmd) in remains[fn].items():
                    if rmd:
                        (uvf, pvn, vt, uv0) = rmd
                        if pv.index == pvn:
                            if pTexVertUv[vt]:
                                uv = pTexVertUv[vt]
                            else:
                                uv = getSeamVertFaceUv(pv, pe, pf, pVertTexVerts, pTexVertUv, be, bEdgeFaces, bTexFaces, pverts, bverts)
                                pTexVertUv[vt] = uv
                            uvf.set(n, uv)
                            remains[fn][n] = None

    for pf in pMeFaces:
        rmd = remains[pf.index]
        for n in range(4):
            if rmd[n]:
                (uvf, pvn, vt, uv) = rmd[n]
                pverts[pvn].select = True
                if pTexVertUv[vt]:
                    uv = pTexVertUv[vt]
                else:
                    pTexVertUv[vt] = uv
                uvf.set(n, uv)
    return


class CTextureFace:
    def __init__(self, f, data, n):
        self.uvs = []
        self.data = data
        self.index = n

    def set(self, n, uv):
        self.data[self.index+n].uv = uv

    def get(self, n):
        return self.data[self.index+n].uv


def getTexFaces(me, ln):
    texFaces = {}
    uvlayer = me.uv_layers[ln]
    n = 0
    for f in me.polygons:
        tf = CTextureFace(f, uvlayer.data, n)
        for vn in f.vertices:
            tf.uvs.append(uvlayer.data[n].uv)
            n += 1
        texFaces[f.index]= tf
    return texFaces


def modifyTexFaces(meFaces, texFaces):
    from . import helpers
    for idx,uvs in helpers.TexFaces.items():
        texFaces[idx].uvs = uvs


def trySetUv(pvn, fn, uvf, rmd, n, uv, vertTexVerts, texVertUv, seamVertEdges):
    (vt, uv_old) = vertTexVerts[pvn][fn]
    if texVertUv[vt]:
        return texVertUv[vt]
    elif not seamVertEdges[pvn]:
        texVertUv[vt] = uv
        return uv
    else:
        rmd[n] = (uvf, pvn, vt, uv)
        return None


def findClosestEdge(pv, edgeList, verts, edges):
    mindist = 1e6
    for e in edgeList:
        vec0 = pv.co - verts[e.vertices[0]].co
        vec1 = pv.co - verts[e.vertices[1]].co
        dist = vec0.length + vec1.length
        if dist < mindist:
            mindist = dist
            best = e
    return best


def getSeamVertFaceUv(pv, pe, pf, pVertTexVerts, pTexVertUv, be, bEdgeFaces, bTexFaces, pverts, bverts):
    dist = {}
    for bf in bEdgeFaces[be.index]:
        dist[bf.index] = 0
    for pvn in pf.vertices:
        (vt, uv_old) = pVertTexVerts[pvn][pf.index]
        puv = pTexVertUv[vt]
        if puv:
            for bf in bEdgeFaces[be.index]:
                for n,bvn in enumerate(bf.vertices):
                    buvf = bTexFaces[bf.index]
                    #buv = getUvVert(buvf, n)
                    buv = buvf.get(n)
                    duv = buv - puv
                    dist[bf.index] += duv.length

    mindist = 1e6
    for bf in bEdgeFaces[be.index]:
        if dist[bf.index] < mindist:
            mindist = dist[bf.index]
            best = bf

    bv0 = bverts[be.vertices[0]]
    bv1 = bverts[be.vertices[1]]
    m0 = getFaceIndex(bv0.index, best)
    m1 = getFaceIndex(bv1.index, best)
    buvf = bTexFaces[best.index]
    #buv0 = getUvVert(buvf, m0)
    #buv1 = getUvVert(buvf, m1)
    buv0 = buvf.get(m0)
    buv1 = buvf.get(m1)
    vec0 = pv.co - bv0.co
    vec1 = pv.co - bv1.co
    vec = bv0.co - bv1.co
    dist0 = abs(vec.dot(vec0))
    dist1 = abs(vec.dot(vec1))
    eps = dist1/(dist0+dist1)
    uv = eps*buv0 + (1-eps)*buv1
    return uv

    best.select = True
    pf.select = True
    bv0.select = True
    bv1.select = True
    pv.select = True
    print(uv)
    print("  ", buv0)
    print("  ", buv1)
    foo

    return uv


def getFaceIndex(vn, f):
    n = 0
    for vn1 in f.vertices:
        if vn1 == vn:
            #print(v.index, n, list(f.vertices))
            return n
        n += 1
    raise MHError("Vert %d not in face %d %s" % (vn, f.index, list(f.vertices)))


def getSeamData(me, uvFaceVerts, edgeFaces):
    seamEdgeFaces = {}
    seamVertEdges = {}
    boundaryEdges = {}
    vertTexVerts = {}
    verts = me.vertices

    for v in me.vertices:
        vn = v.index
        seamVertEdges[vn] = []
        vertTexVerts[vn] = {}
        v.select = False

    meFaces = getFaces(me)
    for f in meFaces:
        fn = f.index
        for vn in f.vertices:
            n = getFaceIndex(vn, f)
            uvf = uvFaceVerts[fn]
            vertTexVerts[vn][fn]= uvf[n]

    for e in me.edges:
        en = e.index
        fcs = edgeFaces[en]
        if len(fcs) < 2:
            boundaryEdges[en] = True
            e.select = False
        else:
            vn0 = e.vertices[0]
            vn1 = e.vertices[1]
            if isSeam(vn0, vn1, fcs[0], fcs[1], vertTexVerts):
                #e.select = True
                seamEdgeFaces[en] = fcs
                seamVertEdges[vn0].append(e)
                seamVertEdges[vn1].append(e)
            else:
                e.select = False
    return (seamEdgeFaces, seamVertEdges, boundaryEdges, vertTexVerts)


def isSeam(vn0, vn1, f0, f1, vertTexVerts):
    (vt00, uv00) = vertTexVerts[vn0][f0.index]
    (vt01, uv01) = vertTexVerts[vn1][f0.index]
    (vt10, uv10) = vertTexVerts[vn0][f1.index]
    (vt11, uv11) = vertTexVerts[vn1][f1.index]
    d00 = uv00-uv10
    d11 = uv01-uv11
    d01 = uv00-uv11
    d10 = uv01-uv10
    #test1 = ((vt00 == vt10) and (vt01 == vt11))
    #test2 = ((vt00 == vt11) and (vt01 == vt10))
    test1 = ((d00.length < Epsilon) and (d11.length < Epsilon))
    test2 = ((d01.length < Epsilon) and (d10.length < Epsilon))
    if (test1 or test2):
        return False
    else:
        return True
        print("%d %s" % (vt00, uv00))
        print("%d %s" % (vt01, uv01))
        print("%d %s" % (vt10, uv10))
        print("%d %s" % (vt11, uv11))


def createFaceTable(verts, faces):
    table = {}
    for v in verts:
        table[v.index] = []
    for f in faces:
        for v in f.vertices:
            table[v].append(f)
    return table


def getSingleUvLoc(vn, table):
    (exact, buvs, wts) = table[vn]
    if exact == 1:
        return buvs
    elif exact == 2:
        return buvs[0]
    else:
        try:
            return buvs[0]*wts[0] + buvs[1]*wts[1] + buvs[2]*wts[2]
        except:
            for n in range(3):
                print(buvs[n], wts[n])
            halt


def getUvLoc(vn, f, uvface):
    for n,vk in enumerate(f.vertices):
        if vk == vn:
            return uvface[n]
    raise MHError("Vertex %d not in face %d??" % (vn,f))

#
#   Recover seams
#

def createSeamObject(context):
    ob = getHuman(context)
    scn = context.scene
    getFaces(ob.data)
    texFaces = getTexFaces(ob.data, 0)
    vertList, pairList, _edgeList = getSeams(ob, texFaces, scn)
    coords = coordList(vertList, ob.data.vertices)
    sme = bpy.data.meshes.new("Seams")
    sme.from_pydata(coords, pairList, [])
    sme.update(calc_edges=True)
    sob = bpy.data.objects.new("Seams", sme)
    sob.show_x_ray = True
    scn.objects.link(sob)
    print("Seam object %s created")
    return


def autoSeams(context):
    (bob, pob) = getObjectPair(context)
    checkObjectOK(bob, context, False)
    checkObjectOK(pob, context, True)
    scn = context.scene

    # Do operator stuff first, because they move verts in memory.
    scn.objects.active = pob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.mark_seam(clear=True)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    getFaces(bob.data)
    texFaces = getTexFaces(bob.data, 0)
    (bvnums, _pairList, bedges) = getSeams(bob, texFaces, scn)

    pVertEdges = {}
    for pv in pob.data.vertices:
        pVertEdges[pv.index] = []
    for pe in pob.data.edges:
        pVertEdges[pe.vertices[0]].append(pe)
        pVertEdges[pe.vertices[1]].append(pe)

    closest = readClosets(pob)
    #closest = {}
    if not closest:
        print("Associate base and proxy verts. This can be slow.")
        for bv in bob.data.vertices:
            if bv.index % 1000 == 0:
                print(bv.index)
            mindist = 1e12
            best = None
            for pv in pob.data.vertices:
                vec = pv.co - bv.co
                if vec.length < mindist:
                    best = pv
                    mindist = vec.length
            closest[bv.index] = best
        saveClosest(closest)
    for pv in closest.values():
        pass
        #pv.select = True

    print("Marking proxy seams")

    for be in bedges:
        pv0 = closest[be.vertices[0]]
        pv1 = closest[be.vertices[1]]
        #print("Mark", be.index, tuple(be.vertices), pv0.index, pv1.index)
        markEdges(pv0, pv1, pob, pVertEdges, {}, 5)

    return
    print("Optimizing")

    for pf in pob.data.polygons:
        nseams = 0
        edges = []
        for verts in pf.edge_keys:
            pe = findEdge(verts, pVertEdges)
            edges.append(pe)
            if pe.use_seam:
                nseams += 1
        if nseams == 3:
            pf.select = True
            for pe in edges:
                pe.use_seam = not pe.use_seam
            halt

def otherEnd(e, v, ob):
    v1 = ob.data.vertices[e.vertices[0]]
    if v1.index == v.index:
        v1 = ob.data.vertices[e.vertices[1]]
    return v1


def findEdge(verts, vertEdges):
    vn1,vn2 = verts
    for e in vertEdges[vn1]:
        if e in vertEdges[vn2]:
            return e
    print(verts)
    print(vertEdges[vn1])
    print(vertEdges[vn2])
    halt


def markEdges(pv0, pv1, pob, pVertEdges, taken, depth):
    if pv0 == pv1 or depth < 0:
        return
    vec = pv0.co - pv1.co
    bestVert = bestEdge = None
    minDist = 1e6

    for pe in pVertEdges[pv0.index]:
        try:
            taken[pe]
            continue
        except KeyError:
            pass
        pv2 = otherEnd(pe, pv0, pob)
        vec = pv2.co - pv1.co
        if vec.length < minDist:
            minDist = vec.length
            bestVert = pv2
            bestEdge = pe

    if bestVert is not None:
        #print("    %d - %d - %d (%.6f) %d" % (pv0.index, bestVert.index, pv1.index, minDist, bestEdge.index))
        bestEdge.use_seam = True
        taken[bestEdge] = True
        markEdges(bestVert, pv1, pob, pVertEdges, taken, depth-1)


def saveClosest(closest):
    fname = settingsFile("closest")
    fp = mc.openOutputFile(fname)
    if fp:
        for bvn,pv in closest.items():
            fp.write("%d %d\n" % (bvn, pv.index))
        fp.close()


def readClosets(pob):
    closest = {}
    fname = settingsFile("closest")
    try:
        fp = open(fname, "rU")
    except FileNotFoundError:
        print("Did not find %s." % fname)
        return closest
    for line in fp:
        words = line.split()
        closest[int(words[0])] = pob.data.vertices[int(words[1])]
    fp.close()
    return closest


def setSeams(context):
    scn = context.scene
    clothing = None
    seams = None
    for ob in scn.objects:
        if ob.select and not ob.MhHuman:
            faces = getFaces(ob.data)
            if faces:
                clothing = ob
            else:
                seams = ob
    if not (clothing and seams):
        raise MHError("A clothing and a seam object must be selected")
    checkObjectOK(clothing, context, True)
    checkObjectOK(seams, context, False)

    for e in clothing.data.edges:
        e.use_seam = False

    for se in seams.data.edges:
        dist = 1e6
        sv0 = seams.data.vertices[se.vertices[0]]
        sv1 = seams.data.vertices[se.vertices[1]]
        best = None
        for e in clothing.data.edges:
            v0 = clothing.data.vertices[e.vertices[0]]
            v1 = clothing.data.vertices[e.vertices[1]]
            d00 = v0.co - sv0.co
            d01 = v0.co - sv1.co
            d10 = v1.co - sv0.co
            d11 = v1.co - sv1.co
            d0 = d00.length + d11.length
            d1 = d01.length + d10.length
            if d1 < d0:
                d0 = d1
            if d0 < dist:
                dist = d0
                best = e
        best.use_seam = True
        best.select = True
        if se.index % 100 == 0:
            print(se.index)
    print("Seams set for object %s\n" % clothing.name)
    return


def coordList(vertList, verts):
    coords = []
    for vn in vertList:
        coords.append(verts[vn].co)
    return coords


def getSeams(ob, texFaces, scn):
    verts = ob.data.vertices
    meFaces = getFaces(ob.data)
    faceTable = createFaceTable(verts, meFaces)
    onEdges = {}
    for v in verts:
        onEdges[v.index] = False
    for v in ob.data.vertices:
        if isOnEdge(v, faceTable, texFaces):
            onEdges[v.index] = True

    vertList = []
    edgeList = []
    pairList = []
    n = 0
    for e in ob.data.edges:
        v0 = e.vertices[0]
        v1 = e.vertices[1]
        e.use_seam = (onEdges[v0] and onEdges[v1])
        if e.use_seam:
            vertList += [v0, v1]
            pairList.append((n,n+1))
            n += 2
            edgeList.append(e)
    return (vertList, pairList, edgeList)


def isOnEdge(v, faceTable, texFaces):
    if v.index >= theSettings.nBodyVerts:
        return False
    uvloc = None
    for f in faceTable[v.index]:
        uvface = texFaces[f.index].uvs
        #print("F", v.index, f.index, uvface)
        for n,vn in enumerate(f.vertices):
            if vn == v.index:
                uvnloc = uvface[n]
                if uvloc:
                    dist = uvnloc - uvloc
                    if dist.length > 0.01:
                        return True
                else:
                    uvloc = uvnloc
    return False


def writeTexVert(fp, uv):
    fp.write("%.4f %.4f\n" % (uv[0], uv[1]))

