#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Plugin to apply custom targets.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Eduardo Menezes de Morais

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO

"""

__docformat__ = 'restructuredtext'

import gui3d
import mh
import os
import humanmodifier
import modifierslider
import gui

class FolderButton(gui.RadioButton):

    def __init__(self, task, group, label, groupBox, selected=False):
        super(FolderButton, self).__init__(group, label, selected)
        self.groupBox = groupBox
        self.task = task

    def onClicked(self, event):
        self.task.syncVisibility()

class CustomTargetsTaskView(gui3d.TaskView):

    def __init__(self, category, app):
        self.app = app
        gui3d.TaskView.__init__(self, category, 'Custom')
        self.targetsPath = mh.getPath('data/custom')
        if not os.path.exists(self.targetsPath):
            os.makedirs(self.targetsPath)

        self.optionsBox = self.addRightWidget(gui.GroupBox('Options'))
        rescanButton = self.optionsBox.addWidget(gui.Button("Rescan targets' folder"))

        self.folderBox = self.addRightWidget(gui.GroupBox('Folders'))
        self.targetsBox = self.addLeftWidget(gui.StackedBox())

        @rescanButton.mhEvent
        def onClicked(event):
            #TODO: undo any applied change here
            self.searchTargets()

        self.folders = []

        self.searchTargets()

    def searchTargets(self):

        self.sliders = []
        self.modifiers = {}
        active = None

        for folder in self.folders:
            self.targetsBox.removeWidget(folder)
            folder.destroy()
        for child in self.folderBox.children[:]:
            if child.selected:
                active = child.getLabel()
            self.folderBox.removeWidget(child)
            child.destroy()

        self.folders = []
        group = []

        for root, dirs, files in os.walk(self.targetsPath):

            groupBox = self.targetsBox.addWidget(gui.GroupBox('Targets'))
            self.folderBox.addWidget(FolderButton(self, group, os.path.basename(root), groupBox, len(self.folderBox.children) == 0))
            self.folders.append(groupBox)

            for f in files:
                if f.endswith(".target"):
                    self.createTargetControls(groupBox, root, f)

        for folder in self.folders:
            for child in folder.children:
                child.update()

        if active is not None:
            for child in self.folderBox.children[:]:
                if active == child.getLabel():
                    child.setSelected(True)

        self.syncVisibility()

        self.syncStatus()

    def syncStatus(self):
        if not self.isVisible():
            return
        if self.sliders:
            gui3d.app.statusPersist('')
        else:
            gui3d.app.statusPersist('No custom targets found. To add a custom target, place the file in %s',
                                    self.targetsPath)

    def createTargetControls(self, box, targetPath, targetFile):
        # When the slider is dragged and released, an onChange event is fired
        # By default a slider goes from 0.0 to 1.0, and the initial position will be 0.0 unless specified

        # We want the slider to start from the middle
        targetName = os.path.splitext(targetFile)[0]

        modifier = humanmodifier.SimpleModifier('custom', os.path.join(targetPath, targetFile))
        modifier.setHuman(gui3d.app.selectedHuman)
        self.modifiers[targetName] = modifier
        self.sliders.append(box.addWidget(modifierslider.ModifierSlider(value=0, label=targetName, modifier=modifier)))

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

    def loadHandler(self, human, values):
        if values[0] == 'status':
            return

        modifier = self.modifiers.get(values[1], None)
        if modifier:
            modifier.setValue(float(values[2]))

    def saveHandler(self, human, file):

        for name, modifier in self.modifiers.iteritems():
            value = modifier.getValue()
            if value:
                file.write('custom %s %f\n' % (name, value))

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
