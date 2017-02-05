#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

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

import os.path
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.ARB.texture_multisample import *
import texture
import log
from core import G

class Uniform(object):
    def __init__(self, index, name, pytype, dims):
        self.index = index
        self.name = name
        self.pytype = pytype
        self.dims = dims
        self.values = None

    def __call__(self, index, values):
        raise NotImplementedError

    def update(self, pgm):
        pass

class VectorUniform(Uniform):
    uniformTypes = {
        GL_FLOAT:               ((1,),  np.float32,     float,  glUniform1fv,           glGetUniformfv),
        GL_FLOAT_VEC2:          ((2,),  np.float32,     float,  glUniform2fv,           glGetUniformfv),
        GL_FLOAT_VEC3:          ((3,),  np.float32,     float,  glUniform3fv,           glGetUniformfv),
        GL_FLOAT_VEC4:          ((4,),  np.float32,     float,  glUniform4fv,           glGetUniformfv),
        GL_INT:                 ((1,),  np.int32,       int,    glUniform1iv,           glGetUniformiv),
        GL_INT_VEC2:            ((2,),  np.int32,       int,    glUniform2iv,           glGetUniformiv),
        GL_INT_VEC3:            ((3,),  np.int32,       int,    glUniform3iv,           glGetUniformiv),
        GL_INT_VEC4:            ((4,),  np.int32,       int,    glUniform4iv,           glGetUniformiv),
        GL_UNSIGNED_INT:        ((1,),  np.uint32,      int,    glUniform1uiv,          glGetUniformuiv),
        GL_UNSIGNED_INT_VEC2:   ((2,),  np.uint32,      int,    glUniform2uiv,          glGetUniformuiv),
        GL_UNSIGNED_INT_VEC3:   ((3,),  np.uint32,      int,    glUniform3uiv,          glGetUniformuiv),
        GL_UNSIGNED_INT_VEC4:   ((4,),  np.uint32,      int,    glUniform4uiv,          glGetUniformuiv),
        GL_BOOL:                ((1,),  np.int32,       bool,   glUniform1iv,           glGetUniformiv),
        GL_BOOL_VEC2:           ((2,),  np.int32,       bool,   glUniform2iv,           glGetUniformiv),
        GL_BOOL_VEC3:           ((3,),  np.int32,       bool,   glUniform3iv,           glGetUniformiv),
        GL_BOOL_VEC4:           ((4,),  np.int32,       bool,   glUniform4iv,           glGetUniformiv),
        GL_FLOAT_MAT2:          ((2,2), np.float32,     float,  glUniformMatrix2fv,     glGetUniformfv),
        GL_FLOAT_MAT2x3:        ((2,3), np.float32,     float,  glUniformMatrix2x3fv,   glGetUniformfv),
        GL_FLOAT_MAT2x4:        ((2,4), np.float32,     float,  glUniformMatrix2x4fv,   glGetUniformfv),
        GL_FLOAT_MAT3x2:        ((3,2), np.float32,     float,  glUniformMatrix3x2fv,   glGetUniformfv),
        GL_FLOAT_MAT3:          ((3,3), np.float32,     float,  glUniformMatrix3fv,     glGetUniformfv),
        GL_FLOAT_MAT3x4:        ((3,4), np.float32,     float,  glUniformMatrix3x4fv,   glGetUniformfv),
        GL_FLOAT_MAT4x2:        ((4,2), np.float32,     float,  glUniformMatrix4x2fv,   glGetUniformfv),
        GL_FLOAT_MAT4x3:        ((4,3), np.float32,     float,  glUniformMatrix4x3fv,   glGetUniformfv),
        GL_FLOAT_MAT4:          ((4,4), np.float32,     float,  glUniformMatrix4fv,     glGetUniformfv),
        }

    if 'glUniform1dv' in globals():
        uniformTypes2 = {
            GL_DOUBLE:              ((1,),  np.float64,     float,  glUniform1dv,           glGetUniformdv),
            GL_DOUBLE_VEC2:         ((2,),  np.float64,     float,  glUniform2dv,           glGetUniformdv),
            GL_DOUBLE_VEC3:         ((3,),  np.float64,     float,  glUniform3dv,           glGetUniformdv),
            GL_DOUBLE_VEC4:         ((4,),  np.float64,     float,  glUniform4dv,           glGetUniformdv),
            GL_DOUBLE_MAT2:         ((2,2), np.float64,     float,  glUniformMatrix2dv,     glGetUniformdv),
            GL_DOUBLE_MAT2x3:       ((2,3), np.float64,     float,  glUniformMatrix2x3dv,   glGetUniformdv),
            GL_DOUBLE_MAT2x4:       ((2,4), np.float64,     float,  glUniformMatrix2x4dv,   glGetUniformdv),
            GL_DOUBLE_MAT3x2:       ((3,2), np.float64,     float,  glUniformMatrix3x2dv,   glGetUniformdv),
            GL_DOUBLE_MAT3:         ((3,3), np.float64,     float,  glUniformMatrix3dv,     glGetUniformdv),
            GL_DOUBLE_MAT3x4:       ((3,4), np.float64,     float,  glUniformMatrix3x4dv,   glGetUniformdv),
            GL_DOUBLE_MAT4x2:       ((4,2), np.float64,     float,  glUniformMatrix4x2dv,   glGetUniformdv),
            GL_DOUBLE_MAT4x3:       ((4,3), np.float64,     float,  glUniformMatrix4x3dv,   glGetUniformdv),
            GL_DOUBLE_MAT4:         ((4,4), np.float64,     float,  glUniformMatrix4dv,     glGetUniformdv),
            }

    @classmethod
    def check(cls, type):
        if hasattr(cls, 'uniformTypes2') and cls.uniformTypes2:
            cls.uniformTypes.update(cls.uniformTypes2)
            cls.uniformTypes2.clear()
        return type in cls.uniformTypes

    def __init__(self, index, name, type):
        dims, dtype, pytype, glfunc, glquery = self.uniformTypes[type]
        super(VectorUniform, self).__init__(index, name, pytype, dims)
        self.type = type
        self.dtype = dtype
        self.glfunc = glfunc
        self.glquery = glquery

    def set(self, data):
        if data is None:
            self.set(self.values)
            return
        values = np.asarray(data, dtype=self.dtype).reshape(self.dims)
        if len(self.dims) > 1:
            self.glfunc(self.index, 1, GL_TRUE, values)
        else:
            self.glfunc(self.index, len(values)/self.dims[0], values)

    def update(self, pgm):
        values = np.zeros(self.dims, dtype=self.dtype)
        self.glquery(pgm, self.index, values)
        if len(self.dims) > 1:
            values = values.T
        self.values = values
        log.debug('VectorUniform(%s) = %s', self.name, self.values)
        return self.values

class SamplerUniform(Uniform):

    textureTargets = {
        GL_SAMPLER_1D:                                  GL_TEXTURE_1D,
        GL_SAMPLER_2D:                                  GL_TEXTURE_2D,
        GL_SAMPLER_3D:                                  GL_TEXTURE_3D,
        GL_SAMPLER_CUBE:                                GL_TEXTURE_CUBE_MAP,
        GL_SAMPLER_1D_SHADOW:                           GL_TEXTURE_1D,
        GL_SAMPLER_2D_SHADOW:                           GL_TEXTURE_2D,
        GL_SAMPLER_1D_ARRAY:                            GL_TEXTURE_1D_ARRAY,
        GL_SAMPLER_2D_ARRAY:                            GL_TEXTURE_2D_ARRAY,
        GL_SAMPLER_1D_ARRAY_SHADOW:                     GL_TEXTURE_1D_ARRAY,
        GL_SAMPLER_2D_ARRAY_SHADOW:                     GL_TEXTURE_2D_ARRAY,
        GL_SAMPLER_2D_MULTISAMPLE:                      GL_TEXTURE_2D_MULTISAMPLE,
        GL_SAMPLER_2D_MULTISAMPLE_ARRAY:                GL_TEXTURE_2D_MULTISAMPLE_ARRAY,
        GL_SAMPLER_CUBE_SHADOW:                         GL_TEXTURE_CUBE_MAP,
        GL_SAMPLER_BUFFER:                              GL_TEXTURE_BUFFER,
        GL_SAMPLER_2D_RECT:                             GL_TEXTURE_RECTANGLE,
        GL_SAMPLER_2D_RECT_SHADOW:                      GL_TEXTURE_RECTANGLE,
        GL_INT_SAMPLER_1D:                              GL_TEXTURE_1D,
        GL_INT_SAMPLER_2D:                              GL_TEXTURE_2D,
        GL_INT_SAMPLER_3D:                              GL_TEXTURE_3D,
        GL_INT_SAMPLER_CUBE:                            GL_TEXTURE_CUBE_MAP,
        GL_INT_SAMPLER_1D_ARRAY:                        GL_TEXTURE_1D_ARRAY,
        GL_INT_SAMPLER_2D_ARRAY:                        GL_TEXTURE_2D_ARRAY,
        GL_INT_SAMPLER_2D_MULTISAMPLE:                  GL_TEXTURE_2D_MULTISAMPLE,
        GL_INT_SAMPLER_2D_MULTISAMPLE_ARRAY:            GL_TEXTURE_2D_MULTISAMPLE_ARRAY,
        GL_INT_SAMPLER_BUFFER:                          GL_TEXTURE_BUFFER,
        GL_INT_SAMPLER_2D_RECT:                         GL_TEXTURE_RECTANGLE,
        GL_UNSIGNED_INT_SAMPLER_1D:                     GL_TEXTURE_1D,
        GL_UNSIGNED_INT_SAMPLER_2D:                     GL_TEXTURE_2D,
        GL_UNSIGNED_INT_SAMPLER_3D:                     GL_TEXTURE_3D,
        GL_UNSIGNED_INT_SAMPLER_CUBE:                   GL_TEXTURE_CUBE_MAP,
        GL_UNSIGNED_INT_SAMPLER_1D_ARRAY:               GL_TEXTURE_1D_ARRAY,
        GL_UNSIGNED_INT_SAMPLER_2D_ARRAY:               GL_TEXTURE_2D_ARRAY,
        GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE:         GL_TEXTURE_2D_MULTISAMPLE,
        GL_UNSIGNED_INT_SAMPLER_2D_MULTISAMPLE_ARRAY:   GL_TEXTURE_2D_MULTISAMPLE_ARRAY,
        GL_UNSIGNED_INT_SAMPLER_BUFFER:                 GL_TEXTURE_BUFFER,
        GL_UNSIGNED_INT_SAMPLER_2D_RECT:                GL_TEXTURE_RECTANGLE,
        }

    if 'GL_IMAGE_1D' in globals():    
        try:
            textureTargets2 = {
                GL_IMAGE_1D:                                    GL_TEXTURE_1D,
                GL_IMAGE_2D:                                    GL_TEXTURE_2D,
                GL_IMAGE_3D:                                    GL_TEXTURE_3D,
                GL_IMAGE_2D_RECT:                               GL_TEXTURE_2D_RECTANGLE,
                GL_IMAGE_CUBE:                                  GL_TEXTURE_CUBE_MAP,
                GL_IMAGE_BUFFER:                                GL_TEXTURE_BUFFER,
                GL_IMAGE_1D_ARRAY:                              GL_TEXTURE_1D_ARRAY,
                GL_IMAGE_2D_ARRAY:                              GL_TEXTURE_2D_ARRAY,
                GL_IMAGE_2D_MULTISAMPLE:                        GL_TEXTURE_2D_MULTISAMPLE,
                GL_IMAGE_2D_MULTISAMPLE_ARRAY:                  GL_TEXTURE_2D_MULTISAMPLE_ARRAY,
                GL_INT_IMAGE_1D:                                GL_TEXTURE_1D,
                GL_INT_IMAGE_2D:                                GL_TEXTURE_2D,
                GL_INT_IMAGE_3D:                                GL_TEXTURE_3D,
                GL_INT_IMAGE_2D_RECT:                           GL_TEXTURE_2D_RECTANGLE,
                GL_INT_IMAGE_CUBE:                              GL_TEXTURE_CUBE_MAP,
                GL_INT_IMAGE_BUFFER:                            GL_TEXTURE_BUFFER,
                GL_INT_IMAGE_1D_ARRAY:                          GL_TEXTURE_1D_ARRAY,
                GL_INT_IMAGE_2D_ARRAY:                          GL_TEXTURE_2D_ARRAY,
                GL_INT_IMAGE_2D_MULTISAMPLE:                    GL_TEXTURE_2D_MULTISAMPLE,
                GL_INT_IMAGE_2D_MULTISAMPLE_ARRAY:              GL_TEXTURE_2D_MULTISAMPLE_ARRAY,
                GL_UNSIGNED_INT_IMAGE_1D:                       GL_TEXTURE_1D,
                GL_UNSIGNED_INT_IMAGE_2D:                       GL_TEXTURE_2D,
                GL_UNSIGNED_INT_IMAGE_3D:                       GL_TEXTURE_3D,
                GL_UNSIGNED_INT_IMAGE_2D_RECT:                  GL_TEXTURE_2D_RECTANGLE,
                GL_UNSIGNED_INT_IMAGE_CUBE:                     GL_TEXTURE_CUBE_MAP,
                GL_UNSIGNED_INT_IMAGE_BUFFER:                   GL_TEXTURE_BUFFER,
                GL_UNSIGNED_INT_IMAGE_1D_ARRAY:                 GL_TEXTURE_1D_ARRAY,
                GL_UNSIGNED_INT_IMAGE_2D_ARRAY:                 GL_TEXTURE_2D_ARRAY,
                GL_UNSIGNED_INT_IMAGE_2D_MULTISAMPLE:           GL_TEXTURE_2D_MULTISAMPLE,
                GL_UNSIGNED_INT_IMAGE_2D_MULTISAMPLE_ARRAY:     GL_TEXTURE_2D_MULTISAMPLE_ARRAY,
                }
        except:
            pass

    @classmethod
    def check(cls, type):
        if hasattr(cls, 'textureTargets2') and cls.textureTargets2:
            cls.textureTargets.update(cls.textureTargets2)
            cls.textureTargets2.clear()
        return type in cls.textureTargets

    def __init__(self, index, name, type):
        target = self.textureTargets[type]
        super(SamplerUniform, self).__init__(index, name, str, (1,))
        self.target = target

    def set(self, data):
        cls = type(self)
        glActiveTexture(GL_TEXTURE0 + cls.currentSampler)
        if data is not None:
            tex = texture.getTexture(data)
        else:
            tex = None
        if tex not in (False, None):
            glBindTexture(self.target, tex.textureId)
        else:
            tex = texture.getTexture(texture.NOTFOUND_TEXTURE)
            if tex in (None, False):
                glBindTexture(self.target, 0)
            else:
                glBindTexture(self.target, tex.textureId)
        glUniform1i(self.index, cls.currentSampler)
        cls.currentSampler += 1

    @classmethod
    def reset(cls):
        cls.currentSampler = 0

class Shader(object):
    _supported = None
    if G.args.get('noshaders', False):
        _supported = False

    _glsl_version_str = None
    _glsl_version = None

    @classmethod
    def supported(cls):
        if cls._supported is None:
            cls._supported = bool(glCreateProgram)
        return cls._supported

    @classmethod
    def glslVersionStr(cls):
        cls.glslVersion()
        return cls._glsl_version_str

    @classmethod
    def glslVersion(cls):
        if cls._glsl_version is None:
            if not cls.supported():
                cls._glsl_version = (0,0)
                cls._glsl_version_str = "NOT SUPPORTED!"
                return cls._glsl_version

            cls._glsl_version_str = OpenGL.GL.glGetString(OpenGL.GL.GL_SHADING_LANGUAGE_VERSION)
            if cls._glsl_version_str:
                import re
                glsl_version = re.search('[0-9]+\.[0-9]+', cls._glsl_version_str).group(0)
                glsl_v_major, glsl_v_minor = glsl_version.split('.')
            else:
                glsl_v_major, glsl_v_minor = (0, 0)
            cls._glsl_version = (int(glsl_v_major), int(glsl_v_minor))
        return cls._glsl_version

    def __init__(self, path, defines = []):
        if not self.supported():
            raise RuntimeError("No shader support detected")

        super(Shader, self).__init__()

        self.path = path

        self.vertexId = None
        self.fragmentId = None
        self.shaderId = None
        self.modified = None
        self.uniforms = None
        self.defines = defines
        self.vertexTangentAttrId = None

        self.initShader()

    def __del__(self):
        try:
            self.delete()
        except StandardError:
            pass

    @staticmethod
    def createShader(file, type, defines = [], defineables = None):
        with open(file, 'rU') as f:
            source = f.read()
        if "#version" not in source:
            log.warning("The shader source in %s does not contain an explicit GLSL version declaration. This could cause problems with some compilers.", file)

        if defineables != None:
            for d in Shader._getDefineables(source):
                if d not in defineables:
                    defineables.append(d)
        if defines:
            # Add #define instructions for shader preprocessor to enable extra
            # shader features at compile time
            firstComments, code = Shader._splitVersionDeclaration(source)
            defineLines = "\n".join([ "#define " + define for define in defines])
            source = "\n".join([firstComments, defineLines, code])
        shader = glCreateShader(type)
        glShaderSource(shader, source)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            logmsg = glGetShaderInfoLog(shader)
            log.error("Error compiling shader: %s", logmsg)
            return None
        return shader

    @staticmethod
    def _getDefineables(sourceStr):
        """
        Note: currently only supports #ifdef and #ifndef preprocessor statements
        The syntax #if defined DEFINEABLE is not supported
        """
        lines = sourceStr.split("\n")
        result = []
        for l in lines:
            l = l.strip()
            if not l:
                continue
            l = l.split()
            if len(l) < 2:
                continue
            if l[0] in ['#ifdef', '#ifndef']:
                result.append(l[1])
        return result

    @staticmethod
    def _splitVersionDeclaration(sourceStr):
        """
        Split source string in part that contains the #version declaration,
        that should occur before any instructions (only comments can preceed),
        and the rest of the shader code.
        Define statements can be inserted between the two split strings.
        This is to ensure that any #version statements remain the first
        instruction in the shader source, conform with the GLSL spec.
        If no #version statement is found, the full source will be in the second
        string, allowing #define statements to be inserted at the top of the 
        source.
        NOTE: For this to work correctly, #version effectively needs to be the
        first instruction in the shader source, but this is usually enforced by
        the GLSL compiler anyway.
        Returns a tuple of two strings.
        """
        if "#version" in sourceStr:
            lines = sourceStr.split("\n")
            for lIdx,line in enumerate(lines):
                # Determine line where #version occurs
                if line.strip().startswith("#version"):
                    return "\n".join(lines[:lIdx+1]), "\n".join(lines[lIdx+1:])
        # Else don't split source
        return "", sourceStr

    def delete(self):
        if self.vertexId:
            glDeleteShader(self.vertexId)
            self.vertexId = None
        if self.fragmentId:
            glDeleteShader(self.fragmentId)
            self.fragmentId = None
        if self.shaderId:
            glDeleteProgram(self.shaderId)
            self.shaderId = None

    def initShader(self):
        vertexSource = self.path + '_vertex_shader.txt'
        geometrySource = self.path + '_geometry_shader.txt'
        fragmentSource = self.path + '_fragment_shader.txt'

        self.shaderId = glCreateProgram()

        self.defineables = []

        if os.path.isfile(vertexSource):
            self.vertexId = self.createShader(vertexSource, GL_VERTEX_SHADER, self.defines, self.defineables)
            if self.vertexId == None:
                raise RuntimeError("No vertex shader program compiled, cannot set vertex shader. (%s)" % vertexSource)
            glAttachShader(self.shaderId, self.vertexId)

        if os.path.isfile(geometrySource) and 'GL_GEOMETRY_SHADER' in globals():
            self.geometryId = self.createShader(geometrySource, GL_GEOMETRY_SHADER, self.defines, self.defineables)
            if self.geometryId == None:
                raise RuntimeError("No geometry shader program compiled, cannot set geometry shader. (%s)" % geometrySource)
            glAttachShader(self.shaderId, self.geometryId)

        if os.path.isfile(fragmentSource):
            self.fragmentId = self.createShader(fragmentSource, GL_FRAGMENT_SHADER, self.defines, self.defineables)
            if self.fragmentId == None:
                raise RuntimeError("No fragment shader program compiled, cannot set fragment shader. (%s)" % fragmentSource)
            glAttachShader(self.shaderId, self.fragmentId)

        glLinkProgram(self.shaderId)
        if not glGetProgramiv(self.shaderId, GL_LINK_STATUS):
            log.error("Error linking shader: %s", glGetProgramInfoLog(self.shaderId))
            self.delete()
            return

        self.vertexTangentAttrId = glGetAttribLocation(self.shaderId, 'tangent')

        self.uniforms = None
        self.glUniforms = []
        self.updateUniforms()

    def getUniforms(self):
        if self.uniforms is None:
            parameterCount = glGetProgramiv(self.shaderId, GL_ACTIVE_UNIFORMS)
            self.uniforms = []
            for index in xrange(parameterCount):
                name, size, type = glGetActiveUniform(self.shaderId, index)
                if name.startswith('gl_'):
                    log.debug("Shader: adding built-in uniform %s", name)
                    self.glUniforms.append(name)
                    continue
                if VectorUniform.check(type):
                    uniform = VectorUniform(index, name, type)
                elif SamplerUniform.check(type):
                    uniform = SamplerUniform(index, name, type)
                uniform.update(self.shaderId)
                self.uniforms.append(uniform)

        return self.uniforms

    def updateUniforms(self):
        for uniform in self.getUniforms():
            uniform.update(self.shaderId)

    def setUniforms(self, params):
        import glmodule
        SamplerUniform.reset()

        for uniform in self.getUniforms():
            value = params.get(uniform.name)
            uniform.set(value)

        # Disable other texture units
        for gl_tex_idx in xrange(GL_TEXTURE0 + SamplerUniform.currentSampler, 
                                 GL_TEXTURE0 + glmodule.MAX_TEXTURE_UNITS):
            glActiveTexture(gl_tex_idx)
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_1D, 0)
            glDisable(GL_TEXTURE_1D)

    def requiresVertexTangent(self):
        return self.vertexTangentAttrId != -1

_shaderCache = {}

def getShader(path, defines=[], cache=None):
    shader = None
    cache = cache or _shaderCache

    path1 = path + '_vertex_shader.txt'
    path2 = path + '_fragment_shader.txt'
    path3 = path + '_geometry_shader.txt'
    paths = [p for p in [path1, path2, path3] if os.path.isfile(p)]
    if not paths:
        log.error('No shader file found at path %s. Shader not loaded.', path)
        cache[path] = False
        return False

    mtime = max(os.path.getmtime(p) for p in paths)

    cacheName = path
    if defines:
        # It's important that the defines are sorted alfpabetically here
        cacheName = cacheName + "@" + "|".join(defines)

    if cacheName in cache:
        shader = cache[cacheName]
        if shader is False:
            return shader

        if mtime > shader.modified:
            log.message('reloading %s', cacheName)
            try:
                shader.initShader()
                shader.modified = mtime
            except RuntimeError, _:
                log.error("Error loading shader %s", cacheName, exc_info=True)
                shader = False
    else:
        try:
            shader = Shader(path, defines)
            shader.modified = mtime
        except RuntimeError, _:
            log.error("Error loading shader %s", path, exc_info=True)
            shader = False

    cache[cacheName] = shader
    return shader
    
def reloadShaders():
    log.message('Reloading shaders')
    for path in _shaderCache:
        if _shaderCache[path]:
            try:
                _shaderCache[path].initShader()
            except RuntimeError, _:
                log.error("Error loading shader %s", path, exc_info=True)
                _shaderCache[path] = False
        else:
            del _shaderCache[path]
