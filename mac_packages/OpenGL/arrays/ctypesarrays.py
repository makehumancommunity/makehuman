"""ctypes sized data-arrays as a data-formatmechanism

XXX we have to use _ctypes.Array as the type descriminator,
would be nice to have it available from the public module
"""
REGISTRY_NAME = 'ctypesarrays'
import ctypes, _ctypes

from OpenGL.raw.GL import _types
from OpenGL.arrays import _arrayconstants as GL_1_1
from OpenGL import constant
from OpenGL.arrays import formathandler
from OpenGL._bytes import bytes,unicode
import operator

class CtypesArrayHandler( formathandler.FormatHandler ):
    """Ctypes Array-type-specific data-type handler for OpenGL"""
    @classmethod
    def from_param( cls, value, typeCode=None ):
        return ctypes.byref( value )
    dataPointer = staticmethod( ctypes.addressof )
    HANDLED_TYPES = (_ctypes.Array, )
    isOutput = True
    @classmethod
    def voidDataPointer( cls, value ):
        """Given value in a known data-pointer type, return void_p for pointer"""
        return ctypes.byref( value )
    @classmethod
    def zeros( cls, dims, typeCode ):
        """Return Numpy array of zeros in given size"""
        type = GL_TYPE_TO_ARRAY_MAPPING[ typeCode ]
        for dim in dims:
            type *= int(dim)
        return type() # should expicitly set to 0s
    @classmethod
    def ones( cls, dims, typeCode='d' ):
        """Return numpy array of ones in given size"""
        raise NotImplementedError( """Haven't got a good ones implementation yet""" )
##		type = GL_TYPE_TO_ARRAY_MAPPING[ typeCode ]
##		for dim in dims:
##			type *= dim 
##		return type() # should expicitly set to 0s
    @classmethod
    def arrayToGLType( cls, value ):
        """Given a value, guess OpenGL type of the corresponding pointer"""
        result = None
        typ = value._type_
        while hasattr(typ,'_type_') and typ not in ARRAY_TO_GL_TYPE_MAPPING:
            typ = typ._type_
        result = ARRAY_TO_GL_TYPE_MAPPING.get( typ )
        if result is not None:
            return result
        raise TypeError(
            """Don't know GL type for array of type %r, known types: %s\nvalue:%s"""%(
                value._type_, list(ARRAY_TO_GL_TYPE_MAPPING.keys()), value,
            )
        )
    @classmethod
    def arraySize( cls, value, typeCode = None ):
        """Given a data-value, calculate dimensions for the array"""
        try:
            return value.__class__.__component_count__
        except AttributeError as err:
            dims = 1
            for length in cls.dims( value ):
                dims *= length
            value.__class__.__component_count__ = dims
            return dims 
    @classmethod
    def arrayByteCount( cls, value, typeCode = None ):
        """Given a data-value, calculate number of bytes required to represent"""
        return ctypes.sizeof( value )
    @classmethod
    def types( cls, value ):
        """Produce iterable producing all composite types"""
        dimObject = value
        while dimObject is not None:
            yield dimObject
            dimObject = getattr( dimObject, '_type_', None )
            if isinstance( dimObject, (bytes,unicode)):
                dimObject = None 
    @classmethod
    def dims( cls, value ):
        """Produce iterable of all dimensions"""
        try:
            return value.__class__.__dimensions__
        except AttributeError as err:
            dimensions = []
            for base in cls.types( value ):
                length = getattr( base, '_length_', None)
                if length is not None:
                    dimensions.append( length )
            dimensions = tuple( dimensions )
            value.__class__.__dimensions__  = dimensions
            return dimensions
    @classmethod
    def asArray( cls, value, typeCode=None ):
        """Convert given value to an array value of given typeCode"""
        return value
    @classmethod
    def unitSize( cls, value, typeCode=None ):
        """Determine unit size of an array (if possible)"""
        try:
            return value.__class__.__min_dimension__
        except AttributeError as err:
            dim = cls.dims( value )[-1]
            value.__class__.__min_dimension__ = dim
            return dim
    @classmethod
    def dimensions( cls, value, typeCode=None ):
        """Determine dimensions of the passed array value (if possible)"""
        return tuple( cls.dims(value) )


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
    _types.GL_VOID_P: _types.GLvoidp,
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
