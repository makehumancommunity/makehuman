#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""

Internal OpenGL Renderer Plugin.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thanasis Papoutsidakis

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

from . import mh2opengl

from core import G
import gui
from guirender import RenderTaskView
import mh


class OpenGLTaskView(RenderTaskView):

    def __init__(self, category):
        RenderTaskView.__init__(self, category, 'Render')

        # Declare settings
        G.app.addSetting('GL_RENDERER_SSS', False)
        G.app.addSetting('GL_RENDERER_AA', True)

        # Don't change shader for this RenderTaskView.
        self.taskViewShader = G.app.selectedHuman.material.shader

        settingsBox = self.addLeftWidget(gui.GroupBox('Settings'))
        settingsBox.addWidget(gui.TextView("Resolution"))
        self.resBox = settingsBox.addWidget(gui.TextEdit(
            "x".join([str(self.renderingWidth), str(self.renderingHeight)])))
        self.AAbox = settingsBox.addWidget(gui.CheckBox("Anti-aliasing"))
        self.AAbox.setSelected(G.app.getSetting('GL_RENDERER_AA'))
        self.renderButton = settingsBox.addWidget(gui.Button('Render'))

        self.lightmapSSS = gui.CheckBox("Lightmap SSS")
        self.lightmapSSS.setSelected(G.app.getSetting('GL_RENDERER_SSS'))

        self.optionsBox = self.addLeftWidget(gui.GroupBox('Options'))
        self.optionsWidgets = []

        renderMethodBox = self.addRightWidget(gui.GroupBox('Rendering methods'))
        self.renderMethodList = renderMethodBox.addWidget(gui.ListView())
        self.renderMethodList.setSizePolicy(
            gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)

        # Rendering methods
        self.renderMethodList.addItem('Quick Render')
        self.renderMethodList.addItem('Advanced Render',
            data=[self.lightmapSSS])

        if not mh.hasRenderToRenderbuffer():
            self.firstTimeWarn = True
            # Can only use screen grabbing as fallback,
            # resolution option disabled
            self.resBox.setEnabled(False)
            self.AAbox.setEnabled(False)

        self.listOptions(None)

        @self.resBox.mhEvent
        def onChange(value):
            try:
                value = value.replace(" ", "")
                res = [int(x) for x in value.split("x")]
                self.renderingWidth = res[0]
                self.renderingHeight = res[1]
            except:  # The user hasn't typed the value correctly yet.
                pass

        @self.AAbox.mhEvent
        def onClicked(value):
            G.app.setSetting('GL_RENDERER_AA', self.AAbox.selected)

        @self.lightmapSSS.mhEvent
        def onClicked(value):
            G.app.setSetting('GL_RENDERER_SSS', self.lightmapSSS.selected)

        @self.renderMethodList.mhEvent
        def onClicked(item):
            self.listOptions(item.getUserData())

        @self.renderButton.mhEvent
        def onClicked(event):
            settings = dict()
            settings['scene'] = G.app.scene
            settings['AA'] = self.AAbox.selected
            settings['dimensions'] = (self.renderingWidth, self.renderingHeight)
            settings['lightmapSSS'] = self.lightmapSSS.selected and self.lightmapSSS in self.optionsWidgets

            mh2opengl.Render(settings)

    def onShow(self, event):
        RenderTaskView.onShow(self, event)
        self.renderButton.setFocus()
        if not mh.hasRenderToRenderbuffer() and self.firstTimeWarn:
            self.firstTimeWarn = False
            G.app.prompt('Lack of 3D hardware support',
                'Your graphics card lacks support for proper rendering.\nOnly limited functionality will be available.',
                'Ok', None, None, None, 'renderingGPUSupportWarning')

    def onHide(self, event):
        RenderTaskView.onHide(self, event)

    def listOptions(self, widgets):
        for child in self.optionsBox.children[:]:
            self.optionsBox.removeWidget(child)

        if widgets:
            self.optionsWidgets = widgets
            self.optionsBox.show()
            for widget in widgets:
                self.optionsBox.addWidget(widget)
        else:
            self.optionsWidgets = []
            self.optionsBox.hide()


def load(app):
    category = app.getCategory('Rendering')
    taskview = OpenGLTaskView(category)
    taskview.sortOrder = 1.3
    category.addTask(taskview)


def unload(app):
    pass
