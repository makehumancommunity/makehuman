#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Joel Palmius

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
import webbrowser
import mh
import gui
import os
from mhversion import MHVersion

class HelpTaskView(gui3d.TaskView):

    def __init__(self, category):
        
        gui3d.TaskView.__init__(self, category, 'Help')

        aboutBox = self.addLeftWidget(gui.GroupBox('About MakeHuman'))
        self.aboutButton = aboutBox.addWidget(gui.Button('About / License'))
        self.websiteButton = aboutBox.addWidget(gui.Button('Website'))
        self.facebookButton = aboutBox.addWidget(gui.Button('FaceBook page'))

        optionsBox = self.addLeftWidget(gui.GroupBox('Support'))
        self.faqButton = optionsBox.addWidget(gui.Button('FAQ'))
        self.forumButton = optionsBox.addWidget(gui.Button('Forum'))
        self.manualButton = optionsBox.addWidget(gui.Button('Wiki'))
        self.patreonButton = optionsBox.addWidget(gui.Button('Patreon'))
        self.reportBugButton = optionsBox.addWidget(gui.Button('Report bug'))
        self.requestFeatureButton = optionsBox.addWidget(gui.Button('Request feature'))

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
            webbrowser.open('http://www.makehumancommunity.org/content/bugtracker.html')
          
        @self.requestFeatureButton.mhEvent
        def onClicked(event):
            webbrowser.open('http://www.makehumancommunity.org/forum/viewforum.php?f=3')

        @self.faqButton.mhEvent
        def onClicked(event):
            webbrowser.open('http://www.makehumancommunity.org/wiki/FAQ:Index')

        @self.forumButton.mhEvent
        def onClicked(event):
            webbrowser.open('http://www.makehumancommunity.org/forum')

        @self.patreonButton.mhEvent
        def onClicked(event):
            webbrowser.open('https://www.patreon.com/makehuman/overview')

        @self.facebookButton.mhEvent
        def onClicked(event):
            webbrowser.open('https://www.facebook.com/makehuman/')

        @self.versionButton.mhEvent
        def onClicked(event):
            mhv = MHVersion()
            gui3d.app.clipboard().setText(mhv.getFullVersionStr())
            
    def onShow(self, event):
    
        gui3d.TaskView.onShow(self, event)
        self.manualButton.setFocus()

def load(app):
    category = app.getCategory('Help')
    taskview = category.addTask(HelpTaskView(category))

def unload(app):
    pass


