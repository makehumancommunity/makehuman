'''OpenGL extension VERSION.GL_3_0

This module customises the behaviour of the 
OpenGL.raw.GL.VERSION.GL_3_0 to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/VERSION/GL_3_0.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.VERSION.GL_3_0 import *
from OpenGL.raw.GL.VERSION.GL_3_0 import _EXTENSION_NAME

def glInitGl30VERSION():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glGetBooleani_v=wrapper.wrapper(glGetBooleani_v).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
glGetIntegeri_v=wrapper.wrapper(glGetIntegeri_v).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
# INPUT glTransformFeedbackVaryings.varyings size not checked against count
glTransformFeedbackVaryings=wrapper.wrapper(glTransformFeedbackVaryings).setInputArraySize(
    'varyings', None
)
glGetTransformFeedbackVarying=wrapper.wrapper(glGetTransformFeedbackVarying).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'name',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'size',size=(1,),orPassIn=True
).setOutput(
    'type',size=(1,),orPassIn=True
)
# INPUT glVertexAttribIPointer.pointer size not checked against 'size,type,stride'
glVertexAttribIPointer=wrapper.wrapper(glVertexAttribIPointer).setInputArraySize(
    'pointer', None
)
glGetVertexAttribIiv=wrapper.wrapper(glGetVertexAttribIiv).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetVertexAttribIuiv=wrapper.wrapper(glGetVertexAttribIuiv).setOutput(
    'params',size=(1,),orPassIn=True
)
glVertexAttribI1iv=wrapper.wrapper(glVertexAttribI1iv).setInputArraySize(
    'v', 1
)
glVertexAttribI2iv=wrapper.wrapper(glVertexAttribI2iv).setInputArraySize(
    'v', 2
)
glVertexAttribI3iv=wrapper.wrapper(glVertexAttribI3iv).setInputArraySize(
    'v', 3
)
glVertexAttribI4iv=wrapper.wrapper(glVertexAttribI4iv).setInputArraySize(
    'v', 4
)
glVertexAttribI1uiv=wrapper.wrapper(glVertexAttribI1uiv).setInputArraySize(
    'v', 1
)
glVertexAttribI2uiv=wrapper.wrapper(glVertexAttribI2uiv).setInputArraySize(
    'v', 2
)
glVertexAttribI3uiv=wrapper.wrapper(glVertexAttribI3uiv).setInputArraySize(
    'v', 3
)
glVertexAttribI4uiv=wrapper.wrapper(glVertexAttribI4uiv).setInputArraySize(
    'v', 4
)
glVertexAttribI4bv=wrapper.wrapper(glVertexAttribI4bv).setInputArraySize(
    'v', 4
)
glVertexAttribI4sv=wrapper.wrapper(glVertexAttribI4sv).setInputArraySize(
    'v', 4
)
glVertexAttribI4ubv=wrapper.wrapper(glVertexAttribI4ubv).setInputArraySize(
    'v', 4
)
glVertexAttribI4usv=wrapper.wrapper(glVertexAttribI4usv).setInputArraySize(
    'v', 4
)
# OUTPUT glGetUniformuiv.params COMPSIZE(program, location) 
# INPUT glBindFragDataLocation.name size not checked against 'name'
glBindFragDataLocation=wrapper.wrapper(glBindFragDataLocation).setInputArraySize(
    'name', None
)
# INPUT glGetFragDataLocation.name size not checked against 'name'
glGetFragDataLocation=wrapper.wrapper(glGetFragDataLocation).setInputArraySize(
    'name', None
)
# INPUT glUniform1uiv.value size not checked against count
glUniform1uiv=wrapper.wrapper(glUniform1uiv).setInputArraySize(
    'value', None
)
# INPUT glUniform2uiv.value size not checked against count*2
glUniform2uiv=wrapper.wrapper(glUniform2uiv).setInputArraySize(
    'value', None
)
# INPUT glUniform3uiv.value size not checked against count*3
glUniform3uiv=wrapper.wrapper(glUniform3uiv).setInputArraySize(
    'value', None
)
# INPUT glUniform4uiv.value size not checked against count*4
glUniform4uiv=wrapper.wrapper(glUniform4uiv).setInputArraySize(
    'value', None
)
# INPUT glTexParameterIiv.params size not checked against 'pname'
glTexParameterIiv=wrapper.wrapper(glTexParameterIiv).setInputArraySize(
    'params', None
)
# INPUT glTexParameterIuiv.params size not checked against 'pname'
glTexParameterIuiv=wrapper.wrapper(glTexParameterIuiv).setInputArraySize(
    'params', None
)
glGetTexParameterIiv=wrapper.wrapper(glGetTexParameterIiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexParameterIuiv=wrapper.wrapper(glGetTexParameterIuiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glClearBufferiv.value size not checked against 'buffer'
glClearBufferiv=wrapper.wrapper(glClearBufferiv).setInputArraySize(
    'value', None
)
# INPUT glClearBufferuiv.value size not checked against 'buffer'
glClearBufferuiv=wrapper.wrapper(glClearBufferuiv).setInputArraySize(
    'value', None
)
# INPUT glClearBufferfv.value size not checked against 'buffer'
glClearBufferfv=wrapper.wrapper(glClearBufferfv).setInputArraySize(
    'value', None
)
# INPUT glDeleteRenderbuffers.renderbuffers size not checked against n
glDeleteRenderbuffers=wrapper.wrapper(glDeleteRenderbuffers).setInputArraySize(
    'renderbuffers', None
)
glGenRenderbuffers=wrapper.wrapper(glGenRenderbuffers).setOutput(
    'renderbuffers',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGetRenderbufferParameteriv=wrapper.wrapper(glGetRenderbufferParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glDeleteFramebuffers.framebuffers size not checked against n
glDeleteFramebuffers=wrapper.wrapper(glDeleteFramebuffers).setInputArraySize(
    'framebuffers', None
)
glGenFramebuffers=wrapper.wrapper(glGenFramebuffers).setOutput(
    'framebuffers',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGetFramebufferAttachmentParameteriv=wrapper.wrapper(glGetFramebufferAttachmentParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glDeleteVertexArrays.arrays size not checked against n
glDeleteVertexArrays=wrapper.wrapper(glDeleteVertexArrays).setInputArraySize(
    'arrays', None
)
glGenVertexArrays=wrapper.wrapper(glGenVertexArrays).setOutput(
    'arrays',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
### END AUTOGENERATED SECTION
from ctypes import c_char_p
glGetStringi.restype = c_char_p
