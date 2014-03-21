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
