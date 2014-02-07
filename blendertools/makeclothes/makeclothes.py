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
Utility for making clothes to MH characters.

"""

import bpy
import os
import math
import random
import ast
from bpy.props import *
from mathutils import Vector

from maketarget.utils import getMHBlenderDirectory
from .error import MHError, addWarning
from . import mc
from . import materials

#
#   Global variables
#

Epsilon = 1e-4

theSettings = mc.settings["hm08"]

#
#   isClothing(ob):
#   getHuman(context):
#   getClothing(context):
#   getObjectPair(context):
#

def isClothing(ob):
    return ((ob.type == 'MESH') and not isOkHuman(ob))


def isOkHuman(ob):
    if not ob.MhHuman:
        return False
    if not theSettings:
        return True
    nverts = len(ob.data.vertices)
    if nverts in getLastVertices():
        return True
    else:
        ob.MhHuman = False
        return False


def getLastVertices():
    vlist = [ vs[1] for vs in theSettings.vertices.values()]
    vlist.append(theSettings.nTotalVerts)
    vlist.sort()
    return vlist


def getHuman(context):
    for ob in context.scene.objects:
        if ob.select and isOkHuman(ob):
            return ob
    raise MHError("No human selected")


def getClothing(context):
    for ob in context.scene.objects:
        if ob.select and isClothing(ob):
            return ob
    for ob in context.scene.objects:
        if ob.select and ob.type == 'MESH' and not isOkHuman(ob):
            return ob
    raise MHError("No clothing selected")


def getObjectPair(context):
    human = None
    clothing = None
    scn = context.scene
    for ob in scn.objects:
        if ob.select:
            if isOkHuman(ob):
                if human:
                    raise MHError("Two humans selected: %s and %s" % (human.name, ob.name))
                else:
                    human = ob
            elif ob.type == 'MESH':
                if clothing:
                    raise MHError("Two pieces of clothing selected: %s and %s" % (clothing.name, ob.name))
                else:
                    clothing = ob
    if not human:
        raise MHError("No human selected")
    if not clothing:
        raise MHError("No clothing selected")
    return (human, clothing)


def selectHelpers(context):
    ob = context.object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    n0 = theSettings.vertices["Penis"][0]
    n1 = theSettings.nTotalVerts
    for n in range(n0,n1):
        ob.data.vertices[n].select = True
    bpy.ops.object.mode_set(mode='EDIT')

#
#   snapSelectedVerts(context):
#

def snapSelectedVerts(context):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    selected = []
    for v in ob.data.vertices:
        if v.select:
            selected.append(v)
    bpy.ops.object.mode_set(mode='EDIT')
    for v in selected:
        v.select = True
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.translate(
            snap=True,
            snap_target='CLOSEST',
            snap_point=(0, 0, 0),
            snap_align=False,
            snap_normal=(0, 0, 0))
    return

#
#    selectVerts(verts, ob):
#

def selectVerts(verts, ob):
    for v in ob.data.vertices:
        v.select = False
    for v in verts:
        v.select = True
    return

#
#
#

def loadHuman(context):
    from maketarget import mt, import_obj, utils
    from maketarget.maketarget import afterImport, newTarget, applyTargets

    scn = context.scene
    bodytype = scn.MCBodyType
    if bodytype[:2] == "h-":
        bodytype = bodytype[2:]
        helpers = True
    else:
        helpers = False

    if helpers:
        basepath = mt.baseMhcloFile
        import_obj.importBaseMhclo(context, basepath)
        afterImport(context, basepath, False, True)
    else:
        basepath = mt.baseObjFile
        import_obj.importBaseObj(context, basepath)
        afterImport(context, basepath, True, False)

    if bodytype == 'None':
        newTarget(context)
        found = True
    else:
        trgpath = os.path.join(os.path.dirname(__file__), "targets", bodytype + ".target")
        try:
            utils.loadTarget(trgpath, context)
            found = True
        except FileNotFoundError:
            found = False
    if not found:
        raise MHError("Target \"%s\" not found.\nPath \"%s\" does not seem to be the path to the MakeHuman program" % (trgpath, scn.MhProgramPath))
    applyTargets(context)
    ob = context.object
    ob.name = "Human"
    ob.MhHuman = True
    if helpers:
        autoVertexGroups(ob, 'Helpers', 'Tights')
    else:
        autoVertexGroups(ob, 'Body', None)
    clearSelection()


#
#
#

theShapeKeys = [
    #'Breathe',
    ]

#
#    findClothes(context, hum, clo, log):
#

def findClothes(context, hum, clo, log):
    base = hum.data
    proxy = clo.data
    scn = context.scene

    bestVerts = []
    for pv in proxy.vertices:
        try:
            pindex = pv.groups[0].group
        except:
            pindex = -1
        if pindex < 0:
            selectVerts([pv], clo)
            raise MHError("Clothes %s vert %d not member of any group" % (clo.name, pv.index))

        gname = clo.vertex_groups[pindex].name
        bindex = None
        for bvg in hum.vertex_groups:
            if bvg.name == gname:
                bindex = bvg.index
        if bindex == None:
            raise MHError("Did not find vertex group %s in base mesh" % gname)

        mverts = []
        for n in range(scn.MCListLength):
            mverts.append((None, 1e6))

        exact = False
        for bv in base.vertices:
            if exact:
                break
            for grp in bv.groups:
                if grp.group == bindex:
                    vec = pv.co - bv.co
                    n = 0
                    for (mv,mdist) in mverts:
                        if vec.length < Epsilon:
                            mverts[0] = (bv, -1)
                            exact = True
                            break
                        if vec.length < mdist:
                            for k in range(n+1, scn.MCListLength):
                                j = scn.MCListLength-k+n
                                mverts[j] = mverts[j-1]
                            mverts[n] = (bv, vec.length)
                            break
                        n += 1

        (mv, mindist) = mverts[0]
        if mv:
            if pv.index % 10 == 0:
                print(pv.index, mv.index, mindist, gname, pindex, bindex)
            if log:
                log.write("%d %d %.5f %s %d %d\n" % (pv.index, mv.index, mindist, gname, pindex, bindex))
        else:
            msg = (
            "Failed to find vert %d in group %s.\n" % (pv.index, gname) +
            "Clothes index %d, Human index %d\n" % (pindex, bindex) +
            "Vertex coordinates (%.4f %.4f %.4f)\n" % (pv.co[0], pv.co[1], pv.co[2])
            )
            selectVerts([pv], clo)
            raise MHError(msg)
        if mindist > 50:
            msg = (
            "Vertex %d is %f dm away from closest body vertex in group %s.\n" % (pv.index, mindist, gname) +
            "Max allowed value is 5dm. Check human and clothes scales.\n" +
            "Vertex coordinates (%.4f %.4f %.4f)\n" % (pv.co[0], pv.co[1], pv.co[2])
            )
            selectVerts([pv], clo)
            raise MHError(msg)

        if gname[0:3] != "Mid" and gname[-2:] != "_M":
            bindex = -1
        bestVerts.append((pv, bindex, exact, mverts, []))

    print("Setting up face table")
    vfaces = {}
    for v in base.vertices:
        vfaces[v.index] = []
    baseFaces = getFaces(base)
    for f in baseFaces:
        v0 = f.vertices[0]
        v1 = f.vertices[1]
        v2 = f.vertices[2]
        if len(f.vertices) == 4:
            v3 = f.vertices[3]
            t0 = [v0,v1,v2]
            t1 = [v1,v2,v3]
            t2 = [v2,v3,v0]
            t3 = [v3,v0,v1]
            vfaces[v0].extend( [t0,t2,t3] )
            vfaces[v1].extend( [t0,t1,t3] )
            vfaces[v2].extend( [t0,t1,t2] )
            vfaces[v3].extend( [t1,t2,t3] )
        else:
            t = [v0,v1,v2]
            vfaces[v0].append(t)
            vfaces[v1].append(t)
            vfaces[v2].append(t)

    print("Finding weights")
    for (pv, bindex, exact, mverts, fcs) in bestVerts:
        if exact:
            continue
        for (bv,mdist) in mverts:
            if bv:
                for f in vfaces[bv.index]:
                    v0 = base.vertices[f[0]]
                    v1 = base.vertices[f[1]]
                    v2 = base.vertices[f[2]]
                    if (bindex >= 0) and (pv.co[0] < 0.01) and (pv.co[0] > -0.01):
                        wts = midWeights(pv, bindex, v0, v1, v2, hum, clo)
                    else:
                        wts = cornerWeights(pv, v0, v1, v2, hum, clo)
                    fcs.append((f, wts))

    print("Finding best weights")
    alwaysOutside = False
    minOffset = 0.0
    useProjection = False

    bestFaces = []
    badVerts = []
    for (pv, bindex, exact, mverts, fcs) in bestVerts:
        #print(pv.index)
        pv.select = False
        if exact:
            bestFaces.append((pv, True, mverts, 0, 0))
            continue
        minmax = -1e6
        for (fverts, wts) in fcs:
            w = minWeight(wts)
            if w > minmax:
                minmax = w
                bWts = wts
                bVerts = fverts
        if minmax < scn.MCThreshold:
            badVerts.append(pv.index)
            pv.select = True
            (mv, mdist) = mverts[0]
            bVerts = [mv.index,0,1]
            bWts = (1,0,0)

        v0 = base.vertices[bVerts[0]]
        v1 = base.vertices[bVerts[1]]
        v2 = base.vertices[bVerts[2]]

        est = bWts[0]*v0.co + bWts[1]*v1.co + bWts[2]*v2.co
        diff = pv.co - est
        bestFaces.append((pv, False, bVerts, bWts, diff))

    return bestFaces


#
#    minWeight(wts)
#

def minWeight(wts):
    best = 1e6
    for w in wts:
        if w < best:
            best = w
    return best

#
#    cornerWeights(pv, v0, v1, v2, hum, clo):
#
#    px = w0*x0 + w1*x1 + w2*x2
#    py = w0*y0 + w1*y1 + w2*y2
#    pz = w0*z0 + w1*z1 + w2*z2
#
#    w2 = 1-w0-w1
#
#    w0*(x0-x2) + w1*(x1-x2) = px-x2
#    w0*(y0-y2) + w1*(y1-y2) = py-y2
#
#    a00*w0 + a01*w1 = b0
#    a10*w0 + a11*w1 = b1
#
#    det = a00*a11 - a01*a10
#
#    det*w0 = a11*b0 - a01*b1
#    det*w1 = -a10*b0 + a00*b1
#

def cornerWeights(pv, v0, v1, v2, hum, clo):
    r0 = v0.co
    r1 = v1.co
    r2 = v2.co
    u01 = r1-r0
    u02 = r2-r0
    n = u01.cross(u02)
    n.normalize()

    u = pv.co-r0
    r = r0 + u - n*u.dot(n)

    """
    a00 = r0[0]-r2[0]
    a01 = r1[0]-r2[0]
    a10 = r0[1]-r2[1]
    a11 = r1[1]-r2[1]
    b0 = r[0]-r2[0]
    b1 = r[1]-r2[1]
    """

    e0 = u01
    e0.normalize()
    e1 = n.cross(e0)
    e1.normalize()

    u20 = r0-r2
    u21 = r1-r2
    ur2 = r-r2

    a00 = u20.dot(e0)
    a01 = u21.dot(e0)
    a10 = u20.dot(e1)
    a11 = u21.dot(e1)
    b0 = ur2.dot(e0)
    b1 = ur2.dot(e1)

    det = a00*a11 - a01*a10
    if abs(det) < 1e-20:
        print("Clothes vert %d mapped to degenerate triangle (det = %g) with corners" % (pv.index, det))
        print("r0 ( %.6f  %.6f  %.6f )" % (r0[0], r0[1], r0[2]))
        print("r1 ( %.6f  %.6f  %.6f )" % (r1[0], r1[1], r1[2]))
        print("r2 ( %.6f  %.6f  %.6f )" % (r2[0], r2[1], r2[2]))
        print("A [ %.6f %.6f ]\n  [ %.6f %.6f ]" % (a00,a01,a10,a11))
        selectVerts([pv], clo)
        selectVerts([v0, v1, v2], hum)
        raise MHError("Singular matrix in cornerWeights")

    w0 = (a11*b0 - a01*b1)/det
    w1 = (-a10*b0 + a00*b1)/det

    return (w0, w1, 1-w0-w1)

#
#   midWeights(pv, bindex, v0, v1, v2, hum, clo):
#

def midWeights(pv, bindex, v0, v1, v2, hum, clo):
    #print("Mid", pv.index, bindex)
    pv.select = True
    if isInGroup(v0, bindex):
        v0.select = True
        if isInGroup(v1, bindex):
            v1.select = True
            return midWeight(pv, v0.co, v1.co)
        elif isInGroup(v2, bindex):
            (w1, w0, w2) = midWeight(pv, v0.co, v2.co)
            v2.select = True
            return (w0, w1, w2)
    elif isInGroup(v1, bindex) and isInGroup(v2, bindex):
        (w1, w2, w0) = midWeight(pv, v1.co, v2.co)
        v1.select = True
        v2.select = True
        return (w0, w1, w2)
    #print("  Failed mid")
    return cornerWeights(pv, v0, v1, v2, hum, clo)

def isInGroup(v, bindex):
    for g in v.groups:
        if g.group == bindex:
            return True
    return False

def midWeight(pv, r0, r1):
    u01 = r1-r0
    d01 = u01.length
    u = pv.co-r0
    s = u.dot(u01)
    w = s/(d01*d01)
    return (1-w, w, 0)

#
#    writeClothes(context, hum, clo, data, matfile):
#

def getHeader(scn):
    if scn.MCAuthor == "Unknown":
        addWarning("Author unknown")
    return (
        "# Exported from MakeClothes (TM)\n" +
        "# author %s\n" % scn.MCAuthor +
        "# license %s\n" % scn.MCLicense +
        "# homepage %s\n" % scn.MCHomePage)


def writeClothesHeader(fp, scn):
    import sys
    if sys.platform == 'win32':
        # Avoid error message in blender by using a version without ctypes
        from . import uuid4 as uuid
    else:
        import uuid

    fp.write(getHeader(scn))
    fp.write("uuid %s\n" % uuid.uuid4())
    if theSettings:
        fp.write("basemesh %s\n" % theSettings.baseMesh)
    for n in range(1,6):
        tag = getattr(scn, "MCTag%d" % n)
        if tag:
            fp.write("tag %s\n" % tag)
    fp.write("\n")


def writeClothes(context, hum, clo, data, matfile):
    scn = context.scene
    firstVert = 0
    (outpath, outfile) = mc.getFileName(clo, scn.MhClothesDir, "mhclo")
    fp = mc.openOutputFile(outfile)
    writeClothesHeader(fp, scn)
    fp.write("name %s\n" % clo.name.replace(" ","_"))
    fp.write("obj_file %s.obj\n" % mc.goodName(clo.name))
    vnums = getBodyPartVerts(scn)
    printScale(fp, hum, scn, 'x_scale', 0, vnums[0])
    printScale(fp, hum, scn, 'z_scale', 1, vnums[1])
    printScale(fp, hum, scn, 'y_scale', 2, vnums[2])
    if scn.MCScaleUniform:
        fp.write("uniform_scale %.4f\n" % scn.MCScaleCorrect)

    writeStuff(fp, clo, context, matfile)

    fp.write("verts %d\n" % (firstVert))

    if scn.MCSelfClothed:
        for n in range(theSettings.vertices["Penis"][0]):
            fp.write("%5d\n" % n)

    for (pv, exact, verts, wts, diff) in data:
        if exact:
            (bv, dist) = verts[0]
            fp.write("%5d\n" % bv.index)
        else:
            fp.write("%5d %5d %5d %.5f %.5f %.5f %.5f %.5f %.5f\n" % (
                verts[0], verts[1], verts[2], wts[0], wts[1], wts[2], diff[0], diff[2], -diff[1]))
    fp.write('\n')
    printDeleteVerts(fp, hum)
    printMhcloUvLayers(fp, clo, scn, True)
    fp.close()
    print("%s done" % outfile)


def printMhcloUvLayers(fp, clo, scn, hasObj, offset=0):
    me = clo.data
    if me.uv_textures:
        for layer,uvtex in enumerate(me.uv_textures):
            if hasObj and (layer == scn.MCTextureLayer):
                continue
            if scn.MCAllUVLayers or not hasObj:
                printLayer = layer
            else:
                printLayer = 1
                if layer != scn.MCMaskLayer:
                    continue
            (vertEdges, vertFaces, edgeFaces, faceEdges, faceNeighbors, uvFaceVertsList, texVertsList) = setupTexVerts(clo)
            texVerts = texVertsList[layer]
            uvFaceVerts = uvFaceVertsList[layer]
            nTexVerts = len(texVerts)
            fp.write("texVerts %d\n" % printLayer)
            for vtn in range(nTexVerts):
                vt = texVerts[vtn]
                fp.write("%.4f %.4f\n" % (vt[0], vt[1]))
            fp.write("texFaces %d\n" % printLayer)
            meFaces = getFaces(me)
            for f in meFaces:
                uvVerts = uvFaceVerts[f.index]
                uvLine = []
                for n,v in enumerate(f.vertices):
                    (vt, uv) = uvVerts[n]
                    uvLine.append("%d" % (vt+offset))
                    #fp.write("(%.3f %.3f) " % (uv[0], uv[1]))
                fp.write((" ".join(uvLine)) +"\n")


def reexportMhclo(context):
    clo = getClothing(context)
    scn = context.scene
    scn.objects.active = clo
    bpy.ops.object.mode_set(mode='OBJECT')
    (outpath, outfile) = mc.getFileName(clo, scn.MhClothesDir, "mhclo")
    matfile = materials.writeMaterial(clo, scn.MhClothesDir)

    lines = []
    print("Reading clothes file %s" % outfile)
    fp = open(outfile, "r")
    for line in fp:
        lines.append(line)
    fp.close()

    fp = mc.openOutputFile(outfile)
    doingStuff = False
    for line in lines:
        words = line.split()
        if len(words) == 0:
            fp.write(line)
        elif (words[0] == "#"):
            if words[1] in ["texVerts", "texFaces"]:
                break
            elif words[1] == "z_depth":
                writeStuff(fp, clo, context, matfile)
                doingStuff = True
            elif words[1] == "use_projection":
                doingStuff = False
            elif doingStuff:
                pass
            else:
                fp.write(line)
        elif not doingStuff:
            fp.write(line)
    printMhcloUvLayers(fp, clo, scn, True)
    fp.close()
    print("%s written" % outfile)
    return


def printDeleteVerts(fp, hum):
    kill = None
    for g in hum.vertex_groups:
        if g.name == "Delete":
            kill = g
            break
    if not kill:
        return

    killList = []
    for v in hum.data.vertices:
        for vg in v.groups:
            if vg.group == kill.index:
                killList.append(v.index)
    if not killList:
        return

    fp.write("delete_verts\n")
    n = 0
    vn0 = -100
    sequence = False
    for vn in killList:
        if vn != vn0+1:
            if sequence:
                fp.write("- %d " % vn0)
            n += 1
            if n % 10 == 0:
                fp.write("\n")
            sequence = False
            fp.write("%d " % vn)
        else:
            if vn0 < 0:
                fp.write("%d " % vn)
            sequence = True
        vn0 = vn
    if sequence:
        fp.write("- %d" % vn)
    fp.write("\n")

#
#   writeStuff(fp, clo, context, matfile):
#   From z_depth to use_projection
#

def writeStuff(fp, clo, context, matfile):
    scn = context.scene
    fp.write("z_depth %d\n" % scn.MCZDepth)

    for mod in clo.modifiers:
        if mod.type == 'SHRINKWRAP':
            fp.write("shrinkwrap %.3f\n" % (mod.offset))
        elif mod.type == 'SUBSURF':
            fp.write("subsurf %d %d\n" % (mod.levels, mod.render_levels))
        elif mod.type == 'SOLIDIFY':
            fp.write("solidify %.3f %.3f\n" % (mod.thickness, mod.offset))

    for skey in theShapeKeys:
        if getattr(scn, "MC" + skey):
            fp.write("shapekey %s\n" % skey)

    if matfile:
        fp.write("material %s\n" % matfile)


#
#   deleteStrayVerts(context, ob):
#

def deleteStrayVerts(context, ob):
    scn = context.scene
    scn.objects.active = ob
    bpy.ops.object.mode_set(mode='OBJECT')
    verts = ob.data.vertices
    onFaces = {}
    for v in verts:
        onFaces[v.index] = False
    faces = getFaces(ob.data)
    for f in faces:
        for vn in f.vertices:
            onFaces[vn] = True
    for v in verts:
        if not onFaces[v.index]:
            raise MHError("Mesh %s has stray vert %d" % (ob.name, v.index))
        return

#
#   exportObjFile(context):
#

def exportObjFile(context):
    scn = context.scene
    ob = getClothing(context)
    deleteStrayVerts(context, ob)
    (objpath, objfile) = mc.getFileName(ob, scn.MhClothesDir, "obj")
    fp = mc.openOutputFile(objfile)
    fp.write(getHeader(scn))

    me = ob.data

    vlist = ["v %.4f %.4f %.4f" % (v.co[0], v.co[2], -v.co[1]) for v in ob.data.vertices]
    fp.write("\n".join(vlist) + "\n")

    if me.uv_textures:
        (vertEdges, vertFaces, edgeFaces, faceEdges, faceNeighbors, uvFaceVertsList, texVertsList) = setupTexVerts(ob)
        layer = scn.MCTextureLayer
        writeObjTextureData(fp, me, texVertsList[layer], uvFaceVertsList[layer])
    else:
        meFaces = getFaces(me)
        flist = []
        for f in meFaces:
            l = ["f"]
            for vn in f.vertices:
                l.append("%d" % (vn+1))
            flist.append(" ".join(l))
        fp.write("\n".join(flist))

    fp.close()
    print(objfile, "exported")

    npzfile = os.path.splitext(objfile)[0] + ".npz"
    try:
        os.remove(npzfile)
        print(npzfile, "removed")
    except FileNotFoundError:
        pass


def writeObjTextureData(fp, me, texVerts, uvFaceVerts):
    nTexVerts = len(texVerts)
    vlist = []
    for vtn in range(nTexVerts):
        vt = texVerts[vtn]
        vlist.append("vt %.4f %.4f" % (vt[0], vt[1]))
    fp.write("\n".join(vlist) + "\n")

    meFaces = getFaces(me)
    flist = []
    for f in meFaces:
        uvVerts = uvFaceVerts[f.index]
        l = ["f"]
        for n,v in enumerate(f.vertices):
            (vt, uv) = uvVerts[n]
            l.append("%d/%d" % (v+1, vt+1))
        flist.append(" ".join(l))
    fp.write("\n".join(flist))


def writeColor(fp, string1, string2, color, intensity):
    fp.write(
        "%s %.4f %.4f %.4f\n" % (string1, color[0], color[1], color[2]) +
        "%s %.4g\n" % (string2, intensity))


def printScale(fp, hum, scn, name, index, vnums):
    verts = hum.data.vertices
    n1,n2 = vnums
    if n1 >=0 and n2 >= 0:
        x1 = verts[n1].co[index]
        x2 = verts[n2].co[index]
        fp.write("%s %d %d %.4f\n" % (name, n1, n2, abs(x1-x2)/scn.MCScaleCorrect))
    return

#
#   setupTexVerts(ob):
#

def setupTexVerts(ob):
    me = ob.data
    vertEdges = {}
    vertFaces = {}
    for v in me.vertices:
        vertEdges[v.index] = []
        vertFaces[v.index] = []
    for e in me.edges:
        for vn in e.vertices:
            vertEdges[vn].append(e)
    meFaces = getFaces(me)
    for f in meFaces:
        for vn in f.vertices:
            vertFaces[vn].append(f)

    edgeFaces = {}
    for e in me.edges:
        edgeFaces[e.index] = []
    faceEdges = {}
    for f in meFaces:
        faceEdges[f.index] = []
    for f in meFaces:
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
    for f in meFaces:
        faceNeighbors[f.index] = []
    for f in meFaces:
        for e in faceEdges[f.index]:
            for f1 in edgeFaces[e.index]:
                if f1 != f:
                    faceNeighbors[f.index].append((e,f1))

    uvFaceVertsList = []
    texVertsList = []
    for index,uvtex in enumerate(me.uv_textures):
        uvFaceVerts = {}
        uvFaceVertsList.append(uvFaceVerts)
        for f in meFaces:
            uvFaceVerts[f.index] = []
        vtn = 0
        texVerts = {}
        texVertsList.append(texVerts)

        uvloop = me.uv_layers[index]
        n = 0
        for f in me.polygons:
            for vn in f.vertices:
                uvv = uvloop.data[n]
                n += 1
                vtn = findTexVert(uvv.uv, vtn, f, faceNeighbors, uvFaceVerts, texVerts, ob)
    return (vertEdges, vertFaces, edgeFaces, faceEdges, faceNeighbors, uvFaceVertsList, texVertsList)


def findTexVert(uv, vtn, f, faceNeighbors, uvFaceVerts, texVerts, ob):
    for (e,f1) in faceNeighbors[f.index]:
        for (vtn1,uv1) in uvFaceVerts[f1.index]:
            vec = uv - uv1
            if vec.length < 1e-8:
                uvFaceVerts[f.index].append((vtn1,uv))
                return vtn
    uvFaceVerts[f.index].append((vtn,uv))
    texVerts[vtn] = uv
    return vtn+1


#
#   storeData(clo, hum, data):
#   restoreData(context):
#

def storeData(clo, hum, data):
    outfile = settingsFile("stored")
    fp = mc.openOutputFile(outfile)
    fp.write("%s\n" % clo.name)
    fp.write("%s\n" % hum.name)
    for (pv, exact, verts, wts, diff) in data:
        if exact:
            bv,n = verts[0]
            fp.write("%d %d %d\n" % (pv.index, exact, bv.index))
        else:
            fp.write("%d %d\n" % (pv.index, exact))
            fp.write("%s\n" % verts)
            fp.write("(%s,%s,%s)\n" % wts)
            fp.write("(%s,%s,%s)\n" % (diff[0],diff[1],diff[2]))
    fp.close()
    return

def parse(string):
    return ast.literal_eval(string)

def restoreData(context):
    (hum, clo) = getObjectPair(context)
    fname = settingsFile("stored")
    fp = mc.openInputFile(fname)
    status = 0
    data = []
    for line in fp:
        #print(line)
        words = line.split()
        if status == 0:
            pname = line.rstrip()
            if pname != clo.name:
                raise MHError(
                "Restore error: stored data for %s does not match selected object %s\n" % (pname, clo.name) +
                "Make clothes for %s first\n" % clo.name)
            status = 10
        elif status == 10:
            bname = line.rstrip()
            if bname != hum.name:
                raise MHError(
                "Restore error: stored human %s does not match selected human %s\n" % (bname, hum.name) +
                "Make clothes for %s first\n" % clo.name)
            status = 1
        elif status == 1:
            pv = clo.data.vertices[int(words[0])]
            exact = int(words[1])
            if exact:
                bv = hum.data.vertices[int(words[2])]
                data.append((pv, exact, ((bv,-1),0,1), 0, 0))
                status = 1
            else:
                status = 2
        elif status == 2:
            verts = parse(line)
            if exact:
                data.append((pv, exact, verts, 0, 0))
                status = 1
            else:
                status = 3
        elif status == 3:
            wts = parse(line)
            status = 4
        elif status == 4:
            diff = Vector( parse(line) )
            data.append((pv, exact, verts, wts, diff))
            status = 1
    hum = context.scene.objects[bname]
    return (hum, data)

#
#    makeClothes(context, doFindClothes):
#

def makeClothes(context, doFindClothes):
    from .project import saveClosest
    (hum, clo) = getObjectPair(context)
    scn = context.scene
    checkNoTriangles(scn, clo)
    checkObjectOK(hum, context, False)
    autoVertexGroupsIfNecessary(hum, 'Selected')
    #checkAndUnVertexDiamonds(context, hum)
    checkObjectOK(clo, context, True)
    autoVertexGroupsIfNecessary(clo)
    checkSingleVertexGroups(clo, scn)
    saveClosest({})
    if scn.MCLogging:
        logfile = '%s/clothes.log' % scn.MhClothesDir
        log = mc.openOutputFile(logfile)
    else:
        log = None
    matfile = materials.writeMaterial(clo, scn.MhClothesDir)
    if doFindClothes:
        data = findClothes(context, hum, clo, log)
        storeData(clo, hum, data)
    else:
        (hum, data) = restoreData(context)
    writeClothes(context, hum, clo, data, matfile)
    if log:
        log.close()
    return


def checkNoTriangles(scn, ob):
    strayVerts = {}
    nPoles = {}
    for vn in range(len(ob.data.vertices)):
        strayVerts[vn] = True
        nPoles[vn] = 0

    for f in ob.data.polygons:
        if len(f.vertices) != 4:
            msg = "Object %s\ncan not be used for clothes creation\nbecause it has non-quad faces.\n" % (ob.name)
            raise MHError(msg)
        for vn in f.vertices:
            strayVerts[vn] = False
            nPoles[vn] += 1

    stray = [vn for vn in strayVerts.keys() if strayVerts[vn]]
    if len(stray) > 0:
        highlightVerts(scn, ob, stray)
        msg = "Object %s\ncan not be used for clothes creation\nbecause it has stray verts:\n  %s" % (ob.name, stray)
        raise MHError(msg)

    excess = [vn for vn in nPoles.keys() if nPoles[vn] > 8]
    if len(excess) > 0:
        highlightVerts(scn, ob, excess)
        msg = "Object %s\ncan not be used for clothes creation\nbecause it has verts with more than 8 poles:\n  %s" % (ob.name, excess)
        raise MHError(msg)


def highlightVerts(scn, ob, verts):
    bpy.ops.object.mode_set(mode='OBJECT')
    scn.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for vn in verts:
        print(vn)
        ob.data.vertices[vn].select = True
    bpy.ops.object.mode_set(mode='EDIT')


def checkObjectOK(ob, context, isClothing):
    old = context.object
    scn = context.scene
    scn.objects.active = ob
    word = None
    err = False
    line2 = "Apply, create or delete before proceeding.\n"

    if ob.location.length > Epsilon:
        word = "object translation"
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    eu = ob.rotation_euler

    if abs(eu.x) + abs(eu.y) + abs(eu.z) > Epsilon:
        word = "object rotation"
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    vec = ob.scale - Vector((1,1,1))

    if vec.length > Epsilon:
        word = "object scaling"
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    if ob.constraints:
        word = "constraints"
        err = True

    for mod in ob.modifiers:
        if (mod.type in ['CHILD_OF', 'ARMATURE']) and mod.show_viewport:
            word = "an enabled %s modifier" % mod.type
            mod.show_viewport = False

    if ob.data.shape_keys:
        word = "shape_keys"
        err = True

    if ob.parent:
        word = "parent"
        ob.parent = None

    if isClothing:
        try:
            ob.data.uv_layers[scn.MCTextureLayer]
        except:
            word = "no texture layers"
            err = True

        if len(ob.data.uv_textures) > 1:
            word = "%d texture layers. Must be exactly one." % len(ob.data.uv_textures)
            err = True

        if len(ob.data.materials) >= 2:
            word = "%d materials. Must be at most one." % len(ob.data.materials)
            err = True

        #if not materials.checkObjectHasDiffuseTexture(ob):
        #    word = "no diffuse image texture"
        #    line2 = "Create texture or delete material before proceeding.\n"
        #    err = True

    if word:
        msg = "Object %s\ncan not be used for clothes creation because\nit has %s.\n" % (ob.name, word)
        if err:
            msg +=  line2
            raise MHError(msg)
        else:
            print(msg)
            print("Fixed automatically")
    context.scene.objects.active = old
    return

#
#   checkSingleVertexGroups(clo, scn):
#

def checkSingleVertexGroups(clo, scn):
    for v in clo.data.vertices:
        n = 0
        for g in v.groups:
            #print("Key", g.group, g.weight)
            n += 1
        if n != 1:
            v.select = True
            for g in v.groups:
                for vg in clo.vertex_groups:
                    if vg.index == g.group:
                        print("  ", vg.name)
            raise MHError("Vertex %d in %s belongs to %d groups. Must be exactly one" % (v.index, clo.name, n))
    return


def writeFaces(clo, fp):
    fp.write("faces\n")
    meFaces = getFaces(clo.data)
    for f in meFaces:
        for v in f.vertices:
            fp.write(" %d" % (v+1))
        fp.write("\n")
    return

def writeVertexGroups(clo, fp):
    for vg in clo.vertex_groups:
        fp.write("weights %s\n" % vg.name)
        for v in clo.data.vertices:
            for g in v.groups:
                if g.group == vg.index and g.weight > 1e-4:
                    fp.write(" %d %.4g \n" % (v.index, g.weight))
    return

#
#    writePrio(data, prio, pad, fp):
#    writeDir(data, exclude, pad, fp):
#

def writePrio(data, prio, pad, fp):
    for ext in prio:
        writeExt(ext, data, [], pad, 0, fp)

def writeDir(data, exclude, pad, fp):
    for ext in dir(data):
        writeExt(ext, data, exclude, pad, 0, fp)

def writeQuoted(arg, fp):
    typ = type(arg)
    if typ == int or typ == float or typ == bool:
        fp.write("%s" % arg)
    elif typ == str:
        fp.write("'%s'"% stringQuote(arg))
    elif len(arg) > 1:
        c = '['
        for elt in arg:
            fp.write(c)
            writeQuoted(elt, fp)
            c = ','
        fp.write("]")
    else:
        raise MHError("Unknown property %s %s" % (arg, typ))
        fp.write('%s' % arg)

def stringQuote(string):
    s = ""
    for c in string:
        if c == '\\':
            s += "\\\\"
        elif c == '\"':
            s += "\\\""
        elif c == '\'':
            s += "\\\'"
        else:
            s += c
    return s


#
#    writeExt(ext, data, exclude, pad, depth, fp):
#

def writeExt(ext, data, exclude, pad, depth, fp):
    if hasattr(data, ext):
        writeValue(ext, getattr(data, ext), exclude, pad, depth, fp)

#
#    writeValue(ext, arg, exclude, pad, depth, fp):
#

excludeList = [
    'bl_rna', 'fake_user', 'id_data', 'rna_type', 'name', 'tag', 'users', 'type'
]

def writeValue(ext, arg, exclude, pad, depth, fp):
    if (len(str(arg)) == 0 or
        arg == None or
        arg == [] or
        ext[0] == '_' or
        ext in excludeList or
        ext in exclude):
        return

    if ext == 'end':
        print("RENAME end", arg)
        ext = '\\ end'

    typ = type(arg)
    if typ == int:
        fp.write("%s%s %d ;\n" % (pad, ext, arg))
    elif typ == float:
        fp.write("%s%s %.3f ;\n" % (pad, ext, arg))
    elif typ == bool:
        fp.write("%s%s %s ;\n" % (pad, ext, arg))
    elif typ == str:
        fp.write("%s%s '%s' ;\n" % (pad, ext, stringQuote(arg.replace(' ','_'))))
    elif typ == list:
        fp.write("%s%s List\n" % (pad, ext))
        n = 0
        for elt in arg:
            writeValue("[%d]" % n, elt, [], pad+"  ", depth+1, fp)
            n += 1
        fp.write("%send List\n" % pad)
    elif typ == Vector:
        c = '('
        fp.write("%s%s " % (pad, ext))
        for elt in arg:
            fp.write("%s%.3f" % (c,elt))
            c = ','
        fp.write(") ;\n")
    else:
        try:
            r = arg[0]
            g = arg[1]
            b = arg[2]
        except:
            return
        if (type(r) == float) and (type(g) == float) and (type(b) == float):
            fp.write("%s%s (%.4f,%.4f,%.4f) ;\n" % (pad, ext, r, g, b))
            print(ext, arg)
    return

###################################################################################
#
#   Boundary parts
#
###################################################################################

def examineBoundary(ob, scn):
    verts = ob.data.vertices
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    vnums = getBodyPartVerts(scn)
    for m,n in vnums:
        verts[m].select = True
        verts[n].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    return


def getBodyPartVerts(scn):
    if scn.MCBodyPart == 'Custom':
        return (
            (scn.MCCustomX1, scn.MCCustomX2),
            (scn.MCCustomY1, scn.MCCustomY2),
            (scn.MCCustomZ1, scn.MCCustomZ2)
            )
    else:
        return theSettings.bodyPartVerts[scn.MCBodyPart]

###################################################################################
#
#   Z depth
#
###################################################################################

#
#   getZDepthItems():
#   setZDepth(scn):
#

ZDepth = {
    "Body" : 0,
    "Underwear and lingerie" : 20,
    "Socks and stockings" : 30,
    "Shirt and trousers" : 40,
    "Sweater" : 50,
    "Indoor jacket" : 60,
    "Shoes and boots" : 70,
    "Coat" : 80,
    "Backpack" : 100,
    }

MinZDepth = 31
MaxZDepth = 69

def setZDepthItems():
    global ZDepthItems
    zlist = sorted(list(ZDepth.items()), key=lambda z: z[1])
    ZDepthItems = []
    for (name, val) in zlist:
        ZDepthItems.append((name,name,name))
    return

def setZDepth(scn):
    scn.MCZDepth = 50 + int((ZDepth[scn.MCZDepthName]-50)/2.6)
    return


###################################################################################
#
#   Utilities
#
###################################################################################
#
#    printVertNums(context):
#

def printVertNums(context):
    ob = context.object
    bpy.ops.object.mode_set(mode='OBJECT')
    print("Verts in ", ob)
    for v in ob.data.vertices:
        if v.select:
            print(v.index)
    print("End verts")
    bpy.ops.object.mode_set(mode='EDIT')

#
#   deleteHelpers(context):
#

def deleteHelpers(context):
    if theSettings is None:
        return
    ob = context.object
    scn = context.scene
    #if not ob.MhHuman:
    #    return
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    nmax = theSettings.vertices[scn.MCKeepVertsUntil][1]
    for v in ob.data.vertices:
        if v.index >= nmax:
            v.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')
    print("Vertices deleted")
    return

#
#   autoVertexGroups(ob):
#

def autoVertexGroupsIfNecessary(ob, type='Selected', htype='Tights'):
    if len(ob.vertex_groups) == 0:
        print("Found no vertex groups for %s." % ob)
        autoVertexGroups(ob, type, htype)


def autoVertexGroups(ob, type, htype):
    if ob.vertex_groups:
        bpy.ops.object.vertex_group_remove(all=True)

    mid = ob.vertex_groups.new("Mid")
    left = ob.vertex_groups.new("Left")
    right = ob.vertex_groups.new("Right")
    if isOkHuman(ob):
        ob.vertex_groups.new("Delete")
        verts = getHumanVerts(ob.data, type, htype)
    else:
        verts = ob.data.vertices
    for v in verts.values():
        vn = v.index
        if v.co[0] > 0.01:
            left.add([vn], 1.0, 'REPLACE')
        elif v.co[0] < -0.01:
            right.add([vn], 1.0, 'REPLACE')
        else:
            mid.add([vn], 1.0, 'REPLACE')
            if (ob.MhHuman and
                (theSettings is None or vn < theSettings.nTotalVerts)):
                left.add([vn], 1.0, 'REPLACE')
                right.add([vn], 1.0, 'REPLACE')
    if ob.MhHuman:
        print("Vertex groups auto assigned to human %s, part %s." % (ob, type.lower()))
    else:
        print("Vertex groups auto assigned to clothing %s" % ob)


def getHumanVerts(me, type, htype):
    if type == 'Selected':
        verts = {}
        for v in me.vertices:
            if v.select:
                verts[v.index] = v
    elif type == 'Helpers':
        verts = getHelperVerts(me, htype)
    elif type == 'Body':
        verts = {}
        addBodyVerts(me, verts)
    elif type == 'All':
        verts = getHelperVerts(me, 'All')
        addBodyVerts(me, verts)
    else:
        print(type, htype)
        halt
    return verts


def getHelperVerts(me, htype):
    verts = {}
    vnums = theSettings.vertices
    if htype == 'All':
        checkEnoughVerts(me, htype, theSettings.clothesVerts[0])
        for vn in range(theSettings.clothesVerts[0], theSettings.clothesVerts[1]):
            verts[vn] = me.vertices[vn]
    elif htype in vnums.keys():
        checkEnoughVerts(me, htype, vnums[htype][0])
        for vn in range(vnums[htype][0], vnums[htype][1]):
            verts[vn] = me.vertices[vn]
    elif htype == 'Coat':
        checkEnoughVerts(me, htype, vnums["Tights"][0])
        zmax = -1e6
        for vn in theSettings.topOfSkirt:
            zn = me.vertices[vn].co[2]
            if zn > zmax:
                zmax = zn
        for vn in range(vnums["Skirt"][0], vnums["Skirt"][1]):
            verts[vn] = me.vertices[vn]
        for vn in range(vnums["Tights"][0], vnums["Tights"][1]):
            zn = me.vertices[vn].co[2]
            if zn > zmax:
                verts[vn] = me.vertices[vn]
    else:
        raise MHError("Unknown helper type %s" % htype)

    return verts


def checkEnoughVerts(me, htype, first):
    if len(me.vertices) < first:
        raise MHError("Mesh has too few vertices for selecting %s" % (htype))


def addBodyVerts(me, verts):
    meFaces = getFaces(me)
    for f in meFaces:
        if len(f.vertices) < 4:
            continue
        for vn in f.vertices:
            if vn < theSettings.nBodyVerts:
                verts[vn] = me.vertices[vn]
    return


def selectHumanPart(ob, btype, htype):
    if isOkHuman(ob):
        clearSelection()
        verts = getHumanVerts(ob.data, btype, htype)
        for v in verts.values():
            v.select = True
        bpy.ops.object.mode_set(mode='EDIT')
    else:
        raise MHError("Object %s is not a human" % ob.name)


#
#   checkAndVertexDiamonds(context, ob):
#

def clearSelection():
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')


def checkAndUnVertexDiamonds(context, ob):
    print("Unvertex diamonds in %s" % ob)
    scn = context.scene
    bpy.ops.object.mode_set(mode='OBJECT')
    scn.objects.active = ob
    clearSelection()
    me = ob.data
    nverts = len(me.vertices)

    if not isOkHuman(ob):
        vertlines = ""
        for n in getLastVertices():
            vertlines += ("\n  %d" % n)
        raise MHError(
            "Base object %s has %d vertices. \n" % (ob, nverts) +
            "The number of verts in an %s MH human must be one of:" % theSettings.baseMesh +
            vertlines)

    joints = theSettings.vertices["Joints"]
    if nverts <= joints[0]:
        return
    for vn in range(joints[0], joints[1]):
        me.vertices[vn].select = True
    lastHair = theSettings.vertices["Hair"][1]
    if nverts > lastHair:
        for vn in range(lastHair, theSettings.nTotalVerts):
            me.vertices[vn].select = True

    bpy.ops.object.mode_set(mode='EDIT')
    for gn in range(len(ob.vertex_groups)):
        ob.vertex_groups.active_index = gn
        bpy.ops.object.vertex_group_remove_from()
    bpy.ops.object.mode_set(mode='OBJECT')
    return


#
#   readDefaultSettings(context):
#   saveDefaultSettings(context):
#

def settingsFile(name):
    outdir = os.path.join(getMHBlenderDirectory(), "settings")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    return os.path.join(outdir, "make_clothes.%s" % name)


def readDefaultSettings(context):
    fname = settingsFile("settings")
    try:
        fp = open(fname, "rU")
    except FileNotFoundError:
        print("Did not find %s. Using default settings" % fname)
        return

    scn = context.scene
    for line in fp:
        words = line.split()
        if len(words) < 3:
            continue
        prop = words[0]
        type = words[1]
        if type == "int":
            scn[prop] = int(words[2])
        elif type == "float":
            scn[prop] = float(words[2])
        elif type == "str":
            string = words[2]
            for word in words[3:]:
                string += " " + word
            scn[prop] = string
    fp.close()
    return


def saveDefaultSettings(context):
    fname = settingsFile("settings")
    fp = mc.openOutputFile(fname)
    scn = context.scene
    for (prop, value) in scn.items():
        if prop[0:2] == "MC":
            if type(value) == int:
                fp.write("%s int %s\n" % (prop, value))
            elif type(value) == float:
                fp.write("%s float %.4f\n" % (prop, value))
            elif type(value) == str:
                fp.write("%s str %s\n" % (prop, value))
    fp.close()
    return

#
#   BMesh
#


def getFaces(me):
    global BMeshAware
    try:
        BMeshAware = True
        return me.polygons
    except:
        BMeshAware = False
        return me.faces

#
#   init():
#

MCIsInited = False

def init():
    global MCIsInited
    import maketarget
    if not maketarget.maketarget.MTIsInited:
        maketarget.maketarget.init()

    for skey in theShapeKeys:
        prop = BoolProperty(
            name = skey,
            description = "Shapekey %s affects clothes" % skey,
            default = False)
        setattr(bpy.types.Scene, 'MC%s' % skey, prop)

    bpy.types.Scene.MCBodyType = EnumProperty(
        items = [('None', 'Base Mesh', 'None'),
                 ('caucasian-male-young', 'Average Male', 'caucasian-male-young'),
                 ('caucasian-female-young', 'Average Female', 'caucasian-female-young'),
                 ('caucasian-male-child', 'Average Child', 'caucasian-male-child'),
                 ('caucasian-male-baby', 'Average Baby', 'caucasian-male-baby'),

                 ('h-None', 'Base Mesh  With Helpers', 'None'),
                 ('h-caucasian-male-young', 'Average Male With Helpers', 'caucasian-male-young'),
                 ('h-caucasian-female-young', 'Average Female With Helpers', 'caucasian-female-young'),
                 ('h-caucasian-male-child', 'Average Child With Helpers', 'caucasian-male-child'),
                 ('h-caucasian-male-baby', 'Average Baby With Helpers', 'caucasian-male-baby'),
                 ],
        description = "Body Type To Load",
    default='None')

    bpy.types.Scene.MCMaterials = BoolProperty(
        name="Materials",
        description="Use materials",
        default=False)

    bpy.types.Scene.MCMaskLayer = IntProperty(
        name="Mask UV layer",
        description="UV layer for mask, starting with 0",
        default=0)

    bpy.types.Scene.MCTextureLayer = IntProperty(
        name="Texture UV layer",
        description="UV layer for textures, starting with 0",
        default=0)

    bpy.types.Scene.MCAllUVLayers = BoolProperty(
        name="All UV layers",
        description="Include all UV layers in export",
        default=False)

    bpy.types.Scene.MCThreshold = FloatProperty(
        name="Threshold",
        description="Minimal allowed value of normal-vector dot product",
        min=-1.0, max=0.0,
        default=-0.2)

    bpy.types.Scene.MCListLength = IntProperty(
        name="List length",
        description="Max number of verts considered",
        default=4)

    bpy.types.Scene.MCUseInternal = BoolProperty(
        name="Use Internal",
        description="Access internal settings",
        default=False)

    bpy.types.Scene.MCLogging = BoolProperty(
        name="Log",
        description="Write a log file for debugging",
        default=False)

    bpy.types.Scene.MCMHVersion = EnumProperty(
        items = [("hm08", "hm08", "hm08"), ("None", "None", "None")],
        name="MakeHuman mesh version",
        description="The human is the MakeHuman base mesh",
        default="hm08")

    bpy.types.Scene.MCSelfClothed = BoolProperty(default=False)

    enums = []
    for name in theSettings.vertices.keys():
        enums.append((name,name,name))

    bpy.types.Scene.MCKeepVertsUntil = EnumProperty(
        items = enums,
        name="Keep verts untils",
        description="Last clothing to keep vertices for",
        default="Tights")

    bpy.types.Scene.MCScaleUniform = BoolProperty(
        name="Uniform Scaling",
        description="Scale offset uniformly in the XYZ directions",
        default=False)

    bpy.types.Scene.MCScaleCorrect = FloatProperty(
        name="Scale Correction",
        default=1.0,
        min=0.5, max=1.5)

    bpy.types.Scene.MCBodyPart = EnumProperty(
        name = "Body Part",
        items = [('Head', 'Head', 'Head'),
                 ('Torso', 'Torso', 'Torso'),
                 ('Arm', 'Arm', 'Arm'),
                 ('Hand', 'Hand', 'Hand'),
                 ('Leg', 'Leg', 'Leg'),
                 ('Foot', 'Foot', 'Foot'),
                 ('Eye', 'Eye', 'Eye'),
                 ('Genital', 'Genital', 'Genital'),
                 ('Body', 'Body', 'Body'),
                 ('Custom', 'Custom', 'Custom'),
                 ],
        default='Head')

    x,y,z = theSettings.bodyPartVerts['Body']

    bpy.types.Scene.MCCustomX1 = IntProperty(name="X1", default=x[0])
    bpy.types.Scene.MCCustomX2 = IntProperty(name="X2", default=x[1])
    bpy.types.Scene.MCCustomY1 = IntProperty(name="Y1", default=y[0])
    bpy.types.Scene.MCCustomY2 = IntProperty(name="Y2", default=y[1])
    bpy.types.Scene.MCCustomZ1 = IntProperty(name="Z1", default=z[0])
    bpy.types.Scene.MCCustomZ2 = IntProperty(name="Z2", default=z[1])

    setZDepthItems()
    bpy.types.Scene.MCZDepthName = EnumProperty(
        name = "Clothes Type",
        items = ZDepthItems,
        default='Sweater')

    bpy.types.Scene.MCZDepth = IntProperty(
        name="Z depth",
        description="Location in the Z buffer",
        default=ZDepth['Sweater'],
        min = MinZDepth,
        max = MaxZDepth)

    bpy.types.Scene.MCAuthor = StringProperty(
        name="Author",
        default="Unknown",
        maxlen=32)

    bpy.types.Scene.MCLicense = StringProperty(
        name="License",
        default="AGPL3 (see also http://www.makehuman.org/node/320)",
        maxlen=256)

    bpy.types.Scene.MCHomePage = StringProperty(
        name="HomePage",
        default="http://www.makehuman.org/",
        maxlen=256)

    bpy.types.Scene.MCTag1 = StringProperty(
        name="Tag1",
        default="",
        maxlen=32)

    bpy.types.Scene.MCTag2 = StringProperty(
        name="Tag2",
        default="",
        maxlen=32)

    bpy.types.Scene.MCTag3 = StringProperty(
        name="Tag3",
        default="",
        maxlen=32)

    bpy.types.Scene.MCTag4 = StringProperty(
        name="Tag4",
        default="",
        maxlen=32)

    bpy.types.Scene.MCTag5 = StringProperty(
        name="Tag5",
        default="",
        maxlen=32)

    bpy.types.Scene.MCShowSettings = BoolProperty(name = "Show Settings", default=False)
    bpy.types.Scene.MCShowUtils = BoolProperty(name = "Show Utilities", default=False)
    bpy.types.Scene.MCShowSelect = BoolProperty(name = "Show Selection", default=False)
    bpy.types.Scene.MCShowMaterials = BoolProperty(name = "Show Materials", default=False)
    bpy.types.Scene.MCShowAdvanced = BoolProperty(name = "Show Advanced", default=False)
    bpy.types.Scene.MCShowUVProject = BoolProperty(name = "Show UV Projection", default=False)
    bpy.types.Scene.MCShowZDepth = BoolProperty(name = "Show Z-Depth (%d-%d range)" % (MinZDepth, MaxZDepth), default=False)
    bpy.types.Scene.MCShowBoundary = BoolProperty(name = "Show Offset Scaling", default=False)
    bpy.types.Scene.MCShowLicense = BoolProperty(name = "Show License", default=False)

    MCIsInited = True

