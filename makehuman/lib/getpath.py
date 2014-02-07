#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Manuel Bastioni, Marc Flerackers, Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Utility module for finding the user home path.
"""

import sys
import os

__home_path = None

def formatPath(path):
    if path is None:
        return None
    return os.path.normpath(path).replace("\\", "/")

def canonicalPath(path):
    """
    Return canonical name for location specified by path.
    Useful for comparing paths.
    """
    return formatPath(os.path.realpath(path))

def localPath(path):
    """
    Returns the path relative to the MH program directory,
    i.e. the inverse of canonicalPath. Needed to get
    human.targetsDetailStack keys from algos3d.targetBuffer keys.
    If all buffers use the same keys, this becomes obsolete.
    """
    path = os.path.realpath(path)
    root = os.path.realpath(".")
    return formatPath(os.path.relpath(path, root))

def getHomePath():
    """
    Find the user home path.
    Note: If you are looking for MakeHuman data, you probably want getPath()!
    """
    # Cache the home path
    global __home_path
    if __home_path is not None:
        return __home_path

    # Windows
    if sys.platform == 'win32':
        import _winreg
        keyname = r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
        #name = 'Personal'
        k = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, keyname)
        value, type_ = _winreg.QueryValueEx(k, 'Personal')
        if type_ == _winreg.REG_EXPAND_SZ:
            __home_path = formatPath(_winreg.ExpandEnvironmentStrings(value))
            return __home_path
        elif type_ == _winreg.REG_SZ:
            __home_path = formatPath(value)
            return __home_path
        else:
            raise RuntimeError("Couldn't determine user folder")

    # Unix-based
    else:
        __home_path = os.path.expanduser('~')
        return __home_path

def getPath(subPath = ""):
    """
    Get MakeHuman folder that contains per-user files, located in the user home
    path.
    """
    path = getHomePath()

    # Windows
    if sys.platform == 'win32':
        path = os.path.join(path, "makehuman")

    # MAC OSX
    elif sys.platform.startswith("darwin"):
        path = os.path.join(path, "Documents")
        path = os.path.join(path, "MakeHuman")

    # Unix/Linux
    else:
        path = os.path.join(path, "makehuman")

    path = os.path.join(path, 'A8')

    if subPath:
        path = os.path.join(path, subPath)

    return formatPath(path)

def getSysDataPath(subPath = ""):
    """
    Path to the data folder that is installed with MakeHuman system-wide.
    """
    if subPath:
        path = getSysPath( os.path.join("data", subPath) )
    else:
        path = getSysPath("data")
    return formatPath(path)

def getSysPath(subPath = ""):
    """
    Path to the system folder where MakeHuman is installed (it is possible that
    data is stored in another path).
    Writing to this folder or modifying this data usually requires admin rights,
    contains system-wide data (for all users).
    """
    if subPath:
        path = os.path.join('.', subPath)
    else:
        path = "."
    return formatPath(path)


def _allnamesequal(name):
    return all(n==name[0] for n in name[1:])

def commonprefix(paths, sep='/'):
    """
    Implementation of os.path.commonprefix that works as you would expect.

    Source: http://rosettacode.org/wiki/Find_Common_Directory_Path#Python
    """
    from itertools import takewhile

    bydirectorylevels = zip(*[p.split(sep) for p in paths])
    return sep.join(x[0] for x in takewhile(_allnamesequal, bydirectorylevels))

def isSubPath(subpath, path):
    """
    Verifies whether subpath is within path.
    """
    subpath = canonicalPath(subpath)
    path = canonicalPath(path)
    return commonprefix([subpath, path]) == path

def getRelativePath(path, relativeTo = [getPath(), getSysPath()]):
    """
    Return a relative file path, relative to one of the specified search paths.
    First valid path is returned, so order in which search paths are given matters.
    """
    if not isinstance(relativeTo, list):
        relativeTo = [relativeTo]

    relto = None
    for p in relativeTo:
        if isSubPath(path, p):
            relto = p
    if relto is None:
        return path

    return formatPath( os.path.relpath(path, relto) )

def findFile(relPath, searchPaths = [getPath(), getSysPath()]):
    """
    Inverse of getRelativePath: find an absolute path from specified relative
    path in one of the search paths.
    First occurence is returned, so order in which search paths are given matters.
    """
    if not isinstance(searchPaths, list):
        searchPaths = [searchPaths]

    for dataPath in searchPaths:
        path = os.path.join(dataPath, relPath)
        if os.path.isfile(path):
            return formatPath( path )

    return relPath

