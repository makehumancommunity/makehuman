#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2020

**Licensing:**         AGPL3

    This file is part of MakeHuman Community (www.makehumancommunity.org).

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


Abstract
--------

This module implements the 'Files > Load' tab 
"""

import mh
import gui3d
import filechooser as fc
import qtgui as gui
from getpath import formatPath
import filecache
import os


class HumanFileSort(fc.FileSort):

    def __init__(self):
        super(HumanFileSort, self).__init__()

        '''
        # TODO
        self.metaFields = ["gender", "age", "muscle", "weight"]
        '''

    def getMeta(self, filename):
        meta = {}

        with open(filename, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                lineData = line.split()
                if not lineData:
                    continue
                field = lineData[0]
                if field in self.metaFields:
                    meta[field] = float(lineData[1])
        return meta


class LoadTaskView(gui3d.TaskView, filecache.MetadataCacher):

    def __init__(self, category):

        gui3d.TaskView.__init__(self, category, 'Load')

        self.modelPath = None

        self.fileentry = self.addTopWidget(gui.FileEntryView(label='Selected Folder:', buttonLabel='Browse', mode='dir'))
        self.fileentry.filter = 'MakeHuman Models (*.mhm)'

        # Declare new settings
        gui3d.app.addSetting('loaddir', mh.getPath("models"))

        @self.fileentry.mhEvent
        def onFileSelected(event):
            self.filechooser.setPaths([event.path])
            self.filechooser.refresh()
            # Remember load folder
            gui3d.app.setSetting('loaddir', formatPath(event.path))

        loadpath = gui3d.app.getSetting('loaddir')
        self.filechooser = fc.IconListFileChooser(loadpath, 'mhm', 'thumb', mh.getSysDataPath('notfound.thumb'), sort=HumanFileSort())
        filecache.MetadataCacher.__init__(self, ['mhm'], 'models_filecache.mhc')
        self.addRightWidget(self.filechooser)
        self.addLeftWidget(self.filechooser.createSortBox())
        self.fileLoadHandler = fc.TaggedFileLoader(self, useNameTags=mh.getSetting('useNameTags'))
        self.filechooser.setFileLoadHandler(self.fileLoadHandler)
        self.addLeftWidget(self.filechooser.createTagFilter())

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            if gui3d.app.currentFile.modified:
                gui3d.app.prompt("Load", "You have unsaved changes. Are you sure you want to close the current file?",
                    "Yes", "No", lambda: gui3d.app.loadHumanMHM(filename))
            else:
                gui3d.app.loadHumanMHM(filename)

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)

        self.fileLoadHandler.setNameTagsUsage(useNameTags = mh.getSetting('useNameTags'))

        #self.modelPath = gui3d.app.currentFile.dir
        #if self.modelPath is None:
        #    self.modelPath = gui3d.app.getSetting('loaddir')
        #
        #self.fileentry.directory = self.modelPath
        #self.filechooser.setPaths(self.modelPath)
        self.fileentry.directory = gui3d.app.getSetting('loaddir')
        self.filechooser.setPaths(gui3d.app.getSetting('loaddir'))
        self.filechooser.setFocus()

        # HACK: otherwise the toolbar background disappears for some weird reason
        # mh.redraw()

    def getMetadataImpl(self, filename):
        version = ''
        name = ''
        uuid = ''
        tags = set()
        if os.path.isfile(filename) and os.path.splitext(filename)[1] == '.mhm':
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    if line and not line.startswith('#'):
                        data = line.strip().split()
                        if len(data) > 1:
                            if data[0] == 'version':
                                version = data[1]
                            if data[0] == 'name':
                                name = ' '.join(data[1:])
                            if data[0] == 'uuid':
                                uuid = data[1]
                            if data[0] == 'tags':
                                for tag in ' '.join(data[1:]).split(';'):
                                    tags.add(tag[:25]) # Max. tag length is 25
                    if version and name and uuid and tags:
                        break
        if version < 'v1.2.0':
            if tags:
                name = ' '.join(tags)
                tags.clear()
        return (name, uuid, tags)

    def getTagsFromMetadata(self, metadata):
        _, _, tags = metadata
        return tags

    def getNameFromMetadata(self, metadata):
        name, _, _ = metadata
        return name

    def getSearchPaths(self):
        if self.modelPath:
            return [self.modelPath]
        else:
            return [gui3d.app.getSetting('loaddir')]

    def getFileExtensions(self):
        return 'mhm'

    def unload(self):
        self.onUnload()
