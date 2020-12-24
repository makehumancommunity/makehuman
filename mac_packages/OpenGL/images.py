"""Image/texture implementation code

This module provides the Pan-OpenGL operations required to support OpenGL
image handling.  Most of this code is simply boilerplate code that sets 
OpenGL parameters such that normal Pythonic assumptions about data-ordering
are met to allow easier interaction with other projects (such as PIL or 
Numpy).

Generally speaking, there are 3 pieces of information which control how 
an image is processed in the system:

    format -- this is the pixel format, such as GL_RGB/GL_RED/GL_ABGR_EXT
    dims -- tuple of dimensions for the image, (width,height,depth) order 
    type -- the storage data-type for the image, normally GL_UNSIGNED_BYTE 
        when working in Python, but all of the standard OpenGL types for 
        images can be used if you happen to have your data in some exotic
        format.
    
    OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING -- if this global value is set,
        then read of unsigned byte images using glReadPixels and 
        glGetTexImage produces a string instead of the default array format.

Attributes of Note:

    COMPONENT_COUNTS -- used to lookup how many units of a 
        given storage type are required to store a unit in a given format
    
    TYPE_TO_ARRAYTYPE -- maps Image storage types to their array data-type
        constants, i.e. maps GL_UNSIGNED_SHORT_4_4_4_4 to GL_UNSIGNED_SHORT
        so that we can use the standard array types for manipulating 
        image arrays.
    
    RANK_PACKINGS -- commands required to set up default array-transfer 
        operations for an array of the specified rank.

New image formats and types will need to be registered here to be supported,
this means that extension modules which add image types/formats need to alter 
the tables described above!

    XXX Should be an API to handle that instead of direct modification.

"""
from OpenGL.raw.GL.VERSION import GL_1_1 as _simple
from OpenGL import arrays
from OpenGL import error
from OpenGL import _configflags
import ctypes

def SetupPixelRead( format, dims, type):
    """Setup transfer mode for a read into a numpy array return the array
    
    Calls setupDefaultTransferMode, sets rankPacking and then 
    returns a createTargetArray for the parameters.
    """
    setupDefaultTransferMode()
    # XXX this is wrong? dims may grow or it may not, depends on whether
    # the format can fit in the type or not, but rank is a property of the 
    # image itself?  Don't know, should test.
    rankPacking( len(dims)+1 )
    return createTargetArray( format, dims, type )

def setupDefaultTransferMode( ):
    """Set pixel transfer mode to assumed internal structure of arrays
    
    Basically OpenGL-ctypes (and PyOpenGL) assume that your image data is in 
    non-byte-swapped order, with big-endian ordering of bytes (though that 
    seldom matters in image data).  These assumptions are normally correct 
    when dealing with Python libraries which expose byte-arrays.
    """
    try:
        _simple.glPixelStorei(_simple.GL_PACK_SWAP_BYTES, 0)
        _simple.glPixelStorei(_simple.GL_PACK_LSB_FIRST, 0)
    except error.GLError:
        # GLES doesn't support pixel storage swapping...
        pass
        
def rankPacking( rank ):
    """Set the pixel-transfer modes for a given image "rank" (# of dims)
    
    Uses RANK_PACKINGS table to issue calls to glPixelStorei
    """
    for func,which,arg in RANK_PACKINGS[rank]:
        try:
            func(which,arg)
        except error.GLError:
            pass

def createTargetArray( format, dims, type ):
    """Create storage array for given parameters
    
    If storage type requires > 1 unit per format pixel, then dims will be
    extended by 1, so in the common case of RGB and GL_UNSIGNED_BYTE you 
    will wind up with an array of dims + (3,) dimensions.  See
    COMPONENT_COUNTS for table which controls which formats produce
    larger dimensions.  The secondary table TIGHT_PACK_FORMATS overrides 
    this case, so that image formats registered as TIGHT_PACK_FORMATS
    only ever return a dims-shaped value.  TIGHT_PACK_FORMATS will raise 
    ValueErrors if they are used with a format that does not have the same 
    number of components as they define.
    
    Note that the base storage type must provide a zeros method.  The zeros
    method relies on their being a registered default array-implementation for 
    the storage type.  The default installation of OpenGL-ctypes will use 
    Numpy arrays for returning the result.
    """
    # calculate the number of storage elements required to store 
    # a single pixel of format, that's the dimension of the resulting array
    componentCount = formatToComponentCount( format )
    if componentCount > 1:
        if type not in TIGHT_PACK_FORMATS:
            # requires multiple elements to store a single pixel (common)
            # e.g. byte array (typeBits = 8) with RGB (24) or RGBA (32)
            dims += (componentCount, )
        elif TIGHT_PACK_FORMATS[ type ] < componentCount:
            raise ValueError(
                """Image type: %s supports %s components, but format %s requires %s components"""%(
                    type,
                    TIGHT_PACK_FORMATS[ type ],
                    format,
                    componentCount,
                )
            )
    arrayType = arrays.GL_CONSTANT_TO_ARRAY_TYPE[ TYPE_TO_ARRAYTYPE.get(type,type) ]
    return arrayType.zeros( dims )

def formatToComponentCount( format ):
    """Given an OpenGL image format specification, get components/pixel"""
    size = COMPONENT_COUNTS.get( format )
    if size is None:
        raise ValueError( """Unrecognised image format: %r"""%(format,))
    return size

def returnFormat( data, type ):
    """Perform compatibility conversion for PyOpenGL 2.x image-as string results
    
    Uses OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING to control whether to perform the 
    conversions.
    """
    if _configflags.UNSIGNED_BYTE_IMAGES_AS_STRING:
        if type == _simple.GL_UNSIGNED_BYTE:
            if hasattr( data, 'tostring' ):
                return data.tostring()
            elif hasattr( data, 'raw' ):
                return data.raw 
            elif hasattr( data, '_type_' ):
                s = ctypes.string_at( ctypes.cast( data, ctypes.c_voidp ), ctypes.sizeof( data ))
                result = s[:] # copy into a new string
                return result
    return data


COMPONENT_COUNTS = {
    # Image-format-constant: number-of-components (integer)
}
TYPE_TO_BITS = { 
    # GL-image-storage-type-constant: number-of-bits (integer)
}
TYPE_TO_ARRAYTYPE = { 
    # GL-image-storage-type-constant: GL-datatype (constant)
}
TIGHT_PACK_FORMATS = {
}
RANK_PACKINGS = {
    # rank (integer): list of (function,**arg) to setup for that rank
}
