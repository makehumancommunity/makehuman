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
import exportutils
import posemode
import log

from . import fbx_utils
from . import fbx_header
from . import fbx_skeleton
from . import fbx_mesh
from . import fbx_deformer
from . import fbx_material
from . import fbx_anim


def exportFbx(human, filepath, config):
    from armature.armature import setupArmature

    #posemode.exitPoseMode()
    #posemode.enterPoseMode()

    G.app.progress(0, text="Preparing")

    config.setHuman(human)
    config.setupTexFolder(filepath)

    log.message("Write FBX file %s" % filepath)

    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])
    amt = setupArmature(name, human, config.rigOptions)
    rawTargets = exportutils.collect.readTargets(human, config)
    rmeshes = exportutils.collect.setupMeshes(
        name,
        human,
        amt=amt,
        config=config,
        rawTargets=rawTargets)

    G.app.progress(0.5, text="Exporting %s" % filepath)

    fp = codecs.open(filepath, "w", encoding="utf-8")
    fbx_utils.resetId()
    fbx_utils.setAbsolutePath(filepath)
    fbx_header.writeHeader(fp, filepath)

    nVertexGroups,nShapes = fbx_deformer.getObjectCounts(rmeshes)
    fbx_header.writeObjectDefs(fp, rmeshes, amt, config)
    fbx_skeleton.writeObjectDefs(fp, rmeshes, amt)
    fbx_mesh.writeObjectDefs(fp, rmeshes, amt, nShapes)
    fbx_deformer.writeObjectDefs(fp, rmeshes, amt)
    if config.useMaterials:
        fbx_material.writeObjectDefs(fp, rmeshes, amt)
    #fbx_anim.writeObjectDefs(fp, rmeshes, amt)
    fp.write('}\n\n')

    fbx_header.writeObjectProps(fp, rmeshes, amt)
    if amt:
        fbx_skeleton.writeObjectProps(fp, rmeshes, amt, config)
    fbx_mesh.writeObjectProps(fp, rmeshes, amt, config)
    fbx_deformer.writeObjectProps(fp, rmeshes, amt, config)
    if config.useMaterials:
        fbx_material.writeObjectProps(fp, rmeshes, amt, config)
    #fbx_anim.writeObjectProps(fp, rmeshes, amt)
    fp.write('}\n\n')

    fbx_utils.startLinking()
    fbx_header.writeLinks(fp, rmeshes, amt)
    if amt:
        fbx_skeleton.writeLinks(fp, rmeshes, amt)
    fbx_mesh.writeLinks(fp, rmeshes, amt)
    fbx_deformer.writeLinks(fp, rmeshes, amt)
    if config.useMaterials:
        fbx_material.writeLinks(fp, rmeshes, amt)
    #fbx_anim.writeLinks(fp, rmeshes, amt)
    fp.write('}\n\n')

    fbx_header.writeTakes(fp)
    fp.close()

    G.app.progress(1)
    #posemode.exitPoseMode()
    log.message("%s written" % filepath)


