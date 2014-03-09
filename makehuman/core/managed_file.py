#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
File class definition
=====================

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module defines the File class, an object that represents a file that
is being edited inside MakeHuman.

"""

import os


class File(object):
    """Object class representing a file that is being opened and edited
    from inside the application.

    It can be used for managing project files, and handling the currently
    opened files in a Graphical User Interface using an organized structure.

    This class is intented to be inherited from, so that specific file types
    implement their own save and load methods.
    """

    def __init__(self, path=None):
        """File object constructor.

        The managed File class has a path member,
        necessary for knowing to which file on disk
        this File object corresponds.

        A File object also contains a modified flag, to indicate whether
        a change occured since the last save or load action.
        """

        self._path = path

        self.modified = False

    @property
    def path(self):
        """Get the full path of the associated file."""
        return self._path

    @property
    def name(self):
        """Get the filename of the associated file."""
        if self.path is not None:
            return os.path.basename(self.path)
        else:
            return None

    @property
    def extension(self):
        """Get the extension of the associated file."""
        if self.path is not None:
            return os.path.splitext(self.path)[1]
        else:
            return None

    @property
    def title(self):
        """Get the title of the associated file,
        which is the filename without the extension."""
        if self.path is not None:
            return os.path.splitext(self.name)[0]
        else:
            return None

    @property
    def dir(self):
        """Get the directory of the associated file."""
        if self.path is not None:
            return os.path.dirname(self.path)
        else:
            return None

    def save(self, path):
        """Method that the user will call to save the File to disk.

        The method is intented to be overwritten by the implementation,
        and shall set the _path member and clear the modified flag accordingly.

        Implementations may treat save(None) as overwrite
        of the current file.
        """
        pass

    def load(self, path):
        """Method that the user will call to load the File from disk.

        The method is intented to be overwritten by the implementation,
        and shall set the _path member and clear the modified flag accordingly.

        Implementations may treat load(None) as loading
        of a default (built-in) file.
        """
        pass

    def reload(self):
        """Reload the currently associated file."""
        self.load(self.path)
