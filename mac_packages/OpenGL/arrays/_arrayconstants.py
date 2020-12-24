import ctypes
from OpenGL.constant import Constant
from OpenGL._bytes import bytes,unicode,as_8_bit, long
from OpenGL._opaque import opaque_pointer_cls as _opaque_pointer_cls
sizeof = ctypes.sizeof

GL_FALSE = Constant( 'GL_FALSE', 0x0 )
GL_TRUE = Constant( 'GL_TRUE', 0x1 )
GL_BYTE = Constant( 'GL_BYTE', 0x1400 )
GL_UNSIGNED_BYTE = Constant( 'GL_UNSIGNED_BYTE', 0x1401 )
GL_SHORT = Constant( 'GL_SHORT', 0x1402 )
GL_UNSIGNED_SHORT = Constant( 'GL_UNSIGNED_SHORT', 0x1403 )
GL_INT = Constant( 'GL_INT', 0x1404 )
GL_UNSIGNED_INT = Constant( 'GL_UNSIGNED_INT', 0x1405 )
GL_UNSIGNED_INT64 = Constant( 'GL_UNSIGNED_INT64_AMD', 0x8BC2 )
GL_FLOAT = Constant( 'GL_FLOAT', 0x1406 )
GL_DOUBLE = Constant( 'GL_DOUBLE', 0x140a )
GL_CHAR = bytes
GL_HALF_FLOAT = Constant( 'GL_HALF_FLOAT_ARB',0x140B)
GL_HALF_NV = Constant( 'GL_HALF_NV', 0x1401 )
GL_VOID_P = object()

BYTE_SIZES = {
    GL_BYTE: 1,
    GL_CHAR: 1,
    GL_UNSIGNED_BYTE: 1,
    GL_SHORT: 2,
    GL_UNSIGNED_SHORT: 2,
    GL_INT: 4,
    GL_UNSIGNED_INT: 4,
    GL_UNSIGNED_INT64: 8,
    GL_FLOAT: 4,
    GL_DOUBLE: 8,
}

ARRAY_TO_GL_TYPE_MAPPING = {
    'c': GL_UNSIGNED_BYTE,
    'f': GL_FLOAT,
    'b': GL_BYTE,
    'i': GL_INT,
    'l': GL_INT,
    '?': GL_INT,# Boolean 
    'd': GL_DOUBLE,
    'L': GL_UNSIGNED_INT,
    'h': GL_SHORT,
    'H': GL_UNSIGNED_SHORT,
    'B': GL_UNSIGNED_BYTE,
    'I': GL_UNSIGNED_INT,
    None: None,
}
