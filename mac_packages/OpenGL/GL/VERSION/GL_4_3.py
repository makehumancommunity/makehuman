'''OpenGL extension VERSION.GL_4_3

This module customises the behaviour of the 
OpenGL.raw.GL.VERSION.GL_4_3 to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/VERSION/GL_4_3.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.VERSION.GL_4_3 import *
from OpenGL.raw.GL.VERSION.GL_4_3 import _EXTENSION_NAME

def glInitGl43VERSION():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glClearBufferData.data size not checked against 'format,type'
glClearBufferData=wrapper.wrapper(glClearBufferData).setInputArraySize(
    'data', None
)
# INPUT glClearBufferSubData.data size not checked against 'format,type'
glClearBufferSubData=wrapper.wrapper(glClearBufferSubData).setInputArraySize(
    'data', None
)
glGetFramebufferParameteriv=wrapper.wrapper(glGetFramebufferParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetInternalformati64v=wrapper.wrapper(glGetInternalformati64v).setOutput(
    'params',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
# INPUT glInvalidateFramebuffer.attachments size not checked against numAttachments
glInvalidateFramebuffer=wrapper.wrapper(glInvalidateFramebuffer).setInputArraySize(
    'attachments', None
)
# INPUT glInvalidateSubFramebuffer.attachments size not checked against numAttachments
glInvalidateSubFramebuffer=wrapper.wrapper(glInvalidateSubFramebuffer).setInputArraySize(
    'attachments', None
)
# INPUT glMultiDrawArraysIndirect.indirect size not checked against 'drawcount,stride'
glMultiDrawArraysIndirect=wrapper.wrapper(glMultiDrawArraysIndirect).setInputArraySize(
    'indirect', None
)
# INPUT glMultiDrawElementsIndirect.indirect size not checked against 'drawcount,stride'
glMultiDrawElementsIndirect=wrapper.wrapper(glMultiDrawElementsIndirect).setInputArraySize(
    'indirect', None
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
# INPUT glGetProgramResourceLocationIndex.name size not checked against 'name'
glGetProgramResourceLocationIndex=wrapper.wrapper(glGetProgramResourceLocationIndex).setInputArraySize(
    'name', None
)
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
### END AUTOGENERATED SECTION

from OpenGL.GL.ARB.arrays_of_arrays import *
from OpenGL.GL.ARB.fragment_layer_viewport import *
from OpenGL.GL.ARB.shader_image_size import *
from OpenGL.GL.ARB.ES3_compatibility import *
from OpenGL.GL.ARB.clear_buffer_object import *
from OpenGL.GL.ARB.compute_shader import *
from OpenGL.GL.ARB.copy_image import *
# Extension registry no longer defines these extensions?
#from OpenGL.GL.ARB.debug_group import *
#from OpenGL.GL.ARB.debug_label import *
#from OpenGL.GL.ARB.debug_output2 import *
from OpenGL.GL.KHR.debug import *
from OpenGL.GL.ARB.explicit_uniform_location import *
from OpenGL.GL.ARB.framebuffer_no_attachments import *
from OpenGL.GL.ARB.internalformat_query2 import *
from OpenGL.GL.ARB.invalidate_subdata import *
from OpenGL.GL.ARB.multi_draw_indirect import *
from OpenGL.GL.ARB.program_interface_query import *
from OpenGL.GL.ARB.robust_buffer_access_behavior import *
from OpenGL.GL.ARB.shader_storage_buffer_object import *
from OpenGL.GL.ARB.stencil_texturing import *
from OpenGL.GL.ARB.texture_buffer_range import *
from OpenGL.GL.ARB.texture_query_levels import *
from OpenGL.GL.ARB.texture_storage_multisample import *
from OpenGL.GL.ARB.texture_view import *
from OpenGL.GL.ARB.vertex_attrib_binding import *
