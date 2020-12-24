'''OpenGL extension VERSION.GLES1_1_0

This module customises the behaviour of the 
OpenGL.raw.GLES1.VERSION.GLES1_1_0 to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/VERSION/GLES1_1_0.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES1 import _types, _glgets
from OpenGL.raw.GLES1.VERSION.GLES1_1_0 import *
from OpenGL.raw.GLES1.VERSION.GLES1_1_0 import _EXTENSION_NAME

def glInitGles110VERSION():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glClipPlanef=wrapper.wrapper(glClipPlanef).setInputArraySize(
    'eqn', 4
)
# INPUT glFogfv.params size not checked against 'pname'
glFogfv=wrapper.wrapper(glFogfv).setInputArraySize(
    'params', None
)
glGetClipPlanef=wrapper.wrapper(glGetClipPlanef).setInputArraySize(
    'equation', 4
)
glGetFloatv=wrapper.wrapper(glGetFloatv).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetLightfv=wrapper.wrapper(glGetLightfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetMaterialfv=wrapper.wrapper(glGetMaterialfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexEnvfv=wrapper.wrapper(glGetTexEnvfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexParameterfv=wrapper.wrapper(glGetTexParameterfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glLightModelfv.params size not checked against 'pname'
glLightModelfv=wrapper.wrapper(glLightModelfv).setInputArraySize(
    'params', None
)
# INPUT glLightfv.params size not checked against 'pname'
glLightfv=wrapper.wrapper(glLightfv).setInputArraySize(
    'params', None
)
glLoadMatrixf=wrapper.wrapper(glLoadMatrixf).setInputArraySize(
    'm', 16
)
# INPUT glMaterialfv.params size not checked against 'pname'
glMaterialfv=wrapper.wrapper(glMaterialfv).setInputArraySize(
    'params', None
)
glMultMatrixf=wrapper.wrapper(glMultMatrixf).setInputArraySize(
    'm', 16
)
# INPUT glPointParameterfv.params size not checked against 'pname'
glPointParameterfv=wrapper.wrapper(glPointParameterfv).setInputArraySize(
    'params', None
)
# INPUT glTexEnvfv.params size not checked against 'pname'
glTexEnvfv=wrapper.wrapper(glTexEnvfv).setInputArraySize(
    'params', None
)
# INPUT glTexParameterfv.params size not checked against 'pname'
glTexParameterfv=wrapper.wrapper(glTexParameterfv).setInputArraySize(
    'params', None
)
# INPUT glBufferData.data size not checked against size
glBufferData=wrapper.wrapper(glBufferData).setInputArraySize(
    'data', None
)
# INPUT glBufferSubData.data size not checked against size
glBufferSubData=wrapper.wrapper(glBufferSubData).setInputArraySize(
    'data', None
)
glClipPlanex=wrapper.wrapper(glClipPlanex).setInputArraySize(
    'equation', 4
)
# INPUT glColorPointer.pointer size not checked against 'size,type,stride'
glColorPointer=wrapper.wrapper(glColorPointer).setInputArraySize(
    'pointer', None
)
# INPUT glCompressedTexImage2D.data size not checked against imageSize
glCompressedTexImage2D=wrapper.wrapper(glCompressedTexImage2D).setInputArraySize(
    'data', None
)
# INPUT glCompressedTexSubImage2D.data size not checked against imageSize
glCompressedTexSubImage2D=wrapper.wrapper(glCompressedTexSubImage2D).setInputArraySize(
    'data', None
)
# INPUT glDeleteBuffers.buffers size not checked against n
glDeleteBuffers=wrapper.wrapper(glDeleteBuffers).setInputArraySize(
    'buffers', None
)
# INPUT glDeleteTextures.textures size not checked against n
glDeleteTextures=wrapper.wrapper(glDeleteTextures).setInputArraySize(
    'textures', None
)
# INPUT glDrawElements.indices size not checked against 'count,type'
glDrawElements=wrapper.wrapper(glDrawElements).setInputArraySize(
    'indices', None
)
# INPUT glFogxv.param size not checked against 'pname'
glFogxv=wrapper.wrapper(glFogxv).setInputArraySize(
    'param', None
)
glGetBooleanv=wrapper.wrapper(glGetBooleanv).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetBufferParameteriv=wrapper.wrapper(glGetBufferParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetClipPlanex=wrapper.wrapper(glGetClipPlanex).setInputArraySize(
    'equation', 4
)
glGenBuffers=wrapper.wrapper(glGenBuffers).setOutput(
    'buffers',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGenTextures=wrapper.wrapper(glGenTextures).setOutput(
    'textures',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGetIntegerv=wrapper.wrapper(glGetIntegerv).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glGetLightxv.params size not checked against 'pname'
glGetLightxv=wrapper.wrapper(glGetLightxv).setInputArraySize(
    'params', None
)
# INPUT glGetMaterialxv.params size not checked against 'pname'
glGetMaterialxv=wrapper.wrapper(glGetMaterialxv).setInputArraySize(
    'params', None
)
glGetPointerv=wrapper.wrapper(glGetPointerv).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetTexEnviv=wrapper.wrapper(glGetTexEnviv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glGetTexEnvxv.params size not checked against 'pname'
glGetTexEnvxv=wrapper.wrapper(glGetTexEnvxv).setInputArraySize(
    'params', None
)
glGetTexParameteriv=wrapper.wrapper(glGetTexParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glGetTexParameterxv.params size not checked against 'pname'
glGetTexParameterxv=wrapper.wrapper(glGetTexParameterxv).setInputArraySize(
    'params', None
)
# INPUT glLightModelxv.param size not checked against 'pname'
glLightModelxv=wrapper.wrapper(glLightModelxv).setInputArraySize(
    'param', None
)
# INPUT glLightxv.params size not checked against 'pname'
glLightxv=wrapper.wrapper(glLightxv).setInputArraySize(
    'params', None
)
glLoadMatrixx=wrapper.wrapper(glLoadMatrixx).setInputArraySize(
    'm', 16
)
# INPUT glMaterialxv.param size not checked against 'pname'
glMaterialxv=wrapper.wrapper(glMaterialxv).setInputArraySize(
    'param', None
)
glMultMatrixx=wrapper.wrapper(glMultMatrixx).setInputArraySize(
    'm', 16
)
# INPUT glNormalPointer.pointer size not checked against 'type,stride'
glNormalPointer=wrapper.wrapper(glNormalPointer).setInputArraySize(
    'pointer', None
)
# INPUT glPointParameterxv.params size not checked against 'pname'
glPointParameterxv=wrapper.wrapper(glPointParameterxv).setInputArraySize(
    'params', None
)
# OUTPUT glReadPixels.pixels COMPSIZE(format, type, width, height) 
# INPUT glTexCoordPointer.pointer size not checked against 'size,type,stride'
glTexCoordPointer=wrapper.wrapper(glTexCoordPointer).setInputArraySize(
    'pointer', None
)
# INPUT glTexEnviv.params size not checked against 'pname'
glTexEnviv=wrapper.wrapper(glTexEnviv).setInputArraySize(
    'params', None
)
# INPUT glTexEnvxv.params size not checked against 'pname'
glTexEnvxv=wrapper.wrapper(glTexEnvxv).setInputArraySize(
    'params', None
)
# INPUT glTexImage2D.pixels size not checked against 'format,type,width,height'
glTexImage2D=wrapper.wrapper(glTexImage2D).setInputArraySize(
    'pixels', None
)
# INPUT glTexParameteriv.params size not checked against 'pname'
glTexParameteriv=wrapper.wrapper(glTexParameteriv).setInputArraySize(
    'params', None
)
# INPUT glTexParameterxv.params size not checked against 'pname'
glTexParameterxv=wrapper.wrapper(glTexParameterxv).setInputArraySize(
    'params', None
)
# INPUT glTexSubImage2D.pixels size not checked against 'format,type,width,height'
glTexSubImage2D=wrapper.wrapper(glTexSubImage2D).setInputArraySize(
    'pixels', None
)
# INPUT glVertexPointer.pointer size not checked against 'size,type,stride'
glVertexPointer=wrapper.wrapper(glVertexPointer).setInputArraySize(
    'pointer', None
)
### END AUTOGENERATED SECTION