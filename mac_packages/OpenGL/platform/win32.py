"""Windows-specific platform features"""
import ctypes
import platform
from OpenGL.platform import ctypesloader, baseplatform
import sys

if sys.hexversion < 0x2070000:
    vc = 'vc7'
elif sys.hexversion >= 0x3050000:
    vc = 'vc14'
elif sys.hexversion >= 0x3030000:
    vc = 'vc10'
else:
    vc = 'vc9'

def _size():
    return platform.architecture()[0].strip( 'bits' )
size = _size()

class Win32Platform( baseplatform.BasePlatform ):
    """Win32-specific platform implementation"""

    GLUT_GUARD_CALLBACKS = True
    @baseplatform.lazy_property
    def GL(self):
        try:
            return ctypesloader.loadLibrary(
                ctypes.windll, 'opengl32', mode = ctypes.RTLD_GLOBAL
            ) 
        except OSError as err:
            raise ImportError("Unable to load OpenGL library", *err.args)
    @baseplatform.lazy_property
    def GLU(self):
        try:
            return ctypesloader.loadLibrary(
                ctypes.windll, 'glu32', mode = ctypes.RTLD_GLOBAL
            )
        except OSError:
            return None
    @baseplatform.lazy_property
    def GLUT( self ):
        for possible in ('freeglut%s.%s'%(size,vc,), 'glut%s.%s'%(size,vc,)):
            # Prefer FreeGLUT if the user has installed it, fallback to the included 
            # GLUT if it is installed
            try:
                return ctypesloader.loadLibrary(
                    ctypes.windll, possible, mode = ctypes.RTLD_GLOBAL
                )
            except WindowsError:
                pass
        return None
    @baseplatform.lazy_property
    def GLE( self ):
        for libName in ('gle%s.%s'%(size,vc,), 'opengle%s.%s'%(size,vc,)):
            try:
                GLE = ctypesloader.loadLibrary( ctypes.cdll, libName )
                GLE.FunctionType = ctypes.CFUNCTYPE
                return GLE
            except WindowsError:
                pass
            else:
                break
        return None

    DEFAULT_FUNCTION_TYPE = staticmethod( ctypes.WINFUNCTYPE )
    # Win32 GLUT uses different types for callbacks and functions...
    GLUT_CALLBACK_TYPE = staticmethod( ctypes.CFUNCTYPE )
    GDI32 = ctypes.windll.gdi32
    @baseplatform.lazy_property
    def WGL( self ):
        return self.OpenGL
    @baseplatform.lazy_property
    def getExtensionProcedure( self ):
        wglGetProcAddress = self.OpenGL.wglGetProcAddress
        wglGetProcAddress.restype = ctypes.c_void_p
        return wglGetProcAddress

    GLUT_FONT_CONSTANTS = {
        'GLUT_STROKE_ROMAN': ctypes.c_void_p( 0),
        'GLUT_STROKE_MONO_ROMAN': ctypes.c_void_p( 1),
        'GLUT_BITMAP_9_BY_15': ctypes.c_void_p( 2),
        'GLUT_BITMAP_8_BY_13': ctypes.c_void_p( 3),
        'GLUT_BITMAP_TIMES_ROMAN_10': ctypes.c_void_p( 4),
        'GLUT_BITMAP_TIMES_ROMAN_24': ctypes.c_void_p( 5),
        'GLUT_BITMAP_HELVETICA_10': ctypes.c_void_p( 6),
        'GLUT_BITMAP_HELVETICA_12': ctypes.c_void_p( 7),
        'GLUT_BITMAP_HELVETICA_18': ctypes.c_void_p( 8),
    }


    def getGLUTFontPointer( self,constant ):
        """Platform specific function to retrieve a GLUT font pointer

        GLUTAPI void *glutBitmap9By15;
        #define GLUT_BITMAP_9_BY_15		(&glutBitmap9By15)

        Key here is that we want the addressof the pointer in the DLL,
        not the pointer in the DLL.  That is, our pointer is to the
        pointer defined in the DLL, we don't want the *value* stored in
        that pointer.
        """
        return self.GLUT_FONT_CONSTANTS[ constant ]

    @baseplatform.lazy_property
    def GetCurrentContext( self ):
        wglGetCurrentContext = self.GL.wglGetCurrentContext
        wglGetCurrentContext.restype = ctypes.c_void_p
        return wglGetCurrentContext

    def constructFunction(
        self,
        functionName, dll, 
        resultType=ctypes.c_int, argTypes=(),
        doc = None, argNames = (),
        extension = None,
        deprecated = False,
        module = None,
        force_extension = False,
        error_checker = None,
    ):
        """Override construct function to do win32-specific hacks to find entry points"""
        try:
            return super( Win32Platform, self ).constructFunction(
                functionName, dll,
                resultType, argTypes,
                doc, argNames,
                extension,
                deprecated,
                module,
                error_checker=error_checker,
            )
        except AttributeError:
            try:
                return super( Win32Platform, self ).constructFunction(
                    functionName, self.GDI32,
                    resultType, argTypes,
                    doc, argNames,
                    extension,
                    deprecated,
                    module,
                    error_checker=error_checker,
                )
            except AttributeError:
                return super( Win32Platform, self ).constructFunction(
                    functionName, dll,
                    resultType, argTypes,
                    doc, argNames,
                    extension,
                    deprecated,
                    module,
                    force_extension = True,
                    error_checker=error_checker,
                )
            
