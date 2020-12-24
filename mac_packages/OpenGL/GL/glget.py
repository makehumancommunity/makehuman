"""Implementation of the special "glGet" functions

For comparison, here's what a straightforward implementation looks like:

    def glGetDoublev( pname ):
        "Natural writing of glGetDoublev using standard ctypes"
        output = c_double*sizes.get( pname )
        result = output()
        result = platform.PLATFORM.GL.glGetDoublev( pname, byref(result) )
        return Numeric.array( result )
"""
from OpenGL.GL.VERSION import GL_1_1 as _simple
import ctypes
GLenum = ctypes.c_uint
GLsize = GLsizei = ctypes.c_int

__all__ = (
    'glGetString',
)

glGetString = _simple.glGetString
glGetString.restype = ctypes.c_char_p
glGetString.__doc__ = """glGetString( constant ) -> Current string value"""
