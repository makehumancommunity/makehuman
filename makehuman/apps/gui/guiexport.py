#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers, Jonas Hauquier

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

This module implements the 'Files > Export' tab
"""

import os

import mh
import gui
import gui3d
import log


class ExportTaskView(gui3d.TaskView):
    def __init__(self, category):
        super(ExportTaskView, self).__init__(category, 'Export')

        # Declare new settings
        gui3d.app.addSetting('exportdir', mh.getPath("exports"))

        self.formats = []
        self.recentlyShown = None
        self._requiresUpdate = True
        self.showOverwriteWarning = False

        self.fileentry = self.addTopWidget(gui.FileEntryView('Export', mode='save'))
        self.fileentry.directory = gui3d.app.getSetting('exportdir')
        self.fileentry.filter = 'All Files (*.*)'

        self.exportBodyGroup = []
        self.exportHairGroup = []

        # Mesh Formats
        self.formatBox = self.addLeftWidget(gui.GroupBox('Mesh Format'))

        # Rig formats
        self.rigBox = self.addLeftWidget(gui.GroupBox('Rig format'))

        # Map formats
        self.mapsBox = self.addLeftWidget(gui.GroupBox('Maps'))

        self.optionsBox = self.addRightWidget(gui.StackedBox())
        self.optionsBox.setAutoResize(True)

        # Scales
        self.scaleBox = self.addRightWidget(gui.GroupBox('Scale units'))
        self.scaleButtons = self.addScales(self.scaleBox)

        self.boxes = {
            'mesh': self.formatBox,
            'rig': self.rigBox,
            'map': self.mapsBox
            }

        self.updateGui()

        @self.fileentry.mhEvent
        def onFileSelected(event):
            dir, name = os.path.split(event.path)
            name, ext = os.path.splitext(name)

            if not os.path.exists(dir):
                os.makedirs(dir)

            # Remember last used export folder
            gui3d.app.setSetting('exportdir', dir)

            def filename(targetExt, different = False):
                if not different and ext != '' and ('.' + targetExt.lower()) != ext.lower():
                    log.warning("expected extension '.%s' but got '%s'", targetExt, ext)
                return os.path.join(dir, name + '.' + targetExt)

            for exporter in [f[0] for f in self.formats if f[1].selected]:
                if self.showOverwriteWarning and \
                    event.source in ('button', 'return') and \
                    os.path.exists(os.path.join(dir, name + '.' + exporter.fileExtension)):
                    if not gui3d.app.prompt("File exists", "The file already exists. Overwrite?", "Yes", "No"):
                        break;
                exporter.export(gui3d.app.selectedHuman, filename)
                gui3d.app.status([u'The mesh has been exported to',u' %s.'], dir)
                self.showOverwriteWarning = False
                break
            else:
                log.error("Unknown export format selected!")

        @self.fileentry.mhEvent
        def onChange(text):
            self.showOverwriteWarning = True

    _scales = {
        "decimeter": 1.0,
        "meter": 0.1,
        "inch": 1.0/0.254,
        "centimeter": 10.0
        }

    def addScales(self, scaleBox):
        check = True
        buttons = []
        scales = []
        for name in ["decimeter", "meter", "inch", "centimeter"]:
            button = scaleBox.addWidget(gui.RadioButton(scales, name, check))
            check = False
            buttons.append((button,name))
        return buttons

    def getScale(self):
        for (button, name) in self.scaleButtons:
            if button.selected and name in self._scales:
                return (self._scales[name], name)
        return (1, "decimeter")

    def addExporter(self, exporter):
        radio = gui.RadioButton(self.exportBodyGroup, exporter.name)
        radio.exporter = exporter
        options = self.optionsBox.addWidget(gui.GroupBox('Options'))
        exporter.build(options, self)
        self.formats.append((exporter, radio, options))

        @radio.mhEvent
        def onClicked(event):
            self.updateGui()

        self._requiresUpdate = True

    def getExporter(self, exporterName, includeOptions = False):
        for exporterFormat in self.formats:
            exporter, _, options = exporterFormat
            if exporter.name == exporterName:
                if includeOptions:
                    return (exporter, options)
                else:
                    return exporter

    def getExporterNames(self):
        return [exporter.name for exporter, _, _ in self.formats]

    def setFileExtension(self, extension, filter='All Files (*.*)'):
        self.fileentry.filter = filter
        path, ext = os.path.splitext(self.fileentry.text)
        if ext:
            if extension:
                self.fileentry.text = "%s.%s" % (path, extension.lstrip('.'))
            else:
                self.fileentry.text = path

    def updateGui(self):
        for exporter, radio, options in self.formats:
            if radio.selected:
                if self.recentlyShown: self.recentlyShown.onHide(self)
                self.optionsBox.showWidget(options)
                self.setFileExtension(exporter.fileExtension, exporter.filter)
                exporter.onShow(self)
                options.setVisible( len(options.children) > 0 )
                self.recentlyShown = exporter
                break

    def buildGui(self):
        if not self._requiresUpdate:
            return

        for group in self.boxes.keys():
            for eIdx, r in enumerate(self.boxes[group].children):
                self.boxes[group].removeWidget(r)

            exporters = [e for e in self.formats if e[0].group == group]
            exporters.sort(key = lambda e: e[0].orderPriority, reverse = True)

            for (exporter, radio, options) in exporters:
                self.boxes[exporter.group].addWidget(radio)

            # Select first exporter
            if group == 'mesh' and len(self.boxes[group].children) > 0:
                self.boxes[group].children[0].setChecked(True)

        self._requiresUpdate = False
        self.updateGui()

    def onHumanChanged(self, event):
        # If a human was loaded, update the line edit
        if event.change in ('load', 'save'):
            self.fileentry.text = gui3d.app.currentFile.title
        elif event.change == 'reset':
            self.fileentry.text = ""

    def onShow(self, event):
        super(ExportTaskView, self).onShow(event)

        self.buildGui()

        self.fileentry.setFocus()

    def onHide(self, event):
        super(ExportTaskView, self).onHide(event)

        for exporter, radio, _ in self.formats:
            if radio.selected:
                exporter.onHide(self)
                break
        self.recentlyShown = None
