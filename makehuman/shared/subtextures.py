#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier
                       Marc Flerackers
                       Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

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

