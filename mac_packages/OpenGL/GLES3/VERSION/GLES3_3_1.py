'''OpenGL extension VERSION.GLES3_3_1

This module customises the behaviour of the 
OpenGL.raw.GLES3.VERSION.GLES3_3_1 to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/VERSION/GLES3_3_1.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES3 import _types, _glgets
from OpenGL.raw.GLES3.VERSION.GLES3_3_1 import *
from OpenGL.raw.GLES3.VERSION.GLES3_3_1 import _EXTENSION_NAME

def glInitGles331VERSION():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glGetFramebufferParameteriv=wrapper.wrapper(glGetFramebufferParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetProgramInterfaceiv=wrapper.wrapper(glGetProgramInterfaceiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glGetProgramResourceIndex.name size not checked against 'name'
glGetProgramResourceIndex=wrapper.wrapper(glGetProgramResourceIndex).setInputArraySize(
    'name', None
)
glGetProgramResourceName=wrapper.wrapper(glGetProgramResourceName).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'name',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
# INPUT glGetProgramResourceiv.props size not checked against propCount
glGetProgramResourceiv=wrapper.wrapper(glGetProgramResourceiv).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'params',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setInputArraySize(
    'props', None
)
# INPUT glGetProgramResourceLocation.name size not checked against 'name'
glGetProgramResourceLocation=wrapper.wrapper(glGetProgramResourceLocation).setInputArraySize(
    'name', None
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
# INPUT glProgramUniform2iv.value size not checked against count*2
glProgramUniform2iv=wrapper.wrapper(glProgramUniform2iv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3iv.value size not checked against count*3
glProgramUniform3iv=wrapper.wrapper(glProgramUniform3iv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4iv.value size not checked against count*4
glProgramUniform4iv=wrapper.wrapper(glProgramUniform4iv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform1uiv.value size not checked against count
glProgramUniform1uiv=wrapper.wrapper(glProgramUniform1uiv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2uiv.value size not checked against count*2
glProgramUniform2uiv=wrapper.wrapper(glProgramUniform2uiv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3uiv.value size not checked against count*3
glProgramUniform3uiv=wrapper.wrapper(glProgramUniform3uiv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4uiv.value size not checked against count*4
glProgramUniform4uiv=wrapper.wrapper(glProgramUniform4uiv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform1fv.value size not checked against count
glProgramUniform1fv=wrapper.wrapper(glProgramUniform1fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2fv.value size not checked against count*2
glProgramUniform2fv=wrapper.wrapper(glProgramUniform2fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3fv.value size not checked against count*3
glProgramUniform3fv=wrapper.wrapper(glProgramUniform3fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4fv.value size not checked against count*4
glProgramUniform4fv=wrapper.wrapper(glProgramUniform4fv).setInputArraySize(
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
glGetProgramPipelineInfoLog=wrapper.wrapper(glGetProgramPipelineInfoLog).setOutput(
    'infoLog',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'length',size=(1,),orPassIn=True
)
glGetBooleani_v=wrapper.wrapper(glGetBooleani_v).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
glGetMultisamplefv=wrapper.wrapper(glGetMultisamplefv).setOutput(
    'val',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexLevelParameteriv=wrapper.wrapper(glGetTexLevelParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexLevelParameterfv=wrapper.wrapper(glGetTexLevelParameterfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
### END AUTOGENERATED SECTION