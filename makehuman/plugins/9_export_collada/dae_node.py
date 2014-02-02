#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Node export

"""

import math
import numpy as np
import numpy.linalg as la
import transformations as tm

from armature.utils import getMatrix

import log

_Identity = np.identity(4, float)

#----------------------------------------------------------------------
#   library_visual_scenes
#----------------------------------------------------------------------

def writeLibraryVisualScenes(fp, rmeshes, amt, config):
    if amt:
        writeSceneWithArmature(fp, rmeshes, amt, config)
    else:
        writeSceneWithoutArmature(fp, rmeshes, config)


def writeSceneWithoutArmature(fp, rmeshes, config):
    fp.write(
        '\n  <library_visual_scenes>\n' +
        '    <visual_scene id="Scene" name="Scene">\n')
    for rmesh in rmeshes:
        writeMeshNode(fp, "        ", rmesh, config)
    fp.write(
        '    </visual_scene>\n' +
        '  </library_visual_scenes>\n')


def writeSceneWithArmature(fp, rmeshes, amt, config):
    fp.write(
        '\n  <library_visual_scenes>\n' +
        '    <visual_scene id="Scene" name="Scene">\n')

    fp.write('      <node id="%s">\n' % amt.name)
    writeMatrix(fp, _Identity, "transform", "        ")
    for root in amt.hierarchy:
        writeBone(fp, root, [0,0,0], 'layer="L1"', "  ", amt, config)
    fp.write('      </node>\n')

    for rmesh in rmeshes:
        writeMeshArmatureNode(fp, "        ", rmesh, amt, config)

    fp.write(
        '    </visual_scene>\n' +
        '  </library_visual_scenes>\n')


def writeMeshArmatureNode(fp, pad, rmesh, amt, config):
    fp.write('\n%s<node id="%sObject" name="%s_%s">\n' % (pad, rmesh.name, amt.name, rmesh.name))
    writeMatrix(fp, _Identity, "transform", pad+"  ")
    fp.write(
        '%s  <instance_controller url="#%s-skin">\n' % (pad, rmesh.name) +
        '%s    <skeleton>#%sSkeleton</skeleton>\n' % (pad, amt.roots[0].name))
    writeBindMaterial(fp, pad, rmesh.material)
    fp.write(
        '%s  </instance_controller>\n' % pad +
        '%s</node>\n' % pad)


def writeMeshNode(fp, pad, rmesh, config):
    fp.write('\n%s<node id="%sObject" name="%s">\n' % (pad, rmesh.name, rmesh.name))
    writeMatrix(fp, _Identity, "transform", pad+"  ")
    fp.write(
        '%s  <instance_geometry url="#%sMesh">\n' % (pad, rmesh.name))
    writeBindMaterial(fp, pad, rmesh.material)
    fp.write(
        '%s  </instance_geometry>\n' % pad +
        '%s</node>\n' % pad)


def writeBindMaterial(fp, pad, mat):
    matname = mat.name.replace(" ", "_")
    fp.write(
        '%s    <bind_material>\n' % pad +
        '%s      <technique_common>\n' % pad +
        '%s        <instance_material symbol="%s" target="#%s">\n' % (pad, matname, matname) +
        '%s          <bind_vertex_input semantic="UVTex" input_semantic="TEXCOORD" input_set="0"/>\n' % pad +
        '%s        </instance_material>\n' % pad +
        '%s      </technique_common>\n' % pad +
        '%s    </bind_material>\n' % pad)


def writeBone(fp, hier, orig, extra, pad, amt, config):
    (bone, children) = hier
    bname = goodBoneName(bone.name)
    if bone:
        nameStr = 'sid="%s"' % bname
        idStr = 'id="%s" name="%s"' % (bname, bname)
    else:
        nameStr = ''
        idStr = ''

    fp.write('%s      <node %s %s type="JOINT" %s>\n' % (pad, extra, nameStr, idStr))
    relmat = bone.getRelativeMatrix(config)
    writeMatrix(fp, relmat, "transform", pad+"        ")
    for child in children:
        writeBone(fp, child, bone.head, '', pad+'  ', amt, config)
    fp.write('%s      </node>\n' % pad)


def writeMatrix(fp, mat, sid, pad):
    fp.write('%s<matrix sid="%s">\n' % (pad, sid))
    for i in range(4):
        fp.write('%s  %.5f %.5f %.5f %.5f\n' % (pad, mat[i][0], mat[i][1], mat[i][2], mat[i][3]))
    fp.write('%s</matrix>\n' % pad)


# To avoid error message about Sax FWL Error in Blender
def goodBoneName(bname):
    return bname.replace(".","_")

