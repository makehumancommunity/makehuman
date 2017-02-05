#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier, Glynn Clements

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
