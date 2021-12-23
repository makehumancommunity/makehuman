#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman community assets

**Product Home Page:** http://www.makehumancommunity.org

**Code Home Page:**    https://github.com/makehumancommunity/community-plugins

**Authors:**           Joel Palmius

**Copyright(c):**      Joel Palmius 2016

**Licensing:**         MIT

Abstract
--------

This plugin manages community assets

"""

import gui3d
import mh
import gui
import json
import os
import re
import platform
import calendar, datetime

from progress import Progress

from core import G

mhapi = gui3d.app.mhapi

class AssetCleaner():

    def __init__(self, remoteAsset):

        self.log = mhapi.utility.getLogChannel("assetdownload")

        self.asset = remoteAsset
        self.assetType = remoteAsset.getType()

        self._mhmat_as_string = ""

        for fn in remoteAsset.localFiles.keys():
            ext = os.path.splitext(fn)
            self.log.debug("ext",ext)

    def checkForMissingFiles(self):
        return []

    def _getTextureTuples(self):

        if self._mhmat_as_string is None or self._mhmat_as_string == "":
            return []

        return []

    def _cleanMHMAT(self):
        textures = self._getTextureTuples()
        pass

    def _cleanMHCLO(self):
        pass

    def _fixClothes(self):
        pass

    def _fixMaterial(self):
        pass

    def cleanAsset(self):

        if self.assetType in ["eyebrows","eyelashes","teeth","hair","clothes"]:
            self._fixClothes()

        if self.assetType == "material":
            self._fixMaterial()


