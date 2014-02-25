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

import os
import math
import meshstat
import warpmodifier
import algos3d
import log
from getpath import getSysDataPath
import targets

#----------------------------------------------------------
#   Get shapes for exporters.
#   Shapekeys are now represented by targets.
#----------------------------------------------------------

def getShape(filepath, obj, isHuman=False):
    if isHuman:
        try:
            return algos3d.targetbuffer[filepath]
        except KeyError:
            pass
    return algos3d.Target(obj, filepath)

#----------------------------------------------------------
#   Setup expressions
#----------------------------------------------------------

def _loadExpressions():
    expressions = []
    exprTargets = targets.getTargets().findTargets('expression-units')
    for eComponent in exprTargets:
        name = eComponent.key
        # Remove 'expression-units' components from group name
        name = name[2:]
        expressions.append('-'.join(name))
    return expressions

_expressionUnits = None

def getExpressionUnits():
    global _expressionUnits
    if _expressionUnits is None:
        # Remove duplicates
        units = {}
        for unit in _loadExpressions():
            units[unit] = True
        _expressionUnits = list(units.keys())
        _expressionUnits.sort()
    return _expressionUnits

#----------------------------------------------------------
#
#----------------------------------------------------------

def readExpressionUnits(human, t0, t1, progressCallback = None):
    targetList = []
    t,dt = initTimes(getExpressionUnits(), 0.0, 1.0)

    referenceVariables = { 'gender': 'female',
                           'age':    'young' }

    for name in getExpressionUnits():
        if progressCallback:
            progressCallback(t, text="Reading expression %s" % name)

        target = warpmodifier.compileWarpTarget('expression-units', name, human, "face", referenceVariables)
        targetList.append((name, target))
        t += dt
    return targetList


def initTimes(flist, t0, t1):
    dt = t1-t0
    n = len(flist)
    if n > 0:
        dt /= n
    return t0,dt


def readExpressionMhm(folder):
    exprList = []
    for file in os.listdir(folder):
        (fname, ext) = os.path.splitext(file)
        if ext == ".mhm":
            path = os.path.join(folder, file)
            fp = open(path, "rU")
            units = []
            for line in fp:
                words = line.split()
                if len(words) < 3:
                    pass
                elif words[0] == "expression":
                    units.append(words[1:3])
            fp.close()
            exprList.append((fname,units))
    return exprList




