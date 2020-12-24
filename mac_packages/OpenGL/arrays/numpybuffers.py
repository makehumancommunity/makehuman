"""Buffer based Numpy plugin (not used)

This API is no more useful than the direct Numpy version, as Numpy already 
gives us the details we need *when using the accelerator module* at a low 
level, with very fast access.  When using the non-accelerated version the 
ctypes version *might* show some performance benefits, but it's not going 
to be fast no matter what we do without C-level code.
"""
REGISTRY_NAME = 'numpybuffers'
import operator
try:
    import numpy
except ImportError as err:
    raise ImportError( """No numpy module present: %s"""%(err))
from OpenGL.arrays import buffers
from OpenGL.raw.GL import _types 
from OpenGL.raw.GL.VERSION import GL_1_1
from OpenGL import constant, error
class NumpyHandler( buffers.BufferHandler ):
    @classmethod
    def zeros( cls, dims, typeCode ):
        """Return Numpy array of zeros in given size"""
        return numpy.zeros( dims, GL_TYPE_TO_ARRAY_MAPPING[typeCode])
    
    @classmethod
    def asArray( cls, value, typeCode=None ):
        """Convert given value to an array value of given typeCode"""
        return super(NumpyHandler,cls).asArray( cls.contiguous(value,typeCode), typeCode )
    @classmethod
    def contiguous( cls, source, typeCode=None ):
        """Get contiguous array from source

        source -- numpy Python array (or compatible object)
            for use as the data source.  If this is not a contiguous
            array of the given typeCode, a copy will be made,
            otherwise will just be returned unchanged.
        typeCode -- optional 1-character typeCode specifier for
            the numpy.array function.

        All gl*Pointer calls should use contiguous arrays, as non-
        contiguous arrays will be re-copied on every rendering pass.
        Although this doesn't raise an error, it does tend to slow
        down rendering.
        """
        typeCode = GL_TYPE_TO_ARRAY_MAPPING[ typeCode ]
        try:
            contiguous = source.flags.contiguous
        except AttributeError as err:
            if typeCode:
                return numpy.ascontiguousarray( source, typeCode )
            else:
                return numpy.ascontiguousarray( source )
        else:
            if contiguous and (typeCode is None or typeCode==source.dtype.char):
                return source
            elif (contiguous and cls.ERROR_ON_COPY):
                from OpenGL import error
                raise error.CopyError(
                    """Array of type %r passed, required array of type %r""",
                    source.dtype.char, typeCode,
                )
            else:
                # We have to do astype to avoid errors about unsafe conversions
                # XXX Confirm that this will *always* create a new contiguous array
                # XXX Guard against wacky conversion types like uint to float, where
                # we really don't want to have the C-level conversion occur.
                # XXX ascontiguousarray is apparently now available in numpy!
                if cls.ERROR_ON_COPY:
                    from OpenGL import error
                    raise error.CopyError(
                        """Non-contiguous array passed""",
                        source,
                    )
                if typeCode is None:
                    typeCode = source.dtype.char
                return numpy.ascontiguousarray( source, typeCode )
try:
    numpy.array( [1], 's' )
    SHORT_TYPE = 's'
except TypeError as err:
    SHORT_TYPE = 'h'
    USHORT_TYPE = 'H'

def lookupDtype( char ):
    return numpy.zeros( (1,), dtype=char ).dtype

ARRAY_TO_GL_TYPE_MAPPING = {
    lookupDtype('d'): GL_1_1.GL_DOUBLE,
    lookupDtype('f'): GL_1_1.GL_FLOAT,
    lookupDtype('i'): GL_1_1.GL_INT,
    lookupDtype(SHORT_TYPE): GL_1_1.GL_SHORT,
    lookupDtype(USHORT_TYPE): GL_1_1.GL_UNSIGNED_SHORT,
    lookupDtype('B'): GL_1_1.GL_UNSIGNED_BYTE,
    lookupDtype('c'): GL_1_1.GL_UNSIGNED_BYTE,
    lookupDtype('b'): GL_1_1.GL_BYTE,
    lookupDtype('I'): GL_1_1.GL_UNSIGNED_INT,
    #lookupDtype('P'), GL_1_1.GL_VOID_P, # normally duplicates another type (e.g. 'I')
    None: None,
}
GL_TYPE_TO_ARRAY_MAPPING = {
    GL_1_1.GL_DOUBLE: lookupDtype('d'),
    GL_1_1.GL_FLOAT:lookupDtype('f'),
    GL_1_1.GL_INT: lookupDtype('i'),
    GL_1_1.GL_BYTE: lookupDtype('b'),
    GL_1_1.GL_SHORT: lookupDtype(SHORT_TYPE),
    GL_1_1.GL_UNSIGNED_INT: lookupDtype('I'),
    GL_1_1.GL_UNSIGNED_BYTE: lookupDtype('B'),
    GL_1_1.GL_UNSIGNED_SHORT: lookupDtype(USHORT_TYPE),
    _types.GL_VOID_P: lookupDtype('P'),
    None: None,
    'f': lookupDtype('f'),
    'd': lookupDtype('d'),
    'i': lookupDtype('i'),
    'I': lookupDtype('I'),
    'h': lookupDtype('h'),
    'H': lookupDtype('H'),
    'b': lookupDtype('b'),
    'B': lookupDtype('B'),
    's': lookupDtype('B'),
}
