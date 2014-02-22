#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers, Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import gui3d
import gui
from progress import Progress
from export import Exporter
from exportutils.config import Config

class MD5Config(Config):

    def __init__(self, exporter):
        Config.__init__(self)
        self.selectedOptions(exporter)
        self.useRelPaths = True

    def selectedOptions(self, exporter):
        self.smooth = self.subdivide = gui3d.app.selectedHuman.isSubdivided()

        return self


class ExporterMD5(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "MD5"
        self.filter = "MD5 (*.md5)"
        self.fileExtension = "md5"

    def build(self, options, taskview):
        self.taskview       = taskview

    def export(self, human, filename):
        from . import mh2md5
        cfg = MD5Config(self)
        cfg.selectedOptions(self)

        progress = Progress.begin() (0, 1)
        mh2md5.exportMd5(human, filename("md5mesh"), cfg)

    def onShow(self, exportTaskView):
        exportTaskView.scaleBox.hide()

    def onHide(self, exportTaskView):
        exportTaskView.scaleBox.show()

def load(app):
    app.addExporter(ExporterMD5())

def unload(app):
    pass
