#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius, Marc Flerackers

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

# We need this for gui controls
import gui3d
import mh
import gui
import log

class ExampleTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Example')

        box = self.addLeftWidget(gui.GroupBox('Example'))
        
        # We add a button to the current task
        # A button just fires an event when it is clicked, if a selected texture is specified,
        # it is used while the mouse is down on the button

        self.aButton = box.addWidget(gui.Button('Button'))
        
        self.pushed = 0
        self.aButtonLabel = box.addWidget(gui.TextView('Pushed 0 times'))

        @self.aButton.mhEvent
        def onClicked(event):
            self.pushed += 1
            self.aButtonLabel.setTextFormat('Pushed %d times', self.pushed)

        # We add a toggle button to the current task
        # A toggle button fires an event when it is clicked but retains its selected state after the mouse is up,
        # if a selected texture is specified, it is used to show whether the button is toggled

        self.aToggleButton = box.addWidget(gui.CheckBox('ToggleButton'))

        self.aToggleButtonLabel = box.addWidget(gui.TextView('Not selected'))

        @self.aToggleButton.mhEvent
        def onClicked(event):
            if self.aToggleButton.selected:
                self.aToggleButtonLabel.setText('Selected')
            else:
                self.aToggleButtonLabel.setText('Not selected')

        # Next we will add some radio buttons. For this we need a group, since only one in the group can be selected
        # A radio button fires an event when it is clicked but retains its selected state after the mouse is up, and deselects all other buttons in the group
        # If a selected texture is specified, it is used to show whether the button is selected

        self.aRadioButtonGroup = []

         # We make the first one selected
        self.aRadioButton1 = box.addWidget(gui.RadioButton(self.aRadioButtonGroup, 'RadioButton1', selected=True))
        self.aRadioButton2 = box.addWidget(gui.RadioButton(self.aRadioButtonGroup, 'RadioButton2'))

        self.aRadioButtonLabel = box.addWidget(gui.TextView('Button 1 is selected'))

        @self.aRadioButton1.mhEvent
        def onClicked(event):
            self.aRadioButtonLabel.setText('Button 1 is selected')

        @self.aRadioButton2.mhEvent
        def onClicked(event):
            self.aRadioButtonLabel.setText('Button 2 is selected')

        # When the slider is dragged and released, an onChange event is fired
        # By default a slider goes from 0.0 to 1.0, and the initial position will be 0.0 unless specified

        # We want the slider to start from the middle
        self.aSlider = box.addWidget(gui.Slider(value=0.5, label=['Slider',' %.2f']))

        self.aSliderLabel = box.addWidget(gui.TextView('Value is 0.5'))

        @self.aSlider.mhEvent
        def onChange(value):
            self.aSliderLabel.setTextFormat('Value is %f', value)
            self.aProgressBar.setProgress(value)

        # we also create a progressbar, which is updated as the slider moves

        self.aProgressBar = box.addWidget(gui.ProgressBar())
        self.aProgressBar.setProgress(0.5)
        
        # A text edit

        self.aTextEdit = box.addWidget(gui.TextEdit(text='Some text'))
        
        self.meshSlider = box.addWidget(gui.Slider(value=0.5, label=['Mesh distort',' %0.2f']))
        
        self.isMeshStored = False
        @self.meshSlider.mhEvent
        def onChanging(value):
            human = gui3d.app.selectedHuman
            if self.isMeshStored:
                self.restoreMesh(human)
            else:
                self.storeMesh(human)
                self.isMeshStored = True
            human.mesh.coord += human.mesh.vnorm * value
            human.mesh.markCoords(coor=True)
            human.mesh.update()
    
        @self.meshSlider.mhEvent
        def onChange(value):
            human = gui3d.app.selectedHuman
            human.applyAllTargets()
            self.isMeshStored = False
            human.mesh.coord += human.mesh.vnorm * value
            human.mesh.markCoords(coor=True)
            human.mesh.update()

    def storeMesh(self, human):
        log.message("Storing mesh status")
        self.meshStored = human.meshData.coord.copy()
        self.meshStoredNormals = human.meshData.vnorm.copy()

    def restoreMesh(self, human):
        human.meshData.coord[...] = self.meshStored
        human.meshData.vnorm[...] = self.meshStoredNormals
        human.meshData.markCoords(coor=True, norm=True)

    def onShow(self, event):
        gui3d.app.statusPersist('This is an example plugin; see plugins/7_example.py')

    def onHide(self, event):
        gui3d.app.statusPersist('')

category = None
taskview = None

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Utilities')
    taskview = category.addTask(ExampleTaskView(category))


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass
