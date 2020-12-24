'''OpenGL extension ARB.framebuffer_object

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.framebuffer_object to provide a more 
Python-friendly API

Overview (from the spec)
	
	ARB_framebuffer_object is an extension intended to address the following
	goals:
	
	- Reflect FBO-related functionality found in the OpenGL 3.0 specification.
	
	- Integrate multiple disjoint extensions into a single ARB extension.
	  These extensions are:
	
	    EXT_framebuffer_object
	    EXT_framebuffer_blit
	    EXT_framebuffer_multisample
	    EXT_packed_depth_stencil
	
	- Where appropriate, relax some of the constraints expressed by previous
	  FBO-related extensions. In particular the requirement of matching
	  attachment dimensions and component sizes has been relaxed, to allow
	  implementations the freedom to support more flexible usages where
	  possible.
	
	
	ARB_framebuffer_object defines an interface for drawing to rendering
	destinations other than the buffers provided to the GL by the
	window-system.
	
	In this extension, these newly defined rendering destinations are
	known collectively as "framebuffer-attachable images".  This
	extension provides a mechanism for attaching framebuffer-attachable
	images to the GL framebuffer as one of the standard GL logical
	buffers: color, depth, and stencil.  (Attaching a
	framebuffer-attachable image to the accum logical buffer is left for
	a future extension to define).  When a framebuffer-attachable image
	is attached to the framebuffer, it is used as the source and
	destination of fragment operations as described in Chapter 4.
	
	By allowing the use of a framebuffer-attachable image as a rendering
	destination, this extension enables a form of "offscreen" rendering.
	Furthermore, "render to texture" is supported by allowing the images
	of a texture to be used as framebuffer-attachable images.  A
	particular image of a texture object is selected for use as a
	framebuffer-attachable image by specifying the mipmap level, cube
	map face (for a cube map texture), and layer (for a 3D texture)
	that identifies the image.  The "render to texture" semantics of
	this extension are similar to performing traditional rendering to
	the framebuffer, followed immediately by a call to CopyTexSubImage.
	However, by using this extension instead, an application can achieve
	the same effect, but with the advantage that the GL can usually
	eliminate the data copy that would have been incurred by calling
	CopyTexSubImage.
	
	This extension also defines a new GL object type, called a
	"renderbuffer", which encapsulates a single 2D pixel image.  The
	image of renderbuffer can be used as a framebuffer-attachable image
	for generalized offscreen rendering and it also provides a means to
	support rendering to GL logical buffer types which have no
	corresponding texture format (stencil, accum, etc).  A renderbuffer
	is similar to a texture in that both renderbuffers and textures can
	be independently allocated and shared among multiple contexts.  The
	framework defined by this extension is general enough that support
	for attaching images from GL objects other than textures and
	renderbuffers could be added by layered extensions.
	
	To facilitate efficient switching between collections of
	framebuffer-attachable images, this extension introduces another new
	GL object, called a framebuffer object.  A framebuffer object
	contains the state that defines the traditional GL framebuffer,
	including its set of images.  Prior to this extension, it was the
	window-system which defined and managed this collection of images,
	traditionally by grouping them into a "drawable".  The window-system
	API's would also provide a function (i.e., wglMakeCurrent,
	glXMakeCurrent, aglSetDrawable, etc.) to bind a drawable with a GL
	context (as is done in the WGL_ARB_pbuffer extension).  In this
	extension however, this functionality is subsumed by the GL and the
	GL provides the function BindFramebufferARB to bind a framebuffer
	object to the current context.  Later, the context can bind back to
	the window-system-provided framebuffer in order to display rendered
	content.
	
	Previous extensions that enabled rendering to a texture have been
	much more complicated.  One example is the combination of
	ARB_pbuffer and ARB_render_texture, both of which are window-system
	extensions.  This combination requires calling MakeCurrent, an
	operation that may be expensive, to switch between the window and
	the pbuffer drawables.  An application must create one pbuffer per
	renderable texture in order to portably use ARB_render_texture.  An
	application must maintain at least one GL context per texture
	format, because each context can only operate on a single
	pixelformat or FBConfig.  All of these characteristics make
	ARB_render_texture both inefficient and cumbersome to use.
	
	ARB_framebuffer_object, on the other hand, is both simpler to use
	and more efficient than ARB_render_texture.  The
	ARB_framebuffer_object API is contained wholly within the GL API and
	has no (non-portable) window-system components.  Under
	ARB_framebuffer_object, it is not necessary to create a second GL
	context when rendering to a texture image whose format differs from
	that of the window.  Finally, unlike the pbuffers of
	ARB_render_texture, a single framebuffer object can facilitate
	rendering to an unlimited number of texture objects.
	
	This extension differs from EXT_framebuffer_object by splitting the
	framebuffer object binding point into separate DRAW and READ
	bindings (incorporating functionality introduced by
	EXT_framebuffer_blit). This allows copying directly from one
	framebuffer to another. In addition, a new high performance blit
	function is added to facilitate these blits and perform some data
	conversion where allowed.
	
	This extension also enables usage of multisampling in conjunction with
	renderbuffers (incorporating functionality from
	EXT_packed_depth_stencil), as follows:
	
	The new operation RenderbufferStorageMultisample() allocates
	storage for a renderbuffer object that can be used as a multisample
	buffer.  A multisample render buffer image differs from a
	single-sample render buffer image in that a multisample image has a
	number of SAMPLES that is greater than zero.  No method is provided
	for creating multisample texture images.
	
	All of the framebuffer-attachable images attached to a framebuffer
	object must have the same number of SAMPLES or else the framebuffer
	object is not "framebuffer complete".  If a framebuffer object with
	multisample attachments is "framebuffer complete", then the
	framebuffer object behaves as if SAMPLE_BUFFERS is one.
	
	In traditional multisample rendering, where
	DRAW_FRAMEBUFFER_BINDING is zero and SAMPLE_BUFFERS is one, the
	GL spec states that "the color sample values are resolved to a
	single, displayable color each time a pixel is updated."  There are,
	however, several modern hardware implementations that do not
	actually resolve for each sample update, but instead postpones the
	resolve operation to a later time and resolve a batch of sample
	updates at a time.  This is OK as long as the implementation behaves
	"as if" it had resolved a sample-at-a-time. Unfortunately, however,
	honoring the "as if" rule can sometimes degrade performance.
	
	In contrast, when DRAW_FRAMEBUFFER_BINDING is an
	application-created framebuffer object, MULTISAMPLE is enabled, and
	SAMPLE_BUFFERS is one, there is no implicit per-sample-update
	resolve.  Instead, the application explicitly controls when the
	resolve operation is performed.  The resolve operation is affected
	by calling BlitFramebuffer where the source is a multisample
	application-created framebuffer object and the destination is a
	single-sample framebuffer object (either application-created or
	window-system provided).
	
	This design for multisample resolve more closely matches current
	hardware, but still permits implementations which choose to resolve
	a single sample at a time.  If hardware that implements the
	multisample resolution "one sample at a time" exposes
	ARB_framebuffer_object, it could perform the implicit resolve
	to a driver-managed hidden surface, then read from that surface when
	the application calls BlitFramebuffer.
	
	Another motivation for granting the application explicit control
	over the multisample resolve operation has to do with the
	flexibility afforded by ARB_framebuffer_object.  Previously, a
	drawable (window or pbuffer) had exclusive access to all of its
	buffers.  There was no mechanism for sharing a buffer across
	multiple drawables.  Under ARB_framebuffer_object, however, a
	mechanism exists for sharing a framebuffer-attachable image across
	several framebuffer objects, as well as sharing an image between a
	framebuffer object and a texture.  If we had retained the "implicit"
	resolve from traditional multisampled rendering, and allowed the
	creation of "multisample" format renderbuffers, then this type of
	sharing would have lead to two problematic situations:
	
	  * Two contexts, which shared renderbuffers, might perform
	    competing resolve operations into the same single-sample buffer
	    with ambiguous results.
	
	  * It would have introduced the unfortunate ability to use the
	    single-sample buffer as a texture while MULTISAMPLE is ENABLED.
	
	Using BlitFramebuffer as an explicit resolve to serialize access to
	the multisampled contents and eliminate the implicit per-sample
	resolve operation, we avoid both of these problems.
	
	This extension also enables usage of packed depth-stencil formats in
	renderbuffers (incorporating functionality from
	EXT_packed_depth_stencil), as follows:
	
	Many OpenGL implementations have chosen to interleave the depth and
	stencil buffers into one buffer, often with 24 bits of depth
	precision and 8 bits of stencil data.  32 bits is more than is
	needed for the depth buffer much of the time; a 24-bit depth buffer,
	on the other hand, requires that reads and writes of depth data be
	unaligned with respect to power-of-two boundaries.  On the other
	hand, 8 bits of stencil data is more than sufficient for most
	applications, so it is only natural to pack the two buffers into a
	single buffer with both depth and stencil data.  OpenGL never
	provides direct access to the buffers, so the OpenGL implementation
	can provide an interface to applications where it appears the one
	merged buffer is composed of two logical buffers.
	
	One disadvantage of this scheme is that OpenGL lacks any means by
	which this packed data can be handled efficiently.  For example,
	when an application reads from the 24-bit depth buffer, using the
	type GL_UNSIGNED_SHORT will lose 8 bits of data, while
	GL_UNSIGNED_INT has 8 too many.  Both require expensive format
	conversion operations.  A 24-bit format would be no more suitable,
	because it would also suffer from the unaligned memory accesses that
	made the standalone 24-bit depth buffer an unattractive proposition
	in the first place.
	
	Many applications, such as parallel rendering applications, may also
	wish to draw to or read back from both the depth and stencil buffers
	at the same time.  Currently this requires two separate operations,
	reducing performance.  Since the buffers are interleaved, drawing to
	or reading from both should be no more expensive than using just
	one; in some cases, it may even be cheaper.
	
	This extension provides a new data format, GL_DEPTH_STENCIL,
	that can be used with the glDrawPixels, glReadPixels, and
	glCopyPixels commands, as well as a packed data type,
	GL_UNSIGNED_INT_24_8, that is meant to be used with
	GL_DEPTH_STENCIL.  No other data types are supported with
	GL_DEPTH_STENCIL.  If ARB_depth_texture or SGIX_depth_texture is
	supported, GL_DEPTH_STENCIL/GL_UNSIGNED_INT_24_8 data can
	also be used for textures; this provides a more efficient way to
	supply data for a 24-bit depth texture.
	
	GL_DEPTH_STENCIL data, when passed through the pixel path,
	undergoes both depth and stencil operations.  The depth data is
	scaled and biased by the current GL_DEPTH_SCALE and GL_DEPTH_BIAS,
	while the stencil data is shifted and offset by the current
	GL_INDEX_SHIFT and GL_INDEX_OFFSET.  The stencil data is also put
	through the stencil-to-stencil pixel map.
	
	glDrawPixels of GL_DEPTH_STENCIL data operates similarly to that
	of GL_STENCIL_INDEX data, bypassing the OpenGL fragment pipeline
	entirely, unlike the treatment of GL_DEPTH_COMPONENT data.  The
	stencil and depth masks are applied, as are the pixel ownership and
	scissor tests, but all other operations are skipped.
	
	glReadPixels of GL_DEPTH_STENCIL data reads back a rectangle
	from both the depth and stencil buffers.
	
	glCopyPixels of GL_DEPTH_STENCIL data copies a rectangle from
	both the depth and stencil buffers.  Like glDrawPixels, it applies
	both the stencil and depth masks but skips the remainder of the
	OpenGL fragment pipeline.
	
	glTex[Sub]Image[1,2,3]D of GL_DEPTH_STENCIL data loads depth and
	stencil data into a depth_stencil texture.  glGetTexImage of
	GL_DEPTH_STENCIL data can be used to retrieve depth and stencil
	data from a depth/stencil texture.
	
	In addition, a new base internal format, GL_DEPTH_STENCIL, can
	be used by both texture images and renderbuffer storage.  When an
	image with a DEPTH_STENCIL internal format is attached to both
	the depth and stencil attachment points of a framebuffer object,
	then it becomes both the depth and stencil
	buffers of the framebuffer.  This fits nicely with hardware that
	interleaves both depth and stencil data into a single buffer.  When
	a texture with DEPTH_STENCIL data is bound for texturing, only
	the depth component is accessible through the texture fetcher.  The
	stencil data can be written with TexImage or CopyTexImage, and can
	be read with GetTexImage.  When a DEPTH_STENCIL image is
	attached to the stencil attachment of the bound framebuffer object,
	the stencil data can be accessed through any operation that reads
	from or writes to the framebuffer's stencil buffer.
	

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/framebuffer_object.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.framebuffer_object import *
from OpenGL.raw.GL.ARB.framebuffer_object import _EXTENSION_NAME

def glInitFramebufferObjectARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

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
### END AUTOGENERATED SECTION
from OpenGL.lazywrapper import lazy as _lazy 

@_lazy( glDeleteFramebuffers )
def glDeleteFramebuffers( baseOperation, n, framebuffers=None ):
    """glDeleteFramebuffers( framebuffers ) -> None 
    """
    if framebuffers is None:
        framebuffers = arrays.GLuintArray.asArray( n )
        n = arrays.GLuintArray.arraySize( framebuffers )
    return baseOperation( n, framebuffers )

# Setup the GL_UNSIGNED_INT_24_8 image type
from OpenGL import images
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_UNSIGNED_INT
images.TYPE_TO_ARRAYTYPE[ GL_UNSIGNED_INT_24_8 ] = GL_UNSIGNED_INT
images.TIGHT_PACK_FORMATS[ GL_UNSIGNED_INT_24_8 ] = 4

# The extensions actually use the _EXT forms, which is a bit confusing 
# for users, IMO.
GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS = constant.Constant( 'GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS', 0x8CD9 )
GL_FRAMEBUFFER_INCOMPLETE_FORMATS = constant.Constant( 'GL_FRAMEBUFFER_INCOMPLETE_FORMATS', 0x8CDA )
GL_FRAMEBUFFER_UNSUPPORTED = constant.Constant( 'GL_FRAMEBUFFER_UNSUPPORTED', 0x8CDD )
del images 
del GL_UNSIGNED_INT
