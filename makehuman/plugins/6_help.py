#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Manuel Bastioni

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

TODO
"""

import gui3d
import webbrowser
import mh
import gui

class HelpTaskView(gui3d.TaskView):

    def __init__(self, category):
        
        gui3d.TaskView.__init__(self, category, 'Help')

        optionsBox = self.addLeftWidget(gui.GroupBox('Support options'))
        self.manualButton = optionsBox.addWidget(gui.Button("Manual"))
        self.reportBugButton = optionsBox.addWidget(gui.Button("Report bug"))
        self.requestFeatureButton = optionsBox.addWidget(gui.Button("Request feature"))   
        self.forumButton = optionsBox.addWidget(gui.Button("Forum")) 
        self.facebookButton = optionsBox.addWidget(gui.Button("FaceBook page"))        
        
        @self.manualButton.mhEvent
        def onClicked(event):
            webbrowser.open('http://www.makehuman.org/documentation');
        
        @self.reportBugButton.mhEvent
        def onClicked(event):
            webbrowser.open('http://bugtracker.makehuman.org/issues/new?project_id=makehuman');
          
        @self.requestFeatureButton.mhEvent
        def onClicked(event):
            webbrowser.open('http://bugtracker.makehuman.org/issues/new?project_id=makehuman&issue[tracker_id]=2');
            
        @self.forumButton.mhEvent
        def onClicked(event):
            webbrowser.open('http://www.makehuman.org/forum/');
            
        @self.facebookButton.mhEvent
        def onClicked(event):
            webbrowser.open('https://www.facebook.com/makehuman/');
            
            
    def onShow(self, event):
    
        gui3d.TaskView.onShow(self, event)
        self.manualButton.setFocus()

def load(app):
    category = app.getCategory('Help')
    taskview = category.addTask(HelpTaskView(category))

def unload(app):
    pass


