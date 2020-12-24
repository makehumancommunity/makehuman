"""Data-type definitions for EGL/GLES"""
import ctypes
pointer = ctypes.pointer

class _Opaque( ctypes.Structure ):
    """An Opaque Structure reference (base class)"""
class _opaque_pointer( ctypes.POINTER( _Opaque ) ):
    _type_ = _Opaque
    @classmethod
    def from_param( cls, value ):
        return ctypes.cast( value, cls )
    @property
    def address( self ):
        return ctypes.addressof( self.contents )
    @property 
    def as_voidp( self ):
        return ctypes.c_voidp( self.address )
    def __hash__(self):
        """Allow these pointers to be used as keys in dictionaries"""
        return self.address
def opaque_pointer_cls( name ):
    """Create an Opaque pointer class for the given name"""
    typ = type( name, (_Opaque,), {} )
    p_typ = type( name+'_pointer', (_opaque_pointer,), {'_type_':typ})
    return p_typ
