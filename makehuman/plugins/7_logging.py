#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

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
import log
from core import G

class LevelRadioButton(gui.RadioButton):
    def __init__(self, group, level):
        name = log.getLevelName(level).capitalize()
        super(LevelRadioButton, self).__init__(group, name, not group)
        self.level = level

    def onClicked(self, _dummy = None):
        if self.selected:
            G.app.log_window.setLevel(self.level)

class LoggingTaskView(gui3d.TaskView):
    def __init__(self, category):
        super(LoggingTaskView, self).__init__(category, 'Logs')
        self.addTopWidget(G.app.log_window)
        self.groupBox = self.addLeftWidget(gui.GroupBox('Level'))
        group = []
        for level in [log.DEBUG, log.MESSAGE, log.NOTICE, log.WARNING, log.ERROR]:
            radio = self.groupBox.addWidget(LevelRadioButton(group, level))
        self.copy = self.addLeftWidget(gui.Button('Copy to Clipboard'))

        @self.copy.mhEvent
        def onClicked(self, _dummy = None):
            strings = G.app.log_window.getSelectedItems()
            if not strings:
                G.app.status('No log items selected')
                return
            text = ''.join(string + '\n' for string in strings)
            G.app.clipboard().setText(text)

def load(app):
    category = app.getCategory('Utilities')
    taskview = category.addTask(LoggingTaskView(category))

def unload(app):
    pass

