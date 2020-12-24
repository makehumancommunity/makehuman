"""Fix missing-API problems in logging module (circa Python 2.3)

Adds constants to the log objects.
Adds getException(err) to log objects to retrieve 
formatted exception or err if traceback not available.
"""
import traceback, logging
from OpenGL._configflags import ERROR_LOGGING, FULL_LOGGING
getLog = logging.getLogger

def getException(error):
    """Get formatted traceback from exception"""
    try:
        return traceback.format_exc( limit=10 )
    except Exception as err:
        return str( error )

logging.Logger.getException = staticmethod( getException )
logging.Logger.err = logging.Logger.error
logging.Logger.DEBUG = logging.DEBUG 
logging.Logger.WARN = logging.WARN 
logging.Logger.INFO = logging.INFO 
logging.Logger.ERR = logging.Logger.ERROR = logging.ERROR

if FULL_LOGGING:
    getLog( 'OpenGL.calltrace' ).setLevel( logging.INFO )

class _LoggedFunction( object ):
    """Proxy that overrides __call__ to log arguments"""
    def __init__( self, base, log ):
        self.__dict__[''] = base 
        self.__dict__['log'] = log
    def __setattr__( self, key, value ):
        if key != '':
            setattr( self.__dict__[''], key, value )
        else:
            self.__dict__[''] = value 
    def __getattr__( self, key ):
        if key == '':
            return self.__dict__['']
        else:
            return getattr( self.__dict__[''], key )
class _FullLoggedFunction( _LoggedFunction ):
    """Fully-logged function wrapper (logs all call params to OpenGL.calltrace)"""
    _callTrace = getLog( 'OpenGL.calltrace' )
    def __call__( self, *args, **named ):
        argRepr = []
        function = getattr( self, '' )
        for arg in args:
            argRepr.append( repr(arg) )
        for key,value in named.items():
            argRepr.append( '%s = %s'%( key,repr(value)) )
        argRepr = ",".join( argRepr )
        self._callTrace.info( '%s( %s )', function.__name__, argRepr )
        try:
            return function( *args, **named )
        except Exception as err:
            self.log.warning(
                """Failure on %s: %s""", function.__name__, self.log.getException( err )
            )
            raise
class _ErrorLoggedFunction ( _LoggedFunction ):
    """On-error-logged function wrapper"""
    def __call__( self, *args, **named ):
        function = getattr( self, '' )
        try:
            return function( *args, **named )
        except Exception as err:
            self.log.warning(
                """Failure on %s: %s""", function.__name__, self.log.getException( err )
            )
            raise
    

def logOnFail( function, log ):
    """Produce possible log-wrapped version of function

    function -- callable object to be wrapped
    log -- the log to which to log information
    
    Uses ERROR_LOGGING and FULL_LOGGING
    to determine whether/how to wrap the function.
    """
    if ERROR_LOGGING or FULL_LOGGING:
        if FULL_LOGGING:
            loggedFunction = _FullLoggedFunction( function, log )
        else:
            loggedFunction = _ErrorLoggedFunction( function, log )
        return loggedFunction
    else:
        return function
