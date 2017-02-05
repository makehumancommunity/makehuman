#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Plugin to apply custom targets.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Eduardo Menezes de Morais, Jonas Hauquier

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

__docformat__ = 'restructuredtext'

import gui3d
import getpath
import os
import humanmodifier
import modifierslider
import gui
import algos3d
from core import G

class FolderButton(gui.RadioButton):

    def __init__(self, task, group, label, groupBox, selected=False):
        super(FolderButton, self).__init__(group, label, selected)
        self.groupBox = groupBox
        self.task = task

    def onClicked(self, event):
        self.task.syncVisibility()

# TODO inherit from guimodifier if possible

class CustomTargetsTaskView(gui3d.TaskView):

    def __init__(self, category, app):
        self.app = app
        gui3d.TaskView.__init__(self, category, 'Custom')
        self.targetsPath = getpath.getPath('data/custom')
        if not os.path.exists(self.targetsPath):
            os.makedirs(self.targetsPath)

        self.optionsBox = self.addRightWidget(gui.GroupBox('Options'))
        rescanButton = self.optionsBox.addWidget(gui.Button("Rescan targets' folder"))

        self.folderBox = self.addRightWidget(gui.GroupBox('Folders'))
        self.targetsBox = self.addLeftWidget(gui.StackedBox())

        self.human = app.selectedHuman

        @rescanButton.mhEvent
        def onClicked(event):
            self.searchTargets()

        self.folders = []
        self.sliders = []
        self.modifiers = {}

        self.searchTargets()

    def searchTargets(self):
        active = None

        self.unloadTargets()
        group = []

        for root, dirs, files in os.walk(self.targetsPath):
            groupBox = self.targetsBox.addWidget(gui.GroupBox('Targets'))
            folderGroup = self.folderBox.addWidget(FolderButton(self, group, os.path.basename(root), groupBox, len(self.folderBox.children) == 0))
            folderGroup.targetCount = 0
            self.folders.append(groupBox)

            # TODO allow creating more complex modifiers (or we could also require the user to create a modifier .json file)
            for f in files:
                if f.endswith(".target"):
                    self.createTargetControls(groupBox, os.path.join(root, f))
                    folderGroup.targetCount += 1

        for folder in self.folders:
            for child in folder.children:
                child.update()

        if active is not None:
            for child in self.folderBox.children:
                if active == child.getLabel():
                    child.setSelected(True)

        selectOther = False
        visible = []
        for child in self.folderBox.children:
            if child.targetCount == 0:
                child.hide()
                if child.selected:
                    selectOther = True
            else:
                visible.append(child)
        if selectOther and len(visible) > 0:
            visible[0].setSelected(True)


        self.syncVisibility()

        self.syncStatus()

    def unloadTargets(self):
        if len(self.modifiers) == 0:
            return

        # Invalidate any cached targets
        for m in self.modifiers.values():
            for tpath,_ in m.targets:
                algos3d.refreshCachedTarget(tpath)

        for b in self.folders:
            self.targetsBox.removeWidget(b)
            b.destroy()

        self.sliders = []
        self.folders = []

        for child in self.folderBox.children[:]:
            self.folderBox.removeWidget(child)
            child.destroy()

        for mod in self.modifiers.values():
            self.human.removeModifier(mod)
            
        self.modifiers = {}

        # Apply changes to human (of unloaded modifiers)
        self.human.applyAllTargets()

    def syncStatus(self):
        if not self.isVisible():
            return
        if self.sliders:
            gui3d.app.statusPersist('')
        else:
            gui3d.app.statusPersist(['No custom targets found. To add a custom target, place the file in',' %s'],
                                    self.targetsPath)

    def createTargetControls(self, box, targetFile):
        # When the slider is dragged and released, an onChange event is fired
        # By default a slider goes from 0.0 to 1.0, and the initial position will be 0.0 unless specified

        targetFile = os.path.relpath(targetFile, self.targetsPath)

        modifier = humanmodifier.SimpleModifier('custom', self.targetsPath, targetFile)
        modifier.setHuman(self.human)
        self.modifiers[modifier.fullName] = modifier

        label = modifier.name.replace('-',' ').capitalize()
        self.sliders.append(box.addWidget(modifierslider.ModifierSlider(modifier=modifier, label=label)))

    def syncSliders(self):
        for slider in self.sliders:
            slider.update()

    def syncVisibility(self):
        for button in self.folderBox.children:
            if button.selected:
                self.targetsBox.showWidget(button.groupBox)
                if button.groupBox.children:
                    button.groupBox.children[0].setFocus()

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        self.syncVisibility()
        self.syncSliders()
        self.syncStatus()

    def onHide(self, event):
        gui3d.app.statusPersist('')

    def onHumanChanging(self, event):
        if event.change == 'reset':
            self.syncVisibility()
            self.syncSliders()
            self.syncStatus()

    def loadHandler(self, human, values, strict):
        pass

    def saveHandler(self, human, file):
        pass

category = None
taskview = None

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Modelling')
    taskview = category.addTask(CustomTargetsTaskView(category, app))

    app.addLoadHandler('custom', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass
