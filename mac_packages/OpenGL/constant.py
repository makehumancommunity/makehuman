"""Implementation of OpenGL constant objects"""
import sys
from OpenGL._bytes import bytes,unicode,as_8_bit, long, integer_types, maxsize
from OpenGL import _configflags

class Constant( object ):
    """OpenGL constant that displays itself as a name rather than a value

    The purpose of this class is to make debugging OpenGL code easier,
    as you recieve messages that say what value you passed in in a
    human-readable form, rather than as a bald number that requires
    lookup and disambiguation in the header file.
    """
    def __new__( cls, name, value=None ):
        """Initialise the constant with the given name and value"""
        if not isinstance( value, Constant ):
            if isinstance( value, float ) and cls is not FloatConstant:
                return FloatConstant( name, value )
            elif isinstance( value, int ) and cls is not IntConstant:
                return IntConstant( name, value )
            elif isinstance( value, long ) and cls is not LongConstant:
                return LongConstant( name, value )
            elif isinstance( value, (bytes,unicode) ) and cls is not StringConstant:
                return StringConstant( name, as_8_bit(value) )
        if isinstance( value, integer_types ):
            if value > maxsize: # TODO: I'm guessing this should really by sizeof GLint, not 
                value = - (value & maxsize)
        base = super(Constant,cls).__new__( cls, value )
        base.name = name
        if _configflags.MODULE_ANNOTATIONS:
            frame = sys._getframe().f_back
            if frame and frame.f_back and '__name__' in frame.f_back.f_globals:
                base.__module__ = frame.f_back.f_globals['__name__']
        return base
    def __repr__( self ):
        """Return the name, rather than the bald value"""
        return self.name
    def __getnewargs__( self ):
        """Produce the new arguments for recreating the instance"""
        return (self.name,) + super( Constant, self ).__getnewargs__()

class NumericConstant( Constant ):
    """Base class for numeric-value constants"""
    def __str__( self ):
        """Return the value as a human-friendly string"""
        return '%s (%s)'%(self.name,super(Constant,self).__str__())
    def __getstate__(self):
        """Retrieve state for pickle and the like"""
        return self.name
    def __setstate__( self, state ):
        self.name = state

class IntConstant( NumericConstant, int ):
    """Integer constant"""
if int is not long:
    class LongConstant( NumericConstant, long ):
        """Long integer constant"""
else:
    LongConstant = IntConstant
class FloatConstant( NumericConstant, float ):
    """Float constant"""

class StringConstant( Constant, bytes ):
    """String constants"""
    def __repr__( self ):
        """Return the value as a human-friendly string"""
        return '%s (%s)'%(self.name,super(Constant,self).__str__())

if __name__ == "__main__":
    x = IntConstant( 'testint', 3 )
    y = FloatConstant( 'testfloat', 3.0 )
    z = StringConstant( 'teststr', 'some testing string' )

    import pickle
    for val in x,y,z:
        restored = pickle.loads( pickle.dumps( val ))
        assert restored == val, (str(restored),str(val))
        assert restored.name == val.name, (restored.name,val.name)
