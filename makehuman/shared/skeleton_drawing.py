#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Functions for transforming a skeleton into a 3D object for visualizing.
"""

import module3d
import numpy as np

SHAPE_VECTORS = {
'Prism': [
    np.array((0, 0, 0, 0)),
    np.array((0.14, 0.25, 0, 0)),
    np.array((0, 0.25, 0.14, 0)),
    np.array((-0.14, 0.25, 0, 0)),
    np.array((0, 0.25, -0.14, 0)),
    np.array((0, 1, 0, 0)),
],
'Box' : [
    np.array((-0.10, 0, -0.10, 0)), 
    np.array((-0.10, 0, 0.10, 0)),
    np.array((-0.10, 1, -0.10, 0)),
    np.array((-0.10, 1, 0.10, 0)),
    np.array((0.10, 0, -0.10, 0)),
    np.array((0.10, 0, 0.10, 0)),
    np.array((0.10, 1, -0.10, 0)),
    np.array((0.10, 1, 0.10, 0)),
],
'Cube' : [
    np.array((-1, 0, -1, 0)), 
    np.array((-1, 0, 1, 0)),
    np.array((-1, 1, -1, 0)),
    np.array((-1, 1, 1, 0)),
    np.array((1, 0, -1, 0)),
    np.array((1, 0, 1, 0)),
    np.array((1, 1, -1, 0)),
    np.array((1, 1, 1, 0)),
],
'Line' : [    
    np.array((-0.03, 0, -0.03, 0)),
    np.array((-0.03, 0, 0.03, 0)),
    np.array((-0.03, 1, -0.03, 0)),
    np.array((-0.03, 1, 0.03, 0)),
    np.array((0.03, 0, -0.03, 0)),
    np.array((0.03, 0, 0.03, 0)),
    np.array((0.03, 1, -0.03, 0)),
    np.array((0.03, 1, 0.03, 0)),
]
}

SHAPE_FACES = {
'Prism': [ (0,1,4,0), (0,4,3,0), (0,3,2,0), (0,2,1,0),
           (5,4,1,5), (5,1,2,5), (5,2,3,5), (5,3,4,5) ],
'Box' : [ (0,1,3,2), (4,6,7,5), (0,2,6,4), 
           (1,5,7,3), (1,0,4,5), (2,3,7,6) ],
'Line' : [ (0,1,3,2), (4,6,7,5), (0,2,6,4), 
           (1,5,7,3), (1,0,4,5), (2,3,7,6) ],
}                   

HEAD_VEC = np.array((0,0,0,1))


def meshFromSkeleton(skel, type="Prism"):
    verts, faces, vertsPerBone, facesPerBone, boneNames = _shapeFromSkeleton(skel, type)

    mesh = module3d.Object3D("SkeletonMesh")
    mesh.boneShape = type   # Append a custom attribute to skeleton meshes

    fgroups = np.zeros(len(faces), dtype=np.uint16)
    for bIdx, boneName in enumerate(boneNames):
        fg = mesh.createFaceGroup(boneName)
        offset = bIdx*facesPerBone
        fgroups[offset:offset+facesPerBone] = np.repeat(np.array(fg.idx, dtype=np.uint16), facesPerBone)

    mesh.setCoords(verts)
    mesh.setUVs(np.zeros((1, 2), dtype=np.float32)) # Set trivial UV coordinates
    mesh.setFaces(faces, None, fgroups)
    
    mesh.updateIndexBuffer()
    mesh.calcNormals()
    mesh.update()

    mesh.setCameraProjection(0)
    mesh.setShadeless(0)
    mesh.setSolid(0)
    mesh.priority = 30

    return mesh

def getVertBoneMapping(skel, skeletonMesh):
    vertBoneMapping = {}    # Format: { boneName: (vertIdxs, weights) }
    if not hasattr(skeletonMesh, "boneShape"):
        raise RuntimeError("Specified mesh object %s is not a skeleton mesh. Make sure it is created using meshFromSkeleton()" % skeletonMesh)
    type = skeletonMesh.boneShape
    nVertsPerBone = len(SHAPE_VECTORS[type])

    #nBones = len(skel.getBones())
    #nVertsPerBone = int(mesh.getVertexCount()/nBones)

    offset = 0
    for bone in skel.getBones():    # We assume that skeleton mesh has bones in breadt-first order
        verts = range(offset, offset + nVertsPerBone)
        weights = np.repeat(1, nVertsPerBone)
        vertBoneMapping[bone.name] = (verts, weights)
        offset = offset + nVertsPerBone
    return vertBoneMapping

def updateSkeletonMeshPose(skeletonMesh, skeleton):
# TODO do we need this method when we can simply construct a skeleton mesh from rest pose and then skin it with rigid weights (method above)?
    if not hasattr(skeletonMesh, "boneShape"):
        raise RuntimeError("Specified mesh object %s is not a skeleton mesh. Make sure it is created using meshFromSkeleton()" % skeletonMesh)
    type = skeletonMesh.boneShape

    coords = np.zeros((skeletonMesh.getVertexCount(),3), dtype=np.float32)

    # TODO add method to skeleton to get numpy array of all mats in breadth first order? try to reduce python loops
    for bIdx, bone in enumerate(skeleton.getBones()):
        mat = bone.matPoseGlobal
        length = bone.yvector4[1]

        nVec = len(SHAPE_VECTORS)
        for i, vec in enumerate(SHAPE_VECTORS[type]):    # TODO avoid for loop with numpy
            p = np.dot(mat, (vec*length + HEAD_VEC))
            coords[bIdx*nVec +i] = p[:3]

    # TODO maybe update only the bones that changed position for performance
    skeletonMesh.changeCoords(coords)
    skeletonMesh.calcNormals()
    skeletonMesh.update()

def _shapeFromSkeleton(skel, type="Prism"):
    """
    For updating the mesh we assume that bones are always retrieved from skeleton in the same
    order. After modifying a skeleton's structure (bones) a new mesh should be
    constructed with this method before it can be updated.
    """
    vertCount = 0
    faceCount = 0
    verts = None
    faces = None
    bones = skel.getBones()
    boneNames = []

    for bone in bones:
        v, f = _shapeFromBone(bone, type)
        if verts == None:
            verts = np.zeros((len(v)*len(bones), 3), np.float32)
            faces = np.zeros((len(f)*len(bones), 4), np.uint16)
        verts[vertCount:vertCount+len(v)] = v              # verts.extend(v)
        faces[faceCount:faceCount+len(f)] = f + vertCount  # faces.extend(f)
        vertCount = vertCount + len(v)
        faceCount = faceCount + len(f)
        boneNames.append(bone.name)

    return verts, faces, len(v), len(f), boneNames

def _shapeFromBone(bone, type="Prism"):
    """
    allowed types Prism, Box, Cube, Line
    Returns vertices and face indices to be used for building a 3d mesh of the
    the skeleton.
    """
    mat = bone.matPoseGlobal
    length = bone.getLength()

    # TODO optimise with numpy?
    points = np.zeros((len(SHAPE_VECTORS[type]), 3), dtype=np.float32)
    for vIdx, vec in enumerate(SHAPE_VECTORS[type]):
        p = np.dot(mat, (vec*length + HEAD_VEC))
        points[vIdx] = p[:3]

    return points, np.asarray(SHAPE_FACES[type], dtype=np.uint16)

DIAMOND_SHAPE_VECTORS = [
    np.array((0, -0.14, 0, 0)),
    np.array((0.14, 0, 0, 0)),
    np.array((0, 0, 0.14, 0)),
    np.array((-0.14, 0, 0, 0)),
    np.array((0, 0, -0.14, 0)),
    np.array((0, 0.14, 0, 0)),
]

def meshFromJoints(jointPositions, jointNames=None, scale = 1.0):
    """
    Create a mesh to visualize joints locations as diamonds.
    jointPositions should be a (n,3) numpy array.
    jointNames, if specified, should be a list of same length as jointPositions.
    jointNames should contain a set of strings describing the name of each joint.
    If jointNames is specified, the mesh will contain facegroups with those names.
    """
    vLen = len(DIAMOND_SHAPE_VECTORS)
    coords = np.zeros((len(jointPositions)*vLen,3), dtype=np.float32)
    shape = np.asarray(DIAMOND_SHAPE_VECTORS, dtype=np.float32)
    for jIdx, pos in enumerate(jointPositions):
        offset = jIdx*vLen
        coords[offset:offset+vLen] = shape[:,:3] + pos

    f = np.asarray(SHAPE_FACES["Prism"], dtype=np.uint16)
    fLen = len(SHAPE_FACES["Prism"])
    faces = np.zeros((fLen*len(jointPositions),4), dtype=np.uint16)

    for jIdx in range(len(jointPositions)):
        offset = jIdx*fLen
        faces[offset:offset+fLen] = f[:]+(jIdx*vLen)

    mesh = module3d.Object3D("jointsMesh")
    fgroups = None

    if jointNames != None:
        fgroups = np.zeros(len(faces), dtype=np.uint16)
        for jIdx, jointName in enumerate(jointNames):
            fg = mesh.createFaceGroup(jointName)
            offset = jIdx*fLen
            fgroups[offset:offset+fLen] = fg.idx

    mesh.setCoords(coords)
    mesh.setUVs(np.zeros((1, 2), dtype=np.float32)) # Set trivial UV coordinates
    mesh.setFaces(faces, None, fgroups)
    
    mesh.updateIndexBuffer()
    mesh.calcNormals()
    mesh.update()

    mesh.setCameraProjection(0)
    mesh.setShadeless(0)
    mesh.setSolid(0)
    mesh.priority = 30

    return mesh

