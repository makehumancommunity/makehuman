#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import gui
from export import Exporter

class ExporterUV(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.group = "map"
        self.name = "UV map"
        self.filter = "PNG (*.png)"

    def build(self, options, taskview):
        self.uvmapDisplay = options.addWidget(gui.CheckBox("Display on human", False))

    def export(self, human, filename):
        import projection

        dstImg = projection.mapUV()
        filepath = filename("png")
        dstImg.save(filepath)

        if self.uvmapDisplay:
            import log
            human.setTexture(filepath)
            log.message("Enabling shadeless rendering on body")
            human.mesh.setShadeless(True)

def load(app):
    app.addExporter(ExporterUV())

def unload(app):
    pass
