"""Run-time calculation of offset into Python string structure

Does a scan to find the digits of pi in a string structure
in order to produce an offset that can be used to produce 
data-pointers from Python strings.

Porting note:
    
    Currently this uses id( str a ) to get the base address
    of the Python string.  Python implementations where id( a )
    is *not* the memory address of the string will not work!
"""
from __future__ import print_function
import ctypes
from OpenGL._bytes import bytes
PI_DIGITS = '31415926535897931'

def calculateOffset( ):
    """Calculates the data-pointer offset for strings
    
    This does a sequential scan for 100 bytes from the id
    of a string to find special data-value stored in the
    string (the digits of PI).  It produces a dataPointer
    function which adds that offset to the id of the 
    passed strings.
    """
    finalOffset = None
    a = PI_DIGITS
    # XXX NOT portable across Python implmentations!!!
    initial = id(a)
    targetType = ctypes.POINTER( ctypes.c_char )
    for offset in range( 100 ):
        vector = ctypes.cast( initial+offset,targetType )
        allMatched = True
        for index,digit in enumerate( a ):
            if vector[index] != digit:
                allMatched = False
                break
        if allMatched:
            finalOffset = offset
            break
    if finalOffset is not None:
        def dataPointer( data ):
            """Return the data-pointer from the array using calculated offset
            
            data -- a Python string
            
            Returns the raw data-pointer to the internal buffer of the passed string
            """
            if not isinstance( data, bytes ):
                raise TypeError(
                    """This function can only handle Python strings!  Got %s"""%(
                        type(data),
                    )
                )
            return id(data) + finalOffset
        # just for later reference...
        dataPointer.offset = finalOffset 
        return dataPointer
    raise RuntimeError(
        """Unable to determine dataPointer offset for strings!"""
    )

dataPointer = calculateOffset()

if __name__ == "__main__":
    a  = 'this'
    print((id(a), dataPointer( a ), dataPointer(a) - id(a)))
    
