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

_contextInstances = dict()

class _GLSettings(object):

    def __init__(self, openGLContext):

        self.setDefaults()
        self.readOverridesFromSettings()

        if not isinstance(openGLContext, QOpenGLContext):
            raise ValueError('Expected openGLContext parameter to be of type QOpenGLContext')

        # All GL widgets in the same window will theoretically share this context
        self.context = openGLContext

        profile = QOpenGLVersionProfile()
        profile.setVersion(self.openGLProfileMajor, self.openGLProfileMinor)

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


    def setDefaults(self):

        # Medium gray
        self.backgroundColor = QColor.fromRgb(128,128,128,255)

        # OpenGL version 2.0 (2004)... probably way too conservative
        self.openGLProfileMajor = 2
        self.openGLProfileMinor = 0

        pass

    def readOverridesFromSettings(self):
        pass

    def getGLFunctions(self):

        return self.gl

def GLSettings(openGLContext):
    global _contextInstances

    if not isinstance(openGLContext, QOpenGLContext):
        raise ValueError('Expected openGLContext parameter to be of type QOpenGLContext')

    if not openGLContext in _contextInstances:
        _contextInstances[openGLContext] = _GLSettings(openGLContext)

    return _contextInstances[openGLContext]


