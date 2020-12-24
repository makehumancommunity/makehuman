"""Storage of per-context values of various types

Because OpenGL needs persistent references to the
objects we're constructing to shadow Python objects,
we have to store references to the objects somewhere

For any given Python GUI library, we can use a weakref
to the library's representation of the GL context to 
call the cleanup function.  That means some per-GUI 
library code in OpenGL (or the library), but it gives 
us very natural operations within OpenGL.

Note: you can entirely disable use of this module by 
setting:

    OpenGL.ERROR_ON_COPY = True 
    OpenGL.STORE_POINTERS = False 
        
before importing OpenGL functionality.
"""
from OpenGL import platform
import weakref
storedPointers = {
    # map from contextID: { constant: value }
}
storedWeakPointers = {
    # map from contextID: WeakValueDictionary({ constant: value })
}
STORAGES = [ storedPointers, storedWeakPointers ]

def getContext( context = None ):
    """Get the context (if passed, just return)
    
    context -- the context ID, if None, the current context
    """
    if context is None:
        context = platform.GetCurrentContext()
        if context == 0:
            from OpenGL import error
            raise error.Error(
                """Attempt to retrieve context when no valid context"""
            )
    return context
def setValue( constant, value, context=None, weak=False ):
    """Set a stored value for the given context
    
    constant -- Normally a GL constant value, but can be any hashable value 
    value -- the value to be stored.  If weak is true must be 
        weak-reference-able.  If None, then the value will be deleted from 
        the storage 
    context -- the context identifier for which we're storing the value
    weak -- if true, value will be stored with a weakref
        Note: you should always pass the same value for "weak" for a given 
        constant, otherwise you will create two storages for the constant.
    """
    if getattr( value, '_no_cache_', False ):
        return 
    context = getContext( context )
    if weak:
        storage = storedWeakPointers
        cls = weakref.WeakValueDictionary
    else:
        storage = storedPointers
        cls = dict
    current = storage.get( context )
    if current is None:
        storage[context] = current = cls()
    previous = current.get( constant )
    if value is None:
        try:
            del current[ constant ]
        except (KeyError,TypeError,ValueError) as err:
            pass 
    else:
        # XXX potential for failure here if a non-weakref-able objects
        # is being stored with weak == True
        current[ constant ] = value 
    return previous
def delValue( constant, context=None ):
    """Delete the specified value for the given context
    
    constant -- Normally a GL constant value, but can be any hashable value 
    context -- the context identifier for which we're storing the value
    """
    context = getContext( context )
    found = False
    for storage in STORAGES:
        contextStorage = storage.get( context  )
        if contextStorage:
            try:
                del contextStorage[ constant ]
                found = True
            except KeyError as err:
                pass
    return found

def getValue( constant, context = None ):
    """Get a stored value for the given constant
    
    constant -- unique ID for the type of data being retrieved
    context -- the context ID, if None, the current context
    """
    context = getContext( context )
    for storage in STORAGES:
        contextStorage = storage.get( context  )
        if contextStorage:
            value =  contextStorage.get( constant )
            if value is not None:
                return value
    return None

def cleanupContext( context=None ):
    """Cleanup all held pointer objects for the given context
    
    Warning: this is dangerous, as if you call it before a context 
    is destroyed you may release memory held by the context and cause
    a protection fault when the GL goes to render the scene!
    
    Normally you will want to get the context ID explicitly and then 
    register cleanupContext as a weakref callback to your GUI library 
    Context object with the (now invalid) context ID as parameter.
    """
    if context is None:
        context = platform.GetCurrentContext()
    for storage in STORAGES:
        try:
            del storedPointers[ context ]
        except KeyError as err:
            return False
        else:
            return True
