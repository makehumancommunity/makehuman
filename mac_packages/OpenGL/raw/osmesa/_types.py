import ctypes
from OpenGL import _opaque
GLenum = ctypes.c_uint
GLboolean = ctypes.c_ubyte
GLsizei = ctypes.c_int
GLint = ctypes.c_int
OSMesaContext = _opaque.opaque_pointer_cls( 'OSMesaContext' )

__all__ = [
    'OSMesaContext',
]
