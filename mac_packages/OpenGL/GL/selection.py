"""Selection-buffer handling code

This code is resonsible for turning gluint *
arrays into structured representations for use
by Python-level code.
"""
from OpenGL._bytes import integer_types

def uintToLong( value ):
    if value < 0:
        # array type without a uint, so represented as an int 
        value = (value & 0x7fffffff) + 0x80000000
    return value

class GLSelectRecord( object ):
    """Minimalist object for storing an OpenGL selection-buffer record
    
    Provides near and far as *float* values by dividing by 
    self.DISTANCE_DIVISOR (2**32-1)
    From the spec:
        Depth values (which are in the range [0,1]) are multiplied by 
        2^32 - 1, before being placed in the hit record.
    
    Names are unmodified, so normally are slices of the array passed in 
    to GLSelectRecord.fromArray( array )
    """
    DISTANCE_DIVISOR = float((2**32)-1)
    __slots__ = ('near','far','names')
    def fromArray( cls, array, total ):
        """Produce list with all records from the array"""
        result = []
        index = 0
        arrayLength = len(array)
        for item in range( total ):
            if index + 2 >= arrayLength:
                break
            count = array[index]
            near = array[index+1]
            far = array[index+2]
            names = [ uintToLong(v) for v in array[index+3:index+3+count]]
            result.append(  cls( near, far, names ) )
            index += 3+count
        return result
    fromArray = classmethod( fromArray )
    
    def __init__( self, near, far, names ):
        """Initialise/store the values"""
        self.near = self.convertDistance( near )
        self.far = self.convertDistance( far )
        self.names = names 
    def convertDistance( self, value ):
        """Convert a distance value from array uint to 0.0-1.0 range float"""
        return uintToLong( value ) / self.DISTANCE_DIVISOR
    def __getitem__( self, key ):
        """Allow for treating the record as a three-tuple"""
        if isinstance( key, integer_types):
            return (self.near,self.far,self.names)[key]
        elif key in self.__slots__:
            try:
                return getattr( self, key )
            except AttributeError as err:
                raise KeyError( """Don't have an index/key %r for %s instant"""%(
                    key, self.__class__,
                ))
