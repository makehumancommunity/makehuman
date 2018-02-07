#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Save Tab GUI
============

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3

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


Abstract
--------

This module implements the 'Files > Save' tab.
"""
import os

import mh
import gui
import gui3d
from core import G
from getpath import pathToUnicode


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
    G.app.selectedHuman.save(path, name)
    #G.app.clearUndoRedo()

    # Remember last save folder
    gui3d.app.setSetting('savedir', os.path.dirname(path))

    G.app.status('Your model has been saved to %s.', path)


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

        self.fileentry = self.addTopWidget(gui.FileEntryView('Save', mode='save'))
        self.fileentry.setFilter('MakeHuman Models (*.mhm)')

        @self.fileentry.mhEvent
        def onFileSelected(event):
            path = event.path
            if os.path.exists(path):
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
