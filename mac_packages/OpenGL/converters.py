"""Implementations for common converter types"""
import ctypes,logging
from OpenGL._bytes import bytes, unicode, as_8_bit
from OpenGL._null import NULL
_log = logging.getLogger( 'OpenGL.converters' )

class Converter( object ):
    """Base class for Converter types

    Converter objects are callable objects used with the
    OpenGL.wrapper.Wrapper class to simplify the wrapping
    of functions by collecting commonly used functionality
    into a reusable function.

    Each Converter has two (class) attributes:

        argNames -- list of argument names for initialisation
        indexLookups -- set of (indexname, argName,methodName) values
            to lookup on wrapper.  These allow us to use argument-name
            references to refer to which arguments to use when
            processing (prevents the need to revise pointers when
            we change the API for a function).

    Converters can be any of the Wrapper API helper functions,
    so the callable interface can vary among Converter classes.
    """
    argNames = ( )
    indexLookups = ( )
    def __init__( self, *args, **named ):
        """Store arguments in attributes

        *args -- mapped to self.argNames in order to set attributes
        **named -- mapped to self.argNames by name to set attributes
        """
        argNames = list(self.argNames)
        for a in self.argNames:
            if a in named:
                setattr( self, a, named[a] )
                argNames.remove( a )
        for a,value in zip( argNames, args ):
            setattr( self, a, value )
    def finalise( self, wrapper ):
        """Look up our indices (where appropriate)"""
        for indexname,argName,methodName in self.indexLookups:
            setattr(
                self, indexname,
                getattr(wrapper,methodName)(getattr( self, argName ))
            )

# Definitions of the abstract interfaces...
class PyConverter( Converter ):
    """Converter sub-class for use in Wrapper.pyConverters

    This class just defines the interface for a pyConverter-style
    Converter object
    """
    def __call__( self, incoming, function, arguments ):
        """Convert incoming argument into compatable data-types

        incoming -- the Python argument for this parameter
        function -- the wrapper.Wrapper class we are supporting
        arguments -- the complete set of arguments passed to the
            function


        """
        raise NotImplemented( """%s class doesn't implement __call__"""%(
            self.__class__.__name__,
        ))

class CConverter( Converter ):
    """Converter sub-class for use in Wrapper.cConverters

    This class just defines the interface for a cConverter-style
    Converter object
    """
    def __call__( self, pyArgs, index, baseOperation ):
        """Calculate C-compatible Python object from Python arguments

        pyArgs -- set of Python argument objects converted by
            pyConverters from the incoming arguments
        index -- our index in baseOperation.cConverters
        baseOperation -- the Wrapper object which we are supporting
        """
        raise NotImplemented( """%s class doesn't implement __call__"""%(
            self.__class__.__name__,
        ))
class ReturnValues( Converter ):
    """Converter sub-class for use as Wrapper.returnValues

    This class just defines the interface for a returnValues-style
    Converter object
    """
    def __call__( self, result, baseOperation, pyArgs, cArgs ):
        """Return a final value to the caller

        result -- the raw ctypes result value
        baseOperation -- the Wrapper object which we are supporting
        pyArgs -- the set of Python arguments produced by pyConverters
        cArgs -- the set of C-compatible arguments produced by CConverter

        return the Python object for the final result
        """
        raise NotImplemented( """%s class doesn't implement __call__"""%(
            self.__class__.__name__,
        ))

# Now the concrete classes...
from OpenGL import acceleratesupport
CallFuncPyConverter = None
if acceleratesupport.ACCELERATE_AVAILABLE:
    try:
        from OpenGL_accelerate.wrapper import (
            CallFuncPyConverter, DefaultCConverter, getPyArgsName,
        )
        from OpenGL_accelerate.arraydatatype import (
            Output,SizedOutput,OutputOrInput,SizedOutputOrInput
        )
        from OpenGL_accelerate.wrapper import (
            returnCArgument, returnPyArgument,
        )
    except ImportError as err:
        _log.warning(
            "Unable to load converters accelerators (wrapper, arraydatatype) from OpenGL_accelerate"
        )
        CallFuncPyConverter = None
if CallFuncPyConverter is None:
    class CallFuncPyConverter( PyConverter ):
        """PyConverter that takes a callable and calls it on incoming"""
        def __init__( self, function ):
            """Store the function"""
            self.function = function
        def __call__( self, incoming, function, argument ):
            """Call our function on incoming"""
            return self.function( incoming )
    class DefaultCConverter( CConverter ):
        """NULL or Default CConverter, returns same-named Python argument

        Used primarily to allow for specifying a converter that explicitly
        says "use the default behaviour".  This is *not* a finalise-ing
        converter, it is passed in the index explicitly and just retrieves
        that index from pyArgs when called.

        Raises informative errors if the index cannot be resolved in pyArgs
        """
        def __init__( self, index ):
            """Just store index for future access"""
            self.index = index
        def __call__( self, pyArgs, index, wrapper ):
            """Return pyArgs[self.index] or raise a ValueError"""
            try:
                return pyArgs[ self.index ]
            except IndexError:
                raise ValueError(
                    """Expected parameter index %r, but pyArgs only length %s"""%(
                    self.index,
                    len(pyArgs )
                ))
    class getPyArgsName( CConverter ):
        """CConverter returning named Python argument

        Intended for use in cConverters, the function returned
        retrieves the named pyArg and returns it when called.
        """
        argNames = ('name',)
        indexLookups = [ ('index','name', 'pyArgIndex' ), ]
        __slots__ = ( 'index', 'name')
        def __call__( self, pyArgs, index, baseOperation ):
            """Return pyArgs[ self.index ]"""
            try:
                return pyArgs[ self.index ]
            except AttributeError:
                raise RuntimeError( """"Did not resolve parameter index for %r"""%(self.name))

    class Output( CConverter ):
        """CConverter generating static-size typed output arrays

        Produces an output array of given type (arrayType) and
        size using self.lookup() to determine the size of the
        array to be produced, where the lookup function is passed
        as an initialisation argument.

        Provides also:

            oldStyleReturn( ... ) for use in the default case of
                PyOpenGL compatability mode, where result arrays of
                size (1,) are returned as scalar values.
        """
        argNames = ('name','size','arrayType' )
        indexLookups = [
            ('outIndex','name', 'cArgIndex' ),
        ]
        __slots__ = ('index','size','arrayType','outIndex','inIndex')
        def __call__( self, pyArgs, index, baseOperation ):
            """Return pyArgs[ self.index ]"""
            return self.arrayType.zeros( self.getSize(pyArgs) )
        def getSize( self, pyArgs ):
            """Retrieve the array size for this argument"""
            return self.size
        def oldStyleReturn( self, result, baseOperation, pyArgs, cArgs ):
            """Retrieve cArgs[ self.index ]"""
            result = cArgs[ self.outIndex ]
            try:
                thisSize = self.getSize(pyArgs)
            except KeyError:
                return result 
            if thisSize == (1,):
                try:
                    return result[0]
                except (IndexError,TypeError):
                    return result
            else:
                return result
    class OutputOrInput( Output ):
        DO_OUTPUT = (None,NULL)
        def __call__( self, pyArgs, index, baseOperation ):
            for do_output in self.DO_OUTPUT:
                if pyArgs[index] is do_output:
                    return super( OutputOrInput,self ).__call__( pyArgs, index, baseOperation )
            return self.arrayType.asArray( pyArgs[index] )

    class SizedOutput( Output ):
        """Output generating dynamically-sized typed output arrays

        Takes an extra parameter "specifier", which is the name of
        a Python argument to be passed to the lookup function in order
        to determine the appropriate size for the output array.
        """
        argNames = ('name','specifier','lookup','arrayType' )
        indexLookups = [
            ('outIndex','name', 'cArgIndex' ),
            ('index','specifier', 'pyArgIndex' ),
        ]
        __slots__ = ('index','outIndex','specifier','lookup','arrayType')
        def getSize( self, pyArgs ):
            """Retrieve the array size for this argument"""
            try:
                specifier = pyArgs[ self.index ]
            except AttributeError:
                raise RuntimeError( """"Did not resolve parameter index for %r"""%(self.name))
            else:
                try:
                    return self.lookup( specifier )
                except KeyError:
                    raise KeyError( """Unknown specifier %s"""%( specifier ))
    class SizedOutputOrInput( SizedOutput ):
        DO_OUTPUT = (None,NULL)
        def __call__( self, pyArgs, index, baseOperation ):
            for do_output in self.DO_OUTPUT:
                if pyArgs[index] is do_output:
                    return super( SizedOutputOrInput,self ).__call__( pyArgs, index, baseOperation )
            return self.arrayType.asArray( pyArgs[index] )
    class returnCArgument( ReturnValues ):
        """ReturnValues returning the named cArgs value"""
        argNames = ('name',)
        indexLookups = [ ('index','name', 'cArgIndex' ), ]
        __slots__ = ( 'index', 'name' )
        def __call__( self, result, baseOperation, pyArgs, cArgs ):
            """Retrieve cArgs[ self.index ]"""
            return cArgs[self.index]

    class returnPyArgument( ReturnValues ):
        """ReturnValues returning the named pyArgs value"""
        argNames = ('name',)
        indexLookups = [ ('index','name', 'pyArgIndex' ), ]
        __slots__ = ( 'index', 'name' )
        def __call__( self, result, baseOperation, pyArgs, cArgs ):
            """Retrieve pyArgs[ self.index ]"""
            return pyArgs[self.index]

class StringLengths( CConverter ):
    """CConverter for processing array-of-pointers-to-strings data-type

    Converter is a CConverter for the array-of-lengths for a
    array-of-pointers-to-strings data-type used to pass a set
    of code fragments to the GLSL compiler.

    Provides also:

        stringArray -- PyConverter callable ensuring list-of-strings
            format for the python argument

        stringArrayForC -- CResolver converting the array to
            POINTER(c_char_p) format for passing to C

        totalCount -- CConverter callable giving count of string
            pointers (that is, length of the pointer array)
    """
    argNames = ('name',)
    indexLookups = [ ('index','name', 'pyArgIndex' ), ]
    __slots__ = ()
    def __call__( self, pyArgs, index, baseOperation ):
        """Get array of length integers for string contents"""
        from OpenGL.raw.GL import _types
        tmp = [len(x) for x in pyArgs[self.index]]
        a_type = _types.GLint * len(tmp)
        return a_type( *tmp )
    def totalCount( self, pyArgs, index, baseOperation ):
        """Get array of length integers for string contents"""
        return len(pyArgs[self.index])
    def stringArray( self, arg, baseOperation, args ):
        """Create basic array-of-strings object from pyArg"""
        if isinstance( arg, (bytes,unicode) ):
            arg = [arg]
        value = [as_8_bit(x) for x in arg]
        return value
    def stringArrayForC( self, strings ):
        """Create a ctypes pointer to char-pointer set"""
        from OpenGL import arrays
        result = (ctypes.c_char_p * len(strings))()
        for i,s in enumerate(strings):
            result[i] = ctypes.cast(
                arrays.GLcharARBArray.dataPointer(s),
                ctypes.c_char_p,
            )
        return result
