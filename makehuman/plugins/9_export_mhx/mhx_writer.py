#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makeinfo.human.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makeinfo.human.org/node/318)

**Coding Standards:**  See http://www.makeinfo.human.org/node/165

Abstract
--------

MHX Writer base class
"""

class Writer:
    def __init__(self):
        self.name = None
        self.type = "undefined"
        self.human = None
        self.armature = None
        self.config = None
        self.proxies = None
        self.customTargetFiles = None
        self.loadedShapes = {}
        self.customProps = []

    def __repr__(self):
        return ("<Writer %s>" % self.type)

    def fromOtherWriter(self, writer):
        self.name = writer.name
        self.human = writer.human
        self.armature = writer.armature
        self.config = writer.config
        self.proxies = writer.proxies
        self.customTargetFiles = writer.customTargetFiles
        self.loadedShapes = writer.loadedShapes
        self.customProps = writer.customProps
        return self


