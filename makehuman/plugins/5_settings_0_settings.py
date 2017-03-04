#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius, Marc Flerackers, Jonas Hauquier

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

import os
import mh
import gui3d
import gui
import log

class SettingCheckbox(gui.CheckBox):
    def __init__(self, label, settingName, postAction=None):
        self.setting_name = settingName
        super(SettingCheckbox, self).__init__(label, self.currentValue())
        self.postAction = postAction

    def onClicked(self, event):
        self.updated()

    def update(self, value):
        if value is None:
            self.setChecked(gui3d.app.getSettingDefault(self.setting_name))
        else:
            self.setChecked(value)
        self.updated()

    def updated(self):
        gui3d.app.setSetting(self.setting_name, self.selected)
        if self.postAction is not None:
            self.postAction(self.selected)

    def currentValue(self):
        return gui3d.app.getSetting(self.setting_name)

class ThemeRadioButton(gui.RadioButton):
    def __init__(self, group, label, theme):
        self.theme = theme
        checked = (gui3d.app.getSetting('guiTheme') == self.theme)
        super(ThemeRadioButton, self).__init__(group, label, checked)

    def onClicked(self, event):
        self.updated()

    def update(self, value):
        self.setChecked(value)
        self.updated()

    def updated(self):
        if self.selected:
            gui3d.app.setSetting('guiTheme', self.theme)
            gui3d.app.setTheme(self.theme)

class PlatformRadioButton(gui.RadioButton):
    def __init__(self, group, looknfeel):
        super(PlatformRadioButton, self).__init__(group, looknfeel, gui3d.app.getLookAndFeel().lower() == looknfeel.lower())
        self.looknfeel = looknfeel

    def onClicked(self, event):
        gui3d.app.setLookAndFeel(self.looknfeel)

class LanguageRadioButton(gui.RadioButton):
    def __init__(self, group, language):
        super(LanguageRadioButton, self).__init__(group, language.capitalize(), gui3d.app.getSetting('language') == language)
        self.language = language
        
    def onClicked(self, event):
        self.updated()
        gui3d.app.prompt('Info', 'You need to restart for your language changes to be applied.', 'OK', helpId='languageHelp')

    def update(self, value):
        self.setChecked(value)
        self.updated()

    def updated(self):
        if self.selected:
            gui3d.app.setSetting('language', self.language)
            gui3d.app.setLanguage(self.language)

class SettingsTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'General')
        self.checkboxes = []

        sliderBox = self.addLeftWidget(gui.GroupBox('Slider behavior'))
        self.realtimeUpdates = sliderBox.addWidget(SettingCheckbox("Update real-time", 'realtimeUpdates'))

        self.realtimeNormalUpdates = sliderBox.addWidget(SettingCheckbox("Update normals real-time", 'realtimeNormalUpdates'))

        self.realtimeFitting = sliderBox.addWidget(SettingCheckbox("Fit objects real-time", 'realtimeFitting'))

        self.cameraAutoZoom = sliderBox.addWidget(SettingCheckbox("Auto-zoom camera", 'cameraAutoZoom'))

        def updateSliderImages(selected):
            gui.Slider.showImages(selected)
            mh.refreshLayout()
        self.sliderImages = sliderBox.addWidget(SettingCheckbox("Slider images", 'sliderImages', updateSliderImages))
            
        modes = []
        unitBox = self.unitsBox = self.addLeftWidget(gui.GroupBox('Units'))
        self.metric = unitBox.addWidget(gui.RadioButton(modes, 'Metric', gui3d.app.getSetting('units') == 'metric'))
        self.imperial = unitBox.addWidget(gui.RadioButton(modes, 'Imperial', gui3d.app.getSetting('units') == 'imperial'))

        startupBox = self.addLeftWidget(gui.GroupBox('Startup'))
        self.preload = startupBox.addWidget(SettingCheckbox("Preload macro targets", 'preloadTargets'))

        self.saveScreenSize = startupBox.addWidget(SettingCheckbox("Restore window size", 'restoreWindowSize'))

        resetBox = self.addLeftWidget(gui.GroupBox('Restore settings'))
        self.resetButton = resetBox.addWidget(gui.Button("Restore to defaults"))
        @self.resetButton.mhEvent
        def onClicked(event):
            gui3d.app.resetSettings()
            self.updateGui()

        self.checkboxes.extend([self.realtimeUpdates, self.realtimeNormalUpdates,
            self.realtimeFitting, self.cameraAutoZoom, self.sliderImages,
            self.preload, self.saveScreenSize])

        themes = []
        self.themesBox = self.addRightWidget(gui.GroupBox('Theme'))
        self.themeNative = self.themesBox.addWidget(ThemeRadioButton(themes, "Native look", "default"))
        self.themeMH = self.themesBox.addWidget(ThemeRadioButton(themes, "MakeHuman", "makehuman"))

        # For debugging themes on multiple platforms
        '''
        platforms = []
        platformsBox = self.platformsBox = self.addRightWidget(gui.GroupBox('Look and feel'))
        for platform in gui3d.app.getLookAndFeelStyles():
            platformsBox.addWidget(PlatformRadioButton(platforms, platform))
        '''

        languages = []
        self.languageBox = self.addRightWidget(gui.GroupBox('Language'))
        
        languageFiles = gui3d.app.getLanguages()
        for language in languageFiles:
            if not language.lower() == "master":
                self.languageBox.addWidget(LanguageRadioButton(languages, language))

        @self.metric.mhEvent
        def onClicked(event):
            gui3d.app.setSetting('units', 'metric')
            gui3d.app.loadGrid()

        @self.imperial.mhEvent
        def onClicked(event):
            gui3d.app.setSetting('units', 'imperial')
            gui3d.app.loadGrid()

        self.updateGui()

    def updateGui(self):
        for checkbox in self.checkboxes:
            checkbox.update(checkbox.currentValue())

        use_metric = gui3d.app.getSetting('units') == 'metric'
        if use_metric:
            self.metric.setChecked(True)
            gui3d.app.setSetting('units', 'metric')
        else:
            self.imperial.setChecked(True)
            gui3d.app.setSetting('units', 'imperial')
        gui3d.app.loadGrid()

        lang = gui3d.app.getSetting('language')
        for radioBtn in self.languageBox.children:
            if radioBtn.language == lang:
                radioBtn.update(True)

        theme = gui3d.app.getSetting('guiTheme')
        for radioBtn in self.themesBox.children:
            if radioBtn.theme == theme:
                radioBtn.update(True)

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)
        gui3d.app.saveSettings()

def load(app):
    category = app.getCategory('Settings')
    taskview = category.addTask(SettingsTaskView(category))

def unload(app):
    pass


