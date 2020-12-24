'''OpenGL extension SC.VERSION_2_0

This module customises the behaviour of the 
OpenGL.raw.GLSC2.SC.VERSION_2_0 to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SC/VERSION_2_0.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLSC2 import _types, _glgets
from OpenGL.raw.GLSC2.SC.VERSION_2_0 import *
from OpenGL.raw.GLSC2.SC.VERSION_2_0 import _EXTENSION_NAME

def glInitVersion20SC():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glBufferData.data size not checked against size
glBufferData=wrapper.wrapper(glBufferData).setInputArraySize(
    'data', None
)
# INPUT glBufferSubData.data size not checked against size
glBufferSubData=wrapper.wrapper(glBufferSubData).setInputArraySize(
    'data', None
)
# INPUT glCompressedTexSubImage2D.data size not checked against imageSize
glCompressedTexSubImage2D=wrapper.wrapper(glCompressedTexSubImage2D).setInputArraySize(
    'data', None
)
# INPUT glDrawRangeElements.indices size not checked against 'count,type'
glDrawRangeElements=wrapper.wrapper(glDrawRangeElements).setInputArraySize(
    'indices', None
)
glGenBuffers=wrapper.wrapper(glGenBuffers).setOutput(
    'buffers',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGenFramebuffers=wrapper.wrapper(glGenFramebuffers).setOutput(
    'framebuffers',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGenRenderbuffers=wrapper.wrapper(glGenRenderbuffers).setOutput(
    'renderbuffers',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGenTextures=wrapper.wrapper(glGenTextures).setOutput(
    'textures',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGetBooleanv=wrapper.wrapper(glGetBooleanv).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetBufferParameteriv=wrapper.wrapper(glGetBufferParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetFloatv=wrapper.wrapper(glGetFloatv).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetFramebufferAttachmentParameteriv=wrapper.wrapper(glGetFramebufferAttachmentParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetIntegerv=wrapper.wrapper(glGetIntegerv).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetProgramiv=wrapper.wrapper(glGetProgramiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetRenderbufferParameteriv=wrapper.wrapper(glGetRenderbufferParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexParameterfv=wrapper.wrapper(glGetTexParameterfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexParameteriv=wrapper.wrapper(glGetTexParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glGetnUniformfv.params size not checked against bufSize
glGetnUniformfv=wrapper.wrapper(glGetnUniformfv).setInputArraySize(
    'params', None
)
# INPUT glGetnUniformiv.params size not checked against bufSize
glGetnUniformiv=wrapper.wrapper(glGetnUniformiv).setInputArraySize(
    'params', None
)
glGetVertexAttribfv=wrapper.wrapper(glGetVertexAttribfv).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetVertexAttribiv=wrapper.wrapper(glGetVertexAttribiv).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetVertexAttribPointerv=wrapper.wrapper(glGetVertexAttribPointerv).setOutput(
    'pointer',size=(1,),orPassIn=True
)
# INPUT glProgramBinary.binary size not checked against length
glProgramBinary=wrapper.wrapper(glProgramBinary).setInputArraySize(
    'binary', None
)
# INPUT glReadnPixels.data size not checked against bufSize
glReadnPixels=wrapper.wrapper(glReadnPixels).setInputArraySize(
    'data', None
)
# INPUT glTexParameterfv.params size not checked against 'pname'
glTexParameterfv=wrapper.wrapper(glTexParameterfv).setInputArraySize(
    'params', None
)
# INPUT glTexParameteriv.params size not checked against 'pname'
glTexParameteriv=wrapper.wrapper(glTexParameteriv).setInputArraySize(
    'params', None
)
# INPUT glTexSubImage2D.pixels size not checked against 'format,type,width,height'
glTexSubImage2D=wrapper.wrapper(glTexSubImage2D).setInputArraySize(
    'pixels', None
)
# INPUT glUniform1fv.value size not checked against count
glUniform1fv=wrapper.wrapper(glUniform1fv).setInputArraySize(
    'value', None
)
# INPUT glUniform1iv.value size not checked against count
glUniform1iv=wrapper.wrapper(glUniform1iv).setInputArraySize(
    'value', None
)
# INPUT glUniform2fv.value size not checked against count*2
glUniform2fv=wrapper.wrapper(glUniform2fv).setInputArraySize(
    'value', None
)
# INPUT glUniform2iv.value size not checked against count*2
glUniform2iv=wrapper.wrapper(glUniform2iv).setInputArraySize(
    'value', None
)
# INPUT glUniform3fv.value size not checked against count*3
glUniform3fv=wrapper.wrapper(glUniform3fv).setInputArraySize(
    'value', None
)
# INPUT glUniform3iv.value size not checked against count*3
glUniform3iv=wrapper.wrapper(glUniform3iv).setInputArraySize(
    'value', None
)
# INPUT glUniform4fv.value size not checked against count*4
glUniform4fv=wrapper.wrapper(glUniform4fv).setInputArraySize(
    'value', None
)
# INPUT glUniform4iv.value size not checked against count*4
glUniform4iv=wrapper.wrapper(glUniform4iv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix2fv.value size not checked against count*4
glUniformMatrix2fv=wrapper.wrapper(glUniformMatrix2fv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix3fv.value size not checked against count*9
glUniformMatrix3fv=wrapper.wrapper(glUniformMatrix3fv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix4fv.value size not checked against count*16
glUniformMatrix4fv=wrapper.wrapper(glUniformMatrix4fv).setInputArraySize(
    'value', None
)
glVertexAttrib1fv=wrapper.wrapper(glVertexAttrib1fv).setInputArraySize(
    'v', 1
)
glVertexAttrib2fv=wrapper.wrapper(glVertexAttrib2fv).setInputArraySize(
    'v', 2
)
glVertexAttrib3fv=wrapper.wrapper(glVertexAttrib3fv).setInputArraySize(
    'v', 3
)
glVertexAttrib4fv=wrapper.wrapper(glVertexAttrib4fv).setInputArraySize(
    'v', 4
)
# INPUT glVertexAttribPointer.pointer size not checked against 'size,type,stride'
glVertexAttribPointer=wrapper.wrapper(glVertexAttribPointer).setInputArraySize(
    'pointer', None
)
### END AUTOGENERATED SECTION