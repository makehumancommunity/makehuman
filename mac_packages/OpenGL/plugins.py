"""Simple plug-in mechanism to provide replacement for setuptools plugins"""

class Plugin( object ):
    """Base class for plugins to be loaded"""
    loaded = False
    def __init__( self, name, import_path, check = None, **named ):
        """Register the plug-in"""
        self.name = name 
        self.import_path = import_path
        self.check = check
        self.registry.append( self )
        self.__dict__.update( named )
    def load( self ):
        """Attempt to load and return our entry point"""
        try:
            return importByName( self.import_path )
        except ImportError:
            return None
    @classmethod
    def match( cls, *args ):
        """Match to return the plugin which is appropriate to load"""
    @classmethod
    def all( cls ):
        """Iterate over all registered plugins"""
        return cls.registry[:]
    @classmethod 
    def by_name( cls, name ):
        for instance in cls.all():
            if instance.name == name:
                return instance 
        return None
    
def importByName( fullName ):
    """Import a class by name"""
    name = fullName.split(".")
    moduleName = name[:-1]
    className = name[-1]
    module = __import__( ".".join(moduleName), {}, {}, moduleName)
    return getattr( module, className )

        
class PlatformPlugin( Plugin ):
    """Platform-level plugin registration"""
    registry = []
    @classmethod
    def match( cls, key ):
        """Determine what platform module to load
        
        key -- (sys.platform,os.name) key to load 
        """
        for possible in key:
            # prefer sys.platform, *then* os.name
            for plugin in cls.registry:
                if plugin.name == possible:
                    return plugin
        raise KeyError( """No platform plugin registered for %s"""%(key,))

class FormatHandler( Plugin ):
    """Data-type storage-format handler"""
    registry = []
    @classmethod
    def match( cls, value ):
        """Lookup appropriate handler based on value (a type)"""
        key = '%s.%s'%( value.__module__, value.__name__ )
        for plugin in cls.registry:
            set = getattr( plugin, 'check', ())
            if set and key in set:
                return plugin
        return None
