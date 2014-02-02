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
Fbx headers
"""

from . import fbx_skeleton
from . import fbx_mesh
from . import fbx_deformer
from . import fbx_material
from . import fbx_anim


def writeHeader(fp, filepath):
    import datetime
    today = datetime.datetime.now()

    fp.write("""; FBX 7.3.0 project file
; Exported from MakeHuman TM
; ----------------------------------------------------

FBXHeaderExtension:  {
    FBXHeaderVersion: 1003
    FBXVersion: 7300
""" +
"""
    CreationTimeStamp:  {
        Version: 1000
        Year: %d
        Month: %d
        Day: %d
        Hour: %d
        Minute: %d
        Second: %d
        Millisecond: %d
    }
""" % (int(today.strftime('%Y')), int(today.strftime('%m')), int(today.strftime('%d')), int(today.strftime('%H')), int(today.strftime('%M')), int(today.strftime('%S')), int(float(today.strftime('%f'))/1000)) +
"""
    Creator: "FBX SDK/FBX Plugins version 2013.3"
    SceneInfo: "SceneInfo::GlobalInfo", "UserData" {
        Type: "UserData"
        Version: 100
        MetaData:  {
            Version: 100
            Title: ""
            Subject: ""
            Author: "www.makehuman.org"
            Keywords: ""
            Revision: ""
            Comment: ""
        }
        Properties70:  {
""" +
'           P: "DocumentUrl", "KString", "Url", "", "%s"\n' % filepath +
'           P: "SrcDocumentUrl", "KString", "Url", "", "%s"\n' % filepath +
"""
            P: "Original", "Compound", "", ""
            P: "Original|ApplicationVendor", "KString", "", "", ""
            P: "Original|ApplicationName", "KString", "", "", ""
            P: "Original|ApplicationVersion", "KString", "", "", ""
            P: "Original|DateTime_GMT", "DateTime", "", "", ""
            P: "Original|FileName", "KString", "", "", ""
            P: "LastSaved", "Compound", "", ""
            P: "LastSaved|ApplicationVendor", "KString", "", "", ""
            P: "LastSaved|ApplicationName", "KString", "", "", ""
            P: "LastSaved|ApplicationVersion", "KString", "", "", ""
            P: "LastSaved|DateTime_GMT", "DateTime", "", "", ""
        }
    }
}
GlobalSettings:  {
    Version: 1000
    Properties70:  {
        P: "UpAxis", "int", "Integer", "",1
        P: "UpAxisSign", "int", "Integer", "",1
        P: "FrontAxis", "int", "Integer", "",2
        P: "FrontAxisSign", "int", "Integer", "",1
        P: "CoordAxis", "int", "Integer", "",0
        P: "CoordAxisSign", "int", "Integer", "",1
        P: "OriginalUpAxis", "int", "Integer", "",-1
        P: "OriginalUpAxisSign", "int", "Integer", "",1
        P: "UnitScaleFactor", "double", "Number", "",10
        P: "OriginalUnitScaleFactor", "double", "Number", "",1
        P: "AmbientColor", "ColorRGB", "Color", "",0,0,0
        P: "DefaultCamera", "KString", "", "", "Producer Perspective"
        P: "TimeMode", "enum", "", "",0
        P: "TimeSpanStart", "KTime", "Time", "",0
        P: "TimeSpanStop", "KTime", "Time", "",46186158000
        P: "CustomFrameRate", "double", "Number", "",-1
    }
}

; Documents Description
;------------------------------------------------------------------

Documents:  {
    Count: 1
    Document: 39112896, "Scene", "Scene" {
        Properties70:  {
            P: "SourceObject", "object", "", ""
            P: "ActiveAnimStackName", "KString", "", "", ""
            P: "COLLADA_ID", "KString", "", "", "Scene"
        }
        RootNode: 0
    }
}

; Document References
;------------------------------------------------------------------

References:  {
}
""")


def writeObjectDefs(fp, rmeshes, amt, config):
    count = (
              fbx_skeleton.countObjects(rmeshes, amt) +
              fbx_mesh.countObjects(rmeshes, amt) +
              fbx_deformer.countObjects(rmeshes, amt) +
              #fbx_anim.countObjects(rmeshes, amt) +
              1
            )
    if config.useMaterials:
        count += fbx_material.countObjects(rmeshes, amt)

    fp.write(
"""
; Object definitions
;------------------------------------------------------------------

Definitions:  {

    Version: 100
""" +
'    Count: %d' % count +
"""
    ObjectType: "GlobalSettings" {
        Count: 1
    }
""")


def writeObjectProps(fp, rmeshes, amt):
    fp.write(
"""
; Object properties
;------------------------------------------------------------------

Objects:  {
""")


def writeLinks(fp, rmeshes, amt):
    fp.write(
"""
; Object connections
;------------------------------------------------------------------

Connections:  {
""")


def writeTakes(fp):
    fp.write(
"""
;Takes section
;----------------------------------------------------

Takes:  {
    Current: ""
}
""")
