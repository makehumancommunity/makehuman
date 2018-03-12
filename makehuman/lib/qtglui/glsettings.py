#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

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

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from core import G

_was_initialized = False

class GLSettings(object):

    def __init__(self):

        # Reuse this after first initialization
        self.gl = None

        self.setDefaults()
        self.readOverridesFromSettings()

    def setDefaults(self):

        # Medium gray
        self.backgroundColor = QColor.fromRgb(128,128,128,255)

        # OpenGL version 2.0 (2004)... probably way too conservative
        self.openGLProfileMajor = 2
        self.openGLProfileMinor = 0

        pass

    def readOverridesFromSettings(self):
        pass

    def initializeGL(self, openGLWidget):

        global _was_initialized

        if not isinstance(openGLWidget, QOpenGLWidget):
            raise ValueError('Expected openGLWidget parameter to be of type QOpenGLWidget')

        if _was_initialized:
            raise ValueError('Attempting to initialize GL a second time. This is probably a bad idea.')

        _was_initialized = True

        profile = QOpenGLVersionProfile()
        profile.setVersion(self.openGLProfileMajor, self.openGLProfileMinor)

        # All GL widgets will theoretically share this context
        context = openGLWidget.context()

        # Fetch a "functions" instance matching the OpenGL version we're using
        #
        # THIS OBJECT IS THE ROOT OF ALL GL CALLS!!! NEVER DO A GL CALL WITHOUT GOING THROUGH THE "functions" OBJECT!!!
        self.gl = self.context.versionFunctions(profile)
        self.gl.initializeOpenGLFunctions()

        r = self.backgroundColor.redF()
        g = self.backgroundColor.greenF()
        b = self.backgroundColor.blueF()
        a = self.backgroundColor.alphaF()

        # Set background color
        self.gl.glClearColor(r,g,b,a)

        return self.gl
