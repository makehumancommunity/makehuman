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

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

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
        human = G.app.selectedHuman
        human.save(path, name)
        G.app.modified = False
        #G.app.clearUndoRedo()

        G.app.setFilenameCaption(filename)
        G.app.setFileModified(False)

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
