#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers, Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import gui
from export import Exporter
from exportutils.config import Config

class STLConfig(Config):

    def __init__(self, exporter):
        Config.__init__(self)
        self.selectedOptions(exporter)
        self.useRelPaths = True


class ExporterSTL(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Stereolithography (stl)"
        self.filter = "Stereolithography (*.stl)"
        self.fileExtension = "stl"

    def build(self, options, taskview):
        Exporter.build(self, options, taskview)
        stlOptions = []
        self.stlAscii = options.addWidget(gui.RadioButton(stlOptions,  "Ascii", selected=True))
        self.stlBinary = options.addWidget(gui.RadioButton(stlOptions, "Binary"))

    def export(self, human, filename):
        from . import mh2stl
        from progress import Progress
        progress = Progress.begin() (0, 1)

        if self.stlAscii.selected:
            mh2stl.exportStlAscii(human, filename("stl"), STLConfig(self))
        else:
            mh2stl.exportStlBinary(human, filename("stl"), STLConfig(self))

def load(app):
    app.addExporter(ExporterSTL())

def unload(app):
    pass
