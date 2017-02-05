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
Fbx animations
"""

from .fbx_utils import *
import math
import numpy as np
import numpy.linalg as la
import transformations as tm

#--------------------------------------------------------------------
#   Object definitions
#--------------------------------------------------------------------

TimeStep = 1847446320
TimeStep = 1528921092

# TODO write an AnimationLayer for each animation!

def countObjects(action):
    return 2 + 3*len(action.keys())


def writeObjectDefs(fp, action, config):
    ncurves = len(action.keys())

    properties_stack = [
        ("Description", "p_string", ""),
        ("LocalStart", "p_timestamp", 0),
        ("LocalStop", "p_timestamp", 0),
        ("ReferenceStart", "p_timestamp", 0),
        ("ReferenceStop", "p_timestamp", 0)
    ]

    properties_layer = [
        ("Weight", "p_number", 100, True),
        ("Mute", "p_bool", 0),
        ("Solo", "p_bool", 0),
        ("Lock", "p_bool", 0),
        ("Color", "p_color_rgb", [0.8,0.8,0.8]),
        ("BlendMode", "p_enum", 0),
        ("RotationAccumulationMode", "p_enum", 0),
        ("ScaleAccumulationMode", "p_enum", 0),
        ("BlendModeBypass", "p_ulonglong", 0)
    ]

    properties_curvenode = [
        ("d", "p_compound", "")
    ]

    if config.binary:
        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, 'Definitions')
        fbx_binary.fbx_template_generate(elem, "AnimationStack", 1, "FbxAnimStack", properties_stack)
        fbx_binary.fbx_template_generate(elem, "AnimationLayer", 1, "FbxAnimLayer", properties_layer)
        fbx_binary.fbx_template_generate(elem, "AnimationCurveNode", ncurves, "FbxAnimCurveNode", properties_curvenode)
        fbx_binary.fbx_template_generate(elem, "AnimationCurve", 3*ncurves)
        return

    import fbx_utils

    fp.write(
"""
    ObjectType: "AnimationStack" {
        Count: 1
        PropertyTemplate: "FbxAnimStack" {
            Properties70:  {
""" + fbx_utils.get_ascii_properties(properties_stack, indent=4) + """
            }
        }
    }
    ObjectType: "AnimationLayer" {
        Count: 1
        PropertyTemplate: "FbxAnimLayer" {
            Properties70:  {
""" + fbx_utils.get_ascii_properties(properties_layer, indent=4) + """
            }
        }
    }
    ObjectType: "AnimationCurveNode" {
""" +
'        Count: %d' % ncurves +
"""
        PropertyTemplate: "FbxAnimCurveNode" {
            Properties70:  {
""" + fbx_utils.get_ascii_properties(properties_curvenode, indent=4) + """
            }
        }
    }
    ObjectType: "AnimationCurve" {
""" +
'        Count: %d' % (3*ncurves) +
"""
    }
""")

#--------------------------------------------------------------------
#   Object properties
#--------------------------------------------------------------------

def writeObjectProps(fp, action, skel, config):
    sid,skey = getId("AnimStack::Take_001")
    lid,lkey = getId("AnimLayer::Layer0")

    fp.write(
        '    AnimationStack: %d, "%s", "" {\n' % (sid, skey) +
        '    }\n')

    fp.write(
        '    AnimationLayer: %d, "%s", "" {\n' % (lid, lkey) +
        '    }\n')

    for bname in action.keys():
        bone = skel.getBone(bname)
        writeAnimation(fp, bone, action, config)


def writeAnimation(fp, bone, action, config):
    aname = "Action%s" % bone.name
    points = action[bone.name]

    for channel,default in [
            ("T", 0),
            ("R", 0),
            ("S", 1)
        ]:
        writeAnimationCurveNode(fp, bone, channel, default)

    relmat = bone.getRelativeMatrix(config.meshOrientation, config.localBoneAxis, config.offset)
    translations = []
    eulers = []
    R = 180/math.pi
    for quat in points:
        mat = tm.quaternion_matrix(quat)
        mat = np.dot(relmat, mat)
        translations.append(mat[:3,3])
        eul = tm.euler_from_matrix(mat, axes='sxyz')
        eulers.append((eul[0]*R, eul[1]*R, eul[2]*R))
    scales = len(points)*[(1,1,1)]

    for channel,data in [
            ("T", translations),
            ("R", eulers),
            ("S", scales)
        ]:
        for idx,coord in enumerate(["X","Y","Z"]):
            writeAnimationCurve(fp, idx, coord, bone, channel, data)


def writeAnimationCurveNode(fp, bone, channel, default):
    id,key = getId("%s:AnimCurveNode:%s" % (bone.name, channel))
    fp.write(
        '    AnimationCurveNode: %d, "AnimCurveNode::%s", "" {\n' % (id, channel) +
        '        Properties70:  {\n' +
        '            P: "d|X", "Number", "", "A",%d\n' % default +
        '            P: "d|Y", "Number", "", "A",%d\n' % default +
        '            P: "d|Z", "Number", "", "A",%d\n' % default +
        '        }\n' +
        '    }\n')


def writeAnimationCurve(fp, idx, coord, bone, channel, data):
    id,key = getId("%s:%s:AnimCurve:%s" % (bone.name, channel, coord))
    npoints = len(data)

    timestring = ''.join(["%d," % ((n+1)*TimeStep) for n in range(npoints)])
    valuestring = ''.join(["%g," % datum[idx] for datum in data])

    fp.write(
        '    AnimationCurve: %d, "AnimCurve::" {\n' % (id) +
        '        Default: 0\n' +
        '        KeyVer: 4008\n' +
        '        KeyTime: *%d {\n' % npoints +
        '            a: %s\n' % timestring[:-1] +
        '        }\n' +
        '        KeyValueFloat: *%d {\n' % npoints +
        '            a: %s\n' % valuestring[:-1] +
        '        }\n' +
        '        ;KeyAttrFlags: Linear\n' +
        '        KeyAttrFlags: *1 {\n' +
        '            a: 260\n' +
        '        }\n' +
        '        ;KeyAttrDataFloat: RightAuto:0, NextLeftAuto:0\n' +
        '        KeyAttrDataFloat: *4 {\n' +
        '            a: 0,0,218434821,0\n' +
        '        }\n' +
        '        KeyAttrRefCount: *1 {\n' +
        '            a: %d\n' % npoints +
        '        }\n' +
        '    }\n')

#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def writeLinks(fp, action, config):
    ooLink(fp, 'AnimLayer::Layer0', 'AnimStack::Take_001', config)

    for bname in action.keys():
        for channel,type in [
                ("T","Lcl Translation"),
                ("R","Lcl Rotation"),
                ("S","Lcl Scaling")
            ]:
            acnode = "%s:AnimCurveNode:%s" % (bname, channel)
            model = "Model::%s" % bname
            ooLink(fp, acnode, 'AnimLayer::Layer0', config)
            opLink(fp, acnode, model, type, config)
            for n,coord in enumerate(["X", "Y", "Z"]):
                acurve = "%s:%s:AnimCurve:%s" % (bname, channel, coord)
                opLink(fp, acurve, acnode, "d|%s" % coord, config)


#--------------------------------------------------------------------
#   Takes
#--------------------------------------------------------------------

def writeTakes(fp, action, config):
    if config.binary:
        import fbx_binary
        fbx_binary.fbx_takes_element(fp)
        return

    fp.write(
"""
;Takes section
;----------------------------------------------------

Takes:  {
    Current: ""
""")

    if action:
        npoints = len(action.values()[0])
        fp.write(
            '   Take: "Take_001" {\n' +
            '       FileName: "Take_001.tak"\n' +
            '       LocalTime: %d,%d\n' % (TimeStep, (npoints+1)*TimeStep) +
            '       ReferenceTime: %d,%d\n' % (TimeStep, (npoints+1)*TimeStep) +
            '   }\n' +
            '}\n')
    else:
        fp.write('}\n')

