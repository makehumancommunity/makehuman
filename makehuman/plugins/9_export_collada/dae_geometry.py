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
    offs = config.scale * config.offset
    coord = [co-offs for co in coord]
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

    coord = rotateCoord(rmesh.getCoord(), config)
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
        normals = rotateCoord(rmesh.getVnorm(), config)
        nNormals = len(normals)
        fp.write(
            '        <source id="%s-Normals">\n' % rmesh.name +
            '          <float_array count="%d" id="%s-Normals-array">\n' % (3*nNormals,rmesh.name) +
            '          ')

        fp.write( ''.join([("%.4f %.4f %.4f " % tuple(normalize(no))) for no in normals]) )

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

    texco = rmesh.getTexco()
    nUvVerts = len(texco)

    fp.write(
        '        <source id="%s-UV">\n' % rmesh.name +
        '          <float_array count="%d" id="%s-UV-array">\n' % (2*nUvVerts,rmesh.name) +
        '           ')

    fp.write( ''.join([("%.4f %.4f " % tuple(uv)) for uv in texco]) )

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

    checkFaces(rmesh, nVerts, nUvVerts)
    progress(0.7, 0.9)
    #writePolygons(fp, rmesh, config)
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


def normalize(vec):
    vec = np.array(vec)
    return vec/math.sqrt(np.dot(vec,vec))


def writeShapeKey(fp, name, shape, rmesh, config):
    if len(shape.verts) == 0:
        log.debug("Shapekey %s has zero verts. Ignored" % name)
        return

    progress = Progress()

    # Verts

    progress(0)
    target = np.array(rmesh.getCoord())
    target[shape.verts] += shape.data[np.s_[...]]
    target = rotateCoord(target, config)
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

    # Normals
    """
    fp.write(
'        <source id="%sMeshMorph_%s-normals">\n' % (rmesh.name, name) +
'          <float_array id="%sMeshMorph_%s-normals-array" count="18">\n' % (rmesh.name, name))
-0.9438583 0 0.3303504 0 0.9438583 0.3303504 0.9438583 0 0.3303504 0 -0.9438583 0.3303504 0 0 -1 0 0 1
    fp.write(
        '          </float_array>\n' +
        '          <technique_common>\n' +
        '            <accessor source="#%sMeshMorph_%s-normals-array" count="6" stride="3">\n' % (rmesh.name, name) +
        '              <param name="X" type="float"/>\n' +
        '              <param name="Y" type="float"/>\n' +
        '              <param name="Z" type="float"/>\n' +
        '            </accessor>\n' +
        '          </technique_common>\n' +
        '        </source>\n')
    """
    progress(0.6)

    # Polylist

    fvert = rmesh.getFvert()
    nFaces = len(fvert)

    fp.write(
        '        <vertices id="%sMeshMorph_%s-vertices">\n' % (rmesh.name, name) +
        '          <input semantic="POSITION" source="#%sMeshMorph_%s-positions"/>\n' % (rmesh.name, name) +
        '        </vertices>\n' +
        '        <polylist count="%d">\n' % nFaces +
        '          <input semantic="VERTEX" source="#%sMeshMorph_%s-vertices" offset="0"/>\n' % (rmesh.name, name) +
        #'          <input semantic="NORMAL" source="#%sMeshMorph_%s-normals" offset="1"/>\n' % (rmesh.name, name) +
        '          <vcount>')

    fp.write( ''.join(["4 " for fv in fvert]) )

    fp.write('\n' +
        '          </vcount>\n' +
        '          <p>')

    fp.write( ''.join([("%d %d %d %d " % (fv[0], fv[1], fv[2], fv[3])) for fv in fvert]) )

    fp.write('\n' +
        '          </p>\n' +
        '        </polylist>\n' +
        '      </mesh>\n' +
        '    </geometry>\n')
    progress(1)


#
#   writePolygons(fp, rmesh, config):
#   writePolylist(fp, rmesh, config):
#
'''
def writePolygons(fp, rmesh, config):
    fvert = rmesh.getFvert()
    fuvs = rmesh.getFuvs()

    fp.write(
        '        <polygons count="%d">\n' % len(fvert) +
        '          <input offset="0" semantic="VERTEX" source="#%s-Vertex"/>\n' % rmesh.name +
        '          <input offset="1" semantic="NORMAL" source="#%s-Normals"/>\n' % rmesh.name +
        '          <input offset="2" semantic="TEXCOORD" source="#%s-UV"/>\n' % rmesh.name)

    for fn,fvs in enumerate(fvert):
        fuv = fuvs[fn]
        fp.write('          <p>')
        for n,vn in enumerate(fvs):
            fp.write("%d %d %d " % (vn, vn, fuv[n]))
        fp.write('</p>\n')

    fp.write('\n' +
        '        </polygons>\n')
    return
'''

def writePolylist(fp, rmesh, config):
    progress = Progress(2)

    fvert = rmesh.getFvert()
    nFaces = len(fvert)

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

    fp.write( ''.join(["4 " for fv in fvert]) )

    fp.write('\n' +
        '          </vcount>\n'
        '          <p>')
    progress.step()

    fuvs = rmesh.getFuvs()

    for fn,fv in enumerate(fvert):
        fuv = fuvs[fn]
        if config.useNormals:
            fp.write( ''.join([("%d %d %d " % (fv[n], fn, fuv[n])) for n in range(4)]) )
        else:
            fp.write( ''.join([("%d %d " % (fv[n], fuv[n])) for n in range(4)]) )

    fp.write(
        '          </p>\n' +
        '        </polylist>\n')
    progress.step()

#
#   checkFaces(rmesh, nVerts, nUvVerts):
#

def checkFaces(rmesh, nVerts, nUvVerts):
    fvert = rmesh.getFvert()
    fuvs = rmesh.getFuvs()
    for fn,fvs in enumerate(fvert):
        for n,vn in enumerate(fvs):
            uv = fuvs[fn][n]
            if vn > nVerts:
                raise NameError("v %d > %d" % (vn, nVerts))
            if uv > nUvVerts:
                raise NameError("uv %d > %d" % (uv, nUvVerts))


