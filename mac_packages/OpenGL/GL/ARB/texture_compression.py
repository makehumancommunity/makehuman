'''OpenGL extension ARB.texture_compression

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.texture_compression to provide a more 
Python-friendly API

Overview (from the spec)
	
	Compressing texture images can reduce texture memory utilization and
	improve performance when rendering textured primitives.  This extension
	allows OpenGL applications to use compressed texture images by providing:
	
	    (1) A framework upon which extensions providing specific compressed
	        image formats can be built.
	
	    (2) A set of generic compressed internal formats that allow
	        applications to specify that texture images should be stored in
	        compressed form without needing to code for specific compression
	        formats.
	
	An application can define compressed texture images by providing a texture
	image stored in a specific compressed image format.  This extension does
	not define any specific compressed image formats, but it does provide the
	mechanisms necessary to enable other extensions that do.
	
	An application can also define compressed texture images by providing an
	uncompressed texture image but specifying a compressed internal format.
	In this case, the GL will automatically compress the texture image using
	the appropriate image format.  Compressed internal formats can either be
	specific (as above) or generic.  Generic compressed internal formats are
	not actual image formats, but are instead mapped into one of the specific
	compressed formats provided by the GL (or to an uncompressed base internal
	format if no appropriate compressed format is available).  Generic
	compressed internal formats allow applications to use texture compression
	without needing to code to any particular compression algorithm.  Generic
	compressed formats allow the use of texture compression across a wide
	range of platforms with differing compression algorithms and also allow
	future GL implementations to substitute improved compression methods
	transparently.
	
	Compressed texture images can be obtained from the GL in uncompressed form
	by calling GetTexImage and in compressed form by calling
	GetCompressedTexImageARB.  Queried compressed images can be saved and
	later reused by calling CompressedTexImage[123]DARB.  Pre-compressed
	texture images do not need to be processed by the GL and should
	significantly improve texture loading performance relative to uncompressed
	images.
	
	This extension does not define specific compressed image formats (e.g.,
	S3TC, FXT1), nor does it provide means to encode or decode such images.
	To support images in a specific compressed format, a hardware vendor
	would:
	
	  (1) Provide a new extension defininig specific compressed
	      <internalformat> and <format> tokens for TexImage[123]D,
	      TexSubImage[123]D, CopyTexImage[12]D, CompressedTexImage[123]DARB,
	      CompressedTexSubImage[123]DARB, and GetCompressedTexImageARB calls.
	
	  (2) Specify the encoding of compressed images of that specific format.
	
	  (3) Specify a method for deriving the size of compressed images of that
	      specific format, using the <internalformat>, <width>, <height>,
	      <depth> parameters, and (if necessary) the compressed image itself.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/texture_compression.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.texture_compression import *
from OpenGL.raw.GL.ARB.texture_compression import _EXTENSION_NAME

def glInitTextureCompressionARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glCompressedTexImage3DARB.data size not checked against imageSize
glCompressedTexImage3DARB=wrapper.wrapper(glCompressedTexImage3DARB).setInputArraySize(
    'data', None
)
# INPUT glCompressedTexImage2DARB.data size not checked against imageSize
glCompressedTexImage2DARB=wrapper.wrapper(glCompressedTexImage2DARB).setInputArraySize(
    'data', None
)
# INPUT glCompressedTexImage1DARB.data size not checked against imageSize
glCompressedTexImage1DARB=wrapper.wrapper(glCompressedTexImage1DARB).setInputArraySize(
    'data', None
)
# INPUT glCompressedTexSubImage3DARB.data size not checked against imageSize
glCompressedTexSubImage3DARB=wrapper.wrapper(glCompressedTexSubImage3DARB).setInputArraySize(
    'data', None
)
# INPUT glCompressedTexSubImage2DARB.data size not checked against imageSize
glCompressedTexSubImage2DARB=wrapper.wrapper(glCompressedTexSubImage2DARB).setInputArraySize(
    'data', None
)
# INPUT glCompressedTexSubImage1DARB.data size not checked against imageSize
glCompressedTexSubImage1DARB=wrapper.wrapper(glCompressedTexSubImage1DARB).setInputArraySize(
    'data', None
)
# OUTPUT glGetCompressedTexImageARB.img COMPSIZE(target, level) 
### END AUTOGENERATED SECTION
from OpenGL.GL import images

for dimensions in (1,2,3):
    for function in ('glCompressedTexImage%sDARB','glCompressedTexSubImage%sDARB'):
        name = function%(dimensions,)
        globals()[ name ] = images.compressedImageFunction(
            globals()[ name ]
        )
        try:
            del name, function
        except NameError as err:
            pass
    try:
        del dimensions
    except NameError as err:
        pass

if glGetCompressedTexImageARB:
    def glGetCompressedTexImageARB( target, level, img=None ):
        """Retrieve a compressed texture image"""
        if img is None:
            length = glget.glGetTexLevelParameteriv(
                target, 0,
                GL_TEXTURE_COMPRESSED_IMAGE_SIZE_ARB,
            )
            img = arrays.ArrayDataType.zeros( (length,), GL_1_0.GL_UNSIGNED_BYTE )
        return glGetCompressedTexImageARB(target, 0, img);
