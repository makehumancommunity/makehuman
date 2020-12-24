"""Late-bound base-class (with acceleration)"""
from OpenGL import acceleratesupport
LateBind = Curry = None
if acceleratesupport.ACCELERATE_AVAILABLE:
    try:
        from OpenGL_accelerate.latebind import LateBind, Curry
    except ImportError as err:
        pass
if LateBind is None:
    class LateBind(object):
        """Provides a __call__ which dispatches to self._finalCall

        When called without self._finalCall() makes a call to
        self.finalise() and then calls self._finalCall()
        """
        _finalCall = None
        def setFinalCall( self, finalCall ):
            """Set our finalCall to the callable object given"""
            self._finalCall = finalCall
        def getFinalCall( self ):
            """Retrieve and/or bind and retrieve final call"""
            if not self._finalCall:
                self._finalCall = self.finalise()
            return self._finalCall


        def finalise( self ):
            """Finalise our target to our final callable object

            return final callable
            """
        def __nonzero__(self):
            """Resolve our final call and check for empty/nonzero on it"""
            return bool(self.getFinalCall())
        def __call__( self, *args, **named ):
            """Call self._finalCall, calling finalise() first if not already called

            There's actually *no* reason to unpack and repack the arguments,
            but unfortunately I don't know of a Cython syntax to specify
            that.
            """
            try:
                return self._finalCall( *args, **named )
            except (TypeError,AttributeError) as err:
                if self._finalCall is None:
                    self._finalCall = self.finalise()
                return self._finalCall( *args, **named )
if Curry is None:
    class Curry(object):
        """Provides a simple Curry which can bind (only) the first element

        This is used by lazywrapper, which explains the weird naming
        of the two attributes...
        """
        wrapperFunction = None
        baseFunction = None
        def __init__( self, wrapperFunction, baseFunction ):
            """Stores self.wrapperFunction and self.baseFunction"""
            self.baseFunction = baseFunction
            self.wrapperFunction = wrapperFunction
        def __call__( self, *args, **named ):
            """returns self.wrapperFunction( self.baseFunction, *args, **named )"""
            return self.wrapperFunction( self.baseFunction, *args, **named )
