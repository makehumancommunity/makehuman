#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Joel Palmius, Marc Flerackers, Jonas Hauquier

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

import os
import sys
import mh
import gui3d
import gui
import log

from qtui import getExistingDirectory
from getpath import getHomePath, formatPath
from language import language
from filechooser import FileChooserBase as fc

class SettingCheckbox(gui.CheckBox):
    def __init__(self, label, settingName, postAction=None):
        self.setting_name = settingName
        super(SettingCheckbox, self).__init__(label, self.currentValue())
        self.postAction = postAction

    def onClicked(self, event):
        self.updated()

    def updateButton(self, value):
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

    def updateButton(self, value):
        self.setChecked(value)
        self.updated()

    def updated(self):
        if self.selected:
            gui3d.app.setSetting('guiTheme', self.theme)
            gui3d.app.setTheme(self.theme)

class SliderEditWidgetVisibilityRadioButton(gui.RadioButton):
    def __init__(self, group, label, sliderEditWidgetVisibility):
        self.sliderEditWidgetVisibility = sliderEditWidgetVisibility
        checked = (gui3d.app.getSetting('sliderEditWidgetVisibility') == self.sliderEditWidgetVisibility)
        super(SliderEditWidgetVisibilityRadioButton, self).__init__(group, label, checked)

    def onClicked(self, event):
        self.updated()

    def updateButton(self, value):
        self.setChecked(value)
        self.updated()

    def updated(self):
        if self.selected:
            gui3d.app.setSetting('sliderEditWidgetVisibility', self.sliderEditWidgetVisibility)
            gui3d.app.setSliderEditWidgetVisibility(self.sliderEditWidgetVisibility)

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

    def updateButton(self, value):
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
        unitBox = self.addLeftWidget(gui.GroupBox('Units'))
        self.metric = unitBox.addWidget(gui.RadioButton(modes, 'Metric', gui3d.app.getSetting('units') == 'metric'))
        self.imperial = unitBox.addWidget(gui.RadioButton(modes, 'Imperial', gui3d.app.getSetting('units') == 'imperial'))

        weights = []
        weightBox = self.addLeftWidget(gui.GroupBox('Weight'))
        self.rel_weight = weightBox.addWidget(gui.RadioButton(weights, 'Relative Weight', not gui3d.app.getSetting('real_weight')))
        self.real_weight = weightBox.addWidget(gui.RadioButton(weights, 'Real Weight', gui3d.app.getSetting('real_weight')))

        tagFilter = []
        self.tagFilterBox = self.addLeftWidget(gui.GroupBox('Tag Filter Mode'))
        self.or_mode = self.tagFilterBox.addWidget(gui.RadioButton(tagFilter, 'OR', gui3d.app.getSetting('tagFilterMode') == 'OR'), 0, 0)
        self.and_mode = self.tagFilterBox.addWidget(gui.RadioButton(tagFilter, 'AND', gui3d.app.getSetting('tagFilterMode') == 'AND'), 0, 1)
        self.nor_mode = self.tagFilterBox.addWidget(gui.RadioButton(tagFilter, 'NOT OR', gui3d.app.getSetting('tagFilterMode') == 'NOR'), 1, 0)
        self.nand_mode = self.tagFilterBox.addWidget(gui.RadioButton(tagFilter, 'NOT AND', gui3d.app.getSetting('tagFilterMode') == 'NAND'), 1, 1)

        tagsBox = self.addLeftWidget(gui.GroupBox('Tags Count'))
        self.countEdit = tagsBox.addWidget(gui.TextEdit(str(gui3d.app.getSetting('tagCount'))), 0, 0, columnSpan=0)
        tagsBox.addWidget(gui.TextView(' Tags '), 0, 1)
        self.countEdit.textChanged.connect(self.onTextChanged)

        nameBox = self.addLeftWidget(gui.GroupBox('Name Tags:'))
        self.useNameTags = nameBox.addWidget(SettingCheckbox('Use Name Tags', 'useNameTags'))

        self.createFilterModeSwitch()

        startupBox = self.addLeftWidget(gui.GroupBox('Startup'))

        def hdpiPostAction(action):
            if action:
                gui3d.app.prompt('Info', 'You need to restart for these changes to be applied.', 'OK', helpId='useHDPI')

        self.preload = startupBox.addWidget(SettingCheckbox("Preload macro targets", 'preloadTargets'))
        self.saveScreenSize = startupBox.addWidget(SettingCheckbox("Restore window size", 'restoreWindowSize'))
        self.useHDPI = startupBox.addWidget(SettingCheckbox("Use HDPI", 'useHDPI', hdpiPostAction))
        self.noShaders = startupBox.addWidget(SettingCheckbox("No shaders", 'noShaders', hdpiPostAction))
        self.noSampleBuffers = startupBox.addWidget(SettingCheckbox("No sample buffers", 'noSampleBuffers', hdpiPostAction))

        resetBox = self.addLeftWidget(gui.GroupBox('Restore settings'))
        self.resetButton = resetBox.addWidget(gui.Button("Restore to defaults"))

        @self.resetButton.mhEvent
        def onClicked(event):
            gui3d.app.resetSettings()
            self.updateGui()

        homeBox = gui.GroupBox('Configure Home Folder')
        self.addLeftWidget(homeBox)
        self.homeButton = homeBox.addWidget(gui.Button(''))
        if hasConfigFile():
            self.homeButton.setLabel('Delete Config File')
        else:
            self.homeButton.setLabel('Create Config File')

        @self.homeButton.mhEvent
        def onClicked(event):
            if hasConfigFile():
                os.remove(getConfigPath('makehuman.conf'))
                self.homeButton.setLabel('Create Config File')
                gui3d.app.statusPersist('Home Folder Location: Default')
            else:
                filePath = getConfigPath('makehuman.conf')
                homePath = formatPath(getExistingDirectory(getHomePath()))
                if homePath != '.':
                    if sys.platform.startswith('darwin') or sys.platform.startswith('linux') and not os.path.isdir(getConfigPath('')):
                        os.makedirs(getConfigPath(''))
                    if os.path.isdir(homePath) and os.path.isdir(getConfigPath('')):
                        with open(filePath, 'w', encoding='utf-8') as f:
                            f.writelines(homePath + '\n')
                    self.homeButton.setLabel('Delete Config File')
                    gui3d.app.statusPersist('Home Folder Location: ' + homePath)

        self.checkboxes.extend([self.realtimeUpdates, self.realtimeNormalUpdates,
            self.realtimeFitting, self.cameraAutoZoom, self.sliderImages,
            self.useNameTags, self.preload, self.saveScreenSize])

        themes = []
        self.themesBox = self.addRightWidget(gui.GroupBox('Theme'))
        self.themeNative = self.themesBox.addWidget(ThemeRadioButton(themes, "Native look", "default"))
        self.themeMH = self.themesBox.addWidget(ThemeRadioButton(themes, "MakeHuman", "makehuman"))

        sliderEditWidgetVisibilities = []
        self.sliderEditWidgetVisibilityBox = self.addRightWidget(gui.GroupBox('Slider\'s Edit Widget Visibility'))
        self.sliderEditWidgetVisibilityVisible = self.sliderEditWidgetVisibilityBox.addWidget(SliderEditWidgetVisibilityRadioButton(sliderEditWidgetVisibilities, "Visible", True))
        self.sliderEditWidgetVisibilityDefault = self.sliderEditWidgetVisibilityBox.addWidget(SliderEditWidgetVisibilityRadioButton(sliderEditWidgetVisibilities, "Default", False))

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
        if not mh.isRelease():
            self.languageBox.addWidget(LanguageRadioButton(languages,"master"))

        @self.metric.mhEvent
        def onClicked(event):
            gui3d.app.setSetting('units', 'metric')
            gui3d.app.loadGrid()

        @self.imperial.mhEvent
        def onClicked(event):
            gui3d.app.setSetting('units', 'imperial')
            gui3d.app.loadGrid()

        @self.rel_weight.mhEvent
        def onClicked(event):
            gui3d.app.setSetting('real_weight', False)

        @self.real_weight.mhEvent
        def onClicked(event):
            gui3d.app.setSetting('real_weight', True)

        @self.and_mode.mhEvent
        def onClicked(event):
            gui3d.app.setSetting('tagFilterMode', 'AND')

        @self.or_mode.mhEvent
        def onClicked(event):
            gui3d.app.setSetting('tagFilterMode', 'OR')

        @self.nor_mode.mhEvent
        def onClicked(event):
            gui3d.app.setSetting('tagFilterMode', 'NOR')

        @self.nand_mode.mhEvent
        def onClicked(event):
            gui3d.app.setSetting('tagFilterMode', 'NAND')

        self.updateGui()

    def updateGui(self):
        for checkbox in self.checkboxes:
            checkbox.updateButton(checkbox.currentValue())

        use_metric = gui3d.app.getSetting('units') == 'metric'
        if use_metric:
            self.metric.setChecked(True)
        else:
            self.imperial.setChecked(True)
        gui3d.app.loadGrid()

        use_real_weight = gui3d.app.getSetting('real_weight')
        if use_real_weight:
            self.real_weight.setChecked(True)
        else:
            self.rel_weight.setChecked(True)

        lang = gui3d.app.getSetting('language')
        for radioBtn in self.languageBox.children:
            if radioBtn.language == lang:
                radioBtn.updateButton(True)

        theme = gui3d.app.getSetting('guiTheme')
        for radioBtn in self.themesBox.children:
            if radioBtn.theme == theme:
                radioBtn.updateButton(True)

        self.updateTagFilterModes()

    def updateTagFilterModes(self):
        convmodes = {'NOR': 'NOT OR',
                     'NAND': 'NOT AND'}
        mode = convmodes.get(gui3d.app.getSetting('tagFilterMode'), gui3d.app.getSetting('tagFilterMode'))

        for radioBtn in self.tagFilterBox.children:
            radioBtn.setChecked(radioBtn.getLabel() == mode)

        self.countEdit.setText(str(gui3d.app.getSetting('tagCount')))

    def createFilterModeSwitch(self):
        action = gui.Action('switchFilterMode', language.getLanguageString('Switch Filter Mode'), self.switchFilterMode)
        gui3d.app.mainwin.addAction(action)
        mh.setShortcut(mh.Modifiers.ALT, mh.Keys.f, action)

    def switchFilterMode(self):
        modes = ['OR', 'AND', 'NOR', 'NAND']
        index = (modes.index(gui3d.app.getSetting('tagFilterMode')) + 1) % 4
        gui3d.app.setSetting('tagFilterMode', modes[index])
        self.updateTagFilterModes()
        for switchFunc in fc.switchFuncList:
            switchFunc()

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        gui3d.app.statusPersist('Home Folder Location: ' + getHomePath())

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)
        gui3d.app.saveSettings()
        gui3d.app.statusPersist('')

    def onTextChanged(self):
        text = self.countEdit.text
        if text.isdigit():
            gui3d.app.setSetting('tagCount', int(text))
        else:
            self.countEdit.setText(str(gui3d.app.getSetting('tagCount')))

def load(app):
    category = app.getCategory('Settings')
    taskview = category.addTask(SettingsTaskView(category))

def unload(app):
    pass


def getConfigPath(filename = ''):
    if sys.platform.startswith('linux'):
        return os.path.expanduser(os.path.join('~/.config', filename))
    elif sys.platform.startswith('darwin'):
        return os.path.expanduser(os.path.join('~/Library/Application Support/MakeHuman', filename))
    elif sys.platform.startswith('win32'):
        return os.path.join(os.getenv('LOCALAPPDATA',''), filename)
    else:
        return ''

def hasConfigFile():
    return os.path.isfile(getConfigPath('makehuman.conf'))
