#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

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

Blend skin and color properties based on human ethnic values
"""

import material
import image
import image_operations
import numpy as np
from getpath import getSysDataPath


asianColor     = np.asarray([0.721, 0.568, 0.431], dtype=np.float32)
africanColor   = np.asarray([0.207, 0.113, 0.066], dtype=np.float32)
caucasianColor = np.asarray([0.843, 0.639, 0.517], dtype=np.float32)

class EthnicSkinBlender(object):
    """
    Skin blender for the adaptive_skin_tone litsphere texture. Makes sure that
    the texture is set to a blend of the three ethnic skin tones based on the
    human macro settings.
    """
    def __init__(self, human):
        self.human = human
        self.skinCache = { 'caucasian' : image.Image(getSysDataPath('litspheres/skinmat_caucasian.png')),
                           'african'   : image.Image(getSysDataPath('litspheres/skinmat_african.png')),
                           'asian'     : image.Image(getSysDataPath('litspheres/skinmat_asian.png')) }
        self._previousEthnicState = [0, 0, 0]

        self._litsphereTexture = None
        self._diffuseColor = material.Color()

        self.checkUpdate()

    def checkUpdate(self):
        newEthnicState = self.getEthnicState()
        if self._previousEthnicState != newEthnicState:
            self.update()
            self._previousEthnicState = newEthnicState
            return True
        return False

    def getEthnicState(self):
        return [ self.human.getCaucasian(),
                 self.human.getAfrican(),
                 self.human.getAsian()     ]

    def getLitsphereTexture(self):
        self.checkUpdate()
        return self._litsphereTexture

    def getDiffuseColor(self):
        self.checkUpdate()
        return self._diffuseColor

    def update(self):
        caucasianWeight = self.human.getCaucasian()
        africanWeight   = self.human.getAfrican()
        asianWeight     = self.human.getAsian()
        blends = []

        # Set litsphere texture
        if caucasianWeight > 0:
            blends.append( ('caucasian', caucasianWeight) )
        if africanWeight > 0:
            blends.append( ('african', africanWeight) )
        if asianWeight > 0:
            blends.append( ('asian', asianWeight) )

        if len(blends) == 1:
            img = self.skinCache[blends[0][0]]
            img.markModified()
        else:
            img = image_operations.mix(self.skinCache[blends[0][0]], self.skinCache[blends[1][0]], blends[0][1], blends[1][1])
            if len(blends) > 2:
                img = image_operations.mix(img, self.skinCache[blends[2][0]], 1.0, blends[2][1])

        # Set parameter so the image can be referenced when material is written to file (and texture can be cached)
        img.sourcePath = getSysDataPath("litspheres/adaptive_skin_tone.png")
        self._litsphereTexture = img

        # Set diffuse color
        diffuse = asianWeight     * asianColor   + \
                  africanWeight   * africanColor + \
                  caucasianWeight * caucasianColor
        self._diffuseColor = material.Color(diffuse)

