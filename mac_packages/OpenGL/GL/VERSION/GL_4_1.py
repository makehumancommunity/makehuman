'''OpenGL extension VERSION.GL_4_1

This module customises the behaviour of the 
OpenGL.raw.GL.VERSION.GL_4_1 to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/VERSION/GL_4_1.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.VERSION.GL_4_1 import *
from OpenGL.raw.GL.VERSION.GL_4_1 import _EXTENSION_NAME

def glInitGl41VERSION():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glShaderBinary.binary size not checked against length
# INPUT glShaderBinary.shaders size not checked against count
glShaderBinary=wrapper.wrapper(glShaderBinary).setInputArraySize(
    'binary', None
).setInputArraySize(
    'shaders', None
)
glGetShaderPrecisionFormat=wrapper.wrapper(glGetShaderPrecisionFormat).setOutput(
    'precision',size=(1,),orPassIn=True
).setOutput(
    'range',size=(2,),orPassIn=True
)
glGetProgramBinary=wrapper.wrapper(glGetProgramBinary).setOutput(
    'binary',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'binaryFormat',size=(1,),orPassIn=True
).setOutput(
    'length',size=(1,),orPassIn=True
)
# INPUT glProgramBinary.binary size not checked against length
glProgramBinary=wrapper.wrapper(glProgramBinary).setInputArraySize(
    'binary', None
)
# INPUT glCreateShaderProgramv.strings size not checked against count
glCreateShaderProgramv=wrapper.wrapper(glCreateShaderProgramv).setInputArraySize(
    'strings', None
)
# INPUT glDeleteProgramPipelines.pipelines size not checked against n
glDeleteProgramPipelines=wrapper.wrapper(glDeleteProgramPipelines).setInputArraySize(
    'pipelines', None
)
glGenProgramPipelines=wrapper.wrapper(glGenProgramPipelines).setOutput(
    'pipelines',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGetProgramPipelineiv=wrapper.wrapper(glGetProgramPipelineiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glProgramUniform1iv.value size not checked against count
glProgramUniform1iv=wrapper.wrapper(glProgramUniform1iv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform1fv.value size not checked against count
glProgramUniform1fv=wrapper.wrapper(glProgramUniform1fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform1dv.value size not checked against count
glProgramUniform1dv=wrapper.wrapper(glProgramUniform1dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform1uiv.value size not checked against count
glProgramUniform1uiv=wrapper.wrapper(glProgramUniform1uiv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2iv.value size not checked against count*2
glProgramUniform2iv=wrapper.wrapper(glProgramUniform2iv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2fv.value size not checked against count*2
glProgramUniform2fv=wrapper.wrapper(glProgramUniform2fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2dv.value size not checked against count*2
glProgramUniform2dv=wrapper.wrapper(glProgramUniform2dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2uiv.value size not checked against count*2
glProgramUniform2uiv=wrapper.wrapper(glProgramUniform2uiv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3iv.value size not checked against count*3
glProgramUniform3iv=wrapper.wrapper(glProgramUniform3iv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3fv.value size not checked against count*3
glProgramUniform3fv=wrapper.wrapper(glProgramUniform3fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3dv.value size not checked against count*3
glProgramUniform3dv=wrapper.wrapper(glProgramUniform3dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3uiv.value size not checked against count*3
glProgramUniform3uiv=wrapper.wrapper(glProgramUniform3uiv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4iv.value size not checked against count*4
glProgramUniform4iv=wrapper.wrapper(glProgramUniform4iv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4fv.value size not checked against count*4
glProgramUniform4fv=wrapper.wrapper(glProgramUniform4fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4dv.value size not checked against count*4
glProgramUniform4dv=wrapper.wrapper(glProgramUniform4dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4uiv.value size not checked against count*4
glProgramUniform4uiv=wrapper.wrapper(glProgramUniform4uiv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2fv.value size not checked against count*4
glProgramUniformMatrix2fv=wrapper.wrapper(glProgramUniformMatrix2fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3fv.value size not checked against count*9
glProgramUniformMatrix3fv=wrapper.wrapper(glProgramUniformMatrix3fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4fv.value size not checked against count*16
glProgramUniformMatrix4fv=wrapper.wrapper(glProgramUniformMatrix4fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2dv.value size not checked against count*4
glProgramUniformMatrix2dv=wrapper.wrapper(glProgramUniformMatrix2dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3dv.value size not checked against count*9
glProgramUniformMatrix3dv=wrapper.wrapper(glProgramUniformMatrix3dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4dv.value size not checked against count*16
glProgramUniformMatrix4dv=wrapper.wrapper(glProgramUniformMatrix4dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x3fv.value size not checked against count*6
glProgramUniformMatrix2x3fv=wrapper.wrapper(glProgramUniformMatrix2x3fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x2fv.value size not checked against count*6
glProgramUniformMatrix3x2fv=wrapper.wrapper(glProgramUniformMatrix3x2fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x4fv.value size not checked against count*8
glProgramUniformMatrix2x4fv=wrapper.wrapper(glProgramUniformMatrix2x4fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x2fv.value size not checked against count*8
glProgramUniformMatrix4x2fv=wrapper.wrapper(glProgramUniformMatrix4x2fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x4fv.value size not checked against count*12
glProgramUniformMatrix3x4fv=wrapper.wrapper(glProgramUniformMatrix3x4fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x3fv.value size not checked against count*12
glProgramUniformMatrix4x3fv=wrapper.wrapper(glProgramUniformMatrix4x3fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x3dv.value size not checked against count*6
glProgramUniformMatrix2x3dv=wrapper.wrapper(glProgramUniformMatrix2x3dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x2dv.value size not checked against count*6
glProgramUniformMatrix3x2dv=wrapper.wrapper(glProgramUniformMatrix3x2dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x4dv.value size not checked against count*8
glProgramUniformMatrix2x4dv=wrapper.wrapper(glProgramUniformMatrix2x4dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x2dv.value size not checked against count*8
glProgramUniformMatrix4x2dv=wrapper.wrapper(glProgramUniformMatrix4x2dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x4dv.value size not checked against count*12
glProgramUniformMatrix3x4dv=wrapper.wrapper(glProgramUniformMatrix3x4dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x3dv.value size not checked against count*12
glProgramUniformMatrix4x3dv=wrapper.wrapper(glProgramUniformMatrix4x3dv).setInputArraySize(
    'value', None
)
glGetProgramPipelineInfoLog=wrapper.wrapper(glGetProgramPipelineInfoLog).setOutput(
    'infoLog',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'length',size=(1,),orPassIn=True
)
glVertexAttribL1dv=wrapper.wrapper(glVertexAttribL1dv).setInputArraySize(
    'v', 1
)
glVertexAttribL2dv=wrapper.wrapper(glVertexAttribL2dv).setInputArraySize(
    'v', 2
)
glVertexAttribL3dv=wrapper.wrapper(glVertexAttribL3dv).setInputArraySize(
    'v', 3
)
glVertexAttribL4dv=wrapper.wrapper(glVertexAttribL4dv).setInputArraySize(
    'v', 4
)
# INPUT glVertexAttribLPointer.pointer size not checked against size
glVertexAttribLPointer=wrapper.wrapper(glVertexAttribLPointer).setInputArraySize(
    'pointer', None
)
glGetVertexAttribLdv=wrapper.wrapper(glGetVertexAttribLdv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glViewportArrayv.v size not checked against 'count'
glViewportArrayv=wrapper.wrapper(glViewportArrayv).setInputArraySize(
    'v', None
)
glViewportIndexedfv=wrapper.wrapper(glViewportIndexedfv).setInputArraySize(
    'v', 4
)
# INPUT glScissorArrayv.v size not checked against 'count'
glScissorArrayv=wrapper.wrapper(glScissorArrayv).setInputArraySize(
    'v', None
)
glScissorIndexedv=wrapper.wrapper(glScissorIndexedv).setInputArraySize(
    'v', 4
)
# INPUT glDepthRangeArrayv.v size not checked against 'count'
glDepthRangeArrayv=wrapper.wrapper(glDepthRangeArrayv).setInputArraySize(
    'v', None
)
glGetFloati_v=wrapper.wrapper(glGetFloati_v).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
glGetDoublei_v=wrapper.wrapper(glGetDoublei_v).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
### END AUTOGENERATED SECTION
from OpenGL.GL.ARB.ES2_compatibility import *
from OpenGL.GL.ARB.get_program_binary import *
from OpenGL.GL.ARB.separate_shader_objects import *
from OpenGL.GL.ARB.shader_precision import *
from OpenGL.GL.ARB.vertex_attrib_64bit import *
from OpenGL.GL.ARB.viewport_array import *
