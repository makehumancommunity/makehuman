#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MakeHuman build prepare

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius

**Copyright(c):**      MakeHuman Team 2001-2018

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

Use pynsist to make a distributable exe
"""

import os
import sys
import configparser
import datetime

pathname = os.path.dirname(sys.argv[0])
build_scripts = os.path.abspath(os.path.join(pathname,'..'))

os.chdir(build_scripts)

sys.path = [build_scripts] + sys.path
try:
    import build_prepare
except:
    print("Failed to import build_prepare, expected to find it at %s. Make sure to run this script from .../buildscripts/win32/" % build_scripts)
    exit(1)
 
if os.path.isfile("build.conf"):
    config = configparser.ConfigParser()
    config.read("build.conf")
else:
    print("Could not find build.conf")
    exit(1)

if len(sys.argv) < 2:
    print("Expected first argument to be location of build prepare export folder")
    exit(1)

exportDir = sys.argv[1]

if not os.path.exists(exportDir):
    print("Export dir %s does not exist" % exportDir)
    exit(1)

pynsistIn = os.path.join(build_scripts,'win32','pynsist.cfg')
pynsistOut = os.path.join(exportDir,'pynsist.cfg')

with open(pynsistIn,'r') as f:
    pynsist = f.read()

title = "makehuman-community"
version = datetime.datetime.today().strftime('%Y%m%d')

if "pynsistTitle" in config["Win32"]:
    title = config["Win32"]["title"]

if "version" in config["BuildPrepare"]:
    version = config["BuildPrepare"]["version"]

pynsist = pynsist.replace("VERSION",version)
pynsist = pynsist.replace("TITLE",title)

with open(pynsistOut,'w') as f:
    f.write(pynsist)

wrapperSrc = os.path.join(build_scripts,'win32','mhstartwrapper.py')
wrapperDst = os.path.join(exportDir,'mhstartwrapper.py')

shutil.copy(wrapperSrc,wrapperDst)

