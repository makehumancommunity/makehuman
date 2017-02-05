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

Standalone script to compile all .proxy and .mhclo proxy files into binary 
.mhpxy (npz) files for faster loading.
"""

import sys
sys.path = ["./core", "./lib", "./shared", "./apps"] + sys.path
import os
import fnmatch
import proxy
from getpath import isSubPath, getSysDataPath
from human import Human
import files3d

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


def compileProxy(path, human):
    name = os.path.basename(path)

    try:
        npzpath = os.path.splitext(path)[0] + '.mhpxy'
        try:
            proxy_ = proxy.loadTextProxy(human, path, type=None)
        except:
            print 'Could not load proxy file %s.' % path
            import traceback
            traceback.print_exc(file=sys.stdout)
            return False
        proxy.saveBinaryProxy(proxy_, npzpath)
    except:
        print 'Unable to save compiled proxy for file %s' % path
        import traceback
        traceback.print_exc(file=sys.stdout)
        if os.path.isfile(npzpath):
            # Remove file again, in case an empty file is left
            try:
                os.remove(npzpath)
            except:
                pass
        return False
        
    return True


if __name__ == '__main__':
    human = Human(files3d.loadMesh(getSysDataPath("3dobjs/base.obj")))
    allFiles = getAllFiles('data', ['*.mhclo', '*.proxy'])
    for allProxies in allFiles:
        for (i, path) in enumerate(allProxies):
            compileProxy(path, human)
            print "[%.0f%% done] converted proxy %s" % (100*(float(i)/float(len(allProxies))), path)

    print "All done."
