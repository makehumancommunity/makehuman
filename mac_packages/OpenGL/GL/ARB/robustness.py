'''OpenGL extension ARB.robustness

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.robustness to provide a more 
Python-friendly API

Overview (from the spec)
	
	Several recent trends in how OpenGL integrates into modern computer
	systems have created new requirements for robustness and security
	for OpenGL rendering contexts.
	
	Additionally GPU architectures now support hardware fault detection;
	for example, video memory supporting ECC (error correcting codes)
	and error detection.  OpenGL contexts should be capable of recovering
	from hardware faults such as uncorrectable memory errors.  Along with
	recovery from such hardware faults, the recovery mechanism can
	also allow recovery from video memory access exceptions and system
	software failures.  System software failures can be due to device
	changes or driver failures.
	
	Demands for increased software robustness and concerns about malware
	exploiting buffer overflows have lead API designers to provide
	additional "safe" APIs that bound the amount of data returned by
	an API query.  For example, the safer "snprintf" or "_snprintf"
	routines are prefered over "sprintf".
	
	The OpenGL API has many such robustness perils.  OpenGL queries
	return (write) some number of bytes to a buffer indicated by a
	pointer parameter.  The exact number of bytes written by existing
	OpenGL queries is not expressed directly by any specific parameter;
	instead the number of bytes returned is a complex function of one
	or more query arguments, sometimes context state such as pixel
	store modes or the active texture selector, and the current state
	of an object (such as a texture level's number of total texels).
	By the standards of modern API design, such queries are not "safe".
	Making these queries safer involves introducing a new query API with
	an additional parameter that specifies the number of bytes in the
	buffer and never writing bytes beyond that limit.
	
	Multi-threaded use of OpenGL contexts in a "share group" allow
	sharing of objects such as textures and programs.  Such sharing in
	conjunction with concurrent OpenGL commands stream execution by two
	or more contexts introduces hazards whereby one context can change
	objects in ways that can cause buffer overflows for another context's
	OpenGL queries.
	
	The original ARB_vertex_buffer_object extension includes an issue
	that explicitly states program termination is allowed when
	out-of-bounds vertex buffer object fetches occur. Modern GPUs
	capable of DirectX 10 enforce the well-defined behavior of always
	returning zero values for indices or non-fixed components in this
	case. Older GPUs may require extra checks to enforce well-defined
	(and termination free) behavior, but this expense is warranted when
	processing potentially untrusted content.
	
	The intent of this extension is to address some specific robustness
	goals:
	
	*   For all existing OpenGL queries, provide additional "safe" APIs 
	    that limit data written to user pointers to a buffer size in 
	    bytes that is an explicit additional parameter of the query.
	
	*   Provide a mechanism for an OpenGL application to learn about
	    graphics resets that affect the context.  When a graphics reset
	    occurs, the OpenGL context becomes unusable and the application
	    must create a new context to continue operation. Detecting a
	    graphics reset happens through an inexpensive query.
	
	*   Provide an enable to guarantee that out-of-bounds buffer object
	    accesses by the GPU will have deterministic behavior and preclude
	    application instability or termination due to an incorrect buffer
	    access.  Such accesses include vertex buffer fetches of
	    attributes and indices, and indexed reads of uniforms or
	    parameters from buffers.
	
	In one anticipated usage model, WebGL contexts may make use of these
	robust features to grant greater stability when using untrusted code.
	WebGL contexts cannot call OpenGL commands directly but rather must
	route all OpenGL API calls through the web browser.  It is then the
	web browser that configures the context, using the commands in this
	extension, to enforce safe behavior. In this scenario, the WebGL
	content cannot specify or change the use of this extension's features
	itself; the web browser enforces this policy.
	
	There are other well-known robustness issues with the OpenGL API
	which this extension does not address.  For example, selector-based
	OpenGL commands are a well-known source of programming errors.
	Code to manipulate texture state may assume the active texture
	selector is set appropriately when an intervening function call
	obscures a change to the active texture state resulting in
	incorrectly updated or queried state.  The EXT_direct_state_access
	extension introduces selector-free OpenGL commands and queries to
	address that particular issue so this extension does not.
	
	The intent of this extension is NOT to deprecate any existing API
	and thereby introduce compatibility issues and coding burdens on
	existing code, but rather to provide new APIs to ensure a level of
	robustness commensurate with the expectations of modern applications
	of OpenGL.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/robustness.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.robustness import *
from OpenGL.raw.GL.ARB.robustness import _EXTENSION_NAME

def glInitRobustnessARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glGetnTexImageARB=wrapper.wrapper(glGetnTexImageARB).setOutput(
    'img',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glReadnPixelsARB=wrapper.wrapper(glReadnPixelsARB).setOutput(
    'data',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnCompressedTexImageARB=wrapper.wrapper(glGetnCompressedTexImageARB).setOutput(
    'img',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnUniformfvARB=wrapper.wrapper(glGetnUniformfvARB).setOutput(
    'params',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnUniformivARB=wrapper.wrapper(glGetnUniformivARB).setOutput(
    'params',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnUniformuivARB=wrapper.wrapper(glGetnUniformuivARB).setOutput(
    'params',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnUniformdvARB=wrapper.wrapper(glGetnUniformdvARB).setOutput(
    'params',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnMapdvARB=wrapper.wrapper(glGetnMapdvARB).setOutput(
    'v',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnMapfvARB=wrapper.wrapper(glGetnMapfvARB).setOutput(
    'v',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnMapivARB=wrapper.wrapper(glGetnMapivARB).setOutput(
    'v',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnPixelMapfvARB=wrapper.wrapper(glGetnPixelMapfvARB).setOutput(
    'values',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnPixelMapuivARB=wrapper.wrapper(glGetnPixelMapuivARB).setOutput(
    'values',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnPixelMapusvARB=wrapper.wrapper(glGetnPixelMapusvARB).setOutput(
    'values',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnPolygonStippleARB=wrapper.wrapper(glGetnPolygonStippleARB).setOutput(
    'pattern',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnColorTableARB=wrapper.wrapper(glGetnColorTableARB).setOutput(
    'table',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnConvolutionFilterARB=wrapper.wrapper(glGetnConvolutionFilterARB).setOutput(
    'image',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnSeparableFilterARB=wrapper.wrapper(glGetnSeparableFilterARB).setOutput(
    'column',size=lambda x:(x,),pnameArg='columnBufSize',orPassIn=True
).setOutput(
    'row',size=lambda x:(x,),pnameArg='rowBufSize',orPassIn=True
).setOutput(
    'span',size=(0,),orPassIn=True
)
glGetnHistogramARB=wrapper.wrapper(glGetnHistogramARB).setOutput(
    'values',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetnMinmaxARB=wrapper.wrapper(glGetnMinmaxARB).setOutput(
    'values',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
### END AUTOGENERATED SECTION