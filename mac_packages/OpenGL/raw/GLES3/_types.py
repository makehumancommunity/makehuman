from OpenGL.raw.GLES2._types import *

from OpenGL.platform import PLATFORM as _p
_error_function = getattr(_p.GLES3, 'glGetError',None)
