#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Manuel Bastioni, Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

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
        self.normal = speedBox.addWidget(gui.Slider(gui3d.app.settings.get('lowspeed', 1), 1, 10,
            "Normal speed: %d"))
        self.shift = speedBox.addWidget(gui.Slider(gui3d.app.settings.get('highspeed', 5), 1, 10,
            "Shift + Mouse: %d"))

        self.mouseBox = self.addLeftWidget(gui.GroupBox('Camera'))

        add(self.mouseBox, "Move",   gui3d.app.mouseTranslate)
        add(self.mouseBox, "Rotate", gui3d.app.mouseRotate)
        add(self.mouseBox, "Zoom",   gui3d.app.mouseZoom)

        self.invertMouseWheel = self.mouseBox.addWidget(gui.CheckBox("Invert wheel", gui3d.app.settings.get('invertMouseWheel', False)))
        
        @self.invertMouseWheel.mhEvent
        def onClicked(event):
            gui3d.app.settings['invertMouseWheel'] = self.invertMouseWheel.selected

        @self.normal.mhEvent
        def onChange(value):
            gui3d.app.settings['lowspeed'] = value
            
        @self.shift.mhEvent
        def onChange(value):
            gui3d.app.settings['highspeed'] = value
            
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


