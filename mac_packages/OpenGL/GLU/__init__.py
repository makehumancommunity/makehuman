"""The GLU library implementation via ctypes"""
from OpenGL import platform
from OpenGL.error import *
from OpenGL.raw.GLU import *
from OpenGL.raw.GLU.annotations import *

from OpenGL.GLU.quadrics import *
from OpenGL.GLU.projection import *
from OpenGL.GLU.tess import *
from OpenGL.GLU.glunurbs import *
import ctypes

gluErrorString.restype = ctypes.c_char_p
gluGetString.restype = ctypes.c_char_p