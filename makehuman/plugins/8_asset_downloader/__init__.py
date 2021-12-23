#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman community assets

**Product Home Page:** TBD

**Code Home Page:**    TBD

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
import log
import json

from .assetdownload import AssetDownloadTaskView

category = None

downloadView = None

def load(app):
    category = app.getCategory('Community')
    downloadView = category.addTask(AssetDownloadTaskView(category))

def unload(app):
    pass

