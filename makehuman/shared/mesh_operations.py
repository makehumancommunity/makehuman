#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Mesh operations such as calculating volume and surface measures.
"""

import numpy as np
import math

def calculateSurface(mesh, vertGroups = None, faceMask = None):
    """
    Calculate surface area of a mesh. Specify vertGroups or faceMask to
    calculate area of a subset of the mesh and filter out other faces.
    """
    if vertGroups != None:
        fvert = mesh.getFacesForGroups(vertGroups)
    elif faceMask != None:
        f_idx = np.argwhere(faceMask)[...,0]
        fvert = mesh.fvert[f_idx]
    else:
        fvert = mesh.fvert

    if mesh.vertsPerPrimitive == 4:
        # Split quads in triangles (assumes clockwise ordering of verts)
        t1 = fvert[:,[0,1,2]]
        t2 = fvert[:,[2,3,0]]
        v1 = mesh.coord[t1]
        v2 = mesh.coord[t2]

        l1 = _sideLengthsFromTris(v1)
        l2 = _sideLengthsFromTris(v2)
        l = np.vstack([l1,l2])

        return _surfaceOfTris(l)
    elif mesh.vertsPerPrimitive == 3:
        v = mesh.coord[fvert]
        l = _sideLengthsFromTris(v)
        return _surfaceOfTris(l)
    else:
        raise RuntimeError("Only supports meshes with triangle or quad primitives.")

def calculateVolume(mesh, vertGroups = None, faceMask = None):
    """
    Calculate the volume of a mesh.
    Mesh is expected to be closed.
    """
    if vertGroups != None:
        fvert = mesh.getFacesForGroups(vertGroups)
    elif faceMask != None:
        f_idx = np.argwhere(faceMask)[...,0]
        fvert = mesh.fvert[f_idx]
    else:
        fvert = mesh.fvert

    if mesh.vertsPerPrimitive == 4:
        # Split quads in triangles (assumes clockwise ordering of verts)
        t1 = fvert[:,[0,1,2]]
        t2 = fvert[:,[2,3,0]]
        v1 = mesh.coord[t1]
        v2 = mesh.coord[t2]

        v = np.vstack([v1,v2])
        return _signedVolumeFromTris(v)
    elif mesh.vertsPerPrimitive == 3:
        v = mesh.coord[fvert]
        return _signedVolumeFromTris(v)
    else:
        raise RuntimeError("Only supports meshes with triangle or quad primitives.")

def _sideLengthsFromTris(triVects):
    """
    Calculate lengths of the sides of triangles specified by their vectors
    in clockwise fashion.
    triVects = [ [T1V1, T1V2, T1V3], [T2V1, T2V2, T2V3], ... ]
    with Ti a triangle, Vi a triange vector, defined in clockwise fashion
    and each vector (TiVi) an array [x, y, z] with vector coordinates

    Returns a list [ [T1L1, T1L2, T1L3], [T2L1, T2L2, T2L3], ...]
    with Ti a triangle (in the same order as in the input), and Li the length of
    side i (a float)
    """
    v = triVects
    s = np.zeros(v.shape, dtype=np.float32)

    # Get side vectors
    s[:,0] = v[:,1] - v[:,0]
    s[:,1] = v[:,2] - v[:,1]
    s[:,2] = v[:,0] - v[:,2]

    # Calculate lengths of sides
    l = s[:,:,0]*s[:,:,0] + s[:,:,1]*s[:,:,1] + s[:,:,2]*s[:,:,2]
    l = np.sqrt(l)

    return l

def _surfaceOfTris(triSideLengths):
    """
    Calculate total surface area of triangles with sides of specified lengths
    triSideLengths should be an array of layout 
    [ [T1L1, T1L2, T1L3], [T2L1, T2L2, T2L3], ... ]
    with Ti a triangle, and Li the length of the ith side of the triangle
    TiLi should be a float.

    Returns a float representing the total surface area.
    """
    l = triSideLengths

    # Heron's formula
    o = ( l[:,0]  +l[:,1]  +l[:,2]) * \
        ( l[:,0]  +l[:,1]  -l[:,2]) * \
        (-l[:,0]  +l[:,1]  +l[:,2]) * \
        ( l[:,0]  -l[:,1]  +l[:,2])
    o = np.sqrt(o)/4

    return np.sum(o)

def _signedVolumeFromTris(triVects):
    """
    Calculate volume of a set of triangles by summing signed volumes of 
    tetrahedrons between those triangles and the origin.
    """
    v = triVects

    v321 = v[:,2,0] * v[:,1,1] * v[:,0,2]
    v231 = v[:,1,0] * v[:,2,1] * v[:,0,2]
    v312 = v[:,2,0] * v[:,0,1] * v[:,1,2]
    v132 = v[:,0,0] * v[:,2,1] * v[:,1,2]
    v213 = v[:,1,0] * v[:,0,1] * v[:,2,2]
    v123 = v[:,0,0] * v[:,1,1] * v[:,2,2]
    signedVolume = -v321 + v231 + v312 - v132 - v213 + v123
    signedVolume /= 6.0

    vol = np.sum(signedVolume)
    return math.fabs(vol)

def findVertIndex(mesh, vert):
    """
    Find the index of specified vertex (as an [x, y, z] array) within mesh.
    """
    matches = list(np.where(mesh.coord == vert)[0])
    return [idx for idx in set(matches) if matches.count(idx) > 2]

