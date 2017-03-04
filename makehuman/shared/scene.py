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

Definitions of scene objects and the scene class.
.mhscene file structure.
"""

import cPickle as pickle

import log
import managed_file
from material import Color

mhscene_version = 5
mhscene_minversion = 5


class FileVersionException(Exception):
    def __init__(self, reason=None):
        Exception.__init__(self)
        self.reason = reason

    def __str__(self):
        if self.reason is None:
            erstr = "Incompatible file version"
        elif self.reason == "#too old":
            erstr =\
"The version of this file is no more supported by this version of MakeHuman."
        elif self.reason == "#too new":
            erstr =\
"The version of MakeHuman you are using is too old to open this file."
        else:
            erstr = repr(self.reason)
        return erstr


def checkVersions(versions, version_exception_class=None):
    if versions[0] is not None and versions[1] < versions[0]:
        if version_exception_class is not None:
            raise version_exception_class("#too old")
        return False
    elif versions[2] is not None and versions[1] > versions[2]:
        if version_exception_class is not None:
            raise version_exception_class("#too new")
        return False
    else:
        return True


class SceneObject(object):
    def __init__(self, scene=None, attributes={}):
        object.__init__(self)
        self._attributes = sorted(attributes.keys())
        self._attrver = {}

        for (attrname, attr) in attributes.items():

            # Version control system for backwards compatibility
            # with older mhscene files.
            # Usage: 'attribute': [attribute, minversion]
            # Or: 'attribute': [attribute, (minversion, maxversion)]
            # Or: 'attribute':
            #     [attribute, [(minver1, maxver1), (minver2, maxver2), ...]]
            attribute = None
            if isinstance(attr, list):
                attribute = attr[0]
                if isinstance(attr[1], list):
                    self._attrver[attrname] = attr[1]
                elif isinstance(attr[1], tuple):
                    self._attrver[attrname] = [attr[1]]
                else:
                    self._attrver[attrname] = [(attr[1], None)]
            else:
                attribute = attr
                self._attrver[attrname] = [(None, None)]

            object.__setattr__(self, "_" + attrname, attribute)

        self._scene = scene

    def __getattr__(self, attr):
        if attr in object.__getattribute__(self, "_attributes"):
            return object.__getattribute__(self, "_" + attr)
        elif hasattr(self, attr):
            return object.__getattribute__(self, attr)
        else:
            raise AttributeError(
                '"%s" type scene objects do not have any "%s" attribute.'
                % (type(self), attr))

    def __setattr__(self, attr, value):
        if hasattr(self, "_attributes") and attr in self._attributes:
            attrValue = getattr(self, "_" + attr)
            if isinstance(attrValue, Color):
                # Ensure Color attributes are of type Color
                value = Color(value)
            if (attrValue != value):
                object.__setattr__(self, "_" + attr, value)
                self.changed()
        else:
            object.__setattr__(self, attr, value)

    def changed(self):
        if (self._scene is not None):
            self._scene.changed()

    def getAttributes(self):
        return self._attributes

    def save(self, hfile):
        for attr in self._attributes:
            pickle.dump(getattr(self, "_" + attr), hfile, protocol=2)

    def load(self, hfile):
        for attr in self._attributes:

            # Check if attribute exists in the file by checking
            # the compatibility of their versions
            filever = self._scene.filever
            supported = False
            for verlim in self._attrver[attr]:
                if checkVersions((verlim[0], filever, verlim[1])):
                    supported = True
                    break

            if supported:
                attrV = pickle.load(hfile)
                if isinstance(getattr(self, "_" + attr), Color):
                    setattr(self, "_" + attr, Color(attrV))
                else:
                    setattr(self, "_" + attr, attrV)


class Light(SceneObject):
    def __init__(self, scene=None):
        SceneObject.__init__(
            self, scene,
            attributes=
            {'position': (-10.99, 20.0, 20.0),
             'focus': (0.0, 0.0, 0.0),
             'color': Color(1.0, 1.0, 1.0),
             'specular': [Color(1.0, 1.0, 1.0), 5],
             'fov': 180.0,
             'attenuation': 0.0,
             'areaLights': 1,
             'areaLightSize': 4.0})


class Environment(SceneObject):
    def __init__(self, scene=None):
        SceneObject.__init__(
            self, scene,
            attributes=
            {'ambience': Color(0.3, 0.3, 0.3),
             'skybox': None})


class Scene(object):
    def __init__(self, path=None):
        self.lights = []
        self.environment = Environment(self)

        self.file = managed_file.File()

        self.load(path)

    def load(self, path):
        """Load scene from a .mhscene file."""

        if path is None:
            return self.reset()

        log.debug('Loading scene file: %s', path)

        try:
            hfile = open(path, 'rb')
        except IOError as e:
            log.warning('Could not load %s: %s', path, e[1])
            return False
        except Exception as e:
            log.error('Failed to load scene file %s\nError: %s',
                path, repr(e), exc_info=True)
            return False
        else:
            try:
                # Ensure the file version is supported
                filever = pickle.load(hfile)
                checkVersions(
                    (mhscene_minversion, filever, mhscene_version),
                    FileVersionException)

                # TODO: Save current state in temporary buffer
                # before loading, for reverting in case of error
                self.filever = filever
                self.environment.load(hfile)
                nlig = pickle.load(hfile)
                self.lights = []
                for i in xrange(nlig):
                    light = Light(self)
                    light.load(hfile)
                    self.lights.append(light)
            except FileVersionException as e:
                log.warning('%s: %s', path, e)
                hfile.close()
                return False
            except Exception as e:
                log.error('Failed to load scene file %s\nError: %s\n',
                    path, repr(e), exc_info=True)
                # TODO: Revert to buffered saved state here instead
                if path != self.path:
                    self.load(self.path)
                else:
                    self.close()
                hfile.close()
                return False
            hfile.close()

        self.file.loaded(path)
        return True

    # Save scene to a .mhscene file.
    def save(self, path):
        log.debug('Saving scene file: %s', path)

        try:
            hfile = open(path, 'wb')
        except IOError as e:
            log.warning('Could not save %s: %s', path, e[1])
            return False
        except Exception as e:
            log.error('Failed to save scene file %s\nError: %s\n',
                path, repr(e), exc_info=True)
            return False
        else:
            try:
                pickle.dump(mhscene_version, hfile, protocol=2)
                self.environment.save(hfile)
                pickle.dump(len(self.lights), hfile, protocol=2)
                for light in self.lights:
                    light.save(hfile)
            except Exception as e:
                log.error('Failed to save scene file %s\nError: %s\n',
                    path, repr(e), exc_info=True)
                hfile.close()
                return False
            hfile.close()

        self.file.saved(path)
        return True

    def reset(self):
        log.debug('Loading default scene')

        self.lights = [Light(self)]
        self.environment = Environment(self)
        # TODO: Hardcoded defaults should be set here, not in classes.

        self.file.closed()
        return True

    def changed(self, *args, **kwargs):
        self.file.changed(*args, **kwargs)

    def addLight(self):
        newlight = Light(self)
        self.lights.append(newlight)
        self.file.changed(("add", "light"))

    def removeLight(self, light):
        self.lights.remove(light)
        self.file.changed(("remove", "light"))
