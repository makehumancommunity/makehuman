#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

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
Fbx exporter

"""

import os.path
import sys
import codecs

from core import G
import log

from . import fbx_utils
from . import fbx_header
from . import fbx_skeleton
from . import fbx_mesh
from . import fbx_deformer
from . import fbx_material
from . import fbx_anim

import skeleton


def exportFbx(filepath, config):
    G.app.progress(0, text="Preparing")

    human = config.human
    config.setupTexFolder(filepath)

    log.message("Write FBX file %s" % filepath)

    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    # Collect objects, scale meshes and filter out hidden faces/verts, scale rig
    objects = human.getObjects(excludeZeroFaceObjs=True)
    meshes = [obj.mesh.clone(config.scale, True) for obj in objects]
    skel = human.getSkeleton()
    if skel:
        skel = skel.scaled(config.scale)

    # Set mesh names
    for mesh in meshes:
        mesh.name = fbx_utils.getMeshName(mesh, skel)

    useAnim = False
    if useAnim:
        # TODO allow exporting poseunits
        action = None
    else:
        action = None

    G.app.progress(0.5, text="Exporting %s" % filepath)

    fp = codecs.open(filepath, "w", encoding="utf-8")
    fbx_utils.resetId()  # Reset global ID generator
    fbx_utils.setAbsolutePath(filepath)
    fbx_header.writeHeader(fp, filepath)

    # Generate bone weights for all meshes up front so they can be reused for all
    if skel:
        rawWeights = human.getVertexWeights()  # Basemesh weights
        for mesh in meshes:
            if mesh.object.proxy:
                # Transfer weights to proxy
                parentWeights = mesh.object.proxy.getVertexWeights(rawWeights)
            else:
                parentWeights = rawWeights
            # Transfer weights to face/vert masked and/or subdivided mesh
            weights = mesh.getVertexWeights(parentWeights)

            # Attach these vertexWeights to the mesh to pass them around the
            # exporter easier, the cloned mesh is discarded afterwards, anyway
            mesh.vertexWeights = weights
    else:
        # Attach trivial weights to the meshes
        for mesh in meshes:
            mesh.vertexWeights = None

    # TODO if "shapes" need to be exported, attach them to meshes in a similar way

    nVertexGroups, nShapes = fbx_deformer.getObjectCounts(meshes)
    fbx_header.writeObjectDefs(fp, meshes, skel, action, config)
    fbx_skeleton.writeObjectDefs(fp, meshes, skel)
    fbx_mesh.writeObjectDefs(fp, meshes, nShapes)
    fbx_deformer.writeObjectDefs(fp, meshes, skel)
    if config.useMaterials:
        fbx_material.writeObjectDefs(fp, meshes)
    if useAnim:
        fbx_anim.writeObjectDefs(fp, action)
    fp.write('}\n\n')

    fbx_header.writeObjectProps(fp)
    if skel:
        fbx_skeleton.writeObjectProps(fp, skel, config)
    fbx_mesh.writeObjectProps(fp, meshes, config)
    fbx_deformer.writeObjectProps(fp, meshes, skel, config)
    if config.useMaterials:
        fbx_material.writeObjectProps(fp, meshes, config)
    if useAnim:
        fbx_anim.writeObjectProps(fp, action, skel, config)
    fp.write('}\n\n')

    fbx_utils.startLinking()
    fbx_header.writeLinks(fp)
    if skel:
        fbx_skeleton.writeLinks(fp, skel)
    fbx_mesh.writeLinks(fp, meshes)
    fbx_deformer.writeLinks(fp, meshes, skel)
    if config.useMaterials:
        fbx_material.writeLinks(fp, meshes)
    if useAnim:
        fbx_anim.writeLinks(fp, action)
    fp.write('}\n\n')

    fbx_anim.writeTakes(fp, action)
    fp.close()

    G.app.progress(1)
    log.message("%s written" % filepath)


