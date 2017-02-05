#!/usr/bin/python2.7
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

import os.path
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.ARB.texture_non_power_of_two import *
from core import G
from image import Image
import log
from getpath import getSysDataPath

NOTFOUND_TEXTURE = getSysDataPath('textures/texture_notfound.png')

class Texture(object):
    _npot = None
    _powers = None

    def __new__(cls, *args, **kwargs):
        self = super(Texture, cls).__new__(cls)

        if cls._npot is None:
            cls._npot = glInitTextureNonPowerOfTwoARB()
            try:
                import debugdump
                debugdump.dump.appendMessage("GL.EXTENSION: GL_ARB_texture_non_power_of_two %s" % ("enabled" if cls._npot else "not available"))
            except Exception as e:
                log.error("Failed to write GL debug info to debug dump: %s", format(str(e)))
        if cls._powers is None:
            cls._powers = [2**i for i in xrange(20)]

        self.textureId = glGenTextures(1)
        self.width = 0
        self.height = 0
        self.modified = None

        return self

    def __init__(self, image = None, size = None, components = 4):
        if image is not None:
            self.loadImage(image)
        elif size is not None:
            width, height = size
            self.initTexture(width, height, components)

    def __del__(self):
        try:
            glDeleteTextures(self.textureId)
        except StandardError:
            pass

    @staticmethod
    def getFormat(components):
        if components == 1:
            return (GL_ALPHA8, GL_ALPHA)
        elif components == 3:
            return (3, GL_RGB)
        elif components == 4:
            return (4, GL_RGBA)
        else:
            raise RuntimeError("Unsupported pixel format")

    def initTexture(self, width, height, components = 4, pixels = None):
        internalFormat, format = self.getFormat(components)

        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        use_mipmaps = False
        if not (width in self._powers and height in self._powers) and not self._npot:
            log.debug("Non-power-of-two textures not supported, building mipmaps for image with dimensions %sx%s.", width, height)
            use_mipmaps = True
        if use_mipmaps and pixels is None:
            raise RuntimeError("Non-power-of-two textures not supported")

        if pixels is None:
            # Zero fill pixel data to allocate
            import numpy as np
            pixels = np.zeros(width*height*components, dtype=np.uint8)

        if height == 1:
            glBindTexture(GL_TEXTURE_1D, self.textureId)

            if not use_mipmaps:
                glTexImage1D(GL_PROXY_TEXTURE_1D, 0, internalFormat, width, 0, format, GL_UNSIGNED_BYTE, pixels)
                if not glGetTexLevelParameteriv(GL_PROXY_TEXTURE_1D, 0, GL_TEXTURE_WIDTH):
                    log.notice('texture size (%d) too large, building mipmaps', width)
                    use_mipmaps = True

            if use_mipmaps:
                gluBuild1DMipmaps(GL_TEXTURE_1D, internalFormat, width, format, GL_UNSIGNED_BYTE, pixels)
                # glGetTexLevelParameter is broken on X11
                # width  = glGetTexLevelParameteriv(GL_TEXTURE_1D, 0, GL_TEXTURE_WIDTH)
            else:
                glTexImage1D(GL_TEXTURE_1D, 0, internalFormat, width, 0, format, GL_UNSIGNED_BYTE, pixels)

            glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_1D, GL_TEXTURE_WRAP_T, GL_REPEAT)

            glBindTexture(GL_TEXTURE_1D, 0)
        else:
            glBindTexture(GL_TEXTURE_2D, self.textureId)

            if not use_mipmaps:
                glTexImage2D(GL_PROXY_TEXTURE_2D, 0, internalFormat, width, height, 0, format, GL_UNSIGNED_BYTE, pixels)
                if not glGetTexLevelParameteriv(GL_PROXY_TEXTURE_2D, 0, GL_TEXTURE_WIDTH):
                    log.notice('texture size (%d x %d) too large, building mipmaps', width, height)
                    use_mipmaps = True

            if use_mipmaps:
                gluBuild2DMipmaps(GL_TEXTURE_2D, internalFormat, width, height, format, GL_UNSIGNED_BYTE, pixels)
                # glGetTexLevelParameter is broken on X11
                # width  = glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH)
                # height = glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT)
            else:
                glTexImage2D(GL_TEXTURE_2D, 0, internalFormat, width, height, 0, format, GL_UNSIGNED_BYTE, pixels)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

            glBindTexture(GL_TEXTURE_2D, 0)
        self.width, self.height = width, height
        log.debug('initTexture: %s, %s, %s', width, height, use_mipmaps)

    def loadImage(self, image):
        if isinstance(image, (str, unicode)):
            image = Image(image)

        pixels = image.flip_vertical().data

        self.initTexture(image.width, image.height, image.components, pixels)

    def loadSubImage(self, image, x, y):
        if not self.textureId:
            raise RuntimeError("Texture is empty, cannot load a sub texture into it")

        if isinstance(image, (str, unicode)):
            image = Image(image)

        internalFormat, format = self.getFormat(image.components)

        pixels = image.flip_vertical().data

        if image.height == 1:
            glBindTexture(GL_TEXTURE_1D, self.textureId)
            glTexSubImage1D(GL_TEXTURE_1D, 0, x, image.width, format, GL_UNSIGNED_BYTE, pixels)
            glBindTexture(GL_TEXTURE_1D, 0)
        else:
            glBindTexture(GL_TEXTURE_2D, self.textureId)
            glTexSubImage2D(GL_TEXTURE_2D, 0, x, y, image.width, image.height, format, GL_UNSIGNED_BYTE, pixels)
            glBindTexture(GL_TEXTURE_2D, 0)

_textureCache = {}

def getTexture(path, cache=None):
    texture = None
    cache = cache or _textureCache

    if isinstance(path, Image):
        img = path
        if hasattr(img, 'sourcePath'):
            if img.sourcePath in cache:
                texture = cache[img.sourcePath]
                if not (hasattr(img, 'modified') and img.modified > texture.modified):
                    return texture
        else:
            log.warning("Image used as texture does not contain a \"sourcePath\" attribute, making it impossible to cache it. This could cause slow rendering (always creates new texture).")
            return Texture(img)

        import time
        if img.sourcePath in cache:
            log.debug("Reloading texture for dynamic image %s.", img.sourcePath)
            texture = cache[img.sourcePath]
            texture.loadImage(img)
        else:
            log.debug("Creating new texture for dynamic image %s.", img.sourcePath)
            texture = Texture(img)
        if hasattr(img, 'modified'):
            texture.modified = img.modified
        else:
            texture.modified = time.time()
        cache[img.sourcePath] = texture
        return texture

    elif not os.path.isfile(path):
        log.error('Cannot get texture for file path %s, no such file.', path)
        return None

    if path in cache:
        texture = cache[path]
        if texture is False:
            return texture

        if os.path.getmtime(path) > texture.modified:
            log.message('Reloading texture %s.', path)   # TL: unicode problems unbracketed

            try:
                img = Image(path=path)
                texture.loadImage(img)
            except RuntimeError, text:
                log.error("%s", text, exc_info=True)
                return
            else:
                texture.modified = os.path.getmtime(path)
    else:
        try:
            log.debug("Creating new texture for image %s.", path)
            img = Image(path=path)
            texture = Texture(img)
        except RuntimeError, text:
            log.error("Error loading texture %s", path, exc_info=True)
            texture = False
        else:
            texture.modified = os.path.getmtime(path)
        cache[path] = texture

    return texture
    
def reloadTextures():
    """
    Clear the entire texture cache, resulting in removing all contained textures
    from the GPU memory (unless other references are kept to the texture 
    objects).
    """
    log.message('Reloading all textures')
    for path in _textureCache:
        try:
            _textureCache[path].loadImage(path)
        except RuntimeError, _:
            log.error("Error loading texture %s", path, exc_info=True)

def reloadTexture(path):
    """
    Remove a texture from the texture cache. Removing a texture from cache will
    result in unloading the texture from the GPU memory, unless another
    reference to it is kept.
    """
    log.message('Reloading texture %s', path)
    if path not in _textureCache:
        log.error('Cannot reload non-existing texture %s', path)
        return
    try:
        _textureCache[path].loadImage(path)
    except RuntimeError, text:
        log.error("Error loading texture %s", path, exc_info=True)

