from OpenGL.raw.GL._types import *
from OpenGL.raw.GL import _types as _base
GLfixed = _base._defineType('GLfixed', ctypes.c_int32, int )
GLclampx = _base._defineType('GLclampx', ctypes.c_int32, int )
