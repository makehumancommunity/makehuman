#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2015

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

from export import Exporter, ExportConfig


class FbxConfig(ExportConfig):

    def __init__(self):
        ExportConfig.__init__(self)

        self.useRelPaths     = False
        self.useMaterials    = True # for debugging  # TODO what is the function of this?
        self.binary = False

        self.yUpFaceZ = True
        self.yUpFaceX = False
        self.zUpFaceNegY = False
        self.zUpFaceX = False

        self.localY = True
        self.localX = False
        self.localG = False

    # TODO preferably these are used (perhaps as enum) instead of the bools above
    # TODO move these to export Config super class
    @property
    def meshOrientation(self):
        if self.yUpFaceZ:
            return 'yUpFaceZ'
        if self.yUpFaceX:
            return 'yUpFaceX'
        if self.zUpFaceNegY:
            return 'zUpFaceNegY'
        if self.zUpFaceX:
            return 'zUpFaceX'
        return 'yUpFaceZ'

    @property
    def localBoneAxis(self):
        if self.localY:
            return 'y'
        if self.localX:
            return 'x'
        if self.localG:
            return 'g'
        return 'y'


class ExporterFBX(Exporter):
    def __init__(self):
        Exporter.__init__(self)
        self.name = "Filmbox (fbx)"
        self.filter = "Filmbox (*.fbx)"
        self.fileExtension = "fbx"
        self.orderPriority = 80.0

    def build(self, options, taskview):
        import gui
        Exporter.build(self, options, taskview)
        self.binary   = options.addWidget(gui.CheckBox("Binary FBX", False))

    def export(self, human, filename):
        from . import mh2fbx
        cfg = self.getConfig()
        cfg.setHuman(human)
        mh2fbx.exportFbx(filename("fbx"), cfg)

    def getConfig(self):
        cfg = FbxConfig()
        cfg.feetOnGround      = self.feetOnGround.selected
        cfg.scale,cfg.unit    = self.taskview.getScale()
        cfg.binary            = self.binary.selected

        return cfg

def load(app):
    app.addExporter(ExporterFBX())

def unload(app):
    pass

