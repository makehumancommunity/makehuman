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

Geometry export

"""

import math
import numpy as np
import log
from progress import Progress

#----------------------------------------------------------------------
#   library_geometry
#----------------------------------------------------------------------

def writeLibraryGeometry(fp, meshes, config, shapes=None):
    progress = Progress(len(meshes), None)
    fp.write('\n  <library_geometries>\n')
    for mIdx,mesh in enumerate(meshes):
        if shapes is None:
            shape = None
        else:
            shape = shapes[mIdx]
        writeGeometry(fp, mesh, config, shape)
        progress.step()
    fp.write('  </library_geometries>\n')


# TODO make shared function, config.getTransform() and mesh.clone(transform)
def rotateCoord(coord, config):
    if config.meshOrientation == 'yUpFaceZ':
        pass
    elif config.meshOrientation == 'yUpFaceX':
        # z,y,-x
        coord = np.dstack((coord[:,2],coord[:,1],-coord[:,0]))[0]
    elif config.meshOrientation == 'zUpFaceNegY':
        # x,z,-y
        coord = np.dstack((coord[:,0],-coord[:,2],coord[:,1]))[0]
    elif config.meshOrientation == 'zUpFaceX':
        # z,x,y
        coord = np.dstack((coord[:,2],coord[:,0],coord[:,1]))[0]
    return coord


def writeGeometry(fp, mesh, config, shapes=None):
    progress = Progress()
    progress(0)

    coord = mesh.coord + config.offset
    coord = rotateCoord(coord, config)
    nVerts = len(coord)

    fp.write('\n' +
        '    <geometry id="%sMesh" name="%s">\n' % (mesh.name,mesh.name) +
        '      <mesh>\n' +
        '        <source id="%s-Position">\n' % mesh.name +
        '          <float_array count="%d" id="%s-Position-array">\n' % (3*nVerts,mesh.name) +
        '          ')

    fp.write( ''.join([("%.4f %.4f %.4f " % tuple(co)) for co in coord]) )

    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor count="%d" source="#%s-Position-array" stride="3">\n' % (nVerts,mesh.name) +
        '              <param type="float" name="X"></param>\n' +
        '              <param type="float" name="Y"></param>\n' +
        '              <param type="float" name="Z"></param>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n')
    progress(0.2)

    # Normals

    if config.useNormals:
        mesh.calcNormals()
        vnorm = rotateCoord(mesh.vnorm, config)
        nNormals = len(mesh.vnorm)
        fp.write(
            '        <source id="%s-Normals">\n' % mesh.name +
            '          <float_array count="%d" id="%s-Normals-array">\n' % (3*nNormals,mesh.name) +
            '          ')

        fp.write( ''.join([("%.4f %.4f %.4f " % tuple(no)) for no in vnorm]) )

        fp.write('\n' +
            '          </float_array>\n' +
            '          <technique_common>\n' +
            '            <accessor count="%d" source="#%s-Normals-array" stride="3">\n' % (nNormals,mesh.name) +
            '              <param type="float" name="X"></param>\n' +
            '              <param type="float" name="Y"></param>\n' +
            '              <param type="float" name="Z"></param>\n' +
            '            </accessor>\n' +
            '          </technique_common>\n' +
            '        </source>\n')
        progress(0.35)

    # UV coordinates

    nUvVerts = len(mesh.texco)

    fp.write(
        '        <source id="%s-UV">\n' % mesh.name +
        '          <float_array count="%d" id="%s-UV-array">\n' % (2*nUvVerts,mesh.name) +
        '           ')

    fp.write( ''.join([("%.4f %.4f " % tuple(uv)) for uv in mesh.texco]) )

    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor count="%d" source="#%s-UV-array" stride="2">\n' % (nUvVerts,mesh.name) +
        '              <param type="float" name="S"></param>\n' +
        '              <param type="float" name="T"></param>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n')
    progress(0.5, 0.7)

    # Faces

    fp.write(
        '        <vertices id="%s-Vertex">\n' % mesh.name +
        '          <input semantic="POSITION" source="#%s-Position"/>\n' % mesh.name +
        '        </vertices>\n')

    checkFaces(mesh, nVerts, nUvVerts)
    progress(0.7, 0.9)
    writePolylist(fp, mesh, config)
    progress(0.9, 0.99)

    fp.write(
        '      </mesh>\n' +
        '    </geometry>\n')

    if shapes is not None:
        shaprog = Progress(len(shapes))
        for name,shape in shapes:
            writeShapeKey(fp, name, shape, mesh, config)
            shaprog.step()

    progress(1)


def writeShapeKey(fp, name, shape, mesh, config):
    if len(shape.verts) == 0:
        log.debug("Shapekey %s has zero verts. Ignored" % name)
        return

    progress = Progress()

    # Verts

    progress(0)
    target = mesh.coord.copy()
    target[:] += config.offset
    target[shape.verts] += shape.data[np.s_[...]]
    target = rotateCoord(config.scale*target, config)
    nVerts = len(target)

    fp.write(
        '    <geometry id="%sMeshMorph_%s" name="%s">\n' % (mesh.name, name, name) +
        '      <mesh>\n' +
        '        <source id="%sMeshMorph_%s-positions">\n' % (mesh.name, name) +
        '          <float_array id="%sMeshMorph_%s-positions-array" count="%d">\n' % (mesh.name, name, 3*nVerts) +
        '           ')

    fp.write( ''.join([("%.4f %.4f %.4f " % tuple(co)) for co in target]) )

    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor source="#%sMeshMorph_%s-positions-array" count="%d" stride="3">\n' % (mesh.name, name, nVerts) +
        '              <param name="X" type="float"/>\n' +
        '              <param name="Y" type="float"/>\n' +
        '              <param name="Z" type="float"/>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n')
    progress(0.3)

    # Polylist

    nFaces = len(mesh.fvert)

    fp.write(
        '        <vertices id="%sMeshMorph_%s-vertices">\n' % (mesh.name, name) +
        '          <input semantic="POSITION" source="#%sMeshMorph_%s-positions"/>\n' % (mesh.name, name) +
        '        </vertices>\n' +
        '        <polylist count="%d">\n' % nFaces +
        '          <input semantic="VERTEX" source="#%sMeshMorph_%s-vertices" offset="0"/>\n' % (mesh.name, name) +
        #'          <input semantic="NORMAL" source="#%sMeshMorph_%s-normals" offset="1"/>\n' % (mesh.name, name) +
        '          <vcount>')

    fp.write( ''.join(["4 " for fv in mesh.fvert]) )

    fp.write('\n' +
        '          </vcount>\n' +
        '          <p>')

    fp.write( ''.join([("%d %d %d %d " % tuple(fv)) for fv in mesh.fvert]) )

    fp.write('\n' +
        '          </p>\n' +
        '        </polylist>\n' +
        '      </mesh>\n' +
        '    </geometry>\n')
    progress(1)


#
#   writePolylist(fp, mesh, config):
#

def writePolylist(fp, mesh, config):
    progress = Progress(2)

    nFaces = len(mesh.fvert)

    fp.write(
        '        <polylist count="%d">\n' % nFaces +
        '          <input offset="0" semantic="VERTEX" source="#%s-Vertex"/>\n' % mesh.name)

    if config.useNormals:
        fp.write(
        '          <input offset="1" semantic="NORMAL" source="#%s-Normals"/>\n' % mesh.name +
        '          <input offset="2" semantic="TEXCOORD" source="#%s-UV"/>\n' % mesh.name +
        '          <vcount>')
    else:
        fp.write(
        '          <input offset="1" semantic="TEXCOORD" source="#%s-UV"/>\n' % mesh.name +
        '          <vcount>')

    fp.write( ''.join(["4 " for fv in mesh.fvert]) )

    fp.write('\n' +
        '          </vcount>\n'
        '          <p>')
    progress.step()

    for fn,fv in enumerate(mesh.fvert):
        fuv = mesh.fuvs[fn]
        if config.useNormals:
            fp.write( ''.join([("%d %d %d " % (fv[n], fv[n], fuv[n])) for n in range(4)]) )
        else:
            fp.write( ''.join([("%d %d " % (fv[n], fuv[n])) for n in range(4)]) )

    fp.write(
        '          </p>\n' +
        '        </polylist>\n')
    progress.step()

#
#   checkFaces(mesh, nVerts, nUvVerts):
#

def checkFaces(mesh, nVerts, nUvVerts):
    # TODO document: what does this do (apart from slowing down export)?
    for fn,fvs in enumerate(mesh.fvert):
        for n,vn in enumerate(fvs):
            uv = mesh.fuvs[fn][n]
            if vn > nVerts:
                raise NameError("v %d > %d" % (vn, nVerts))
            if uv > nUvVerts:
                raise NameError("uv %d > %d" % (uv, nUvVerts))


