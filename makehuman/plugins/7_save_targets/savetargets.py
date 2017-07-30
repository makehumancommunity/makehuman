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

import gui
import gui3d
import os
import getpath as gp
import algos3d
import mh
import log
from core import G
from language import language

universalBaseTargets = ['universal-female-young-averagemuscle-averageweight.target',
                        'universal-male-young-averagemuscle-averageweight.target']

baseTargets = ['african-female-young.target',
               'african-male-young.target',
               'asian-female-young.target',
               'asian-male-young.target',
               'caucasian-female-young.target',
               'caucasian-male-young.target']


class SaveTargetsTaskView(gui3d.TaskView):

    def __init__(self, category):

        super(SaveTargetsTaskView, self).__init__(category, 'Save Targets')

        self.fileName = 'full_target.target'
        self.dirName = gp.getDataPath('custom')

        self.diffFileName = 'diff_target.target'
        self.diffDirName = gp.getDataPath('custom')

        self.saveBox = gui.GroupBox('Save Model as Target')
        self.addLeftWidget(self.saveBox)

        label = self.saveBox.addWidget(gui.TextView('Filename:'))

        self.nameEdit = gui.TextEdit(self.fileName)
        self.nameEdit.textChanged.connect(self.onChange)
        self.saveBox.addWidget(self.nameEdit)

        self.stripBaseTargets = gui.CheckBox('Strip Base Targets', True)
        self.saveBox.addWidget(self.stripBaseTargets)

        self.saveButton = gui.Button('Save')
        self.saveBox.addWidget(self.saveButton)

        self.saveAsButton = gui.BrowseButton(label='Save As ...', mode='save')
        self.saveAsButton.path = os.path.join(self.dirName,  self.fileName)
        self.saveAsButton.setFilter('MakeHuman Target ( *.target )')
        self.saveBox.addWidget(self.saveAsButton)

        self.saveDiffBox = gui.GroupBox('Save Diff Target')
        self.addLeftWidget(self.saveDiffBox)

        self.diffNameEdit = gui.TextEdit(self.diffFileName)
        self.diffNameEdit.textChanged.connect(self.onDiffChange)
        self.saveDiffBox.addWidget(self.diffNameEdit)

        self.diffStripBaseTargets = gui.CheckBox('Strip Base Targets', True)
        self.saveDiffBox.addWidget(self.diffStripBaseTargets)

        self.setBaseButton = gui.Button('Set Base')
        self.saveDiffBox.addWidget(self.setBaseButton)

        self.saveDiffButton = gui.Button('Save')
        self.saveDiffBox.addWidget(self.saveDiffButton)

        self.saveDiffAsButton = gui.BrowseButton(label='Save As ...', mode='save')
        self.saveDiffAsButton.path = os.path.join(self.diffDirName, self.diffFileName)
        self.saveDiffAsButton.setFilter('MakeHuman Target ( *.target )')
        self.saveDiffBox.addWidget(self.saveDiffAsButton)

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
                    self.saveTargets(path, self.stripBaseTargets.selected)
                    self.fileName = os.path.basename(path)
                    self.dirName = os.path.dirname(path)
                    self.nameEdit.setText(self.fileName)
                    self.saveAsButton.path = path
                    G.app.statusPersist('Saving Target Directory: ' + self.dirName +
                                        '   Saving Diff Targets Directory: ' + self.diffDirName)

        @self.setBaseButton.mhEvent
        def onClicked(event):
            dir_path = os.path.join(os.path.dirname(__file__), 'cache')
            if not os.path.isdir(dir_path):
                os.mkdir(dir_path)
            file_path = os.path.join(dir_path, 'meta.target')
            self.saveTargets(file_path, True)
            result = algos3d._targetBuffer.pop(gp.canonicalPath(file_path), None)
            

        @self.saveDiffButton.mhEvent
        def onClicked(event):
            meta_file_path = os.path.join(os.path.dirname(__file__), 'cache', 'meta.target')
            if not os.path.isfile(meta_file_path):
                error_msg = 'No Base Target defined.\nPress "Set Base"'
                dialog = gui.Dialog()
                dialog.prompt(title='Error', text=error_msg, button1Label='OK')
                log.warning(error_msg)
            else:
                path = os.path.join(self.diffDirName, self.diffFileName)
                overwrite = True
                dialog = gui.Dialog()

                if not path.lower().endswith('.target'):
                    error_msg = 'Cannot save target to file: {0:s}\n Expected a path to a .target file'.format(path)
                    dialog.prompt(title='Error', text=error_msg, button1Label='OK')
                    log.error('cannot save tagets to %s. Not a .target file.', path)
                    return
                else:
                    if os.path.exists(path):
                        msg = 'File {0:s} already exists. Overwrite?'.format(path)
                        overwrite = dialog.prompt(title='Warning', text=msg, button1Label='YES', button2Label='NO')
                        if overwrite:
                            log.message('overwriting %s ...', path)
                    if overwrite:
                        human = G.app.selectedHuman
                        target = algos3d.getTarget(human.meshData, meta_file_path)
                        target.apply(human.meshData, -1)
                        self.saveTargets(path, self.stripBaseTargets.selected)
                        target.apply(human.meshData, 1)

        @self.saveDiffAsButton.mhEvent
        def onClicked(path):
            meta_file_path = os.path.join(os.path.dirname(__file__), 'cache', 'meta.target')
            if not os.path.isfile(meta_file_path):
                error_msg = 'No Base Target defined.\nPress "Set Base"'
                dialog = gui.Dialog()
                dialog.prompt(title='Error', text=error_msg, button1Label='OK')
                log.warning(error_msg)
            else:
                if path:
                    if not path.lower().endswith('.target'):
                        error_msg = 'Cannot save diff target to file: {0:s}\n Expected a path to a .target file'.format(path)
                        dialog = gui.Dialog()
                        dialog.prompt(title='Error', text=error_msg, button1Label='OK')
                        return
                    else:
                        human = G.app.selectedHuman
                        target = algos3d.getTarget(human.meshData, meta_file_path)
                        target.apply(human.meshData, -1)
                        self.saveTargets(path, self.diffStripBaseTargets.selected)
                        target.apply(human.meshData, 1)
                        self.diffFileName = os.path.basename(path)
                        self.diffDirName = os.path.dirname(path)
                        self.diffNameEdit.setText(self.fileName)
                        self.saveDiffAsButton.path = path

    def quickSave(self):
        path = os.path.join(self.dirName, self.fileName)
        overwrite = True
        dialog = gui.Dialog()

        if not path.lower().endswith('.target'):
            error_msg = 'Cannot save target to file: {0:s}\n Expected a path to a .target file'.format(path)
            dialog.prompt(title='Error', text=error_msg, button1Label='OK')
            log.error('cannot save tagets to %s. Not a .target file.', path)
            return
        else:
            if os.path.exists(path):
                msg = 'File {0:s} already exists. Overwrite?'.format(path)
                overwrite = dialog.prompt(title='Warning', text=msg, button1Label='YES', button2Label='NO')
                if overwrite:
                    log.message('overwriting %s ...', path)
            if overwrite:
                self.saveTargets(path, self.stripBaseTargets.selected)

    def stripTargets(self, obj, action=-1):
        for targetName in universalBaseTargets:
            filename = os.path.join(gp.getSysDataPath('targets/macrodetails'), targetName)
            target = algos3d.getTarget(obj, filename)
            if target:
                target.apply(obj, action * 1 / len(universalBaseTargets))
        for targetName in baseTargets:
            filename = os.path.join(gp.getSysDataPath('targets/macrodetails'), targetName)
            target = algos3d.getTarget(obj, filename)
            if target:
                target.apply(obj, action * 1 / len(baseTargets))

    def unstripTargets(self, obj):
        self.stripTargets(obj, action=1)

    def saveTargets(self, path, strip=True):
        human = G.app.selectedHuman

        if strip:
            self.stripTargets(human.meshData)

        algos3d.saveTranslationTarget(human.meshData, path)
        log.message('saving target to %s', path)
        self.fileName = os.path.basename(path)
        self.dirName = os.path.dirname(path)

        if strip:
            self.unstripTargets(human.meshData)

    def onChange(self):
        self.fileName = self.nameEdit.text
        self.saveAsButton.path = os.path.join(self.dirName, self.fileName)

    def onDiffChange(self):
        self.diffFileName = self.diffNameEdit.text
        self.saveAsButton.path = os.path.join(self.dirName, self.fileName)


    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        G.app.statusPersist('Saving Target Directory: ' + self.dirName +
                            '   Saving Diff Targets Directory: ' + self.diffDirName)

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)
        G.app.statusPersist('')

    def createShortCut(self):
        action = gui.Action('savetgt', language.getLanguageString('Save Targets'), self.quickSave)
        G.app.mainwin.addAction(action)
        mh.setShortcut(mh.Modifiers.ALT, mh.Keys.t, action)
        toolbar = G.app.file_toolbar
        toolbar.addAction(action)
