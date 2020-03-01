#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MakeHuman build prepare

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Joel Palmius

**Copyright(c):**      MakeHuman Team 2001-2019

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

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
import shutil
import subprocess
from distutils.dir_util import copy_tree

pathname = os.path.dirname(sys.argv[0])
build_scripts = os.path.abspath(os.path.join(pathname,'..'))
rootdir = os.path.abspath(os.path.join(build_scripts,'..'))
parentdir = os.path.abspath(os.path.join(rootdir,'..'))
defaultworkdir = os.path.abspath(os.path.join(parentdir,'pynsist-work'))

os.chdir(build_scripts)

deleteAfterExport = ["docs","blendertools","create_pylint_log.py","testsuite"]

sys.path = [build_scripts] + sys.path
try:
    import build_prepare
    from build_prepare import export
except:
    print("Failed to import build_prepare, expected to find it at %s. Make sure to run this script from .../buildscripts/win32/" % build_scripts)
    exit(1)
 
if os.path.isfile("build.conf"):
    config = configparser.ConfigParser()
    config.read("build.conf")
else:
    print("Could not find build.conf")
    exit(1)

exportDir = None
if len(sys.argv) > 1:
    exportDir = sys.argv[1]
if exportDir is None:
    exportDir = defaultworkdir

if not os.path.exists(exportDir):
    os.mkdir(exportDir)

shutil.rmtree(exportDir)

export(rootdir,exportDir,False,False)

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

rootdir = os.path.abspath(os.path.join(build_scripts,".."))
icons = os.path.join(rootdir,"makehuman","icons")

iconSrc = os.path.join(icons,"makehuman-large.ico")
iconDst = os.path.join(exportDir,"makehuman.ico")

shutil.copy(wrapperSrc,wrapperDst)
shutil.copy(iconSrc,iconDst)

targetmhdir = os.path.abspath(os.path.join(exportDir,'makehuman'))
for d in deleteAfterExport:
    f = os.path.abspath(os.path.join(targetmhdir,d))
    if os.path.exists(f):
        if os.path.isfile(f):
            os.remove(f)
        else:
            shutil.rmtree(f)

pluginsdir = os.path.abspath(os.path.join(targetmhdir,'plugins'))

mhx2 = os.path.abspath(os.path.join(parentdir,'mhx2-makehuman-exchange'))
if os.path.exists(mhx2):
    tocopy = os.path.abspath(os.path.join(mhx2,'9_export_mhx2'))
    todest = os.path.abspath(os.path.join(pluginsdir,'9_export_mhx2'))
    copy_tree(tocopy, todest)
else:
    print("MHX2 was not found in parent directory: " + mhx2)

asset = os.path.abspath(os.path.join(parentdir,'community-plugins-assetdownload'))
if os.path.exists(asset):
    tocopy = os.path.abspath(os.path.join(asset,'8_asset_downloader'))
    todest = os.path.abspath(os.path.join(pluginsdir,'8_asset_downloader'))
    copy_tree(tocopy, todest)
else:
    print("asset downloader was not found in parent directory: " + asset)

mhapi = os.path.abspath(os.path.join(parentdir,'community-plugins-mhapi'))
if os.path.exists(mhapi):
    tocopy = os.path.abspath(os.path.join(mhapi,'1_mhapi'))
    todest = os.path.abspath(os.path.join(pluginsdir,'1_mhapi'))
    copy_tree(tocopy, todest)
else:
    print("MHAPI was not found in parent directory: " + mhapi)

socket = os.path.abspath(os.path.join(parentdir,'community-plugins-socket'))
if os.path.exists(socket):
    tocopy = os.path.abspath(os.path.join(socket,'8_server_socket'))
    todest = os.path.abspath(os.path.join(pluginsdir,'8_server_socket'))
    copy_tree(tocopy, todest)
else:
    print("socket plugin was not found in parent directory: " + socket)

mp = os.path.abspath(os.path.join(parentdir,'community-plugins-massproduce'))
if os.path.exists(mp):
    tocopy = os.path.abspath(os.path.join(mp,'9_massproduce'))
    todest = os.path.abspath(os.path.join(pluginsdir,'9_massproduce'))
    copy_tree(tocopy, todest)
else:
    print("mass produce plugin was not found in parent directory: " + mp)

subprocess.call(["pynsist", "pynsist.cfg"], cwd=exportDir)

buildDir = os.path.join(exportDir,"build","nsis")

for file in os.listdir(buildDir):
    if file.endswith(".exe"):
        os.remove(os.path.join(buildDir, file))
        
with open(os.path.join(buildDir,"installer.nsi"), 'r') as file:
    data = file.readlines()

data[127] = 'CreateShortCut "$Desktop\makehuman-community.lnk" "$INSTDIR\Python\pythonw.exe" \
            "$INSTDIR\mhstartwrapper.py" "$INSTDIR\makehuman.ico"\n\n'

with open(os.path.join(buildDir, "installer.nsi"), 'w') as file:
    file.writelines(data)

makensis = "/usr/bin/makensis"

if os.name == 'nt':
    makensis = os.path.join(os.environ["programfiles(x86)"], "NSIS", "makensis.exe")

try:
    subprocess.call([makensis, os.path.join(buildDir, "installer.nsi")])
except Exception as e:
    print("NSIS script failed with exception: " + e)
    print("Do you have NSIS installed to the default location?")

