#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements, Jonas Hauquier

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

import os
import zipfile
from getpath import getSysDataPath, canonicalPath
import log

# TODO share with algos3d
TARGETS_NPZ_PATH = getSysDataPath('targets.npz')

# Defines reserved value keywords and which category they map to
# Used for specifying dependencies between targets using their filename
# Maps macro variable to discrete variables controlled by that macro modifier
_cat_data = [
   # category     values
    ('gender',   ['male', 'female']),
    ('age',      ['baby', 'child', 'young', 'old']),
    ('race',     ['caucasian', 'asian', 'african']),
    ('muscle',   ['maxmuscle', 'averagemuscle', 'minmuscle']),
    ('weight',   ['minweight', 'averageweight', 'maxweight']),
    ('height',   ['minheight', 'averageheight', 'maxheight']),
    ('breastsize',     ['mincup', 'averagecup', 'maxcup']),
    ('breastfirmness', ['minfirmness', 'averagefirmness', 'maxfirmness']),
    ('bodyproportions', ['uncommonproportions', 'regularproportions', 'idealproportions'])
    ]

_cat_values = dict(_cat_data)
_categories = [cat for cat, value in _cat_data]
_value_cat = dict([(value, cat)
                   for cat, values in _cat_data
                   for value in values])
del cat, value, values


class Component(object):
    """
    Defines a target or target folder.
    Refers to its path either in an NPZ archive or as a file on disk.
    A Component does not actually contain target data, see algos3d.Target for
    that.
    """

    def __init__(self, other = None):
        self.path = None
        if other is None:
            self.key = []   # Used for referencing this component in Targets.groups
            self.data = {}  # Dependent (macro) variables that influence the weight of this target
            self.parent = None
        else:
            self.key = other.key[:]
            self.data = other.data.copy()
            self.parent = other

        global _categories, _value_cat

        self._categories = list(_categories)
        self._value_cat = dict(_value_cat)

    def __repr__(self):
        return repr((self.key, self.data, self.path))

    def isRoot(self):
        return self.parent == None

    def getVariables(self):
        """
        The variables that apply to this target component.
        """
        return [value for key,value in self.data.items() if value != None]

    def set_data(self, category, value):
        orig = self.data.get(category)
        if orig is not None and orig != value:
            raise RuntimeError('%s already set' % category)
        self.data = self.data.copy()
        self.data[category] = value

    def add_key(self, value):
        self.key.append(value)

    def clone(self):
        return Component(self)

    def update(self, value):
        category = self._value_cat.get(value)
        if category is not None:
            self.set_data(category, value)
        elif value == 'target':
            pass
        else:
            self.add_key(value)

    def finish(self, path):
        """
        Finish component as a leaf in the tree (file).
        """
        self.path = path
        for category in self._categories:
            if category not in self.data:
                self.data[category] = None

class TargetsCrawler(object):
    """
    Recursive target finder baseclass.
    """
    def __init__(self, dataPath):
        self.dataPath = dataPath

        self.rootComponent = Component()

        self.targets = []
        self.groups = {}
        self.images = {}

    def list_dir(self, path):
        raise NotImplementedError("Implement TargetsCrawler.list_dir(path)")

    def is_dir(self, path):
        raise NotImplementedError("Implement TargetsCrawler.is_dir(path)")

    def is_file(self, path):
        raise NotImplementedError("Implement TargetsCrawler.is_file(path)")

    def real_path(self, path):
        raise NotImplementedError("Implement TargetsCrawler.real_path(path)")

    def buildIndex(self):
        """
        Build target index
        """
        self.index = {}
        for target in self.targets:
            if tuple(target.key) not in self.index:
                self.index[tuple(target.key)] = []
            self.index[tuple(target.key)].append(target)
            component = target
            while not component.isRoot():
                parent = component.parent
                if tuple(parent.key) not in self.index:
                    self.index[tuple(parent.key)] = []
                if tuple(component.key) not in self.index[tuple(parent.key)] \
                   and tuple(component.key) != tuple(parent.key):
                    self.index[tuple(parent.key)].append(tuple(component.key))
                component = parent

    def findTargets(self):
        self.walkTargets('', self.rootComponent)
        self.buildIndex()

    def walkTargets(self, root, base):
        dirs = self.list_dir(self.real_path(root))
        for name in sorted(dirs):
            path = self.real_path(os.path.join(root, name)).replace('\\','/')

            if self.is_file(path) and not path.lower().endswith('.target'):
                # File but not a .target file
                if path.lower().endswith('.png'):
                    # Add image
                    self.images[name.lower()] = path

            else:   # Add target or folder
                item = base.clone() # Create new Component

                # Split filename in parts
                parts = name.replace('_','-').replace('.','-').split('-')
                for pIdx, part in enumerate(parts):
                    if pIdx == 0 and part == "targets":
                        # Do not add targets/ path component to group names
                        # This is a shortcut in naming for target files inside
                        # the targets/ folder.
                        # For target files in other data subfolders, the containing
                        # subfolder is prepended to the group name
                        # eg. poses-...
                        # To avoid clashes, placing .target files in the data
                        # folder root is not advised.
                        continue
                    item.update(part)   # Set Component.key or dependencies data

                if self.is_dir(path):
                    # Continue recursion on subfolder
                    _root = os.path.join(root, name).replace('\\','/')
                    self.walkTargets(_root, item)
                else: # File is a .target file: add Component to groups
                    item.finish(path)
                    self.targets.append(item)
                    key = tuple(item.key)
                    if key not in self.groups:
                        self.groups[key] = []
                    self.groups[key].append(item)


class FilesTargetsCrawler(TargetsCrawler):
    """
    Finds targets that are separate ASCII .target files in recursive folders.
    """
    def __init__(self, dataPath):
        super(FilesTargetsCrawler, self).__init__(dataPath)

    def is_dir(self, path):
        return os.path.isdir(path)

    def is_file(self, path):
        return os.path.isfile(path)

    def list_dir(self, path):
        return os.listdir(path)

    def real_path(self, path):
        return os.path.normpath( os.path.join(self.dataPath, path) )


class ZippedTargetsCrawler(TargetsCrawler):
    """
    Finds targets packed in a binary .npz archive.
    """
    def __init__(self, dataPath, npzFile):
        super(ZippedTargetsCrawler, self).__init__(dataPath)

        self.npzPath = os.path.join(dataPath, npzFile)
        if not os.path.isfile(self.npzPath):
            raise StandardError('Could not load load targets from npz archive. Archive file %s not found.', self.npzPath)
        self._files = None

    def lookupPath(self, realPath):
        """
        Returns the _files lookup path for specified real path.
        """
        if canonicalPath(realPath) == canonicalPath(self.dataPath):
            return ''
        return os.path.normpath(os.path.relpath(realPath, self.dataPath)).replace('\\', '/')

    def is_file(self, realPath):
        path = self.lookupPath(realPath)
        return self.namei(path) is None

    def is_dir(self, realPath):
        path = self.lookupPath(realPath)
        return isinstance(self.namei(path), dict)

    def list_dir(self, realPath):
        path = self.lookupPath(realPath)
        if self._files is None:
            self.buildTree()
        return self.namei(path).keys()

    def real_path(self, path):
        return os.path.join(self.dataPath, path).replace('\\', '/')

    def namei(self, path):
        if isinstance(path, basestring):
            if not path:
                path = []
            elif path == '.':
                path = []
            else:
                path = list(reversed(path.split('/')))
        else:
            path = list(reversed(path))
        dir_ = self._files
        while path:
            dir_ = dir_[path.pop()]
        return dir_

    def buildTree(self):
        """
        Build file tree of .target files from targets.npz and image file from
        the data file path.
        Targets in NPZ archive are referenced as regular target files relative
        to sys path (paths like data/targets/...).
        This method will throw an exception if npz is not found or faulty.
        """
        self._files = {}

        def add_file(dir, path):
            head, tail = path[0], path[1:]
            if not tail:
                dir[head] = None
            else:
                if head not in dir:
                    dir[head] = {}
                add_file(dir[head], tail)

        # Add targets in npz archive to file list
        with zipfile.ZipFile(self.npzPath, 'r') as npzfile:
            for file_ in npzfile.infolist():
                name = file_.filename
                if not name.endswith('.index.npy'):
                    continue
                name = name[:-len('.index.npy')] + '.target'
                path = name.split('/')
                add_file(self._files, path)

        # Walk file path (not .npz archive) to find images to add to file list
        from codecs import open
        with open(os.path.join(self.dataPath, 'images.list'), 'rU', encoding="utf-8") as imgfile:
            for line in imgfile:
                name = line.rstrip()
                if not name.endswith('.png'):
                    continue
                path = os.path.normpath(os.path.relpath(name, self.dataPath)).replace('\\', '/')
                path = path.split('/')
                add_file(self._files, path)

        def _debug_print(root, pre=''):
                if not root:
                    return
                for (key, vals) in root.items():
                    log.debug( pre+"%s" % key )
                    _debug_print(vals, pre+'    ')
        #_debug_print(self._files)


class Targets(object):
    def __init__(self, dataPath):
        self.targets = []       # List of target files
        self.groups = {}        # Target components, ordered per group
        self.images = {}        # Images list
        self.walk(dataPath)

    def debugGroups(self):
        """
        Debug print all group keys for the targets stored in groups.
        """
        log.debug("Targets keys:\n%s", "\n".join(["-".join(k) for k in self.groups.keys()]))

    def debugTargets(self, showData = False):
        """
        Elaborately print all targets stored in this collection.
        """
        for groupKey, targets in self.groups.items():
            groupKeyStr = "-".join(groupKey)
            log.debug("\n========== Group: %s ===============\n", groupKeyStr)
            for targetComponent in targets:
                log.debug("    [target] path: %s", targetComponent.path)
                if showData:
                    log.debug("             data: %s", targetComponent.data)
                dependsOn = dict([(varName, value) 
                            for (varName, value) in targetComponent.data.items()
                            if value is not None])
                log.debug("             depends on variables: %s", dependsOn)

    def getTargetsByGroup(self, group):
        if isinstance(group, basestring):
            group = tuple(group.split('-'))
        elif not isinstance(group, tuple):
            group = tuple(group)
        return self.groups[group]

    def findTargets(self, partialGroup):
        if isinstance(partialGroup, basestring):
            partialGroup = tuple(partialGroup.split('-'))
        elif not isinstance(partialGroup, tuple):
            partialGroup = tuple(partialGroup)

        if partialGroup not in self.index:
            return []
        result = []
        for entry in self.index[partialGroup]:
            if isinstance(entry, Component):
                result.append(entry)
            else:
                result.extend(self.findTargets(entry))
        return result

    def walk(self, dataPath):
        try:
            # Load cached targets from .npz file
            log.debug("Attempting to load targets from NPZ file.")
            targetFinder = ZippedTargetsCrawler(dataPath, 'targets.npz')
            targetFinder.findTargets()
            log.debug("%s targets loaded from NPZ file succesfully.", len(targetFinder.targets))
        except StandardError as e:
            # Load targets from .target files
            log.debug("Could not load targets from NPZ, loading individual files from %s (Error message: %s)", dataPath, e, exc_info=False)

            targetFinder = FilesTargetsCrawler(dataPath)
            targetFinder.findTargets()
            log.debug("%s targets loaded from .target files.", len(targetFinder.targets))

        self.targets = targetFinder.targets
        self.groups = targetFinder.groups
        self.images = targetFinder.images
        self.index = targetFinder.index


_targets = None

def getTargets():
    global _targets
    if _targets is None:
        _targets = Targets(getSysDataPath())
    return _targets
