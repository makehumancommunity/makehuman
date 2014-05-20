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

MakeHuman to Collada (MakeHuman eXchange format) exporter. Collada files can be loaded into
Blender by collada_import.py.

TODO
"""

import os.path
import time
import codecs
import log

import gui3d
import exportutils

from progress import Progress

from . import dae_materials
from . import dae_controller
from . import dae_geometry
from . import dae_node

#
#    Size of end bones = 1 mm
#
Delta = [0,0.01,0]

#
# exportCollada(human, filepath, config):
#

def exportCollada(filepath, config):
    progress = Progress()

    time1 = time.clock()
    human = config.human
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    progress(0, 0.5, "Preparing")
    #rawTargets = exportutils.collect.readTargets(human, config)    # TODO what is this used for?

    objects = human.getObjects()
    # Clone meshes with desired scale and hidden faces/vertices filtered out
    meshes = [obj.mesh.clone(config.scale, True) for obj in objects]

    # TODO a shared method for properly naming meshes would be a good idea
    for mesh in meshes:
        if mesh.object.proxy:
            mesh.name = mesh.object.proxy.name
        mesh.name = os.path.splitext(mesh.name)[0]
        mesh.name = name + '-' + config.goodName(mesh.name)

    try:
        progress(0.5, 0.55, "Exporting %s", filepath)

        try:
            fp = codecs.open(filepath, 'w', encoding="utf-8")
            log.message("Writing Collada file %s" % filepath)
        except:
            fp = None
            log.error("Unable to open file for writing %s" % filepath)

        date = time.strftime(u"%a, %d %b %Y %H:%M:%S +0000".encode('utf-8'), time.localtime()).decode('utf-8')
        # TODO revise to make this enum-like
        if config.yUpFaceZ or config.yUpFaceX:
            upvector = "Y_UP"
        else:
            upvector = "Z_UP"
        fp.write('<?xml version="1.0" encoding="utf-8"?>\n' +
            '<COLLADA version="1.4.0" xmlns="http://www.collada.org/2005/11/COLLADASchema">\n' +
            '  <asset>\n' +
            '    <contributor>\n' +
            '      <author>www.makehuman.org</author>\n' +
            '    </contributor>\n' +
            '    <created>%s</created>\n' % date +
            '    <modified>%s</modified>\n' % date +
            '    <unit meter="%.4f" name="%s"/>\n' % (0.1/config.scale, config.unit) +
            '    <up_axis>%s</up_axis>\n' % upvector +
            '  </asset>\n')

        progress(0.55, 0.6, "Exporting images")
        dae_materials.writeLibraryImages(fp, objects, config)

        progress(0.6, 0.65, "Exporting effects")
        dae_materials.writeLibraryEffects(fp, objects, config)

        progress(0.65, 0.7, "Exporting materials")
        dae_materials.writeLibraryMaterials(fp, objects, config)

        progress(0.7, 0.75, "Exporting controllers")
        dae_controller.writeLibraryControllers(fp, human, meshes, config)

        progress(0.75, 0.9, "Exporting geometry")
        dae_geometry.writeLibraryGeometry(fp, meshes, config)

        progress(0.9, 0.99, "Exporting scene")
        dae_node.writeLibraryVisualScenes(fp, human, meshes, config)

        fp.write(
            '  <scene>\n' +
            '    <instance_visual_scene url="#Scene"/>\n' +
            '  </scene>\n' +
            '</COLLADA>\n')

        progress(1, None, "Export finished.")
        time2 = time.clock()
        log.message("Wrote Collada file in %g s: %s", time2-time1, filepath)

    finally:
        if fp:
            fp.close()

