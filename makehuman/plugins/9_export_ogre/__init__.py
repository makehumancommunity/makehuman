#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2020

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

Exporter plugin for the Ogre3d mesh format.
"""

from . import mh2ogre
from export import Exporter, ExportConfig
import importlib

class OgreConfig(ExportConfig):

    def __init__(self):
        ExportConfig.__init__(self)
        self.useRelPaths = True
        self.exportShaders = False  # TODO add support for this

    @property
    def subdivide(self):
        return self.human.isSubdivided()

class ExporterOgre(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Ogre3D"
        self.filter = "Ogre3D Mesh XML (*.mesh.xml)"
        self.fileExtension = "mesh.xml"
        self.orderPriority = 60.0

    def export(self, human, filename):
        importlib.reload(mh2ogre) # TODO ?
        cfg = self.getConfig()
        cfg.setHuman(human)
        mh2ogre.exportOgreMesh(filename("mesh.xml"), cfg)

    def build(self, options, taskview):
        import gui
        self.taskview     = taskview
        self.feetOnGround = options.addWidget(gui.CheckBox("Feet on ground", True))

    def getConfig(self):
        cfg = OgreConfig()
        cfg.feetOnGround      = self.feetOnGround.selected
        cfg.scale,cfg.unit    = self.taskview.getScale()

        return cfg

def load(app):
    app.addExporter(ExporterOgre())

def unload(app):
    pass

