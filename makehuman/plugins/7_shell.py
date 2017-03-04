#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements, Jonas Hauquier

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

import sys
import traceback

import gui3d
import gui
from core import G
import log
from PyQt4 import QtCore, QtGui

import ipythonconsole

MAX_COMPLETIONS = -1

class ShellTextEdit(gui.TextEdit):
    def tabPressed(self):
        self.callEvent('onTabPressed', self)
        return True

class ShellTaskView(gui3d.TaskView):
    def __init__(self, category):
        super(ShellTaskView, self).__init__(category, 'Shell')
        self.globals = {'G': G}
        self.history = []
        self.histitem = None

        if ipythonconsole:
            # Use the more advanced Ipython console
            self.console = self.addTopWidget(ipythonconsole.IPythonConsoleWidget())
            return

        # Fall back to old console
        self.console = None
        self.main = self.addTopWidget(QtGui.QWidget())
        self.layout = QtGui.QGridLayout(self.main)
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 0)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 0)

        self.text = gui.DocumentEdit()
        self.text.setSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding)
        self.layout.addWidget(self.text, 0, 0, 1, 2)

        self.line = ShellTextEdit()
        self.line.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.layout.addWidget(self.line, 1, 0, 1, 1)
        self.globals = {'G': G}

        self.clear = gui.Button("Clear")
        self.layout.addWidget(self.clear, 1, 1, 1, 1)

        @self.line.mhEvent
        def onActivate(text):
            self.execute(text)
            self.history.append(text)
            self.histitem = None
            self.line.setText('')

        @self.line.mhEvent
        def onTabPressed(edit):
            def _longest_common_substring(s1, s2):
                """
                This is simply the O(n) left-aligned version
                """
                limit = min(len(s1), len(s2))
                i = 0
                while i < limit and s1[i] == s2[i]:
                    i += 1
                return s1[:i]

            def _largest_common(strings):
                strings = list(strings)
                try:
                    strings.remove('...')
                except:
                    pass

                if len(strings) == 0:
                    return ""
                elif len(strings) == 1:
                    return strings[0]
                else:
                    result = strings[0]
                    for s in strings[1:]:
                        result = _longest_common_substring(result, s)
                    return result

            line = edit.getText()
            suggestions = self.getSuggestions(line)

            if len(suggestions) == 0:
                return
            if len(suggestions) > 1:
                self.write('\n'.join(suggestions)+"\n")
                scrollbar = self.text.verticalScrollBar()
                scrollbar.setSliderPosition(scrollbar.maximum())
                edit.setText(_largest_common(suggestions))
            elif len(suggestions) == 1:
                edit.setText(suggestions[0])

        @self.clear.mhEvent
        def onClicked(event):
            self.clearText()

        @self.line.mhEvent
        def onUpArrow(_dummy):
            self.upArrow()

        @self.line.mhEvent
        def onDownArrow(_dummy):
            self.downArrow()

    def getSuggestions(self, line):
        from rlcompleter import Completer
        def _inRange(i):
            if MAX_COMPLETIONS <= 0:
                # No limit
                return True
            else:
                return i <= MAX_COMPLETIONS
        result = []
        completer = Completer(self.globals)
        i = 0
        suggestion = True
        while suggestion and _inRange(i):
            suggestion = completer.complete(line, i)
            if suggestion:
                if i == MAX_COMPLETIONS and MAX_COMPLETIONS != 0:
                    result.append('...')
                else:
                    if suggestion not in result:
                        result.append(suggestion)
            i += 1
        return result

    def execute(self, text):
        stdout = sys.stdout
        stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self
        try:
            code = compile(text, '<shell>', 'single')
            eval(code, self.globals)
            # exec text in self.globals, {}
        except:
            traceback.print_exc()
        sys.stdout = stdout
        sys.stderr = stderr

    def write(self, text):
        self.text.addText(text)

    def flush(self):
        pass

    def clearText(self):
        self.text.setText('')

    def upArrow(self):
        if not self.history:
            return
        if self.histitem is None or self.histitem == 0:
            self.histitem = len(self.history) - 1
        else:
            self.histitem -= 1
        self.line.setText(self.history[self.histitem])

    def downArrow(self):
        if not self.history:
            return
        if self.histitem is None or self.histitem >= len(self.history) - 1:
            self.histitem = None
            self.line.setText('')
        else:
            self.histitem += 1
            self.line.setText(self.history[self.histitem])

    def onThemeChanged(self, event):
        if self.console is None:
            return
        self.console.set_theme(G.app.theme)

def load(app):
    category = app.getCategory('Utilities')
    taskview = category.addTask(ShellTaskView(category))

def unload(app):
    pass

