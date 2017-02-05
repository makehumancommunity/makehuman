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

import gui3d
import mh
import gui
    
class AppMouseActionEdit(gui.MouseActionEdit):
    def __init__(self, method):
        super(AppMouseActionEdit, self).__init__(gui3d.app.getMouseAction(method))
        self.method = method

    def onChanged(self, shortcut):
        modifiers, button = shortcut
        if not gui3d.app.setMouseAction(modifiers, button, self.method):
            self.setShortcut(gui3d.app.getMouseAction(self.method))

class MouseActionsTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Mouse')

        row = [0]
        def add(widget, name, method):
            widget.addWidget(gui.TextView(name), row[0], 0)
            widget.addWidget(AppMouseActionEdit(method), row[0], 1)
            row[0] += 1

        speedBox = self.addLeftWidget(gui.SliderBox('3D Viewport Speed'))
        self.normal = speedBox.addWidget(gui.Slider(gui3d.app.getSetting('lowspeed'), 1, 10,
            ["Normal speed",": %d"]))

        self.mouseBox = self.addLeftWidget(gui.GroupBox('Camera'))

        add(self.mouseBox, "Move",   gui3d.app.mouseTranslate)
        add(self.mouseBox, "Rotate", gui3d.app.mouseRotate)
        add(self.mouseBox, "Zoom",   gui3d.app.mouseZoom)

        self.invertMouseWheel = self.mouseBox.addWidget(gui.CheckBox("Invert wheel", gui3d.app.getSetting('invertMouseWheel')))
        
        @self.invertMouseWheel.mhEvent
        def onClicked(event):
            gui3d.app.setSetting('invertMouseWheel', self.invertMouseWheel.selected)

        @self.normal.mhEvent
        def onChange(value):
            gui3d.app.setSetting('lowspeed', value)
            
    def onShow(self, event):
        
        gui3d.TaskView.onShow(self, event)
        self.mouseBox.children[1].setFocus()
        gui3d.app.prompt('Info', 'Click on a mouse action box using the modifiers and buttons which you would like to assign to the given action.',
            'OK', helpId='mouseActionHelp')
        gui3d.app.statusPersist('Click on a mouse action box using the modifiers and buttons which you would like to assign to the given action.')
            
    def onHide(self, event):

        gui3d.app.statusPersist('')
        gui3d.TaskView.onHide(self, event)
        gui3d.app.saveSettings()

def load(app):
    category = app.getCategory('Settings')
    taskview = category.addTask(MouseActionsTaskView(category))

def unload(app):
    pass


