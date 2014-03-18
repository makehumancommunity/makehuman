#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makeinfo.human.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

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

    # Names exported to Blender

    def meshName(self, proxy=None):
        if proxy:
            return "%s:%s" % (self.name, proxy.name)
        else:
            return "%s:Body" % self.name

    def materialName(self, matname, proxy=None):
        if proxy:
            return "%s:%s:%s" % (self.name, proxy.name, matname)
        else:
            return "%s:%s" % (self.name, matname)

    def textureName(self, channel, proxy=None):
        if proxy:
            return "%s:%s:%s" % (self.name, proxy.name, channel)
        else:
            return "%s:%s" % (self.name, channel)



