"""Base class for GLU callback-caching structures"""
import ctypes
import weakref
from OpenGL._bytes import long, integer_types

class GLUStruct( object ):
    """Mix-in class for GLU Structures that want to retain references to callbacks
    
    Also provides original-object-return for the "datapointer" style paremters
    
    Each sub-class must override:
        CALLBACK_TYPES -- maps a "which" constant to a function type 
        CALLBACK_FUNCTION_REGISTRARS -- maps a "which" constant to the 
            registration function for functions of that type
        WRAPPER_METHODS -- maps a "which" consant to a method of the structure 
            that produces a callable around the function which takes care of 
            input/output arguments, data conversions, error handling and the 
            like.
    Creates a dictionary member dataPointers if original-object-return is used
    Creates a dictionary member callbacks if callback registration is used
    """
    def getAsParam( self ):
        """Gets as a ctypes pointer to the underlying structure"""
        return ctypes.pointer( self )
    _as_parameter_ = property( getAsParam )
    CALLBACK_TYPES = None
    CALLBACK_FUNCTION_REGISTRARS = None
    WRAPPER_METHODS = None
    def noteObject( self, object ):
        """Note object for later retrieval as a Python object pointer
        
        This is the registration point for "original object return", returns 
        a void pointer to the Python object, though this is, effectively, an 
        opaque value.
        """
        identity = id(object)
        try:
            self.dataPointers[ identity ] = object
        except AttributeError as err:
            self.dataPointers = { identity: object }
        return identity
    def originalObject( self, voidPointer ):
        """Given a void-pointer, try to find our original Python object"""
        if isinstance( voidPointer, integer_types):
            identity = voidPointer
        elif voidPointer is None:
            return None
        else:
            try:
                identity = voidPointer.value 
            except AttributeError as err:
                identity = voidPointer[0]
        try:
            return self.dataPointers[ identity ]
        except (KeyError,AttributeError) as err:
            return voidPointer
    def addCallback( self, which, function ):
        """Register a callback for this structure object"""
        callbackType = self.CALLBACK_TYPES.get( which )
        if not callbackType:
            raise ValueError(
                """Don't have a registered callback type for %r"""%(
                    which,
                )
            )
        wrapperMethod = self.WRAPPER_METHODS.get( which )
        if wrapperMethod is not None:
            function = getattr(self,wrapperMethod)( function )
        cCallback = callbackType( function )
        # XXX this is ugly, query to ctypes list on how to fix it...
        try:
            self.CALLBACK_FUNCTION_REGISTRARS[which]( self, which, cCallback )
        except ctypes.ArgumentError as err:
            err.args += (which,cCallback)
            raise
        #gluTessCallbackBase( self, which, cCallback)
        # XXX catch errors!
        if getattr( self, 'callbacks', None ) is None:
            self.callbacks = {}
        self.callbacks[ which ] = cCallback
        return cCallback
    def ptrAsArray( self, ptr, length, type ):
        """Copy length values from ptr into new array of given type"""
        result = type.zeros( (length,) )
        for i in range(length):
            result[i] = ptr[i]
        return result
