#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

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

Exporter plugin for the Ogre3d mesh format.
"""

import gui3d
import gui
import mh2ogre
from export import Exporter
from exportutils.config import Config

class OgreConfig(Config):

    def __init__(self):
        Config.__init__(self)
        self.useRelPaths = True

    @property
    def subdivide(self):
        return self.human.isSubdivided()

class ExporterOgre(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Ogre3D"
        self.filter = "Ogre3D Mesh XML (*.mesh.xml)"
        self.fileExtension = "mesh.xml"

    def export(self, human, filename):
        reload(mh2ogre) # TODO ?
        cfg = self.getConfig()
        cfg.setHuman(human)
        mh2ogre.exportOgreMesh(filename("mesh.xml"), cfg)

    def build(self, options, taskview):
        self.taskview     = taskview
        self.feetOnGround = options.addWidget(gui.CheckBox("Feet on ground", True))
        #self.scales       = self.addScales(options)  # TODO reintroduce scales?

    def getConfig(self):
        cfg = OgreConfig()
        cfg.useTPose          = False # self.useTPose.selected
        cfg.feetOnGround      = self.feetOnGround.selected
        cfg.scale,cfg.unit    = self.taskview.getScale()

        return cfg

    def onShow(self, exportTaskView):
        exportTaskView.scaleBox.hide()

    def onHide(self, exportTaskView):
        exportTaskView.scaleBox.show()

def load(app):
    app.addExporter(ExporterOgre())

def unload(app):
    pass

