#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius

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
import webbrowser
import mh
import gui
import os
from gui import QtGui

class HelpTaskView(gui3d.TaskView):

    def __init__(self, category):
        
        gui3d.TaskView.__init__(self, category, 'Help')

        aboutBox = self.addLeftWidget(gui.GroupBox('About MakeHuman'))
        self.aboutButton = aboutBox.addWidget(gui.Button("About"))
        self.websiteButton = aboutBox.addWidget(gui.Button("Website"))
        self.facebookButton = aboutBox.addWidget(gui.Button("FaceBook page")) 

        optionsBox = self.addLeftWidget(gui.GroupBox('Support'))
        self.forumButton = optionsBox.addWidget(gui.Button("Forum")) 
        self.manualButton = optionsBox.addWidget(gui.Button("Wiki"))
        self.reportBugButton = optionsBox.addWidget(gui.Button("Report bug"))
        self.requestFeatureButton = optionsBox.addWidget(gui.Button("Request feature"))

        copyBox = self.addLeftWidget(gui.GroupBox('Copy to clipboard'))
        self.versionButton = copyBox.addWidget(gui.Button('Version String'))

        @self.aboutButton.mhEvent
        def onClicked(event):
            gui3d.app.about()

        @self.websiteButton.mhEvent
        def onClicked(event):
            webbrowser.open('http://www.makehumancommunity.org')

        @self.manualButton.mhEvent
        def onClicked(event):
            webbrowser.open('http://www.makehumancommunity.org/wiki/Main_Page')
        
        @self.reportBugButton.mhEvent
        def onClicked(event):
            webbrowser.open('http://bugtracker.makehumancommunity.org/issues/new?project_id=makehuman')
          
        @self.requestFeatureButton.mhEvent
        def onClicked(event):
            webbrowser.open('http://bugtracker.makehumancommunity.org/issues/new?project_id=makehuman&issue[tracker_id]=2')
            
        @self.forumButton.mhEvent
        def onClicked(event):
            webbrowser.open('http://www.makehumancommunity.org/forum')
            
        @self.facebookButton.mhEvent
        def onClicked(event):
            webbrowser.open('https://www.facebook.com/makehuman/')

        @self.versionButton.mhEvent
        def onClicked(event):
            version_string ='v' + mh.getVersionDigitsStr()  + ' ' + os.getenv('HGBRANCH','') \
                            + ' (r' + os.getenv('HGREVISION','') + ' ' + os.getenv('HGNODEID','') + ')'
            gui3d.app.clipboard().setText(version_string)
            
    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        self.manualButton.setFocus()

def load(app):
    category = app.getCategory('Help')
    taskview = category.addTask(HelpTaskView(category))

def unload(app):
    pass


