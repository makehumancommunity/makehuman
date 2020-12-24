"""VertexBufferObject helper class

Basic usage:

    my_data = numpy.array( data, 'f')
    my_vbo = vbo.VBO( my_data )
    ...
    my_vbo.bind()
    try:
        ...
        glVertexPointer( my_vbo, ... )
        ...
        glNormalPointer( my_vbo + 12, ... )
    finally:
        my_vbo.unbind()
    
    or 
    
    with my_vbo:
        ...
        glVertexPointer( my_vbo, ... )
        ...
        glNormalPointer( my_vbo + 12, ... )        

See the OpenGLContext shader tutorials for a gentle introduction on the 
usage of VBO objects:

    http://pyopengl.sourceforge.net/context/tutorials/shader_intro.xhtml

This implementation will choose either the ARB or Core (OpenGL 1.5) 
implementation of the VBO functions.
"""
from OpenGL.arrays.arraydatatype import ArrayDatatype
from OpenGL.arrays.formathandler import FormatHandler
from OpenGL.raw.GL import _types 
from OpenGL import error
from OpenGL._bytes import bytes,unicode,as_8_bit
import ctypes,logging
_log = logging.getLogger( 'OpenGL.arrays.vbo' )
from OpenGL._bytes import long, integer_types

import weakref
__all__ = ('VBO','VBOHandler','mapVBO')

class Implementation( object ):
    """Abstraction point for the various implementations that can be used
    """
    IMPLEMENTATION_CLASSES = []
    CHOSEN = None
    @classmethod
    def register( cls ):
        cls.IMPLEMENTATION_CLASSES.append( cls )
    
    @classmethod 
    def get_implementation( cls, *args ):
        if cls.CHOSEN is None:
            for possible in cls.IMPLEMENTATION_CLASSES:
                implementation = possible()
                if possible:
                    Implementation.CHOSEN = implementation
                    break
        return cls.CHOSEN

    EXPORTED_NAMES = '''glGenBuffers
    glBindBuffer 
    glBufferData 
    glBufferSubData 
    glDeleteBuffers
    glMapBuffer
    glUnmapBuffer
    GL_STATIC_DRAW
    GL_STATIC_READ
    GL_STATIC_COPY
    GL_DYNAMIC_DRAW
    GL_DYNAMIC_READ
    GL_DYNAMIC_COPY
    GL_STREAM_DRAW
    GL_STREAM_READ
    GL_STREAM_COPY
    GL_ARRAY_BUFFER
    GL_ELEMENT_ARRAY_BUFFER
    GL_UNIFORM_BUFFER
    GL_TEXTURE_BUFFER
    GL_TRANSFORM_FEEDBACK_BUFFER'''.split()
    available = False
    def _arbname( self, name ):
        return (
            (name.startswith( 'gl' ) and name.endswith( 'ARB' )) or
            (name.startswith( 'GL_' ) and name.endswith( 'ARB' ))
        ) and (name != 'glInitVertexBufferObjectARB')
    def basename( self, name ):
        if name.endswith( '_ARB' ):
            return name[:-4]
        elif name.endswith( 'ARB' ):
            return name[:-3]
        else:
            return name
    def __nonzero__( self ):
        return self.available
    __bool__ = __nonzero__
    def deleter( self, buffers, key):
        """Produce a deleter callback to delete the given buffer"""
        # these values are stored here to avoid them being cleaned up 
        # to non during module deletion and causing errors to be raised
        nfe = error.NullFunctionError
        gluint = _types.GLuint
        def doBufferDeletion( *args, **named ):
            while buffers:
                try:
                    buffer = buffers.pop()
                except IndexError as err:
                    break
                else:
                    try:
                        # Note that to avoid ERROR_ON_COPY issues
                        # we have to pass an array-compatible type here...
                        buf = gluint( buffer )
                        self.glDeleteBuffers(1, buf)
                    except (AttributeError, nfe, TypeError) as err:
                        pass
            try:
                self._DELETERS_.pop( key )
            except KeyError as err:
                pass
        return doBufferDeletion
    _DELETERS_ = {}

get_implementation = Implementation.get_implementation

from OpenGL import acceleratesupport
VBO = None
if acceleratesupport.ACCELERATE_AVAILABLE:
    try:
        from OpenGL_accelerate.vbo import (
            VBO,VBOOffset,VBOHandler,VBOOffsetHandler,
        )
    except ImportError as err:
        _log.warning(
            "Unable to load VBO accelerator from OpenGL_accelerate"
        )
if VBO is None:
    class VBO( object ):
        """Instances can be passed into array-handling routines

        You can check for whether VBOs are supported by accessing the implementation:

            if bool(vbo.get_implementation()):
                # vbo version of code
            else:
                # fallback version of code
        """
        copied = False
        _no_cache_ = True # do not cache in context data arrays
        def __init__(
            self, data, usage='GL_DYNAMIC_DRAW',
            target='GL_ARRAY_BUFFER', size=None,
        ):
            """Initialize the VBO object 
            
            data -- PyOpenGL-compatible array-data structure, numpy arrays, ctypes arrays, etc.
            usage -- OpenGL usage constant describing expected data-flow patterns (this is a hint 
                to the GL about where/how to cache the data)
                
                GL_STATIC_DRAW_ARB
                GL_STATIC_READ_ARB
                GL_STATIC_COPY_ARB
                GL_DYNAMIC_DRAW_ARB
                GL_DYNAMIC_READ_ARB
                GL_DYNAMIC_COPY_ARB
                GL_STREAM_DRAW_ARB
                GL_STREAM_READ_ARB
                GL_STREAM_COPY_ARB
                
                DRAW constants suggest to the card that the data will be primarily used to draw 
                on the card.  READ that the data will be read back into the GL.  COPY means that 
                the data will be used both for DRAW and READ operations.
                
                STATIC suggests that the data will only be written once (or a small number of times).
                DYNAMIC suggests that the data will be used a small number of times before being 
                discarded.
                STREAM suggests that the data will be updated approximately every time that it is 
                used (that is, it will likely only be used once).
                
            target -- VBO target to which to bind (array or indices)
                GL_ARRAY_BUFFER -- array-data binding 
                GL_ELEMENT_ARRAY_BUFFER -- index-data binding
                GL_UNIFORM_BUFFER -- used to pass mid-size arrays of data packed into a buffer
                GL_TEXTURE_BUFFER -- used to pass large arrays of data as a pseudo-texture
                GL_TRANSFORM_FEEDBACK_BUFFER -- used to receive transformed vertices for processing
                
            size -- if not provided, will use arrayByteCount to determine the size of the data-array,
                thus this value (number of bytes) is required when using opaque data-structures,
                (such as ctypes pointers) as the array data-source.
            """
            self.usage = usage
            self.set_array( data, size )
            self.target = target
            self.buffers = []
            self._copy_segments = []
        _I_ = None
        implementation = property( get_implementation, )
        def resolve( self, value ):
            """Resolve string constant to constant"""
            if isinstance( value, (bytes,unicode)):
                return getattr( self.implementation, self.implementation.basename( value ) )
            return value
        def set_array( self, data, size=None ):
            """Update our entire array with new data
            
            data -- PyOpenGL-compatible array-data structure, numpy arrays, ctypes arrays, etc.
            size -- if not provided, will use arrayByteCount to determine the size of the data-array,
                thus this value (number of bytes) is required when using opaque data-structures,
                (such as ctypes pointers) as the array data-source.
            """
            self.data = data
            self.copied = False
            if size is not None:
                self.size = size
            elif self.data is not None:
                self.size = ArrayDatatype.arrayByteCount( self.data )
        def __setitem__( self, slice, array):
            """Set slice of data on the array and vbo (if copied already)

            slice -- the Python slice object determining how the data should
                be copied into the vbo/array
            array -- something array-compatible that will be used as the
                source of the data, note that the data-format will have to
                be the same as the internal data-array to work properly, if
                not, the amount of data copied will be wrong.

            This is a reasonably complex operation, it has to have all sorts
            of state-aware changes to correctly map the source into the low-level
            OpenGL view of the buffer (which is just bytes as far as the GL
            is concerned).
            """
            if slice.step and not slice.step == 1:
                raise NotImplemented( """Don't know how to map stepped arrays yet""" )
            # TODO: handle e.g. mapping character data into an integer data-set
            data = ArrayDatatype.asArray( array )
            data_length = ArrayDatatype.arrayByteCount( array )
            start = (slice.start or 0)
            stop = (slice.stop or len(self.data))
            if start < 0:
                start += len(self.data)
                start = max((start,0))
            if stop < 0:
                stop += len(self.data)
                stop = max((stop,0))
            self.data[ slice ] = data
            if self.copied and self.buffers:
                if start-stop == len(self.data):
                    # re-copy the whole data-set
                    self.copied = False
                elif len(data):
                    # now the fun part, we need to make the array match the
                    # structure of the array we're going to copy into and make
                    # the "size" parameter match the value we're going to copy in,
                    # note that a 2D array (rather than a 1D array) may require
                    # multiple mappings to copy into the memory area...

                    # find the step size from the dimensions and base size...
                    size = ArrayDatatype.arrayByteCount( self.data[0] )
                    #baseSize = ArrayDatatype.unitSize( data )
                    # now create the start and distance values...
                    start *= size
                    stop *= size
                    # wait until the last moment (bind) to copy the data...
                    self._copy_segments.append(
                        (start,(stop-start), data)
                    )
        def __len__( self ):
            """Delegate length/truth checks to our data-array"""
            return len( self.data )
        def __getattr__( self, key ):
            """Delegate failing attribute lookups to our data-array"""
            if key not in ('data','usage','target','buffers', 'copied','_I_','implementation','_copy_segments' ):
                return getattr( self.data, key )
            else:
                raise AttributeError( key )
        def create_buffers( self ):
            """Create the internal buffer(s)"""
            assert not self.buffers, """Already created the buffer"""
            self.buffers = [ long(self.implementation.glGenBuffers(1)) ]
            self.target = self.resolve( self.target )
            self.usage = self.resolve( self.usage )
            self.implementation._DELETERS_[ id(self) ] = weakref.ref( self, self.implementation.deleter( self.buffers, id(self) ))
            return self.buffers
        def copy_data( self ):
            """Copy our data into the buffer on the GL side (if required)
            
            Ensures that the GL's version of the data in the VBO matches our 
            internal view of the data, either by copying the entire data-set 
            over with glBufferData or by updating the already-transferred 
            data with glBufferSubData.
            """
            assert self.buffers, """Should do create_buffers before copy_data"""
            if self.copied:
                if self._copy_segments:
                    while self._copy_segments:
                        start,size,data  = self._copy_segments.pop(0)
                        dataptr = ArrayDatatype.voidDataPointer( data )
                        self.implementation.glBufferSubData(self.target, start, size, dataptr)
            else:
                if self.data is not None and self.size is None:
                    self.size = ArrayDatatype.arrayByteCount( self.data )
                self.implementation.glBufferData(
                    self.target,
                    self.size,
                    self.data,
                    self.usage,
                )
                self.copied = True
        def delete( self ):
            """Delete this buffer explicitly"""
            if self.buffers:
                while self.buffers:
                    try:
                        self.implementation.glDeleteBuffers(1, self.buffers.pop(0))
                    except (AttributeError,error.NullFunctionError) as err:
                        pass
        def __int__( self ):
            """Get our VBO id"""
            if not self.buffers:
                self.create_buffers()
            return self.buffers[0]
        def bind( self ):
            """Bind this buffer for use in vertex calls
            
            If we have not yet created our implementation-level VBO, then we 
            will create it before binding.  Once bound, calls self.copy_data()
            """
            if not self.buffers:
                buffers = self.create_buffers()
            self.implementation.glBindBuffer( self.target, self.buffers[0])
            self.copy_data()
        def unbind( self ):
            """Unbind the buffer (make normal array operations active)"""
            self.implementation.glBindBuffer( self.target,0 )

        def __add__( self, other ):
            """Add an integer to this VBO (create a VBOOffset)"""
            if hasattr( other, 'offset' ):
                other = other.offset
            assert isinstance( other, integer_types ), """Only know how to add integer/long offsets"""
            return VBOOffset( self, other )

        __enter__ = bind
        def __exit__( self, exc_type=None, exc_val=None, exc_tb=None ):
            """Context manager exit"""
            self.unbind()
            return False # do not supress exceptions...

    class VBOOffset( object ):
        """Offset into a VBO instance 
        
        This class is normally instantiated by doing a my_vbo + int operation,
        it can be passed to VBO requiring operations and will generate the 
        appropriate integer offset value to be passed in.
        """
        def __init__( self, vbo, offset ):
            """Initialize the offset with vbo and offset (unsigned integer)"""
            self.vbo = vbo
            self.offset = offset
        def __getattr__( self, key ):
            """Delegate any undefined attribute save vbo to our vbo"""
            if key != 'vbo':
                return getattr( self.vbo, key )
            raise AttributeError( 'No %r key in VBOOffset'%(key,))
        def __add__( self, other ):
            """Allow adding integers or other VBOOffset instances 
            
            returns a VBOOffset to the this VBO with other.offset + self.offset
            or, if other has no offset, returns VBOOffset with self.offset + other
            """
            if hasattr( other, 'offset' ):
                other = other.offset
            return VBOOffset( self.vbo, self.offset + other )

    class VBOHandler( FormatHandler ):
        """Handles VBO instances passed in as array data
        
        This FormatHandler is registered with PyOpenGL on import of this module 
        to provide handling of VBO objects as array data-sources
        """
        vp0 = ctypes.c_void_p( 0 )
        def dataPointer( self, instance ):
            """Retrieve data-pointer from the instance's data

            Is always NULL, to indicate use of the bound pointer
            """
            return 0
        def from_param( self, instance, typeCode=None ):
            """Always returns c_void_p(0)"""
            return self.vp0
        def zeros( self, dims, typeCode ):
            """Not implemented"""
            raise NotImplemented( """Don't have VBO output support yet""" )
        ones = zeros
        def asArray( self, value, typeCode=None ):
            """Given a value, convert to array representation"""
            return value
        def arrayToGLType( self, value ):
            """Given a value, guess OpenGL type of the corresponding pointer"""
            return ArrayDatatype.arrayToGLType( value.data )
        def arrayByteCount( self, value ):
            return ArrayDatatype.arrayByteCount( value.data )
        def arraySize( self, value, typeCode = None ):
            """Given a data-value, calculate dimensions for the array"""
            return ArrayDatatype.arraySize( value.data )
        def unitSize( self, value, typeCode=None ):
            """Determine unit size of an array (if possible)"""
            return ArrayDatatype.unitSize( value.data )
        def dimensions( self, value, typeCode=None ):
            """Determine dimensions of the passed array value (if possible)"""
            return ArrayDatatype.dimensions( value.data )

    class VBOOffsetHandler( VBOHandler ):
        """Handles VBOOffset instances passed in as array data
        
        Registered on module import to provide support for VBOOffset instances 
        as sources for array data.
        """
        def dataPointer( self, instance ):
            """Retrieve data-pointer from the instance's data

            returns instance' offset
            """
            return instance.offset
        def from_param( self, instance, typeCode=None ):
            """Returns a c_void_p( instance.offset )"""
            return ctypes.c_void_p( instance.offset )

_cleaners = {}
def _cleaner( vbo ):
    """Construct a mapped-array cleaner function to unmap vbo.target"""
    def clean( ref ):
        try:
            _cleaners.pop( vbo )
        except Exception as err:
            pass
        else:
            vbo.implementation.glUnmapBuffer( vbo.target )
    return clean

def mapVBO( vbo, access=0x88BA ): # GL_READ_WRITE
    """Map the given buffer into a numpy array...

    Method taken from:
     http://www.mail-archive.com/numpy-discussion@lists.sourceforge.net/msg01161.html

    This should be considered an *experimental* API,
    it is not guaranteed to be available in future revisions
    of this library!
    
    Simplification to use ctypes cast from comment by 'sashimi' on my blog...
    """
    from numpy import frombuffer
    vp = vbo.implementation.glMapBuffer( vbo.target, access )
    # TODO: obviously this is not the right way to do this should allow each format 
    # handler to convert the pointer in their own way...
    vp_array = ctypes.cast(vp, ctypes.POINTER(ctypes.c_byte*vbo.size) )
    # Note: we could have returned the raw ctypes.c_byte array instead...
    array = frombuffer( vp_array, 'B' )
    _cleaners[vbo] = weakref.ref( array, _cleaner( vbo ))
    return array
