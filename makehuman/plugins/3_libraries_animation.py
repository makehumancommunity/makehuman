#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Jonas Hauquier, punkduck

**Copyright(c):**      MakeHuman Team 2001-2020

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

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

Animation   this plugin displays all frames of a loaded pose when a skeleton is available
            the camera is set to no autoscale
"""

import mh
import gui
import gui3d
from core import G

from PyQt5 import QtGui
from PyQt5.QtWidgets import QStyle, QApplication

class AnimationLibrary(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Animations')

        # we need a different color to make the standard icons visible
        #
        pcolor= "background-color :#e0e0e0"
        standardIcon = QApplication.style().standardIcon

        self.human = gui3d.app.selectedHuman
        self.currentframe = 0

        box = self.addLeftWidget(gui.GroupBox('Animations'))

        self.playbackSlider = box.addWidget(gui.Slider(label='Frame'))
        self.playbackSlider.setMin(0)
        self.frameLbl = box.addWidget(gui.TextView(''))
        self.frameLbl.setTextFormat(u"Frame: %s", 0)

        playerbox  = box.addWidget(gui.QtWidgets.QGroupBox('Position'))
        layout = gui.QtWidgets.QGridLayout()
        playerbox.setLayout(layout)

        self.btn1 =gui.Button()
        self.btn1.setIcon(standardIcon(QStyle.SP_MediaSkipBackward))
        self.btn1.setStyleSheet(pcolor)
        self.btn1.setToolTip("Set to first frame")
        layout.addWidget(self.btn1,0,0)

        self.btn2 =gui.Button()
        self.btn2.setIcon(standardIcon(QStyle.SP_MediaSeekBackward))
        self.btn2.setStyleSheet(pcolor)
        self.btn2.setToolTip("One frame backward")
        layout.addWidget(self.btn2,0,1)

        self.btn3 =gui.Button()
        self.btn3.setIcon(standardIcon(QStyle.SP_MediaSeekForward))
        self.btn3.setStyleSheet(pcolor)
        self.btn3.setToolTip("One frame forward")
        layout.addWidget(self.btn3,0,2)

        self.btn4 =gui.Button()
        self.btn4.setIcon(standardIcon(QStyle.SP_MediaSkipForward))
        self.btn4.setStyleSheet(pcolor)
        self.btn4.setToolTip("Set to last frame")
        layout.addWidget(self.btn4,0,3)

        self.messageBox = box.addWidget(gui.TextView(''))

        @self.btn1.mhEvent
        def onClicked(event):
            self.currentframe = 0
            self.updateFrame()

        @self.btn2.mhEvent
        def onClicked(event):
            if self.currentframe > 0:
                self.currentframe -= 1
                self.updateFrame()

        @self.btn3.mhEvent
        def onClicked(event):
            if self.currentframe < self.nFrames -1:
                self.currentframe += 1
                self.updateFrame()

        @self.btn4.mhEvent
        def onClicked(event):
            if self.nFrames > 1:
                self.currentframe = self.nFrames -1
                self.updateFrame()

        @self.playbackSlider.mhEvent
        def onChange(value):
            self.currentframe = int(value)
            self.updateFrame()

        @self.playbackSlider.mhEvent
        def onChanging(value):
            self.currentframe = int(value)
            self.updateFrame()

    def toggleEnable(self, enable, reason):
        for button in [self.playbackSlider, self.btn1, self.btn2, self.btn3, self.btn4]:
            button.setEnabled(enable)
        self.messageBox.setText("<br>" + reason)
        if not enable:
            self.playbackSlider.setValue(0)
            self.frameLbl.setTextFormat(["Frame",": %s"], self.currentframe)

    def updateFrame(self):
        self.human.setToFrame(self.currentframe)
        self.human.refreshPose()                    # needed otherwise proxies will not refresh
        self.playbackSlider.setValue(self.currentframe)
        self.frameLbl.setTextFormat(["Frame",": %s"], self.currentframe)

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        if gui3d.app.getSetting('cameraAutoZoom'):
            gui3d.app.setGlobalCamera()

        self.nFrames = self.human.getActiveAnimation().nFrames if self.human.getActiveAnimation() else 0
        #
        # reset this value in case a new shorter pose was loaded inbetween
        #
        if self.currentframe > self.nFrames -1:
            self.currentframe = 0

        if self.human.getSkeleton():
            if self.nFrames > 1:
                self.playbackSlider.setMax(self.nFrames-1)
                self.toggleEnable(True, "<font color='#00ff00'>" + str(self.nFrames) + " frames available</font>")
                G.cameras[0].noAutoScale = True
                G.cameras[1].noAutoScale = True
            else:
                self.toggleEnable(False, "<font color='yellow'>Only one frame available</font>")
        else:
            self.toggleEnable(False, "<font color='red'>Please select a skeleton first</font>")

    def onHide(self, event):
        G.cameras[0].noAutoScale = False
        G.cameras[1].noAutoScale = False
        gui3d.TaskView.onHide(self, event)

    def onHumanChanged(self, event):
        human = event.human
        if event.change == 'reset':
            if self.isShown():
                # Refresh onShow status
                self.onShow(event)


def load(app):
    category = app.getCategory('Pose/Animate')
    maintask = AnimationLibrary(category)
    maintask.sortOrder = 8
    category.addTask(maintask)


def unload(app):
    pass
