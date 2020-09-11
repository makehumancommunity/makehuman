#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Save Tab GUI
============

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

This module implements the 'Files > Save' tab.
"""
import os

import mh
import gui
import gui3d
from core import G
from getpath import pathToUnicode, formatPath
from events3d import EventHandler


def saveMHM(path):
    """Save the .mhm and the thumbnail to the selected save path."""
    path = pathToUnicode(os.path.normpath(path))

    savedir = os.path.dirname(path)
    if not os.path.exists(savedir):
        os.makedirs(savedir)

    name = os.path.splitext(os.path.basename(path))[0]

    # Save square sized thumbnail
    size = min(G.windowWidth, G.windowHeight)
    img = mh.grabScreen(
        (G.windowWidth - size) // 2, (G.windowHeight - size) // 2, size, size)

    # Resize thumbnail to max 128x128
    if size > 128:
        img.resize(128, 128)
    img.save(os.path.join(savedir, name + '.thumb'))

    # Save the model
    G.app.selectedHuman.save(path)
    #G.app.clearUndoRedo()

    # Remember last save folder
    gui3d.app.setSetting('savedir', formatPath(os.path.dirname(path)))

    G.app.status('Your model has been saved to %s.', path)

class UuidView(gui.GroupBox):

    def __init__(self):
        super(UuidView, self).__init__('UUID')
        self.uuidText = gui.TextView()
        self.addWidget(self.uuidText)
        self.genButton = self.addWidget(gui.Button('Generate UUID'))
        self.uuidText.setWordWrap(True)

        @self.genButton.mhEvent
        def onClicked(event):
            self.uuid = '\n'.join(self.isplit(G.app.selectedHuman.newUuid(), 24))
            self.uuidText.setText(self.uuid)

    def onShow(self, event):
        super(UuidView, self).onShow(event)
        self.uuid = '\n'.join(self.isplit(G.app.selectedHuman.getUuid(), 24))
        self.uuidText.setText(self.uuid)

    def clearUuid(self):
        self.uuid = ''
        self.uuidText.setText('')

    def getUuid(self):
        return self.uuid.replace('\n','')

    @classmethod
    def isplit(cls, string, width):
        if string:
            n = len(string) // width
            r = len(string) % width
            l = []
            for i in range(n):
                l.append(string[i*width:(i+1)*width])
            l.append(string[-r:])
            return l
        else:
            return string


class TagsView(gui.GroupBox):

    def __init__(self):
        super(TagsView, self).__init__('Tags')
        self.editList = []
        for _ in range(int(G.app.getSetting('tagCount'))):
            edit = gui.TextEdit('')
            edit.setMaxLength(25)
            self.editList.append(self.addWidget(edit))

    def setTags(self, tags):
        tags = sorted(tags)
        for edit in self.editList:
            if tags:
                edit.setText(tags.pop(0))
            else:
                edit.setText('')

    def getTags(self):
        tags = set()
        for edit in self.editList:
            tag = edit.getText().lower()
            if tag:
                tags.add(tag)
        return tags

    tags=property(getTags, setTags)

    def clearTags(self):
        for edit in self.editList:
            edit.setText('')

    def onShow(self, event):
        super(TagsView, self).onShow(event)
        editDiff = int(G.app.getSetting('tagCount')) - len(self.editList)
        if editDiff > 0:
            for _ in range(editDiff):
                edit = gui.TextEdit('')
                edit.setMaxLength(25)
                self.editList.append(self.addWidget(edit))
        elif editDiff < 0:
            for _ in range(abs(editDiff)):
                edit = self.editList.pop()
                edit.hide()
                edit.destroy()
        self.setTags(G.app.selectedHuman.getTags())

    def onHide(self, event):
        super(TagsView, self).onHide(event)
        G.app.selectedHuman.setTags(self.getTags())


class NameView(gui.GroupBox):

    def __init__(self):
        super(NameView, self).__init__('Human Name')
        self.nameEdit = self.addWidget(gui.TextEdit())

    def getName(self):
        return self.nameEdit.getText()

    def setName(self, name):
        self.nameEdit.setText(name)

    def onShow(self, event):
        super(NameView, self).onShow(event)
        self.setName(G.app.selectedHuman.getName())

    def onHide(self, event):
        super(NameView, self).onHide(event)
        G.app.selectedHuman.setName(self.getName())

    def clearName(self):
        self.setName('')


class MetadataView(gui.QtWidgets.QWidget, gui.Widget):

    def __init__(self):

        super(MetadataView, self).__init__()

        layout = gui.QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.label = gui.TextView('Metadata')
        self.label.setAlignment(gui.QtCore.Qt.AlignHCenter)
        layout.addWidget(self.label)
        layout.addSpacing(10)

        self.name_view = NameView()
        layout.addWidget(self.name_view)

        self.uuid_view = UuidView()
        layout.addWidget(self.uuid_view)

        self.tags_view = TagsView()
        layout.addWidget(self.tags_view)

        self.reset_button = gui.Button('Reset Metadata')
        layout.addWidget(self.reset_button)

        @self.reset_button.mhEvent
        def onClicked(event):
            self.uuid_view.clearUuid()
            self.tags_view.clearTags()
            self.name_view.clearName()
            G.app.selectedHuman.setName('')
            G.app.selectedHuman.clearTags()
            G.app.selectedHuman.setUuid('')

    def getMetadata(self):
        return self.name_view.getName(), self.uuid_view.getUuid(), self.tags_view.getTags()


class SaveTaskView(gui3d.TaskView):
    """Task view for saving MakeHuman model files."""

    def __init__(self, category):
        """SaveTaskView constructor.

        The Save Task view contains a filename entry box at the top,
        and lets the model be displayed in the center,
        accompanied by a square border which the user can utilize
        to create a thumbnail for the saved model.
        """
        gui3d.TaskView.__init__(self, category, 'Save')

        # Declare new settings
        gui3d.app.addSetting('savedir', mh.getPath("models"))

        self.fileentry = self.addTopWidget(gui.FileEntryView(label='File Name:', buttonLabel='Save', mode='save'))
        self.fileentry.setFilter('MakeHuman Models (*.mhm)')

        self.metadata_view = self.addLeftWidget(MetadataView())

        @self.fileentry.mhEvent
        def onFileSelected(event):
            path = event.path
            if path:
                _name, _uuid, _tags = self.metadata_view.getMetadata()
                G.app.selectedHuman.setName(_name)
                G.app.selectedHuman.setUuid(_uuid)
                G.app.selectedHuman.setTags(_tags)
                if not path.lower().endswith(".mhm"):
                    path += ".mhm"
                if event.source in ('return', 'button') and \
                    os.path.exists(path) and \
                    path != G.app.currentFile.path:
                    G.app.prompt("File exists", "The file already exists. Overwrite?",
                        "Yes", "No", lambda: saveMHM(path))
                else:
                    saveMHM(path)

    def onShow(self, event):
        """Handler for the TaskView onShow event.
        Once the task view is shown, preset the save directory
        and give focus to the file entry."""
        gui3d.TaskView.onShow(self, event)

        modelPath = G.app.currentFile.dir
        if modelPath is None:
            modelPath = gui3d.app.getSetting('savedir')
        self.fileentry.directory = modelPath

        name = G.app.currentFile.title
        if name is None:
            name = ""
        self.fileentry.text = name

        self.fileentry.setFocus()
