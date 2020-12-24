"""GLUT functions requiring special handling to provide Pythonic wrappers

Note:
    GLUT callbacks are controlled by a flag in the platform module.  The
    GLUT_GUARD_CALLBACKS flag controls whether to wrap passed functions
    with error-checking and context-validity checking code so that the
    callbacks will only trigger if there is a valid context.  This is done
    so that systems such as Win32 will not continue running GLUT callbacks
    after the system has exited.

    Note:
        This is not a problem with FreeGLUT on Linux, so Linux does not
        add the extra overhead of the wrapper function.
    Note:
        This hack does *not* prevent hanging if there is no GLUT callback
        being triggered.  I.e. if you create a GLUT program that doesn't
        explicitly call exit and doesn't call display or the like in a timer
        then your app will hang on exit on Win32.

XXX the platform-specific stuff should be getting done in the 
platform module *not* in the module here!
"""
from OpenGL.platform import CurrentContextIsValid, GLUT_GUARD_CALLBACKS, PLATFORM
GLUT = PLATFORM.GLUT
from OpenGL import contextdata, error, platform, logs
from OpenGL.raw import GLUT as _simple
from OpenGL._bytes import bytes, unicode,as_8_bit
import ctypes, os, sys, traceback
PLATFORM = platform.PLATFORM
FUNCTION_TYPE = _simple.CALLBACK_FUNCTION_TYPE
from OpenGL._bytes import long, integer_types

_log = logs.getLog( 'OpenGL.GLUT.special' )

if os.name == "nt":
    _log.info( """Using NT-specific GLUT calls with exit callbacks""" )
    _exitfunctype = FUNCTION_TYPE( None, ctypes.c_int )
    __glutInitWithExit = platform.createBaseFunction(
        '__glutInitWithExit', dll=platform.PLATFORM.GLUT, resultType=None,
        argTypes=[ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_char_p),_exitfunctype],
        doc='glutInit( POINTER(c_int)(pargc), POINTER(STRING)(argv) ) -> None',
        argNames=('pargc', 'argv'),
    )
    __glutCreateWindowWithExit = platform.createBaseFunction(
        '__glutCreateWindowWithExit', dll=platform.PLATFORM.GLUT, resultType=ctypes.c_int,
        argTypes=[ctypes.c_char_p,_exitfunctype],
        doc='glutCreateWindow( STRING(title) ) -> c_int',
        argNames=('title',),
    )
    __glutCreateMenuWithExit = platform.createBaseFunction( 
        '__glutCreateMenuWithExit', dll=platform.PLATFORM.GLUT, resultType=ctypes.c_int, 
        argTypes=[FUNCTION_TYPE(None, ctypes.c_int),_exitfunctype],
        doc='glutCreateMenu( FUNCTION_TYPE(None, c_int)(callback) ) -> c_int', 
        argNames=('callback',),
    )
else:
    # Linux, OSX, etceteras
    __glutInitWithExit = None
if __glutInitWithExit:
    # Normal platforms + Win32 w/ FreeGLUT (SF#2813722)
    import sys
    _exitfunc = _exitfunctype(sys.exit)
    
    def _base_glutInit(pargc, argv):
        """Overrides base glut init with exit-function-aware version"""
        return __glutInitWithExit(pargc, argv, _exitfunc)
    def glutCreateWindow(title):
        """Create window with given title
        
        This is the Win32-specific version that handles
        registration of an exit-function handler 
        """
        return __glutCreateWindowWithExit(title, _exitfunc)
    def glutCreateMenu(callback):
        """Create menu with given callback 
        
        This is the Win32-specific version that handles 
        registration of an exit-function callback.
        """
        return __glutCreateMenuWithExit(callback, _exitfunc)
else:
    _base_glutInit = platform.nullFunction( 
        'glutInit', GLUT,
        resultType=None, 
        argTypes=(ctypes.POINTER(ctypes.c_int),ctypes.POINTER( ctypes.c_char_p )),
        doc = 'Initialize the GLUT library', argNames = ('argcp','argv'),
        module = __name__,
        error_checker = None,
    )
##_base_glutDisplayFunc = GLUT.glutDisplayFunc
##_base_glutIdleFunc = GLUT.glutIdleFunc
##_base_glutEntryFunc = GLUT.glutEntryFunc
##_base_glutReshapeFunc = GLUT.glutReshapeFunc
_base_glutDestroyWindow = getattr(GLUT, 'glutDestroyWindow', None)

class GLUTCallback( object ):
    """Class implementing GLUT Callback registration functions"""
    def __init__( self, typeName, parameterTypes, parameterNames ):
        """Initialise the glut callback instance"""
        self.typeName = typeName
        def describe( typ, name ):
            return '(int) %s'%(name)
        self.__doc__ = """Specify handler for GLUT %r events
    def handler( %s ):
        return None"""%( typeName, ", ".join([
            describe( typ,name )
            for (typ,name) in zip( parameterTypes, parameterNames )
        ]))
        try:
            self.wrappedOperation = getattr( GLUT, 'glut%sFunc'%(typeName) )
        except AttributeError as err:
            def failFunction( *args, **named ):
                from OpenGL import error
                raise error.NullFunctionError(
                    """Undefined GLUT callback function %s, check for bool(%s) before calling"""%(
                        typeName, 'glut%sFunc'%(typeName),
                    )
                )
            self.wrappedOperation = failFunction
        self.callbackType = FUNCTION_TYPE( None, *parameterTypes )
        self.CONTEXT_DATA_KEY = 'glut%sFunc'%(typeName, )
    argNames = ('function',)
    def __call__( self, function, *args ):
        if GLUT_GUARD_CALLBACKS and hasattr( function,'__call__' ):
            def safeCall( *args, **named ):
                """Safe calling of GUI callbacks, exits on failures"""
                try:
                    if not CurrentContextIsValid():
                        raise RuntimeError( """No valid context!""" )
                    return function( *args, **named )
                except Exception as err:
                    traceback.print_exc()
                    sys.stderr.write( """GLUT %s callback %s with %s,%s failed: returning None %s\n"""%(
                        self.typeName, function, args, named, err, 
                    ))
                    os._exit(1)
                    #return None
            finalFunction = safeCall
        else:
            finalFunction = function
        if hasattr( finalFunction,'__call__' ):
            cCallback = self.callbackType( finalFunction )
        else:
            cCallback = function
        # keep the function alive as long as the cCallback is...
        #cCallback.function = function
        contextdata.setValue( self.CONTEXT_DATA_KEY, cCallback )
        self.wrappedOperation( cCallback, *args )
        return cCallback
class GLUTTimerCallback( GLUTCallback ):
    """GLUT timer callbacks (completely nonstandard wrt other GLUT callbacks)"""
    def __call__( self, milliseconds, function, value ):
        cCallback = self.callbackType( function )
        # timers should de-register as soon as they are called...
        # Note: there's no good key to use! we want to allow for
        # multiple instances of the same function with the same value 
        # which means we have nothing that can store it properly...
        callbacks = contextdata.getValue( self.CONTEXT_DATA_KEY )
        if callbacks is None:
            callbacks = []
            contextdata.setValue( self.CONTEXT_DATA_KEY, callbacks )
        def deregister( value ):
            try:
                function( value )
            finally:
                for item in callbacks:
                    if item.function is deregister:
                        callbacks.remove( item )
                        item.function = None
                        break
                if not callbacks:
                    contextdata.delValue( self.CONTEXT_DATA_KEY )
        cCallback = self.callbackType( deregister )
        cCallback.function = deregister
        callbacks.append( cCallback )
        self.wrappedOperation( milliseconds, cCallback, value )
        return cCallback

class GLUTMenuCallback( object ):
    """Place to collect the GLUT Menu manipulation special code"""
    callbackType = FUNCTION_TYPE( ctypes.c_int, ctypes.c_int )
    def glutCreateMenu( cls, func ):
        """Create a new (current) menu, return small integer identifier
        
        func( int ) -- Function taking a single integer reflecting
            the user's choice, the value passed to glutAddMenuEntry
        
        return menuID (small integer)
        """
        cCallback = cls.callbackType( func )
        menu = _simple.glutCreateMenu( cCallback )
        contextdata.setValue( ('menucallback',menu), (cCallback,func) )
        return menu
    glutCreateMenu.argNames = [ 'func' ]
    glutCreateMenu = classmethod( glutCreateMenu )
    def glutDestroyMenu( cls, menu ):
        """Destroy (cleanup) the given menu
        
        Deregister's the interal pointer to the menu callback 
        
        returns None
        """
        result = _simple.glutDestroyMenu( menu )
        contextdata.delValue( ('menucallback',menu) )
        return result
    glutDestroyMenu.argNames = [ 'menu' ]
    glutDestroyMenu = classmethod( glutDestroyMenu )

glutCreateMenu = GLUTMenuCallback.glutCreateMenu
#glutCreateMenu.wrappedOperation = _simple.glutCreateMenu
glutDestroyMenu = GLUTMenuCallback.glutDestroyMenu
#glutDestroyMenu.wrappedOperation = _simple.glutDestroyMenu

glutButtonBoxFunc = GLUTCallback(
    'ButtonBox', (ctypes.c_int,ctypes.c_int), ('button','state'),
)
glutDialsFunc = GLUTCallback(
    'Dials', (ctypes.c_int,ctypes.c_int), ('dial','value'),
)
glutDisplayFunc = GLUTCallback(
    'Display', (), (),
)
glutEntryFunc = GLUTCallback(
    'Entry', (ctypes.c_int,), ('state',),
)
glutIdleFunc = GLUTCallback(
    'Idle', (), (),
)
glutJoystickFunc = GLUTCallback(
    'Joystick', (ctypes.c_uint,ctypes.c_int,ctypes.c_int,ctypes.c_int), ('buttonMask','x','y','z'),
)
glutKeyboardFunc = GLUTCallback(
    'Keyboard', (ctypes.c_char,ctypes.c_int,ctypes.c_int), ('key','x','y'),
)
glutKeyboardUpFunc = GLUTCallback(
    'KeyboardUp', (ctypes.c_char,ctypes.c_int,ctypes.c_int), ('key','x','y'),
)
glutMenuStatusFunc = GLUTCallback(
    'MenuStatus', (ctypes.c_int,ctypes.c_int,ctypes.c_int), ('status','x','y'),
)
glutMenuStateFunc = GLUTCallback(
    'MenuState', (ctypes.c_int,), ('status',),
)
glutMotionFunc = GLUTCallback(
    'Motion', (ctypes.c_int,ctypes.c_int), ('x','y'),
)
glutMouseFunc = GLUTCallback(
    'Mouse', (ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int), ('button','state','x','y'),
)
glutOverlayDisplayFunc = GLUTCallback(
    'OverlayDisplay', (), (),
)
glutPassiveMotionFunc = GLUTCallback(
    'PassiveMotion', (ctypes.c_int,ctypes.c_int), ('x','y'),
)
glutReshapeFunc = GLUTCallback(
    'Reshape', (ctypes.c_int,ctypes.c_int), ('width','height'),
)
glutSpaceballButtonFunc = GLUTCallback(
    'SpaceballButton', (ctypes.c_int,ctypes.c_int), ('button','state'),
)
glutSpaceballMotionFunc = GLUTCallback(
    'SpaceballMotion', (ctypes.c_int,ctypes.c_int,ctypes.c_int), ('x','y','z'),
)
glutSpaceballRotateFunc = GLUTCallback(
    'SpaceballRotate', (ctypes.c_int,ctypes.c_int,ctypes.c_int), ('x','y','z'),
)
glutSpecialFunc = GLUTCallback(
    'Special', (ctypes.c_int,ctypes.c_int,ctypes.c_int), ('key','x','y'),
)
glutSpecialUpFunc = GLUTCallback(
    'SpecialUp', (ctypes.c_int,ctypes.c_int,ctypes.c_int), ('key','x','y'),
)
glutTabletButtonFunc = GLUTCallback(
    'TabletButton', (ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int), ('button','state','x','y',),
)
glutTabletButtonFunc = GLUTCallback(
    'TabletButton', (ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int), ('button','state','x','y',),
)
glutTabletMotionFunc = GLUTCallback(
    'TabletMotion', (ctypes.c_int,ctypes.c_int), ('x','y',),
)
glutVisibilityFunc = GLUTCallback(
    'Visibility', (ctypes.c_int,), ('state',),
)
glutWindowStatusFunc = GLUTCallback(
    'WindowStatus', (ctypes.c_int,), ('state',),
)

# glutTimerFunc is unlike any other GLUT callback-registration...
glutTimerFunc = GLUTTimerCallback(
    'Timer', (ctypes.c_int,), ('value',),
)

INITIALIZED = False
def glutInit( *args ):
    """Initialise the GLUT library"""
    global INITIALIZED
    if INITIALIZED:
        return args
    INITIALIZED = True
    if args:
        arg,args = args[0],args[1:]
        count = None
        if isinstance(arg, integer_types):
            # raw API style, (count, values)
            count = arg
            if count != len(args):
                raise ValueError( """Specified count of %s does not match length (%s) of argument list %s"""%(
                    count, len(args), args,
                ))
        elif isinstance( arg, (bytes,unicode)):
            # passing in a sequence of strings as individual arguments
            args = (arg,)+args 
            count = len(args)
        else:
            args = arg 
            count = len(args)
    else:
        count=0
        args = []
    args = [as_8_bit(x) for x in args]
    if not count:
        count, args = 1, [as_8_bit('foo')]
    holder = (ctypes.c_char_p * len(args))()
    for i,arg in enumerate(args):
        holder[i] = arg
    count = ctypes.c_int( count )
    import os 
    currentDirectory = os.getcwd()
    try:
        # XXX need to check for error condition here...
        _base_glutInit( ctypes.byref(count), holder )
    finally:
        os.chdir( currentDirectory )
    return [
        holder[i] for i in range( count.value )
    ]
glutInit.wrappedOperation = _simple.glutInit

def glutDestroyWindow( window ):
    """Want to destroy the window, we need to do some cleanup..."""
    context = 0
    try:
        GLUT.glutSetWindow(window)
        context = contextdata.getContext()
        result = contextdata.cleanupContext( context )
        _log.info( """Cleaning up context data for window %s: %s""", window, result )
    except Exception as err:
        _log.error( """Error attempting to clean up context data for GLUT window %s: %s""", window, result )
    return _base_glutDestroyWindow( window )
glutDestroyWindow.wrappedOperation = _simple.glutDestroyWindow
