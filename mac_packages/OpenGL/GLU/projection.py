"""glu[Un]Project[4] convenience wrappers"""
from OpenGL.raw import GLU as _simple
from OpenGL import GL
from OpenGL.lazywrapper import lazy as _lazy
import ctypes 
POINTER = ctypes.POINTER

@_lazy( _simple.gluProject )
def gluProject( baseFunction, objX, objY, objZ, model=None, proj=None, view=None ):
    """Convenience wrapper for gluProject
    
    Automatically fills in the model, projection and viewing matrices
    if not provided.
    
    returns (winX,winY,winZ) doubles
    """
    if model is None:
        model = GL.glGetDoublev( GL.GL_MODELVIEW_MATRIX )
    if proj is None:
        proj = GL.glGetDoublev( GL.GL_PROJECTION_MATRIX )
    if view is None:
        view = GL.glGetIntegerv( GL.GL_VIEWPORT )
    winX = _simple.GLdouble( 0.0 )
    winY = _simple.GLdouble( 0.0 )
    winZ = _simple.GLdouble( 0.0 )
    result = baseFunction( 
        objX,objY,objZ,
        model,proj,view,
        winX,winY,winZ,
    )
    # On Ubuntu 9.10 we see a None come out of baseFunction,
    # despite it having a return-type specified of GLint!
    if result is not None and result != _simple.GLU_TRUE:
        raise ValueError( """Projection failed!""" )
    return winX.value, winY.value, winZ.value 

@_lazy( _simple.gluUnProject )
def gluUnProject( baseFunction, winX, winY, winZ, model=None, proj=None, view=None ):
    """Convenience wrapper for gluUnProject
    
    Automatically fills in the model, projection and viewing matrices
    if not provided.
    
    returns (objX,objY,objZ) doubles
    """
    if model is None:
        model = GL.glGetDoublev( GL.GL_MODELVIEW_MATRIX )
    if proj is None:
        proj = GL.glGetDoublev( GL.GL_PROJECTION_MATRIX )
    if view is None:
        view = GL.glGetIntegerv( GL.GL_VIEWPORT )
    objX = _simple.GLdouble( 0.0 )
    objY = _simple.GLdouble( 0.0 )
    objZ = _simple.GLdouble( 0.0 )
    result = baseFunction( 
        winX,winY,winZ,
        model,proj,view,
        ctypes.byref(objX),ctypes.byref(objY),ctypes.byref(objZ),
    )
    if not result:
        raise ValueError( """Projection failed!""" )
    return objX.value, objY.value, objZ.value 
@_lazy( _simple.gluUnProject4 )
def gluUnProject4(
    baseFunction,
    winX, winY, winZ, clipW, 
    model=None, proj=None, view=None, 
    near=0.0, far=1.0
):
    """Convenience wrapper for gluUnProject
    
    Automatically fills in the model, projection and viewing matrices
    if not provided.
    
    returns (objX,objY,objZ) doubles
    """
    if model is None:
        model = GL.glGetDoublev( GL.GL_MODELVIEW_MATRIX )
    if proj is None:
        proj = GL.glGetDoublev( GL.GL_PROJECTION_MATRIX )
    if view is None:
        view = GL.glGetIntegerv( GL.GL_VIEWPORT )
    objX = _simple.GLdouble( 0.0 )
    objY = _simple.GLdouble( 0.0 )
    objZ = _simple.GLdouble( 0.0 )
    objW = _simple.GLdouble( 0.0 )
    result = baseFunction( 
        winX,winY,winZ,
        model,proj,view,
        ctypes.byref(objX),ctypes.byref(objY),ctypes.byref(objZ),ctypes.byref(objW)
    )
    if not result:
        raise ValueError( """Projection failed!""" )
    return objX.value, objY.value, objZ.value, objW.value

__all__ = (
    'gluProject',
    'gluUnProject',
    'gluUnProject4',
)
