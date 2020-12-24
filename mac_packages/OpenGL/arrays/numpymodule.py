"""Numpy (new version) module implementation of the OpenGL-ctypes array interfaces

XXX Need to register handlers for all of the scalar types that numpy returns,
would like to have all return values be int/float if they are of  compatible
type as well.
"""
REGISTRY_NAME = 'numpy'
import logging
from OpenGL import _configflags
_log = logging.getLogger( __name__ )
try:
    import numpy
except ImportError as err:
    raise ImportError( """No numpy module present: %s"""%(err))
import OpenGL
assert OpenGL
import ctypes
from OpenGL._bytes import long
from OpenGL.raw.GL import _types 
from OpenGL.raw.GL.VERSION import GL_1_1
from OpenGL import error
from OpenGL.arrays import formathandler
c_void_p = ctypes.c_void_p
from OpenGL import acceleratesupport
NumpyHandler = None
if acceleratesupport.ACCELERATE_AVAILABLE:
    try:
        from OpenGL_accelerate.numpy_formathandler import NumpyHandler
    except ImportError as err:
        _log.warning(
            "Unable to load numpy_formathandler accelerator from OpenGL_accelerate"
        )
if NumpyHandler is None:
    # numpy's array interface has changed over time :(
    testArray = numpy.array( [1,2,3,4],'i' )
    # Numpy's "ctypes" interface actually creates a new ctypes object
    # in python for every access of the .ctypes attribute... which can take
    # ridiculously large periods when you multiply it by millions of iterations
    if hasattr(testArray,'__array_interface__'):
        def dataPointer( cls, instance ):
            """Convert given instance to a data-pointer value (integer)"""
            try:
                return long(instance.__array_interface__['data'][0])
            except AttributeError:
                instance = cls.asArray( instance )
                try:
                    return long(instance.__array_interface__['data'][0])
                except AttributeError:
                    return long(instance.__array_data__[0],0)
    else:
        def dataPointer( cls, instance ):
            """Convert given instance to a data-pointer value (integer)"""
            try:
                return long(instance.__array_data__[0],0)
            except AttributeError:
                instance = cls.asArray( instance )
                try:
                    return long(instance.__array_interface__['data'][0])
                except AttributeError:
                    return long(instance.__array_data__[0],0)
    try:
        del testArray
    except NameError as err:
        pass
    dataPointer = classmethod( dataPointer )


    class NumpyHandler( formathandler.FormatHandler ):
        """Numpy-specific data-type handler for OpenGL

        Attributes:

            ERROR_ON_COPY -- if True, will raise errors
                if we have to copy an array object in order to produce
                a contiguous array of the correct type.
        """
        HANDLED_TYPES = (
            numpy.ndarray,
            numpy.bool_,
            numpy.intc, 
            numpy.uintc,
            numpy.int8,
            numpy.uint8,
            numpy.int16,
            numpy.uint16,
            numpy.int32,
            numpy.uint32,
            numpy.int64,
            numpy.uint64,
            numpy.int64,
            numpy.uint64,
            numpy.float16,
            numpy.float32,
            numpy.float64,
            numpy.complex64,
            numpy.complex128,
            numpy.bytes_,
            numpy.str_,
            numpy.void,
            numpy.datetime64,
            numpy.timedelta64,
        )# list, tuple )
        if hasattr(numpy,'float128'):
            HANDLED_TYPES += (numpy.float128,)
        if hasattr(numpy,'complex256'):
            HANDLED_TYPES += (numpy.complex256,)
        dataPointer = dataPointer
        isOutput = True
        ERROR_ON_COPY = _configflags.ERROR_ON_COPY
        @classmethod
        def zeros( cls, dims, typeCode ):
            """Return Numpy array of zeros in given size"""
            dims = numpy.array( dims, dtype='i')
            return numpy.zeros( dims, GL_TYPE_TO_ARRAY_MAPPING[typeCode])
        @classmethod
        def arrayToGLType( cls, value ):
            """Given a value, guess OpenGL type of the corresponding pointer"""
            typeCode = value.dtype
            constant = ARRAY_TO_GL_TYPE_MAPPING.get( typeCode )
            if constant is None:
                raise TypeError(
                    """Don't know GL type for array of type %r, known types: %s\nvalue:%s"""%(
                        typeCode, list(ARRAY_TO_GL_TYPE_MAPPING.keys()), value,
                    )
                )
            return constant

        @classmethod
        def arraySize( cls, value, typeCode = None ):
            """Given a data-value, calculate dimensions for the array"""
            return value.size
        @classmethod
        def arrayByteCount( cls, value, typeCode = None ):
            """Given a data-value, calculate number of bytes required to represent"""
            try:
                return value.nbytes
            except AttributeError:
                if cls.ERROR_ON_COPY:
                    raise error.CopyError(
                        """Non-numpy array passed to numpy arrayByteCount: %s""",
                        type(value),
                    )
                value = cls.asArray( value, typeCode )
                return value.nbytes
        @classmethod
        def asArray( cls, value, typeCode=None ):
            """Convert given value to an array value of given typeCode"""
            if value is None:
                return value
            else:
                return cls.contiguous( value, typeCode )

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
            except AttributeError:
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
        @classmethod
        def unitSize( cls, value, typeCode=None ):
            """Determine unit size of an array (if possible)"""
            return value.shape[-1]
        @classmethod
        def dimensions( cls, value, typeCode=None ):
            """Determine dimensions of the passed array value (if possible)"""
            return value.shape
        @classmethod
        def from_param( cls, instance, typeCode=None ):
            try:
                pointer = cls.dataPointer( instance )
            except TypeError:
                array = cls.asArray( instance, typeCode )
                pp = cls.dataPointer( array )
                pp._temporary_array_ = (array,)
                return pp
            else:
                if typeCode and instance.dtype != GL_TYPE_TO_ARRAY_MAPPING[ typeCode ]:
                    raise error.CopyError(
                        """Array of type %r passed, required array of type %r""",
                        instance.dtype.char, typeCode,
                    )
                return c_void_p( pointer )

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
    #lookupDtype('P'), _types.GL_VOID_P, # normally duplicates another type (e.g. 'I')
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
