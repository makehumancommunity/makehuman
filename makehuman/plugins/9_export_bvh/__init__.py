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

BVH exporter.
Supports exporting of selected skeleton and animations in BVH format.
"""

import bvh

from export import Exporter
from exportutils.config import Config
import gui
import gui3d
import log

import os

# TODO add options such as z-up, feetonground, etc

class BvhConfig(Config):

    def __init__(self, exporter):
        Config.__init__(self)
        self.selectedOptions(exporter)
        self.useRelPaths = True

    def selectedOptions(self, exporter):
        self.scale,self.unit    = exporter.taskview.getScale()
        return self

class ExporterBVH(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.group = "rig"
        self.name = "Biovision Hierarchy BVH"
        self.filter = "Biovision Hierarchy (*.bvh)"
        self.fileExtension = "bvh"

    def build(self, options, taskview):
        self.taskview       = taskview
        self.exportAnimations = options.addWidget(gui.CheckBox("Animations", True))

    def export(self, human, filename):
        if not human.getSkeleton():
            gui3d.app.prompt('Error', 'You did not select a skeleton from the library.', 'OK')
            return

        skel = human.getSkeleton()
        cfg = BvhConfig(self)

        if self.exportAnimations and len(human.animated.getAnimations()) > 0:
            baseFilename = os.path.splitext(filename("bvh"))[0]
            for animName in human.animated.getAnimations():
                fn = baseFilename + "_%s.bvh" % animName
                log.message("Exporting file %s.", fn)
                bvhData = bvh.createFromSkeleton(skel, human.animated.getAnimation(animName))
                if cfg.scale != 1:
                    bvhData.scale(cfg.scale)
                bvhData.writeToFile(fn)
        else:
            fn = filename("bvh")
            log.message("Exporting file %s.", fn)
            bvhData = bvh.createFromSkeleton(skel)
            if cfg.scale != 1:
                bvhData.scale(cfg.scale)
            bvhData.writeToFile(fn)

    def onShow(self, exportTaskView):
        exportTaskView.scaleBox.hide()

    def onHide(self, exportTaskView):
        exportTaskView.scaleBox.show()

def load(app):
    app.addExporter(ExporterBVH())

def unload(app):
    pass
