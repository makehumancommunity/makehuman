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

def writeLibraryControllers(fp, human, meshes, skel, config, shapes=None):
    progress = Progress(len(meshes), None)
    fp.write('\n  <library_controllers>\n')
    for mIdx, mesh in enumerate(meshes):
        subprog = Progress() (0, 0.5)
        if skel:
            writeSkinController(fp, human, mesh, skel, config)
        subprog(0.5, 1)
        if shapes is not None:
            writeMorphController(fp, mesh, shapes[mIdx], config)
        progress.step()
    fp.write('  </library_controllers>\n')


def writeSkinController(fp, human, mesh, skel, config):
    """
    Write controller for skinning or rigging, in other words: the controller
    that ties an animation skeleton to the mesh.
    """
    progress = Progress()
    progress(0, 0.1)

    nVerts = len(mesh.coord)
    nBones = len(skel.getBones())

    rawWeights = human.getVertexWeights(human.getSkeleton())

    obj = mesh.object

    # Remap vertex weights to mesh
    if obj.proxy:
        parentWeights = obj.proxy.getVertexWeights(rawWeights, human.getSkeleton())
    else:
        parentWeights = rawWeights
    weights = mesh.getVertexWeights(parentWeights)

    vertexWeights = [list() for _ in xrange(nVerts)]
    skinWeights = []
    wn = 0
    boneNames = [ bone.name for bone in skel.getBones() ]
    for bIdx, boneName in enumerate(boneNames):
        try:
            (verts,ws) = weights.data[boneName]
        except:
            (verts,ws) = ([], [])
        wts = zip(verts, ws)
        skinWeights += wts
        for (vn,_w) in wts:
            vertexWeights[int(vn)].append((bIdx,wn))
            wn += 1
    nSkinWeights = len(skinWeights)


    # Write rig transform matrix
    progress(0.1, 0.2)
    fp.write('\n' +
        '    <controller id="%s-skin">\n' % mesh.name +
        '      <skin source="#%sMesh">\n' % mesh.name +
        '        <bind_shape_matrix>\n' +
        '          1 0 0 0\n' +
        '          0 1 0 0\n' +
        '          0 0 1 0\n' +
        '          0 0 0 1\n' +
        '        </bind_shape_matrix>\n' +
        '        <source id="%s-skin-joints">\n' % mesh.name +
        '          <IDREF_array count="%d" id="%s-skin-joints-array">\n' % (nBones,mesh.name) +
        '           ')

    # Write bones
    for bone in skel.getBones():
        bname = goodBoneName(bone.name)
        fp.write(' %s' % bname)

    progress(0.2, 0.4)
    fp.write('\n' +
        '          </IDREF_array>\n' +
        '          <technique_common>\n' +
        '            <accessor count="%d" source="#%s-skin-joints-array" stride="1">\n' % (nBones,mesh.name) +
        '              <param type="IDREF" name="JOINT"></param>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n' +
        '        <source id="%s-skin-weights">\n' % mesh.name +
        '          <float_array count="%d" id="%s-skin-weights-array">\n' % (nSkinWeights,mesh.name) +
        '           ')

    fp.write(' '.join('%s' % w[1] for w in skinWeights))

    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor count="%d" source="#%s-skin-weights-array" stride="1">\n' % (nSkinWeights,mesh.name) +
        '              <param type="float" name="WEIGHT"></param>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n' +
        '        <source id="%s-skin-poses">\n' % mesh.name +
        '          <float_array count="%d" id="%s-skin-poses-array">' % (16*nBones,mesh.name))

    progress(0.4, 0.6)
    for bone in skel.getBones():
        mat = la.inv(bone.getRestMatrix(config.meshOrientation, config.localBoneAxis, config.offset))
        for i in range(4):
            fp.write('\n           ')
            for j in range(4):
                fp.write(' %.4f' % mat[i,j])
        fp.write('\n')

    progress(0.6, 0.8)
    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor count="%d" source="#%s-skin-poses-array" stride="16">\n' % (nBones,mesh.name) +
        '              <param type="float4x4"></param>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n' +
        '        <joints>\n' +
        '          <input semantic="JOINT" source="#%s-skin-joints"/>\n' % mesh.name +
        '          <input semantic="INV_BIND_MATRIX" source="#%s-skin-poses"/>\n' % mesh.name +
        '        </joints>\n' +
        '        <vertex_weights count="%d">\n' % nVerts +
        '          <input offset="0" semantic="JOINT" source="#%s-skin-joints"/>\n' % mesh.name +
        '          <input offset="1" semantic="WEIGHT" source="#%s-skin-weights"/>\n' % mesh.name +
        '          <vcount>\n' +
        '            ')

    # Write number of bones weighted per vertex
    fp.write(' '.join(['%d' % len(wts) for wts in vertexWeights]))

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


def writeMorphController(fp, mesh, shapes, config):
    progress = Progress()
    progress(0, 0.7)
    nShapes = len(shapes)

    fp.write(
        '    <controller id="%sMorph" name="%sMorph">\n' % (mesh.name, mesh.name)+
        '      <morph source="#%sMesh" method="NORMALIZED">\n' % (rmesh.name) +
        '    <source id="%sTargets">\n' % (mesh.name) +
        '          <IDREF_array id="%sTargets-array" count="%d">' % (mesh.name, nShapes))

    for key,_ in shapes:
        fp.write(" %sMeshMorph_%s" % (mesh.name, key))

    fp.write(
        '        </IDREF_array>\n' +
        '          <technique_common>\n' +
        '            <accessor source="#%sTargets-array" count="%d" stride="1">\n' % (mesh.name, nShapes) +
        '              <param name="IDREF" type="IDREF"/>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n' +
        '        <source id="%sWeights">\n' % (mesh.name) +
        '          <float_array id="%sWeights-array" count="%d">' % (mesh.name, nShapes))

    progress(0.7, 0.99)
    fp.write(nShapes*" 0")

    fp.write('\n' +
        '        </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor source="#%sWeights-array" count="%d" stride="1">\n' % (mesh.name, nShapes) +
        '              <param name="MORPH_WEIGHT" type="float"/>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n' +
        '        <targets>\n' +
        '          <input semantic="MORPH_TARGET" source="#%sTargets"/>\n' % (mesh.name) +
        '          <input semantic="MORPH_WEIGHT" source="#%sWeights"/>\n' % (mesh.name) +
        '        </targets>\n' +
        '      </morph>\n' +
        '    </controller>\n')

    progress(1)


