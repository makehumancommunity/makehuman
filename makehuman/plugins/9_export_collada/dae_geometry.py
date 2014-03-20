#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

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

Geometry export

"""

import math
import numpy as np
import log
from progress import Progress

#----------------------------------------------------------------------
#   library_geometry
#----------------------------------------------------------------------

def writeLibraryGeometry(fp, rmeshes, config):
    progress = Progress(len(rmeshes), None)
    fp.write('\n  <library_geometries>\n')
    for rmesh in rmeshes:
        writeGeometry(fp, rmesh, config)
        progress.step()
    fp.write('  </library_geometries>\n')


def rotateCoord(coord, config):
    if config.yUpFaceZ:
        pass
    elif config.yUpFaceX:
        coord = [(z,y,-x) for (x,y,z) in coord]
    elif config.zUpFaceNegY:
        coord = [(x,-z,y) for (x,y,z) in coord]
    elif config.zUpFaceX:
        coord = [(z,x,y) for (x,y,z) in coord]
    return coord


def writeGeometry(fp, rmesh, config):
    progress = Progress()
    progress(0)

    obj = rmesh.object

    coord = config.scale*(obj.coord - config.offset)
    coord = rotateCoord(coord, config)
    nVerts = len(coord)

    fp.write('\n' +
        '    <geometry id="%sMesh" name="%s">\n' % (rmesh.name,rmesh.name) +
        '      <mesh>\n' +
        '        <source id="%s-Position">\n' % rmesh.name +
        '          <float_array count="%d" id="%s-Position-array">\n' % (3*nVerts,rmesh.name) +
        '          ')

    fp.write( ''.join([("%.4f %.4f %.4f " % tuple(co)) for co in coord]) )

    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor count="%d" source="#%s-Position-array" stride="3">\n' % (nVerts,rmesh.name) +
        '              <param type="float" name="X"></param>\n' +
        '              <param type="float" name="Y"></param>\n' +
        '              <param type="float" name="Z"></param>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n')
    progress(0.2)

    # Normals

    if config.useNormals:
        obj.calcNormals()
        vnorm = rotateCoord(obj.vnorm, config)
        nNormals = len(obj.vnorm)
        fp.write(
            '        <source id="%s-Normals">\n' % rmesh.name +
            '          <float_array count="%d" id="%s-Normals-array">\n' % (3*nNormals,rmesh.name) +
            '          ')

        fp.write( ''.join([("%.4f %.4f %.4f " % tuple(no)) for no in vnorm]) )

        fp.write('\n' +
            '          </float_array>\n' +
            '          <technique_common>\n' +
            '            <accessor count="%d" source="#%s-Normals-array" stride="3">\n' % (nNormals,rmesh.name) +
            '              <param type="float" name="X"></param>\n' +
            '              <param type="float" name="Y"></param>\n' +
            '              <param type="float" name="Z"></param>\n' +
            '            </accessor>\n' +
            '          </technique_common>\n' +
            '        </source>\n')
        progress(0.35)

    # UV coordinates

    nUvVerts = len(obj.texco)

    fp.write(
        '        <source id="%s-UV">\n' % rmesh.name +
        '          <float_array count="%d" id="%s-UV-array">\n' % (2*nUvVerts,rmesh.name) +
        '           ')

    fp.write( ''.join([("%.4f %.4f " % tuple(uv)) for uv in obj.texco]) )

    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor count="%d" source="#%s-UV-array" stride="2">\n' % (nUvVerts,rmesh.name) +
        '              <param type="float" name="S"></param>\n' +
        '              <param type="float" name="T"></param>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n')
    progress(0.5, 0.7)

    # Faces

    fp.write(
        '        <vertices id="%s-Vertex">\n' % rmesh.name +
        '          <input semantic="POSITION" source="#%s-Position"/>\n' % rmesh.name +
        '        </vertices>\n')

    checkFaces(obj, nVerts, nUvVerts)
    progress(0.7, 0.9)
    writePolylist(fp, rmesh, config)
    progress(0.9, 0.99)

    fp.write(
        '      </mesh>\n' +
        '    </geometry>\n')

    if rmesh.shapes:
        shaprog = Progress(len(rmesh.shapes))
        for name,shape in rmesh.shapes:
            writeShapeKey(fp, name, shape, rmesh, config)
            shaprog.step()

    progress(1)


def writeShapeKey(fp, name, shape, rmesh, config):
    if len(shape.verts) == 0:
        log.debug("Shapekey %s has zero verts. Ignored" % name)
        return

    progress = Progress()
    obj = rmesh.object

    # Verts

    progress(0)
    target = obj.coord - config.offset
    target[shape.verts] += shape.data[np.s_[...]]
    target = rotateCoord(config.scale*target, config)
    nVerts = len(target)

    fp.write(
        '    <geometry id="%sMeshMorph_%s" name="%s">\n' % (rmesh.name, name, name) +
        '      <mesh>\n' +
        '        <source id="%sMeshMorph_%s-positions">\n' % (rmesh.name, name) +
        '          <float_array id="%sMeshMorph_%s-positions-array" count="%d">\n' % (rmesh.name, name, 3*nVerts) +
        '           ')

    fp.write( ''.join([("%.4f %.4f %.4f " % tuple(co)) for co in target]) )

    fp.write('\n' +
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor source="#%sMeshMorph_%s-positions-array" count="%d" stride="3">\n' % (rmesh.name, name, nVerts) +
        '              <param name="X" type="float"/>\n' +
        '              <param name="Y" type="float"/>\n' +
        '              <param name="Z" type="float"/>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n')
    progress(0.3)

    # Polylist

    nFaces = len(obj.fvert)

    fp.write(
        '        <vertices id="%sMeshMorph_%s-vertices">\n' % (rmesh.name, name) +
        '          <input semantic="POSITION" source="#%sMeshMorph_%s-positions"/>\n' % (rmesh.name, name) +
        '        </vertices>\n' +
        '        <polylist count="%d">\n' % nFaces +
        '          <input semantic="VERTEX" source="#%sMeshMorph_%s-vertices" offset="0"/>\n' % (rmesh.name, name) +
        #'          <input semantic="NORMAL" source="#%sMeshMorph_%s-normals" offset="1"/>\n' % (rmesh.name, name) +
        '          <vcount>')

    fp.write( ''.join(["4 " for fv in obj.fvert]) )

    fp.write('\n' +
        '          </vcount>\n' +
        '          <p>')

    fp.write( ''.join([("%d %d %d %d " % tuple(fv)) for fv in obj.fvert]) )

    fp.write('\n' +
        '          </p>\n' +
        '        </polylist>\n' +
        '      </mesh>\n' +
        '    </geometry>\n')
    progress(1)


#
#   writePolylist(fp, rmesh, config):
#

def writePolylist(fp, rmesh, config):
    progress = Progress(2)

    obj = rmesh.object
    nFaces = len(obj.fvert)

    fp.write(
        '        <polylist count="%d">\n' % nFaces +
        '          <input offset="0" semantic="VERTEX" source="#%s-Vertex"/>\n' % rmesh.name)

    if config.useNormals:
        fp.write(
        '          <input offset="1" semantic="NORMAL" source="#%s-Normals"/>\n' % rmesh.name +
        '          <input offset="2" semantic="TEXCOORD" source="#%s-UV"/>\n' % rmesh.name +
        '          <vcount>')
    else:
        fp.write(
        '          <input offset="1" semantic="TEXCOORD" source="#%s-UV"/>\n' % rmesh.name +
        '          <vcount>')

    fp.write( ''.join(["4 " for fv in obj.fvert]) )

    fp.write('\n' +
        '          </vcount>\n'
        '          <p>')
    progress.step()

    for fn,fv in enumerate(obj.fvert):
        fuv = obj.fuvs[fn]
        if config.useNormals:
            fp.write( ''.join([("%d %d %d " % (fv[n], fv[n], fuv[n])) for n in range(4)]) )
        else:
            fp.write( ''.join([("%d %d " % (fv[n], fuv[n])) for n in range(4)]) )

    fp.write(
        '          </p>\n' +
        '        </polylist>\n')
    progress.step()

#
#   checkFaces(obj, nVerts, nUvVerts):
#

def checkFaces(obj, nVerts, nUvVerts):
    for fn,fvs in enumerate(obj.fvert):
        for n,vn in enumerate(fvs):
            uv = obj.fuvs[fn][n]
            if vn > nVerts:
                raise NameError("v %d > %d" % (vn, nVerts))
            if uv > nUvVerts:
                raise NameError("uv %d > %d" % (uv, nUvVerts))


