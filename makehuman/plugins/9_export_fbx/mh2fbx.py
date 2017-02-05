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
Fbx exporter

"""

import os.path
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


def exportFbx(filepath, config):
    G.app.progress(0, text="Preparing")

    human = config.human
    config.setupTexFolder(filepath)

    log.message("Write FBX file %s" % filepath)

    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    # Collect objects, scale meshes and filter out hidden faces/verts, scale rig
    objects = human.getObjects(excludeZeroFaceObjs=not config.hiddenGeom)
    meshes = [obj.mesh.clone(config.scale, filterMaskedVerts=not config.hiddenGeom) for obj in objects]

    if config.hiddenGeom:
        import numpy as np
        # Disable the face masking on copies of the input meshes
        for m in meshes:
            # Disable the face masking on the mesh
            face_mask = np.ones(m.face_mask.shape, dtype=bool)
            m.changeFaceMask(face_mask)
            m.calcNormals()
            m.updateIndexBuffer()

    skel = human.getSkeleton()
    if skel:
        if config.scale != 1:
            skel = skel.scaled(config.scale)  # TODO perhaps create a skeleton.transformed() just like for mesh

    # Set mesh names
    for mesh in meshes:
        mesh.name = fbx_utils.getMeshName(mesh, name)

    useAnim = False
    if useAnim:
        # TODO allow exporting poseunits
        action = None
    else:
        action = None

    G.app.progress(0.5, text="Exporting %s" % filepath)

    if config.binary:
        import fbx_binary
        root = fbx_binary.elem_empty(None, b"")
        fp = root
    else:
        fp = codecs.open(filepath, "w", encoding="utf-8")

    fbx_utils.resetId()  # Reset global ID generator
    fbx_utils.setAbsolutePath(filepath)  # TODO fix this

    # 1) FBX Header, documents and references
    fbx_header.writeHeader(fp, filepath, config)

    # Generate bone weights for all meshes up front so they can be reused for all
    if skel:
        rawWeights = human.getVertexWeights(human.getSkeleton())  # Basemesh weights
        for mesh in meshes:
            if mesh.object.proxy:
                # Transfer weights to proxy
                parentWeights = mesh.object.proxy.getVertexWeights(rawWeights, human.getSkeleton())
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

    # 2) FBX template definitions
    # GlobalSettings template definition
    fbx_header.writeObjectDefs(fp, meshes, skel, action, config)
    # Skeleton template definition
    fbx_skeleton.writeObjectDefs(fp, meshes, skel, config)
    # Material template definition
    if config.useMaterials:
        fbx_material.writeObjectDefs(fp, meshes, config)
    # Objects template definition
    fbx_mesh.writeObjectDefs(fp, meshes, nShapes, config)
    # Skin deformer template definition
    fbx_deformer.writeObjectDefs(fp, meshes, skel, config)
    # Animation template definition
    if useAnim:
        fbx_anim.writeObjectDefs(fp, action, config)
    if not config.binary: fp.write('}\n\n')

    # 3) FBX object properties (the actual data)
    fbx_header.writeObjectProps(fp, config)
    if skel:
        fbx_skeleton.writeObjectProps(fp, skel, config)
    fbx_mesh.writeObjectProps(fp, meshes, config)
    if config.useMaterials:
        fbx_material.writeObjectProps(fp, meshes, config)
    fbx_deformer.writeObjectProps(fp, meshes, skel, config)
    if useAnim:
        # TODO support binary FBX animations export
        fbx_anim.writeObjectProps(fp, action, skel, config)
    if not config.binary: fp.write('}\n\n')

    # 4) FBX node links
    fbx_utils.startLinking()
    fbx_header.writeLinks(fp, config)
    if skel:
        fbx_skeleton.writeLinks(fp, skel, config)
    fbx_mesh.writeLinks(fp, meshes, config)
    fbx_deformer.writeLinks(fp, meshes, skel, config)
    if config.useMaterials:
        fbx_material.writeLinks(fp, meshes, config)
    if useAnim:
        fbx_anim.writeLinks(fp, action, config, config)
    if not config.binary: fp.write('}\n\n')

    # 5) FBX animations (takes)
    # TODO support binary FBX export
    fbx_anim.writeTakes(fp, action, config)
    if config.binary:
        import encode_bin
        root = fp
        encode_bin.write(filepath, root)
    else:
        fp.close()

    G.app.progress(1)
    log.message("%s written" % filepath)
