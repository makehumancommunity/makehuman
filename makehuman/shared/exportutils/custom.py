#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

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

