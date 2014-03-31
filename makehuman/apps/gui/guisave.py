#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Save Tab GUI
============

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers

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

This module implements the 'Files > Save' tab.
"""

import os

import mh
import gui
import gui3d
from core import G


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

        self.fileentry = self.addTopWidget(
            gui.FileEntryView('Save', mode='save'))
        self.fileentry.setDirectory(mh.getPath('models'))
        self.fileentry.setFilter('MakeHuman Models (*.mhm)')

        @self.fileentry.mhEvent
        def onFileSelected(filename):
            self.saveMHM(filename)

    def saveMHM(self, filename):
        """Method that does the saving of the .mhm and the thumbnail once
        the save path is selected."""
        if not filename.lower().endswith('.mhm'):
            filename += '.mhm'

        modelPath = mh.getPath('models')
        path = os.path.normpath(os.path.join(modelPath, filename))

        dir, name = os.path.split(path)
        name, ext = os.path.splitext(name)

        if not os.path.exists(dir):
            os.makedirs(dir)

        # Save square sized thumbnail
        size = min(G.windowWidth, G.windowHeight)
        img = mh.grabScreen(
            (G.windowWidth - size) / 2, (G.windowHeight - size) / 2, size, size)

        # Resize thumbnail to max 128x128
        if size > 128:
            img.resize(128, 128)
        img.save(os.path.join(dir, name + '.thumb'))

        # Save the model
        G.app.selectedHuman.save(path, name)
        #G.app.clearUndoRedo()

        self.parent.tasksByName['Load'].fileentry.text = dir
        self.parent.tasksByName['Load'].fileentry.edit.setText(dir)
        self.parent.tasksByName['Load'].fileentry.setDirectory(dir)

        mh.changeCategory('Modelling')

    def onShow(self, event):
        """Handler for the TaskView onShow event.
        Once the task view is shown, give focus to the file entry."""
        gui3d.TaskView.onShow(self, event)
        self.fileentry.setFocus()

    def onHide(self, event):
        """Handler for the TaskView onHide event."""
        gui3d.TaskView.onHide(self, event)
