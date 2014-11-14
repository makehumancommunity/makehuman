#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
File properties cache

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

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

A generic cache for storing metadata for files
"""

import os
import getpath

# TODO create a class for filecache and have a method to query the cache (that updates the entry if stale mtime is detected)

def updateFileCache(paths, fileExts, getMetadata, cache=None, removeOldEntries=True):
    """
    Update cache of files in the specified paths. If no cache is given as
    parameter, a new cache is created.
    This cache contains per canonical filename (key) metadata of that file.
    The contents of this metadata, and how it is parsed from file is completely 
    customizable.
    Cache entries are invalidated if their modification time has changed, or no
    longer exist on disk.
    Requires passing a method getMetadata(filename) that retrieves metadata to
    be stored in the cache from specified file, that should return a tuple.
    """
    def _getOverridingFile(filepath, fileExts, mtime=None):
        """
        Overriding happens if a file with lesser precedence has a more recent
        modification time. fileExts are expected to be passed in reverse order
        """
        if mtime is None:
            mtime = os.path.getmtime(filepath)

        fileExt = os.path.splitext(filepath)[1][1:].lower()
        i = fileExts.index(fileExt)
        if i != 0:
            for altExt in fileExts[:i]:
                overridepath = os.path.splitext(filepath)[0] + "." + altExt
                if os.path.isfile(overridepath):
                    mtime_ = os.path.getmtime(overridepath)
                    if mtime_ > mtime:
                        return (overridepath, mtime_)
        return None

    if cache is None:
        cache = dict()
    if not isinstance(paths, list):
        paths = [ paths ]
    if not isinstance(fileExts, list):
        fileExts = [ fileExts ]
    fileExts = [f[1:].lower() if f.startswith('.') else f.lower() for f in fileExts]

    files = []
    oldEntries = dict((key, True) for key in cache.keys()) # lookup dict for old entries in cache
    for folder in paths:
        files.extend(getpath.search(folder, fileExts, recursive=True, mutexExtensions=True))
    for filepath in files:
        fileId = getpath.canonicalPath(filepath)
        mtime = os.path.getmtime(filepath)

        overridepath = _getOverridingFile(filepath, list(reversed(fileExts)), mtime)
        if overridepath is not None:
            filepath, mtime = overridepath

        if fileId in cache:
            try: # Guard against doubles
                del oldEntries[fileId]    # Mark that old cache entry is still valid
            except:
                pass
            cached_mtime = cache[fileId][0]
            if not (mtime > cached_mtime):
                continue

        cache[fileId] = (mtime,) + getMetadata(filepath)

    if removeOldEntries:
        # Remove entries from cache that no longer exist
        for key in oldEntries.keys():
            try:
                del cache[key]
            except:
                pass
    return cache

def cleanupCache(cache):
    """
    Remove non-existing entries from cache
    :param cache:
    :return: pointer to modified cache (input cache is modified in place)
    """
    oldEntries = dict((key, True) for key in cache.keys()) # lookup dict for old entries in cache

    for fileId in oldEntries.keys():
        if os.path.exists(fileId):
           try:
               del oldEntries[fileId]    # Mark that old cache entry is still valid
           except:
               pass

    for key in oldEntries.keys():
        try:
            del cache[key]
        except:
            pass
    return cache

def saveCache(cache, filename):
    import cPickle as pickle
    f = open(filename, "wb")
    pickle.dump(cache, f, protocol=2)
    f.close()

def loadCache(filename):
    import cPickle as pickle
    f = open(filename, "rb")
    result = pickle.load(f)
    f.close()
    return result