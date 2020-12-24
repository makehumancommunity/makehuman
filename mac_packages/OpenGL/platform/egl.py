"""EGL (cross-platform) platform library"""
import ctypes, ctypes.util
from OpenGL.platform import baseplatform, ctypesloader

class EGLPlatform( baseplatform.BasePlatform ):
    """EGL platform for opengl-es only platforms"""
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
    def GL(self):
        try:
            for name in ('OpenGL','GL'):
                lib = ctypesloader.loadLibrary(
                    ctypes.cdll,
                    'GL', 
                    mode=ctypes.RTLD_GLOBAL 
                )
                if lib:
                    return lib 
            raise OSError("No GL/OpenGL library available")
        except OSError:
            return self.GLES2 or self.GLES1
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
    @baseplatform.lazy_property
    def OpenGL(self): return self.GL
    
    @baseplatform.lazy_property
    def EGL(self):
        # TODO: the raspberry pi crashes on trying to load EGL module 
        # because the EGL library requires a structure from GLES2 without 
        # linking to that library... Github issue is here:
        #   https://github.com/raspberrypi/firmware/issues/110
        import os
        if os.path.exists('/proc/cpuinfo'):
            info = open('/proc/cpuinfo').read()
            if 'BCM2708' in info or 'BCM2709' in info:
                assert self.GLES2
        try:
            return ctypesloader.loadLibrary(
                ctypes.cdll,
                'EGL', 
                mode=ctypes.RTLD_GLOBAL 
            )
        except OSError as err:
            raise ImportError("Unable to load EGL library", *err.args)
    @baseplatform.lazy_property
    def getExtensionProcedure( self ):
        eglGetProcAddress = self.EGL.eglGetProcAddress
        eglGetProcAddress.restype = ctypes.c_void_p
        return eglGetProcAddress
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
    @baseplatform.lazy_property
    def GetCurrentContext( self ):
        return self.EGL.eglGetCurrentContext
