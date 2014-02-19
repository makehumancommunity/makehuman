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

Armature utilities
"""

import log
import math
import numpy as np
import transformations as tm


#-------------------------------------------------------------------------------
#   Calc joint position. Moved here from mh2proxy
#-------------------------------------------------------------------------------

def calcJointPos(obj, joint):
    verts = obj.getVerticesForGroups(["joint-"+joint])
    coords = obj.coord[verts]
    return coords.mean(axis=0)

#-------------------------------------------------------------------------------
#   Utilities
#-------------------------------------------------------------------------------

def debugCoords(string):
    from core import G
    obj = G.app.selectedHuman.meshData
    selection = obj.coord[[3630,3631,3632,3633,13634,13635,13636,13637]]
    log.debug("DebugCoords: %s" % string)
    #log.debug(str(selection))
    vec = selection[4] - selection[5]
    if np.dot(vec,vec) < 1e-10:
        raise NameError("Dead joint")


def m2b(vec):
    return np.array((vec[0], -vec[2], vec[1]))

def b2m(vec):
    return np.array((vec[0], vec[2], -vec[1]))

def getUnitVector(vec):
    length = math.sqrt(np.dot(vec,vec))
    return vec/length


def splitBoneName(bone):
    words = bone.rsplit(".", 1)
    if len(words) > 1:
        return words[0], "."+words[1]
    else:
        return words[0], ""


def getFkName(base, ext):
    return (base + ".fk" + ext)


def getIkName(base, ext):
    return (base + ".ik" + ext)


def splitBonesNames(base, ext, prefix, numAfter):
    if numAfter:
        defname1 = prefix+base+ext+".01"
        defname2 = prefix+base+ext+".02"
        defname3 = prefix+base+ext+".03"
    else:
        defname1 = prefix+base+".01"+ext
        defname2 = prefix+base+".02"+ext
        defname3 = prefix+base+".03"+ext
    return defname1, defname2, defname3


def csysBoneName(bname, infix):
    base,ext = splitBoneName(bname)
    return ("CSYS-" + base + infix + ext)


def addDict(dict, struct):
    for key,value in dict.items():
        struct[key] = value


def safeAppendToDict(struct, key, value):
    try:
        struct[key] = list(struct[key])
    except KeyError:
        struct[key] = []
    struct[key].append(value)


def mergeDicts(dicts):
    struct = {}
    for dict in dicts:
        addDict(dict, struct)
    return struct


def safeGet(dict, key, default):
    try:
        return dict[key]
    except KeyError:
        return default


def copyTransform(target, cnsname, inf=1):
    return ('CopyTrans', 0, inf, [cnsname, target, 0])


def checkOrthogonal(mat):
    prod = np.dot(mat, mat.transpose())
    diff = prod - np.identity(3,float)
    sum = 0
    for i in range(3):
        for j in range(3):
            if abs(diff[i,j]) > 1e-5:
                raise NameError("Not ortho: diff[%d,%d] = %g\n%s\n\%s" % (i, j, diff[i,j], mat, prod))
    return True


def computeRoll(head, tail, normal, bone=None):
    if normal is None:
        return 0

    p1 = m2b(head)
    p2 = m2b(tail)
    xvec = normal
    pvec = getUnitVector(p2-p1)
    xy = np.dot(xvec,pvec)
    yvec = getUnitVector(pvec-xy*xvec)
    zvec = getUnitVector(np.cross(xvec, yvec))
    if zvec is None:
        return 0
    else:
        mat = np.array((xvec,yvec,zvec))

    checkOrthogonal(mat)
    quat = tm.quaternion_from_matrix(mat)
    if abs(quat[0]) < 1e-4:
        return 0
    else:
        roll = math.pi - 2*math.atan(quat[2]/quat[0])

    if roll < -math.pi:
        roll += 2*math.pi
    elif roll > math.pi:
        roll -= 2*math.pi
    return roll

    if bone and bone.name in ["forearm.L", "forearm.R"]:
        log.debug("B  %s" % bone.name)
        log.debug(" H  %.4g %.4g %.4g" % tuple(head))
        log.debug(" T  %.4g %.4g %.4g" % tuple(tail))
        log.debug(" N  %.4g %.4g %.4g" % tuple(normal))
        log.debug(" P  %.4g %.4g %.4g" % tuple(pvec))
        log.debug(" X  %.4g %.4g %.4g" % tuple(xvec))
        log.debug(" Y  %.4g %.4g %.4g" % tuple(yvec))
        log.debug(" Z  %.4g %.4g %.4g" % tuple(zvec))
        log.debug(" Q  %.4g %.4g %.4g %.4g" % tuple(quat))
        log.debug(" R  %.4g" % roll)

    return roll


#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
"""
def readVertexGroups(file, vgroups, vgroupList):
    #file = os.path.join("shared/armature/vertexgroups", name)
    fp = open(file, "rU")
    for line in fp:
        words = line.split()
        if len(words) < 2:
            continue
        elif words[1] == "weights":
            name = words[2]
            try:
                vgroup = vgroups[name]
            except KeyError:
                vgroup = []
                vgroups[name] = vgroup
            vgroupList.append((name, vgroup))
        else:
            vgroup.append((int(words[0]), float(words[1])))
    fp.close()
"""

def mergeWeights(vgroup):
    vgroup.sort()
    ngroup = []
    vn0 = -1
    w0 = 0
    for vn,w in vgroup:
        if vn == vn0:
            w0 += w
        else:
            ngroup.append((vn0,w0))
            vn0 = vn
            w0 = w
    if vn0 >= 0:
        ngroup.append((vn0,w0))
    return ngroup

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

XUnit = np.array((1,0,0))
YUnit = np.array((0,1,0))
ZUnit = np.array((0,0,1))

YZRotation = np.array(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
ZYRotation = np.array(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))

def m2b3(vec):
    return np.dot(ZYRotation[:3,:3], vec)

def b2m4(mat):
    return np.dot(YZRotation, mat)

def getMatrix(head, tail, roll):
    vector = m2b3(tail - head)
    length = math.sqrt(np.dot(vector, vector))
    vector = vector/length
    yproj = np.dot(vector, YUnit)

    if yproj > 1-1e-6:
        axis = YUnit
        angle = 0
    elif yproj < -1+1e-6:
        axis = YUnit
        angle = math.pi
    else:
        axis = np.cross(YUnit, vector)
        axis = axis / math.sqrt(np.dot(axis,axis))
        angle = math.acos(yproj)
    mat = tm.rotation_matrix(angle, axis)
    if roll:
        mat = np.dot(mat, tm.rotation_matrix(roll, YUnit))
    mat = b2m4(mat)
    mat[:3,3] = head
    return length, mat


def normalizeQuaternion(quat):
    r2 = quat[1]*quat[1] + quat[2]*quat[2] + quat[3]*quat[3]
    if r2 > 1:
        r2 = 1
    if quat[0] >= 0:
        sign = 1
    else:
        sign = -1
    quat[0] = sign*math.sqrt(1-r2)


def checkPoints(vec1, vec2):
    return ((abs(vec1[0]-vec2[0]) < 1e-6) and
            (abs(vec1[1]-vec2[1]) < 1e-6) and
            (abs(vec1[2]-vec2[2]) < 1e-6))


