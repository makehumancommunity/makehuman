from OpenGL import platform as _p, constant, extensions
from ctypes import *
from OpenGL.raw.GL._types import *
from OpenGL._bytes import as_8_bit
c_void = None
void = None 
Bool = c_uint

class _GLXQuerier( extensions.ExtensionQuerier ):
    prefix = as_8_bit('GLX_')
    assumed_version = [1,1]
    version_prefix = as_8_bit('GLX_VERSION_GLX_')
    def getDisplay( self ):
        from OpenGL.raw.GLX import _types
        from OpenGL.platform import ctypesloader
        import ctypes, os
        X11 = ctypesloader.loadLibrary( ctypes.cdll, 'X11' )
        XOpenDisplay = X11.XOpenDisplay 
        XOpenDisplay.restype = ctypes.POINTER(_types.Display)
        return XOpenDisplay( os.environ.get( 'DISPLAY' ))
    def getScreen( self, display ):
        from OpenGL.platform import ctypesloader
        from OpenGL.raw.GLX import _types
        import ctypes, os
        X11 = ctypesloader.loadLibrary( ctypes.cdll, 'X11' )
        XDefaultScreen = X11.XDefaultScreen
        XDefaultScreen.argtypes = [ctypes.POINTER(_types.Display)]
        return XDefaultScreen( display )
        
    def pullVersion( self ):
        from OpenGL.GLX import glXQueryVersion
        import ctypes
        if glXQueryVersion:
            display = self.getDisplay()
            major,minor = ctypes.c_int(),ctypes.c_int()
            glXQueryVersion(display, major, minor)
            return [major.value,minor.value]
        else:
            return [1,1]
    def pullExtensions( self ):
        if self.getVersion() >= [1,2]:
            from OpenGL.GLX import glXQueryExtensionsString
            display = self.getDisplay()
            screen = self.getScreen( display )
            
            if glXQueryExtensionsString:
                return glXQueryExtensionsString( display,screen ).split()
        return []
GLXQuerier=_GLXQuerier()


class struct___GLXcontextRec(Structure):
    __slots__ = [
    ]
struct___GLXcontextRec._fields_ = [
    ('_opaque_struct', c_int)
]

class struct___GLXcontextRec(Structure):
    __slots__ = [
    ]
struct___GLXcontextRec._fields_ = [
    ('_opaque_struct', c_int)
]

GLXContext = POINTER(struct___GLXcontextRec) 	# /usr/include/GL/glx.h:178
XID = c_ulong 	# /usr/include/X11/X.h:66
GLXPixmap = XID 	# /usr/include/GL/glx.h:179
GLXDrawable = XID 	# /usr/include/GL/glx.h:180
class struct___GLXFBConfigRec(Structure):
    __slots__ = [
    ]
struct___GLXFBConfigRec._fields_ = [
    ('_opaque_struct', c_int)
]

class struct___GLXFBConfigRec(Structure):
    __slots__ = [
    ]
struct___GLXFBConfigRec._fields_ = [
    ('_opaque_struct', c_int)
]

GLXFBConfig = POINTER(struct___GLXFBConfigRec) 	# /usr/include/GL/glx.h:182
GLXFBConfigID = XID 	# /usr/include/GL/glx.h:183
GLXContextID = XID 	# /usr/include/GL/glx.h:184
GLXWindow = XID 	# /usr/include/GL/glx.h:185
GLXPbuffer = XID 	# /usr/include/GL/glx.h:186
GLXPbufferSGIX = XID
GLXVideoSourceSGIX = XID

class struct_anon_103(Structure):
    __slots__ = [
        'visual',
        'visualid',
        'screen',
        'depth',
        'class',
        'red_mask',
        'green_mask',
        'blue_mask',
        'colormap_size',
        'bits_per_rgb',
    ]
class struct_anon_18(Structure):
    __slots__ = [
        'ext_data',
        'visualid',
        'class',
        'red_mask',
        'green_mask',
        'blue_mask',
        'bits_per_rgb',
        'map_entries',
    ]
class struct__XExtData(Structure):
    __slots__ = [
        'number',
        'next',
        'free_private',
        'private_data',
    ]
XPointer = c_char_p 	# /usr/include/X11/Xlib.h:84
struct__XExtData._fields_ = [
    ('number', c_int),
    ('next', POINTER(struct__XExtData)),
    ('free_private', POINTER(CFUNCTYPE(c_int, POINTER(struct__XExtData)))),
    ('private_data', XPointer),
]

XExtData = struct__XExtData 	# /usr/include/X11/Xlib.h:163
VisualID = c_ulong 	# /usr/include/X11/X.h:76
struct_anon_18._fields_ = [
    ('ext_data', POINTER(XExtData)),
    ('visualid', VisualID),
    ('class', c_int),
    ('red_mask', c_ulong),
    ('green_mask', c_ulong),
    ('blue_mask', c_ulong),
    ('bits_per_rgb', c_int),
    ('map_entries', c_int),
]

Visual = struct_anon_18 	# /usr/include/X11/Xlib.h:246
struct_anon_103._fields_ = [
    ('visual', POINTER(Visual)),
    ('visualid', VisualID),
    ('screen', c_int),
    ('depth', c_int),
    ('class', c_int),
    ('red_mask', c_ulong),
    ('green_mask', c_ulong),
    ('blue_mask', c_ulong),
    ('colormap_size', c_int),
    ('bits_per_rgb', c_int),
]

XVisualInfo = struct_anon_103 	# /usr/include/X11/Xutil.h:294
class struct__XDisplay(Structure):
    __slots__ = [
    ]
struct__XDisplay._fields_ = [
    ('_opaque_struct', c_int)
]

class struct__XDisplay(Structure):
    __slots__ = [
    ]
struct__XDisplay._fields_ = [
    ('_opaque_struct', c_int)
]

Display = struct__XDisplay 	# /usr/include/X11/Xlib.h:495

Pixmap = XID 	# /usr/include/X11/X.h:102
Font = XID 	# /usr/include/X11/X.h:100
Window = XID 	# /usr/include/X11/X.h:96
GLX_ARB_get_proc_address = constant.Constant( 'GLX_ARB_get_proc_address', 1 )
__GLXextFuncPtr = CFUNCTYPE(None) 	# /usr/include/GL/glx.h:330

# EXT_texture_from_pixmap (/usr/include/GL/glx.h:436)
class struct_anon_111(Structure):
    __slots__ = [
        'event_type',
        'draw_type',
        'serial',
        'send_event',
        'display',
        'drawable',
        'buffer_mask',
        'aux_buffer',
        'x',
        'y',
        'width',
        'height',
        'count',
    ]
struct_anon_111._fields_ = [
    ('event_type', c_int),
    ('draw_type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('drawable', GLXDrawable),
    ('buffer_mask', c_uint),
    ('aux_buffer', c_uint),
    ('x', c_int),
    ('y', c_int),
    ('width', c_int),
    ('height', c_int),
    ('count', c_int),
]

GLXPbufferClobberEvent = struct_anon_111 	# /usr/include/GL/glx.h:502
class struct_anon_112(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'drawable',
        'event_type',
        'ust',
        'msc',
        'sbc',
    ]
struct_anon_112._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('drawable', GLXDrawable),
    ('event_type', c_int),
    ('ust', c_int64),
    ('msc', c_int64),
    ('sbc', c_int64),
]

GLXBufferSwapComplete = struct_anon_112 	# /usr/include/GL/glx.h:514
class struct___GLXEvent(Union):
    __slots__ = [
        'glxpbufferclobber',
        'glxbufferswapcomplete',
        'pad',
    ]
struct___GLXEvent._fields_ = [
    ('glxpbufferclobber', GLXPbufferClobberEvent),
    ('glxbufferswapcomplete', GLXBufferSwapComplete),
    ('pad', c_long * 24),
]

GLXEvent = struct___GLXEvent 	# /usr/include/GL/glx.h:520

class GLXHyperpipeConfigSGIX( Structure ):
    _fields_ = [
        ('pipeName', c_char * 80),
        ('channel',c_int),
        ('participationType',c_uint),
        ('timeSlice',c_int),
    ]

