"""Wrapper/Implementation of the GLU quadrics object for PyOpenGL"""
from OpenGL.raw import GLU as _simple
from OpenGL.platform import createBaseFunction, PLATFORM
import ctypes

class GLUQuadric( _simple.GLUquadric ):
    """Implementation class for GLUQuadric classes in PyOpenGL"""
    FUNCTION_TYPE = PLATFORM.functionTypeFor(PLATFORM.GLU)
    CALLBACK_TYPES = {
        # mapping from "which" GLU enumeration to a ctypes function type
        _simple.GLU_ERROR : FUNCTION_TYPE( None, _simple.GLenum )
    }
    def addCallback( self, which, function ):
        """Register a callback for the quadric object
        
        At the moment only GLU_ERROR is supported by OpenGL, but
        we allow for the possibility of more callbacks in the future...
        """
        callbackType = self.CALLBACK_TYPES.get( which )
        if not callbackType:
            raise ValueError(
                """Don't have a registered callback type for %r"""%(
                    which,
                )
            )
        if not isinstance( function, callbackType ):
            cCallback = callbackType( function )
        else:
            cCallback = function
        PLATFORM.GLU.gluQuadricCallback( self, which, cCallback )
        # XXX catch errors!
        if getattr( self, 'callbacks', None ) is None:
            self.callbacks = {}
        self.callbacks[ which ] = cCallback
        return cCallback
GLUquadric = GLUQuadric

def gluQuadricCallback( quadric, which=_simple.GLU_ERROR, function=None ):
    """Set the GLU error callback function"""
    return quadric.addCallback( which, function )

# Override to produce instances of the sub-class...
gluNewQuadric = createBaseFunction( 
    'gluNewQuadric', dll=PLATFORM.GLU, resultType=ctypes.POINTER(GLUQuadric), 
    argTypes=[],
    doc="""gluNewQuadric(  ) -> GLUQuadric
    
Create a new GLUQuadric object""", 
    argNames=[],
)

__all__ = (
    'gluNewQuadric',
    'gluQuadricCallback',
    'GLUQuadric',
)
