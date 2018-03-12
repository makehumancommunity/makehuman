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

from PyQt5.QtWidgets import QOpenGLWidget

from core import G
from getpath import *
from image import Image

NOTFOUND_TEXTURE = getSysDataPath('textures/texture_notfound.png')

class Texture(object):

    def __init__(self, image = None, size = None, components = 4):
        if image is not None:
            self.loadImage(image)
        elif size is not None:
            width, height = size
            self.initTexture(width, height, components)

    def initTexture(self, width, height, components=4, pixels=None):
        # TODO: adapt from lib/texture.py
        pass

    def loadImage(self, image):
        if isinstance(image, str):
            image = Image(image)

        pixels = image.flip_vertical().data

        self.initTexture(image.width, image.height, image.components, pixels)

