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
Fbx mesh
"""

import math
import numpy as np
import numpy.linalg as la
import transformations as tm

from .fbx_utils import *

#--------------------------------------------------------------------
#   Object definitions
#--------------------------------------------------------------------

def getObjectCounts(rmeshes):
    nVertexGroups = 0
    for rmesh in rmeshes:
        for weights in rmesh.weights:
            if weights:
                nVertexGroups += 1

    nShapes = 0
    for rmesh in rmeshes:
        for key,shape in rmesh.shapes:
            if shape:
                nShapes += 1

    return nVertexGroups, nShapes

def countObjects(rmeshes, amt):
    nVertexGroups, nShapes = getObjectCounts(rmeshes)
    if amt:
        return (nVertexGroups + 1 + 2*nShapes)
    else:
        return 2*nShapes


def writeObjectDefs(fp, rmeshes, amt):
    nVertexGroups, nShapes = getObjectCounts(rmeshes)

    if amt:
        fp.write(
'    ObjectType: "Deformer" {\n' +
'       Count: %d' % (nVertexGroups + 1 + 2*nShapes) +
"""
    }

    ObjectType: "Pose" {
        Count: 1
    }
""")

    else:
        fp.write(
'    ObjectType: "Deformer" {\n' +
'       Count: %d' % (2*nShapes) +
"""
}
""")


#--------------------------------------------------------------------
#   Object properties
#--------------------------------------------------------------------

def writeObjectProps(fp, rmeshes, amt, config):
    if amt:
        writeBindPose(fp, rmeshes, amt, config)

        for rmesh in rmeshes:
            name = getRmeshName(rmesh, amt)
            writeDeformer(fp, name)
            for bone in amt.bones.values():
                try:
                    weights = rmesh.weights[bone.name]
                except KeyError:
                    continue
                writeSubDeformer(fp, name, bone, weights, config)

    for rmesh in rmeshes:
        name = getRmeshName(rmesh, amt)
        if rmesh.shapes:
            for sname,shape in rmesh.shapes:
                writeShapeGeometry(fp, name, sname, shape, config)
                writeShapeDeformer(fp, name, sname)
                writeShapeSubDeformer(fp, name, sname, shape)


def writeShapeGeometry(fp, name, sname, shape, config):
        id,key = getId("Geometry::%s_%sShape" % (name, sname))
        nVerts = len(shape.verts)
        fp.write(
'    Geometry: %d, "%s", "Shape" {\n' % (id, key) +
'        version: 100\n' +
'        Indexes: *%d   {\n' % nVerts +
'            a: ')

        string = "".join( ['%d,' % vn for vn in shape.verts] )
        fp.write(string[:-1])

        fp.write('\n' +
'        }\n' +
'        Vertices: *%d   {\n' % (3*nVerts) +
'            a: ')

        string = "".join( ["%.4f,%.4f,%.4f," % tuple(dr) for dr in shape.data] )
        fp.write(string[:-1])

        # Must use normals for shapekeys
        fp.write('\n' +
'        }\n' +
'        Normals: *%d {\n' % (3*nVerts) +
'            a: ')

        string = nVerts * "0,0,0,"
        fp.write(string[:-1])

        fp.write('\n' +
'        }\n' +
'    }\n')


def writeShapeDeformer(fp, name, sname):
    id,key = getId("Deformer::%s_%sShape" % (name, sname))
    fp.write(
'    Deformer: %d, "%s", "BlendShape" {\n' % (id, key) +
'        Version: 100\n' +
'    }\n')


def writeShapeSubDeformer(fp, name, sname, shape):
    sid,skey = getId("SubDeformer::%s_%sShape" % (name, sname))
    fp.write(
'    Deformer: %d, "%s", "BlendShapeChannel" {' % (sid, skey) +
"""
        version: 100
        deformpercent: 0.0
        FullWeights: *1   {
            a: 100
        }
    }
""")


def writeDeformer(fp, name):
    id,key = getId("Deformer::%s" % name)

    fp.write(
'    Deformer: %d, "%s", "Skin" {' % (id, key) +
"""
        Version: 101
        Properties70:  {
""" +
'            P: "MHName", "KString", "", "", "%sSkin"' % name +
"""
        }
        Link_DeformAcuracy: 50
    }
""")


def writeSubDeformer(fp, name, bone, weights, config):
    nVertexWeights = len(weights)
    id,key = getId("SubDeformer::%s_%s" % (bone.name, name))

    fp.write(
'    Deformer: %d, "%s", "Cluster" {\n' % (id, key) +
'        Version: 100\n' +
'        UserData: "", ""\n' +
'        Indexes: *%d {\n' % nVertexWeights +
'            a: ')

    last = nVertexWeights - 1
    for n,data in enumerate(weights):
        vn,w = data
        fp.write(str(vn))
        writeComma(fp, n, last)

    fp.write(
'        } \n' +
'        Weights: *%d {\n' % nVertexWeights +
'            a: ')

    for n,data in enumerate(weights):
        vn,w = data
        fp.write(str(w))
        writeComma(fp, n, last)

    bindmat,bindinv = bone.getBindMatrix(config)
    fp.write('        }\n')
    writeMatrix(fp, 'Transform', bindmat)
    writeMatrix(fp, 'TransformLink', bindinv)
    fp.write('    }\n')


def writeBindPose(fp, rmeshes, amt, config):
    id,key = getId("Pose::" + amt.name)
    nBones = len(amt.bones)
    nMeshes = len(rmeshes)

    fp.write(
'    Pose: %d, "%s", "BindPose" {\n' % (id, key)+
'        Type: "BindPose"\n' +
'        Version: 100\n' +
'        NbPoseNodes: %d\n' % (1+nMeshes+nBones))

    startLinking()
    amtbindmat = amt.getBindMatrix(config)
    poseNode(fp, "Model::%s" % amt.name, amtbindmat)

    for rmesh in rmeshes:
        name = getRmeshName(rmesh, amt)
        poseNode(fp, "Model::%sMesh" % name, amtbindmat)

    for bone in amt.bones.values():
        bindmat,_ = bone.getBindMatrix(config)
        poseNode(fp, "Model::%s" % bone.name, bindmat)

    stopLinking()
    fp.write('    }\n')


def poseNode(fp, key, matrix):
    pid,_ = getId(key)
    matrix[:3,3] = 0
    fp.write(
'        PoseNode:  {\n' +
'            Node: %d\n' % pid)
    writeMatrix(fp, 'Matrix', matrix, "    ")
    fp.write('        }\n')

#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def writeLinks(fp, rmeshes, amt):

    if amt:
        for rmesh in rmeshes:
            name = getRmeshName(rmesh, amt)

            ooLink(fp, 'Deformer::%s' % name, 'Geometry::%s' % name)
            for bone in amt.bones.values():
                subdef = 'SubDeformer::%s_%s' % (bone.name, name)
                try:
                    getId(subdef)
                except NameError:
                    continue
                ooLink(fp, subdef, 'Deformer::%s' % name)
                ooLink(fp, 'Model::%s' % bone.name, subdef)

    for rmesh in rmeshes:
        if rmesh.shapes:
            name = getRmeshName(rmesh, amt)
            for sname, shape in rmesh.shapes:
                deform = "Deformer::%s_%sShape" % (name, sname)
                subdef = "SubDeformer::%s_%sShape" % (name, sname)
                ooLink(fp, "Geometry::%s_%sShape" % (name, sname), subdef)
                ooLink(fp, subdef, deform)
                ooLink(fp, deform, "Geometry::%s" % name)


