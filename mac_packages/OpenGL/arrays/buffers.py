#! /usr/bin/env python
"""Test for a buffer-protocol-based access mechanism

Will *only* work for Python 2.6+, and pretty much just works for strings
under 2.6 (in terms of the common object types).
"""
import sys,operator,logging,traceback
from OpenGL.arrays import _buffers
from OpenGL.raw.GL import _types
#from OpenGL.raw.GL.VERSION import GL_1_1
from OpenGL.arrays import formathandler
from OpenGL import _configflags
from OpenGL import acceleratesupport
_log = logging.getLogger( __name__ )
try:
    reduce 
except NameError as err:
    from functools import reduce

MemoryviewHandler = BufferHandler = None
if sys.version_info[:2] > (2,6):
    # Only Python 2.7+ has memoryview support, and the accelerate module 
    # requires memoryviews to be able to pass around the buffer structures
    if acceleratesupport.ACCELERATE_AVAILABLE:
        try:
            from OpenGL_accelerate.buffers_formathandler import MemoryviewHandler
        except ImportError as err:
            traceback.print_exc()
            _log.warning(
                "Unable to load buffers_formathandler accelerator from OpenGL_accelerate"
            )
        else:
            BufferHandler = MemoryviewHandler
if not BufferHandler:
    class BufferHandler( formathandler.FormatHandler ):
        """Buffer-protocol data-type handler for OpenGL"""
        isOutput=False
        ERROR_ON_COPY = _configflags.ERROR_ON_COPY
        if sys.version_info[0] >= 3:
            @classmethod
            def from_param( cls, value, typeCode=None ):
                if not isinstance( value, _buffers.Py_buffer ):
                    value = cls.asArray( value )
                    #raise TypeError( """Can't convert value to py-buffer in from_param""" )
                # TODO: only do this IFF value.internal is None
                return _types.GLvoidp( value.buf )
#                return value
        else:
            @classmethod
            def from_param( cls, value, typeCode=None ):
                if not isinstance( value, _buffers.Py_buffer ):
                    value = cls.asArray( value )
                    #raise TypeError( """Can't convert value to py-buffer in from_param""" )
                return value.buf
        def dataPointer( value ):
            if not isinstance( value, _buffers.Py_buffer ):
                value = _buffers.Py_buffer.from_object( value )
            return value.buf
        dataPointer = staticmethod( dataPointer )
        @classmethod
        def zeros( cls, dims, typeCode=None ):
            """Currently don't allow strings as output types!"""
            raise NotImplementedError( "Generic buffer type does not have output capability" )
            return cls.asArray( bytearray( b'\000'*reduce(operator.mul,dims)*BYTE_SIZES[typeCode] ) )
        @classmethod
        def ones( cls, dims, typeCode=None ):
            """Currently don't allow strings as output types!"""
            raise NotImplementedError( """Have not implemented ones for buffer type""" )
        @classmethod
        def arrayToGLType( cls, value ):
            """Given a value, guess OpenGL type of the corresponding pointer"""
            format = value.format 
            if format in ARRAY_TO_GL_TYPE_MAPPING:
                return ARRAY_TO_GL_TYPE_MAPPING[format]
            raise TypeError( 'Unknown format: %r'%(format,))
        @classmethod
        def arraySize( cls, value, typeCode = None ):
            """Given a data-value, calculate ravelled size for the array"""
            return value.len // value.itemsize
        @classmethod
        def arrayByteCount( cls, value, typeCode = None ):
            """Given a data-value, calculate number of bytes required to represent"""
            return value.len
        @classmethod 
        def unitSize( cls, value, default=None ):
            return value.dims[-1]
        @classmethod
        def asArray( cls, value, typeCode=None ):
            """Convert given value to an array value of given typeCode"""
            buf = _buffers.Py_buffer.from_object( value )
            return buf
        @classmethod
        def dimensions( cls, value, typeCode=None ):
            """Determine dimensions of the passed array value (if possible)"""
            return value.dims

ARRAY_TO_GL_TYPE_MAPPING = _buffers.ARRAY_TO_GL_TYPE_MAPPING
BYTE_SIZES = _buffers.BYTE_SIZES
