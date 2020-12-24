from ctypes import *
from ctypes import _SimpleCData, _check_size
from OpenGL import extensions
from OpenGL.raw.GL._types import *
from OpenGL._bytes import as_8_bit
from OpenGL._opaque import opaque_pointer_cls as _opaque_pointer_cls
c_void = None

class _WGLQuerier( extensions.ExtensionQuerier ):
    prefix = b'WGL_'
    assumed_version = [1,0]
    version_prefix = b'WGL_VERSION_WGL_'
    def pullVersion( self ):
        # only one version...
        return [1,0]
    def pullExtensions( self ):
        from OpenGL.platform import PLATFORM
        wglGetCurrentDC = PLATFORM.OpenGL.wglGetCurrentDC
        wglGetCurrentDC.restyle = HDC
        try:
            dc = wglGetCurrentDC()
            proc_address = PLATFORM.getExtensionProcedure(b'wglGetExtensionsStringARB')
            wglGetExtensionStringARB = PLATFORM.functionTypeFor( PLATFORM.WGL )(
                c_char_p,
                HDC,
            )( proc_address )
        except TypeError as err:
            return None
        except AttributeError as err:
            return []
        else:
            return wglGetExtensionStringARB(dc).split()
WGLQuerier=_WGLQuerier()

INT8 = c_char 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:35
PINT8 = c_char_p 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:35
INT16 = c_short 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:36
PINT16 = POINTER(c_short) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:36
INT32 = c_int 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:37
PINT32 = POINTER(c_int) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:37
UINT8 = c_ubyte 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:38
PUINT8 = POINTER(c_ubyte) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:38
UINT16 = c_ushort 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:39
PUINT16 = POINTER(c_ushort) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:39
UINT32 = c_uint 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:40
PUINT32 = POINTER(c_uint) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:40
LONG32 = c_int 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:41
PLONG32 = POINTER(c_int) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:41
ULONG32 = c_uint 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:42
PULONG32 = POINTER(c_uint) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:42
DWORD32 = c_uint 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:43
PDWORD32 = POINTER(c_uint) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:43
INT64 = c_longlong 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:44
PINT64 = POINTER(c_longlong) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:44
UINT64 = c_ulonglong 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:45
PUINT64 = POINTER(c_ulonglong) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:45
VOID = None 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:47
LPVOID = POINTER(None) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:47
LPCSTR = c_char_p 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:48
CHAR = c_char 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:49
BYTE = c_ubyte 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:50
WORD = c_ushort 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:51
USHORT = c_ushort 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:51
UINT = c_uint 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:52
INT = c_int 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:53
INT_PTR = POINTER(c_int) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:53
BOOL = c_long 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:54
LONG = c_long 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:55
DWORD = c_ulong 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:56
FLOAT = c_float 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:57
COLORREF = DWORD 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:58
LPCOLORREF = POINTER(DWORD) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:58

#HANDLE = POINTER(None) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:60
# TODO: figure out how to make the handle not appear as a void_p within the code...
# This decorates *every* c_void_p reference, as ctypes now reuses the references
# which means it completely disables all of the array-handing machinery
class HANDLE(_SimpleCData):
    """Github Issue #8 CTypes shares all references to c_void_p
    
    We have to have a separate type to avoid short-circuiting all
    of the array-handling machinery for real c_void_p arguments.
    """
    _type_ = "P"
_check_size(HANDLE)
HANDLE.final = True

HGLRC = HANDLE 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:62
HDC = HANDLE 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:63
PROC = CFUNCTYPE(INT_PTR) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:65
HPBUFFERARB = HANDLE
HPBUFFEREXT = HANDLE

class struct__POINTFLOAT(Structure):
    __slots__ = [
        'x',
        'y',
    ]
struct__POINTFLOAT._fields_ = [
    ('x', FLOAT),
    ('y', FLOAT),
]

POINTFLOAT = struct__POINTFLOAT 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:83
PPOINTFLOAT = POINTER(struct__POINTFLOAT) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:83
class struct__GLYPHMETRICSFLOAT(Structure):
    __slots__ = [
        'gmfBlackBoxX',
        'gmfBlackBoxY',
        'gmfptGlyphOrigin',
        'gmfCellIncX',
        'gmfCellIncY',
    ]
struct__GLYPHMETRICSFLOAT._fields_ = [
    ('gmfBlackBoxX', FLOAT),
    ('gmfBlackBoxY', FLOAT),
    ('gmfptGlyphOrigin', POINTFLOAT),
    ('gmfCellIncX', FLOAT),
    ('gmfCellIncY', FLOAT),
]

GLYPHMETRICSFLOAT = struct__GLYPHMETRICSFLOAT 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:91
PGLYPHMETRICSFLOAT = POINTER(struct__GLYPHMETRICSFLOAT) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:91
LPGLYPHMETRICSFLOAT = POINTER(struct__GLYPHMETRICSFLOAT) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:91

class struct_tagLAYERPLANEDESCRIPTOR(Structure):
    __slots__ = [
        'nSize',
        'nVersion',
        'dwFlags',
        'iPixelType',
        'cColorBits',
        'cRedBits',
        'cRedShift',
        'cGreenBits',
        'cGreenShift',
        'cBlueBits',
        'cBlueShift',
        'cAlphaBits',
        'cAlphaShift',
        'cAccumBits',
        'cAccumRedBits',
        'cAccumGreenBits',
        'cAccumBlueBits',
        'cAccumAlphaBits',
        'cDepthBits',
        'cStencilBits',
        'cAuxBuffers',
        'iLayerPlane',
        'bReserved',
        'crTransparent',
    ]
struct_tagLAYERPLANEDESCRIPTOR._fields_ = [
    ('nSize', WORD),
    ('nVersion', WORD),
    ('dwFlags', DWORD),
    ('iPixelType', BYTE),
    ('cColorBits', BYTE),
    ('cRedBits', BYTE),
    ('cRedShift', BYTE),
    ('cGreenBits', BYTE),
    ('cGreenShift', BYTE),
    ('cBlueBits', BYTE),
    ('cBlueShift', BYTE),
    ('cAlphaBits', BYTE),
    ('cAlphaShift', BYTE),
    ('cAccumBits', BYTE),
    ('cAccumRedBits', BYTE),
    ('cAccumGreenBits', BYTE),
    ('cAccumBlueBits', BYTE),
    ('cAccumAlphaBits', BYTE),
    ('cDepthBits', BYTE),
    ('cStencilBits', BYTE),
    ('cAuxBuffers', BYTE),
    ('iLayerPlane', BYTE),
    ('bReserved', BYTE),
    ('crTransparent', COLORREF),
]

LAYERPLANEDESCRIPTOR = struct_tagLAYERPLANEDESCRIPTOR 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:127
PLAYERPLANEDESCRIPTOR = POINTER(struct_tagLAYERPLANEDESCRIPTOR) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:127
LPLAYERPLANEDESCRIPTOR = POINTER(struct_tagLAYERPLANEDESCRIPTOR) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:127

class struct__WGLSWAP(Structure):
    __slots__ = [
        'hdc',
        'uiFlags',
    ]
struct__WGLSWAP._fields_ = [
    ('hdc', HDC),
    ('uiFlags', UINT),
]

WGLSWAP = struct__WGLSWAP 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:190
PWGLSWAP = POINTER(struct__WGLSWAP) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:190
LPWGLSWAP = POINTER(struct__WGLSWAP) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:190

class struct_tagRECT(Structure):
    __slots__ = [
        'left',
        'top',
        'right',
        'bottom',
    ]
struct_tagRECT._fields_ = [
    ('left', LONG),
    ('top', LONG),
    ('right', LONG),
    ('bottom', LONG),
]

RECT = struct_tagRECT 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:202
PRECT = POINTER(struct_tagRECT) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:202
NPRECT = POINTER(struct_tagRECT) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:202
LPRECT = POINTER(struct_tagRECT) 	# /home/mcfletch/pylive/OpenGL-ctypes/src/wgl.h:202

class PIXELFORMATDESCRIPTOR(Structure):
    _fields_ = [
        ('nSize',WORD),
        ('nVersion',WORD),
        ('dwFlags',DWORD),
        ('iPixelType',BYTE),
        ('cColorBits',BYTE),
        ('cRedBits',BYTE),
        ('cRedShift',BYTE),
        ('cGreenBits',BYTE),
        ('cGreenShift',BYTE),
        ('cBlueBits',BYTE),
        ('cBlueShift',BYTE),
        ('cAlphaBits',BYTE),
        ('cAlphaShift',BYTE),
        ('cAccumBits',BYTE),
        ('cAccumRedBits',BYTE),
        ('cAccumGreenBits',BYTE),
        ('cAccumBlueBits',BYTE),
        ('cAccumAlphaBits',BYTE),
        ('cAccumDepthBits',BYTE),
        ('cAccumStencilBits',BYTE),
        ('cAuxBuffers',BYTE),
        ('iLayerType',BYTE),
        ('bReserved',BYTE),
        ('dwLayerMask',DWORD),
        ('dwVisibleMask',DWORD),
        ('dwDamageMask',DWORD),
    ]

# TODO: This is *not* a working definition, calling any function with this will segfault
HENHMETAFILE = _opaque_pointer_cls( 'HENHMETAFILE' )
