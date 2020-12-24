"""8-bit string definitions for Python 2/3 compatibility

Defines the following which allow for dealing with Python 3 breakages:

    STR_IS_BYTES
    STR_IS_UNICODE
    
        Easily checked booleans for type identities
    
    _NULL_8_BYTE
    
        An 8-bit byte with NULL (0) value 
    
    as_8_bit( x, encoding='utf-8')
    
        Returns the value as the 8-bit version
    
    unicode -- always pointing to the unicode type 
    bytes -- always pointing to the 8-bit bytes type
"""
import sys

STR_IS_BYTES = True

if sys.version_info[:2] < (2,6):
    # no bytes, traditional setup...
    bytes = str 
else:
    bytes = bytes
try:
    long = long
except NameError as err:
    long = int
if sys.version_info[:2] < (3,0):
    # traditional setup, with bytes defined...
    unicode = unicode
    _NULL_8_BYTE = '\000'
    def as_8_bit( x, encoding='utf-8' ):
        if isinstance( x, unicode ):
            return x.encode( encoding )
        return bytes( x )
    integer_types = int,long
    def as_str( x, encoding='utf-8'):
        """Produce a native string (i.e. different on python 2 and 3)"""
        if isinstance(x,bytes):
            return x
        elif isinstance(x,unicode):
            return x.encode(encoding)
        else:
            return str(x)
else:
    # new setup, str is now unicode...
    STR_IS_BYTES = False
    _NULL_8_BYTE = bytes( '\000','latin1' )
    def as_8_bit( x, encoding='utf-8' ):
        if isinstance( x,unicode ):
            return x.encode(encoding)
        elif isinstance( x, bytes ):
            # Note: this can create an 8-bit string that is *not* in encoding,
            # but that is potentially exactly what we wanted, as these can 
            # be arbitrary byte-streams being passed to C functions
            return x
        return str(x).encode( encoding )
    unicode = str
    integer_types = int,
    def as_str( x, encoding='utf-8'):
        """Produce a native string (i.e. different on python 2 and 3)"""
        if isinstance(x,unicode):
            return x
        elif isinstance(x,bytes):
            return x.decode(encoding)
        else:
            return str(x)

STR_IS_UNICODE = not STR_IS_BYTES
if hasattr( sys, 'maxsize' ):
    maxsize = sys.maxsize 
else:
    maxsize = sys.maxint

def as_unicode(x,encoding='utf-8'):
    """Ensure is a unicode object given default encoding"""
    if isinstance(x,unicode):
        return x
    elif isinstance(x,bytes):
        try:
            return x.decode(encoding)
        except UnicodeDecodeError as err:
            return x.decode('latin-1')
    else:
        return unicode(x)

