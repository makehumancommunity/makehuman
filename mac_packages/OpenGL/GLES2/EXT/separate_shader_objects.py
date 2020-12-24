'''OpenGL extension EXT.separate_shader_objects

This module customises the behaviour of the 
OpenGL.raw.GLES2.EXT.separate_shader_objects to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/separate_shader_objects.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES2 import _types, _glgets
from OpenGL.raw.GLES2.EXT.separate_shader_objects import *
from OpenGL.raw.GLES2.EXT.separate_shader_objects import _EXTENSION_NAME

def glInitSeparateShaderObjectsEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glCreateShaderProgramvEXT.strings size not checked against count
glCreateShaderProgramvEXT=wrapper.wrapper(glCreateShaderProgramvEXT).setInputArraySize(
    'strings', None
)
# INPUT glDeleteProgramPipelinesEXT.pipelines size not checked against n
glDeleteProgramPipelinesEXT=wrapper.wrapper(glDeleteProgramPipelinesEXT).setInputArraySize(
    'pipelines', None
)
# INPUT glGenProgramPipelinesEXT.pipelines size not checked against n
glGenProgramPipelinesEXT=wrapper.wrapper(glGenProgramPipelinesEXT).setInputArraySize(
    'pipelines', None
)
# INPUT glGetProgramPipelineInfoLogEXT.infoLog size not checked against bufSize
glGetProgramPipelineInfoLogEXT=wrapper.wrapper(glGetProgramPipelineInfoLogEXT).setInputArraySize(
    'infoLog', None
).setInputArraySize(
    'length', 1
)
# INPUT glProgramUniform1fvEXT.value size not checked against count
glProgramUniform1fvEXT=wrapper.wrapper(glProgramUniform1fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform1ivEXT.value size not checked against count
glProgramUniform1ivEXT=wrapper.wrapper(glProgramUniform1ivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2fvEXT.value size not checked against count*2
glProgramUniform2fvEXT=wrapper.wrapper(glProgramUniform2fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2ivEXT.value size not checked against count*2
glProgramUniform2ivEXT=wrapper.wrapper(glProgramUniform2ivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3fvEXT.value size not checked against count*3
glProgramUniform3fvEXT=wrapper.wrapper(glProgramUniform3fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3ivEXT.value size not checked against count*3
glProgramUniform3ivEXT=wrapper.wrapper(glProgramUniform3ivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4fvEXT.value size not checked against count*4
glProgramUniform4fvEXT=wrapper.wrapper(glProgramUniform4fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4ivEXT.value size not checked against count*4
glProgramUniform4ivEXT=wrapper.wrapper(glProgramUniform4ivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2fvEXT.value size not checked against count*4
glProgramUniformMatrix2fvEXT=wrapper.wrapper(glProgramUniformMatrix2fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3fvEXT.value size not checked against count*9
glProgramUniformMatrix3fvEXT=wrapper.wrapper(glProgramUniformMatrix3fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4fvEXT.value size not checked against count*16
glProgramUniformMatrix4fvEXT=wrapper.wrapper(glProgramUniformMatrix4fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform1uivEXT.value size not checked against count
glProgramUniform1uivEXT=wrapper.wrapper(glProgramUniform1uivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2uivEXT.value size not checked against count*2
glProgramUniform2uivEXT=wrapper.wrapper(glProgramUniform2uivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3uivEXT.value size not checked against count*3
glProgramUniform3uivEXT=wrapper.wrapper(glProgramUniform3uivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4uivEXT.value size not checked against count*4
glProgramUniform4uivEXT=wrapper.wrapper(glProgramUniform4uivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4fvEXT.value size not checked against count*16
glProgramUniformMatrix4fvEXT=wrapper.wrapper(glProgramUniformMatrix4fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x3fvEXT.value size not checked against count*6
glProgramUniformMatrix2x3fvEXT=wrapper.wrapper(glProgramUniformMatrix2x3fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x2fvEXT.value size not checked against count*6
glProgramUniformMatrix3x2fvEXT=wrapper.wrapper(glProgramUniformMatrix3x2fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x4fvEXT.value size not checked against count*8
glProgramUniformMatrix2x4fvEXT=wrapper.wrapper(glProgramUniformMatrix2x4fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x2fvEXT.value size not checked against count*8
glProgramUniformMatrix4x2fvEXT=wrapper.wrapper(glProgramUniformMatrix4x2fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x4fvEXT.value size not checked against count*12
glProgramUniformMatrix3x4fvEXT=wrapper.wrapper(glProgramUniformMatrix3x4fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x3fvEXT.value size not checked against count*12
glProgramUniformMatrix4x3fvEXT=wrapper.wrapper(glProgramUniformMatrix4x3fvEXT).setInputArraySize(
    'value', None
)
### END AUTOGENERATED SECTION