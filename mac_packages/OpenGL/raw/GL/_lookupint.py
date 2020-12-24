"""Integer values looked up via glGetIntegerv( constant )"""
import ctypes
_get = None
_get_float = None

class LookupInt( object ):
    def __init__( self, lookup, format=ctypes.c_int, calculation=None ):
        self.lookup = lookup 
        self.format = format
        self.calculation = calculation
    def __int__( self ):
        global _get
        if _get is None:
            from OpenGL.GL import glGetIntegerv
            _get = glGetIntegerv
        output = self.format()
        _get( self.lookup, output )
        if self.calculation:
            return self.calculation( output.value )
        return output.value
    __long__ = __int__
    def __eq__( self, other ):
        return int(self) == other
    def __cmp__( self, other ):
        return cmp( int(self), other )
    def __str__(self):
        return str(int(self))
    __repr__ = __str__
