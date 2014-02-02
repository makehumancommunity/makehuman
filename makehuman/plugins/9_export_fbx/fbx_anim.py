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
Fbx animations
"""

from .fbx_utils import *

#--------------------------------------------------------------------
#   Object definitions
#--------------------------------------------------------------------

def countObjects(rmeshes, amt):
    return 2


def writeObjectDefs(fp, rmeshes, amt):
    fp.write(
"""
    ObjectType: "AnimationStack" {
        Count: 1
        PropertyTemplate: "FbxAnimStack" {
            Properties70:  {
                P: "Description", "KString", "", "", ""
                P: "LocalStart", "KTime", "Time", "",0
                P: "LocalStop", "KTime", "Time", "",0
                P: "ReferenceStart", "KTime", "Time", "",0
                P: "ReferenceStop", "KTime", "Time", "",0
            }
        }
    }
    ObjectType: "AnimationLayer" {
        Count: 1
        PropertyTemplate: "FbxAnimLayer" {
            Properties70:  {
                P: "Weight", "Number", "", "A",100
                P: "Mute", "bool", "", "",0
                P: "Solo", "bool", "", "",0
                P: "Lock", "bool", "", "",0
                P: "Color", "ColorRGB", "Color", "",0.8,0.8,0.8
                P: "BlendMode", "enum", "", "",0
                P: "RotationAccumulationMode", "enum", "", "",0
                P: "ScaleAccumulationMode", "enum", "", "",0
                P: "BlendModeBypass", "ULongLong", "", "",0
            }
        }
    }
""")

#--------------------------------------------------------------------
#   Object properties
#--------------------------------------------------------------------

def writeObjectProps(fp, rmeshes, amt):
    sid,skey = getId("AnimStack::Take 001")
    lid,lkey = getId("AnimLayer::BaseLayer")

    fp.write(
'    AnimationStack: %d, "%s", "" {' % (sid, skey) +
"""
        Properties70:  {
            P: "LocalStart", "KTime", "Time", "",1924423250
            P: "LocalStop", "KTime", "Time", "",46186158000
            P: "ReferenceStart", "KTime", "Time", "",1924423250
            P: "ReferenceStop", "KTime", "Time", "",46186158000
        }
    }
""" +
'    AnimationLayer: %d, "%s", "" {' % (lid, lkey) +
"""
    }
""")

#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def writeLinks(fp, rmeshes, amt):
    ooLink(fp, 'AnimLayer::BaseLayer', 'AnimStack::Take 001')
