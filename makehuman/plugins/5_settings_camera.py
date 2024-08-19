#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Joel Palmius, Marc Flerackers

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

TODO
"""


import gui3d
import mh
import gui


class CameraActionsTaskView(gui3d.TaskView):
    def __init__(self, category) -> None:
        super().__init__(self, category, 'Camera')

        self.cameraBox = self.addLeftWidget(gui.GroupBox('Camera'))


        self.orthogonal = self.cameraBox.addWidget(
                gui.CheckBox(
                    label = "Orthogonal/Perspective",
                    selected = True if gui3d.app.modelCamera.getProjection() == 0 else False
                )
        )

        self.fovAngle = self.cameraBox.addWidget(
                gui.Slider(
                    value = gui3d.app.modelCamera.getFovAngle(),
                    min = 1, max = 171,
                    label = ["Fov Angle",": %d"]
                )
        )


        @self.orthogonal.mhEvent
        def onClicked(event):
            if self.orthogonal.selected == True:
                gui3d.app.modelCamera.switchToOrtho()
            else:
                gui3d.app.modelCamera.switchToPerspective()


        @self.fovAngle.mhEvent
        def onChange(value):
            gui3d.app.modelCamera.setFovAngle(value)

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        # gui3d.app.statusPersist("Change camera settings")

    def onHide(self, event):
        # gui3d.app.statusPersist("")
        gui3d.TaskView.onHide(self, event)


def load(app):
    category = app.getCategory('Settings')
    taskview = category.addTask(CameraActionsTaskView(category))

def unload(app):
    pass
