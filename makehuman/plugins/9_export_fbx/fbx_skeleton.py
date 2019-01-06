#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2019

**Licensing:**         AGPL3

    This file is part of MakeHuman Community (www.makehumancommunity.org).

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
        (b"QuaternionInterpolate", (0, "p_enum", False)),  # 0 = no quat interpolation.
        (b"RotationOffset", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"RotationPivot", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"ScalingOffset", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"ScalingPivot", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"TranslationActive", (False, "p_bool", False)),
        (b"TranslationMin", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"TranslationMax", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"TranslationMinX", (False, "p_bool", False)),
        (b"TranslationMinY", (False, "p_bool", False)),
        (b"TranslationMinZ", (False, "p_bool", False)),
        (b"TranslationMaxX", (False, "p_bool", False)),
        (b"TranslationMaxY", (False, "p_bool", False)),
        (b"TranslationMaxZ", (False, "p_bool", False)),
        (b"RotationOrder", (0, "p_enum", False)),  # we always use 'XYZ' order.
        (b"RotationSpaceForLimitOnly", (False, "p_bool", False)),
        (b"RotationStiffnessX", (0.0, "p_double", False)),
        (b"RotationStiffnessY", (0.0, "p_double", False)),
        (b"RotationStiffnessZ", (0.0, "p_double", False)),
        (b"AxisLen", (10.0, "p_double", False)),
        (b"PreRotation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"PostRotation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"RotationActive", (False, "p_bool", False)),
        (b"RotationMin", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"RotationMax", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"RotationMinX", (False, "p_bool", False)),
        (b"RotationMinY", (False, "p_bool", False)),
        (b"RotationMinZ", (False, "p_bool", False)),
        (b"RotationMaxX", (False, "p_bool", False)),
        (b"RotationMaxY", (False, "p_bool", False)),
        (b"RotationMaxZ", (False, "p_bool", False)),
        (b"InheritType", (0, "p_enum", False)),  # RrSs
        (b"ScalingActive", (False, "p_bool", False)),
        (b"ScalingMin", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"ScalingMax", ((1.0, 1.0, 1.0), "p_vector_3d", False)),
        (b"ScalingMinX", (False, "p_bool", False)),
        (b"ScalingMinY", (False, "p_bool", False)),
        (b"ScalingMinZ", (False, "p_bool", False)),
        (b"ScalingMaxX", (False, "p_bool", False)),
        (b"ScalingMaxY", (False, "p_bool", False)),
        (b"ScalingMaxZ", (False, "p_bool", False)),
        (b"GeometricTranslation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"GeometricRotation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"GeometricScaling", ((1.0, 1.0, 1.0), "p_vector_3d", False)),
        (b"MinDampRangeX", (0.0, "p_double", False)),
        (b"MinDampRangeY", (0.0, "p_double", False)),
        (b"MinDampRangeZ", (0.0, "p_double", False)),
        (b"MaxDampRangeX", (0.0, "p_double", False)),
        (b"MaxDampRangeY", (0.0, "p_double", False)),
        (b"MaxDampRangeZ", (0.0, "p_double", False)),
        (b"MinDampStrengthX", (0.0, "p_double", False)),
        (b"MinDampStrengthY", (0.0, "p_double", False)),
        (b"MinDampStrengthZ", (0.0, "p_double", False)),
        (b"MaxDampStrengthX", (0.0, "p_double", False)),
        (b"MaxDampStrengthY", (0.0, "p_double", False)),
        (b"MaxDampStrengthZ", (0.0, "p_double", False)),
        (b"PreferedAngleX", (0.0, "p_double", False)),
        (b"PreferedAngleY", (0.0, "p_double", False)),
        (b"PreferedAngleZ", (0.0, "p_double", False)),
        (b"LookAtProperty", (None, "p_object", False)),
        (b"UpVectorProperty", (None, "p_object", False)),
        (b"Show", (True, "p_bool", False)),
        (b"NegativePercentShapeSupport", (True, "p_bool", False)),
        (b"DefaultAttributeIndex", (-1, "p_integer", False)),
        (b"Freeze", (False, "p_bool", False)),
        (b"LODBox", (False, "p_bool", False)),
        (b"Lcl Translation", ((0.0, 0.0, 0.0), "p_lcl_translation", True)),
        (b"Lcl Rotation", ((0.0, 0.0, 0.0), "p_lcl_rotation", True)),
        (b"Lcl Scaling", ((1.0, 1.0, 1.0), "p_lcl_scaling", True)),
        (b"Visibility", (1.0, "p_visibility", True)),
        (b"Visibility Inheritance", (1, "p_visibility_inheritance", False))
    ]

    skel_properties = [
        (b"Color",           "p_color_rgb",  [0.8,0.8,0.8]),
        (b"Size",            "p_double",     100),
        (b"LimbLength",      "p_double",     1)  # TODO this property had special "H" flag, is this required?
    ]

    if config.binary:
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
        (b"Size",        "p_double",     1),
        (b"LimbLength",  "p_double",     bone.length)  # TODO what to do with "H" flag?
    ]

    if config.binary:
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
        (b"RotationActive",  "p_bool",       1),
        (b"InheritType",     "p_enum",       1),
        (b"ScalingMax",      "p_vector_3d",  [0,0,0]),
        (b"MHName",          "p_string",     skel.name, False, True)
    ]

    if config.binary:
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
        (b"RotationActive",  "p_bool",       1),
        (b"InheritType",     "p_enum",       1),
        (b"ScalingMax",      "p_vector_3d",  [0,0,0]),
        (b"DefaultAttributeIndex", "p_integer",  0),
        (b"Lcl Translation", "p_lcl_translation", list(trans), True),
        (b"Lcl Rotation",    "p_lcl_rotation", [e[0]*R, e[1]*R, e[2]*R], True),
        (b"Lcl Scaling",     "p_lcl_scaling",  [1,1,1], True),
        (b"MHName",          "p_string",     bone.name, False, True),
    ]

    if config.binary:
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


