"""GLE exceptional functions (specialised signatures"""
from OpenGL.raw import GLE as raw
from OpenGL.raw.GLE import annotations as _simple

from OpenGL import wrapper, arrays

class _lengthOfArgname( object ):
    """Calculates the length of a given argname over a divisor value"""
    def __init__( self, arrayName, divisor, arrayType = arrays.GLdoubleArray ):
        self.arrayName = arrayName
        self.divisor = divisor
        self.arrayType = arrayType
    def finalise( self, wrapper ):
        self.arrayIndex = wrapper.pyArgIndex( self.arrayName )
    def __call__( self, pyArgs, index, wrappedOperation ):
        """Get the length of pyArgs[2], a glDoubleArray"""
        return self.arrayType.arraySize( pyArgs[self.arrayIndex] )//self.divisor
def _baseWrap( base, lengthName='ncp', contourName='contour', divisor=2 ):
    """Do the basic wrapping operation for a GLE function"""
    return wrapper.wrapper( base ).setPyConverter(
        lengthName,
    ).setCConverter(
        lengthName, _lengthOfArgname( contourName, divisor, arrays.GLdoubleArray ),
    )

gleLathe = _baseWrap( _simple.gleLathe )
glePolyCone = _baseWrap( _simple.glePolyCone, 'npoints', 'point_array', 3)
glePolyCylinder = _baseWrap( _simple.glePolyCylinder, 'npoints', 'point_array', 3)
gleScrew = _baseWrap( _simple.gleScrew )
gleSpiral = _baseWrap( _simple.gleSpiral )

gleExtrusion = _baseWrap( 
    _baseWrap( _simple.gleExtrusion ),
    'npoints', 'point_array', 3
)
gleSuperExtrusion = _baseWrap( 
    _baseWrap( _simple.gleSuperExtrusion ),
    'npoints', 'point_array', 3
)
gleTwistExtrusion = _baseWrap( 
    _baseWrap( _simple.gleTwistExtrusion ),
    'npoints', 'point_array', 3
)