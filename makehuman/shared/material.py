#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
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

MakeHuman Material format with parser and serializer.
"""

import log
import os

_autoSkinBlender = None

class Color(object):
    def __init__(self, r=0.00, g=0.00, b=0.00):
        if hasattr(r, '__iter__'):
            # Copy constructor
            self.copyFrom(r)
        else:
            self.setValues(r,g,b)

    def setValues(self, r, g, b):
        self.setR(r)
        self.setG(g)
        self.setB(b)

    def getValues(self):
        return [self.r, self.g, self.b]

    values = property(getValues, setValues)

    def setR(self, r):
        self._r = max(0.0, min(1.0, float(r)))

    def setG(self, g):
        self._g = max(0.0, min(1.0, float(g)))

    def setB(self, b):
        self._b = max(0.0, min(1.0, float(b)))

    def getR(self):
        return self._r

    def getG(self):
        return self._g

    def getB(self):
        return self._b

    r = property(getR, setR)
    g = property(getG, setG)
    b = property(getB, setB)

    def __repr__(self):
        return "Color(%s %s %s)" % (self.r,self.g,self.b)

    # List interface
    def __getitem__(self, key):
        return self.asTuple()[key]

    def __iter__(self):
        return self.asTuple().__iter__()

    def copyFrom(self, color):
        r = color[0]
        g = color[1]
        b = color[2]
        self.setValues(r, g, b)

        return self

    def clone(self):
        return type(self)().copyFrom(self)

    def asTuple(self):
        return (self.r, self.g, self.b)

    def asStr(self):
        return "%r %r %r" % self.asTuple()

    # Comparison operators
    def __lt__(self, other):
        return self.asTuple().__lt__(other.asTuple())

    def __le__(self, other):
        return self.asTuple().__le__(other.asTuple())

    def __eq__(self, other):
        return self.asTuple().__eq__(other.asTuple())

    def __ne__(self, other):
        return self.asTuple().__ne__(other.asTuple())

    def __gt__(self, other):
        return self.asTuple().__gt__(other.asTuple())

    def __ge__(self, other):
        return self.asTuple().__ge__(other.asTuple())

    # Arithmetic operators
    # Vector operators are performed element-wise and expect an iterable with at least 3 elements
    def __add__(self, other):
        return type(self)(self.r + other[0], self.g + other[1], self.b + other[2])

    def __radd__(self, other):
        return type(self)(other[0] + self.r, other[1] + self.g, other[2] + self.b)

    def __sub__(self, other):
        return type(self)(self.r - other[0], self.g - other[1], self.b - other[2])

    def __rsub__(self, other):
        return type(self)(other[0] - self.r, other[1] - self.g, other[2] - self.b)

    # Scalar operators work both with iterables as well as single values
    def __mul__(self, other):
        if isinstance(other, (int, float, long, bool)):
            return type(self)(self.r * other, self.g * other, self.b * other)
        else:
            return type(self)(self.r * other[0], self.g * other[1], self.b * other[2])

    def __rmul__(self, other):
        if isinstance(other, (int, float, long, bool)):
            return type(self)(other * self.r, other * self.g, other * self.b)
        else:
            return type(self)(other[0] * self.r, other[1] * self.g, other[2] * self.b)

    def __div__(self, other):
        if isinstance(other, (int, float, long, bool)):
            return type(self)(self.r / other, self.g / other, self.b / other)
        else:
            return type(self)(self.r / other[0], self.g / other[1], self.b / other[2])

    def __rdiv__(self, other):
        if isinstance(other, (int, float, long, bool)):
            return type(self)(other / self.r, other / self.g, other / self.b)
        else:
            return type(self)(other[0] / self.r, other[1] / self.g, other[2] / self.b)

# Protected shaderDefine parameters that are set exclusively by means of shaderConfig options (configureShading())
_shaderConfigDefines = ['DIFFUSE', 'BUMPMAP', 'NORMALMAP', 'DISPLACEMENT', 'SPECULARMAP', 'VERTEX_COLOR', 'TRANSPARENCYMAP', 'AOMAP']

# Protected shader parameters that are set exclusively by means of material properties (configureShading())
_materialShaderParams = ['diffuse', 'ambient', 'specular', 'emissive', 'diffuseTexture', 'bumpmapTexture', 'bumpmapIntensity', 'normalmapTexture', 'normalmapIntensity', 'displacementmapTexture', 'displacementmapTexture', 'specularmapTexture', 'specularmapIntensity', 'transparencymapTexture', 'transparencymapIntensity', 'aomapTexture', 'aomapIntensity']

# Generic list of the names of texture members of material (append "Texture" to get the member name)
textureTypes = ["diffuse", "bumpMap", "normalMap", "displacementMap", "specularMap", "transparencyMap", "aoMap"]

# TODO a more generic approach to declaring material properties could reduce code duplication a lot
class Material(object):
    """
    Material definition.
    Defines the visual appearance of an object when it is rendered (when it is
    set to solid).

    NOTE: Use one material per object! You can use copyFrom() to duplicate
    materials.
    """

    def __init__(self, name="UnnamedMaterial", performConfig=True):
        if isinstance(name, Material):
            # Copy constructor (after initing the material class)
            self.name = "UnnamedMaterial"
        else:
            self.name = name

        self.description = "%s material" % name

        self.filename = None
        self.filepath = None

        self.tags = set()

        self._ambientColor = Color(1.0, 1.0, 1.0)
        self._diffuseColor = Color(1.0, 1.0, 1.0)
        self._specularColor = Color(1.0, 1.0, 1.0)
        self._shininess = 0.2
        self._emissiveColor = Color()

        self._opacity = 1.0
        self._translucency = 0.0

        self._shadeless = False   # Set to True to disable shading. Configured shader will have no effect
        self._wireframe = False   # Set to True to do wireframe render
        self._transparent = False # Set to True to enable transparency rendering (usually needed when opacity is < 1)
        self._backfaceCull = True # Set to False to disable backface culling (render back of polygons)
        self._depthless = False   # Set to True for depthless rendering (object is not occluded and does not occlude other objects)
        self._castShadows = True  # Set to True to make the object cast shadows on others.
        self._receiveShadows = True # Set to True to make the object receive shadows from others
        self._alphaToCoverage = True # Applies when _transparent is True, and GPU supports alpha to coverage (A2C) rendering. Enables A2C feature (disables anti-aliasing for this object which also uses the multisample buffer)

        self._autoBlendSkin = False # Set to True to adapt diffuse color and litsphere texture to skin tone

        self._diffuseTexture = None
        self._bumpMapTexture = None
        self._bumpMapIntensity = 1.0
        self._normalMapTexture = None
        self._normalMapIntensity = 1.0
        self._displacementMapTexture = None
        self._displacementMapIntensity = 1.0
        self._specularMapTexture = None
        self._specularMapIntensity = 1.0
        self._transparencyMapTexture = None
        self._transparencyMapIntensity = 1.0
        self._aoMapTexture = None
        self._aoMapIntensity = 1.0

        # Sub-surface scattering parameters
        self._sssEnabled = False
        self._sssRScale = 0.0
        self._sssGScale = 0.0
        self._sssBScale = 0.0

        self._shader = None
        self._shaderConfig = {
            'diffuse'      : True,
            'bump'         : True,
            'normal'       : True,
            'displacement' : True,
            'spec'         : True,
            'vertexColors' : True,
            'transparency' : True,
            'ambientOcclusion': True
        }
        self._shaderParameters = {}
        self._shaderDefines = []
        self.shaderChanged = True   # Determines whether shader should be recompiled

        if performConfig:
            self._updateShaderConfig()

        self._uvMap = None

        if isinstance(name, Material):
            # Copy constructor
            self.copyFrom(name)

    def copyFrom(self, material):
        self.name = material.name
        self.description = material.description

        self.filename = material.filename
        self.filepath = material.filepath

        self._ambientColor.copyFrom(material.ambientColor)
        self._diffuseColor.copyFrom(material._diffuseColor)
        self._specularColor.copyFrom(material.specularColor)
        self._shininess = material.shininess
        self._emissiveColor.copyFrom(material.emissiveColor)

        self._opacity = material.opacity
        self._translucency = material.translucency

        self._shadeless = material.shadeless
        self._wireframe = material.wireframe
        self._transparent = material.transparent
        self._backfaceCull = material.backfaceCull
        self._depthless = material.depthless
        self._alphaToCoverage = material.alphaToCoverage
        self._castShadows = material.castShadows
        self._receiveShadows = material.receiveShadows

        self._autoBlendSkin = material.autoBlendSkin

        self._diffuseTexture = material.diffuseTexture
        self._bumpMapTexture = material.bumpMapTexture
        self._bumpMapIntensity = material.bumpMapIntensity
        self._normalMapTexture = material.normalMapTexture
        self._normalMapIntensity = material.normalMapIntensity
        self._displacementMapTexture = material.displacementMapTexture
        self._displacementMapIntensity = material.displacementMapIntensity
        self._specularMapTexture = material.specularMapTexture
        self._specularMapIntensity = material.specularMapIntensity
        self._transparencyMapTexture = material.transparencyMapTexture
        self._transparencyMapIntensity = material.transparencyMapIntensity
        self._aoMapTexture = material.aoMapTexture
        self._aoMapIntensity = material.aoMapIntensity

        self._sssEnabled = material.sssEnabled
        self._sssRScale = material.sssRScale
        self._sssGScale = material.sssGScale
        self._sssBScale = material.sssBScale

        self._shader = material.shader
        self._shaderConfig = dict(material._shaderConfig)
        self._shaderParameters = dict(material._shaderParameters)
        self._shaderDefines = list(material.shaderDefines)
        self.shaderChanged = True

        self._uvMap = material.uvMap

        return self

    def clone(self):
        return type(self)().copyFrom(self)

    def fromFile(self, filename):
        """
        Parse .mhmat file and set as the properties of this material.
        """
        from codecs import open
        log.debug("Loading material from file %s", filename)
        try:
            f = open(filename, "rU", encoding="utf-8")
        except:
            f = None
        if f == None:
            log.error("Failed to load material from file %s.", filename)
            return

        self.filename = os.path.normpath(filename)
        self.filepath = os.path.dirname(self.filename)

        shaderConfig_diffuse = None
        shaderConfig_bump = None
        shaderConfig_normal = None
        shaderConfig_displacement = None
        shaderConfig_spec = None
        shaderConfig_vertexColors = None
        shaderConfig_transparency = None
        shaderConfig_ambientOcclusion = None

        def _readbool(value):
            return value.lower() in ["yes", "enabled", "true"]

        for line in f:
            words = line.split()
            if len(words) == 0:
                continue
            if words[0] in ["#", "//"]:
                continue

            if words[0] == "name":
                self.name = words[1]
            elif words[0] == "tag":
                self.addTag(" ".join(words[1:]))
            elif words[0] == "description":
                self.description = " ".join(words[1:])
            elif words[0] == "ambientColor":
                self._ambientColor.copyFrom([float(w) for w in words[1:4]])
            elif words[0] == "diffuseColor":
                self._diffuseColor.copyFrom([float(w) for w in words[1:4]])
            elif words[0] == "diffuseIntensity":
                log.warning('Deprecated parameter "diffuseIntensity" specified in material %s', self.name)
            elif words[0] == "specularColor":
                self._specularColor.copyFrom([float(w) for w in words[1:4]])
            elif words[0] == "specularIntensity":
                log.warning('Deprecated parameter "specularIntensity" specified in material %s', self.name)
            elif words[0] == "shininess":
                self._shininess = max(0.0, min(1.0, float(words[1])))
            elif words[0] == "emissiveColor":
                self._emissiveColor.copyFrom([float(w) for w in words[1:4]])
            elif words[0] == "opacity":
                self._opacity = max(0.0, min(1.0, float(words[1])))
            elif words[0] == "translucency":
                self._translucency = max(0.0, min(1.0, float(words[1])))
            elif words[0] == "shadeless":
                self._shadeless = _readbool(words[1])
            elif words[0] == "wireframe":
                self._wireframe = _readbool(words[1])
            elif words[0] == "transparent":
                self._transparent = _readbool(words[1])
            elif words[0] == "alphaToCoverage":
                self._alphaToCoverage = _readbool(words[1])
            elif words[0] == "backfaceCull":
                self._backfaceCull = _readbool(words[1])
            elif words[0] == "depthless":
                self._depthless = _readbool(words[1])
            elif words[0] == "castShadows":
                self._castShadows = _readbool(words[1])
            elif words[0] == "receiveShadows":
                self._receiveShadows = _readbool(words[1])
            elif words[0] == "autoBlendSkin":
                self._autoBlendSkin = _readbool(words[1])
            elif words[0] == "diffuseTexture":
                self._diffuseTexture = getFilePath(words[1], self.filepath)
            elif words[0] == "bumpmapTexture":
                self._bumpMapTexture = getFilePath(words[1], self.filepath)
            elif words[0] == "bumpmapIntensity":
                self._bumpMapIntensity = max(0.0, min(1.0, float(words[1])))
            elif words[0] == "normalmapTexture":
                self._normalMapTexture = getFilePath(words[1], self.filepath)
            elif words[0] == "normalmapIntensity":
                self._normalMapIntensity = max(0.0, min(1.0, float(words[1])))
            elif words[0] == "displacementmapTexture":
                self._displacementMapTexture = getFilePath(words[1], self.filepath)
            elif words[0] == "displacementmapIntensity":
                self._displacementMapIntensity = max(0.0, min(1.0, float(words[1])))
            elif words[0] == "specularmapTexture":
                self._specularMapTexture = getFilePath(words[1], self.filepath)
            elif words[0] == "specularmapIntensity":
                self._specularMapIntensity = max(0.0, min(1.0, float(words[1])))
            elif words[0] == "transparencymapTexture":
                self._transparencyMapTexture = getFilePath(words[1], self.filepath)
            elif words[0] == "transparencymapIntensity":
                self._transparencyMapIntensity = max(0.0, min(1.0, float(words[1])))
            elif words[0] == "aomapTexture":
                self._aoMapTexture = getFilePath(words[1], self.filepath)
            elif words[0] == "aomapIntensity":
                self._aoMapIntensity = max(0.0, min(1.0, float(words[1])))
            elif words[0] == "sssEnabled":
                self._sssEnabled = _readbool(words[1])
            elif words[0] == "sssRScale":
                self._sssRScale = max(0.0, float(words[1]))
            elif words[0] == "sssGScale":
                self._sssGScale = max(0.0, float(words[1]))
            elif words[0] == "sssBScale":
                self._sssBScale = max(0.0, float(words[1]))
            elif words[0] == "shader":
                self._shader = getShaderPath(words[1], self.filepath)
            elif words[0] == "uvMap":
                self._uvMap = getFilePath(words[1], self.filepath)
                from getpath import getSysDataPath, canonicalPath
                if self._uvMap and \
                   canonicalPath(self._uvMap) == canonicalPath(getSysDataPath('uvs/default.mhuv')):
                    # uvs/default.mhuv is a meta-file that refers to the default uv set
                    # TODO remove this, use None for setting default UV map
                    self._uvMap = None
            elif words[0] == "shaderParam":
                if len(words) > 3:
                    self.setShaderParameter(words[1], words[2:])
                else:
                    self.setShaderParameter(words[1], words[2])
            elif words[0] == "shaderDefine":
                self.addShaderDefine(words[1])
            elif words[0] == "shaderConfig":
                if words[1] == "diffuse":
                    shaderConfig_diffuse = _readbool(words[2])
                elif words[1] == "bump":
                    shaderConfig_bump = _readbool(words[2])
                elif words[1] == "normal":
                    shaderConfig_normal = _readbool(words[2])
                elif words[1] == "displacement":
                    shaderConfig_displacement = _readbool(words[2])
                elif words[1] == "spec":
                    shaderConfig_spec = _readbool(words[2])
                elif words[1] == "vertexColors":
                    shaderConfig_vertexColors = _readbool(words[2])
                elif words[1] == "transparency":
                    shaderConfig_transparency = _readbool(words[2])
                elif words[1] == "ambientOcclusion":
                    shaderConfig_ambientOcclusion = _readbool(words[2])
                else:
                    log.warning('Unknown material shaderConfig property: %s', words[1])

        f.close()
        self.configureShading(diffuse=shaderConfig_diffuse, bump=shaderConfig_bump, normal=shaderConfig_normal, displacement=shaderConfig_displacement, spec=shaderConfig_spec, vertexColors=shaderConfig_vertexColors, transparency=shaderConfig_transparency, ambientOcclusion=shaderConfig_ambientOcclusion)

    def _texPath(self, filename, materialPath = None):
        """
        Produce a portable path for writing to file.
        """
        def _get_relative(filename, relativeTo):
            from getpath import getJailedPath
            path = getJailedPath(filename, relativeTo)
            if path:
                return path
            else:
                log.warning("Beware! Writing a material with a texture path outside of data folders! Your material will not be portable.")
                from getpath import canonicalPath
                return canonicalPath(filename)

        if materialPath:
            return _get_relative(filename, materialPath)
        elif self.filepath:
            return _get_relative(filename, self.filepath)
        else:
            from getpath import formatPath
            return formatPath(filename)

    def toFile(self, filename, comments = []):
        from codecs import open

        try:
            f = open(filename, 'w', encoding='utf-8')
        except:
            f = None
        if f == None:
            log.error("Failed to open material file %s for writing.", filename)
            return

        f.write('# Material definition for %s\n' % self.name)
        for comment in comments:
            if not (comment.strip().startswith('//') or comment.strip().startswith('#')):
                comment = "# " + comment
            f.write(comment+"\n")
        f.write("\n")

        f.write("name %s\n" % self.name)
        f.write("description %s\n" % self.description)
        f.write("ambientColor %s\n" % self.ambientColor.asStr())
        f.write("diffuseColor %s\n" % self.diffuseColor.asStr())
        f.write("specularColor %s\n" % self.specularColor.asStr())
        f.write("shininess %s\n" % self.shininess)
        f.write("emissiveColor %s\n" % self.emissiveColor.asStr())
        f.write("opacity %s\n" % self.opacity)
        f.write("translucency %s\n\n" % self.translucency)

        f.write("shadeless %s\n" % self.shadeless)
        f.write("wireframe %s\n" % self.wireframe)
        f.write("transparent %s\n" % self.transparent)
        f.write("alphaToCoverage %s\n" % self.alphaToCoverage)
        f.write("backfaceCull %s\n" % self.backfaceCull)
        f.write("depthless %s\n\n" % self.depthless)
        f.write("castShadows %s\n\n" % self.castShadows)
        f.write("receiveShadows %s\n\n" % self.receiveShadows)

        hasTexture = False
        filedir = os.path.dirname(filename)
        if self.diffuseTexture:
            f.write("diffuseTexture %s\n" % self._texPath(self.diffuseTexture, filedir) )
            hasTexture = True
        if self.bumpMapTexture:
            f.write("bumpmapTexture %s\n" % self._texPath(self.bumpMapTexture, filedir) )
            f.write("bumpmapIntensity %s\n" % self.bumpMapIntensity)
            hasTexture = True
        if self.normalMapTexture:
            f.write("normalmapTexture %s\n" % self._texPath(self.normalMapTexture, filedir) )
            f.write("normalmapIntensity %s\n" % self.normalMapIntensity)
            hasTexture = True
        if self.displacementMapTexture:
            f.write("displacementmapTexture %s\n" % self._texPath(self.displacementMapTexture, filedir) )
            f.write("displacementmapIntensity %s\n" % self.displacementMapIntensity)
            hasTexture = True
        if self.specularMapTexture:
            f.write("specularmapTexture %s\n" % self._texPath(self.specularMapTexture, filedir) )
            f.write("specularmapIntensity %s\n" % self.specularMapIntensity)
            hasTexture = True
        if self.transparencyMapTexture:
            f.write("transparencymapTexture %s\n" % self._texPath(self.transparencyMapTexture, filedir) )
            f.write("transparencymapIntensity %s\n" % self.transparencyMapIntensity)
            hasTexture = True
        if self.aoMapTexture:
            f.write("aomapTexture %s\n" % self._texPath(self.aoMapTexture, filedir) )
            f.write("aomapIntensity %s\n" % self.aoMapIntensity)
            hasTexture = True
        if hasTexture: f.write('\n')

        if self.sssEnabled:
            f.write("# Sub-surface scattering parameters\n" )
            f.write("sssEnabled %s\n" % self.sssEnabled )
            f.write("sssRScale %s\n" % self.sssRScale )
            f.write("sssGScale %s\n" % self.sssGScale )
            f.write("sssBScale %s\n\n" % self.sssBScale )

        if self.uvMap:
            f.write("uvMap %s\n\n" % self._texPath(self.uvMap, filedir) )

        if self.shader:
            f.write("shader %s\n\n" % self._texPath(self.shader, filedir))

        hasShaderParam = False
        global _materialShaderParams
        for name, param in self.shaderParameters.items():
            if name not in _materialShaderParams:
                hasShaderParam = True
                import image
                if isinstance(param, image.Image):
                    if hasattr(param, "sourcePath"):
                        f.write("shaderParam %s %s\n" % (name, self._texPath(param.sourcePath, filedir)) )
                elif isinstance(param, list):
                    f.write("shaderParam %s %s\n" % (name, " ".join([str(p) for p in param])) )
                elif isinstance(param, basestring) and not isNumeric(param):
                    # Assume param is a path
                    f.write("shaderParam %s %s\n" % (name, self._texPath(param, filedir)) )
                else:
                    f.write("shaderParam %s %s\n" % (name, param) )
        if hasShaderParam: f.write('\n')

        hasShaderDefine = False
        global _shaderConfigDefines
        for define in self.shaderDefines:
            if define not in _shaderConfigDefines:
                hasShaderDefine = True
                f.write("shaderDefine %s\n" % define)
        if hasShaderDefine: f.write('\n')

        for name, value in self.shaderConfig.items():
            f.write("shaderConfig %s %s\n" % (name, value) )

        f.close()

    def addTag(self, tag):
        self.tags.add(tag.lower())

    def removeTag(self, tag):
        tag = tag.lower()
        if tag in self.tags:
            self.tags.remove(tag)

    def getUVMap(self):
        return self._uvMap

    def setUVMap(self, uvMap):
        self._uvMap = getFilePath(uvMap, self.filepath)
        from getpath import getSysDataPath, canonicalPath
        if self._uvMap and \
           canonicalPath(self._uvMap) == canonicalPath(getSysDataPath('uvs/default.mhuv')):
            # uvs/default.mhuv is a meta-file that refers to the default uv set
            self._uvMap = None

    uvMap = property(getUVMap, setUVMap)

    def getAmbientColor(self):
        return self._ambientColor

    def setAmbientColor(self, color):
        self._ambientColor.copyFrom(color)

    ambientColor = property(getAmbientColor, setAmbientColor)


    def getDiffuseColor(self):
        if self.autoBlendSkin:
            self._diffuseColor = Color(getSkinBlender().getDiffuseColor())
        return self._diffuseColor

    def setDiffuseColor(self, color):
        self._diffuseColor.copyFrom(color)

    diffuseColor = property(getDiffuseColor, setDiffuseColor)


    def getDiffuseIntensity(self):
        """
        Read-only property that represents the greyscale intensity of the
        diffuse color.
        """
        return getIntensity(self.diffuseColor)

    @property
    def diffuseIntensity(self):
        return self.getDiffuseIntensity()


    def getSpecularColor(self):
        return self._specularColor

    def setSpecularColor(self, color):
        self._specularColor.copyFrom(color)

    specularColor = property(getSpecularColor, setSpecularColor)


    def getShininess(self):
        """
        The specular shininess (the inverse of roughness or specular hardness).
        """
        return self._shininess

    def setShininess(self, hardness):
        """
        Sets the specular hardness or shinyness. Between 0 and 1.
        """
        self._shininess = min(1.0, max(0.0, hardness))

    shininess = property(getShininess, setShininess)


    def getSpecularIntensity(self):
        """
        Read-only property that represents the greyscale intensity of the
        specular color.
        """
        return getIntensity(self.specularColor)

    @property
    def specularIntensity(self):
        return self.getSpecularIntensity()


    def getEmissiveColor(self):
        #return self._emissiveColor.values
        return self._emissiveColor

    def setEmissiveColor(self, color):
        self._emissiveColor.copyFrom(color)

    emissiveColor = property(getEmissiveColor, setEmissiveColor)


    def getOpacity(self):
        return self._opacity

    def setOpacity(self, opacity):
        self._opacity = min(1.0, max(0.0, opacity))

    opacity = property(getOpacity, setOpacity)


    def getTranslucency(self):
        return self._translucency

    def setTranslucency(self, translucency):
        self._translucency = min(1.0, max(0.0, translucency))

    translucency = property(getTranslucency, setTranslucency)


    def getShadeless(self):
        return self._shadeless

    def setShadeless(self, shadeless):
        self._shadeless = shadeless

    shadeless = property(getShadeless, setShadeless)

    def getWireframe(self):
        return self._wireframe

    def setWireframe(self, wireframe):
        self._wireframe = wireframe

    wireframe = property(getWireframe, setWireframe)

    def getTransparent(self):
        return self._transparent

    def setTransparent(self, transparent):
        self._transparent = transparent

    transparent = property(getTransparent, setTransparent)

    def getAlphaToCoverage(self):
        return self._alphaToCoverage

    def setAlphaToCoverage(self, a2cEnabled):
        self._alphaToCoverage = a2cEnabled

    alphaToCoverage = property(getAlphaToCoverage, setAlphaToCoverage)

    def getBackfaceCull(self):
        return self._backfaceCull

    def setBackfaceCull(self, backfaceCull):
        self._backfaceCull = backfaceCull

    backfaceCull = property(getBackfaceCull, setBackfaceCull)

    def getDepthless(self):
        return self._depthless

    def setDepthless(self, depthless):
        self._depthless = depthless

    depthless = property(getDepthless, setDepthless)

    def getCastShadows(self):
        return self._castShadows

    def setCastShadows(self, enabled):
        self._castShadows = enabled

    castShadows = property(getCastShadows, setCastShadows)

    def getReceiveShadows(self):
        return self._receiveShadows

    def setReceiveShadows(self, enabled):
        self._receiveShadows = enabled

    receiveShadows = property(getReceiveShadows, setReceiveShadows)

    def getAutoBlendSkin(self):
        return self._autoBlendSkin

    def setAutoBlendSkin(self, autoblend):
        self._autoBlendSkin = autoblend

    autoBlendSkin = property(getAutoBlendSkin, setAutoBlendSkin)

    def getSSSEnabled(self):
        return self._sssEnabled

    def setSSSEnabled(self, sssEnabled):
        self._sssEnabled = sssEnabled

    sssEnabled = property(getSSSEnabled, setSSSEnabled)

    def getSSSRScale(self):
        return self._sssRScale

    def setSSSRScale(self, sssRScale):
        self._sssRScale = sssRScale

    sssRScale = property(getSSSRScale, setSSSRScale)

    def getSSSGScale(self):
        return self._sssGScale

    def setSSSGScale(self, sssGScale):
        self._sssGScale = sssGScale

    sssGScale = property(getSSSGScale, setSSSGScale)

    def getSSSBScale(self):
        return self._sssBScale

    def setSSSBScale(self, sssBScale):
        self._sssBScale = sssBScale

    sssBScale = property(getSSSBScale, setSSSBScale)


    def supportsDiffuse(self):
        result = (self.diffuseTexture != None)
        if self.shaderObj and result:
            # TODO appplies to fixed function shading too...
            return ('DIFFUSE' in self.shaderObj.defineables \
                    or 'diffuseTexture' in self.shaderUniforms)
        else:
            return result

    def supportsBump(self):
        result = (self.bumpMapTexture != None)
        if self.shaderObj and result:
            return ('BUMPMAP' in self.shaderObj.defineables \
                    or 'bumpmapTexture' in self.shaderUniforms)
        else:
            return result

    def supportsDisplacement(self):
        result = (self.displacementMapTexture != None)
        if self.shaderObj and result:
            return ('DISPLACEMENT' in self.shaderObj.defineables \
                    or 'displacementmapTexture' in self.shaderUniforms)
        else:
            return result

    def supportsNormal(self):
        result = (self.normalMapTexture != None)
        if self.shaderObj and result:
            return ('NORMALMAP' in self.shaderObj.defineables \
                    or 'normalmapTexture' in self.shaderUniforms)
        else:
            return result

    def supportsSpecular(self):
        result = (self.specularMapTexture != None)
        if self.shaderObj and result:
            return ('SPECULARMAP' in self.shaderObj.defineables \
                    or 'specularmapTexture' in self.shaderUniforms)
        else:
            return result

    def supportsTransparency(self):
        result = (self.transparencyMapTexture != None)
        if self.shaderObj and result:
            return ('TRANSPARENCYMAP' in self.shaderObj.defineables \
                    or 'transparencymapTexture' in self.shaderUniforms)
        else:
            return result

    def supportsAo(self):
        return self.supportsAmbientOcclusion()

    def supportsAmbientOcclusion(self):
        result = (self.aoMapTexture != None)
        if self.shaderObj and result:
            return ('AOMAP' in self.shaderObj.defineables \
                    or 'aomapTexture' in self.shaderUniforms)
        else:
            return result

    def configureShading(self, diffuse=None, bump = None, normal=None, displacement=None, spec = None, vertexColors = None, transparency=None, ambientOcclusion=None):
        """
        Configure shading options and set the necessary properties based on
        the material configuration of this object. This configuration applies
        for shaders only (depending on whether the selected shader supports the
        chosen options), so only has effect when a shader is set.
        This method can be invoked even when no shader is set, the chosen
        options will remain effective when another shader is set.
        A value of None leaves configuration options unchanged.
        """
        if diffuse != None: self._shaderConfig['diffuse'] = diffuse
        if bump != None: self._shaderConfig['bump'] = bump
        if normal != None: self._shaderConfig['normal'] = normal
        if displacement != None: self._shaderConfig['displacement'] = displacement
        if spec != None: self._shaderConfig['spec'] = spec
        if vertexColors != None: self._shaderConfig['vertexColors'] = vertexColors
        if transparency != None: self._shaderConfig['transparency'] = transparency
        if ambientOcclusion != None: self._shaderConfig['ambientOcclusion'] = ambientOcclusion

        self._updateShaderConfig()

    @property
    def shaderConfig(self):
        """
        The shader parameters as set by configureShading().
        """
        return dict(self._shaderConfig)

    def _updateShaderConfig(self):
        global _shaderConfigDefines
        global _materialShaderParams

        if not self.shader:
            return

        # Remove (non-custom) shader config defines (those set by shader config)
        for shaderDefine in _shaderConfigDefines:
            try:
                self._shaderDefines.remove(shaderDefine)
            except:
                pass

        # Reset (non-custom) shader parameters controlled by material properties
        for shaderParam in _materialShaderParams:
            try:
                del self._shaderParameters[shaderParam]
            except:
                pass

        if self._shaderConfig['vertexColors']:
            #log.debug("Enabling vertex colors.")
            self._shaderDefines.append('VERTEX_COLOR')
        if self._shaderConfig['diffuse'] and self.supportsDiffuse():
            #log.debug("Enabling diffuse texturing.")
            self._shaderDefines.append('DIFFUSE')
            self._shaderParameters['diffuseTexture'] = self.diffuseTexture
        bump = self._shaderConfig['bump'] and self.supportsBump()
        normal = self._shaderConfig['normal'] and self.supportsNormal()
        if bump and not normal:
            #log.debug("Enabling bump mapping.")
            self._shaderDefines.append('BUMPMAP')
            self._shaderParameters['bumpmapTexture'] = self.bumpMapTexture
            self._shaderParameters['bumpmapIntensity'] = self.bumpMapIntensity
        if normal:
            #log.debug("Enabling normal mapping.")
            self._shaderDefines.append('NORMALMAP')
            self._shaderParameters['normalmapTexture'] = self.normalMapTexture
            self._shaderParameters['normalmapIntensity'] = self.normalMapIntensity
        if self._shaderConfig['displacement'] and self.supportsDisplacement():
            #log.debug("Enabling displacement mapping.")
            self._shaderDefines.append('DISPLACEMENT')
            self._shaderParameters['displacementmapTexture'] = self.displacementMapTexture
            self._shaderParameters['displacementmapIntensity'] = self.displacementMapIntensity
        if self._shaderConfig['spec'] and self.supportsSpecular():
            #log.debug("Enabling specular mapping.")
            self._shaderDefines.append('SPECULARMAP')
            self._shaderParameters['specularmapTexture'] = self.specularMapTexture
            self._shaderParameters['specularmapIntensity'] = self._specularMapIntensity
        if self._shaderConfig['transparency'] and self.supportsTransparency():
            self._shaderDefines.append('TRANSPARENCYMAP')
            self._shaderParameters['transparencymapTexture'] = self.transparencyMapTexture
            self._shaderParameters['transparencymapIntensity'] = self.transparencyMapIntensity
        if self._shaderConfig['ambientOcclusion'] and self.supportsAmbientOcclusion():
            self._shaderDefines.append('AOMAP')
            self._shaderParameters['aomapTexture'] = self.aoMapTexture
            self._shaderParameters['aomapIntensity'] = self.aoMapIntensity

        self._shaderDefines.sort()   # This is important for shader caching
        self.shaderChanged = True

    def setShader(self, shader):
        self._shader = getShaderPath(shader, self.filepath)
        self._updateShaderConfig()
        self.shaderChanged = True

    def getShader(self):
        return self._shader

    shader = property(getShader, setShader)

    def getShaderObj(self):
        import sys
        if 'shader' not in sys.modules.keys():
            # Don't import shader module in application if it is not loaded yet
            # Avoid unneeded dependency on OpenGL/shader modules
            return None
        import shader
        if not shader.Shader.supported():
            return None
        shaderPath = self.getShader()
        if not shaderPath:
            return None
        return shader.getShader(shaderPath, self.shaderDefines)

    @property
    def shaderObj(self):
        return self.getShaderObj()

    def getShaderChanged(self):
        return self._shaderChanged

    def setShaderChanged(self, changed=True):
        if changed:
            import time
            self._shaderChanged = time.time()

    shaderChanged = property(getShaderChanged, setShaderChanged)

    @property
    def shaderUniforms(self, includeGLReserved = True):
        shaderObj = self.shaderObj
        if not shaderObj:
            return []
        uniforms = [u.name for u in shaderObj.getUniforms()]
        if includeGLReserved:
            uniforms = uniforms + shaderObj.glUniforms
        return uniforms

    @property
    def shaderParameters(self):
        """
        All shader parameters. Both those set by material properties as well as
        custom shader parameters set by setShaderParameter().
        """
        import numpy as np

        result = dict(self._shaderParameters)
        result['ambient']  = self.ambientColor.values
        result['diffuse'] = self.diffuseColor.values + [self.opacity]
        result['specular'] = self.specularColor.values + [self.shininess]
        result['emissive'] = self.emissiveColor.values

        if self.autoBlendSkin:
            result["litsphereTexture"] = getSkinBlender().getLitsphereTexture()
        return result

    def setShaderParameter(self, name, value):
        """
        Set a custom shader parameter. Shader parameters are uniform parameters
        passed to the shader programme, their type should match that declared in
        the shader code.
        """
        global _materialShaderParams

        if name in _materialShaderParams:
            raise RuntimeError('The shader parameter "%s" is protected and should be set by means of material properties.' % name)

        if isinstance(value, list):
            value = [float(v) for v in value]
        elif isinstance(value, basestring):
            if isNumeric(value):
                value = float(value)
            else:
                # Assume value is a path
                value = getFilePath(value, self.filepath)

        self._shaderParameters[name] = value

    def removeShaderParameter(self, name):
        global _materialShaderParams

        if name in _materialShaderParams:
            raise RuntimeError('The shader parameter "%s" is protected and should be set by means of material properties.' % name)
        try:
            del self._shaderParameters[name]
        except:
            pass

    def clearShaderParameters(self):
        """
        Remove all custom set shader parameters.
        """
        global _materialShaderParams

        for shaderParam in self.shaderParameters:
            if shaderParam not in _materialShaderParams:
                self.removeShaderParameter(shaderParam)


    @property
    def shaderDefines(self):
        """
        All shader defines. Both those set by configureShading() as well as
        custom shader defines set by addShaderDefine().
        """
        return list(self._shaderDefines)

    def addShaderDefine(self, defineStr):
        global _shaderConfigDefines

        if defineStr in _shaderConfigDefines:
            raise RuntimeError('The shader define "%s" is protected and should be set by means of configureShading().' % defineStr)
        if defineStr in self.shaderDefines:
            return
        self._shaderDefines.append(defineStr)
        self._shaderDefines.sort()   # This is important for shader caching

        self.shaderChanged = True

    def removeShaderDefine(self, defineStr):
        global _shaderConfigDefines

        if defineStr in _shaderConfigDefines:
            raise RuntimeError('The shader define %s is protected and should be set by means of configureShading().' % defineStr)
        try:
            self._shaderDefines.remove(defineStr)
        except:
            pass

        self.shaderChanged = True

    def clearShaderDefines(self):
        """
        Remove all custom set shader defines.
        """
        global _shaderConfigDefines

        for shaderDefine in self._shaderDefines:
            if shaderDefine not in _shaderConfigDefines:
                self.removeShaderDefine(shaderDefine)
        self.shaderChanged = True


    def _getTexture(self, texture):
        if isinstance(texture, basestring):
            return getFilePath(texture, self.filepath)
        else:
            return texture

    def getTextureDict(self, includeUniforms=True, includeUnused=False, includeInMemory=True):
        """
        Dict with typename - texturepath pairs that returns all textures set on
        this material which are configured to be used (empty ones are excluded).
        If includeUniforms is True, textures supplied as uniform shader
        properties will be returned too.
        If includeUnused is set to true, all textures set on the material are
        returned, whether they are used for shading or not.
        If includeInMemory is True, the result can contain Image objects, which
        are not stored on disk but reside in memory.
        """
        from collections import OrderedDict
        result = OrderedDict()
        for t in textureTypes:
            tName = t+"Texture"
            if (includeUnused and getattr(self, tName) is not None) or \
               getattr(self, "supports"+t.replace("Map","").capitalize())():  # TODO influenced by shader availability (perhaps a simple != None test is better)
                result[tName] = getattr(self, tName)
        if includeUniforms:
            uniformSamplers = OrderedDict()
            usedByShader = self.shaderUniforms
            for name, param in self.shaderParameters.items():
                if name not in _materialShaderParams and \
                   (includeUnused or name in usedByShader):
                    import image
                    if isinstance(param, image.Image) and includeInMemory:
                        uniformSamplers[name] = param
                    elif isinstance(param, basestring) and not isNumeric(param):
                        # Assume param is a path
                        uniformSamplers[name] = param
            result.update(uniformSamplers)
        return result

    def getDiffuseTexture(self):
        return self._diffuseTexture

    def setDiffuseTexture(self, texture):
        self._diffuseTexture = self._getTexture(texture)
        self._updateShaderConfig()

    diffuseTexture = property(getDiffuseTexture, setDiffuseTexture)


    def getBumpMapTexture(self):
        return self._bumpMapTexture

    def setBumpMapTexture(self, texture):
        self._bumpMapTexture = self._getTexture(texture)
        self._updateShaderConfig()

    bumpMapTexture = property(getBumpMapTexture, setBumpMapTexture)


    def getBumpMapIntensity(self):
        return self._bumpMapIntensity

    def setBumpMapIntensity(self, intensity):
        self._bumpMapIntensity = intensity
        self._updateShaderConfig()

    bumpMapIntensity = property(getBumpMapIntensity, setBumpMapIntensity)


    def getNormalMapTexture(self):
        return self._normalMapTexture

    def setNormalMapTexture(self, texture):
        self._normalMapTexture = self._getTexture(texture)
        self._updateShaderConfig()

    normalMapTexture = property(getNormalMapTexture, setNormalMapTexture)


    def getNormalMapIntensity(self):
        return self._normalMapIntensity

    def setNormalMapIntensity(self, intensity):
        self._normalMapIntensity = intensity
        self._updateShaderConfig()

    normalMapIntensity = property(getNormalMapIntensity, setNormalMapIntensity)


    def getDisplacementMapTexture(self):
        return self._displacementMapTexture

    def setDisplacementMapTexture(self, texture):
        self._displacementMapTexture = self._getTexture(texture)
        self._updateShaderConfig()

    displacementMapTexture = property(getDisplacementMapTexture, setDisplacementMapTexture)


    def getDisplacementMapIntensity(self):
        return self._displacementMapIntensity

    def setDisplacementMapIntensity(self, intensity):
        self._displacementMapIntensity = intensity
        self._updateShaderConfig()

    displacementMapIntensity = property(getDisplacementMapIntensity, setDisplacementMapIntensity)


    def getSpecularMapTexture(self):
        """
        The specular or reflectivity map texture.
        """
        return self._specularMapTexture

    def setSpecularMapTexture(self, texture):
        """
        Set the specular or reflectivity map texture.
        """
        self._specularMapTexture = self._getTexture(texture)
        self._updateShaderConfig()

    specularMapTexture = property(getSpecularMapTexture, setSpecularMapTexture)


    def getSpecularMapIntensity(self):
        return self._specularMapIntensity

    def setSpecularMapIntensity(self, intensity):
        self._specularMapIntensity = intensity
        self._updateShaderConfig()

    specularMapIntensity = property(getSpecularMapIntensity, setSpecularMapIntensity)


    def getTransparencyMapTexture(self):
        """
        The transparency or reflectivity map texture.
        """
        return self._transparencyMapTexture

    def setTransparencyMapTexture(self, texture):
        """
        Set the transparency or reflectivity map texture.
        """
        self._transparencyMapTexture = self._getTexture(texture)
        self._updateShaderConfig()

    transparencyMapTexture = property(getTransparencyMapTexture, setTransparencyMapTexture)


    def getTransparencyMapIntensity(self):
        return self._transparencyMapIntensity

    def setTransparencyMapIntensity(self, intensity):
        self._transparencyMapIntensity = intensity
        self._updateShaderConfig()

    transparencyMapIntensity = property(getTransparencyMapIntensity, setTransparencyMapIntensity)


    def getAOMapTexture(self):
        """
        The Ambient Occlusion map texture.
        """
        return self._aoMapTexture

    def setAOMapTexture(self, texture):
        """
        Set the Ambient Occlusion map texture.
        """
        self._aoMapTexture = self._getTexture(texture)
        self._updateShaderConfig()

    aoMapTexture = property(getAOMapTexture, setAOMapTexture)


    def getAOMapIntensity(self):
        return self._aoMapIntensity

    def setAOMapIntensity(self, intensity):
        self._aoMapIntensity = intensity
        self._updateShaderConfig()

    aoMapIntensity = property(getAOMapIntensity, setAOMapIntensity)


    def exportTextures(self, exportPath, excludeUniforms=False, excludeTextures=[]):
        """
        Export the textures referenced by this material to the specified folder.
        The result of this operation is returned as a dict with the file
        paths of the exported textures.
        """
        from progress import Progress
        import shutil
        if not os.path.exists(exportPath):
            os.makedirs(exportPath)

        textures = self.getTextureDict(not excludeUniforms)
        for t in excludeTextures:
            if t in textures:
                del textures[t]

        progress = Progress(len(textures))
        for tName,tPath in textures.items():
            progress.step("Exporting texture %s", tName)
            import image
            if isinstance(tPath, image.Image):
                if hasattr(tPath, "sourcePath"):
                    newPath = os.path.join(exportPath, os.path.basename(tPath.sourcePath))
                    if os.path.splitext(newPath)[1] != '.png':
                        newPath = newPath + '.png'
                else:
                    # Generate random name
                    import random
                    newPath = 'texture-%s.png' % int(random.random()*100)
                tPath.save(newPath)
                tPath = None
            else:
                newPath = os.path.join(exportPath, os.path.basename(tPath))

            if tPath:
                shutil.copy(tPath, newPath)

            textures[tName] = newPath

        progress(1.0, "Exported all textures of material %s", self.name)

        return textures

def fromFile(filename):
    """
    Create a material from a .mhmat file.
    """
    mat = Material(performConfig=False)
    mat.fromFile(filename)
    return mat

def getSkinBlender():
    global _autoSkinBlender
    if not _autoSkinBlender:
        import autoskinblender
        from core import G
        human = G.app.selectedHuman
        _autoSkinBlender = autoskinblender.EthnicSkinBlender(human)
    return _autoSkinBlender

def getFilePath(filename, folder = None):
    if not filename or not isinstance(filename, basestring):
        return filename

    searchPaths = []

    # Search within current folder
    if folder:
        searchPaths.append(folder)

    import getpath
    return getpath.thoroughFindFile(filename, searchPaths, True)

def getShaderPath(shader, folder = None):
    if not shader:
        return None

    shaderSuffixes = ['_vertex_shader.txt', '_fragment_shader.txt', '_geometry_shader.txt']
    paths = [shader+s for s in shaderSuffixes]
    paths = [p for p in paths if os.path.isfile(getFilePath(p, folder))]
    if len(paths) > 0:
        path = getFilePath(paths[0], folder)
        for s in shaderSuffixes:
            if path.endswith(s):
                path = path[:-len(s)]
    else:
        path = shader
    return path

def isNumeric(string):
    try:
        float(string)
        return True
    except:
        return False

def getIntensity(color):
    return 0.2126 * color[0] + \
           0.7152 * color[1] + \
           0.0722 * color[2]

class UVMap:
    def __init__(self, name):
        self.name = name
        self.type = "UvSet"
        self.filepath = None
        self.materialName = "Default"
        self.uvs = None
        self.fuvs = None


    def read(self, mesh, filepath):
        import numpy as np

        filename,ext = os.path.splitext(filepath)

        uvs,fuvs = loadUvObjFile(filepath)
        self.filepath = filepath
        self.uvs = np.array(uvs)
        self.fuvs = np.array(fuvs)


def loadUvObjFile(filepath):
    from codecs import open
    fp = open(filepath, "rU", encoding="utf-8")
    uvs = []
    fuvs = []
    for line in fp:
        words = line.split()
        if len(words) == 0:
            continue
        elif words[0] == "vt":
            uvs.append((float(words[1]), float(words[2])))
        elif words[0] == "f":
            fuvs.append( [(int(word.split("/")[1]) - 1) for word in words[1:]] )
    fp.close()
    return uvs,fuvs

def peekMetadata(filename):
    from codecs import open
    try:
        f = open(filename, "rU", encoding="utf-8")
    except:
        f = None
    if f == None:
        log.error("Failed to load metadata from material file %s.", filename)
        return

    name = "UnnamedMaterial"
    description = None
    tags = set()

    for line in f:
        words = line.split()
        if len(words) == 0:
            continue
        if words[0] in ["#", "//"]:
            continue

        if words[0] == "name":
            name = words[1]
        elif words[0] == "tag":
            tags.add((" ".join(words[1:])).lower())
        if words[0] == "description":
            description = " ".join(words[1:])
        else:
            pass

    if description is None:
        description = "%s material" % name

    return (name, tags, description)
