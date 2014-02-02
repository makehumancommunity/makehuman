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

import log
import gui
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

    def __init__(self, exporter):
        from armature.options import ArmatureOptions
        from .mhx_rigify import RigifyOptions

        Config.__init__(self)
        self.scale,self.unit =      exporter.taskview.getScale()
        self.useRelPaths =          True
        self.useAdvancedMHX =       False

        self.feetOnGround =         exporter.feetOnGround.selected
        self.useFaceRig =           False   # exporter.useFaceRig.selected
        self.expressions =          False   #exporter.expressions.selected
        self.useCustomTargets =     False   #exporter.useCustomTargets.selected

        if exporter.useRigify.selected:
            self.rigOptions = RigifyOptions(self)
            return
        else:
            self.rigOptions = exporter.getRigOptions()
            if not self.rigOptions:
                self.useAdvancedMHX = True
                self.rigOptions = ArmatureOptions()
                self.rigOptions.loadPreset("data/mhx/advanced.json", None)

        self.rigOptions.setExportOptions(
            useCustomShapes = True,
            useConstraints = True,
            useBoneGroups = True,
            useLocks = True,
            useRotationLimits = exporter.useRotationLimits.selected,
            useCorrectives = False,
            useFaceRig = self.useFaceRig,
            useExpressions = self.expressions,
            useLeftRight = False,
        )


class ExporterMHX(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Blender exchange (mhx)"
        self.filter = "Blender Exchange (*.mhx)"
        self.fileExtension = "mhx"
        self.orderPriority = 90.0

    def build(self, options, taskview):
        self.taskview       = taskview
        self.feetOnGround   = options.addWidget(gui.CheckBox("Feet on ground", True))
        self.useRotationLimits   = options.addWidget(gui.CheckBox("Rotation limits", False))
        #self.useFaceRig     = options.addWidget(gui.CheckBox("Face rig", True))
        #self.expressions    = options.addWidget(gui.CheckBox("Expressions", False))
        #self.useCustomTargets = options.addWidget(gui.CheckBox("Custom targets", False))
        self.useRigify      = options.addWidget(gui.CheckBox("Export for Rigify", False))


    def export(self, human, filename):
        self.taskview.exitPoseMode()
        mhx_main.exportMhx(human, filename("mhx"), MhxConfig(self))
        self.taskview.enterPoseMode()


def load(app):
    app.addExporter(ExporterMHX())

def unload(app):
    pass
