#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

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

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module contains the Render Task View class to serve as a base class
for task views that implement renderers and rendering related tasks.
"""

from core import G
from guipose import PoseModeTaskView

class RenderTaskView(PoseModeTaskView):
    def __init__(self, category, name, label=None):
        PoseModeTaskView.__init__(self, category, name, label)

        self.oldShader = None
        self.taskViewShader = None

    # Render task views enable pose mode when shown, so that the selected pose
    # is seen and rendered, and a light-based shader (default phong) is
    # selected, so that the actual scene lighting is simulated.

    def onShow(self, event):
        PoseModeTaskView.onShow(self, event)
        import getpath

        human = G.app.selectedHuman
        self.oldShader = human.material.shader
        human.material.shader = getpath.getSysDataPath(self.taskViewShader)

    def onHide(self, event):
        human = G.app.selectedHuman
        human.material.shader = self.oldShader

        PoseModeTaskView.onHide(self, event)

    # renderingWidth, renderingHeight: properties for getting/setting
    # the rendering width and height stored in the settings.

    def getRenderingWidth(self):
        return G.app.settings.get('rendering_width', 800)

    def setRenderingWidth(self, value = None):
        G.app.settings['rendering_width'] = 0 if not value else int(value)

    renderingWidth = property(getRenderingWidth, setRenderingWidth)

    def getRenderingHeight(self):
        return G.app.settings.get('rendering_height', 600)

    def setRenderingHeight(self, value = None):
        G.app.settings['rendering_height'] = 0 if not value else int(value)

    renderingHeight = property(getRenderingHeight, setRenderingHeight)

    # getScene(): Static method for getting the currently selected scene.
    # If scene selector plugin isn't available, it returns the default scene.
    @staticmethod
    def getScene():
        mhscene = None
        try:
            mhscene = G.app.getCategory('Rendering').getTaskByName('Scene').scene
        except:
            import scene
            mhscene = scene.Scene()
        return mhscene
