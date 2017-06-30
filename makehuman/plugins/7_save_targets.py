#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius, Aranuvir

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

TODO
"""

import gui, gui3d
import os
import getpath as gp
import algos3d
import mh
from core import G
from language import language

class SaveTargetsTaskView(gui3d.TaskView):

    def __init__(self, category):

        super(SaveTargetsTaskView, self).__init__(category, 'Save Targets')

        self.fileName = 'full_target.target'
        self.dirName = gp.getDataPath('custom')

        self.saveBox = gui.GroupBox('Save Model as Target')
        self.addLeftWidget(self.saveBox)

        label = self.saveBox.addWidget(gui.TextView('Filename:'))

        self.nameEdit = gui.TextEdit(self.fileName)
        self.nameEdit.textChanged.connect(self.onChange)
        self.saveBox.addWidget(self.nameEdit)

        space = self.saveBox.addWidget(gui.TextView(''))

        self.saveButton = gui.Button('Save')
        self.saveBox.addWidget(self.saveButton)

        self.saveAsButton = gui.BrowseButton(label='Save As ...', mode='save')
        self.saveAsButton.path = os.path.join(self.dirName,  self.fileName)
        self.saveAsButton.setFilter('MakeHuman Target ( *.target )')
        self.saveBox.addWidget(self.saveAsButton)

        self.createShortCut()

        @self.saveButton.mhEvent
        def onClicked(event):
            self.quickSave()

        @self.saveAsButton.mhEvent
        def onClicked(path):
            if path:
                if not path.lower().endswith('.target'):
                    error_msg = 'Cannot save target to file: {0:s}\n Expected a path to a .target file'.format(path)
                    dialog = gui.Dialog()
                    dialog.prompt(title='Error', text=error_msg, button1Label='OK')
                    return
                else:
                    self.saveTargets(path)
                    self.nameEdit.setText(self.fileName)
                    self.saveAsButton.path = path
                    G.app.statusPersist('Saving Directory: ' + self.dirName)

    def quickSave(self):
        path = os.path.join(self.dirName, self.fileName)
        overwrite = True
        dialog = gui.Dialog()

        if not path.lower().endswith('.target'):
            error_msg = 'Cannot save target to file: {0:s}\n Expected a path to a .target file'.format(path)
            dialog.prompt(title='Error', text=error_msg, button1Label='OK')
            return
        else:
            if os.path.exists(path):
                msg = 'File {0:s} already exists. Overwrite?'.format(path)
                overwrite = dialog.prompt(title='Warning', text=msg, button1Label='YES', button2Label='NO')
            if overwrite:
                self.saveTargets(path)


    def saveTargets(self, path):
        human = G.app.selectedHuman
        algos3d.saveTranslationTarget(human.meshData, path)
        self.fileName = os.path.basename(path)
        self.dirName = os.path.dirname(path)

    def onChange(self):
        self.fileName = self.nameEdit.text
        self.saveAsButton.path = os.path.join(self.dirName, self.fileName)

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        G.app.statusPersist('Saving Directory: ' + self.dirName)

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)
        G.app.statusPersist('')

    def createShortCut(self):
        action = gui.Action('savetgt', language.getLanguageString('Save Targets'), self.quickSave)
        G.app.mainwin.addAction(action)
        mh.setShortcut(mh.Modifiers.ALT, mh.Keys.t, action)
        toolbar = G.app.file_toolbar
        toolbar.addAction(action)

def load(app):
    category = app.getCategory('Utilities')
    taskview = category.addTask(SaveTargetsTaskView(category))

def unload(app):
    pass