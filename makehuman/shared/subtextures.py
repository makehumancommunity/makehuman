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

Functions for processing .mhstx files
and manipulating subtextures as Image objects.
"""

import os
import inifile
import image

def combine(image, mhstx):
    img = image.Image(image)
    f = open(mhstx, 'rU')
    try:
        subTextures = inifile.parseINI(f.read(), [("(","["), (")","]")])
    except:
        log.warning("subtextures.combine(%s)", mhstx, exc_info=True)
        f.close()
        return img
    f.close()
    
    texdir = os.path.dirname(mhstx)
    for subTexture in subTextures:
        path = os.path.join(texdir, subTexture['txt'])
        subImg = image.Image(path)
        x, y = subTexture['dst']
        img.blit(subImg, x, y)

    return img

