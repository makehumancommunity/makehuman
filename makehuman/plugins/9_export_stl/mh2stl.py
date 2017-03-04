#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Export to stereolithography format.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius

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

This module implements a plugin to export MakeHuman mesh to stereolithography format.
See http://en.wikipedia.org/wiki/STL_(file_format) for information on the format.

Requires:

- base modules

"""

__docformat__ = 'restructuredtext'

import os
import struct
import numpy as np
import math
from progress import Progress

# TODO perhaps add scale option

def exportStlAscii(filepath, config, exportJoints = False):
    """
    This function exports MakeHuman mesh to stereolithography ascii format.

    Parameters
    ----------

    human:
      *Human*.  The object whose information is to be used for the export.
    filepath:
      *string*.  The filepath of the file to export the object to.
    config:
      *Config*.  Export configuration.
    """

    progress = Progress(0, None)

    human = config.human
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    objects = human.getObjects(True)
    meshes = [o.mesh.clone(1,True) for o in objects]

    from codecs import open
    fp = open(filepath, 'w', encoding="utf-8")
    solid = name.replace(' ','_')
    fp.write('solid %s\n' % solid)

    progress(0.3, 0.99, "Writing Objects")
    objprog = Progress(len(meshes))

    def chunked_enumerate(chunk_size, offs, list_):
        return zip(range(offs,offs+chunk_size), list_[offs:offs+chunk_size])

    for mesh in meshes:
        coord = config.scale*mesh.coord + config.offset
        offs = 0
        chunk_size = 2000   # The higher the chunk size, the faster, but setting this too high can run into memory errors on some machines
        meshprog = Progress(math.ceil( float(len(mesh.fvert)) / chunk_size ))
        while(offs < len(mesh.fvert)):
            fp.write("".join( [(
                'facet normal %f %f %f\n' % tuple(mesh.fnorm[fn]) +
                '\touter loop\n' +
                '\t\tvertex %f %f %f\n' % tuple(coord[fv[0]]) +
                '\t\tvertex %f %f %f\n' % tuple(coord[fv[1]]) +
                '\t\tvertex %f %f %f\n' % tuple(coord[fv[2]]) +
                '\tendloop\n' +
                '\tendfacet\n' +
                'facet normal %f %f %f\n' % tuple(mesh.fnorm[fn]) +
                '\touter loop\n' +
                '\t\tvertex %f %f %f\n' % tuple(coord[fv[2]]) +
                '\t\tvertex %f %f %f\n' % tuple(coord[fv[3]]) +
                '\t\tvertex %f %f %f\n' % tuple(coord[fv[0]]) +
                '\tendloop\n' +
                '\tendfacet\n'
                ) for fn,fv in chunked_enumerate(offs, chunk_size, mesh.fvert)] ))
            fp.flush()
            os.fsync(fp.fileno())
            offs += chunk_size
            meshprog.step()
        meshprog.finish()
        objprog.step()

    fp.write('endsolid %s\n' % solid)
    fp.close()
    progress(1, None, "STL export finished. Exported file: %s", filepath)


def exportStlBinary(filepath, config, exportJoints = False):
    """
    filepath:
      *string*.  The filepath of the file to export the object to.
    config:
      *Config*.  Export configuration.
    """

    progress = Progress(0, None)

    human = config.human
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    objects = human.getObjects(True)
    meshes = [o.mesh.clone(1,True) for o in objects]

    fp = open(filepath, 'wb')
    fp.write('\x00' * 80)
    fp.write(struct.pack('<I', 0))
    count = 0

    progress(0.3, 0.99, "Writing Objects")
    objprog = Progress(len(meshes))
    for mesh in meshes:
        coord = config.scale * mesh.coord + config.offset
        for fn,fv in enumerate(mesh.fvert):
            fno = mesh.fnorm[fn]
            co = coord[fv]

            fp.write(struct.pack('<fff', fno[0], fno[1], fno[2]))
            fp.write(struct.pack('<fff', co[0][0], co[0][1], co[0][2]))
            fp.write(struct.pack('<fff', co[1][0], co[1][1], co[1][2]))
            fp.write(struct.pack('<fff', co[2][0], co[2][1], co[2][2]))
            fp.write(struct.pack('<H', 0))
            count += 1

            fp.write(struct.pack('<fff', fno[0], fno[1], fno[2]))
            fp.write(struct.pack('<fff', co[2][0], co[2][1], co[2][2]))
            fp.write(struct.pack('<fff', co[3][0], co[3][1], co[3][2]))
            fp.write(struct.pack('<fff', co[0][0], co[0][1], co[0][2]))
            fp.write(struct.pack('<H', 0))
            count += 1
        objprog.step()

    fp.seek(80)
    fp.write(struct.pack('<I', count))
    progress(1, None, "STL export finished. Exported file: %s", filepath)

