#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier
                       Marc Flerackers
                       Thanasis Papoutsidakis

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

Subtexture class definition.
Functions for combining and manipulating subtextures.
"""

import inifile
import image
from codecs import open


class Subtexture(object):
    """
    A Subtexture is a texture that can be
    combined with a larger texture by overlapping it.
    It is useful for modifying small areas of large textures
    without replacing the whole texture.
    """

    def __init__(self, source, position):
        super(Subtexture, self).__init__()
        self.source = image.Image(source)
        self.position = position

    def overlap(img):
        img = image.Image(img)
        img.blit(self.source, *self.position)
        return img

    # [("(","["), (")","]")]
