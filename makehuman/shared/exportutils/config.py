#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

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

from core import G
import os
from getpath import getPath, getSysDataPath
import log
import shutil
import numpy as np

#
#   class Config
#

class Config(object):

    def __init__(self):
        self.useTPose           = False
        self.feetOnGround       = False
        self.scale              = 1.0
        self.unit               = "dm"

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


    @property
    def offset(self):
        return -self.scale * self.human.getJointPosition('ground')[1]

    @property
    def offsetVect(self):
        return np.asarray([0.0, self.offset, 0.0], dtype=np.float32)


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
        for pxy in self.human.getProxies():
            if pxy:
                name = self.goodName(pxy.name)
                proxies[name] = pxy

        if self.human.proxy:
            pxy = self.human.proxy
            name = self.goodName(pxy.name)
            proxies[name] = pxy

        if self.cage:
            import proxy
            human = G.app.selectedHuman
            filepath = getSysDataPath("cages/cage/cage.mhclo")
            pxy = proxy.loadProxy(human, filepath, type="Cage")
            pxy.update(human.meshData)
            proxies[name] = pxy

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


    def getRigType(self):
        """
        Return the name of the skeleton type currently set on the human.
        """
        if not hasattr(self.human, "getSkeleton"):
            return None
        skel = self.human.getSkeleton()
        if skel:
            return skel.name
        else:
            return None


    def _getRigOptions(self):
        return self.getRigOptions()

    def _setRigOptions(self):
        raise RuntimeError("Setting rigOptions directly not allowed!")

    rigOptions = property(_getRigOptions, _setRigOptions)


    def getRigOptions(self):
        """
        Retrieve custom rig options of the rig set on the human.
        """
        if not hasattr(self.human, "getSkeleton"):
            return None
        skel = self.human.getSkeleton()
        if skel:
            return skel.options
        else:
            return None

