'''OpenGL extension APPLE.client_storage

This module customises the behaviour of the 
OpenGL.raw.GL.APPLE.client_storage to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides a simple mechanism to optimize texture data handling
	by clients.  GL implementations normally maintain a copy of texture image
	data supplied clients when any of the various texturing commands, such as
	TexImage2D, are invoked.  This extension eliminates GL's internal copy of
	the texture image data and allows a client to maintain this data locally for
	textures when the UNPACK_CLIENT_STORAGE_APPLE pixel storage parameter is
	TRUE at the time of texture specification.  Local texture data storage is
	especially useful in cases where clients maintain internal copies of
	textures used in any case.  This results in what could be considered an
	extra copy of the texture image data.  Assuming all operations are error
	free, the use of client storage has no affect on the result of texturing
	operations and will not affect rendering results. APPLE_client_storage
	allows clients to optimize memory requirements and copy operations it also
	requires adherence to specific rules in maintaining texture image data.
	
	Clients using this extension are agreeing to preserve a texture's image data
	for the life of the texture.  The life of the texture is defined, in this
	case, as the time from first issuing the TexImage3D, TexImage2D or
	TexImage1D command, for the specific texture object with the
	UNPACK_CLIENT_STORAGE_APPLE pixel storage parameter set to TRUE, until the
	DeleteTextures command or another TexImage command for that same object. 
	Only after DeleteTextures has completed, or new texture is specified, can
	the local texture memory be released, as it will no longer be utilized by
	OpenGL.  Changing the UNPACK_CLIENT_STORAGE_APPLE pixel storage parameter
	will have no additional effect once the texturing command has been issued
	and specifically will not alleviate the client from maintaining the texture
	data.
	
	Client storage is implemented as a pixel storage parameter which affects
	texture image storage at the time the texturing command is issued.  As with
	other pixel storage parameters this state may differ from the time the
	texturing command in executed if the command is placed in a display list. 
	The PixelStore command is used to set the parameter
	UNPACK_CLIENT_STORAGE_APPLE.  Values can either be TRUE or FALSE, with TRUE
	representing the use of client local storage and FALSE indicating the OpenGL
	engine and not the client will be responsible for maintaining texture
	storage for future texturing commands issued per the OpenGL specification.
	The default state for the UNPACK_CLIENT_STORAGE_APPLE parameter is FALSE
	
	Client storage is only available for texture objects and not the default
	texture (of any target type).  This means that a texture object has to
	generated and bound to be used with client storage.  Setting
	UNPACK_CLIENT_STORAGE_APPLE to TRUE and texturing with the default texture
	will result in normally texturing with GL maintaining a copy of the texture
	image data.
	
	Normally, client storage will be used in conjunction with normal texturing
	techniques.  An application would use GenTextures to generate texture
	objects as needed.  BindTexture to the texture object name of interest. 
	Enable client storage via the PixelStore command setting the
	UNPACK_CLIENT_STORAGE_APPLE parameter to TRUE. Then use TexImage3D,
	TexImage2D or TexImage1D to specify the texture image.  If no further use of
	client storage is desired, it is recommended to again use the PixelStore
	command, in this case setting the UNPACK_CLIENT_STORAGE_APPLE parameter to
	FALSE to disable client storage, since this pixel state is maintained unless
	explicitly set by the PixelStore command.
	
	If an application needs to modify the texture, using TexSubImage for
	example, it should be noted that the pointer passed to TexSubImage1D,
	TexSubImage2D or TexSubImage3D does not have to the same, or within the
	original texture memory.  It if is not, there is the likelihood of GL
	copying the new data to the original texture memory owned by the client,
	thus actually modifying this texture image data.  This does not affect
	requirement to maintain the original texture memory but also does not add
	the requirement to maintain the sub image data, due to the copy.
	
	Once a client has completed use of the texture stored in client memory, it
	should issue a DeleteTextures command to delete the texture object or issue
	a texture command, with the same target type, for the object, with either a
	different data pointer, or UNPACK_CLIENT_STORAGE_APPLE set to false, in any
	case, breaking the tie between GL and the texture buffer.  An implicit Flush
	command is issued in these cases, ensuring all access to the texture by
	OpenGL is complete.  Only at this point can the texture buffer be safely
	released.  Releasing the texture buffer prior has undefined results and will
	very possibly display texel anomalies at run time.  System level memory
	management and paging schemes should not affect the use of client storage. 
	Consider in any case, that GL has an alias of the base pointer for this
	block of texture memory which is maintained until GL is finished rendering
	with the texture and it has been deleted or reassigned to another set of
	texture data.  As long as this alias exists, applications must not
	de-allocate, move or purge this memory.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/APPLE/client_storage.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.APPLE.client_storage import *
from OpenGL.raw.GL.APPLE.client_storage import _EXTENSION_NAME

def glInitClientStorageAPPLE():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION