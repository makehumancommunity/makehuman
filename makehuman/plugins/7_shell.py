#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import traceback

import gui3d
import gui
from core import G
import log
from PyQt4 import QtCore, QtGui

class ShellTaskView(gui3d.TaskView):
    def __init__(self, category):
        super(ShellTaskView, self).__init__(category, 'Shell')
        self.globals = {'G': G}
        self.history = []
        self.histitem = None

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

        self.line = gui.TextEdit()
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

        @self.clear.mhEvent
        def onClicked(event):
            self.clearText()

        @self.line.mhEvent
        def onUpArrow(_dummy):
            self.upArrow()

        @self.line.mhEvent
        def onDownArrow(_dummy):
            self.downArrow()

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

def load(app):
    category = app.getCategory('Utilities')
    taskview = category.addTask(ShellTaskView(category))

def unload(app):
    pass

