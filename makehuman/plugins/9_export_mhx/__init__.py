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

from export import Exporter
from exportutils.config import Config

from . import mhx_main

class MhxConfig(Config):

    def __init__(self):
        Config.__init__(self)
        self.scale,self.unit =      (1, "decimeter")
        self.useRelPaths =          True
        self.useStandardRig =       True
        self.useNewMHX =            False
        self.useLegacyMHX =         False
        self.useNewRigify =         False
        self.useLegacyRigify =      False
        self.useRotationLimits =    False

        self.feetOnGround =         True
        self.useFaceRig =           True
        self.expressions =          False
        self.useCustomTargets =     False

    def getRigOptions(self):
        from armature.options import ArmatureOptions

        if self.useLegacyRigify or self.useNewRigify:
            rigOptions = ArmatureOptions()
            if self.useLegacyRigify:
                rigOptions.loadPreset("data/mhx/legacy-rigify.json", None)
            else:
                rigOptions.loadPreset("data/mhx/new-rigify.json", None)

            rigOptions.setExportOptions(
                useCustomShapes = "face",
                useConstraints = True,
                useFaceRig = self.useFaceRig,
            )

        elif self.useLegacyMHX or self.useNewMHX:
            rigOptions = ArmatureOptions()
            if self.useLegacyMHX:
                rigOptions.loadPreset("data/mhx/legacy-mhx.json", None)
            else:
                rigOptions.loadPreset("data/mhx/new-mhx.json", None)

            rigOptions.setExportOptions(
                useCustomShapes = "all",
                useConstraints = True,
                useBoneGroups = True,
                useLocks = True,
                useRotationLimits = self.useRotationLimits,
                useFaceRig = self.useFaceRig,
            )

        else:
            rigOptions = super(MhxConfig, self).getRigOptions()
            if rigOptions is None:
                # No rig is selected from skeleton library, use standard MakeHuman rig
                rigOptions = ArmatureOptions()
                rigOptions.loadPreset("data/rigs/makehuman.json", None)

            rigOptions.setExportOptions(
                useFaceRig = self.useFaceRig,
            )

        return rigOptions


class ExporterMHX(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Blender exchange (mhx)"
        self.filter = "Blender Exchange (*.mhx)"
        self.fileExtension = "mhx"
        self.orderPriority = 90.0

    def build(self, options, taskview):
        import gui
        self.taskview       = taskview
        self.useFaceRig   = options.addWidget(gui.CheckBox("Face rig", True))
        self.feetOnGround   = options.addWidget(gui.CheckBox("Feet on ground", True))
        self.useRotationLimits   = options.addWidget(gui.CheckBox("Rotation limits", False))
        #self.expressions    = options.addWidget(gui.CheckBox("Expressions", False))
        #self.useCustomTargets = options.addWidget(gui.CheckBox("Custom targets", False))

        rigs = []
        self.useStandardRig = options.addWidget(gui.RadioButton(rigs, "Standard rig", True))
        self.useNewMHX = options.addWidget(gui.RadioButton(rigs, "MHX rig", False))
        self.useNewRigify = options.addWidget(gui.RadioButton(rigs, "Rigify rig", False))
        #self.useLegacyMHX = options.addWidget(gui.RadioButton(rigs, "Legacy MHX rig", False))
        #self.useLegacyRigify = options.addWidget(gui.RadioButton(rigs, "Legacy Rigify rig", False))

    def getConfig(self):
        """
        Construct config object from GUI settings
        """
        cfg = MhxConfig()
        cfg.scale, cfg.unit = self.taskview.getScale()

        cfg.useFaceRig = self.useFaceRig.selected
        cfg.feetOnGround = self.feetOnGround.selected
        cfg.useRotationLimits = self.useRotationLimits.selected
        cfg.useStandardRig = self.useStandardRig.selected
        cfg.useNewMHX = self.useNewMHX.selected
        cfg.useNewRigify = self.useNewRigify.selected
        #cfg.useLegacyMHX = self.useLegacyMHX.selected
        #cfg.useLegacyRigify = self.useLegacyRigify.selected

        return cfg

    def export(self, human, filename):
        #self.taskview.exitPoseMode()
        cfg = self.getConfig()
        cfg.setHuman(human)
        mhx_main.exportMhx(filename("mhx"), cfg)
        #self.taskview.enterPoseMode()


def load(app):
    app.addExporter(ExporterMHX())

def unload(app):
    pass
