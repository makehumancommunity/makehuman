#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier, Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Standalone script to compile all obj mesh files into binary npz files for faster
loading.
"""

import sys
sys.path = ["./core", "./lib", "./shared"] + sys.path
import os
import fnmatch
import module3d
import files3d
from getpath import isSubPath

def getAllFiles(rootPath, filterStrArr):
    result = [ None ]*len(filterStrArr)
    for root, dirnames, filenames in os.walk(rootPath):
        for i, filterStr in enumerate(filterStrArr):
            if not result[i]:
                result[i] = []
            result[i].extend(getFiles(root, filenames, filterStr))
    return result

def getFiles(root, filenames, filterStr):
    foundFiles = []
    for filename in fnmatch.filter(filenames, filterStr):
        foundFiles.append(os.path.join(root, filename))
    return foundFiles


def compileMesh(path):
    name = os.path.basename(path)
    obj = module3d.Object3D(name)

    obj.path = path

    try:
        npzpath = os.path.splitext(path)[0] + '.npz'
        #print 'Compiling mesh to binary: %s' % npzpath
        try:
            files3d.loadTextMesh(obj, path)
        except:
            print 'Could not load OBJ file %s. Perhaps it mixes tris and quads.' % path
            #import traceback
            #traceback.print_exc(file=sys.stdout)
            return False
        files3d.saveBinaryMesh(obj, npzpath)
    except:
        print 'Unable to save compiled mesh for file %s' % path
        #import traceback
        #traceback.print_exc(file=sys.stdout)
        return False
        
    return True


if __name__ == '__main__':
    allFiles = getAllFiles('data', ['*.obj'])
    allOBJs = allFiles[0]
    for (i, path) in enumerate(allOBJs):
        compileMesh(path)
        print "[%.0f%% done] converted mesh %s" % (100*(float(i)/float(len(allOBJs))), path)

    print "All done."
