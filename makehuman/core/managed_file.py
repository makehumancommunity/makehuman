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
import log
import events3d


class FileModifiedEvent(events3d.Event):
    """Event class to be emitted upon modification of a managed File object.

    It contains information about the state of the modified flag and
    possibly about the reason that the event was triggered.
    """

    def __init__(self, file, value, oldvalue, reason=None, data=None):
        """FileModifiedEvent constructor.

        The FileModifiedEvent object has .value and .oldvalue members for
        the new and the previous state of the associated File object's
        modified flag.

        The reason argument might be a string or a container of strings to be
        inserted as the emitted event's .reasons set. It may describe
        aditional information about the cause of the event, with a usage
        similar to using flags - i.e. like: if "save" in event.reasons: (...).

        The data member is an optional extra object for the event to carry.
        A good practice for this could be to be a dictionary of attributes
        that can provide information about the event.
        """

        events3d.Event.__init__(self)

        self.file = file
        self.value = value
        self.oldvalue = oldvalue
        self.reasons = set()
        self.addReason(reason)
        self.data = data

    def __repr__(self):
        """Print out information about the FileModifiedEvent."""
        return "FileModifiedEvent: file: %s, flag state: %s, previous flag state: %s, reasons: %s" % (
            self.file.path, repr(self.value), repr(self.oldvalue), repr(self.reasons))

    def __nonzero__(self):
        """Boolean representation of the event. Returns its .value member."""
        return self.value

    def addReason(self, reason):
        """Add the given reason to the event's reason list."""
        if reason is not None:
            if hasattr(reason, '__iter__'):
                self.reasons |= set(reason)
            else:
                self.reasons.add(reason)

    @property
    def objectWasChanged(self):
        """Return whether the cause that triggered the event has altered
        the associated object's data.

        This method can be used by external classes for invoking
        update routines.
        """
        return self.value or "load" in self.reasons

    @property
    def pathWasChanged(self):
        """Return whether the cause that triggered the event has changed
        the location of the associated file.

        This method can be used by external classes for updating path
        inspectors like path explorers / tree views.
        """
        return "newpath" in self.reasons


class File(events3d.EventHandler):
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
        a change occured since the last save or load action. This flag is
        a property that emits events upon assignment, which can be used
        for signaling external classes to update their data.
        """

        events3d.EventHandler.__init__(self)

        self._path = None
        self._modified = False

        self.load(path)

    def getModified(self):
        """Get the state of the modified flag."""
        return self._modified

    def setModified(self, value):
        """Set the value of the modified flag and emit an event."""
        event = FileModifiedEvent(self, value, self._modified)
        self._modified = value
        self.callEvent('onModified', event)

    modified = property(getModified, setModified)

    def changed(self, reason=None, data=None):
        """Method to be called when the File's associated data is modified.

        Without arguments, it is equivalent to File.modified = True.
        Extra arguments are passed to the FileModifiedEvent constructor.
        """

        event = FileModifiedEvent(self, True, self._modified, reason, data)
        self._modified = True
        self.callEvent('onModified', event)

    def _associate(self, path, reason, extrareason=None, data=None):
        """Internal method that associates the File object with a path."""
        if isinstance(path, basestring):
            path = os.path.normpath(path)

        event = FileModifiedEvent(self, False, self._modified, reason, data)
        self._modified = False
        event.addReason(extrareason)
        if path != self.path:
            event.addReason("newpath")
            self._path = path
        self.callEvent('onModified', event)

    def saved(self, path, reason=None, data=None):
        """Method to be called after saving the file to a path."""
        self._associate(path, "save", reason, data)

    def loaded(self, path, reason=None, data=None):
        """Method to be called after loading the file from a path."""
        self._associate(path, "load", reason, data)

    def closed(self, reason=None, data=None):
        """Method to be called after closing the file."""
        self._associate(None, ("load", "close"), reason, data)

    @property
    def path(self):
        """Get the full path of the associated file."""
        return self._path

    @property
    def filename(self):
        """Get the filename of the associated file."""
        if self.path is not None:
            return os.path.basename(self.path)
        else:
            return None

    @property
    def fileextension(self):
        """Get the extension of the associated file."""
        if self.path is not None:
            return os.path.splitext(self.path)[1]
        else:
            return None

    @property
    def filetitle(self):
        """Get the title of the associated file,
        which is the filename without the extension."""
        if self.path is not None:
            return os.path.splitext(self.filename)[0]
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
        and shall call the saved() method upon success.
        """

        self.saved(path)
        return True

    def load(self, path):
        """Method that the user will call to load the File from disk.

        The method is intented to be overwritten by the implementation,
        and shall call the loaded() method upon success.

        Implementations should process load(None) as a call to close().
        """

        if path is None:
            return self.close()

        self.loaded(path)
        return True

    def close(self):
        """Method that the user will call to close the File.
        It presets the File object to its initial state.

        The method is intented to be overwritten by the implementation,
        and shall call the closed() method upon success.
        """

        self.closed()
        return True

    def reload(self):
        """Reload the currently associated file.

        Useful when the associated file is modified externally.
        """

        return self.load(self.path)
