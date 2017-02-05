#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Internal OpenGL Renderer Functions.

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

"""

import os
import projection
import mh
import log
import gui3d
from core import G
import gui
import image
import image_operations as imgop
from progress import Progress
import numpy as np

# TODO perhaps these settings should be saved in settings.ini as well to remember them

def Render(settings):
    progress = Progress.begin()
    
    if not mh.hasRenderToRenderbuffer():
        settings['dimensions'] = (G.windowWidth, G.windowHeight)

    if settings['lightmapSSS']:
        progress(0, 0.05, "Storing data")
        import material
        human = G.app.selectedHuman
        materialBackup = material.Material(human.material)

        progress(0.05, 0.1, "Projecting lightmaps")
        diffuse = imgop.Image(data = human.material.diffuseTexture)
        lmap = projection.mapSceneLighting(
            settings['scene'], border = human.material.sssRScale)
        progress(0.1, 0.4, "Applying medium scattering")
        lmapG = imgop.blurred(lmap, human.material.sssGScale, 13)
        progress(0.4, 0.7, "Applying high scattering")
        lmapR = imgop.blurred(lmap, human.material.sssRScale, 13)
        lmap = imgop.compose([lmapR, lmapG, lmap])
        if not diffuse.isEmpty:
            progress(0.7, 0.8, "Combining textures")
            lmap = imgop.resized(lmap, diffuse.width, diffuse.height, filter=image.FILTER_BILINEAR)
            progress(0.8, 0.9)
            lmap = imgop.multiply(lmap, diffuse)
        lmap.sourcePath = "Internal_Renderer_Lightmap_SSS_Texture"

        progress(0.9, 0.95, "Setting up renderer")
        human.material.diffuseTexture = lmap
        human.configureShading(diffuse = True)
        human.shadeless = True
        progress(0.95, 0.98, None)
    else:
        progress(0, 0.99, None)
        
    if not mh.hasRenderToRenderbuffer():
        # Limited fallback mode, read from screen buffer
        log.message("Fallback render: grab screen")
        img = mh.grabScreen(0, 0, G.windowWidth, G.windowHeight)
        alphaImg = None
    else:
        # Render to framebuffer object
        renderprog = Progress()
        renderprog(0, 0.99 - 0.59 * settings['AA'], "Rendering")
        width, height = settings['dimensions']
        log.message("Rendering at %sx%s", width, height)
        if settings['AA']:
            width = width * 2
            height = height * 2
        img = mh.renderToBuffer(width, height)
        alphaImg = mh.renderAlphaMask(width, height)
        img = imgop.addAlpha(img, imgop.getChannel(alphaImg, 0))

        if settings['AA']:
            renderprog(0.4, 0.99, "AntiAliasing")
            # Resize to 50% using bi-linear filtering
            img = img.resized(width/2, height/2, filter=image.FILTER_BILINEAR)
            # TODO still haven't figured out where components get swapped, but this hack appears to be necessary
            img.data[:,:,:] = img.data[:,:,(2,1,0,3)]
        renderprog.finish()

    if settings['lightmapSSS']:
        progress(0.98, 0.99, "Restoring data")
        human.material = materialBackup

    progress(1, None, 'Rendering complete')

    gui3d.app.getCategory('Rendering').getTaskByName('Viewer').setImage(img)
    mh.changeTask('Rendering', 'Viewer')
    gui3d.app.statusPersist('Rendering complete')
