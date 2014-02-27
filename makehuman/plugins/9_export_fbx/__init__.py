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

TODO
"""

import gui
from export import Exporter
from exportutils.config import Config


class FbxConfig(Config):

    def __init__(self, exporter):
        from armature.options import ArmatureOptions

        Config.__init__(self)
        self.selectedOptions(exporter)

        self.useRelPaths     = False
        self.expressions = False    #exporter.expressions.selected
        self.useCustomTargets = False   #exporter.useCustomTargets.selected
        self.useMaterials    = True # for debugging

        # Used by Collada, needed for armature access
        self.useTPose = False

        self.yUpFaceZ = True
        self.yUpFaceX = False
        self.zUpFaceNegY = False
        self.zUpFaceX = False

        self.localY = True
        self.localX = False
        self.localG = False

        self.rigOptions = exporter.getRigOptions()
        if not self.rigOptions:
            return
        self.rigOptions.setExportOptions(
            useExpressions = self.expressions,
            useTPose = self.useTPose,
            useLeftRight = False,
        )



    def __repr__(self):
        return("<FbxConfig %s e %s>" % (
            self.rigOptions.rigtype, self.expressions))


class ExporterFBX(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Filmbox (fbx)"
        self.filter = "Filmbox (*.fbx)"
        self.fileExtension = "fbx"
        self.orderPriority = 80.0

    def build(self, options, taskview):
        Exporter.build(self, options, taskview)
        #self.expressions     = options.addWidget(gui.CheckBox("Expressions", False))
        #self.useCustomTargets = options.addWidget(gui.CheckBox("Custom targets", False))

    def export(self, human, filename):
        from . import mh2fbx
        self.taskview.exitPoseMode()
        mh2fbx.exportFbx(human, filename("fbx"), FbxConfig(self))
        self.taskview.enterPoseMode()


def load(app):
    app.addExporter(ExporterFBX())

def unload(app):
    pass
