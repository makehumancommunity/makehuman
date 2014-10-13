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
Fbx skeleton
"""

import numpy as np
import transformations as tm
from .fbx_utils import *

#--------------------------------------------------------------------
#   Object definitions
#--------------------------------------------------------------------

def countObjects(skel):
    """
    Number of object required for exporting the specified skeleton.
    """
    if skel:
        nBones = skel.getBoneCount()
        return (2*nBones + 1)
    else:
        return 0


def writeObjectDefs(fp, meshes, skel):
    nModels = len(meshes)
    if skel:
        nBones = skel.getBoneCount()
        nModels += nBones + 1

    fp.write(
"""
    ObjectType: "Model" {
""" +
'    Count: %d' % nModels +
"""
        PropertyTemplate: "FbxNode" {
            Properties70:  {
                P: "QuaternionInterpolate", "enum", "", "",0
                P: "RotationOffset", "Vector3D", "Vector", "",0,0,0
                P: "RotationPivot", "Vector3D", "Vector", "",0,0,0
                P: "ScalingOffset", "Vector3D", "Vector", "",0,0,0
                P: "ScalingPivot", "Vector3D", "Vector", "",0,0,0
                P: "TranslationActive", "bool", "", "",0
                P: "TranslationMin", "Vector3D", "Vector", "",0,0,0
                P: "TranslationMax", "Vector3D", "Vector", "",0,0,0
                P: "TranslationMinX", "bool", "", "",0
                P: "TranslationMinY", "bool", "", "",0
                P: "TranslationMinZ", "bool", "", "",0
                P: "TranslationMaxX", "bool", "", "",0
                P: "TranslationMaxY", "bool", "", "",0
                P: "TranslationMaxZ", "bool", "", "",0
                P: "RotationOrder", "enum", "", "",0
                P: "RotationSpaceForLimitOnly", "bool", "", "",0
                P: "RotationStiffnessX", "double", "Number", "",0
                P: "RotationStiffnessY", "double", "Number", "",0
                P: "RotationStiffnessZ", "double", "Number", "",0
                P: "AxisLen", "double", "Number", "",10
                P: "PreRotation", "Vector3D", "Vector", "",0,0,0
                P: "PostRotation", "Vector3D", "Vector", "",0,0,0
                P: "RotationActive", "bool", "", "",0
                P: "RotationMin", "Vector3D", "Vector", "",0,0,0
                P: "RotationMax", "Vector3D", "Vector", "",0,0,0
                P: "RotationMinX", "bool", "", "",0
                P: "RotationMinY", "bool", "", "",0
                P: "RotationMinZ", "bool", "", "",0
                P: "RotationMaxX", "bool", "", "",0
                P: "RotationMaxY", "bool", "", "",0
                P: "RotationMaxZ", "bool", "", "",0
                P: "InheritType", "enum", "", "",0
                P: "ScalingActive", "bool", "", "",0
                P: "ScalingMin", "Vector3D", "Vector", "",0,0,0
                P: "ScalingMax", "Vector3D", "Vector", "",1,1,1
                P: "ScalingMinX", "bool", "", "",0
                P: "ScalingMinY", "bool", "", "",0
                P: "ScalingMinZ", "bool", "", "",0
                P: "ScalingMaxX", "bool", "", "",0
                P: "ScalingMaxY", "bool", "", "",0
                P: "ScalingMaxZ", "bool", "", "",0
                P: "GeometricTranslation", "Vector3D", "Vector", "",0,0,0
                P: "GeometricRotation", "Vector3D", "Vector", "",0,0,0
                P: "GeometricScaling", "Vector3D", "Vector", "",1,1,1
                P: "MinDampRangeX", "double", "Number", "",0
                P: "MinDampRangeY", "double", "Number", "",0
                P: "MinDampRangeZ", "double", "Number", "",0
                P: "MaxDampRangeX", "double", "Number", "",0
                P: "MaxDampRangeY", "double", "Number", "",0
                P: "MaxDampRangeZ", "double", "Number", "",0
                P: "MinDampStrengthX", "double", "Number", "",0
                P: "MinDampStrengthY", "double", "Number", "",0
                P: "MinDampStrengthZ", "double", "Number", "",0
                P: "MaxDampStrengthX", "double", "Number", "",0
                P: "MaxDampStrengthY", "double", "Number", "",0
                P: "MaxDampStrengthZ", "double", "Number", "",0
                P: "PreferedAngleX", "double", "Number", "",0
                P: "PreferedAngleY", "double", "Number", "",0
                P: "PreferedAngleZ", "double", "Number", "",0
                P: "LookAtProperty", "object", "", ""
                P: "UpVectorProperty", "object", "", ""
                P: "Show", "bool", "", "",1
                P: "NegativePercentShapeSupport", "bool", "", "",1
                P: "DefaultAttributeIndex", "int", "Integer", "",-1
                P: "Freeze", "bool", "", "",0
                P: "LODBox", "bool", "", "",0
                P: "Lcl Translation", "Lcl Translation", "", "A",0,0,0
                P: "Lcl Rotation", "Lcl Rotation", "", "A",0,0,0
                P: "Lcl Scaling", "Lcl Scaling", "", "A",1,1,1
                P: "Visibility", "Visibility", "", "A",1
                P: "Visibility Inheritance", "Visibility Inheritance", "", "",1
            }
        }
    }
""")

    if skel:
        fp.write(
'    ObjectType: "NodeAttribute" {\n' +
'       Count: %d' % (nBones) +
"""
        PropertyTemplate: "FbxSkeleton" {
            Properties70:  {
                P: "Color", "ColorRGB", "Color", "",0.8,0.8,0.8
                P: "Size", "double", "Number", "",100
                P: "LimbLength", "double", "Number", "H",1
            }
        }
    }
""")

#--------------------------------------------------------------------
#   Object properties
#--------------------------------------------------------------------

def writeObjectProps(fp, skel, config):
    if skel is None:
        return
    for bone in skel.getBones():
        writeNodeAttributeProp(fp, bone)
    writeNodeProp(fp, skel, config)
    for bone in skel.getBones():
        writeBoneProp(fp, bone, config)


def writeNodeAttributeProp(fp, bone):
    id,key = getId("NodeAttribute::%s" % bone.name)
    fp.write(
'    NodeAttribute: %d, "%s", "LimbNode" {\n' % (id, key) +
'        Properties70:  {\n' +
'            P: "Size", "double", "Number", "",1\n' +
'            P: "LimbLength", "double", "Number", "H",%d\n' % bone.length +
'        }\n' +
'        TypeFlags: "Skeleton"\n' +
'    }\n')


def writeNodeProp(fp, skel, config):
    id,key = getId("Model::%s" % skel.name)
    fp.write(
'    Model: %d, "%s", "Null" {' % (id, key) +
"""
        Version: 232
        Properties70:  {
            P: "RotationActive", "bool", "", "",1
            P: "InheritType", "enum", "", "",1
            P: "ScalingMax", "Vector3D", "Vector", "",0,0,0
""" +
'            P: "MHName", "KString", "", "", "%s"' % skel.name +
"""
        }
        Shading: Y
        Culling: "CullingOff"
    }
""")


def writeBoneProp(fp, bone, config):
    id,key = getId("Model::%s" % bone.name)
    fp.write(
'    Model: %d, "%s", "LimbNode" {' % (id,key) +
"""
        Version: 232
        Properties70:  {
            P: "RotationActive", "bool", "", "",1
            P: "InheritType", "enum", "", "",1
            P: "ScalingMax", "Vector3D", "Vector", "",0,0,0
            P: "DefaultAttributeIndex", "int", "Integer", "",0
""")

    mat = bone.getRelativeMatrix(config.meshOrientation, config.localBoneAxis, config.offset)
    trans = mat[:3,3]
    e = tm.euler_from_matrix(mat, axes='sxyz')
    fp.write(
'            P: "Lcl Translation", "Lcl Translation", "", "A",%.4f,%.4f,%.4f\n' % tuple(trans) +
'            P: "Lcl Rotation", "Lcl Rotation", "", "A",%.4f,%.4f,%.4f\n' % (e[0]*R, e[1]*R, e[2]*R) +
'            P: "Lcl Scaling", "Lcl Scaling", "", "A",1,1,1\n' +
'            P: "MHName", "KString", "", "", "%s"' % bone.name +
"""
        }
        Shading: Y
        Culling: "CullingOff"
    }
""")

#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def writeLinks(fp, skel):
    if skel is None:
        return

    ooLink(fp, 'Model::%s' % skel.name, 'Model::RootNode')

    for bone in skel.getBones():
        if bone.parent:
            parentName = bone.parent.name if bone.parent else None
            ooLink(fp, 'Model::%s' % bone.name, 'Model::%s' % parentName)
        else:
            ooLink(fp, 'Model::%s' % bone.name, 'Model::%s' % skel.name)
        ooLink(fp, 'NodeAttribute::%s' % bone.name, 'Model::%s' % bone.name)


