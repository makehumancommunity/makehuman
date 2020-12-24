"""Extension module support methods

This module provides the tools required to check whether
an extension is available
"""
from OpenGL.latebind import LateBind
from OpenGL._bytes import bytes,unicode,as_8_bit
import OpenGL as root
import sys
import logging
_log = logging.getLogger( 'OpenGL.extensions' )
VERSION_PREFIX = as_8_bit('GL_VERSION_GL_')
CURRENT_GL_VERSION = None
AVAILABLE_GL_EXTENSIONS = []
AVAILABLE_GLU_EXTENSIONS = []

# version tuple -> list of implicitly included extensions...
VERSION_EXTENSIONS = [
    ((3,0), [
        as_8_bit('GL_ARB_vertex_array_object'),
        as_8_bit('GL_ARB_texture_buffer_object'),
        as_8_bit('GL_ARB_framebuffer_object'),
        as_8_bit('GL_ARB_map_buffer_range'),
    ]),
    ((3,1), [
        as_8_bit('GL_ARB_copy_buffer'),
        as_8_bit('GL_ARB_uniform_buffer_object'),
    ]),
    ((3,2), [
        as_8_bit('GL_ARB_draw_elements_base_vertex'),
        as_8_bit('GL_ARB_provoking_vertex'),
        as_8_bit('GL_ARB_sync'),
        as_8_bit('GL_ARB_texture_multisample'),
    ]),
    ((3,3), [
        as_8_bit('GL_ARB_texture_multisample'),
        as_8_bit('GL_ARB_blend_func_extended'),
        as_8_bit('GL_ARB_sampler_objects'),
        as_8_bit('GL_ARB_explicit_attrib_location'),
        as_8_bit('GL_ARB_occlusion_query2'),
        as_8_bit('GL_ARB_shader_bit_encoding'),
        as_8_bit('GL_ARB_texture_rgb10_a2ui'),
        as_8_bit('GL_ARB_texture_swizzle'),
        as_8_bit('GL_ARB_timer_query'),
        as_8_bit('GL_ARB_vertex_type_2_10_10_10_rev'),
    ]),
    ((4,0), [
        as_8_bit('GL_ARB_texture_query_lod'),
        as_8_bit('GL_ARB_draw_indirect'),
        as_8_bit('GL_ARB_gpu_shader5'),
        as_8_bit('GL_ARB_gpu_shader_fp64'),
        as_8_bit('GL_ARB_shader_subroutine'),
        as_8_bit('GL_ARB_tessellation_shader'),
        as_8_bit('GL_ARB_texture_buffer_object_rgb32'),
        as_8_bit('GL_ARB_texture_cube_map_array'),
        as_8_bit('GL_ARB_texture_gather'),
        as_8_bit('GL_ARB_transform_feedback2'),
        as_8_bit('GL_ARB_transform_feedback3'),
    ]),
    ((4,1), [
        as_8_bit('GL_ARB_ES2_compatibility'),
        as_8_bit('GL_ARB_get_program_binary'),
        as_8_bit('GL_ARB_separate_shader_objects'),
        as_8_bit('GL_ARB_shader_precision'),
        as_8_bit('GL_ARB_vertex_attrib_64bit'),
        as_8_bit('GL_ARB_viewport_array'),
    ]),
    ((4,2), [
        as_8_bit('GL_ARB_base_instance'),
        as_8_bit('GL_ARB_shading_language_420pack'),
        as_8_bit('GL_ARB_transform_feedback_instanced'),
        as_8_bit('GL_ARB_compressed_texture_pixel_storage'),
        as_8_bit('GL_ARB_conservative_depth'),
        as_8_bit('GL_ARB_internalformat_query'),
        as_8_bit('GL_ARB_map_buffer_alignment'),
        as_8_bit('GL_ARB_shader_atomic_counters'),
        as_8_bit('GL_ARB_shader_image_load_store'),
        as_8_bit('GL_ARB_shading_language_packing'),
        as_8_bit('GL_ARB_texture_storage'),
    ]),
]

class ExtensionQuerier( object ):
    prefix = None
    version_prefix = None
    assumed_version = [1,0]
    
    version = extensions = None
    version_string = extensions_string = None
    
    registered = []
    def __init__( self ):
        self.registered.append( self )
    
    @classmethod 
    def hasExtension( self, specifier ):
        for registered in self.registered:
            result = registered( specifier )
            if result:
                return result 
        return False
    
    def __call__( self, specifier ):
        specifier = as_8_bit(specifier).replace(as_8_bit('.'),as_8_bit('_'))
        if not specifier.startswith( as_8_bit(self.prefix) ):
            return None 
        
        if specifier.startswith( as_8_bit(self.version_prefix) ):
            specifier = [
                int(x)
                for x in specifier[ len(self.version_prefix):].split(as_8_bit('_'))
            ]
            if specifier[:2] <= self.assumed_version:
                return True
            version = self.getVersion()
            if not version:
                return version
            return specifier <= version
        else:
            extensions = self.getExtensions()
            return extensions and specifier in extensions
    def getVersion( self ):
        if not self.version:
            self.version = self.pullVersion()
        return self.version 
    def getExtensions( self ):
        if not self.extensions:
            self.extensions = self.pullExtensions()
        return self.extensions

class _GLQuerier( ExtensionQuerier ):
    prefix = as_8_bit('GL_')
    version_prefix = as_8_bit('GL_VERSION_GL_')
    assumed_version = [1,1]
    def pullVersion( self ):
        """Retrieve 2-int declaration of major/minor GL version

        returns [int(major),int(minor)] or False if not loaded
        """
        from OpenGL import platform
        if not platform.PLATFORM.CurrentContextIsValid():
            return False
        from OpenGL.raw.GL.VERSION.GL_1_1 import glGetString 
        from OpenGL.raw.GL.VERSION.GL_1_1 import GL_VERSION
        new = glGetString( GL_VERSION )
        
        self.version_string = new
        if new:
            return [
                int(x) for x in new.split(as_8_bit(' '),1)[0].split( as_8_bit('.') )
            ]
        else:
            return False # not yet loaded/supported
    def pullExtensions( self ):
        from OpenGL import platform
        if not platform.PLATFORM.CurrentContextIsValid():
            return False
        from OpenGL.raw.GL._types import GLint
        from OpenGL.raw.GL.VERSION.GL_1_1 import glGetString, glGetError
        from OpenGL.raw.GL.VERSION.GL_1_1 import GL_EXTENSIONS
        from OpenGL import error
        try:
            extensions = glGetString( GL_EXTENSIONS )
            if glGetError():
                raise error.GLError()
            if extensions:
                extensions = extensions.split()
            else:
                return False
        except (AttributeError, error.GLError):
            # OpenGL 3.0 deprecates glGetString( GL_EXTENSIONS )
            from OpenGL.raw.GL.VERSION.GL_3_0 import GL_NUM_EXTENSIONS, glGetStringi
            from OpenGL.raw.GL.VERSION.GL_1_1 import glGetIntegerv
            count = GLint()
            glGetIntegerv( GL_NUM_EXTENSIONS, count )
            extensions = []
            for i in range( count.value ):
                extension = glGetStringi( GL_EXTENSIONS, i )
                extensions.append(
                    extension
                )
        # Add included-by-reference extensions...
        version = self.getVersion()
        if not version:
            # should not be possible?
            return version 
        check = tuple( version[:2] )
        for (v,v_exts) in VERSION_EXTENSIONS:
            if v <= check:
                for v_ext in v_exts:
                    if v_ext not in extensions:
                        extensions.append( as_8_bit(v_ext) )
            else:
                break
        return extensions
GLQuerier = _GLQuerier()
class _GLUQuerier( ExtensionQuerier ):
    prefix = as_8_bit('GLU_')
    version_prefix = as_8_bit('GLU_VERSION_GL_')
    def pullVersion( self ):
        from OpenGL.GLU import gluGetString,GLU_VERSION
        return [
            int(x) for x in gluGetString( GLU_VERSION ).split(as_8_bit('_'))
            if x.isdigit()
        ]
    def pullExtensions( self ):
        from OpenGL.GLU import gluGetString,GLU_EXTENSIONS
        return gluGetString( GLU_EXTENSIONS ).split()
GLUQuerier = _GLUQuerier()

def hasExtension( specifier ):
    return ExtensionQuerier.hasExtension( specifier )
hasGLExtension = hasGLUExtension = hasExtension

class _Alternate( LateBind ):
    def __init__( self, name, *alternates ):
        """Initialize set of alternative implementations of the same function"""
        self.__name__ = name
        self._alternatives = alternates
        if root.MODULE_ANNOTATIONS:
            frame = sys._getframe().f_back
            if frame and frame.f_back and '__name__' in frame.f_back.f_globals:
                self.__module__ = frame.f_back.f_globals['__name__']
    def __bool__( self ):
        from OpenGL import error
        try:
            return bool( self.getFinalCall())
        except error.NullFunctionError as err:
            return False
    __nonzero__ = __bool__ # Python 2.6 compatibility
    def finalise( self ):
        """Call, doing a late lookup and bind to find an implementation"""
        for alternate in self._alternatives:
            if alternate:
#                _log.info(
#                    """Chose alternate: %s from %s""",
#                    alternate.__name__,
#                    ", ".join([x.__name__ for x in self._alternatives])
#                )
                return alternate
        from OpenGL import error
        raise error.NullFunctionError(
            """Attempt to call an undefined alternate function (%s), check for bool(%s) before calling"""%(
                ', '.join([x.__name__ for x in self._alternatives]),
                self.__name__,
            )
        )
def alternate( name, *functions ):
    """Construct a callable that functions as the first implementation found of given set of alternatives

    if name is a function then its name will be used....
    """
    if not isinstance( name, (bytes,unicode)):
        functions = (name,)+functions
        name = name.__name__
    return type( name, (_Alternate,), {} )( name, *functions )
