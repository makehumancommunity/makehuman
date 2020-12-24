'''GLU extension EXT.object_space_tess
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes

GLU_OBJECT_PARAMETRIC_ERROR_EXT = constant.Constant( 'GLU_OBJECT_PARAMETRIC_ERROR_EXT', 100208 )
GLU_OBJECT_PATH_LENGTH_EXT = constant.Constant( 'GLU_OBJECT_PATH_LENGTH_EXT', 100209)

def gluInitObjectSpaceTessEXT():
    '''Return boolean indicating whether this module is available'''
    return extensions.hasGLUExtension( 'GLU_EXT_object_space_tess' )
