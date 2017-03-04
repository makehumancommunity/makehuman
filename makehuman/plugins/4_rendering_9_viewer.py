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

Image viewer plugin .
Useful for showing the rendering results.
It can also be used to view other MH related image files,
like textures, bump maps etc.
"""

import os

import gui
import gui3d
import mh
import log

class ViewerTaskView(gui3d.TaskView):
    def __init__(self, category):
        super(ViewerTaskView, self).__init__(category, 'Viewer')
        self.image = self.addTopWidget(gui.ZoomableImageView())
        self.path = None

        tools = self.addLeftWidget(gui.GroupBox('Tools'))
        self.refrBtn = tools.addWidget(gui.Button('Refresh'))
        self.saveBtn = tools.addWidget(gui.Button('Save As...'))

        @self.saveBtn.mhEvent
        def onClicked(event):
            if not self.path:
                if not os.path.exists(mh.getPath('render')):
                    os.makedirs(mh.getPath('render'))
                self.path = mh.getPath('render')
            filename = mh.getSaveFileName(os.path.splitext(self.path)[0],
                                          'PNG Image (*.png);;JPEG Image (*.jpg);;All files (*.*)')
            if filename:
                self.path = os.path.dirname(filename)
                self.image.save(filename)

        @self.refrBtn.mhEvent
        def onClicked(event):
            if not self.path:
                return
            self.image.setImage(self.path)

    def setImage(self, path):
        if isinstance(path, basestring):
            self.path = path
        else:
            self.path = None
        self.image.setImage(path)
        log.message('Image "%s" loaded in image viewer.', path)

def load(app):
    category = app.getCategory('Rendering')
    taskview = ViewerTaskView(category)
    taskview.sortOrder = 2.0
    category.addTask(taskview)

def unload(app):
    pass

