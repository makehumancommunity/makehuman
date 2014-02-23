#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

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

    def __init__(self, exporter):
        Config.__init__(self)
        self.selectedOptions(exporter)
        self.useRelPaths = True

    def selectedOptions(self, exporter):
        self.feetOnGround          = exporter.feetOnGround.selected
        self.subdivide          = gui3d.app.selectedHuman.isSubdivided()

        return self

class ExporterOgre(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Ogre3D"
        self.filter = "Ogre3D Mesh XML (*.mesh.xml)"
        self.fileExtension = "mesh.xml"

    def export(self, human, filename):
        reload(mh2ogre) # TODO ?
        mh2ogre.exportOgreMesh(human, filename("mesh.xml"), OgreConfig(self))

    def build(self, options, taskview):
        self.taskview     = taskview
        self.feetOnGround = options.addWidget(gui.CheckBox("Feet on ground", True))
        #self.scales       = self.addScales(options)  # TODO reintroduce scales?

    def onShow(self, exportTaskView):
        exportTaskView.scaleBox.hide()

    def onHide(self, exportTaskView):
        exportTaskView.scaleBox.show()

def load(app):
    app.addExporter(ExporterOgre())

def unload(app):
    pass
