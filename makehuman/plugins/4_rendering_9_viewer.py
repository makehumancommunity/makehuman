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

