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
