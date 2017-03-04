#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

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
Fbx headers
"""

from . import fbx_skeleton
from . import fbx_mesh
from . import fbx_deformer
from . import fbx_material
from . import fbx_anim


def writeHeader(fp, filepath, config):
    import datetime
    today = datetime.datetime.now()

    id = 39112896

    if config.binary:
        from . import fbx_binary
        import os
        root = fp
        fbx_binary.fbx_header_elements(root, config, filepath, today)
        name = os.path.splitext(os.path.basename(filepath))[0]
        fbx_binary.fbx_documents_elements(root, name, id)
        fbx_binary.fbx_references_elements(root)
        return

    import fbx_utils
    mesh_orientation = fbx_utils.getMeshOrientation(config)
    up_axis, front_axis, coord_axis = fbx_utils.RIGHT_HAND_AXES[mesh_orientation]

    fp.write("""; FBX 7.3.0 project file
; Exported from MakeHuman TM (www.makehuman.org)
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
        P: "UpAxis", "int", "Integer", "",%s
        P: "UpAxisSign", "int", "Integer", "",%s
        P: "FrontAxis", "int", "Integer", "",%s
        P: "FrontAxisSign", "int", "Integer", "",%s
        P: "CoordAxis", "int", "Integer", "",%s
        P: "CoordAxisSign", "int", "Integer", "",%s
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
}""" % (up_axis[0], up_axis[0], front_axis[0], front_axis[1], coord_axis[0], coord_axis[1]) + """

; Documents Description
;------------------------------------------------------------------

Documents:  {
    Count: 1
    Document: %s, "Scene", "Scene" {""" % id + """
        Properties70:  {
            P: "SourceObject", "object", "", ""
            P: "ActiveAnimStackName", "KString", "", "", ""
        }
        RootNode: 0
    }
}

; Document References
;------------------------------------------------------------------

References:  {
}
""")


def writeObjectDefs(fp, meshes, skel, action, config):
    count = (
              fbx_skeleton.countObjects(skel) +
              fbx_mesh.countObjects(meshes) +
              fbx_deformer.countObjects(meshes, skel) +
              1
            )
    if config.useMaterials:
        count += fbx_material.countObjects(meshes)

    if action:
        count += fbx_anim.countObjects(action)

    if config.binary:
        from . import fbx_binary
        fbx_binary.fbx_definitions_elements(fp, count)
        return

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


def writeObjectProps(fp, config):
    if config.binary:
        from . import fbx_binary
        objects = fbx_binary.elem_empty(fp, b"Objects")
        return

    fp.write(
"""
; Object properties
;------------------------------------------------------------------

Objects:  {
""")


def writeLinks(fp, config):
    if config.binary:
        from . import fbx_binary
        fbx_binary.fbx_connections_element(fp)
        return

    fp.write(
"""
; Object connections
;------------------------------------------------------------------

Connections:  {
""")
