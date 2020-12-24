"""String-array-handling code for PyOpenGL
"""
from OpenGL.raw.GL import _types 
from OpenGL.raw.GL.VERSION import GL_1_1
from OpenGL.arrays import formathandler
import ctypes
from OpenGL import _bytes, error
from OpenGL._configflags import ERROR_ON_COPY

def dataPointer( value, typeCode=None ):
    return ctypes.cast(ctypes.c_char_p(value),
                           ctypes.c_void_p).value

class StringHandler( formathandler.FormatHandler ):
    """String-specific data-type handler for OpenGL"""
    HANDLED_TYPES = (_bytes.bytes, )
    @classmethod
    def from_param( cls, value, typeCode=None ):
        return ctypes.c_void_p( dataPointer( value ) )
    dataPointer = staticmethod( dataPointer )
    def zeros( self, dims, typeCode=None ):
        """Currently don't allow strings as output types!"""
        raise NotImplemented( """Don't currently support strings as output arrays""" )
    def ones( self, dims, typeCode=None ):
        """Currently don't allow strings as output types!"""
        raise NotImplemented( """Don't currently support strings as output arrays""" )
    def arrayToGLType( self, value ):
        """Given a value, guess OpenGL type of the corresponding pointer"""
        raise NotImplemented( """Can't guess data-type from a string-type argument""" )
    def arraySize( self, value, typeCode = None ):
        """Given a data-value, calculate ravelled size for the array"""
        # need to get bits-per-element...
        byteCount = BYTE_SIZES[ typeCode ]
        return len(value)//byteCount
    def arrayByteCount( self, value, typeCode = None ):
        """Given a data-value, calculate number of bytes required to represent"""
        return len(value)
    def asArray( self, value, typeCode=None ):
        """Convert given value to an array value of given typeCode"""
        if isinstance( value, bytes ):
            return value
        elif hasattr( value, 'tostring' ):
            return value.tostring()
        elif hasattr( value, 'raw' ):
            return value.raw
        # could convert types to string here, but we're not registered for
        # anything save string types...
        raise TypeError( """String handler got non-string object: %r"""%(type(value)))
    def dimensions( self, value, typeCode=None ):
        """Determine dimensions of the passed array value (if possible)"""
        raise TypeError(
            """Cannot calculate dimensions for a String data-type"""
        )

class UnicodeHandler( StringHandler ):
    HANDLED_TYPES = (_bytes.unicode,)
    @classmethod
    def from_param( cls, value, typeCode=None ):
        # TODO: raise CopyError if the flag is set!
        converted = _bytes.as_8_bit( value )
        result = StringHandler.from_param( converted )
        if converted is not value:
            if ERROR_ON_COPY:
                raise error.CopyError(
                    """Unicode string passed, cannot copy with ERROR_ON_COPY set, please use 8-bit strings"""
                )
            result._temporary_array_ = converted 
        return result
    def asArray( self, value, typeCode=None ):
        value = _bytes.as_8_bit( value )
        return StringHandler.asArray( self, value, typeCode=typeCode )


BYTE_SIZES = {
    GL_1_1.GL_DOUBLE: ctypes.sizeof( _types.GLdouble ),
    GL_1_1.GL_FLOAT: ctypes.sizeof( _types.GLfloat ),
    GL_1_1.GL_INT: ctypes.sizeof( _types.GLint ),
    GL_1_1.GL_SHORT: ctypes.sizeof( _types.GLshort ),
    GL_1_1.GL_UNSIGNED_BYTE: ctypes.sizeof( _types.GLubyte ),
    GL_1_1.GL_UNSIGNED_SHORT: ctypes.sizeof( _types.GLshort ),
    GL_1_1.GL_BYTE: ctypes.sizeof( _types.GLbyte ),
    GL_1_1.GL_UNSIGNED_INT: ctypes.sizeof( _types.GLuint ),
}
