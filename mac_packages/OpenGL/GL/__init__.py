"""OpenGL.GL, the core GL library and extensions to it"""
# early import of our modules to prevent import loops...
from OpenGL import error as _error
from OpenGL.GL.VERSION.GL_1_1 import *
from OpenGL.GL.pointers import *
from OpenGL.GL.images import *

from OpenGL.GL.exceptional import *

from OpenGL.GL.glget import *

from OpenGL.GL.VERSION.GL_1_2 import *
from OpenGL.GL.VERSION.GL_1_3 import *
from OpenGL.GL.VERSION.GL_1_4 import *
from OpenGL.GL.VERSION.GL_1_5 import *
from OpenGL.GL.VERSION.GL_2_0 import *
from OpenGL.GL.VERSION.GL_2_1 import *
from OpenGL.GL.VERSION.GL_3_0 import *
from OpenGL.GL.VERSION.GL_3_1 import *
from OpenGL.GL.VERSION.GL_3_2 import *
from OpenGL.GL.VERSION.GL_3_3 import *
from OpenGL.GL.VERSION.GL_4_0 import *
from OpenGL.GL.VERSION.GL_4_1 import *
from OpenGL.GL.VERSION.GL_4_2 import *
from OpenGL.GL.VERSION.GL_4_3 import *
from OpenGL.GL.VERSION.GL_4_4 import *
from OpenGL.GL.VERSION.GL_4_5 import *
from OpenGL.GL.VERSION.GL_4_6 import *

from OpenGL.error import *
GLerror = GLError

# Now the aliases...
glRotate = glRotated
glTranslate = glTranslated
glLight = glLightfv
glTexCoord = glTexCoord2d
glScale = glScaled
#glColor = glColor3f
glNormal = glNormal3d

glGetBoolean = glGetBooleanv
glGetDouble = glGetDoublev
glGetFloat = glGetFloatv
glGetInteger = glGetIntegerv 
glGetPolygonStippleub = glGetPolygonStipple

from OpenGL.GL import vboimplementation as _core_implementation
from OpenGL.GL.ARB import vboimplementation as _arb_implementation
