#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Marc Flerackers, Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2019

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

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

class STLConfig(ExportConfig):

    def __init__(self):
        ExportConfig.__init__(self)
        self.useRelPaths = True


class ExporterSTL(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Stereolithography (stl)"
        self.filter = "Stereolithography (*.stl)"
        self.fileExtension = "stl"
        self.orderPriority = 5.0

    def build(self, options, taskview):
        import gui
        Exporter.build(self, options, taskview)
        self.stlBinary = options.addWidget(gui.CheckBox("Binary STL", False))

    def getConfig(self):
        cfg = STLConfig()
        cfg.feetOnGround      = self.feetOnGround.selected
        cfg.scale,cfg.unit    = self.taskview.getScale()
        return cfg

    def export(self, human, filename):
        from . import mh2stl
        from progress import Progress
        progress = Progress.begin() (0, 1)

        cfg = self.getConfig()
        cfg.setHuman(human)
        if not self.stlBinary.selected:
            try:
                mh2stl.exportStlAscii(filename("stl"), cfg)
            except MemoryError:
                log.error("Not enough memory to export the mesh. Try exporting a binary STL or disable mesh smoothing.")
        else:
            mh2stl.exportStlBinary(filename("stl"), cfg)

def load(app):
    app.addExporter(ExporterSTL())

def unload(app):
    pass
