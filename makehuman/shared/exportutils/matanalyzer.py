#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Material Analysis class.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

The Material Analyzer module implements the MaterialAnalysis class,
a class that is able to prepare the textures of a list of RichMeshes
according to instructions passed to it through a dictionary.

This class is a very useful tool for easier writing of exporter modules.
It includes functionality for returning specialized and specially
formatted strings for each texture, according to the passed instructions,
so that texture definitions, specialized for each exporter, are directly
exported without the addition of extra string formatting code.

The module also includes several handy image_operations functions to use
with the analyzer, by updating the functions dictionary with them before
passing it to the class.

"""

import os
import log
import numbers
import shutil

class MaterialAnalysis(object):
    def __init__(self, rmeshes, map, functions):
        self.map = map
        self.rmeshes = rmeshes
        self.functions = functions
        self.objects = {rmesh:self.Object(self, rmesh) for rmesh in rmeshes}

    def __getitem__(self, key):
        if isinstance(key, numbers.Integral):
            return self.objects[self.rmeshes[key]]
        else:
            return self.objects[key]

    def __len__(self):
        return len(self.objects)

    class Object(object):
        def __init__(self, analyzer, rmesh):
            self.analyzer = analyzer
            self.rmesh = rmesh
            for name in analyzer.map.keys():
                setattr(self, name, self.Texture(self, name))

        def getTex(self, tex, cguard = []):
            if isinstance(tex, tuple):
                if tex[0] == 'param':
                    return tex[1]
                elif tex[0] == 'tuple':
                    return tuple([self.getTex(t) for t in tex[1:]])
                elif tex[0] == 'list':
                    return [self.getTex(t) for t in tex[1:]]
                else:
                    return self.analyzer.functions[tex[0]](*tuple([self.getTex(t, cguard) for t in tex[1:]]))
            elif isinstance(tex, basestring):
                if "." in tex:
                    txs = tex.split(".", 2)
                    if txs[0] == "mat":
                        try:
                            if (getattr(self.rmesh.material, 'supports' + txs[1].capitalize())() and
                                self.rmesh.material.shaderConfig['spec' if txs[1] == 'specular' else txs[1]]):
                                return getattr(self.rmesh.material, txs[1] + ('' if txs[1] == 'diffuse' else 'Map') + 'Texture')
                            else:
                                return None
                        except KeyError: # In case the material has no shader config for the texture
                            return None
                    elif txs[0] == "func":
                        if txs[1] in self.analyzer.functions:
                            if len(txs) == 2:
                                return self.analyzer.functions[txs[1]](self.rmesh)
                            else:
                                return self.analyzer.functions[txs[1]](self.rmesh, txs[2])
                        else:
                            raise NameError('Analyzer has no function named "%s"' % txs[1])
                    elif txs[0] == "param":
                        return txs[1] if len(txs) == 2 else ".".join(txs[1:])
                    else:
                        raise NameError('"%s" is an invalid texture source' % txs[0])
                else:
                    return getattr(self, tex).get(cguard)
            else:
                return tex
        
        class Texture(object):
            def __init__(self, Object, name):
                self.Object = Object
                self.name = name
                self.isCompiled = False
                self.compiled = None

            def __nonzero__(self):
                return bool(self.get())

            # Process, if needed, and get the final texure.
            def get(self, cguard = []):
                
                # After the texture has been processed once, save it in a variable,
                # and return it the next time it is requested, instead of reprocessing.
                if self.isCompiled:
                    return self.compiled
                else:
                    self.isCompiled = True
                
                # Cross - guard to prevent infinite loops.
                if self in cguard:
                    self.compiled = None
                    return None
                else:
                    cguard.append(self)

                # Get list of alternative textures by looking up Texture.name in the map.
                mapentry = self.Object.analyzer.map[self.name]
                if isinstance(mapentry, tuple):
                    texlist = mapentry[0]
                else:   # Enable the user to avoid tuples if the Texture has no definition.
                    texlist = mapentry
                # Enable the user to avoid creating a list if the Texture has no alternatives.
                if not isinstance(texlist, list):
                    texlist = [texlist]
                    
                # Return the first texture in the map list that exists.
                self.successfulAlternative = -1
                for tex in texlist:
                    self.successfulAlternative += 1
                    rt = self.Object.getTex(tex, cguard)
                    if rt is not None:
                        self.compiled = rt
                        return rt

                # If no texture was found, return None.
                self.successfulAlternative = -1
                self.compiled = None
                return None

            # Get the extension that the saved texture will have.
            def getSaveExt(self):
                tex = self.get()
                return os.path.splitext(tex)[-1] if isinstance(tex, basestring) else ".png"

            # Get the filename that the saved texture will have.
            def getSaveName(self, altTexName = None):
                return self.Object.rmesh.name + "_" + (altTexName if altTexName else self.name) + self.getSaveExt()
            
            # Save the final texture.
            def save(self, path):
                tex = self.get()
                if tex is not None:
                    dest = os.path.join(path, self.getSaveName())
                    if isinstance(tex, basestring):
                        shutil.copy(tex, dest)
                        log.debug('Copied %s to %s', tex, dest)
                    else:
                        tex.save(dest)
                        log.debug('Saved texture to %s', dest)

            # Write exporter definition for the texture.
            def define(self, options = {}, func = None):

                # Function to analyze definition-writer functions.
                def analyzeDef(tdi):
                    
                    if isinstance(tdi, basestring):
                        if "." in tdi:      # First we resolve the texture scope.
                            fsp = tdi.split(".", 1)
                            return getattr(self.Object, fsp[0]).define(options, fsp[1])
                        elif " " in tdi:    # If the scope is the current texture, we execute any commands.
                            fsp = tdi.split(" ", 1)
                            if fsp[0] == 'use':                 # Use the definition from another texture type for writing this definition.
                                return getattr(self.Object, fsp[1]).define(options)
                            else:                               # Command does not exist. Raise an error.
                                raise NameError('"%s": Texture definition command does not exist' % fsp[0])
                        else:               # If no commands are issued, we write the definition using the given function.
                            return self.Object.analyzer.functions[tdi](self, options)
                    elif isinstance(tdi, tuple):
                        return (tdi[1] if tdi[0] == 'param'     # 'param' overrides analysis and passes the second element directly.
                                else self.Object.analyzer.functions[tdi[0]](*tuple(
                                    [analyzeDef(f) for f in tdi[1:]])))
                    elif tdi is None:
                        return ""
                    else:
                        return tdi

                if not func:
                    # Get the map item associated with the current Texture.
                    mapitem = self.Object.analyzer.map[self.name]
                    if len(mapitem) == 2:
                        # If it has only 1 definition-writer function, use it.
                        func = mapitem[1]
                    else:
                        # Else, use the first provided definition-writer function
                        # if the texture exists, else the second
                        # (2nd and 3rd map tuple item respectively).
                        func = mapitem[(1 if self.__nonzero__() else 2)]

                return analyzeDef(func)
                    

import image_operations as imgop

imgopfuncs = {
    'black': lambda img: imgop.getBlack(img) if img else None,
    'white': lambda img: imgop.getWhite(img) if img else None,
    'blur': lambda img, lev, ker: imgop.blurred(imgop.Image(data = img), lev, ker) if img else None,
    'compose': lambda l: imgop.compose(l),
    'getChannel': lambda t, c: imgop.getChannel(imgop.Image(data = t),c) if t else None,
    'getAlpha': lambda t: imgop.getAlpha(imgop.Image(data = t)) if t else None,
    'growMask': lambda t, p: imgop.growMask(imgop.Image(data = t), p) if t else None,
    'shrinkMask': lambda t, p: imgop.shrinkMask(imgop.Image(data = t), p) if t else None}

