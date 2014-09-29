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

# Access to submodules for derived mhx exporters.
# The idea is that I can use a custom mhx exporter
# for experimentation, without affecting official
# MH code. This is somewhat tricky because
# import 9_export_mhx
# yields a syntax error.
from . import mhx_main
from . import mhx_mesh
from . import mhx_materials
from . import mhx_armature
from . import mhx_pose
from . import mhx_proxy
from . import mhx_writer
from . import mhx_rigify

class MhxConfig(Config):

    def __init__(self):
        Config.__init__(self)
        self.scale,self.unit =      (1, "decimeter")
        self.useRelPaths =          True
        self.useAdvancedMHX =       False
        self.useRigify =            False
        self.useRotationLimits =    False

        self.feetOnGround =         True
        self.expressions =          False
        self.useCustomTargets =     False

    def getRigOptions(self):
        if self.useRigify:
            from .mhx_rigify import RigifyOptions
            return RigifyOptions(self)

        rigOptions = super(MhxConfig, self).getRigOptions()
        if rigOptions is None:
            # No rig is selected from skeleton library, use custom MHX rig
            from armature.options import ArmatureOptions
            self.useAdvancedMHX = True  # TODO this is ugly, a getter modifying the state of the object, probably should set rigOptions.useAdvancedMHX
            rigOptions = ArmatureOptions()
            rigOptions.loadPreset("data/mhx/advanced.json", None)

            rigOptions.setExportOptions(
                useCustomShapes = "all",
                useConstraints = True,
                useBoneGroups = True,
                useLocks = True,
                useRotationLimits = self.useRotationLimits,
                useCorrectives = False,
                useExpressions = self.expressions,
                useLeftRight = False,
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
        self.feetOnGround   = options.addWidget(gui.CheckBox("Feet on ground", True))
        self.useRotationLimits   = options.addWidget(gui.CheckBox("Rotation limits", False))
        self.useRigify      = options.addWidget(gui.CheckBox("Export for Rigify", False))

    def getConfig(self):
        """
        Construct config object from GUI settings
        """
        cfg = MhxConfig()
        cfg.scale, cfg.unit = self.taskview.getScale()

        cfg.feetOnGround = self.feetOnGround.selected

        cfg.useRigify = self.useRigify.selected
        cfg.useRotationLimits = self.useRotationLimits.selected

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
