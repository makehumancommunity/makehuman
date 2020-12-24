"""ctypes data-pointers as a data-format mechanism
"""
REGISTRY_NAME = 'ctypespointers'
import ctypes, _ctypes
from OpenGL.raw.GL import _types 
from OpenGL.arrays import _arrayconstants as GL_1_1
from OpenGL import constant
from OpenGL.arrays import formathandler
import operator

class CtypesPointerHandler( formathandler.FormatHandler ):
    """Ctypes Pointer-type-specific data-type handler for OpenGL
    
    Because pointers do not have size information we can't use
    them for output of data, but they can be used for certain
    types of input...
    """
    @classmethod
    def from_param( cls, value, typeCode=None  ):
        return value
    @classmethod
    def dataPointer( cls, value ):
        return value.value
    HANDLED_TYPES = (ctypes._Pointer, )
    isOutput=False
    def voidDataPointer( cls, value ):
        """Given value in a known data-pointer type, return void_p for pointer"""
        return ctypes.cast( value, ctypes.c_void_p )
    def zeros( self, dims, typeCode ):
        """Return Numpy array of zeros in given size"""
        raise NotImplementedError( """Sized output doesn't yet work...""" )
    def ones( self, dims, typeCode='d' ):
        """Return numpy array of ones in given size"""
        raise NotImplementedError( """Haven't got a good ones implementation yet""" )
    def arrayToGLType( self, value ):
        """Given a value, guess OpenGL type of the corresponding pointer"""
        result = ARRAY_TO_GL_TYPE_MAPPING.get( value._type_ )
        if result is not None:
            return result
        raise TypeError(
            """Don't know GL type for array of type %r, known types: %s\nvalue:%s"""%(
                value._type_, list(ARRAY_TO_GL_TYPE_MAPPING.keys()), value,
            )
        )
    def arraySize( self, value, typeCode = None ):
        """Given a data-value, calculate dimensions for the array"""
        raise NotImplementedError( """Haven't got an arraySize implementation""" )
    def asArray( self, value, typeCode=None ):
        """Convert given value to an array value of given typeCode"""
        return value
    def unitSize( self, value, typeCode=None ):
        """Determine unit size of an array (if possible)"""
        return 1
    def dimensions( self, value, typeCode=None ):
        """Determine dimensions of the passed array value (if possible)"""
        raise NotImplementedError( """Haven't got a dimensions implementation""" )


ARRAY_TO_GL_TYPE_MAPPING = {
    _types.GLdouble: GL_1_1.GL_DOUBLE,
    _types.GLfloat: GL_1_1.GL_FLOAT,
    _types.GLint: GL_1_1.GL_INT,
    _types.GLuint: GL_1_1.GL_UNSIGNED_INT,
    _types.GLshort: GL_1_1.GL_SHORT,
    _types.GLushort: GL_1_1.GL_UNSIGNED_SHORT,
        
    _types.GLchar: GL_1_1.GL_CHAR,
    _types.GLbyte: GL_1_1.GL_BYTE,
    _types.GLubyte: GL_1_1.GL_UNSIGNED_BYTE,
}
GL_TYPE_TO_ARRAY_MAPPING = {
    GL_1_1.GL_DOUBLE: _types.GLdouble,
    GL_1_1.GL_FLOAT: _types.GLfloat,
    GL_1_1.GL_INT: _types.GLint,
    GL_1_1.GL_UNSIGNED_INT: _types.GLuint,
    GL_1_1.GL_SHORT: _types.GLshort,
    GL_1_1.GL_UNSIGNED_SHORT: _types.GLushort,
        
    GL_1_1.GL_CHAR: _types.GLchar,
    GL_1_1.GL_BYTE: _types.GLbyte,
    GL_1_1.GL_UNSIGNED_BYTE: _types.GLubyte,
    'f': _types.GLfloat,
    'd': _types.GLdouble,
    'i': _types.GLint,
    'I': _types.GLuint,
    'h': _types.GLshort,
    'H': _types.GLushort,
    'b': _types.GLbyte,
    'B': _types.GLubyte,
    's': _types.GLchar,
}
