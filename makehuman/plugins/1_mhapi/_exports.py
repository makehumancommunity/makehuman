#!/usr/bin/python

from .namespace import NameSpace

import getpath
import os
import sys
import gui3d
import gui
import mh

class Exports(NameSpace):
    """This namespace wraps all calls that are related to producing file output."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()

    def _getExportTaskView(self):
        return self.api.ui.getTaskView("Files","Export")

    def getExportFormats(self):
        tv = self._getExportTaskView()
        return list(tv.formats)

    def getExporterByClassname(self, className):
        className = className.lower()
        for f in self.getExportFormats():
            cn = str(type(f[0])).lower()
            if className in cn:
                return f[0]
        return None

    def _getDummyFileEntry(self, outputFilename, useExportsDir=True):
        def fileentry(ext):
            of = outputFilename
            if useExportsDir:
                of = os.path.basename(of)
                ed = mh.getPath("exports")
                of = os.path.join(ed,of)
            return of
        return fileentry

    def getOBJExporter(self):
        return self.getExporterByClassname("ExporterOBJ")

    def getFBXExporter(self):
        return self.getExporterByClassname("ExporterFBX")

    def getDAEExporter(self):
        return self.getExporterByClassname("ExporterCollada")

    def getMHX2Exporter(self):
        return self.getExporterByClassname("ExporterMHX2")

    def exportAsOBJ(self, outputFilename, useExportsDir=True):
        """Export the current toon as wavefront obj."""
        e = self.getOBJExporter()
        human = gui3d.app.selectedHuman
        fileentry = self._getDummyFileEntry(outputFilename, useExportsDir)
        e.export(human, fileentry)

    def exportAsFBX(self, outputFilename, useExportsDir=True):
        """Export the current toon as wavefront obj."""
        e = self.getFBXExporter()
        human = gui3d.app.selectedHuman
        fileentry = self._getDummyFileEntry(outputFilename, useExportsDir)
        e.export(human, fileentry)

    def exportAsDAE(self, outputFilename, useExportsDir=True):
        """Export the current toon as wavefront obj."""
        e = self.getDAEExporter()
        human = gui3d.app.selectedHuman
        fileentry = self._getDummyFileEntry(outputFilename, useExportsDir)
        e.export(human, fileentry)

    def exportAsMHX2(self, outputFilename, useExportsDir=True):
        """Export the current toon as wavefront obj."""
        e = self.getMHX2Exporter()
        human = gui3d.app.selectedHuman
        fileentry = self._getDummyFileEntry(outputFilename, useExportsDir)
        e.export(human, fileentry)


