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

Controller export

"""

from .dae_node import goodBoneName
from progress import Progress

import math
import log
import numpy as np
import numpy.linalg as la
import transformations as tm

#----------------------------------------------------------------------
#   library_controllers
#----------------------------------------------------------------------

def writeLibraryControllers(fp, rmeshes, amt, config):
    progress = Progress(len(rmeshes), None)
    fp.write('\n  <library_controllers>\n')
    for rmesh in rmeshes:
        subprog = Progress() (0, 0.5)
        if amt:
            writeSkinController(fp, rmesh, amt, config)
        subprog(0.5, 1)
        if rmesh.shapes:
            writeMorphController(fp, rmesh, config)
        progress.step()
    fp.write('  </library_controllers>\n')


def writeSkinController(fp, rmesh, amt, config):
    progress = Progress()
    progress(0, 0.1)

    nVerts = len(rmesh.getCoord())
    nBones = len(amt.bones)

    skinWeights = []
    vertexWeights = [list() for _ in xrange(nVerts)]
    wn = 0
    for bn,bname in enumerate(amt.bones):
        try:
            wts = rmesh.weights[bname]
        except KeyError:
            wts = []
        log.debug("W %d %s %s" % (bn,bname,wts))
        skinWeights += wts
        for (vn,_w) in wts:
            vertexWeights[int(vn)].append((bn,wn))
            wn += 1
    nSkinWeights = len(skinWeights)

    progress(0.1, 0.2)
    fp.write('\n' +
        '    <controller id="%s-skin">\n' % rmesh.name +
        '      <skin source="#%sMesh">\n' % rmesh.name +
        '        <bind_shape_matrix>\n' +
        '          1 0 0 0\n' +
        '          0 1 0 0\n' +
        '          0 0 1 0\n' +
        '          0 0 0 1\n' +
        '        </bind_shape_matrix>\n' +
        '        <source id="%s-skin-joints">\n' % rmesh.name +
        '          <IDREF_array count="%d" id="%s-skin-joints-array">\n' % (nBones,rmesh.name) +
        '           ')

    for bone in amt.bones.values():
        bname = goodBoneName(bone.name)
        fp.write(' %s' % bname)

    progress(0.2, 0.4)
    fp.write('\n' +
        '          </IDREF_array>\n' +
        '          <technique_common>\n' +
        '            <accessor count="%d" source="#%s-skin-joints-array" stride="1">\n' % (nBones,rmesh.name) +
        '              <param type="IDREF" name="JOINT"></param>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n' +
        '        <source id="%s-skin-weights">\n' % rmesh.name +
        '          <float_array count="%d" id="%s-skin-weights-array">\n' % (nSkinWeights,rmesh.name) +
        '           ')

    fp.write(''.join(' %s' % w[1] for w in skinWeights))

    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor count="%d" source="#%s-skin-weights-array" stride="1">\n' % (nSkinWeights,rmesh.name) +
        '              <param type="float" name="WEIGHT"></param>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n' +
        '        <source id="%s-skin-poses">\n' % rmesh.name +
        '          <float_array count="%d" id="%s-skin-poses-array">' % (16*nBones,rmesh.name))

    progress(0.4, 0.6)
    for bone in amt.bones.values():
        #mat = la.inv(bone.getRestOrTPoseMatrix(config))
        mat = la.inv(bone.getRestMatrix(config))
        for i in range(4):
            fp.write('\n           ')
            for j in range(4):
                fp.write(' %.4f' % mat[i,j])
        fp.write('\n')

    progress(0.6, 0.8)
    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor count="%d" source="#%s-skin-poses-array" stride="16">\n' % (nBones,rmesh.name) +
        '              <param type="float4x4"></param>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n' +
        '        <joints>\n' +
        '          <input semantic="JOINT" source="#%s-skin-joints"/>\n' % rmesh.name +
        '          <input semantic="INV_BIND_MATRIX" source="#%s-skin-poses"/>\n' % rmesh.name +
        '        </joints>\n' +
        '        <vertex_weights count="%d">\n' % nVerts +
        '          <input offset="0" semantic="JOINT" source="#%s-skin-joints"/>\n' % rmesh.name +
        '          <input offset="1" semantic="WEIGHT" source="#%s-skin-weights"/>\n' % rmesh.name +
        '          <vcount>\n' +
        '            ')

    fp.write(''.join(['%d ' % len(wts) for wts in vertexWeights]))

    progress(0.8, 0.99)
    fp.write('\n' +
        '          </vcount>\n'
        '          <v>\n' +
        '           ')

    for wts in vertexWeights:
        fp.write(''.join([' %d %d' % pair for pair in wts]))

    fp.write('\n' +
        '          </v>\n' +
        '        </vertex_weights>\n' +
        '      </skin>\n' +
        '    </controller>\n')

    progress(1)


def writeMorphController(fp, rmesh, config):
    progress = Progress()
    progress(0, 0.7)
    nShapes = len(rmesh.shapes)

    fp.write(
        '    <controller id="%sMorph" name="%sMorph">\n' % (rmesh.name, rmesh.name)+
        '      <morph source="#%sMesh" method="NORMALIZED">\n' % (rmesh.name) +
        '    <source id="%sTargets">\n' % (rmesh.name) +
        '          <IDREF_array id="%sTargets-array" count="%d">' % (rmesh.name, nShapes))

    for key,_ in rmesh.shapes:
        fp.write(" %sMeshMorph_%s" % (rmesh.name, key))

    fp.write(
        '        </IDREF_array>\n' +
        '          <technique_common>\n' +
        '            <accessor source="#%sTargets-array" count="%d" stride="1">\n' % (rmesh.name, nShapes) +
        '              <param name="IDREF" type="IDREF"/>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n' +
        '        <source id="%sWeights">\n' % (rmesh.name) +
        '          <float_array id="%sWeights-array" count="%d">' % (rmesh.name, nShapes))

    progress(0.7, 0.99)
    fp.write(nShapes*" 0")

    fp.write('\n' +
        '        </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor source="#%sWeights-array" count="%d" stride="1">\n' % (rmesh.name, nShapes) +
        '              <param name="MORPH_WEIGHT" type="float"/>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n' +
        '        <targets>\n' +
        '          <input semantic="MORPH_TARGET" source="#%sTargets"/>\n' % (rmesh.name) +
        '          <input semantic="MORPH_WEIGHT" source="#%sWeights"/>\n' % (rmesh.name) +
        '        </targets>\n' +
        '      </morph>\n' +
        '    </controller>\n')

    progress(1)


