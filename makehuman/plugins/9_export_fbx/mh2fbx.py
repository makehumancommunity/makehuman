#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------
Fbx exporter

"""

import os.path
import sys
import codecs

import gui3d
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

    gui3d.app.progress(0, text="Preparing")

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

    gui3d.app.progress(0.5, text="Exporting %s" % filepath)

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
        fbx_material.writeObjectProps(fp, rmeshes, amt)
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

    gui3d.app.progress(1)
    #posemode.exitPoseMode()
    log.message("%s written" % filepath)


