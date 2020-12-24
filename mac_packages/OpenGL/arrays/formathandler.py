"""Base class for the various Python data-format storage type APIs

Data-type handlers are specified using OpenGL.plugins module
"""
import ctypes
from OpenGL import plugins

class FormatHandler( object ):
    """Abstract class describing the handler interface
    
    Each data-type handler is responsible for providing a number of methods
    which allow it to manipulate (and create) instances of the data-type 
    it represents.
    """
    LAZY_TYPE_REGISTRY = {}  # more registrations
    HANDLER_REGISTRY = {}
    baseType = None
    typeConstant = None
    HANDLED_TYPES = ()
    preferredOutput = None
    isOutput = False
    GENERIC_OUTPUT_PREFERENCES = ['numpy','ctypesarrays']
    ALL_OUTPUT_HANDLERS = []
    def loadAll( cls ):
        """Load all OpenGL.plugins-registered FormatHandler classes
        """
        for entrypoint in plugins.FormatHandler.all():
            cls.loadPlugin( entrypoint )
    @classmethod
    def loadPlugin( cls, entrypoint ):
        """Load a single entry-point via plugins module"""
        if not entrypoint.loaded:
            from OpenGL.arrays.arraydatatype import ArrayDatatype
            try:
                plugin_class = entrypoint.load()
            except ImportError as err:
                from OpenGL import logs
                from OpenGL._configflags import WARN_ON_FORMAT_UNAVAILABLE
                _log = logs.getLog( 'OpenGL.formathandler' )
                if WARN_ON_FORMAT_UNAVAILABLE:
                    logFunc = _log.warn
                else:
                    logFunc = _log.info 
                logFunc(
                    'Unable to load registered array format handler %s:\n%s', 
                    entrypoint.name, _log.getException( err )
                )
            else:
                handler = plugin_class()
                #handler.register( handler.HANDLED_TYPES )
                ArrayDatatype.getRegistry()[ entrypoint.name ] = handler
                return handler
            entrypoint.loaded = True
    @classmethod
    def typeLookup( cls, type ):
        """Lookup handler by data-type"""
        registry = ArrayDatatype.getRegistry()
        try:
            return registry[ type ]
        except KeyError as err:
            key = '%s.%s'%(type.__module__,type.__name__)
            plugin = cls.LAZY_TYPE_REGISTRY.get( key )
            if plugin:
                cls.loadPlugin( plugin )
                return registry[ type ]
            raise KeyError( """Unable to find data-format handler for %s"""%( type,))
    loadAll = classmethod( loadAll )

    def register( self, types=None ):
        """Register this class as handler for given set of types"""
        from OpenGL.arrays.arraydatatype import ArrayDatatype
        ArrayDatatype.getRegistry().register( self, types )
    def registerReturn( self ):
        """Register this handler as the default return-type handler"""
        from OpenGL.arrays.arraydatatype import ArrayDatatype
        ArrayDatatype.getRegistry().registerReturn( self )

    def from_param( self, value, typeCode=None  ):
        """Convert to a ctypes pointer value"""
    def dataPointer( self, value ):
        """return long for pointer value"""
    def asArray( self, value, typeCode=None ):
        """Given a value, convert to array representation"""
    def arrayToGLType( self, value ):
        """Given a value, guess OpenGL type of the corresponding pointer"""
    def arraySize( self, value, typeCode = None ):
        """Given a data-value, calculate dimensions for the array"""
    def unitSize( self, value, typeCode=None ):
        """Determine unit size of an array (if possible)"""
        if self.baseType is not None:
            return 
    def dimensions( self, value, typeCode=None ):
        """Determine dimensions of the passed array value (if possible)"""
