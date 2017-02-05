#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

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
Fbx utilities
"""

import os
from .fbx_utils_bin import *

#--------------------------------------------------------------------
#   Radians - degrees
#--------------------------------------------------------------------

R = 180/math.pi
D = math.pi/180

#--------------------------------------------------------------------
#   Ids
#--------------------------------------------------------------------

def resetId():
    global _IdDict, _Id, _IsLinking
    _IdDict = { 'Model::RootNode' : 0 }
    _Id = 1000
    _IsLinking = False


def startLinking():
    global _IsLinking
    _IsLinking = True


def stopLinking():
    global _IsLinking
    _IsLinking = False


def getId(key):
    global _IdDict, _Id, _IsLinking
    try:
        return _IdDict[key],key
    except KeyError:
        pass
    if _IsLinking:
        raise NameError("Did not find id for key %s while linking" % key)
    _Id += 1
    _IdDict[key] = _Id
    return _Id,key

#--------------------------------------------------------------------
#   Paths
#--------------------------------------------------------------------

# TODO storing global variable is ugly
def setAbsolutePath(filepath):
    global _AbsPath
    _AbsPath = os.path.dirname(os.path.abspath(filepath))


def getRelativePath(filepath):
    global _AbsPath
    relpath = os.path.relpath(os.path.abspath(filepath), _AbsPath)
    relpath = os.path.join("textures", os.path.basename(filepath))
    return relpath


def getTexturePath(filepath):
    global _AbsPath
    filepath = os.path.abspath(os.path.expanduser(filepath))
    filepath = os.path.join(_AbsPath, "textures", os.path.basename(filepath))
    return filepath


def getTextureName(filepath):
    texfile = os.path.basename(filepath)
    return texfile.replace(".","_")


def getMeshName(mesh, exportname):
    if mesh.name == "base.obj":
        return exportname
    else:
        return os.path.splitext(mesh.name)[0]

#--------------------------------------------------------------------
#   Write utils
#--------------------------------------------------------------------

def writeMatrix(fp, name, mat, pad=""):
    fp.write(
        '%s        %s: *16 {\n' % (pad, name) +
        '%s            a: ' % pad)
    for i in range(4):
        # FBX stores matrices in column-major fashion
        fp.write("%.4f,%.4f,%.4f,%.4f" % (mat[i,0],mat[i,1],mat[i,2],mat[i,3]))
        if i < 3:
            fp.write(',\n%s               ' % pad)
    fp.write('\n%s        }\n' % pad)

#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def ooLink(fp, child, parent, config):
    cid,_ = getId(child)
    pid,_ = getId(parent)

    if config.binary:
        import fbx_binary
        elem = fbx_binary.get_child_element(fp, 'Connections')
        fbx_binary.elem_connection(elem, b"OO", cid, pid)
        return

    fp.write(
'    ;%s, %s\n' % (child, parent) +
'    C: "OO",%d,%d\n' % (cid, pid) +
'\n')


def opLink(fp, child, parent, channel, config):
    cid,_ = getId(child)
    pid,_ = getId(parent)

    if config.binary:
        import fbx_binary
        elem = fbx_binary.get_child_element(fp, 'Connections')
        fbx_binary.elem_connection(elem, b"OP", cid, pid, channel)
        return

    fp.write(
'    ;%s, %s\n' % (child, parent) +
'    C: "OP",%d,%d, "%s"\n' % (cid, pid, channel) +
'\n')
