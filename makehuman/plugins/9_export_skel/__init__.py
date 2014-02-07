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

from export import Exporter

class ExporterSkel(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.group = "rig"
        self.name = "Skeleton (skel)"
        self.filter = "Skeleton (*.skel)"
        self.fileExtension = "skel"

    def build(self, options, taskview):
        pass

    def export(self, human, filename):
        from . import mh2skel
        mh2skel.exportSkel(filename("skel"))

def load(app):
    app.addExporter(ExporterSkel())

def unload(app):
    pass
