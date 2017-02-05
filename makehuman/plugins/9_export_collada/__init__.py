#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3

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


Abstract
--------

TODO
"""

from export import Exporter, ExportConfig


class DaeConfig(ExportConfig):
    def __init__(self):
        ExportConfig.__init__(self)

        self.useRelPaths = True
        self.useNormals = True

        self.yUpFaceZ = True
        self.yUpFaceX = False
        self.zUpFaceNegY = False
        self.zUpFaceX = False

        self.localY = True
        self.localX = False
        self.localG = False

        self.facePoseUnits = False
        self.hiddenGeom = False

    # TODO preferably these are used (perhaps as enum) instead of the bools above
    # TODO move these to export Config super class
    @property
    def meshOrientation(self):
        if self.yUpFaceZ:
            return 'yUpFaceZ'
        if self.yUpFaceX:
            return 'yUpFaceX'
        if self.zUpFaceNegY:
            return 'zUpFaceNegY'
        if self.zUpFaceX:
            return 'zUpFaceX'
        return 'yUpFaceZ'

    @property
    def localBoneAxis(self):
        if self.localY:
            return 'y'
        if self.localX:
            return 'x'
        if self.localG:
            return 'g'
        return 'y'

    @property
    def upAxis(self):
        if self.meshOrientation.startswith('yUp'):
            return 1
        elif self.meshOrientation.startswith('zUp'):
            return 2

    '''
    @property
    def offsetVect(self):
        result = [0.0, 0.0, 0.0]
        result[self.upAxis] = self.offset
        return result
    '''

class ExporterCollada(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Collada (dae)"
        self.filter = "Collada (*.dae)"
        self.fileExtension = "dae"
        self.orderPriority = 95.0

    def build(self, options, taskview):
        import gui
        Exporter.build(self, options, taskview)

        self.hiddenGeom = options.addWidget(gui.CheckBox("Helper geometry", False))
        self.facePoseUnits = options.addWidget(gui.CheckBox("Facial pose-units", False))

        orients = []
        box = options.addWidget(gui.GroupBox("Orientation"))
        self.yUpFaceZ = box.addWidget(gui.RadioButton(orients, "Y up, face Z", True))
        self.yUpFaceX = box.addWidget(gui.RadioButton(orients, "Y up, face X", False))
        self.zUpFaceNegY = box.addWidget(gui.RadioButton(orients, "Z up, face -Y", False))
        self.zUpFaceX = box.addWidget(gui.RadioButton(orients, "Z up, face X", False))

        csyses = []
        box = options.addWidget(gui.GroupBox("Bone orientation"))
        self.localY = box.addWidget(gui.RadioButton(csyses, "Along local Y", True))
        self.localX = box.addWidget(gui.RadioButton(csyses, "Along local X", False))
        self.localG = box.addWidget(gui.RadioButton(csyses, "Local = Global", False))

    def export(self, human, filename):
        from .mh2collada import exportCollada
        cfg = self.getConfig()
        cfg.setHuman(human)
        exportCollada(filename("dae"), cfg)

    def getConfig(self):
        cfg = DaeConfig()
        cfg.feetOnGround       = self.feetOnGround.selected
        cfg.scale,cfg.unit    = self.taskview.getScale()

        cfg.yUpFaceZ = self.yUpFaceZ.selected
        cfg.yUpFaceX = self.yUpFaceX.selected
        cfg.zUpFaceNegY = self.zUpFaceNegY.selected
        cfg.zUpFaceX = self.zUpFaceX.selected

        cfg.localY = self.localY.selected
        cfg.localX = self.localX.selected
        cfg.localG = self.localG.selected

        cfg.facePoseUnits = self.facePoseUnits.selected
        cfg.hiddenGeom        = self.hiddenGeom.selected

        return cfg


def load(app):
    app.addExporter(ExporterCollada())

def unload(app):
    pass
