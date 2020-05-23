#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2020

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

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

BVH exporter.
Supports exporting of selected skeleton and animations in BVH format.
"""

import bvh

from export import Exporter, ExportConfig
import log
from core import G

import os

# TODO add options such as z-up, feetonground, etc

class BvhConfig(ExportConfig):

    def __init__(self):
        ExportConfig.__init__(self)
        self.useRelPaths = True

class ExporterBVH(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.group = "rig"
        self.name = "Biovision Hierarchy BVH"
        self.filter = "Biovision Hierarchy (*.bvh)"
        self.fileExtension = "bvh"

    def build(self, options, taskview):
        import gui
        self.taskview       = taskview
        #self.exportAnimations = options.addWidget(gui.CheckBox("Animations", True))
        self.feetOnGround = options.addWidget(gui.CheckBox("Feet on ground", True))

    def getConfig(self):
        cfg = BvhConfig()
        cfg.feetOnGround      = self.feetOnGround.selected
        cfg.scale,cfg.unit    = self.taskview.getScale()
        #cfg.exportAnimations = self.exportAnimations.selected
        cfg.exportAnimations = False

        return cfg

    def export(self, human, filename):
        if not human.getSkeleton():
            G.app.prompt('Error', 'You did not select a skeleton from the library.', 'OK')
            return

        skel = human.getSkeleton()
        cfg = self.getConfig()
        cfg.setHuman(human)

        if cfg.exportAnimations and len(human.getAnimations()) > 0:
            baseFilename = os.path.splitext(filename("bvh"))[0]
            for animName in human.getAnimations():
                fn = baseFilename + "_%s.bvh" % animName
                log.message("Exporting file %s.", fn)
                bvhData = bvh.createFromSkeleton(skel, human.getAnimation(animName))
                if cfg.scale != 1:
                    bvhData.scale(cfg.scale)
                if cfg.feetOnGround:
                    bvhData.offset(cfg.offset)
                bvhData.writeToFile(fn)
        else:
            fn = filename("bvh")
            log.message("Exporting file %s.", fn)
            if human.isPosed():
                bvhData = bvh.createFromSkeleton(skel, human.getActiveAnimation())
            else:
                bvhData = bvh.createFromSkeleton(skel)
            if cfg.scale != 1:
                bvhData.scale(cfg.scale)
            if cfg.feetOnGround:
                bvhData.offset(cfg.offset)
            bvhData.writeToFile(fn)

def load(app):
    app.addExporter(ExporterBVH())

def unload(app):
    pass
