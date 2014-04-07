#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers, Thomas Larsson, Jonas Hauquier

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

TODO
"""

import mh2md5

from progress import Progress
from export import Exporter
from exportutils.config import Config
from core import G

class MD5Config(Config):

    def __init__(self):
        Config.__init__(self)
        self.useRelPaths = True
        self.feetOnGround = True

    def selectedOptions(self, exporter):
        self.smooth = self.subdivide = G.app.selectedHuman.isSubdivided()

        return self


class ExporterMD5(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "MD5"
        self.filter = "MD5 (*.md5)"
        self.fileExtension = "md5"
        self.orderPriority = 10.0

    def build(self, options, taskview):
        self.taskview       = taskview

    def export(self, human, filename):
        reload(mh2md5)
        cfg = self.getConfig()
        cfg.setHuman(human)

        progress = Progress.begin() (0, 1)
        mh2md5.exportMd5(filename("md5mesh"), cfg)

    def getConfig(self):
        cfg = MD5Config()
        cfg.useTPose          = False # self.useTPose.selected
        cfg.scale,cfg.unit    = self.taskview.getScale()

        return cfg

    def onShow(self, exportTaskView):
        exportTaskView.scaleBox.hide()

    def onHide(self, exportTaskView):
        exportTaskView.scaleBox.show()

def load(app):
    app.addExporter(ExporterMD5())

def unload(app):
    pass

