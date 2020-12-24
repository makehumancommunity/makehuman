"""GLX (x-windows)-specific platform features"""
import ctypes, ctypes.util
from OpenGL.platform import baseplatform, ctypesloader

class GLXPlatform( baseplatform.BasePlatform ):
    """Posix (Linux, FreeBSD, etceteras) implementation for PyOpenGL"""
    # On Linux (and, I assume, most GLX platforms, we have to load 
    # GL and GLU with the "global" flag to allow GLUT to resolve its
    # references to GL/GLU functions).
    @baseplatform.lazy_property
    def GL(self):
        try:
            return ctypesloader.loadLibrary(
                ctypes.cdll,
                'GL', 
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
        except OSError:
            return None
    @baseplatform.lazy_property
    def GLUT( self ):
        try:
            return ctypesloader.loadLibrary(
                ctypes.cdll,
                'glut', 
                mode=ctypes.RTLD_GLOBAL 
            )
        except OSError:
            return None
    # GLX doesn't seem to have its own loadable module?
    @baseplatform.lazy_property
    def GLX(self): return self.GL

    @baseplatform.lazy_property
    def GLES1(self):
        try:
            return ctypesloader.loadLibrary(
                ctypes.cdll,
                'GLESv1_CM', # ick
                mode=ctypes.RTLD_GLOBAL 
            )
        except OSError:
            return None
    @baseplatform.lazy_property
    def GLES2(self):
        try:
            return ctypesloader.loadLibrary(
                ctypes.cdll,
                'GLESv2', 
                mode=ctypes.RTLD_GLOBAL 
            )
        except OSError:
            return None
    @baseplatform.lazy_property
    def GLES3(self):
        # implementers guide says to use the same name for the DLL
        return self.GLES2
    
    @baseplatform.lazy_property
    def glXGetProcAddressARB(self):
        base = self.GLX.glXGetProcAddressARB
        base.restype = ctypes.c_void_p
        return base
    @baseplatform.lazy_property
    def getExtensionProcedure(self):
        return self.glXGetProcAddressARB
    
    @baseplatform.lazy_property
    def GLE( self ):
        try:
            return ctypesloader.loadLibrary(
                ctypes.cdll,
                'gle', 
                mode=ctypes.RTLD_GLOBAL 
            )
        except OSError:
            return None

    DEFAULT_FUNCTION_TYPE = staticmethod( ctypes.CFUNCTYPE )

    # This loads the GLX functions from the GL .so, not sure if that's
    # really kosher...
    @baseplatform.lazy_property
    def GetCurrentContext( self ):
        return self.GL.glXGetCurrentContext

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
    
    @baseplatform.lazy_property
    def glGetError( self ):
        return self.GL.glGetError
    
