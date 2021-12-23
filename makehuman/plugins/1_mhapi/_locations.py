#!/usr/bin/python

from .namespace import NameSpace

import getpath
import os
import sys

class Locations(NameSpace):
    """This namespace wraps all calls that are related to file and directory locations."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()

    def getUnicodeAbsPath(self,path):
        """Returns the abspath version of path, and ensures that it is correctly encoded"""
        ap = os.path.abspath(path)

        # In later python versions, there is a path object model that
        # could be investigated. Assume all is well in python 3 for now though
        if self.api.utility.isPython3():
            return ap

        en = sys.getfilesystemencoding()
        if isinstance(ap,unicode) or en == "UTF-8":
            # Assume we already have a valid UTF-8 string
            upath = ap
        else:
            # Assume we need to perform encoding            
            upath = unicode(ap,en)
        return upath

    def getInstallationPath(self,subpath = ""):
        """Returns the unicode-encoded absolut path to the directory which contains the makehuman.py file"""
        self.trace()
        return self.getUnicodeAbsPath(getpath.getSysPath(subpath))

    def getSystemDataPath(self,subpath = ""):
        """Returns the unicode-encoded absolute path to the location of the user's "data" directory (as opposed to the installation's data directory). If subpath is given, assume that a subdirectory is indicated and return the combined path."""
        self.trace()
        return self.getUnicodeAbsPath(getpath.getSysDataPath(subpath))

    def getUserHomePath(self, subpath = ""):
        """Returns unicode-encoded absolute path to the location of the user's makehuman directory (i.e normally ~/makehuman)."""
        self.trace()
        if subpath == "":
            return self.getUnicodeAbsPath(getpath.getHomePath())
        else:
            return self.getUnicodeAbsPath(getpath.getPath(subpath))

    def getUserDataPath(self,subpath = ""):
        """Returns unicode-encoded absolute path to the location of the user's "data" directory (as opposed to the installation's data directory)"""
        self.trace()
        return self.getUnicodeAbsPath(getpath.getDataPath(subpath))


