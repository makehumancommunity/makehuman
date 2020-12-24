"""Implementation of GLU Nurbs structure and callback methods

Same basic pattern as seen with the gluTess* functions, just need to
add some bookkeeping to the structure class so that we can keep the
Python function references alive during the calling process.
"""
from OpenGL.raw import GLU as _simple
from OpenGL import platform, converters, wrapper
from OpenGL.GLU import glustruct
from OpenGL.lazywrapper import lazy as _lazy
from OpenGL import arrays, error
import ctypes
import weakref
from OpenGL.platform import PLATFORM
import OpenGL
from OpenGL import _configflags

__all__ = (
    'GLUnurbs',
    'gluNewNurbsRenderer',
    'gluNurbsCallback',
    'gluNurbsCallbackData',
    'gluNurbsCallbackDataEXT',
    'gluNurbsCurve',
    'gluNurbsSurface',
    'gluPwlCurve',
)

# /usr/include/GL/glu.h 242
class GLUnurbs(glustruct.GLUStruct, _simple.GLUnurbs):
    """GLU Nurbs structure with oor and callback storage support

    IMPORTANT NOTE: the texture coordinate callback receives a raw ctypes
    data-pointer, as without knowing what type of evaluation is being done
    (1D or 2D) we cannot safely determine the size of the array to convert
    it.  This is a limitation of the C implementation.  To convert to regular
    data-pointer, just call yourNurb.ptrAsArray( ptr, size, arrays.GLfloatArray )
    with the size of data you expect.
    """
    FUNCTION_TYPE = PLATFORM.functionTypeFor(PLATFORM.GLU)
    CALLBACK_FUNCTION_REGISTRARS = {
        # mapping from "which" to a function that should take 3 parameters,
        # the nurb, the which and the function pointer...
    }
    CALLBACK_TYPES = {
        # mapping from "which" GLU enumeration to a ctypes function type
        _simple.GLU_NURBS_BEGIN: FUNCTION_TYPE(
            None, _simple.GLenum
        ),
        _simple.GLU_NURBS_BEGIN_DATA: FUNCTION_TYPE(
            None, _simple.GLenum, ctypes.POINTER(_simple.GLvoid)
        ),
        _simple.GLU_NURBS_VERTEX: FUNCTION_TYPE(
            None, ctypes.POINTER(_simple.GLfloat)
        ),
        _simple.GLU_NURBS_VERTEX_DATA: FUNCTION_TYPE(
            None, ctypes.POINTER(_simple.GLfloat), ctypes.POINTER(_simple.GLvoid)
        ),
        _simple.GLU_NURBS_NORMAL: FUNCTION_TYPE(
            None, ctypes.POINTER(_simple.GLfloat)
        ),
        _simple.GLU_NURBS_NORMAL_DATA: FUNCTION_TYPE(
            None, ctypes.POINTER(_simple.GLfloat), ctypes.POINTER(_simple.GLvoid)
        ),
        _simple.GLU_NURBS_COLOR: FUNCTION_TYPE(
            None, ctypes.POINTER(_simple.GLfloat)
        ),
        _simple.GLU_NURBS_COLOR_DATA: FUNCTION_TYPE(
            None, ctypes.POINTER(_simple.GLfloat), ctypes.POINTER(_simple.GLvoid)
        ),
        _simple.GLU_NURBS_TEXTURE_COORD: FUNCTION_TYPE(
            None, ctypes.POINTER(_simple.GLfloat)
        ),
        _simple.GLU_NURBS_TEXTURE_COORD_DATA: FUNCTION_TYPE(
            None, ctypes.POINTER(_simple.GLfloat), ctypes.POINTER(_simple.GLvoid)
        ),
        _simple.GLU_NURBS_END:FUNCTION_TYPE(
            None
        ),
        _simple.GLU_NURBS_END_DATA: FUNCTION_TYPE(
            None, ctypes.POINTER(_simple.GLvoid)
        ),
        _simple.GLU_NURBS_ERROR:FUNCTION_TYPE(
            None, _simple.GLenum,
        ),
    }
    WRAPPER_METHODS = {
        _simple.GLU_NURBS_BEGIN: None,
        _simple.GLU_NURBS_BEGIN_DATA: '_justOOR',
        _simple.GLU_NURBS_VERTEX: '_vec3',
        _simple.GLU_NURBS_VERTEX_DATA: '_vec3',
        _simple.GLU_NURBS_NORMAL: '_vec3',
        _simple.GLU_NURBS_NORMAL_DATA: '_vec3',
        _simple.GLU_NURBS_COLOR: '_vec4',
        _simple.GLU_NURBS_COLOR_DATA: '_vec4',
        _simple.GLU_NURBS_TEXTURE_COORD: '_tex',
        _simple.GLU_NURBS_TEXTURE_COORD_DATA: '_tex',
        _simple.GLU_NURBS_END: None,
        _simple.GLU_NURBS_END_DATA: '_justOOR',
        _simple.GLU_NURBS_ERROR: None,
    }
    def _justOOR( self, function ):
        """Just do OOR on the last argument..."""
        def getOOR( *args ):
            args = args[:-1] + (self.originalObject(args[-1]),)
            return function( *args )
        return getOOR
    def _vec3( self, function, size=3 ):
        """Convert first arg to size-element array, do OOR on arg2 if present"""
        def vec( *args ):
            vec = self.ptrAsArray(args[0],size,arrays.GLfloatArray)
            if len(args) > 1:
                oor = self.originalObject(args[1])
                return function( vec, oor )
            else:
                return function( vec )
        return vec
    def _vec4( self, function ):
        """Size-4 vector version..."""
        return self._vec3( function, 4 )
    def _tex( self, function ):
        """Texture coordinate callback

        NOTE: there is no way for *us* to tell what size the array is, you will
        get back a raw data-point, not an array, as you do for all other callback
        types!!!
        """
        def oor( *args ):
            if len(args) > 1:
                oor = self.originalObject(args[1])
                return function( args[0], oor )
            else:
                return function( args[0] )
        return oor

# XXX yes, this is a side-effect...
_simple.gluNewNurbsRenderer.restype = ctypes.POINTER( GLUnurbs )

def _callbackWithType( funcType ):
    """Get gluNurbsCallback function with set last arg-type"""
    result =  platform.copyBaseFunction(
        _simple.gluNurbsCallback
    )
    result.argtypes = [ctypes.POINTER(GLUnurbs), _simple.GLenum, funcType]
    assert result.argtypes[-1] == funcType
    return result

for (c,funcType) in GLUnurbs.CALLBACK_TYPES.items():
    cb = _callbackWithType( funcType )
    GLUnurbs.CALLBACK_FUNCTION_REGISTRARS[ c ] = cb
    assert funcType == GLUnurbs.CALLBACK_TYPES[c]
    assert cb.argtypes[-1] == funcType
try:
    del c,cb, funcType
except NameError as err:
    pass

def gluNurbsCallback( nurb, which, CallBackFunc ):
    """Dispatch to the nurb's addCallback operation"""
    return nurb.addCallback( which, CallBackFunc )

@_lazy( _simple.gluNewNurbsRenderer )
def gluNewNurbsRenderer( baseFunction ):
    """Return a new nurbs renderer for the system (dereferences pointer)"""
    newSet = baseFunction()
    new = newSet[0]
    #new.__class__ = GLUnurbs # yes, I know, ick
    return new

@_lazy( _simple.gluNurbsCallbackData )
def gluNurbsCallbackData( baseFunction, nurb, userData ):
    """Note the Python object for use as userData by the nurb"""
    return baseFunction(
        nurb, nurb.noteObject( userData )
    )

MAX_ORDER = 8
def checkOrder( order,knotCount,name ):
    """Check that order is valid..."""
    if order < 1:
        raise error.GLUError(
            """%s should be 1 or more, is %s"""%( name,order,)
        )
    elif order > MAX_ORDER:
        raise error.GLUError(
            """%s should be %s or less, is %s"""%( name, MAX_ORDER, order)
        )
    elif knotCount < (2*order):
        raise error.GLUError(
            """Knotcount must be at least 2x %s is %s should be at least %s"""%( name, knotCount, 2*order)
        )
def checkKnots( knots, name ):
    """Check that knots are in ascending order"""
    if len(knots):
        knot = knots[0]
        for next in knots[1:]:
            if next < knot:
                raise error.GLUError(
                    """%s has decreasing knot %s after %s"""%( name, next, knot )
                )

@_lazy( _simple.gluNurbsCallbackDataEXT )
def gluNurbsCallbackDataEXT( baseFunction,nurb, userData ):
    """Note the Python object for use as userData by the nurb"""
    return baseFunction(
        nurb, nurb.noteObject( userData )
    )

@_lazy( _simple.gluNurbsCurve )
def gluNurbsCurve( baseFunction, nurb, knots, control, type ):
    """Pythonic version of gluNurbsCurve

    Calculates knotCount, stride, and order automatically
    """
    knots = arrays.GLfloatArray.asArray( knots )
    knotCount = arrays.GLfloatArray.arraySize( knots )
    control = arrays.GLfloatArray.asArray( control )
    try:
        length,step = arrays.GLfloatArray.dimensions( control )
    except ValueError as err:
        raise error.GLUError( """Need a 2-dimensional control array""" )
    order = knotCount - length
    if _configflags.ERROR_CHECKING:
        checkOrder( order, knotCount, 'order of NURBS curve')
        checkKnots( knots, 'knots of NURBS curve')
    return baseFunction(
        nurb, knotCount, knots, step, control, order, type,
    )

@_lazy( _simple.gluNurbsSurface )
def gluNurbsSurface( baseFunction, nurb, sKnots, tKnots, control, type ):
    """Pythonic version of gluNurbsSurface

    Calculates knotCount, stride, and order automatically
    """
    sKnots = arrays.GLfloatArray.asArray( sKnots )
    sKnotCount = arrays.GLfloatArray.arraySize( sKnots )
    tKnots = arrays.GLfloatArray.asArray( tKnots )
    tKnotCount = arrays.GLfloatArray.arraySize( tKnots )
    control = arrays.GLfloatArray.asArray( control )

    try:
        length,width,step = arrays.GLfloatArray.dimensions( control )
    except ValueError as err:
        raise error.GLUError( """Need a 3-dimensional control array""" )
    sOrder = sKnotCount - length
    tOrder = tKnotCount - width
    sStride = width*step
    tStride = step
    if _configflags.ERROR_CHECKING:
        checkOrder( sOrder, sKnotCount, 'sOrder of NURBS surface')
        checkOrder( tOrder, tKnotCount, 'tOrder of NURBS surface')
        checkKnots( sKnots, 'sKnots of NURBS surface')
        checkKnots( tKnots, 'tKnots of NURBS surface')
    if not (sKnotCount-sOrder)*(tKnotCount-tOrder) == length*width:
        raise error.GLUError(
            """Invalid NURB structure""",
            nurb, sKnotCount, sKnots, tKnotCount, tKnots,
            sStride, tStride, control,
            sOrder,tOrder,
            type
        )

    result = baseFunction(
        nurb, sKnotCount, sKnots, tKnotCount, tKnots,
        sStride, tStride, control,
        sOrder,tOrder,
        type
    )
    return result

@_lazy( _simple.gluPwlCurve )
def gluPwlCurve( baseFunction, nurb, data, type ):
    """gluPwlCurve -- piece-wise linear curve within GLU context

    data -- the data-array
    type -- determines number of elements/data-point
    """
    data = arrays.GLfloatArray.asArray( data )
    if type == _simple.GLU_MAP1_TRIM_2:
        divisor = 2
    elif type == _simple.GLU_MAP_TRIM_3:
        divisor = 3
    else:
        raise ValueError( """Unrecognised type constant: %s"""%(type))
    size = arrays.GLfloatArray.arraySize( data )
    size = int(size//divisor)
    return baseFunction( nurb, size, data, divisor, type )
