#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Joel Palmius, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2019

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
import gui
import os
import zipfile
import log
import getpath
import shutil

class UserPluginCheckBox(gui.CheckBox):

    def __init__(self, name, path=''):
        super(UserPluginCheckBox, self).__init__(name, name in gui3d.app.getSetting('activeUserPlugins'))
        self.name = name
        self.path = path

    def onClicked(self, event):
        if self.selected:
            includes = gui3d.app.getSetting('activeUserPlugins')
            includes.append(self.name)
            gui3d.app.setSetting('activeUserPlugins', includes)
        else:
            includes = gui3d.app.getSetting('activeUserPlugins')
            includes.remove(self.name)
            gui3d.app.setSetting('activeUserPlugins', includes)

        gui3d.app.saveSettings()

class UserPluginsTaskView(gui3d.TaskView):

    def __init__(self, category):

        info_msg = "Install new plugins by either copying to the user plugins folder or using the built in installer.\n"\
                   "The installer only handles Python script files and plugin packages in plain zip file format."\
                   "\n\nTo activate a plugin it must be checked in the list. Then click the \"Activate\"-Button or " \
                   "restart MakeHuman.\nTo deactivate a plugin uncheck it in the list and restart MakeHuman."

        gui3d.TaskView.__init__(self, category, 'User Plugins')

        self.userPlugins = getUserPlugins()
        activePlugins = gui3d.app.getSetting('activeUserPlugins')

        for plugin in activePlugins:
            if plugin not in [k for k, _ in self.userPlugins]:
                activePlugins.remove(plugin)

        gui3d.app.setSetting('activeUserPlugins', activePlugins)
        gui3d.app.saveSettings()

        self.home = getpath.getHomePath()

        scroll = self.addTopWidget(gui.VScrollArea())
        self.userPluginBox = gui.GroupBox('User Plugins')
        self.userPluginBox.setSizePolicy(gui.SizePolicy.MinimumExpanding, gui.SizePolicy.Preferred)
        scroll.setWidget(self.userPluginBox)

        self.updatePluginList()

        installWidget = gui.QtWidgets.QWidget()
        installWidgetLayout = gui.QtWidgets.QVBoxLayout()
        installWidget.setLayout(installWidgetLayout)
        self.addLeftWidget(installWidget)

        installBox = gui.GroupBox('')
        self.installPyButton = gui.Button('Install Plugin File')
        installBox.addWidget(self.installPyButton)
        self.installZipButton = gui.Button('Install Zipped Plugin')
        installBox.addWidget(self.installZipButton)
        installWidgetLayout.addWidget(installBox)

        actionsBox = gui.GroupBox('')
        self.reloadButton = gui.Button('Reload Plugins Folder')
        actionsBox.addWidget(self.reloadButton)
        self.activateButton = gui.Button('Activate Plugins')
        actionsBox.addWidget(self.activateButton)
        installWidgetLayout.addWidget(actionsBox)

        infoBox = gui.GroupBox('Info')
        infoText = gui.TextView(info_msg)
        infoText.setWordWrap(True)
        infoText.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.MinimumExpanding)
        infoBox.addWidget(infoText)
        installWidgetLayout.addWidget(infoBox)
        installWidgetLayout.addStretch(1)

        @self.installZipButton.mhEvent
        def onClicked(event):

            filename = getpath.pathToUnicode(gui.QtWidgets.QFileDialog.getOpenFileName(gui3d.app.mainwin, directory=self.home,
                                             filter='Zip files ( *.zip );; All files ( *.* )')[0])

            dest_path = getpath.getPath('plugins')
            if os.path.isfile(filename):
                result = decompress(filename, dest_path)
                if result == 0:
                    self.updatePluginList()
                    gui3d.app.prompt('Info', 'The plugin copied successfully. To activate, check '
                                     'the plugin in the list and press the "Activate"-Button or restart MakeHuman.',
                                     'OK', helpId='installPluginHelp')
                elif result == 3:
                    gui3d.app.prompt('Warning', 'Potentially dangerous zip file, containing files with unsuitable path. '
                                                'Inspect/fix the zip file before usage!', 'OK')
                elif result == 4:
                    gui3d.app.prompt('Error', 'Zip file {0:s} contains exiting files.'.format(filename), 'OK')
                elif result == 1:
                    gui3d.app.prompt('Error', 'Not a zip file {0:s}'.format(filename), 'OK')
            self.home = os.path.dirname(filename)

        @self.installPyButton.mhEvent
        def onClicked(event):
            filename = getpath.pathToUnicode(gui.QtWidgets.QFileDialog.getOpenFileName(gui3d.app.mainwin, directory=self.home,
                                             filter='Python files ( *.py );; All files ( *.* )')[0])
            if os.path.isfile(filename) and os.path.splitext(filename)[1] == '.py':
                try:
                    shutil.copy2(filename, getpath.getPath('plugins'))
                except OSError as e:
                    gui3d.app.prompt('Error', 'Failed to copy {0:s} to user plugins folder'.format(filename), 'OK')
                self.updatePluginList()
                gui3d.app.prompt('Info', 'The plugin copied successfully. To activate, check '
                                 'the plugin in the list and press the "Activate"-Button or restart MakeHuman.',
                                 'OK', helpId='installPluginHelp')
            self.home = os.path.dirname(filename)

        @self.reloadButton.mhEvent
        def onClicked(event):
            self.updatePluginList()

        @self.activateButton.mhEvent
        def onClicked(event):
            for child in self.userPluginBox.children:
                if child.selected:
                    if not child.name in gui3d.app.modules:
                        if not gui3d.app.loadPlugin(name=child.name, location=child.path):
                            gui3d.app.prompt('Error', 'Cannot load module {0:s}\nCheck the log files'.format(child.name), 'OK')
                    else:
                        log.message('Module %s already exists and will not be imported a second time.', child.name)

    def updatePluginList(self):
        for child in self.userPluginBox.children:
            self.userPluginBox.removeWidget(child)
        updatePlugins = getUserPlugins()
        for i, (name, location) in enumerate(sorted(updatePlugins, key=lambda plugin: plugin[0])):
            self.userPluginBox.addWidget(UserPluginCheckBox(name, location), row=i, alignment=gui.QtCore.Qt.AlignTop)


def getUserPlugins():

    pluginsToLoad = []
    user_path = getpath.getPath('plugins')

    for file in os.listdir(user_path):

        location = os.path.join(user_path, file)

        if os.path.isdir(location) and not file.startswith('_'):
            pLocation = os.path.join(location, '__init__.py')
            if os.path.isfile(pLocation):
                pluginsToLoad.append((file, pLocation))

        elif os.path.isfile(location) and file.endswith('.py') and not file.startswith('_'):
            name = os.path.splitext(file)[0]
            pluginsToLoad.append((name, location))

    return pluginsToLoad

def decompress(filename, dest_path):
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
                return 4
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
