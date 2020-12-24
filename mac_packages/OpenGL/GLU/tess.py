"""Wrapper/Implementation of the GLU tessellator objects for PyOpenGL"""
from OpenGL.raw import GLU as _simple
from OpenGL.raw.GL.VERSION import GL_1_1
from OpenGL.platform import createBaseFunction
from OpenGL.GLU import glustruct
from OpenGL import arrays, wrapper
from OpenGL.platform import PLATFORM
GLU = PLATFORM.GLU
from OpenGL.lazywrapper import lazy as _lazy
import ctypes

class GLUtesselator( glustruct.GLUStruct, _simple.GLUtesselator):
    """Implementation class for GLUTessellator structures in OpenGL-ctypes"""
    FUNCTION_TYPE = PLATFORM.functionTypeFor(PLATFORM.GLU)
    CALLBACK_TYPES = {
        # mapping from "which" GLU enumeration to a ctypes function type
        _simple.GLU_TESS_BEGIN: FUNCTION_TYPE( None, _simple.GLenum ),
        _simple.GLU_TESS_BEGIN_DATA: FUNCTION_TYPE(
            None, _simple.GLenum, ctypes.c_void_p
        ),
        _simple.GLU_TESS_EDGE_FLAG: FUNCTION_TYPE( None, _simple.GLboolean),
        _simple.GLU_TESS_EDGE_FLAG_DATA: FUNCTION_TYPE(
            None, _simple.GLboolean, ctypes.c_void_p
        ),
        _simple.GLU_TESS_VERTEX: FUNCTION_TYPE( None, ctypes.c_void_p ),
        _simple.GLU_TESS_VERTEX_DATA: FUNCTION_TYPE(
            None, ctypes.c_void_p, ctypes.c_void_p
        ),
        _simple.GLU_TESS_END: FUNCTION_TYPE( None ),
        _simple.GLU_TESS_END_DATA: FUNCTION_TYPE( None, ctypes.c_void_p),
        _simple.GLU_TESS_COMBINE: FUNCTION_TYPE(
            None,
            ctypes.POINTER(_simple.GLdouble),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(_simple.GLfloat),
            ctypes.POINTER(ctypes.c_void_p)
        ),
        _simple.GLU_TESS_COMBINE_DATA: FUNCTION_TYPE(
            None,
            ctypes.POINTER(_simple.GLdouble),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.POINTER(_simple.GLfloat),
            ctypes.POINTER(ctypes.c_void_p),
            ctypes.c_void_p,
        ),
        _simple.GLU_TESS_ERROR: FUNCTION_TYPE( None, _simple.GLenum),
        _simple.GLU_TESS_ERROR_DATA: FUNCTION_TYPE(
            None, _simple.GLenum, ctypes.c_void_p
        ),
        _simple.GLU_ERROR : FUNCTION_TYPE( None, _simple.GLenum )
    }
    WRAPPER_METHODS = {
        _simple.GLU_TESS_BEGIN_DATA: 'dataWrapper',
        _simple.GLU_TESS_EDGE_FLAG_DATA: 'dataWrapper',
        _simple.GLU_TESS_VERTEX: 'vertexWrapper',
        _simple.GLU_TESS_VERTEX_DATA: 'vertexWrapper',
        _simple.GLU_TESS_END_DATA: 'dataWrapper',
        _simple.GLU_TESS_COMBINE: 'combineWrapper',
        _simple.GLU_TESS_COMBINE_DATA: 'combineWrapper',
        _simple.GLU_TESS_ERROR_DATA: 'dataWrapper',
    }
    def gluTessVertex( self, location, data=None ):
        """Add a vertex to this tessellator, storing data for later lookup"""
        vertexCache = getattr( self, 'vertexCache', None )
        if vertexCache is None:
            self.vertexCache = []
            vertexCache = self.vertexCache
        location = arrays.GLdoubleArray.asArray( location, GL_1_1.GL_DOUBLE )
        if arrays.GLdoubleArray.arraySize( location ) != 3:
            raise ValueError( """Require 3 doubles for array location, got: %s"""%(location,))
        oorValue = self.noteObject(data)
        vp = ctypes.c_void_p( oorValue )
        self.vertexCache.append( location )
        return gluTessVertexBase( self, location, vp )
    def gluTessBeginPolygon( self, data ):
        """Note the object pointer to return it as a Python object"""
        return _simple.gluTessBeginPolygon(
            self, ctypes.c_void_p(self.noteObject( data ))
        )
    def combineWrapper( self, function ):
        """Wrap a Python function with ctypes-compatible wrapper for combine callback

        For a Python combine callback, the signature looks like this:
            def combine(
                GLdouble coords[3],
                void *vertex_data[4],
                GLfloat weight[4]
            ):
                return data
        While the C signature looks like this:
            void combine(
                GLdouble coords[3],
                void *vertex_data[4],
                GLfloat weight[4],
                void **outData
            )
        """
        if (function is not None) and (not hasattr( function,'__call__' )):
            raise TypeError( """Require a callable callback, got:  %s"""%(function,))
        def wrap( coords, vertex_data, weight, outData, *args ):
            """The run-time wrapper around the function"""
            coords = self.ptrAsArray( coords, 3, arrays.GLdoubleArray )
            weight = self.ptrAsArray( weight, 4, arrays.GLfloatArray )
            # find the original python objects for vertex data
            vertex_data = [ self.originalObject( vertex_data[i] ) for i in range(4) ]
            args = tuple( [ self.originalObject( x ) for x in args ] )
            try:
                result = function( coords, vertex_data, weight, *args )
            except Exception as err:
                raise err.__class__(
                    """Failure during combine callback %r with args( %s,%s,%s,*%s):\n%s"""%(
                        function, coords, vertex_data, weight, args, str(err),
                    )
                )
            outP = ctypes.c_void_p(self.noteObject(result))
            if outData:
                outData[0] = outP
            else:
                raise RuntimeError( "Null outData passed to callback" )
            return None
        return wrap
    def dataWrapper( self, function ):
        """Wrap a function which only has the one data-pointer as last arg"""
        if (function is not None) and (not hasattr( function,'__call__' )):
            raise TypeError( """Require a callable callback, got:  %s"""%(function,))
        def wrap( *args ):
            """Just return the original object for polygon_data"""
            args = args[:-1] + ( self.originalObject(args[-1]), )
            try:
                return function( *args )
            except Exception as err:
                err.args += (function,args)
                raise
        return wrap
    def dataWrapper2( self, function ):
        """Wrap a function which has two data-pointers as last args"""
        if (function is not None) and (not hasattr( function,'__call__' )):
            raise TypeError( """Require a callable callback, got:  %s"""%(function,))
        def wrap( *args ):
            """Just return the original object for polygon_data"""
            args = args[:-2] + ( self.originalObject(args[-2]), self.originalObject(args[-1]), )
            try:
                return function( *args )
            except Exception as err:
                err.args += (function,args)
                raise
        return wrap
    def vertexWrapper( self, function ):
        """Converts a vertex-pointer into an OOR vertex for processing"""
        if (function is not None) and (not hasattr( function,'__call__' )):
            raise TypeError( """Require a callable callback, got:  %s"""%(function,))
        def wrap( vertex, data=None ):
            """Just return the original object for polygon_data"""
            vertex = self.originalObject(vertex)
            try:
                if data is not None:
                    data = self.originalObject(data)
                    return function( vertex, data )
                else:
                    return function( vertex )
            except Exception as err:
                err.args += (function,(vertex,data))
                raise
        return wrap

GLUtesselator.CALLBACK_FUNCTION_REGISTRARS = dict([
    (c,createBaseFunction(
        'gluTessCallback', dll=GLU, resultType=None,
        argTypes=[ctypes.POINTER(GLUtesselator), _simple.GLenum,funcType],
        doc='gluTessCallback( POINTER(GLUtesselator)(tess), GLenum(which), _GLUfuncptr(CallBackFunc) ) -> None',
        argNames=('tess', 'which', 'CallBackFunc'),
    ))
    for (c,funcType) in GLUtesselator.CALLBACK_TYPES.items()
])
try:
    del c, funcType
except NameError as err:
    pass

def gluTessCallback( tess, which, function ):
    """Set a given gluTessellator callback for the given tessellator"""
    return tess.addCallback( which, function )
def gluTessBeginPolygon( tess, data ):
    """Start definition of polygon in the tessellator"""
    return tess.gluTessBeginPolygon( data )
def gluTessVertex( tess, location, data=None ):
    """Add a vertex to the tessellator's current polygon"""
    return tess.gluTessVertex( location, data )

# /usr/include/GL/glu.h 293
@_lazy(
    createBaseFunction(
        'gluNewTess', dll=GLU, resultType=ctypes.POINTER(GLUtesselator),
        doc='gluNewTess(  ) -> POINTER(GLUtesselator)',
    )
)
def gluNewTess( baseFunction ):
    """Get a new tessellator object (just unpacks the pointer for you)"""
    return baseFunction()[0]

@_lazy( _simple.gluGetTessProperty )
def gluGetTessProperty( baseFunction, tess, which, data=None ):
    """Retrieve single double for a tessellator property"""
    if data is None:
        data = _simple.GLdouble( 0.0 )
        baseFunction( tess, which, data )
        return data.value
    else:
        return baseFunction( tess, which, data )

gluTessVertexBase = wrapper.wrapper( _simple.gluTessVertex ).setInputArraySize(
    'location',
    3,
)

__all__ = (
    'gluNewTess',
    'gluGetTessProperty',
    'gluTessBeginPolygon',
    'gluTessCallback',
    'gluTessVertex',
)
