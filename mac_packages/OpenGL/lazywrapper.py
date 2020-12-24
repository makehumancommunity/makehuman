"""Simplistic wrapper decorator for Python-coded wrappers"""
from OpenGL.latebind import Curry
from OpenGL import MODULE_ANNOTATIONS

class _LazyWrapper( Curry ):
    """Marker to tell us that an object is a lazy wrapper"""

def lazy( baseFunction ):
    """Produce a lazy-binding decorator that uses baseFunction

    Allows simple implementation of wrappers where the
    whole of the wrapper can be summed up as do 1 thing
    then call base function with the cleaned up result.

    Passes baseFunction in as the first argument of the
    wrapped function, all other parameters are passed
    unchanged.  The wrapper class created has __nonzero__
    and similar common wrapper entry points defined.
    """
    def wrap( wrapper ):
        """Wrap wrapper with baseFunction"""
        def __bool__( self ):
            return bool( baseFunction )
        def __repr__( self ):
            return '%s( %r )'%(
                'OpenGL.lazywrapper.lazy',
                baseFunction.__name__,
            )
        _with_wrapper = type( wrapper.__name__, (_LazyWrapper,), {
            '__repr__': __repr__,
            '__doc__': wrapper.__doc__,
            '__nonzero__': __bool__,
            '__bool__': __bool__,
            'wrappedOperation': baseFunction,
            'restype': getattr(wrapper, 'restype',getattr(baseFunction,'restype',None)),
        } )
        with_wrapper = _with_wrapper(wrapper,baseFunction)
        with_wrapper.__name__ = wrapper.__name__
        if hasattr( baseFunction, '__module__' ):
            with_wrapper.__module__ = baseFunction.__module__
        return with_wrapper
    return wrap


if __name__ == "__main__":
    from OpenGL.raw import GLU
    func = GLU.gluNurbsCallbackData
    output = []
    def testwrap( base ):
        "Testing"
        output.append( base )
    testlazy = lazy( func )( testwrap )
    testlazy( )
    assert testlazy.__doc__ == "Testing"
    assert testlazy.__class__.__name__ == 'testwrap'
    assert testlazy.__name__ == 'testwrap'
    assert testlazy.baseFunction is func
    assert testlazy.wrapperFunction is testwrap
    assert output
