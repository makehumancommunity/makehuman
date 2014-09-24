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


    class Manager(object):
        """
        Interface hidden in objects utilized by caches
        that enables the use of operations on all the
        cached objects of the parent.
        """

        # Name of the hidden member of the managed object
        # that holds the Cache Manager.
        CMMemberName = "_CM_Cache_Manager_"

        @staticmethod
        def of(object):
            """
            Return the Cache Manager of the object.
            Instantiates a new one if it doesn't have one.
            """

            Manager(object)
            return getattr(object, Manager.CMMemberName)

        def __init__(self, parent):
            """
            Cache Manager constructor.
            :param parent: The object whose caches will be managed.
            """

            if hasattr(parent, Manager.CMMemberName) and \
               isinstance(getattr(parent, Manager.CMMemberName), Manager):
                return

            setattr(parent, Manager.CMMemberName, self)

            self.caches = set()


    # Represents an empty cache.
    Empty = object()

    def __init__(self, method):
        self.method = method
        self.cache = Cache.Empty

    def __call__(self, parent, *args, **kwargs):
        Cache.Manager.of(parent).caches.add(self)

        if self.cache is Cache.Empty:
            self.cache = self.method(parent, *args, **kwargs)
        return self.cache

    @staticmethod
    def invalidate(object, *args):
        """
        Invalidate the caches of the object
        defined in the arguments.
        """

        for arg in args:
            if hasattr(object, arg) and \
               isinstance(getattr(object, arg), Cache):
                getattr(object, arg).cache = Cache.Empty

    @staticmethod
    def invalidateAll(object):
        """
        Invalidate all caches of the given object.
        """

        Cache.invalidate(object, *Cache.Manager.of(object).caches)


class Layer(Image):
    """
    A Layer is an Image that can be inserted in a
    LayeredImage to be processed as a layer of a
    greater image compilation.
    """

    def __init__(self, img, borders=(0, 0, 0, 0)):
        if isinstance(img, Layer):  # Copy construction
            self.copyFrom(img)
            return

        self.image = img
        self.copyonwrite = True
        if len(borders) == 2:
            self.borders = borders + img.size
        else:
            self.borders = borders

    def copyFrom(self, other):
        self.image = other.image
        self.copyonwrite = other.copyonwrite
        self.borders = other.borders

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

        Cache.invalidateAll(self)

    # TODO Override and imitate Image's methods
    # so that they return the result calculated
    # by processing all layers. Use caching to
    # avoid calculation repetitions.

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

    @Cache
    def compile(self):
        """
        Compute the result of flattening all layers
        and return it as an Image.
        """

        if not self.layers: return Image()

        img = Image(None, *self.size, components=self.components)
        for layer in self.layers:
            img.blit(layer, *layer.borders[0:1])

        return img

    @property
    def data(self):
        """
        Return the result of flattening all layers.
        Operations on the returned array will only
        affect the cached object.
        """

        return self.compile().data

    def save(self, path):
        import image_qt as image_lib

        image_lib.save(path, self.data)

    def blit(self, other, x, y):
        """
        Blitting an image onto a LayeredImage is,
        guess what, adding a new layer.
        """

        self.addLayer(Layer(other, (x, y)))

    @property
    @Cache
    def isEmpty(self):
        """
        Returns True if the LayeredImage has no layers
        or if all its layers are empty.
        Returns False if any of the layers contains data
        or has been modified.
        """

        for layer in self.layers:
            if not layer.isEmpty: return False
        return True
