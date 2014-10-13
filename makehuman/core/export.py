#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

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

Common base class for all exporters.
"""

from core import G
import log


class Exporter(object):
    """
    Exporter GUI widget for use within ExportTaskView
    """

    def __init__(self):
        self.group = "mesh"
        self.fileExtension = ""
        self.filter = 'All Files (*.*)'
        self.orderPriority = 10.0   # Priority that determines order of exporter in gui. Highest priority is on top.

    def build(self, options, taskview):
        import gui

        self.taskview       = taskview
        self.feetOnGround   = options.addWidget(gui.CheckBox("Feet on ground", True))

    def export(self, human, filename):
        raise NotImplementedError()

    def getConfig(self, update):
        raise NotImplementedError("getConfig not implemented for Exporter")

    def onShow(self, exportTaskView):
        """
        This method is called when this exporter is selected and shown in the
        export GUI.
        """
        pass

    def onHide(self, exportTaskView):
        """
        This method is called when this exporter is hidden from the export GUI.
        """
        pass

class ExportConfig(object):

    def __init__(self):
        self.feetOnGround       = False
        self.scale              = 1.0
        self.unit               = "dm"

        self.useNormals         = False
        self.useRelPaths        = True
        self.texFolder          = None
        self.customPrefix       = ""
        self.human              = None


    def selectedOptions(self, exporter):
        self.feetOnGround =         exporter.feetOnGround.selected
        self.scale,self.unit    = exporter.taskview.getScale()
        return self


    @property
    def offset(self):
        import numpy as np
        if self.feetOnGround:
            yOffset = -self.scale * self.human.getJointPosition('ground')[1]
            return np.asarray([0.0, yOffset, 0.0], dtype=np.float32)
        else:
            return np.zeros(3, dtype=np.float32)


    @property
    def subdivide(self):
        if not self.human:
            log.warning('No human set in config, disabled subdivision for export.')
            return False
        else:
            return self.human.isSubdivided()


    def setHuman(self, human):
        """
        Set the human object for this config.
        """
        self.human = human


    # TODO revise
    def setupTexFolder(self, filepath):
        import os

        def _getSubFolder(path, name):
            folder = os.path.join(path, name)
            if not os.path.exists(folder):
                log.message("Creating folder %s", folder)
                try:
                    os.mkdir(folder)
                except:
                    log.error("Unable to create separate folder:", exc_info=True)
                    return None
            return folder

        (fname, ext) = os.path.splitext(filepath)
        fname = self.goodName(os.path.basename(fname))
        self.outFolder = os.path.realpath(os.path.dirname(filepath))
        self.filename = os.path.basename(filepath)
        self.texFolder = _getSubFolder(self.outFolder, "textures")
        self._copiedFiles = {}


    # TODO revise
    def copyTextureToNewLocation(self, filepath):
        import os

        srcDir = os.path.abspath(os.path.expanduser(os.path.dirname(filepath)))
        filename = os.path.basename(filepath)

        newpath = os.path.abspath( os.path.join(self.texFolder, filename) )
        try:
            self._copiedFiles[filepath]
            done = True
        except:
            done = False
        if not done:
            try:
                shutil.copyfile(filepath, newpath)
            except:
                log.message("Unable to copy \"%s\" -> \"%s\"" % (filepath, newpath))
            self._copiedFiles[filepath] = True

        if not self.useRelPaths:
            return newpath
        else:
            relpath = os.path.relpath(newpath, self.outFolder)
            return str(os.path.normpath(relpath))


    def goodName(self, name):
        string = name.replace(" ", "_").replace("-","_").lower()
        return string

