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

Node export

"""

import math
import numpy as np
import numpy.linalg as la
import transformations as tm

import log

_Identity = np.identity(4, float)

#----------------------------------------------------------------------
#   library_visual_scenes
#----------------------------------------------------------------------

def writeLibraryVisualScenes(fp, meshes, skel, config, name):
    if skel:
        writeSceneWithArmature(fp, meshes, skel, config, name)
    else:
        writeSceneWithoutArmature(fp, meshes, config, name)


def writeSceneWithoutArmature(fp, meshes, config, name):
    fp.write(
        '\n  <library_visual_scenes>\n' +
        '    <visual_scene id="Scene" name="%s_Scene">\n' % name)
    for mesh in meshes:
        writeMeshNode(fp, mesh, config, 8)
    fp.write(
        '    </visual_scene>\n' +
        '  </library_visual_scenes>\n')


def writeSceneWithArmature(fp, meshes, skel, config, name):
    fp.write(
        '\n  <library_visual_scenes>\n' +
        '    <visual_scene id="Scene" name="%s_Scene">\n' % name)

    fp.write('      <node id="%s" name="%s">\n' % (skel.name,name))
    writeMatrix(fp, _Identity, "transform", 8)
    for rootBone in skel.roots:
        writeBone(fp, rootBone, config, 'layer="L1"', 1)
    fp.write('      </node>\n')

    for mesh in meshes:
        writeMeshArmatureNode(fp, mesh, skel, config)

    fp.write(
        '    </visual_scene>\n' +
        '  </library_visual_scenes>\n')


def writeMeshArmatureNode(fp, mesh, skel, config):
    padding = 8*" "
    fp.write('\n%s<node id="%sObject" name="%s">\n' % (padding, mesh.name, mesh.name))
    writeMatrix(fp, _Identity, "transform", 8+2)
    fp.write(
        '%s  <instance_controller url="#%s-skin">\n' % (padding, mesh.name) +
        '%s    <skeleton>#%sSkeleton</skeleton>\n' % (padding, skel.roots[0].name))
    writeBindMaterial(fp, mesh.material, 8)
    fp.write(
        '%s  </instance_controller>\n' % padding +
        '%s</node>\n' % padding)


def writeMeshNode(fp, mesh, config, padCount=0):
    padding = padCount*' '
    fp.write('\n%s<node id="%sObject" name="%s">\n' % (padding, mesh.name, mesh.name))
    writeMatrix(fp, _Identity, "transform", padCount+2)
    fp.write(
        '%s  <instance_geometry url="#%sMesh">\n' % (padding, mesh.name))
    writeBindMaterial(fp, mesh.material, padCount)
    fp.write(
        '%s  </instance_geometry>\n' % padding +
        '%s</node>\n' % padding)


def writeBindMaterial(fp, mat, padCount=0):
    padding = padCount*' '
    matname = mat.name.replace(" ", "_")
    fp.write(
        '%s    <bind_material>\n' % padding +
        '%s      <technique_common>\n' % padding +
        '%s        <instance_material symbol="%s" target="#%s">\n' % (padding, matname, matname) +
        '%s          <bind_vertex_input semantic="UVTex" input_semantic="TEXCOORD" input_set="0"/>\n' % padding +
        '%s        </instance_material>\n' % padding +
        '%s      </technique_common>\n' % padding +
        '%s    </bind_material>\n' % padding)


def writeBone(fp, bone, config, extra='', indentLevel=0):
    bname = goodBoneName(bone.name)
    if bone:
        nameStr = 'sid="%s"' % bname
        idStr = 'id="%s" name="%s"' % (bname, bname)
    else:
        nameStr = ''
        idStr = ''

    padding = indentLevel*"  "
    fp.write('%s      <node %s %s type="JOINT" %s>\n' % (padding, extra, nameStr, idStr))
    relmat = bone.getRelativeMatrix(config.meshOrientation, config.localBoneAxis, config.offset)
    writeMatrix(fp, relmat, "transform", indentLevel*2+8)
    for childBone in bone.children:
        writeBone(fp, childBone, config, '', indentLevel+1)
    fp.write('%s      </node>\n' % padding)


def writeMatrix(fp, mat, sid, padCount=0):
    padding = padCount*' '
    fp.write('%s<matrix sid="%s">\n' % (padding, sid))
    for i in range(4):
        fp.write('%s  %.5f %.5f %.5f %.5f\n' % (padding, mat[i][0], mat[i][1], mat[i][2], mat[i][3]))
    fp.write('%s</matrix>\n' % padding)


# To avoid error message about Sax FWL Error in Blender
def goodBoneName(bname):
    return bname.replace(".","_")

