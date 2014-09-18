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

Definitions for combining and manipulating subtextures
as multi-layered images.
"""

from image import Image


class Cache(object):
    """
    Method decorator class.
    Used on methods whose result will be cached.
    """

    def __init__(self, method):
        self.method = method
        self.cache = None

    def __call__(self, *args, **kwargs):
        if self.cache is None:
            self.cache = self.method(*args, **kwargs)
        return self.cache


class Layer(Image):
    """
    A Layer is an Image that can be inserted in a
    LayeredImage to be processed as a layer of a
    greater image compilation.
    """

    def __init__(self, img, borders=(0, 0, 0, 0)):
        self.image = img
        self.copyonwrite = True
        self.borders = borders

    def __getattr__(self, attr):
        if hasattr(self.image, attr):
            # When image is shared, create a copy on modifying operations.
            if self.copyonwrite and \
               attr in ("resize", "data", "blit", "__setitem__"):
                self.image = Image(self.image)
                self.copyonwrite = False
            return getattr(self.image, attr)
        else:
            return object.__getattribute__(self, attr)


class LayeredImage(Image):
    """
    A LayeredImage is a container of multiple
    overlapping image layers.
    It is designed to inherit from and externally
    behave like an Image, while managing all its
    layers in the background.
    """

    def __init__(self, *args, **kwargs):
        self.layers = []
        for arg in args: self.addLayer(arg)

    def addLayer(self, layer):
        """
        Add a layer in front of the LayeredImage's
        existing layers.

        If the layer added is a LayeredImage, its layers are
        appended to this LayeredImage's layers.
        To add a LayeredImage as a single layer, you can
        do it explicitly using addLayer(Layer(limg)).
        """

        if isinstance(layer, Layer):
            self.layers.append(layer)
        elif isinstance(layer, LayeredImage):
            self.layers.extend(layer.layers)
        elif isinstance(layer, Image):
            self.layers.append(Layer(layer))
        else:  # Layers from paths etc.
            self.layers.append(Layer(Image(layer)))

    # TODO Override and imitate Image's methods
    # so that they return the result calculated
    # by processing all layers. Use caching to
    # avoid calculation repetitions.

    #TODO: Possibly redesign cache so that it is invalidated properly.

    @property
    @Cache
    def size(self):
        if not self.layers: return (0, 0)
        b = self.layers[0].borders[2:3]
        for layer in self.layers[1:]:
            for i in xrange(1):
                b[i] = max(b[i], layer.borders[i + 2])
        return b

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    @Cache
    def components(self):
        if not self.layers: return 4  # Empty Image default.
        c = self.layers[0].components
        for layer in self.layers[1:]:
            c = max(c, layer.components)

    @property
    def bitsPerPixel(self):
        return self.components * 8

    @property
    @Cache
    def data(self):
        """
        Return the result of flattening all layers.
        Operations on the returned array will only
        affect the cached object.
        """

        if not self.layers: return Image()

        img = Image(None, *self.size, components=self.components)
        for layer in self.layers:
            img.blit(layer, *layer.borders[0:1])

        return img.data

    def save(self, path):
        import image_qt as image_lib

        image_lib.save(path, self.data)