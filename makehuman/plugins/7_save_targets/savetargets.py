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
from uuid import uuid4
from PyQt5 import QtWidgets


universalBaseTargets = ['universal-female-young-averagemuscle-averageweight.target',
                        'universal-male-young-averagemuscle-averageweight.target']

baseTargets = ['african-female-young.target',
               'african-male-young.target',
               'asian-female-young.target',
               'asian-male-young.target',
               'caucasian-female-young.target',
               'caucasian-male-young.target']

info_message = """Save target saves the current state of all targets applied to the default start up mesh as one global\
 target. The strip option will remove all targets that constitute the default mesh from the global target. This is\
 mandatory when reusing the global target inside MakeHuman. For usage on the base mesh in MakeTarget uncheck the strip\
 option.\n\nSave diff target saves the data difference of two models as a global target. First create or load a model\
 and press \"Set Base\". Then create or load a second model. Pressing \"Save diff target\" will create a global target,\
 which can transform the first model into the second one. The resulting global diff target is absolutely specific to the\
 first model and will not work on any other model.\n\nThe default license of the saved global targets will be AGPL3.\
 The license can be changed by the user if the global target only contains data from custom targets, though licenses\
 from other custom targets need to be taken into account."""


class SaveTargetsTaskView(gui3d.TaskView):

    def __init__(self, category):

        super(SaveTargetsTaskView, self).__init__(category, 'Save Targets')

        mainPanel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        mainPanel.setLayout(layout)

        metaFileID = str(uuid4()) + '.target'
        self.metaFilePath = os.path.join(os.path.dirname(__file__), '__cache__')
        self.metaFile = os.path.join(self.metaFilePath, metaFileID)

        self.fileName = 'full_target.target'
        self.dirName = gp.getDataPath('custom')

        self.diffFileName = 'diff_target.target'
        self.diffDirName = gp.getDataPath('custom')

        self.saveBox = gui.GroupBox('Save Model as Target')
        layout.addWidget(self.saveBox)

        layout.addSpacing(15)

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
        layout.addWidget(self.saveDiffBox)

        layout.addSpacing(15)

        self.diffNameEdit = gui.TextEdit(self.diffFileName)
        self.diffNameEdit.textChanged.connect(self.onDiffChange)
        self.saveDiffBox.addWidget(self.diffNameEdit)

        self.setBaseButton = gui.Button('Set Base')
        self.saveDiffBox.addWidget(self.setBaseButton)

        self.saveDiffButton = gui.Button('Save')
        self.saveDiffBox.addWidget(self.saveDiffButton)

        self.saveDiffAsButton = gui.BrowseButton(label='Save As ...', mode='save')
        self.saveDiffAsButton.path = os.path.join(self.diffDirName, self.diffFileName)
        self.saveDiffAsButton.setFilter('MakeHuman Target ( *.target )')
        self.saveDiffBox.addWidget(self.saveDiffAsButton)

        self.clearButton = gui.Button(label='Clear Cache')
        self.saveDiffBox.addWidget((self.clearButton))

        infoBox = gui.GroupBox('Info')
        layout.addWidget(infoBox)
        infoText = gui.TextView(info_message)
        infoText.setWordWrap(True)
        infoBox.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)
        infoBox.addWidget(infoText)

        layout.addStretch()
        self.addLeftWidget(mainPanel)

        self.createShortCut()

        @self.saveAsButton.mhEvent
        def beforeBrowse(event):
            self.saveAsButton.path = os.path.join(self.dirName, self.fileName)

        @self.saveDiffAsButton.mhEvent
        def beforeBrowse(event):
            self.saveDiffAsButton.path = os.path.join(self.dirName, self.fileName)

        @self.saveButton.mhEvent
        def onClicked(event):
            self.quickSave()

        @self.saveAsButton.mhEvent
        def onClicked(path):
            if os.path.exists(path):
                if not path.lower().endswith('.target'):
                    error_msg = 'Cannot save target to file: {0:s}\nExpected a path to a .target file'.format(path)
                    dialog = gui.Dialog()
                    dialog.prompt(title='Error', text=error_msg, button1Label='OK')
                    log.error('Cannot save targets to %s. Not a .target file.', path)
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
            if not os.path.isdir(self.metaFilePath):
                os.mkdir(self.metaFilePath)
            self.saveTargets(self.metaFile, False)

        @self.saveDiffButton.mhEvent
        def onClicked(event):
            if not os.path.isfile(self.metaFile):
                error_msg = 'No Base Model defined.\nPress "Set Base"'
                dialog = gui.Dialog()
                dialog.prompt(title='Error', text=error_msg, button1Label='OK')
                log.warning(error_msg)
            else:
                path = os.path.join(self.diffDirName, self.diffFileName)
                overwrite = True
                dialog = gui.Dialog()

                if not path.lower().endswith('.target'):
                    error_msg = 'Cannot save target to file: {0:s}\nExpected a path to a .target file'.format(path)
                    dialog.prompt(title='Error', text=error_msg, button1Label='OK')
                    log.error('Cannot save targets to %s. Not a .target file.', path)
                    return
                else:
                    if os.path.exists(path):
                        msg = 'File {0:s} already exists. Overwrite?'.format(path)
                        overwrite = dialog.prompt(title='Warning', text=msg, button1Label='YES', button2Label='NO')
                        if overwrite:
                            log.message('Overwriting %s ...', path)
                    if overwrite:
                        human = G.app.selectedHuman
                        target = algos3d.getTarget(human.meshData, self.metaFile)
                        target.apply(human.meshData, -1)
                        self.saveTargets(path, False)
                        target.apply(human.meshData, 1)

        @self.saveDiffAsButton.mhEvent
        def onClicked(path):
            if path:
                if not os.path.isfile(self.metaFile):
                    error_msg = 'No Base Model defined.\nPress "Set Base"'
                    dialog = gui.Dialog()
                    dialog.prompt(title='Error', text=error_msg, button1Label='OK')
                    log.warning(error_msg)
                else:
                    if not path.lower().endswith('.target'):
                        error_msg = 'Cannot save diff target to file: {0:s}\nExpected a path to a .target file'.format(path)
                        dialog = gui.Dialog()
                        dialog.prompt(title='Error', text=error_msg, button1Label='OK')
                        return
                    else:
                        human = G.app.selectedHuman
                        target = algos3d.getTarget(human.meshData, self.metaFile)
                        target.apply(human.meshData, -1)
                        self.saveTargets(path, False)
                        target.apply(human.meshData, 1)
                        self.diffFileName = os.path.basename(path)
                        self.diffDirName = os.path.dirname(path)
                        self.diffNameEdit.setText(self.diffFileName)
                        self.saveDiffAsButton.path = path
                        G.app.statusPersist('Saving Target Directory: ' + self.dirName +
                                            '   Saving Diff Targets Directory: ' + self.diffDirName)

        @self.clearButton.mhEvent
        def onClicked(sevent):
            for file in os.listdir(path=self.metaFilePath):
                if file:
                    try:
                        os.remove(os.path.join(self.metaFilePath, file))
                    except os.error as e:
                        pass

    def quickSave(self):
        path = os.path.join(self.dirName, self.fileName)
        overwrite = True
        dialog = gui.Dialog()

        if not path.lower().endswith('.target'):
            error_msg = 'Cannot save target to file: {0:s}\nExpected a path to a .target file'.format(path)
            dialog.prompt(title='Error', text=error_msg, button1Label='OK')
            log.error('Cannot save targets to %s. Not a .target file.', path)
            return
        else:
            if os.path.exists(path):
                msg = 'File {0:s} already exists. Overwrite?'.format(path)
                overwrite = dialog.prompt(title='Warning', text=msg, button1Label='YES', button2Label='NO')
                if overwrite:
                    log.message('Overwriting %s ...', path)
            if overwrite:
                self.saveTargets(path, self.stripBaseTargets.selected)

    def stripTargets(self, obj, action=-1):
        for targetName in universalBaseTargets:
            filename = os.path.join(gp.getSysDataPath('targets/macrodetails'), targetName)
            target = algos3d.getTarget(obj, filename)
            if target:
                target.apply(obj, action * 1.0 / len(universalBaseTargets))
        for targetName in baseTargets:
            filename = os.path.join(gp.getSysDataPath('targets/macrodetails'), targetName)
            target = algos3d.getTarget(obj, filename)
            if target:
                target.apply(obj, action * 1.0 / len(baseTargets))

    def unstripTargets(self, obj):
        self.stripTargets(obj, action=1)

    def saveTargets(self, path, strip=True):
        human = G.app.selectedHuman

        if strip:
            self.stripTargets(human.meshData)

        algos3d.saveTranslationTarget(human.meshData, path)
        log.message('Saving target to %s', path)
        self.fileName = os.path.basename(path)
        self.dirName = os.path.dirname(path)

        if strip:
            self.unstripTargets(human.meshData)

    def onChange(self):
        self.fileName = self.nameEdit.text
        self.saveAsButton.path = os.path.join(self.dirName, self.fileName)

    def onDiffChange(self):
        self.diffFileName = self.diffNameEdit.text
        self.saveDiffAsButton.path = os.path.join(self.dirName, self.fileName)

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
