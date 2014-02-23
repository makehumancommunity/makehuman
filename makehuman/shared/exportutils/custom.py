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

TODO
"""

import sys
import os
import numpy
from getpath import getPath
import log


def listCustomFiles(config):
    files = []
    if config.useCustomTargets:
        folder = getPath('data/custom')
        files += readCustomFolder(folder, config)
    return files


def readCustomFolder(folder, config):
    files = []
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isdir(path):
            files += readCustomFolder(path, config)
        else:
            (fname, ext) = os.path.splitext(file)
            if ext == ".target":
                path = os.path.join(folder, file)
                name = config.customPrefix + fname.capitalize().replace(" ","_").replace("-","_")
                files.append((path, name))
    return files

