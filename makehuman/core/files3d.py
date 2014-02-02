#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Modules to handle supported 3D file formats. 

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Manuel Bastioni, Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

.. image:: ../images/files_data.png
   :align: right   
   
This Module handles the 3D file formats supported by MakeHuman. It is planned that this module 
will implement a range of functions to handle most common 3D file formats in the future. 
The functions within this module should all follow a standard pattern
designed to facilitate the implementation of new interfaces.

This module will include functions to:
   
  - Transpose imported 3D data into a standard internal format for 
    each of the 3D file formats supported by the MakeHuman import 
    functions.
  - Generate 3D data structures that correspond to 3D file formats 
    supported by the makeHuman export function.
  - Provide generic transformation utilities such as the 
    dataTo3Dobject() function which takes an object defined 
    in the standard internal format and makes it visible to the user.  

The image on the right shows the general schema for implementing new MakeHuman importers. 
The wavefrontToData_simple() function below can be used as a template for developing 
new functions. 

Each importer function must return the 3d data in a standard format 
(a list [verts,vertsSharedFaces,vertsUV,faceGroups,faceGroupsNames] ).
The dataTo3Dobject() function can then be used to convert it into an object that 
is visible to the user through the GUI.
"""

import os.path
import module3d
import numpy as np
import log
import wavefront
from getpath import isSubPath, getPath

def packStringList(strings):
    text = ''
    index = []
    for string in strings:
        index.append(len(text))
        text += string
    text = np.fromstring(text, dtype='S1')
    index = np.array(index, dtype=np.uint32)
    return text, index

def unpackStringList(text, index):
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

def saveBinaryMesh(obj, path):
    fgstr, fgidx = packStringList(fg.name for fg in obj._faceGroups)

    vars_ = dict(
        coord = obj.coord,
        vface = obj.vface,
        nfaces = obj.nfaces,
        texco = obj.texco,
        fvert = obj.fvert,
        group = obj.group,
        fgstr = fgstr,
        fgidx = fgidx)

    if obj.has_uv:
        vars_['fuvs']  = obj.fuvs

    np.savez(path, **vars_)

def loadBinaryMesh(obj, path):
    log.debug("Loading binary mesh %s.", path)
    #log.debug('loadBinaryMesh: np.load()')

    npzfile = np.load(path)

    #log.debug('loadBinaryMesh: loading arrays')
    coord = npzfile['coord']
    obj.setCoords(coord)

    texco = npzfile['texco']
    obj.setUVs(texco)

    fvert = npzfile['fvert']
    fuvs = npzfile['fuvs'] if 'fuvs' in npzfile.files else None
    group = npzfile['group']
    obj.setFaces(fvert, fuvs, group, skipUpdate=True)

    obj.vface[:,:] = npzfile['vface'][:,:obj.MAX_FACES]
    obj.nfaces = npzfile['nfaces']

    #log.debug('loadBinaryMesh: loaded arrays')

    fgstr = npzfile['fgstr']
    fgidx = npzfile['fgidx']
    for name in unpackStringList(fgstr, fgidx):
        obj.createFaceGroup(name)
    del fgstr, fgidx

    #log.debug('loadBinaryMesh: unpacked facegroups')

    obj.calcNormals()
    #log.debug('loadBinaryMesh: calculated normals')

    obj.updateIndexBuffer()
    #log.debug('loadBinaryMesh: built index buffer for rendering')

def loadTextMesh(obj, path):
    """
    Parse and load a Wavefront OBJ file as mesh.
    """
    log.debug("Loading ASCII mesh %s.", path)
    #log.debug('loadTextMesh: begin')
    wavefront.loadObjFile(path, obj)
    #log.debug('loadTextMesh: end')

def loadMesh(path, locX=0, locY=0, locZ=0, loadColors=1, maxFaces=None):
    """
    This function loads the specified mesh object into internal MakeHuman data 
    structures, and returns it. The loaded file should be in Wavefront OBJ 
    format.
    
    Parameters:
    -----------
   
    path:     
      *String*.  The file system path to the file containing the object to load.

    locX:
      *float* X location of loaded obj, default = 0

    locY:
      *float* Y location of loaded obj, default = 0

    locZ:
      *float* Z location of loaded obj, default = 0

    Note: loadColors is currently unused

    maxFaces:
      *uint* Number of faces per vertex (pole), None for default (min 4)
    """
    name = os.path.basename(path)
    obj = module3d.Object3D(name)
    if maxFaces:
        obj.MAX_FACES = maxFaces

    obj.path = path
    obj.x = locX
    obj.y = locY
    obj.z = locZ

    try:
        npzpath = os.path.splitext(path)[0] + '.npz'
        try:
            if not os.path.isfile(npzpath):
                log.message('compiled file missing: %s', npzpath)
                raise RuntimeError()
            if os.path.isfile(path) and os.path.getmtime(path) > os.path.getmtime(npzpath):
                log.message('compiled file out of date: %s', npzpath)
                raise RuntimeError()
            loadBinaryMesh(obj, npzpath)
        except:
            loadTextMesh(obj, path)
            if isSubPath(npzpath, getPath('')):
                # Only write compiled binary meshes to user data path
                try:
                    saveBinaryMesh(obj, npzpath)
                except StandardError:
                    log.notice('unable to save compiled mesh: %s', npzpath)
            else:
                log.debug('Not writing compiled meshes to system paths (%s).', npzpath)
    except:
        log.error('Unable to load obj file: %s', path, exc_info=True)
        return False

    return obj
