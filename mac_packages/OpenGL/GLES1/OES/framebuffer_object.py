'''OpenGL extension OES.framebuffer_object

This module customises the behaviour of the 
OpenGL.raw.GLES1.OES.framebuffer_object to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension defines a simple interface for drawing to rendering
	destinations other than the buffers provided to the GL by the
	window-system.  OES_framebuffer_object is a simplified version
	of EXT_framebuffer_object with modifications to match the needs of 
	OpenGL ES.
	
	In this extension, these newly defined rendering destinations are
	known collectively as "framebuffer-attachable images".  This
	extension provides a mechanism for attaching framebuffer-attachable
	images to the GL framebuffer as one of the standard GL logical
	buffers: color, depth, and stencil.  When a framebuffer-attachable 
	image is attached to the framebuffer, it is used as the source and
	destination of fragment operations as described in Chapter 4.
	
	By allowing the use of a framebuffer-attachable image as a rendering
	destination, this extension enables a form of "offscreen" rendering.
	Furthermore, "render to texture" is supported by allowing the images
	of a texture to be used as framebuffer-attachable images.  A
	particular image of a texture object is selected for use as a
	framebuffer-attachable image by specifying the mipmap level, cube
	map face (for a cube map texture) that identifies the image.  
	The "render to texture" semantics of this extension are similar to 
	performing traditional rendering to the framebuffer, followed 
	immediately by a call to CopyTexSubImage.  However, by using this 
	extension instead, an application can achieve the same effect, 
	but with the advantage that the GL can usually eliminate the data copy 
	that would have been incurred by calling CopyTexSubImage.
	
	This extension also defines a new GL object type, called a
	"renderbuffer", which encapsulates a single 2D pixel image.  The
	image of renderbuffer can be used as a framebuffer-attachable image
	for generalized offscreen rendering and it also provides a means to
	support rendering to GL logical buffer types which have no
	corresponding texture format (stencil, etc).  A renderbuffer
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
	APIs would also provide a function (i.e., eglMakeCurrent) to bind a 
	drawable with a GL context.  In this extension, however, this 
	functionality is subsumed by the GL and the GL provides the function 
	BindFramebufferOES to bind a framebuffer object to the current context.  
	Later, the context can bind back to the window-system-provided framebuffer 
	in order to display rendered content.
	
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
	
	OES_framebuffer_object, on the other hand, is both simpler to use
	and more efficient than ARB_render_texture.  The
	OES_framebuffer_object API is contained wholly within the GL API and
	has no (non-portable) window-system components.  Under
	OES_framebuffer_object, it is not necessary to create a second GL
	context when rendering to a texture image whose format differs from
	that of the window.  Finally, unlike the pbuffers of
	ARB_render_texture, a single framebuffer object can facilitate
	rendering to an unlimited number of texture objects.
	
	Please refer to the EXT_framebuffer_object extension for a 
	detailed explaination of how framebuffer objects are supposed to work,
	the issues and their resolution.  This extension can be found at
	http://oss.sgi.com/projects/ogl-sample/registry/EXT/framebuffer_object.txt

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/OES/framebuffer_object.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES1 import _types, _glgets
from OpenGL.raw.GLES1.OES.framebuffer_object import *
from OpenGL.raw.GLES1.OES.framebuffer_object import _EXTENSION_NAME

def glInitFramebufferObjectOES():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDeleteRenderbuffersOES.renderbuffers size not checked against n
glDeleteRenderbuffersOES=wrapper.wrapper(glDeleteRenderbuffersOES).setInputArraySize(
    'renderbuffers', None
)
# INPUT glGenRenderbuffersOES.renderbuffers size not checked against n
glGenRenderbuffersOES=wrapper.wrapper(glGenRenderbuffersOES).setInputArraySize(
    'renderbuffers', None
)
# INPUT glGetRenderbufferParameterivOES.params size not checked against 'pname'
glGetRenderbufferParameterivOES=wrapper.wrapper(glGetRenderbufferParameterivOES).setInputArraySize(
    'params', None
)
# INPUT glDeleteFramebuffersOES.framebuffers size not checked against n
glDeleteFramebuffersOES=wrapper.wrapper(glDeleteFramebuffersOES).setInputArraySize(
    'framebuffers', None
)
# INPUT glGenFramebuffersOES.framebuffers size not checked against n
glGenFramebuffersOES=wrapper.wrapper(glGenFramebuffersOES).setInputArraySize(
    'framebuffers', None
)
# INPUT glGetFramebufferAttachmentParameterivOES.params size not checked against 'pname'
glGetFramebufferAttachmentParameterivOES=wrapper.wrapper(glGetFramebufferAttachmentParameterivOES).setInputArraySize(
    'params', None
)
### END AUTOGENERATED SECTION