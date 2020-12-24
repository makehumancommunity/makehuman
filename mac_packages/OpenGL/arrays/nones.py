"""Passing of None as an array data-type
"""
REGISTRY_NAME = 'nones'
import logging
_log = logging.getLogger( 'OpenGL.arrays.nones' )

from OpenGL import acceleratesupport
NoneHandler = None
if acceleratesupport.ACCELERATE_AVAILABLE:
    try:
        from OpenGL_accelerate.nones_formathandler import NoneHandler
    except ImportError as err:
        _log.warning(
            "Unable to load nones_formathandler accelerator from OpenGL_accelerate"
        )
if NoneHandler is None:
    from OpenGL.arrays import formathandler
    class NoneHandler( formathandler.FormatHandler ):
        """Numpy-specific data-type handler for OpenGL"""
        HANDLED_TYPES = (type(None), )
        def from_param( self, value, typeCode=None  ):
            """Convert to a ctypes pointer value"""
            return None
        def dataPointer( self, value ):
            """return long for pointer value"""
            return None
        def voidDataPointer( cls, value ):
            """Given value in a known data-pointer type, return void_p for pointer"""
            return None
        def asArray( self, value, typeCode=None ):
            """Given a value, convert to array representation"""
            return None
        def arrayToGLType( self, value ):
            """Given a value, guess OpenGL type of the corresponding pointer"""
            raise TypeError( """Can't guess type of a NULL pointer""" )
        def arraySize( self, value, typeCode = None ):
            """Given a data-value, calculate dimensions for the array"""
            return 0
        def arrayByteCount( self, value, typeCode = None ):
            """Given a data-value, calculate number of bytes required to represent"""
            return 0
        def zeros( self, shape, typeCode= None ):
            """Create an array of given shape with given typeCode"""
            raise TypeError( """Can't create NULL pointer filled with values""" )
        def ones( self, shape, typeCode= None ):
            """Create an array of given shape with given typeCode"""
            raise TypeError( """Can't create NULL pointer filled with values""" )
        def unitSize( self, value, typeCode=None ):
            """Determine unit size of an array (if possible)"""
            raise TypeError( """Can't determine unit size of a null pointer""" )
        def dimensions( self, value, typeCode=None ):
            """Determine dimensions of the passed array value (if possible)"""
            return (0,)
