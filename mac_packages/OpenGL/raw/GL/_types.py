"""OpenGL-wide constant types (not OpenGL.GL-specific)

These are basically the fundamental data-types that OpenGL 
uses (note, doesn't include the OpenGL-ES types!)
"""
import ctypes
from OpenGL.constant import Constant
from OpenGL._bytes import bytes,unicode,as_8_bit, long
assert unicode
assert as_8_bit
from OpenGL._opaque import opaque_pointer_cls as _opaque_pointer_cls

sizeof = ctypes.sizeof
GL_FALSE = Constant( 'GL_FALSE', 0x0 )
GL_TRUE = Constant( 'GL_TRUE', 0x1 )
GL_BYTE = Constant( 'GL_BYTE', 0x1400 )
GL_UNSIGNED_BYTE = Constant( 'GL_UNSIGNED_BYTE', 0x1401 )
GL_SHORT = Constant( 'GL_SHORT', 0x1402 )
GL_UNSIGNED_SHORT = Constant( 'GL_UNSIGNED_SHORT', 0x1403 )
GL_INT = Constant( 'GL_INT', 0x1404 )
GL_UNSIGNED_INT = Constant( 'GL_UNSIGNED_INT', 0x1405 )
GL_UNSIGNED_INT64 = Constant( 'GL_UNSIGNED_INT64_AMD', 0x8BC2 )
GL_FLOAT = Constant( 'GL_FLOAT', 0x1406 )
GL_DOUBLE = Constant( 'GL_DOUBLE', 0x140a )
GL_CHAR = bytes
GL_HALF_FLOAT = Constant( 'GL_HALF_FLOAT_ARB',0x140B)
GL_HALF_NV = Constant( 'GL_HALF_NV', 0x1401 )
GL_FIXED=Constant('GL_FIXED',0x140C)
GL_VOID_P = object()

def _get_ctypes_version():
    return [int(i) for i in ctypes.__version__.split('.')[:3]]
ctypes_version = _get_ctypes_version()

# Basic OpenGL data-types as ctypes declarations...
def _defineType( name, baseType, convertFunc = long ):
    from OpenGL import _configflags
    do_wrapping = (
        _configflags.ALLOW_NUMPY_SCALARS or # explicitly require
        (( # or we are using Python 2.5.x ctypes which doesn't support uint type numpy scalars
            ctypes_version < [1,1,0]
            and baseType in (ctypes.c_uint,ctypes.c_uint64,ctypes.c_ulong,ctypes.c_ushort)
        ) or
        ( # or we are using Python 2.5.x (x < 2) ctypes which doesn't support any numpy int scalars
            ctypes_version < [1,0,2]
            and baseType in (ctypes.c_int,ctypes.c_int64,ctypes.c_long,ctypes.c_short)
        ))
    )
    if do_wrapping:
        original = baseType.from_param
        if not getattr( original, 'from_param_numpy_scalar', False ):
            def from_param( x, typeCode=None ):
                try:
                    return original( x )
                except TypeError as err:
                    try:
                        return original( convertFunc(x) )
                    except TypeError:
                        raise err
            from_param = staticmethod( from_param )
            setattr( baseType, 'from_param', from_param )
            baseType.from_param_numpy_scalar = True
        return baseType
    else:
        return baseType

GLvoid = None
GLboolean = _defineType( 'GLboolean', ctypes.c_ubyte, bool )
GLenum = _defineType( 'GLenum', ctypes.c_uint )

GLfloat = _defineType( 'GLfloat', ctypes.c_float, float )
GLfloat_2 = GLfloat * 2
GLfloat_3 = GLfloat * 3
GLfloat_4 = GLfloat * 4
GLdouble = _defineType( 'GLdouble', ctypes.c_double, float )
GLdouble_2 = GLdouble * 2
GLdouble_3 = GLdouble * 3
GLdouble_4 = GLdouble * 4

GLbyte = ctypes.c_byte
GLshort = _defineType( 'GLshort', ctypes.c_short, int )
GLint = _defineType( 'GLint', ctypes.c_int, int )
GLuint = _defineType( 'GLuint', ctypes.c_uint, long )
GLfixed = _defineType('GLfixed', ctypes.c_int32, int )
GLclampx = _defineType('GLclampx', ctypes.c_int32, int )

if hasattr(ctypes, 'c_ptrdiff_t'): # maybe some day...
    GLsizei = _defineType( 'GLsizei', ctypes.c_ptrdiff_t, int )
elif hasattr(ctypes, 'c_ssize_t'): # 2.7+ should have this
    GLsizei = _defineType( 'GLsizei', ctypes.c_ssize_t, int )
else: # really old, likely never hit these days
    GLsizei = _defineType( 'GLsizei', ctypes.c_long, int )

GLubyte = ctypes.c_ubyte
GLubyte_3 = GLubyte * 3
GLushort = _defineType( 'GLushort', ctypes.c_ushort, int )
GLulong = _defineType( 'GLulong', ctypes.c_ulong, int )
GLhandleARB = _defineType( 'GLhandleARB', ctypes.c_uint, long )
GLhandle = _defineType( 'GLhandle', ctypes.c_uint, long )

GLchar = GLcharARB = ctypes.c_char

GLbitfield = _defineType( 'GLbitfield', ctypes.c_uint, long )

GLclampd = _defineType( 'GLclampd', ctypes.c_double, float )
GLclampf = _defineType( 'GLclampf', ctypes.c_float, float )

GLuint64 = GLuint64EXT = _defineType('GLuint64', ctypes.c_uint64, long )
GLint64 = GLint64EXT = _defineType('GLint64', ctypes.c_int64, long )

# ptrdiff_t, actually...
GLsizeiptrARB = GLsizeiptr = GLsizei
GLvdpauSurfaceNV = GLintptrARB = GLintptr = GLsizei
size_t = ctypes.c_size_t
int32_t = ctypes.c_int32
int64_t = ctypes.c_int64

void = None

# this is *wrong*, half is a *float* type, but ctypes doesn't have 16-bit float support
GLhalfNV = GLhalfARB = ctypes.c_ushort

# GL.ARB.sync extension, GLsync is an opaque pointer to a struct 
# in the extensions header, basically just a "token" that can be 
# passed to the various operations...
GLsync = _opaque_pointer_cls( 'GLsync' )
GLvoidp = ctypes.c_void_p

ARRAY_TYPE_TO_CONSTANT = [
    ('GLclampd', GL_DOUBLE),
    ('GLclampf', GL_FLOAT),
    ('GLfloat', GL_FLOAT),
    ('GLdouble', GL_DOUBLE),
    ('GLbyte', GL_BYTE),
    ('GLshort', GL_SHORT),
    ('GLint', GL_INT),
    ('GLubyte', GL_UNSIGNED_BYTE),
    ('GLushort', GL_UNSIGNED_SHORT),
    ('GLuint', GL_UNSIGNED_INT),
    ('GLenum', GL_UNSIGNED_INT),
]

from OpenGL.platform import PLATFORM as _p

GLDEBUGPROCARB = GLDEBUGPROCKHR = GLDEBUGPROC = _p.DEFAULT_FUNCTION_TYPE(
    void, 
    GLenum,  # source,
    GLenum, #type,
    GLuint, # id 
    GLenum, # severity
    GLsizei, # length
    ctypes.c_char_p, # message 
    GLvoidp, # userParam
)

class _cl_context( ctypes.Structure ):
    """Placeholder/empty structure for _cl_context"""
class _cl_event( ctypes.Structure ):
    """Placeholder/empty structure for _cl_event"""
    
GLDEBUGPROCAMD = _p.DEFAULT_FUNCTION_TYPE(
    void,
    GLuint,# id,
    GLenum,# category,
    GLenum,# severity,
    GLsizei,# length,
    ctypes.c_char_p,# message,
    GLvoidp,# userParam
)

GLeglImageOES = GLvoidp 
c_int = ctypes.c_int

