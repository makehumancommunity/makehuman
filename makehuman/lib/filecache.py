#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
File properties cache

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

A generic cache for storing metadata for files
"""

import os
import getpath
import log
import cPickle as pickle

CACHE_FORMAT_VERSION = 1  # You can use any type, strings or ints, only equality test is done on these


class FileCache(object):
    def __init__(self, filepath, version=None):
        """Create an empty filecache
        """
        if version is None:
            self.version = CACHE_FORMAT_VERSION
        else:
            self.version = version
        self.filepath = filepath

        self._cache = dict()

        self.get_metadata_filename = None

    def __getstate__(self):
        """Return state values to be pickled."""
        return {'version': self.version, '_cache': self._cache}

    def save(self):
        """Save filecache to file"""
        f = open(self.filepath, "wb")
        pickle.dump(self, f, protocol=2)
        f.close()

    def getMetadata(self, filename):
        """Retrieve a metadata entry from this cache"""
        fileId = getpath.canonicalPath(filepath)
        return self[fileId]

    def cleanup(self):
        """
        Remove non-existing entries from this cache
        """
        for fileId in self._cache.keys():
            if not os.path.exists(fileId):
                try:
                    del self._cache[fileId]
                except:
                    pass

    def getMetadataFile(self, filename):
        if self.get_metadata_filename is None:
            return filename
        else:
            return self.get_metadata_filename(filename)

    def update(self, paths, fileExts, getMetadata, removeOldEntries=True):
        """
        Update this cache of files in the specified paths.
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
                mtime = os.path.getmtime(self.getMetadataFile(filepath))

            fileExt = os.path.splitext(filepath)[1][1:].lower()
            i = fileExts.index(fileExt)
            if i != 0:
                for altExt in fileExts[:i]:
                    overridepath = os.path.splitext(filepath)[0] + "." + altExt
                    if os.path.isfile(overridepath):
                        mtime_ = os.path.getmtime(self.getMetadataFile(overridepath))
                        if mtime_ > mtime:
                            return (overridepath, mtime_)
            return None

        if not isinstance(paths, list):
            paths = [ paths ]
        if not isinstance(fileExts, list):
            fileExts = [ fileExts ]
        fileExts = [f[1:].lower() if f.startswith('.') else f.lower() for f in fileExts]

        files = []
        oldEntries = dict((key, True) for key in self._cache.keys()) # lookup dict for old entries in cache
        for folder in paths:
            files.extend(getpath.search(folder, fileExts, recursive=True, mutexExtensions=True))
        for filepath in files:
            fileId = getpath.canonicalPath(filepath)
            mtime = os.path.getmtime(self.getMetadataFile(filepath))

            overridepath = _getOverridingFile(filepath, list(reversed(fileExts)), mtime)
            if overridepath is not None:
                filepath, mtime = overridepath

            if fileId in self._cache:
                try: # Guard against doubles
                    del oldEntries[fileId]    # Mark that old cache entry is still valid
                except:
                    pass
                cached_mtime = self[fileId][0]
                if not (mtime > cached_mtime):
                    continue

            try:
                metadata = getMetadata(filepath)
            except:
                log.error("Failed to load metadata from file %s, it's probably corrupt." % filepath)
                raise

            self._cache[fileId] = (mtime,) + metadata

        if removeOldEntries:
            """Remove entries from cache that no longer exist"""
            for key in oldEntries.keys():
                try:
                    del self._cache[key]
                except:
                    pass

    def __getitem__(self, key):
        return self._cache[key]

    def __contains__(self, key):
        return key in self._cache

    def __len__(self):
        return len(self._cache)

    def items(self):
        return self._cache.items()

    def keys(self):
        return self._cache.keys()


class MetadataCacher(object):
    """Super class that can be used for libraries that store file metadata in a
    cache.
    """
    def __init__(self, file_extensions, cache_file):
        self.file_extensions = file_extensions
        self.cache_file = cache_file
        self._filecache = None

        self.cache_format_version = None  # Override this in a subclass to specify a custom cache version

    def _get_metadata_callback(self, filename):
        return self.getMetadataImpl(self.getMetadataFile(filename))

    def getMetadataFile(self, filename):
        """For a specified asset file, return the file that should be read for
        metadata. By default returns the same filename. Change this if the
        metadata is stored in a separate file.
        It is from this file that the modification time is tested, to update
        the metadata in the cache if a newer file is available.
        This method is expected to return an existing file, if the metadata file
        does not exist it should return, for example, the path to the original
        file.
        """
        return filename

    def getMetadataImpl(self, filename):
        """This method should be implemented by the library to define the logic
        to retrieve the metadata of a file.
        """
        raise NotImplementedError("Subclass should implement this method")

    def getTagsFromMetadata(self, metadata):
        """Override this if the format of the metadata is different.
        NOTE: The returned tags should be all in lower cases!
        """
        name, tags = metadata
        return tags

    def getSearchPaths(self):
        """This method should be implemented by the library to return the paths
        that should be searched for updating the cache.
        """
        raise NotImplementedError("Subclass should implement this method")

    def getMetadata(self, filename):
        """Retrieves the metadata of a specified file.
        Updates the cache if needed.
        """
        if self._filecache is None:
            # Init cache
            self.loadCache()
            self.updateFileCache(self.getSearchPaths(), self.getFileExtensions(), False)

        fileId = getpath.canonicalPath(filename)
        if fileId not in self._filecache._cache:
            # Lazily update cache
            self.updateFileCache(self.getSearchPaths() + [os.path.dirname(fileId)], self.getFileExtensions(), False)

        if fileId in self._filecache:
            metadata = self._filecache[fileId]
            if metadata is not None:
                mtime = metadata[0]
                metadata = metadata[1:]

                if mtime < os.path.getmtime(self.getMetadataFile(fileId)):
                    # Queried file was updated, update stale cache
                    self.updateFileCache(self.getSearchPaths() + [os.path.dirname(fileId)], self.getFileExtensions(), False)
                    metadata = self._filecache[fileId]
                    mtime = metadata[0]
                    metadata = metadata[1:]

                return metadata
        else:
            log.warning('Could not get metadata for file %s. Does not exist in cache.', filename)
        return None

    def getTags(self, filename=None):
        if filename is None:
            return self.getAllTags()

        metadata = self.getMetadata(filename)
        if metadata is not None:
            return self.getTagsFromMetadata(metadata)
        else:
            return set()

    def getAllTags(self):
        result = set()
        for (path, metadata) in self._filecache.items():
            tags = self.getTagsFromMetadata(metadata[1:])
            result = result.union(tags)
        return result

    def getFileExtensions(self):
        return self.file_extensions

    def updateFileCache(self, search_paths=None, file_extensions=None, remove_old_entries=True):
        """
        Update cache of file metadata in the specified paths.
        This cache contains per canonical filename (key) the UUID and tags of that
        proxy file.
        Cache entries are invalidated if their modification time has changed, or no
        longer exist on disk.
        """
        if search_paths is None:
            search_paths=self.getSearchPaths()
        if file_extensions is None:
            file_extensions=self.getFileExtensions()
        self._filecache.update(search_paths, file_extensions, self._get_metadata_callback, remove_old_entries)

    def onUnload(self):
        """
        Called when this library taskview is being unloaded (usually when MH
        is exited).
        Note: make sure you connect the plugin's unload() method to this one!
        """
        self.storeCache()

    def storeCache(self):
        if self._filecache is None or len(self._filecache) == 0:
            return

        self._filecache.cleanup()

        cachedir = getpath.getPath('cache')
        if not os.path.isdir(cachedir):
            os.makedirs(cachedir)
        saveCache(self._filecache)

    def loadCache(self):
        filename = getpath.getPath(os.path.join('cache', self.cache_file))
        self._filecache = loadCache(filename, self.cache_format_version)
        self._filecache.get_metadata_filename = self.getMetadataFile


def saveCache(cache):
    cache.save()

def loadCache(filepath, expected_version=None):
    if expected_version is None:
        expected_version = CACHE_FORMAT_VERSION

    try:
        if os.path.isfile(filepath):
            f = open(filepath, "rb")
            result = pickle.load(f)
            f.close()
            if result.version != expected_version:
                log.message("File cache %s has a different version (%s) than expected (%s), dropping it." % (filepath, result.version, expected_version))
                del result
            else:
                result.filepath = filepath
                return result
    except:
        log.debug("Failed to load stored cache %s" % filepath, exc_info=True)
    # Create new filecache
    log.debug("Creating new file metadata cache %s" % filepath)
    return FileCache(filepath, expected_version)

