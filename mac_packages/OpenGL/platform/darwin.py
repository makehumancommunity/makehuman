"""Darwin (MacOSX)-specific platform features

This was implemented with the help of the following links:
[1] Apple's Mac OS X OpenGL interfaces: http://developer.apple.com/qa/qa2001/qa1269.html
[2] As above, but updated: http://developer.apple.com/documentation/GraphicsImaging/Conceptual/OpenGL-MacProgGuide/opengl_pg_concepts/chapter_2_section_3.html
[3] CGL reference: http://developer.apple.com/documentation/GraphicsImaging/Reference/CGL_OpenGL/index.html#//apple_ref/doc/uid/TP40001186
[4] Intro to OpenGL on Mac OS X: http://developer.apple.com/documentation/GraphicsImaging/Conceptual/OpenGL-MacProgGuide/opengl_intro/chapter_1_section_1.html#//apple_ref/doc/uid/TP40001987-CH207-TP9

About the  CGL API, (from [1]):
CGL or Core OpenGL is the lowest accessible interface API for OpenGL. 
It knows nothing about windowing systems but can be used directly to 
find both renderer information and as a full screen or off screen 
interface. It is accessible from both Cocoa and Carbon and is what both 
NSGL and AGL are built on. A complete Pbuffer interface is also provided. 
Functionality is provided in via the OpenGL framework and applications 
can include the OpenGL.h header to access CGL's functionality. Developers
can see an example of using CGL with Carbon in the Carbon CGL code sample.

Documentation and header files are found in:
/System/Library/Frameworks/OpenGL.framework
/System/Library/Frameworks/GLUT.framework

"""
import ctypes, ctypes.util
from OpenGL.platform import baseplatform, ctypesloader

class DarwinPlatform( baseplatform.BasePlatform ):
    """Darwin (OSX) platform implementation"""
    DEFAULT_FUNCTION_TYPE = staticmethod( ctypes.CFUNCTYPE )
    EXTENSIONS_USE_BASE_FUNCTIONS = True

    @baseplatform.lazy_property
    def GL(self):
        try:
            return ctypesloader.loadLibrary(
                ctypes.cdll,
                'OpenGL', 
                mode=ctypes.RTLD_GLOBAL 
            ) 
        except OSError as err:
            raise ImportError("Unable to load OpenGL library", *err.args)
    @baseplatform.lazy_property
    def GLU(self): return self.GL
    @baseplatform.lazy_property
    def CGL(self): return self.GL

    @baseplatform.lazy_property
    def GLUT( self ):
        try:
            return ctypesloader.loadLibrary(
                ctypes.cdll,
                'GLUT', 
                mode=ctypes.RTLD_GLOBAL 
            )
        except OSError:
            return None
    @baseplatform.lazy_property
    def GLE(self): return self.GLUT

    @baseplatform.lazy_property
    def GetCurrentContext( self ):
        return self.CGL.CGLGetCurrentContext 

    def getGLUTFontPointer( self, constant ):
        """Platform specific function to retrieve a GLUT font pointer
        
        GLUTAPI void *glutBitmap9By15;
        #define GLUT_BITMAP_9_BY_15     (&glutBitmap9By15)
        
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

