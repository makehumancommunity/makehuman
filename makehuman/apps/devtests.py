#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Tests module.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

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
