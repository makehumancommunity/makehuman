#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

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

class ObjConfig(ExportConfig):

    def __init__(self):
        ExportConfig.__init__(self)
        self.useRelPaths = True
        self.useNormals = False
        self.hiddenGeom = False


class ExporterOBJ(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Wavefront obj"
        self.filter = "Wavefront (*.obj)"
        self.fileExtension = "obj"
        self.orderPriority = 60.0

    def build(self, options, taskview):
        import gui
        Exporter.build(self, options, taskview)
        self.useNormals = options.addWidget(gui.CheckBox("Normals", False))
        self.hiddenGeom = options.addWidget(gui.CheckBox("Helper geometry", False))

    def export(self, human, filename):
        from progress import Progress
        from . import mh2obj

        progress = Progress.begin() (0, 1)
        cfg = self.getConfig()
        cfg.setHuman(human)
        mh2obj.exportObj(filename("obj"), cfg)

    def getConfig(self):
        cfg = ObjConfig()
        cfg.useNormals = self.useNormals.selected

        cfg.feetOnGround      = self.feetOnGround.selected
        cfg.scale,cfg.unit    = self.taskview.getScale()
        cfg.hiddenGeom        = self.hiddenGeom.selected

        return cfg

def load(app):
    app.addExporter(ExporterOBJ())

def unload(app):
    pass
