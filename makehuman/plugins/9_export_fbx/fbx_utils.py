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
Fbx utilities
"""

import os
import math

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
    tex = os.path.basename(filepath).replace(" ","_")
    return filepath, tex


def getRmeshName(rmesh, amt):
    if amt and rmesh.name == "base.obj":
        return amt.name
    else:
        return os.path.splitext(rmesh.name)[0]

#--------------------------------------------------------------------
#   Write utils
#--------------------------------------------------------------------

def writeMatrix(fp, name, mat, pad=""):
    fp.write(
        '%s        %s: *16 {\n' % (pad, name) +
        '%s            a: ' % pad)
    for i in range(4):
        fp.write("%.4f,%.4f,%.4f,%.4f" % (mat[i,0],mat[i,1],mat[i,2],mat[i,3]))
        if i < 3:
            fp.write(',\n%s               ' % pad)
    fp.write('\n%s        }\n' % pad)


def writeComma(fp, n, last):
    if n == last:
        fp.write('\n')
    elif n%1024 == 1023:
        fp.write(',\n            ')
    else:
        fp.write(',')

#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def ooLink(fp, child, parent):
    cid,_ = getId(child)
    pid,_ = getId(parent)
    fp.write(
'    ;%s, %s\n' % (child, parent) +
'    C: "OO",%d,%d\n' % (cid, pid) +
'\n')


def opLink(fp, child, parent, channel):
    cid,_ = getId(child)
    pid,_ = getId(parent)
    fp.write(
'    ;%s, %s\n' % (child, parent) +
'    C: "OP",%d,%d, "%s"\n' % (cid, pid, channel) +
'\n')

