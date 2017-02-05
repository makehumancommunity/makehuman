#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

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

TODO
"""

import sys
sys.path = [".", "./core", "./lib"] + sys.path
import makehuman
import algos3d
import numpy as np
import os
import zipfile
import fnmatch
from codecs import open

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


if __name__ == '__main__':
    obj = algos3d.Target(None, None)
    allFiles = getAllFiles('data', ['*.target', '*.png'])
    npzPath = 'data/targets.npz'
    with zipfile.ZipFile(npzPath, mode='w', compression=zipfile.ZIP_DEFLATED) as zip:
        npzdir = os.path.dirname(npzPath)
        allTargets = allFiles[0]

        # License for all official MH targets
        lpath = 'data/targets/targets.license.npy'
        np.save(lpath, makehuman.getAssetLicense().toNumpyString())
        zip.write(lpath, os.path.relpath(lpath, npzdir))
        os.remove(lpath)

        for (i, path) in enumerate(allTargets):
            try:
                obj._load_text(path)
                iname, vname, lname = obj._save_binary(path)
                zip.write(iname, os.path.relpath(iname, npzdir))
                zip.write(vname, os.path.relpath(vname, npzdir))
                if lname:
                    zip.write(lname, os.path.relpath(lname, npzdir))
                    os.remove(lname)
                os.remove(iname)
                os.remove(vname)
                print "[%.0f%% done] converted target %s" % (100*(float(i)/float(len(allTargets))), path)
            except None, e:
                raise e
                print 'error converting target %s' % path

    print "Writing images list"
    with open('data/images.list', 'w', encoding="utf-8") as f:
        allImages = allFiles[1]
        for path in allImages:
            path = path.replace('\\','/')
            f.write(path + '\n')
    print "All done."
