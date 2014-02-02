#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Definitions of scene objects and the scene class.
.mhscene file structure.
"""

import events3d
import pickle
import log
from material import Color

mhscene_version = 5
mhscene_minversion = 5

class SceneObject(object):
    def __init__(self, scene = None, attributes = {}):
        object.__init__(self)
        self._attributes = sorted(attributes.keys())
        self._attrver = {}

        for (attrname, attr) in attributes.items():
            
            # Version control system for backwards compatibility
            # with older mhscene files.
            # Usage: 'attribute': [attribute, minversion]
            # Or: 'attribute': [attribute, (minversion, maxversion)]
            # Or: 'attribute': [attribute, [(minver1, maxver1), (minver2, maxver2), ...]]
            attribute = None
            if isinstance(attr, list):
                attribute = attr[0]
                if isinstance(attr[1], list):
                    self._attrver[attrname] = attr[1]
                elif isinstance(attr[1], tuple):
                    self._attrver[attrname] = [attr[1]]
                else:
                    self._attrver[attrname] = [(attr[1], mhscene_version)]
            else:
                attribute = attr
                self._attrver[attrname] = [(mhscene_minversion, mhscene_version)]
                
            object.__setattr__(self, "_" + attrname, attribute)
            
        self._scene = scene
        

    def __getattr__(self, attr):
        if attr in object.__getattribute__(self, "_attributes"):
            return object.__getattribute__(self, "_" + attr)
        elif hasattr(self, attr):
            return object.__getattribute__(self, attr)
        else:
            raise AttributeError('"%s" type scene objects do not have any "%s" attribute.' % (type(self), attr))

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
                self.changed(False)
        else:
            object.__setattr__(self, attr, value)
                
    def changed(self, modified = True):
        if (self._scene is not None):
            self._scene.changed(modified)
       
    def getAttributes(self):
        return self._attributes

    def save(self, hfile):
        for attr in self._attributes:
            pickle.dump(getattr(self, "_" + attr), hfile)

    def load(self, hfile):
        for attr in self._attributes:

            # Check if attribute exists in the file by checking
            # the compatibility of their versions
            filever = self._scene.filever
            supported = False
            for verlim in self._attrver[attr]:
                if filever >= verlim[0] and filever <= verlim[1]:
                    supported = True
                    break

            if supported:
                attrV = pickle.load(hfile)
                if isinstance( getattr(self, "_" + attr), Color ):
                    setattr(self, "_" + attr, Color(attrV))
                else:
                    setattr(self, "_" + attr, attrV)

    
class Light(SceneObject):
    def __init__(self, scene = None):
        SceneObject.__init__(
            self, scene,
            attributes =
            {'position': (-10.99, 20.0, 20.0),
             'focus': (0.0, 0.0, 0.0),
             'color': Color(1.0, 1.0, 1.0),
             'specular': [Color(1.0, 1.0, 1.0), 5],
             'fov': 180.0,
             'attenuation': 0.0,
             'areaLights': 1,
             'areaLightSize': 4.0})


class Environment(SceneObject):
    def __init__(self, scene = None):
        SceneObject.__init__(
            self, scene,
            attributes =
            {'ambience': Color(0.2, 0.2, 0.2),
             'skybox': None})


class Scene(events3d.EventHandler):
    def __init__(self, path = None):
        if path is None:
            self.lights = [Light(self)]
            self.environment = Environment(self)
            
            self.unsaved = False
            self.path = None
        else:
            self.load(path)

    def changed(self, modified = True):
        self.unsaved = modified
        self.callEvent('onChanged', self)

    def load(self, path):   # Load scene from a .mhscene file.        
        hfile = open(path, 'rb')
        self.filever = pickle.load(hfile)
        if (self.filever < mhscene_minversion):   # Minimum supported version
            hfile.close()
            return False
        self.unsaved = False
        self.path = path
        
        self.environment.load(hfile)
        nlig = pickle.load(hfile)
        self.lights = []
        for i in xrange(nlig):
            light = Light(self)
            light.load(hfile)
            self.lights.append(light)
        hfile.close()
        return True

    def save(self, path = None):    # Save scene to a .mhscene file.
        if path is not None:
            self.path = path
        self.unsaved = False
        hfile = open(self.path, 'wb')
        pickle.dump(mhscene_version, hfile)
        
        self.environment.save(hfile)
        pickle.dump(len(self.lights), hfile)
        for light in self.lights:
            light.save(hfile)
        hfile.close()

    def close(self):
        self.__init__()

    def addLight(self):
        self.changed()
        newlight = Light(self)
        self.lights.append(newlight)

    def removeLight(self, light):
        self.changed()
        self.lights.remove(light)

