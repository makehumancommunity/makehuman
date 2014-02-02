#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module implements the 'Files > Export' tab
"""

import os

import mh
import gui
import gui3d
import guipose
import log

class ExportTaskView(guipose.PoseModeTaskView):
    def __init__(self, category):
        guipose.PoseModeTaskView.__init__(self, category, 'Export')

        self.formats = []
        self.recentlyShown = None
        self._requiresUpdate = True

        exportPath = mh.getPath('exports')

        self.fileentry = self.addTopWidget(gui.FileEntryView('Export', mode='save'))
        self.fileentry.setDirectory(exportPath)
        self.fileentry.setFilter('All Files (*.*)')

        self.exportBodyGroup = []
        self.exportHairGroup = []

        self.posefile = None

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
        def onFileSelected(filename):
            path = os.path.normpath(os.path.join(exportPath, filename))
            dir, name = os.path.split(path)
            name, ext = os.path.splitext(name)

            if not os.path.exists(dir):
                os.makedirs(dir)

            def filename(targetExt, different = False):
                if not different and ext != '' and ('.' + targetExt.lower()) != ext.lower():
                    log.warning("expected extension '.%s' but got '%s'", targetExt, ext)
                return os.path.join(dir, name + '.' + targetExt)

            found = False
            for exporter, radio, options in self.formats:
                if radio.selected:
                    exporter.export(gui3d.app.selectedHuman, filename)
                    found = True
                    break

            if not found:
                log.error("Unknown export format selected!")
                return

            gui3d.app.prompt('Info', u'The mesh has been exported to %s.' % dir, 'OK', helpId='exportHelp')

            mh.changeCategory('Modelling')


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
        self.fileentry.setFilter(filter)
        path,ext = os.path.splitext(unicode(self.fileentry.edit.text()))
        if ext:
            if extension:
                self.fileentry.edit.setText("%s.%s" % (path, extension.lstrip('.')))
            else:
                self.fileentry.edit.setText(path)

    def updateGui(self):
        for exporter, radio, options in self.formats:
            if radio.selected:
                if self.recentlyShown: self.recentlyShown.onHide(self)
                self.optionsBox.showWidget(options)
                self.setFileExtension(exporter.fileExtension, exporter.filter)
                exporter.onShow(self)
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

    def onShow(self, event):
        guipose.PoseModeTaskView.onShow(self, event)

        self.buildGui()

        self.fileentry.setFocus()

        human = gui3d.app.selectedHuman
        skel = human.getSkeleton()
        if skel and skel.object:
            skel.object.show()
        gui3d.app.redraw()


    def onHide(self, event):
        guipose.PoseModeTaskView.onHide(self, event)

        human = gui3d.app.selectedHuman

        skel = human.getSkeleton()
        if skel and skel.object:
            skel.object.hide()
        gui3d.app.redraw()

        for exporter, radio, _ in self.formats:
            if radio.selected:
                exporter.onHide(self)
                break
        self.recentlyShown = None
