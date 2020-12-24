'''OpenGL extension ES.VERSION_3_2

This module customises the behaviour of the 
OpenGL.raw.GLES2.ES.VERSION_3_2 to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ES/VERSION_3_2.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES2 import _types, _glgets
from OpenGL.raw.GLES2.ES.VERSION_3_2 import *
from OpenGL.raw.GLES2.ES.VERSION_3_2 import _EXTENSION_NAME

def glInitVersion32ES():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDebugMessageControl.ids size not checked against count
glDebugMessageControl=wrapper.wrapper(glDebugMessageControl).setInputArraySize(
    'ids', None
)
# INPUT glDebugMessageInsert.buf size not checked against 'buf,length'
glDebugMessageInsert=wrapper.wrapper(glDebugMessageInsert).setInputArraySize(
    'buf', None
)
glGetDebugMessageLog=wrapper.wrapper(glGetDebugMessageLog).setOutput(
    'ids',size=lambda x:(x,),pnameArg='count',orPassIn=True
).setOutput(
    'lengths',size=lambda x:(x,),pnameArg='count',orPassIn=True
).setOutput(
    'messageLog',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'severities',size=lambda x:(x,),pnameArg='count',orPassIn=True
).setOutput(
    'sources',size=lambda x:(x,),pnameArg='count',orPassIn=True
).setOutput(
    'types',size=lambda x:(x,),pnameArg='count',orPassIn=True
)
# INPUT glPushDebugGroup.message size not checked against 'message,length'
glPushDebugGroup=wrapper.wrapper(glPushDebugGroup).setInputArraySize(
    'message', None
)
# INPUT glObjectLabel.label size not checked against 'label,length'
glObjectLabel=wrapper.wrapper(glObjectLabel).setInputArraySize(
    'label', None
)
glGetObjectLabel=wrapper.wrapper(glGetObjectLabel).setOutput(
    'label',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'length',size=(1,),orPassIn=True
)
# INPUT glObjectPtrLabel.label size not checked against 'label,length'
glObjectPtrLabel=wrapper.wrapper(glObjectPtrLabel).setInputArraySize(
    'label', None
)
glGetObjectPtrLabel=wrapper.wrapper(glGetObjectPtrLabel).setOutput(
    'label',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'length',size=(1,),orPassIn=True
)
glGetPointerv=wrapper.wrapper(glGetPointerv).setOutput(
    'params',size=(1,),orPassIn=True
)
# INPUT glDrawElementsBaseVertex.indices size not checked against 'count,type'
glDrawElementsBaseVertex=wrapper.wrapper(glDrawElementsBaseVertex).setInputArraySize(
    'indices', None
)
# INPUT glDrawRangeElementsBaseVertex.indices size not checked against 'count,type'
glDrawRangeElementsBaseVertex=wrapper.wrapper(glDrawRangeElementsBaseVertex).setInputArraySize(
    'indices', None
)
# INPUT glDrawElementsInstancedBaseVertex.indices size not checked against 'count,type'
glDrawElementsInstancedBaseVertex=wrapper.wrapper(glDrawElementsInstancedBaseVertex).setInputArraySize(
    'indices', None
)
# INPUT glReadnPixels.data size not checked against bufSize
glReadnPixels=wrapper.wrapper(glReadnPixels).setInputArraySize(
    'data', None
)
# INPUT glGetnUniformfv.params size not checked against bufSize
glGetnUniformfv=wrapper.wrapper(glGetnUniformfv).setInputArraySize(
    'params', None
)
# INPUT glGetnUniformiv.params size not checked against bufSize
glGetnUniformiv=wrapper.wrapper(glGetnUniformiv).setInputArraySize(
    'params', None
)
# INPUT glGetnUniformuiv.params size not checked against bufSize
glGetnUniformuiv=wrapper.wrapper(glGetnUniformuiv).setInputArraySize(
    'params', None
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
# INPUT glSamplerParameterIiv.param size not checked against 'pname'
glSamplerParameterIiv=wrapper.wrapper(glSamplerParameterIiv).setInputArraySize(
    'param', None
)
# INPUT glSamplerParameterIuiv.param size not checked against 'pname'
glSamplerParameterIuiv=wrapper.wrapper(glSamplerParameterIuiv).setInputArraySize(
    'param', None
)
glGetSamplerParameterIiv=wrapper.wrapper(glGetSamplerParameterIiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetSamplerParameterIuiv=wrapper.wrapper(glGetSamplerParameterIuiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
### END AUTOGENERATED SECTION