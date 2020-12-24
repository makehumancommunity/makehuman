"""Version 1.2 Image-handling functions

Almost all of the 1.2 enhancements are image-handling-related,
so this is, most of the 1.2 wrapper code...

Note that the functions that manually wrap certain operations are
guarded by if simple.functionName checks, so that you can use
if functionName to see if the function is available at run-time.
"""
from OpenGL import wrapper, constants, arrays
from OpenGL.raw.GL.ARB import imaging
from OpenGL.raw.GL.VERSION import GL_1_2 as _simple
from OpenGL.GL.ARB.imaging import *

from OpenGL.GL import images
import ctypes

for suffix,arrayConstant in [
    ('b', constants.GL_BYTE),
    ('f', constants.GL_FLOAT),
    ('i', constants.GL_INT),
    ('s', constants.GL_SHORT),
    ('ub', constants.GL_UNSIGNED_BYTE),
    ('ui', constants.GL_UNSIGNED_INT),
    ('us', constants.GL_UNSIGNED_SHORT),
]:
    for functionName in (
        'glTexImage3D',
        'glTexSubImage3D', # extension/1.2 standard
    ):
        functionName, function = images.typedImageFunction(
            suffix, arrayConstant, getattr(_simple, functionName),
        )
        globals()[functionName] = function
        try:
            del function, functionName
        except NameError as err:
            pass
    try:
        del suffix,arrayConstant
    except NameError as err:
        pass

glTexImage3D = images.setDimensionsAsInts(
    images.setImageInput(
        _simple.glTexImage3D,
        typeName = 'type',
    )
)
glTexSubImage3D = images.setDimensionsAsInts(
    images.setImageInput(
        _simple.glTexSubImage3D,
        typeName = 'type',
    )
)
