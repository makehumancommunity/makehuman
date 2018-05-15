#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2017

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
Fbx skeleton
"""

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


def writeObjectDefs(fp, meshes, skel, config):
    nModels = len(meshes)
    if skel:
        nBones = skel.getBoneCount()
        nModels += nBones + 1

    # (name, ptype, value, animatable, custom)
    properties = [
        ("QuaternionInterpolate", "p_enum", 0),
        ("RotationOffset",  "p_vector_3d",  [0,0,0]),
        ("RotationPivot",   "p_vector_3d",  [0,0,0]),
        ("ScalingOffset",   "p_vector_3d",  [0,0,0]),
        ("ScalingPivot",    "p_vector_3d",  [0,0,0]),
        ("TranslationActive", "p_bool",     0),
        ("TranslationMin",  "p_vector_3d",  [0,0,0]),
        ("TranslationMax",  "p_vector_3d",  [0,0,0]),
        ("TranslationMinX", "p_bool",       0),
        ("TranslationMinY", "p_bool",       0),
        ("TranslationMinZ", "p_bool",       0),
        ("TranslationMaxX", "p_bool",       0),
        ("TranslationMaxY", "p_bool",       0),
        ("TranslationMaxZ", "p_bool",       0),
        ("RotationOrder",   "p_enum",       0),
        ("RotationSpaceForLimitOnly", "p_bool", 0),
        ("RotationStiffnessX", "p_double",  0),
        ("RotationStiffnessY", "p_double",  0),
        ("RotationStiffnessZ", "p_double",  0),
        ("AxisLen",         "p_double",     10),
        ("PreRotation",     "p_vector_3d",  [0,0,0]),
        ("PostRotation",    "p_vector_3d",  [0,0,0]),
        ("RotationActive",  "p_bool",       0),
        ("RotationMin",     "p_vector_3d",  [0,0,0]),
        ("RotationMax",     "p_vector_3d",  [0,0,0]),
        ("RotationMinX",    "p_bool",       0),
        ("RotationMinY",    "p_bool",       0),
        ("RotationMinZ",    "p_bool",       0),
        ("RotationMaxX",    "p_bool",       0),
        ("RotationMaxY",    "p_bool",       0),
        ("RotationMaxZ",    "p_bool",       0),
        ("InheritType",     "p_enum",       0),
        ("ScalingActive",   "p_bool",       0),
        ("ScalingMin",      "p_vector_3d",  [0,0,0]),
        ("ScalingMax",      "p_vector_3d",  [1,1,1]),
        ("ScalingMinX",     "p_bool",       0),
        ("ScalingMinY",     "p_bool",       0),
        ("ScalingMinZ",     "p_bool",       0),
        ("ScalingMaxX",     "p_bool",       0),
        ("ScalingMaxY",     "p_bool",       0),
        ("ScalingMaxZ",     "p_bool",       0),
        ("GeometricTranslation", "p_vector_3d", [0,0,0]),
        ("GeometricRotation", "p_vector_3d", [0,0,0]),
        ("GeometricScaling", "p_vector_3d", [1,1,1]),
        ("MinDampRangeX",   "p_double",     0),
        ("MinDampRangeY",   "p_double",     0),
        ("MinDampRangeZ",   "p_double",     0),
        ("MaxDampRangeX",   "p_double",     0),
        ("MaxDampRangeY",   "p_double",     0),
        ("MaxDampRangeZ",   "p_double",     0),
        ("MinDampStrengthX", "p_double",    0),
        ("MinDampStrengthY", "p_double",    0),
        ("MinDampStrengthZ", "p_double",    0),
        ("MaxDampStrengthX", "p_double",    0),
        ("MaxDampStrengthY", "p_double",    0),
        ("MaxDampStrengthZ", "p_double",    0),
        ("PreferedAngleX",  "p_double",     0),
        ("PreferedAngleY",  "p_double",     0),
        ("PreferedAngleZ",  "p_double",     0),
        ("LookAtProperty",  "p_object",     None),
        ("UpVectorProperty", "p_object",    None),
        ("Show",            "p_bool",       1),
        ("NegativePercentShapeSupport", "p_bool", 1),
        ("DefaultAttributeIndex", "p_integer", -1),
        ("Freeze",          "p_bool",       0),
        ("LODBox",          "p_bool",       0),
        ("Lcl Translation", "p_lcl_translation", [0,0,0], True),
        ("Lcl Rotation",    "p_lcl_rotation", [0,0,0],  True),
        ("Lcl Scaling",     "p_lcl_scaling", [1,1,1],   True),
        ("Visibility",      "p_visibility", 1,          True),
        ("Visibility Inheritance", "p_visibility_inheritance", 1)
    ]

    skel_properties = [
        ("Color",           "p_color_rgb",  [0.8,0.8,0.8]),
        ("Size",            "p_double",     100),
        ("LimbLength",      "p_double",     1)  # TODO this property had special "H" flag, is this required?
    ]

    if config.binary:

        properties = [
            (b"QuaternionInterpolate", b"p_enum", 0),
            (b"RotationOffset", b"p_vector_3d", [0, 0, 0]),
            (b"RotationPivot", b"p_vector_3d", [0, 0, 0]),
            (b"ScalingOffset", b"p_vector_3d", [0, 0, 0]),
            (b"ScalingPivot", b"p_vector_3d", [0, 0, 0]),
            (b"TranslationActive", b"p_bool", 0),
            (b"TranslationMin", b"p_vector_3d", [0, 0, 0]),
            (b"TranslationMax", b"p_vector_3d", [0, 0, 0]),
            (b"TranslationMinX", b"p_bool", 0),
            (b"TranslationMinY", b"p_bool", 0),
            (b"TranslationMinZ", b"p_bool", 0),
            (b"TranslationMaxX", b"p_bool", 0),
            (b"TranslationMaxY", b"p_bool", 0),
            (b"TranslationMaxZ", b"p_bool", 0),
            (b"RotationOrder", b"p_enum", 0),
            (b"RotationSpaceForLimitOnly", b"p_bool", 0),
            (b"RotationStiffnessX", b"p_double", 0),
            (b"RotationStiffnessY", b"p_double", 0),
            (b"RotationStiffnessZ", b"p_double", 0),
            (b"AxisLen", b"p_double", 10),
            (b"PreRotation", b"p_vector_3d", [0, 0, 0]),
            (b"PostRotation", b"p_vector_3d", [0, 0, 0]),
            (b"RotationActive", b"p_bool", 0),
            (b"RotationMin", b"p_vector_3d", [0, 0, 0]),
            (b"RotationMax", b"p_vector_3d", [0, 0, 0]),
            (b"RotationMinX", b"p_bool", 0),
            (b"RotationMinY", b"p_bool", 0),
            (b"RotationMinZ", b"p_bool", 0),
            (b"RotationMaxX", b"p_bool", 0),
            (b"RotationMaxY", b"p_bool", 0),
            (b"RotationMaxZ", b"p_bool", 0),
            (b"InheritType", b"p_enum", 0),
            (b"ScalingActive", b"p_bool", 0),
            (b"ScalingMin", b"p_vector_3d", [0, 0, 0]),
            (b"ScalingMax", b"p_vector_3d", [1, 1, 1]),
            (b"ScalingMinX", b"p_bool", 0),
            (b"ScalingMinY", b"p_bool", 0),
            (b"ScalingMinZ", b"p_bool", 0),
            (b"ScalingMaxX", b"p_bool", 0),
            (b"ScalingMaxY", b"p_bool", 0),
            (b"ScalingMaxZ", b"p_bool", 0),
            (b"GeometricTranslation", b"p_vector_3d", [0, 0, 0]),
            (b"GeometricRotation", b"p_vector_3d", [0, 0, 0]),
            (b"GeometricScaling", b"p_vector_3d", [1, 1, 1]),
            (b"MinDampRangeX", b"p_double", 0),
            (b"MinDampRangeY", b"p_double", 0),
            (b"MinDampRangeZ", b"p_double", 0),
            (b"MaxDampRangeX", b"p_double", 0),
            (b"MaxDampRangeY", b"p_double", 0),
            (b"MaxDampRangeZ", b"p_double", 0),
            (b"MinDampStrengthX", b"p_double", 0),
            (b"MinDampStrengthY", b"p_double", 0),
            (b"MinDampStrengthZ", b"p_double", 0),
            (b"MaxDampStrengthX", b"p_double", 0),
            (b"MaxDampStrengthY", b"p_double", 0),
            (b"MaxDampStrengthZ", b"p_double", 0),
            (b"PreferedAngleX", b"p_double", 0),
            (b"PreferedAngleY", b"p_double", 0),
            (b"PreferedAngleZ", b"p_double", 0),
            (b"LookAtProperty", b"p_object", None),
            (b"UpVectorProperty", b"p_object", None),
            (b"Show", b"p_bool", 1),
            (b"NegativePercentShapeSupport", b"p_bool", 1),
            (b"DefaultAttributeIndex", b"p_integer", -1),
            (b"Freeze", b"p_bool", 0),
            (b"LODBox", b"p_bool", 0),
            (b"Lcl Translation", b"p_lcl_translation", [0, 0, 0], True),
            (b"Lcl Rotation", b"p_lcl_rotation", [0, 0, 0], True),
            (b"Lcl Scaling", b"p_lcl_scaling", [1, 1, 1], True),
            (b"Visibility", b"p_visibility", 1, True),
            (b"Visibility Inheritance", b"p_visibility_inheritance", 1)
        ]

        skel_properties = [
            (b"Color", b"p_color_rgb", [0.8, 0.8, 0.8]),
            (b"Size", b"p_double", 100),
            (b"LimbLength", b"p_double", 1)  # TODO this property had special "H" flag, is this required?
        ]

        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, b'Definitions')
        fbx_binary.fbx_template_generate(elem, b"Model", nModels, b"FbxNode", properties)

        if skel:
            fbx_binary.fbx_template_generate(elem, b"NodeAttribute", nBones, b"FbxSkeleton", skel_properties)
        return

    from . import fbx_utils
    fp.write(
"""
    ObjectType: "Model" {
""" +
'    Count: %d' % nModels +
"""
        PropertyTemplate: "FbxNode" {
            Properties70:  {
"""+ fbx_utils.get_ascii_properties(properties, indent=3) + """
            }
        }
    }
""")

    if skel:
        fp.write(
"""    ObjectType: "NodeAttribute" {
        Count: %d""" % (nBones) +
"""
        PropertyTemplate: "FbxSkeleton" {
            Properties70:  {
""" + fbx_utils.get_ascii_properties(skel_properties, indent=3) + """
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
        writeNodeAttributeProp(fp, bone, config)
    writeNodeProp(fp, skel, config)
    for bone in skel.getBones():
        writeBoneProp(fp, bone, config)


def writeNodeAttributeProp(fp, bone, config):
    id,key = getId("NodeAttribute::%s" % bone.name)

    properties = [
        ("Size",        "p_double",     1),
        ("LimbLength",  "p_double",     bone.length)  # TODO what to do with "H" flag?
    ]

    if config.binary:
        properties = [
            (b"Size", b"p_double", 1),
            (b"LimbLength", b"p_double", bone.length)  # TODO what to do with "H" flag?
        ]
        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, b'Objects')
        fbx_binary.fbx_data_skeleton_bone_node(elem, key, id, properties)
        return

    from . import fbx_utils
    fp.write(
'    NodeAttribute: %d, "%s", "LimbNode" {' % (id, key) + """
        Properties70:  {
"""+ fbx_utils.get_ascii_properties(properties, indent=3) + """
        }
        TypeFlags: "Skeleton"
    }
""")


def writeNodeProp(fp, skel, config):
    id,key = getId("Model::%s" % skel.name)

    properties = [
        ("RotationActive",  "p_bool",       1),
        ("InheritType",     "p_enum",       1),
        ("ScalingMax",      "p_vector_3d",  [0,0,0]),
        ("MHName",          "p_string",     skel.name, False, True)
    ]

    if config.binary:

        properties = [
            (b"RotationActive", b"p_bool", 1),
            (b"InheritType", b"p_enum", 1),
            (b"ScalingMax", b"p_vector_3d", [0, 0, 0]),
            (b"MHName", b"p_string", skel.name, False, True)
        ]

        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, b'Objects')
        fbx_binary.fbx_data_skeleton_model(elem, key, id, properties)
        return

    from . import fbx_utils
    fp.write(
'    Model: %d, "%s", "Null" {' % (id, key) +
"""
        Version: 232
        Properties70:  {
""" + fbx_utils.get_ascii_properties(properties, indent=3) + """
        }
        Shading: Y
        Culling: "CullingOff"
    }
""")


def writeBoneProp(fp, bone, config):
    from . import fbx_utils
    id,key = getId("Model::%s" % bone.name)

    mat = bone.getRelativeMatrix(config.meshOrientation, config.localBoneAxis, config.offset)
    trans = mat[:3,3]
    e = tm.euler_from_matrix(mat, axes='sxyz')

    properties = [
        ("RotationActive",  "p_bool",       1),
        ("InheritType",     "p_enum",       1),
        ("ScalingMax",      "p_vector_3d",  [0,0,0]),
        ("DefaultAttributeIndex", "p_integer",  0),
        ("Lcl Translation", "p_lcl_translation", list(trans), True),
        ("Lcl Rotation",    "p_lcl_rotation", [e[0]*R, e[1]*R, e[2]*R], True),
        ("Lcl Scaling",     "p_lcl_scaling",  [1,1,1], True),
        ("MHName",          "p_string",     bone.name, False, True),
    ]

    if config.binary:

        properties = [
            (b"RotationActive", b"p_bool", 1),
            (b"InheritType", b"p_enum", 1),
            (b"ScalingMax", b"p_vector_3d", [0, 0, 0]),
            (b"DefaultAttributeIndex", b"p_integer", 0),
            (b"Lcl Translation", b"p_lcl_translation", list(trans), True),
            (b"Lcl Rotation", b"p_lcl_rotation", [e[0] * R, e[1] * R, e[2] * R], True),
            (b"Lcl Scaling", b"p_lcl_scaling", [1, 1, 1], True),
            (b"MHName", b"p_string", bone.name, False, True),
        ]

        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, b'Objects')
        fbx_binary.fbx_data_skeleton_bone_model(elem, key, id, properties)
        return

    fp.write(
'    Model: %d, "%s", "LimbNode" {' % (id,key) +
"""
        Version: 232
        Properties70:  {
"""+ fbx_utils.get_ascii_properties(properties, indent=3) + """
        }
        Shading: Y
        Culling: "CullingOff"
    }
""")

#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def writeLinks(fp, skel, config):
    if skel is None:
        return

    ooLink(fp, 'Model::%s' % skel.name, 'Model::RootNode', config)

    for bone in skel.getBones():
        if bone.parent:
            parentName = bone.parent.name if bone.parent else None
            ooLink(fp, 'Model::%s' % bone.name, 'Model::%s' % parentName, config)
        else:
            ooLink(fp, 'Model::%s' % bone.name, 'Model::%s' % skel.name, config)
        ooLink(fp, 'NodeAttribute::%s' % bone.name, 'Model::%s' % bone.name, config)


