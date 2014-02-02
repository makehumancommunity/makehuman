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
Exports proxy mesh to obj

"""

import wavefront
import os
import exportutils
from progress import Progress

#
#    exportObj(human, filepath, config):
#

def exportObj(human, filepath, config=None):
    progress = Progress(0, None)
    if config is None:
        config = exportutils.config.Config()
    config.setHuman(human)
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    progress(0, 0.3, "Collecting Objects")
    rmeshes = exportutils.collect.setupMeshes(
        name,
        human,
        config=config,
        subdivide=config.subdivide)

    progress(0.3, 0.99, "Writing Objects")
    objects = [rmesh.object for rmesh in rmeshes]
    wavefront.writeObjFile(filepath, objects, True, config)

    progress(1.0, None, "OBJ Export finished. Output file: %s" % filepath)
