"""Exceptional cases that need some extra wrapping"""
from OpenGL import arrays
from OpenGL.arrays.arraydatatype import GLfloatArray
from OpenGL.lazywrapper import lazy as _lazy
from OpenGL.GL.VERSION import GL_1_1 as full
from OpenGL.raw.GL import _errors
from OpenGL._bytes import bytes
from OpenGL import _configflags
from OpenGL._null import NULL as _NULL
import ctypes

__all__ = [
    'glBegin',
    'glCallLists',
    'glColor',
    'glDeleteTextures',
    'glEnd',
    'glMap1d',
    'glMap1f',
    'glMap2d',
    'glMap2f',
    'glMaterial',
    'glRasterPos',
    'glTexParameter',
    'glVertex',
    'glAreTexturesResident',
]

glRasterPosDispatch = {
    2: full.glRasterPos2d,
    3: full.glRasterPos3d,
    4: full.glRasterPos4d,
}

if _configflags.ERROR_CHECKING:
    @_lazy( full.glBegin )
    def glBegin( baseFunction, mode ):
        """Begin GL geometry-definition mode, disable automatic error checking"""
        _errors._error_checker.onBegin( )
        return baseFunction( mode )
    @_lazy( full.glEnd )
    def glEnd( baseFunction ):
        """Finish GL geometry-definition mode, re-enable automatic error checking"""
        _errors._error_checker.onEnd( )
        return baseFunction( )
else:
    glBegin = full.glBegin
    glEnd = full.glEnd

@_lazy( full.glDeleteTextures )
def glDeleteTextures( baseFunction, size, array=_NULL ):
    """Delete specified set of textures
    
    If array is *not* passed then `size` must be a `GLuintArray`
    compatible object which can be sized using `arraySize`, the 
    result of which will be used as size.
    """
    if array is _NULL:
        ptr = arrays.GLuintArray.asArray( size )
        size = arrays.GLuintArray.arraySize( ptr )
    else:
        ptr = array
    return baseFunction( size, ptr )


def glMap2( baseFunction, arrayType ):
    def glMap2( target, u1, u2, v1, v2, points):
        """glMap2(target, u1, u2, v1, v2, points[][][]) -> None

        This is a completely non-standard signature which doesn't allow for most
        of the funky uses with strides and the like, but it has been like this for
        a very long time...
        """
        ptr = arrayType.asArray( points )
        uorder,vorder,vstride = arrayType.dimensions( ptr )
        ustride = vstride*vorder
        return baseFunction(
            target,
            u1, u2,
            ustride, uorder,
            v1, v2,
            vstride, vorder,
            ptr
        )
    glMap2.__name__ = baseFunction.__name__
    glMap2.baseFunction = baseFunction
    return glMap2
glMap2d = glMap2( full.glMap2d, arrays.GLdoubleArray )
glMap2f = glMap2( full.glMap2f, arrays.GLfloatArray )
try:
    del glMap2
except NameError as err:
    pass

def glMap1( baseFunction, arrayType ):
    def glMap1(target,u1,u2,points):
        """glMap1(target, u1, u2, points[][][]) -> None

        This is a completely non-standard signature which doesn't allow for most
        of the funky uses with strides and the like, but it has been like this for
        a very long time...
        """
        ptr = arrayType.asArray( points )
        dims = arrayType.dimensions( ptr )
        uorder = dims[0]
        ustride = dims[1]
        return baseFunction( target, u1,u2,ustride,uorder, ptr )
    glMap1.__name__ == baseFunction.__name__
    glMap1.baseFunction = baseFunction
    return glMap1
glMap1d = glMap1( full.glMap1d, arrays.GLdoubleArray )
glMap1f = glMap1( full.glMap1f, arrays.GLfloatArray )
try:
    del glMap1
except NameError as err:
    pass

def glRasterPos( *args ):
    """Choose glRasterPosX based on number of args"""
    if len(args) == 1:
        # v form...
        args = args[0]
    function = glRasterPosDispatch[ len(args) ]
    return function( *args )

glVertexDispatch = {
    2: full.glVertex2d,
    3: full.glVertex3d,
    4: full.glVertex4d,
}
def glVertex( *args ):
    """Choose glVertexX based on number of args"""
    if len(args) == 1:
        # v form...
        args = args[0]
    return glVertexDispatch[ len(args) ]( *args )

@_lazy( full.glCallLists )
def glCallLists( baseFunction, lists, *args ):
    """glCallLists( bytes( lists ) or lists[] ) -> None

    Restricted version of glCallLists, takes a string or a GLuint compatible
    array data-type and passes into the base function.
    """
    if not len(args):
        if isinstance( lists, bytes ):
            return baseFunction(
                len(lists),
                full.GL_UNSIGNED_BYTE,
                ctypes.c_void_p(arrays.GLubyteArray.dataPointer( lists )),
            )
        ptr = arrays.GLuintArray.asArray( lists )
        size = arrays.GLuintArray.arraySize( ptr )
        return baseFunction(
            size,
            full.GL_UNSIGNED_INT,
            ctypes.c_void_p( arrays.GLuintArray.dataPointer(ptr))
        )
    return baseFunction( lists, *args )

def glTexParameter( target, pname, parameter ):
    """Set a texture parameter, choose underlying call based on pname and parameter"""
    if isinstance( parameter, float ):
        return full.glTexParameterf( target, pname, parameter )
    elif isinstance( parameter, int ):
        return full.glTexParameteri( target, pname, parameter )
    else:
        value = GLfloatArray.asArray( parameter, full.GL_FLOAT )
        return full.glTexParameterfv( target, pname, value )

def glMaterial( faces, constant, *args ):
    """glMaterial -- convenience function to dispatch on argument type

    If passed a single argument in args, calls:
        glMaterialfv( faces, constant, args[0] )
    else calls:
        glMaterialf( faces, constant, *args )
    """
    if len(args) == 1:
        arg = GLfloatArray.asArray( args[0] )
        if arg is None:
            raise ValueError( """Null value in glMaterial: %s"""%(args,) )
        return full.glMaterialfv( faces, constant, arg )
    else:
        return full.glMaterialf( faces, constant, *args )

glColorDispatch = {
    3: full.glColor3fv,
    4: full.glColor4fv,
}

def glColor( *args ):
    """glColor*f* -- convenience function to dispatch on argument type

    dispatches to glColor3f, glColor2f, glColor4f, glColor3f, glColor2f, glColor4f
    depending on the arguments passed...
    """
    arglen = len(args)
    if arglen == 1:
        arg = arrays.GLfloatArray.asArray( args[0] )
        function = glColorDispatch[arrays.GLfloatArray.arraySize( arg )]
        return function( arg )
    elif arglen == 2:
        return full.glColor2d( *args )
    elif arglen == 3:
        return full.glColor3d( *args )
    elif arglen == 4:
        return full.glColor4d( *args )
    else:
        raise ValueError( """Don't know how to handle arguments: %s"""%(args,))


# Rectagle coordinates,
@_lazy( full.glAreTexturesResident )
def glAreTexturesResident( baseFunction, *args ):
    """Allow both Pythonic and C-style calls to glAreTexturesResident

        glAreTexturesResident( arrays.GLuintArray( textures) )

    or

        glAreTexturesResident( int(n), arrays.GLuintArray( textures), arrays.GLuboolean( output) )

    or

        glAreTexturesResident( int(n), arrays.GLuintArray( textures) )

    returns the output arrays.GLubooleanArray
    """
    if len(args) == 1:
        # Pythonic form...
        textures = args[0]
        textures = arrays.GLuintArray.asArray( textures )
        n = arrays.GLuintArray.arraySize(textures)
        output = arrays.GLbooleanArray.zeros( (n,))
    elif len(args) == 2:
        try:
            n = int( args[0] )
        except TypeError:
            textures = args[0]
            textures = arrays.GLuintArray.asArray( textures )

            n = arrays.GLuintArray.arraySize(textures)
            output = args[1]
            output = arrays.GLbooleanArray.asArray( output )
        else:
            textures = args[1]
            textures = arrays.GLuintArray.asArray( textures )

            output = arrays.GLbooleanArray.zeros( (n,))
    elif len(args) == 3:
        n,textures,output = args
        textures = arrays.GLuintArray.asArray( textures )
        output = arrays.GLbooleanArray.asArray( output )
    else:
        raise TypeError( """Expected 1 to 3 arguments to glAreTexturesResident""" )
    texturePtr = arrays.GLuintArray.typedPointer( textures )
    outputPtr = arrays.GLbooleanArray.typedPointer( output )
    result = baseFunction( n, texturePtr, outputPtr )
    if result:
        # weirdness of the C api, doesn't produce values if all are true
        for i in range(len(output)):
            output[i] = 1
    return output
