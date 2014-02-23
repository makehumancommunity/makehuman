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

from core import G
import os
from getpath import getPath, getSysDataPath
import log
import shutil
import numpy as np

#
#   class Config
#

class Config:

    def __init__(self):
        self.useTPose           = False
        self.feetOnGround       = False
        self.scale              = 1.0
        self.unit               = "dm"
        self.offset             = np.array((0.0, 0.0, 0.0))

        self.rigOptions         = None
        self.useNormals         = False
        self.useRelPaths        = True
        self.cage               = False
        self.texFolder          = None
        self.customPrefix       = ""
        self.human              = None


    def selectedOptions(self, exporter):
        self.useTPose           = False # exporter.useTPose.selected
        self.feetOnGround =         exporter.feetOnGround.selected
        self.scale,self.unit    = exporter.taskview.getScale()
        return self


    def setOffset(self, human):
        from armature.utils import calcJointPos
        if self.feetOnGround:
            self.offset = np.array(calcJointPos(human.meshData, 'ground'))
        else:
            self.offset = np.array((0,0,0), float)


    @property
    def subdivide(self):
        if not self.human:
            log.warning('No human set in config, disabled subdivision for export.')
            return False
        else:
            return self.human.isSubdivided()


    def setHuman(self, human):
        """
        Set the human object for this config.
        """
        self.human = human


    def getProxies(self):
        """
        Get the proxy list from the current state of the set human object.
        Proxy list will contain all proxy items such as proxy mesh and clothes,
        hair, eyes, genitals and cages.
        """
        if not self.human:
            return {}

        proxies = {}
        for proxy in self.human.getProxies():
            if proxy:
                name = self.goodName(proxy.name)
                proxies[name] = proxy

        if self.human.proxy:
            proxy = self.human.proxy
            name = self.goodName(proxy.name)
            proxies[name] = proxy

        if self.cage:
            import mh2proxy
            obj = G.app.selectedHuman
            filepath = getSysDataPath("cages/cage/cage.mhclo")
            proxy = mh2proxy.readProxyFile(obj, filepath, type="Cage")
            proxy.update(obj)
            proxies[name] = proxy

        return proxies


    def setupTexFolder(self, filepath):
        (fname, ext) = os.path.splitext(filepath)
        fname = self.goodName(os.path.basename(fname))
        self.outFolder = os.path.realpath(os.path.dirname(filepath))
        self.filename = os.path.basename(filepath)
        self.texFolder = self.getSubFolder(self.outFolder, "textures")
        self._copiedFiles = {}


    def getSubFolder(self, path, name):
        folder = os.path.join(path, name)
        if not os.path.exists(folder):
            log.message("Creating folder %s", folder)
            try:
                os.mkdir(folder)
            except:
                log.error("Unable to create separate folder:", exc_info=True)
                return None
        return folder


    def copyTextureToNewLocation(self, filepath):
        srcDir = os.path.abspath(os.path.expanduser(os.path.dirname(filepath)))
        filename = os.path.basename(filepath)

        newpath = os.path.abspath( os.path.join(self.texFolder, filename) )
        try:
            self._copiedFiles[filepath]
            done = True
        except:
            done = False
        if not done:
            try:
                shutil.copyfile(filepath, newpath)
            except:
                log.message("Unable to copy \"%s\" -> \"%s\"" % (filepath, newpath))
            self._copiedFiles[filepath] = True

        if not self.useRelPaths:
            return newpath
        else:
            relpath = os.path.relpath(newpath, self.outFolder)
            return str(os.path.normpath(relpath))


    def goodName(self, name):
        string = name.replace(" ", "_").replace("-","_").lower()
        return string


