"""OSMesa-specific features

To request an OSMesa context, you need to run your script with:

    PYOPENGL_PLATFORM=osmesa

defined in your shell/execution environment.
"""
import ctypes, ctypes.util
from OpenGL.platform import baseplatform, ctypesloader
from OpenGL.constant import Constant
from OpenGL.raw.osmesa import _types

class OSMesaPlatform( baseplatform.BasePlatform ):
    """OSMesa implementation for PyOpenGL"""
    EXPORTED_NAMES = baseplatform.BasePlatform.EXPORTED_NAMES[:] + [
        'OSMesa',
    ]
    @baseplatform.lazy_property
    def GL(self):
        try:
            return ctypesloader.loadLibrary(
                ctypes.cdll,
                'OSMesa', 
                mode=ctypes.RTLD_GLOBAL 
            ) 
        except OSError as err:
            raise ImportError("Unable to load OpenGL library", *err.args)
    @baseplatform.lazy_property
    def GLU(self):
        try:
            return ctypesloader.loadLibrary(
                ctypes.cdll,
                'GLU',
                mode=ctypes.RTLD_GLOBAL 
            )
        except OSError as err:
            return None
    @baseplatform.lazy_property
    def GLUT( self ):
        try:
            return ctypesloader.loadLibrary(
                ctypes.cdll,
                'glut', 
                mode=ctypes.RTLD_GLOBAL 
            )
        except OSError as err:
            return None
    @baseplatform.lazy_property
    def GLE( self ):
        try:
            return ctypesloader.loadLibrary(
                ctypes.cdll,
                'gle', 
                mode=ctypes.RTLD_GLOBAL 
            )
        except OSError as err:
            return None
    @baseplatform.lazy_property
    def OSMesa( self ): return self.GL
        
    DEFAULT_FUNCTION_TYPE = staticmethod( ctypes.CFUNCTYPE )

    @baseplatform.lazy_property
    def GetCurrentContext( self ):
        function = self.OSMesa.OSMesaGetCurrentContext
        function.restype = _types.OSMesaContext
        return function
    @baseplatform.lazy_property
    def CurrentContextIsValid( self ): return self.GetCurrentContext
    
    @baseplatform.lazy_property
    def getExtensionProcedure( self ):
        function = self.OSMesa.OSMesaGetProcAddress
        function.restype = ctypes.c_void_p
        return function

    def getGLUTFontPointer( self, constant ):
        """Platform specific function to retrieve a GLUT font pointer
        
        GLUTAPI void *glutBitmap9By15;
        #define GLUT_BITMAP_9_BY_15		(&glutBitmap9By15)
        
        Key here is that we want the addressof the pointer in the DLL,
        not the pointer in the DLL.  That is, our pointer is to the 
        pointer defined in the DLL, we don't want the *value* stored in
        that pointer.
        """
        name = [ x.title() for x in constant.split( '_' )[1:] ]
        internal = 'glut' + "".join( [x.title() for x in name] )
        pointer = ctypes.c_void_p.in_dll( self.GLUT, internal )
        return ctypes.c_void_p(ctypes.addressof(pointer))
