#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

""" 
Tests module.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers

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

This module is just for internal use, to test API and ideas.
Actually it's just a random collection of functions...and
IT NOT WORK
"""

import log
import mh


def testAnimation(self):

    # TODO: move this in a test module

    x = self.basemesh.x + .01
    log.message('animation test %s', x)
    self.basemesh.setLoc(x, self.basemesh.y, self.basemesh.z)
    self.scene.redraw()


def testUPArrowsEvent(self):

    # TODO: move this in a test module

    log.message('test up arrow')
    self.basemesh.y += .25
    self.basemesh.setLoc(self.basemesh.x, self.basemesh.y, self.basemesh.z)
    self.scene.redraw()


def testColor(self):
    """
    This method loads vertex colors on the base object.
    
    **Parameters:** This method has no parameters.

    """

    # TODO: move this in a test module

    algos3d.loadVertsColors(self.basemesh, mh.getSysDataPath('3dobjs/base.obj.colors'))


def applyTexture(self):
    """
    This method applies the texture file to either the standard mesh or the
    subdivided mesh (epending upon which is currently active).

    **Parameters:** None.

    """

    if not self.basemesh.isSubdivided:
        self.basemesh.setTexture('data/textures/texture.tga')
    else:
        sob = self.scene.getObject(self.basemesh.name + '.sub')
        sob.setTexture(mh.getSysDataPath('textures/texture.tga'))
    self.scene.redraw()


def analyzeTestTarget(self):
    """
    This function analyses a specific morph target file from a hardcoded
    file location that is used as part of the morph target file development
    cycle.

    **Parameters:** None.

    """

    # TODO: move this function in an utility module

    if not self.basemesh.isSubdivided:
        self.basemesh.applyDefaultColor()
        self.analyzeTarget(basemesh, mh.getSysDataPath('targets/test.target'))
        self.scene.redraw()


self.scene.connect('UP_ARROW', self.testUPArrowsEvent)
self.scene.connect('TIMER', self.testAnimation)
