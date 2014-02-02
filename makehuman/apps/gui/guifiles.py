#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module implements the top-level 'Files' tab.
"""

import gui3d
from guisave import SaveTaskView
from guiload import LoadTaskView
from guiexport import ExportTaskView

class FilesCategory(gui3d.Category):
    def __init__(self):
        super(FilesCategory, self).__init__('Files')

        self.load = LoadTaskView(self)
        self.save = SaveTaskView(self)
        self.export = ExportTaskView(self)

        self.addTask(self.load)
        self.addTask(self.save)
        self.addTask(self.export)
