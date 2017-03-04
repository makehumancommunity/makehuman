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
    
class AppShortcutEdit(gui.ShortcutEdit):
    def __init__(self, action):
        super(AppShortcutEdit, self).__init__(gui3d.app.getShortcut(action))
        self.action = action

    def updateShortcut(self):
        self.setShortcut(gui3d.app.getShortcut(self.action))

    def onChanged(self, shortcut):
        modifiers, key = shortcut
        if not gui3d.app.setShortcut(modifiers, key, self.action):
            self.updateShortcut()

class ShortcutsTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Shortcuts')

        box = None
        self.widgets = []

        row = [0]
        def add(action):
            box.addWidget(gui.TextView(action.text), row[0], 0)
            w = box.addWidget(AppShortcutEdit(action), row[0], 1)
            self.widgets.append(w)
            row[0] += 1

        actions = gui3d.app.actions

        box = self.cameraBox = self.addLeftWidget(gui.GroupBox('Camera'))
        add(actions.rotateU)
        add(actions.rotateD)
        add(actions.rotateL)
        add(actions.rotateR)
        add(actions.panU)
        add(actions.panD)
        add(actions.panL)
        add(actions.panR)
        add(actions.zoomIn)
        add(actions.zoomOut)
        add(actions.front)
        add(actions.right)
        add(actions.top)
        add(actions.back)
        add(actions.left)
        add(actions.bottom)
        add(actions.resetCam)

        box = self.actionBox = self.addRightWidget(gui.GroupBox('Actions'))
        add(actions.undo)
        add(actions.redo)

        box = self.navigationBox = self.addRightWidget(gui.GroupBox('Navigation'))
        add(actions.modelling)
        add(actions.save)
        add(actions.load)
        add(actions.export)
        add(actions.rendering)
        add(actions.help)
        add(actions.exit)

        restorebox = gui.GroupBox('Restore Settings')
        self.addLeftWidget(restorebox)
        self.restoreBtn = gui.Button('Restore to defaults')
        restorebox.addWidget(self.restoreBtn)

        @self.restoreBtn.mhEvent
        def onClicked(event):
            gui3d.app.resetShortcuts()
            self.updateShortcuts()


    def updateShortcuts(self):
        for w in self.widgets:
            w.updateShortcut()

    def onShow(self, event):
        
        gui3d.TaskView.onShow(self, event)
        self.cameraBox.children[1].setFocus()
        gui3d.app.prompt('Info', 'Click on a shortcut box and press the keys of the shortcut which you would like to assign to the given action.',
            'OK', helpId='shortcutHelp')
        gui3d.app.statusPersist('Click on a shortcut box and press the keys of the shortcut which you would like to assign to the given action.')
        self.updateShortcuts()
    
    def onHide(self, event):

        gui3d.app.statusPersist('')
        gui3d.TaskView.onHide(self, event)
        gui3d.app.saveSettings()

def load(app):
    category = app.getCategory('Settings')
    taskview = category.addTask(ShortcutsTaskView(category))

def unload(app):
    pass


