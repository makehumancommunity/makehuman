#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thanasis Papoutsidakis

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

Tools and interfaces for managing caches.

A cache is a container associated with a method.
When the method is called, the result is stored in the
cache, and on subsequent calls of the method the stored
result is returned, so that no recomputation is needed.
The result of the method will be recalculated once the
cache is explicitly invalidated (emptied) and the method
gets called again.

To use the caching mechanisms in your code, simply use
the Cache decorator in front of the method you want to cache.

Example:

@Cache
def method(self):
    ...

To invalidate a cached result, you can assign Cache Empty to
your method's cache: self.method.cache = Cache.Empty

You can also use Cache.invalidate to inalidate caches,
like so: Cache.invalidate(self, "method1", "method2")

Or use Cache.invalidateAll to clear all caches of an object:
Cache.invalidateAll(self)

If your object happens to have a method that somehow processes
all of its caches, and returns a similar object with the same
methods but with all the computation done, decorate it as
Cache.Compiler. When next time a method is called, the computed
object's methods will be called instead of returning the method's
cache, if the object is newer than the cache.

"""


class Cache(object):
    """
    Method decorator class.
    Used on methods whose result will be cached.
    """

    # A unique ever-increasing id for each cache update.
    # Can be used for comparing the age of caches.
    _C_CacheUID = 0

    # Represents an empty cache.
    Empty = object()

    @staticmethod
    def getNewCacheUID():
        """
        Get a new unique ID for the Cache that is
        about to be constructed or updated.
        """

        r = _C_CacheUID
        _C_CacheUID += 1
        return r


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
            self.compiler = None


    class Compiler(Cache):
        """
        A Cache Compiler is a special form of cache,
        which when invoked creates a "Compiled Cache".

        A Compiled Cache is a cache that is stored in the
        parent's Cache Manager, and essentialy replaces
        the parent. So, the method that will be decorated
        with the Compiler has to return an object with the
        same type as the parent, or at least one that supports
        the same methods of the parent that are decorated as
        Cache. After that, whenever a cached method is called,
        the result is taken from the compiled cache (except if
        the method's cache is newer).

        This is useful for objects that cache many parameters,
        but also have a greater method that creates a 'baked'
        replica of themselves. After the 'baking', the parameters
        can simply be taken from the cached replica.
        """

        @staticmethod
        def of(object):
            """
            Return the Cache Compiler of the object.
            """

            return Cache.Manager.of(parent).compiler

        def __call__(self, parent, *args, **kwargs):
            Cache.Manager.of(parent).compiler = self

            if self.cache is Cache.Empty:
                self.calculate(parent, *args, **kwargs)
            return self.cache


    def __init__(self, method):
        """
        Cache constructor.

        Cache is a decorator class, so the constructor is
        essentialy applied to a method to be cached.
        """

        self.method = method
        self.cache = Cache.Empty
        self.cacheUID = Cache.getNewCacheUID()

    def __call__(self, parent, *args, **kwargs):
        Cache.Manager.of(parent).caches.add(self)

        # If a compiled cache exists and is newer,
        # prefer to get the value from it instead.
        compiler = Cache.Compiler.of(parent)
        if compiler and \
           compiler.cacheUID > self.cacheUID and \
           compiler.cache is not Cache.Empty:
            return getattr(compiler.cache, self.method)(parent, *args, **kwargs)

        if self.cache is Cache.Empty:
            self.calculate(parent, *args, **kwargs)
        return self.cache

    def calculate(self, *args, **kwargs):
        self.cache = self.method(*args, **kwargs)
        self.cacheUID = Cache.getNewCacheUID()

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
