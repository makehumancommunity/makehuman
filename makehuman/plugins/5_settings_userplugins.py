#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius, Jonas Hauquier

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
import gui
import os
import glob
import zipfile
import log
import getpath

class UserPluginCheckBox(gui.CheckBox):

    def __init__(self, module):
        super(UserPluginCheckBox, self).__init__(module, module in gui3d.app.getSetting('activeUserPlugins'))
        self.module = module

    def onClicked(self, event):
        if self.selected:
            includes = gui3d.app.getSetting('activeUserPlugins')
            includes.append(self.module)
            gui3d.app.setSetting('activeUserPlugins', includes)
        else:
            includes = gui3d.app.getSetting('activeUserPlugins')
            includes.remove(self.module)
            gui3d.app.setSetting('activeUserPlugins', includes)

        gui3d.app.saveSettings()

class UserPluginsTaskView(gui3d.TaskView):

    def __init__(self, category):

        info_msg = u"Install new plugins by either copying to the user plugins folder or using the built in installer. "\
                   u"The installer only handles plugin packages in plain zip file format. To (de-)activate a plugin "\
                   u"it must be (un-)checked in the list. Changes only come into effect after MakeHuman is restarted."

        gui3d.TaskView.__init__(self, category, 'User Plugins')

        userPlugins = self.getUserPlugins()
        activePlugins = gui3d.app.getSetting('activeUserPlugins')

        for plugin in activePlugins:
            if plugin not in userPlugins:
                activePlugins.remove(plugin)

        gui3d.app.setSetting('activeUserPlugins', activePlugins)
        gui3d.app.saveSettings()

        self.scroll = self.addTopWidget(gui.VScrollArea())
        self.userPluginBox = gui.GroupBox('User Plugins')
        self.userPluginBox.setSizePolicy(gui.SizePolicy.MinimumExpanding, gui.SizePolicy.Preferred)
        self.scroll.setWidget(self.userPluginBox)

        for i, plugin in enumerate(userPlugins):
            self.userPluginBox.addWidget(UserPluginCheckBox(plugin), row=i, alignment=gui.QtCore.Qt.AlignTop)

        self.installWidget = gui.QtWidgets.QWidget()
        installWidgetLayout = gui.QtWidgets.QVBoxLayout()
        self.installWidget.setLayout(installWidgetLayout)
        self.addLeftWidget(self.installWidget)

        self.installBox = gui.GroupBox('')
        self.installButton = gui.Button('Install Zipped Plugins')
        self.installBox.addWidget(self.installButton)
        installWidgetLayout.addWidget(self.installBox)

        self.reloadBox = gui.GroupBox('')
        self.reloadButton = gui.Button('Reload Plugins Folder')
        self.reloadBox.addWidget(self.reloadButton)
        installWidgetLayout.addWidget(self.reloadBox)

        self.infoBox = gui.GroupBox('Info')
        self.infoText = gui.TextView(info_msg)
        self.infoText.setWordWrap(True)
        self.infoText.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.MinimumExpanding)
        self.infoBox.addWidget(self.infoText)
        installWidgetLayout.addWidget(self.infoBox)
        installWidgetLayout.addStretch(1)

        @self.installButton.mhEvent
        def onClicked(event):
            filename = None
            home = os.path.expanduser('~')
            filename = getpath.pathToUnicode(gui.QtWidgets.QFileDialog.getOpenFileName(gui3d.app.mainwin, directory=home,
                                             filter='Zip files ( *.zip );; All files ( *.* )'))
            dest_path = getpath.getPath('plugins')
            if filename:
                result = self.decompress(filename, dest_path)
                if result == 1:
                    gui3d.app.prompt('Error', 'Not a zip file {0}'.format(filename), 'OK')
                elif result == 3:
                    gui3d.app.prompt('Warning', 'Potentially dangerous zip file, containing files with unsuitable path. '\
                                                'Inspect/fix the zip file before usage!', 'OK')
                elif result == -1:
                    gui3d.app.prompt('Error', 'Zip file {0} contains exiting files.'.format(filename), 'OK')
                elif result == 0:
                    gui3d.app.prompt('Info', 'The plugin copied successfully. To activate check '
                                               'the plugin in the list and restart MakeHuman.', 'OK', helpId='installPluginHelp' )
                    for child in self.userPluginBox.children:
                        self.userPluginBox.removeWidget(child)
                    updatePlugins = self.getUserPlugins()
                    for i, plugin in enumerate(updatePlugins):
                        self.userPluginBox.addWidget(UserPluginCheckBox(plugin), row = i, alignment=gui.QtCore.Qt.AlignTop)

        @self.reloadButton.mhEvent
        def onClicked(event):
            for child in self.userPluginBox.children:
                self.userPluginBox.removeWidget(child)
            updatePlugins = self.getUserPlugins()
            for i, plugin in enumerate(updatePlugins):
                self.userPluginBox.addWidget(UserPluginCheckBox(plugin), row=i, alignment=gui.QtCore.Qt.AlignTop)

    def getUserPlugins(self):
        pluginList = []

        userPlugins = glob.glob(getpath.getPath(os.path.join("plugins/", '[!_]*.py')))
        if userPlugins:
            for userPlugin in userPlugins:
                pluginList.append(os.path.splitext(os.path.basename(userPlugin))[0])

        for fname in os.listdir(getpath.getPath("plugins/")):
            if fname[0] != "_":
                    folder = os.path.join("plugins", fname)
                    if os.path.isdir(getpath.getPath(folder)) and ("__init__.py" in os.listdir(getpath.getPath(folder))):
                        pluginList.append(fname)

        pluginList.sort()
        return pluginList

    def decompress(self, filename, dest_path):
        if not zipfile.is_zipfile(filename):
            log.message('Not a zip file: {0}'.format(filename))
            return 1
        if not os.path.isdir(dest_path):
            log.message('Not a directory: {0}'.format(dest_path))
            return 2
        with zipfile.ZipFile(filename) as zf:
            for f in zf.infolist():
                if os.path.isabs(os.path.split(f.filename)[0]) or '..' in os.path.split(f.filename)[0]:
                    log.warning('Potentially dangerous zip file, '
                                'containing files with unsuitable path: {0}  {1}'.format(filename, f.filename))
                    return 3
                if os.path.exists(os.path.join(dest_path, f.filename)):
                    log.warning('Zip file contains existing file: {0}  {1}'.format(filename, f.filename))
                    return -1
            try:
                zf.extractall(dest_path)
            except:
                pass
        return 0

def load(app):
    category = app.getCategory('Settings')
    taskview = category.addTask(UserPluginsTaskView(category))

def unload(app):
    pass