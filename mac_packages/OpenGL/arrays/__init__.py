"""Abstraction point for handling of data-pointers in OpenGL

The purpose of this package is to allow for the registration and dispatch
of handlers for different data-types in such a way that you can add new
data-types to the set of types which PyOpenGL will handle as arguments
to functions requiring typed pointers.

Possible data types:
    Numpy arrays
    Numarray arrays
    PyGame surfaces
    PyMedia buffers
    Python buffer-objects
    Memory-mapped files
    PIL images
"""
import ctypes
import OpenGL
from OpenGL.arrays.arraydatatype import *
from OpenGL.arrays import formathandler
from OpenGL.arrays.arrayhelpers import *
