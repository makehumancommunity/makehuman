"""The GLUT library implementation via ctypes"""
from OpenGL.raw.GLUT import *

from OpenGL.GLUT.special import *
from OpenGL.GLUT.fonts import *
from OpenGL.GLUT.freeglut import *
from OpenGL.GLUT.osx import *

if glutLeaveMainLoop:
    HAVE_FREEGLUT = True 
else:
    HAVE_FREEGLUT = False 
