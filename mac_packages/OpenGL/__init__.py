"""ctypes-based OpenGL wrapper for Python

This is the PyOpenGL 3.x tree, it attempts to provide
a largely compatible API for code written with the
PyOpenGL 2.x series using the ctypes foreign function
interface system.

Configuration Variables:

There are a few configuration variables in this top-level
module.  Applications should be the only code that tweaks
these variables, mid-level libraries should not take it
upon themselves to disable/enable features at this level.
The implication there is that your library code should be
able to work with any of the valid configurations available
with these sets of flags.

Further, once any entry point has been loaded, the variables 
can no longer be updated.  The OpenGL._confligflags module 
imports the variables from this location, and once that 
import occurs the flags should no longer be changed.

    ERROR_CHECKING -- if set to a False value before
        importing any OpenGL.* libraries will completely
        disable error-checking.  This can dramatically
        improve performance, but makes debugging far
        harder.

        This is intended to be turned off *only* in a
        production environment where you *know* that
        your code is entirely free of situations where you
        use exception-handling to handle error conditions,
        i.e. where you are explicitly checking for errors
        everywhere they can occur in your code.

        Default: True

    ERROR_LOGGING -- If True, then wrap array-handler
        functions with  error-logging operations so that all exceptions
        will be reported to log objects in OpenGL.logs, note that
        this means you will get lots of error logging whenever you
        have code that tests by trying something and catching an
        error, this is intended to be turned on only during
        development so that you can see why something is failing.

        Errors are normally logged to the OpenGL.errors logger.

        Only triggers if ERROR_CHECKING is True

        Default: False

    ERROR_ON_COPY -- if set to a True value before
        importing the numpy/lists support modules, will
        cause array operations to raise
        OpenGL.error.CopyError if the operation
        would cause a data-copy in order to make the
        passed data-type match the target data-type.

        This effectively disables all list/tuple array
        support, as they are inherently copy-based.

        This feature allows for optimisation of your
        application.  It should only be enabled during
        testing stages to prevent raising errors on
        recoverable conditions at run-time.

        Default: False

    CONTEXT_CHECKING -- if set to True, PyOpenGL will wrap
        *every* GL and GLU call with a check to see if there
        is a valid context.  If there is no valid context
        then will throw OpenGL.errors.NoContext.  This is an
        *extremely* slow check and is not enabled by default,
        intended to be enabled in order to track down (wrong)
        code that uses GL/GLU entry points before the context
        has been initialized (something later Linux GLs are
        very picky about).

        Default: False

    STORE_POINTERS -- if set to True, PyOpenGL array operations
        will attempt to store references to pointers which are
        being passed in order to prevent memory-access failures
        if the pointed-to-object goes out of scope.  This
        behaviour is primarily intended to allow temporary arrays
        to be created without causing memory errors, thus it is
        trading off performance for safety.

        To use this flag effectively, you will want to first set
        ERROR_ON_COPY to True and eliminate all cases where you
        are copying arrays.  Copied arrays *will* segfault your
        application deep within the GL if you disable this feature!

        Once you have eliminated all copying of arrays in your
        application, you will further need to be sure that all
        arrays which are passed to the GL are stored for at least
        the time period for which they are active in the GL.  That
        is, you must be sure that your array objects live at least
        until they are no longer bound in the GL.  This is something
        you need to confirm by thinking about your application's
        structure.

        When you are sure your arrays won't cause seg-faults, you
        can set STORE_POINTERS=False in your application and enjoy
        a (slight) speed up.

        Note: this flag is *only* observed when ERROR_ON_COPY == True,
            as a safety measure to prevent pointless segfaults

        Default: True

    WARN_ON_FORMAT_UNAVAILABLE -- If True, generates
        logging-module warn-level events when a FormatHandler
        plugin is not loadable (with traceback).

        Default: False

    FULL_LOGGING -- If True, then wrap functions with
        logging operations which reports each call along with its
        arguments to  the OpenGL.calltrace logger at the INFO
        level.  This is *extremely* slow.  You should *not* enable
        this in production code!

        You will need to have a  logging configuration (e.g.
            logging.basicConfig()
        ) call  in your top-level script to see the results of the
        logging.

        Default: False

    ALLOW_NUMPY_SCALARS -- if True, we will wrap
        all GLint/GLfloat calls conversions with wrappers
        that allow for passing numpy scalar values.

        Note that this is experimental, *not* reliable,
        and very slow!

        Note that byte/char types are not wrapped.

        Default: False

    UNSIGNED_BYTE_IMAGES_AS_STRING -- if True, we will return
        GL_UNSIGNED_BYTE image-data as strings, instead of arrays
        for glReadPixels and glGetTexImage

        Default: True

    FORWARD_COMPATIBLE_ONLY -- only include OpenGL 3.1 compatible
        entry points.  Note that this will generally break most
        PyOpenGL code that hasn't been explicitly made "legacy free"
        via a significant rewrite.

        Default: False

    SIZE_1_ARRAY_UNPACK -- if True, unpack size-1 arrays to be
        scalar values, as done in PyOpenGL 1.5 -> 3.0.0, that is,
        if a glGenList( 1 ) is done, return a uint rather than
        an array of uints.

        Default: True

    USE_ACCELERATE -- if True, attempt to use the OpenGL_accelerate
        package to provide Cython-coded accelerators for core wrapping
        operations.

        Default: True
    
    MODULE_ANNOTATIONS -- if True, attempt to annotate alternates() and 
        constants to track in which module they are defined (only useful 
        for the documentation-generation passes, really).
        
        Default: False
    
    TYPE_ANNOTATIONS -- if True, set up type annotations in __annotations__
        on raw functions. This is mostly just so that people can play
        with the use of e.g. mypy or the like, but the values put in the
        annotations dictionary are generally either ctypes types or 
        ArrayDataType references, so this isn't *likely* to be all that useful
        without further work.
"""
from OpenGL.version import __version__
import os
def environ_key( name, default ):
    composed = 'PYOPENGL_%s'%name.upper()
    if composed in os.environ:
        value = os.environ[composed]
        if value.lower() in ('1','true'):
            return True 
        else:
            return False
    return os.environ.get( composed, default )

ERROR_CHECKING = environ_key( 'ERROR_CHECKING', True)
ERROR_LOGGING = environ_key( 'ERROR_LOGGING', False )
ERROR_ON_COPY = environ_key( 'ERROR_ON_COPY', False )
ARRAY_SIZE_CHECKING = environ_key( 'ARRAY_SIZE_CHECKING', True )
STORE_POINTERS = environ_key( 'STORE_POINTERS', True )
WARN_ON_FORMAT_UNAVAILABLE = False
FORWARD_COMPATIBLE_ONLY = False
SIZE_1_ARRAY_UNPACK = True
USE_ACCELERATE = environ_key( 'USE_ACCELERATE', True )
CONTEXT_CHECKING = environ_key( 'CONTEXT_CHECKING', False )

FULL_LOGGING = environ_key( 'FULL_LOGGING', False )
ALLOW_NUMPY_SCALARS = environ_key( 'ALLOW_NUMPY_SCALARS', False )
UNSIGNED_BYTE_IMAGES_AS_STRING = environ_key( 'UNSIGNED_BYTE_IMAGES_AS_STRING', True )
MODULE_ANNOTATIONS = False
TYPE_ANNOTATIONS = False


# Declarations of plugins provided by PyOpenGL itself
from OpenGL.plugins import PlatformPlugin, FormatHandler
PlatformPlugin( 'nt', 'OpenGL.platform.win32.Win32Platform' )
PlatformPlugin( 'linux2', 'OpenGL.platform.glx.GLXPlatform' )
PlatformPlugin( 'darwin', 'OpenGL.platform.darwin.DarwinPlatform' )
PlatformPlugin( 'posix', 'OpenGL.platform.glx.GLXPlatform' )
PlatformPlugin( 'osmesa', 'OpenGL.platform.osmesa.OSMesaPlatform')
PlatformPlugin( 'egl', 'OpenGL.platform.egl.EGLPlatform')

import sys
if sys.version_info[0] < 3:
    # Python 3.x renames the built-in module
    _bi = '__builtin__'
else:
    _bi = 'builtins'

FormatHandler( 'none', 'OpenGL.arrays.nones.NoneHandler', [ _bi+'.NoneType'],isOutput=False )

if sys.version_info[0] < 3:
    FormatHandler( 'str', 'OpenGL.arrays.strings.StringHandler',[_bi+'.str'], isOutput=False )
    FormatHandler( 'unicode', 'OpenGL.arrays.strings.UnicodeHandler',[_bi+'.unicode'], isOutput=False )
else:
    FormatHandler( 'bytes', 'OpenGL.arrays.strings.StringHandler',[_bi+'.bytes'], isOutput=False )
    FormatHandler( 'str', 'OpenGL.arrays.strings.UnicodeHandler',[_bi+'.str'], isOutput=False )
    
FormatHandler( 'list', 'OpenGL.arrays.lists.ListHandler', [
    _bi+'.list',
    _bi+'.tuple',
], isOutput=False )
FormatHandler( 'numbers', 'OpenGL.arrays.numbers.NumberHandler', [
    _bi+'.int',
    _bi+'.float',
    _bi+'.long',
], isOutput=False )
FormatHandler(
    'ctypesarrays', 'OpenGL.arrays.ctypesarrays.CtypesArrayHandler',
    [
        '_ctypes.ArrayType',
        '_ctypes.PyCArrayType',
        '_ctypes.Array',
        '_ctypes.array.Array',
    ],
    isOutput=True,
)
FormatHandler(
    'ctypesparameter',
    'OpenGL.arrays.ctypesparameters.CtypesParameterHandler',
    [
        _bi+'.CArgObject',
        'ctypes.c_uint',
        'ctypes.c_int',
        'ctypes.c_float',
        'ctypes.c_double',
        'ctypes.c_ulong',
        'ctypes.c_long',
        'ctypes.c_longlong',
    ],
    isOutput=True,
)
FormatHandler( 'ctypespointer', 'OpenGL.arrays.ctypespointers.CtypesPointerHandler',[
    'ctypes.c_void_p',
    '_ctypes._Pointer',
    'ctypes.c_char_p',
    '_ctypes.pointer._Pointer',
],isOutput=False )
FormatHandler( 'numpy', 'OpenGL.arrays.numpymodule.NumpyHandler', [
    'numpy.ndarray',
    'numpy.core.memmap.memmap',
    'numpy.uint8',
    'numpy.uint16',
    'numpy.uint32',
    'numpy.uint64',
    'numpy.int8',
    'numpy.int16',
    'numpy.int32',
    'numpy.int64',
    'numpy.float32',
    'numpy.float64',
    'numpy.float128',
],isOutput=True )
FormatHandler( 'buffer', 'OpenGL.arrays.buffers.BufferHandler', [
    'OpenGL.arrays._buffers.Py_buffer',
    _bi+'.memoryview',
    _bi+'.bytearray',
],isOutput=True )
FormatHandler( 'vbo', 'OpenGL.arrays.vbo.VBOHandler', ['OpenGL.arrays.vbo.VBO','OpenGL_accelerate.vbo.VBO'],isOutput=False )
FormatHandler( 'vbooffset', 'OpenGL.arrays.vbo.VBOOffsetHandler', ['OpenGL.arrays.vbo.VBOOffset','OpenGL_accelerate.vbo.VBOOffset'],isOutput=False )
