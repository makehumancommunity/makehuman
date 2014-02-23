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


class DaeConfig(Config):
    def __init__(self, exporter):
        from armature.options import ArmatureOptions

        Config.__init__(self)
        self.selectedOptions(exporter)

        self.useRelPaths = True
        self.useNormals = True

        self.expressions = False
        #self.expressions = exporter.expressions.selected
        self.useCustomTargets = False
        #self.useCustomTargets = exporter.useCustomTargets.selected
        self.useTPose = False
        #self.useTPose = exporter.useTPose.selected

        self.yUpFaceZ = exporter.yUpFaceZ.selected
        self.yUpFaceX = exporter.yUpFaceX.selected
        self.zUpFaceNegY = exporter.zUpFaceNegY.selected
        self.zUpFaceX = exporter.zUpFaceX.selected

        self.localY = True  # exporter.localY.selected
        self.localX = False  # exporter.localX.selected
        self.localG = False  # exporter.localG.selected

        self.rigOptions = exporter.getRigOptions()
        if not self.rigOptions:
            return
            self.rigOptions = ArmatureOptions()
        self.rigOptions.setExportOptions(
            useExpressions = self.expressions,
            useTPose = self.useTPose,
        )



class ExporterCollada(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Collada (dae)"
        self.filter = "Collada (*.dae)"
        self.fileExtension = "dae"
        self.orderPriority = 70.0

    def build(self, options, taskview):
        Exporter.build(self, options, taskview)
        #self.expressions     = options.addWidget(gui.CheckBox("Expressions", False))
        #self.useCustomTargets = options.addWidget(gui.CheckBox("Custom targets", False))
        #self.useTPose = options.addWidget(gui.CheckBox("T-pose", False))

        orients = []
        self.yUpFaceZ = options.addWidget(gui.RadioButton(orients, "Y up, face Z", True))
        self.yUpFaceX = options.addWidget(gui.RadioButton(orients, "Y up, face X", False))
        self.zUpFaceNegY = options.addWidget(gui.RadioButton(orients, "Z up, face -Y", False))
        self.zUpFaceX = options.addWidget(gui.RadioButton(orients, "Z up, face X", False))

        #csyses = []
        #self.localY = options.addWidget(gui.RadioButton(csyses, "Local Y along bone", True))
        #self.localX = options.addWidget(gui.RadioButton(csyses, "Local X along bone", False))
        #self.localG = options.addWidget(gui.RadioButton(csyses, "Local = Global", False))

    def export(self, human, filename):
        from .mh2collada import exportCollada
        self.taskview.exitPoseMode()
        exportCollada(human, filename("dae"), DaeConfig(self))
        self.taskview.enterPoseMode()


def load(app):
    app.addExporter(ExporterCollada())

def unload(app):
    pass
