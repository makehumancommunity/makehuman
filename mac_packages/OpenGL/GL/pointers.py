"""Implementations for "held-pointers" of various types

This argument type is special because it is stored, that is, it
needs to be cached on our side so that the memory address does not
go out-of-scope

storedPointers = {}
def glVertexPointerd( array ):
    "Natural writing of glVertexPointerd using standard ctypes"
    arg2 = GL_DOUBLE
    arg3 = 0 # stride
    arg4 = arrays.asArray(array, GL_DOUBLE)
    arg1 = arrays.arraySize( arg4, 'd' )
    platform.PLATFORM.GL.glVertexPointer( arg1, arg2, arg3, arrays.ArrayDatatype.dataPointer(arg4) )
    # only store if we successfully set the value...
    storedPointers[ GL_VERTEX_ARRAY ] = arg4
    return arg4
"""
from OpenGL import platform, error, wrapper, contextdata, converters, constant
from OpenGL.arrays import arrayhelpers, arraydatatype
from OpenGL.raw.GL.VERSION import GL_1_1 as _simple
import ctypes

GLsizei = ctypes.c_int
GLenum = ctypes.c_uint
GLint = ctypes.c_int
# OpenGL-ctypes variables that mimic OpenGL constant operation...
GL_INTERLEAVED_ARRAY_POINTER = constant.Constant( 'GL_INTERLEAVED_ARRAY_POINTER', -32910 )

__all__ = (
    'glColorPointer',
    'glColorPointerb','glColorPointerd','glColorPointerf','glColorPointeri',
    'glColorPointers','glColorPointerub','glColorPointerui','glColorPointerus',
    'glEdgeFlagPointer',
    'glEdgeFlagPointerb',
    'glIndexPointer',
    'glIndexPointerb','glIndexPointerd','glIndexPointerf',
    'glIndexPointeri','glIndexPointers','glIndexPointerub',
    'glNormalPointer',
    'glNormalPointerb',
    'glNormalPointerd','glNormalPointerf','glNormalPointeri','glNormalPointers',
    'glTexCoordPointer',
    'glTexCoordPointerb','glTexCoordPointerd','glTexCoordPointerf',
    'glTexCoordPointeri','glTexCoordPointers',
    'glVertexPointer',
    'glVertexPointerb','glVertexPointerd','glVertexPointerf','glVertexPointeri',
    'glVertexPointers',
    'glDrawElements','glDrawElementsui','glDrawElementsub','glDrawElementsus',
    'glFeedbackBuffer',
    'glSelectBuffer',
    'glRenderMode',
    'glGetPointerv',
    'glInterleavedArrays',
    'GL_INTERLEAVED_ARRAY_POINTER',
)


# Have to create *new* ctypes wrappers for the platform object!
# We can't just alter the default one since we have different ways of
# calling it

POINTER_FUNCTION_DATA = [
    ('glColorPointerd',  _simple.glColorPointer, _simple.GL_DOUBLE, _simple.GL_COLOR_ARRAY_POINTER, 0, 3),
    ('glColorPointerf',  _simple.glColorPointer, _simple.GL_FLOAT, _simple.GL_COLOR_ARRAY_POINTER, 0, 3),
    ('glColorPointeri',  _simple.glColorPointer, _simple.GL_INT, _simple.GL_COLOR_ARRAY_POINTER, 0, 3),
    ('glColorPointers',  _simple.glColorPointer, _simple.GL_SHORT, _simple.GL_COLOR_ARRAY_POINTER, 0, 3),
    ('glColorPointerub', _simple.glColorPointer, _simple.GL_UNSIGNED_BYTE, _simple.GL_COLOR_ARRAY_POINTER, 0, 3),
    # these data-types are mapped from diff Numeric types
    ('glColorPointerb',  _simple.glColorPointer, _simple.GL_BYTE, _simple.GL_COLOR_ARRAY_POINTER, 0, 3),
    ('glColorPointerui', _simple.glColorPointer, _simple.GL_UNSIGNED_INT, _simple.GL_COLOR_ARRAY_POINTER, 0, 3),
    ('glColorPointerus', _simple.glColorPointer, _simple.GL_UNSIGNED_SHORT, _simple.GL_COLOR_ARRAY_POINTER, 0, 3),

    ('glEdgeFlagPointerb', _simple.glEdgeFlagPointer, _simple.GL_BYTE, _simple.GL_EDGE_FLAG_ARRAY_POINTER, 2, None),

    ('glIndexPointerd',  _simple.glIndexPointer, _simple.GL_DOUBLE, _simple.GL_INDEX_ARRAY_POINTER, 1, None),
    ('glIndexPointerf',  _simple.glIndexPointer, _simple.GL_FLOAT, _simple.GL_INDEX_ARRAY_POINTER, 1, None),
    ('glIndexPointeri',  _simple.glIndexPointer, _simple.GL_INT, _simple.GL_INDEX_ARRAY_POINTER, 1, None),
    ('glIndexPointerub', _simple.glIndexPointer, _simple.GL_UNSIGNED_BYTE, _simple.GL_INDEX_ARRAY_POINTER, 1, None),
    ('glIndexPointers',  _simple.glIndexPointer, _simple.GL_SHORT, _simple.GL_INDEX_ARRAY_POINTER, 1, None),
    # these data-types are mapped from diff Numeric types
    ('glIndexPointerb',  _simple.glIndexPointer, _simple.GL_BYTE, _simple.GL_INDEX_ARRAY_POINTER, 1, None),

    ('glNormalPointerd',  _simple.glNormalPointer, _simple.GL_DOUBLE, _simple.GL_NORMAL_ARRAY_POINTER, 1, None),
    ('glNormalPointerf',  _simple.glNormalPointer, _simple.GL_FLOAT, _simple.GL_NORMAL_ARRAY_POINTER, 1, None),
    ('glNormalPointeri',  _simple.glNormalPointer, _simple.GL_INT, _simple.GL_NORMAL_ARRAY_POINTER, 1, None),
    ('glNormalPointerb',  _simple.glNormalPointer, _simple.GL_BYTE, _simple.GL_NORMAL_ARRAY_POINTER, 1, None),
    ('glNormalPointers',  _simple.glNormalPointer, _simple.GL_SHORT, _simple.GL_NORMAL_ARRAY_POINTER, 1, None),

    ('glTexCoordPointerd',  _simple.glTexCoordPointer, _simple.GL_DOUBLE, _simple.GL_TEXTURE_COORD_ARRAY_POINTER, 0, 2),
    ('glTexCoordPointerf',  _simple.glTexCoordPointer, _simple.GL_FLOAT, _simple.GL_TEXTURE_COORD_ARRAY_POINTER, 0, 2),
    ('glTexCoordPointeri',  _simple.glTexCoordPointer, _simple.GL_INT, _simple.GL_TEXTURE_COORD_ARRAY_POINTER, 0, 2),
    ('glTexCoordPointerb',  _simple.glTexCoordPointer, _simple.GL_BYTE, _simple.GL_TEXTURE_COORD_ARRAY_POINTER, 0, 2),
    ('glTexCoordPointers',  _simple.glTexCoordPointer, _simple.GL_SHORT, _simple.GL_TEXTURE_COORD_ARRAY_POINTER, 0, 2),

    ('glVertexPointerd', _simple.glVertexPointer, _simple.GL_DOUBLE, _simple.GL_VERTEX_ARRAY_POINTER, 0, 3),
    ('glVertexPointerf', _simple.glVertexPointer, _simple.GL_FLOAT, _simple.GL_VERTEX_ARRAY_POINTER, 0, 3),
    ('glVertexPointeri', _simple.glVertexPointer, _simple.GL_INT, _simple.GL_VERTEX_ARRAY_POINTER, 0, 3),
    ('glVertexPointerb', _simple.glVertexPointer, _simple.GL_INT, _simple.GL_VERTEX_ARRAY_POINTER, 0, 3),
    ('glVertexPointers', _simple.glVertexPointer, _simple.GL_SHORT, _simple.GL_VERTEX_ARRAY_POINTER, 0, 3),
]
def wrapPointerFunction( name, baseFunction, glType, arrayType,startArgs, defaultSize ):
    """Wrap the given pointer-setting function"""
    function= wrapper.wrapper( baseFunction )
    if 'ptr' in baseFunction.argNames:
        pointer_name = 'ptr'
    else:
        pointer_name = 'pointer'
    assert not getattr( function, 'pyConverters', None ), """Reusing wrappers?"""
    if arrayType:
        arrayModuleType = arraydatatype.GL_CONSTANT_TO_ARRAY_TYPE[ glType ]
        function.setPyConverter( pointer_name, arrayhelpers.asArrayType(arrayModuleType) )
    else:
        function.setPyConverter( pointer_name, arrayhelpers.AsArrayOfType(pointer_name,'type') )
    function.setCConverter( pointer_name, converters.getPyArgsName( pointer_name ) )
    if 'size' in function.argNames:
        function.setPyConverter( 'size' )
        function.setCConverter( 'size', arrayhelpers.arraySizeOfFirstType(arrayModuleType,defaultSize) )
    if 'type' in function.argNames:
        function.setPyConverter( 'type' )
        function.setCConverter( 'type', glType )
    if 'stride' in function.argNames:
        function.setPyConverter( 'stride' )
        function.setCConverter( 'stride', 0 )
    function.setStoreValues( arrayhelpers.storePointerType( pointer_name, arrayType ) )
    function.setReturnValues( wrapper.returnPyArgument( pointer_name ) )
    return name,function



for name,function in [
    wrapPointerFunction( *args )
    for args in POINTER_FUNCTION_DATA
]:
    globals()[name] = function
try:
    del name, function
except NameError as err:
    pass

glVertexPointer = wrapper.wrapper( _simple.glVertexPointer ).setPyConverter(
    'pointer', arrayhelpers.AsArrayOfType( 'pointer', 'type' ),
).setStoreValues(
    arrayhelpers.storePointerType( 'pointer', _simple.GL_VERTEX_ARRAY_POINTER )
).setReturnValues(
    wrapper.returnPyArgument( 'pointer' )
)
glTexCoordPointer = wrapper.wrapper( _simple.glTexCoordPointer ).setPyConverter(
    'pointer', arrayhelpers.AsArrayOfType( 'pointer', 'type' ),
).setStoreValues(
    arrayhelpers.storePointerType( 'pointer', _simple.GL_TEXTURE_COORD_ARRAY_POINTER )
).setReturnValues(
    wrapper.returnPyArgument( 'pointer' )
)
glNormalPointer = wrapper.wrapper( _simple.glNormalPointer ).setPyConverter(
    'pointer', arrayhelpers.AsArrayOfType( 'pointer', 'type' ),
).setStoreValues(
    arrayhelpers.storePointerType( 'pointer', _simple.GL_NORMAL_ARRAY_POINTER )
).setReturnValues(
    wrapper.returnPyArgument( 'pointer' )
)
glIndexPointer = wrapper.wrapper( _simple.glIndexPointer ).setPyConverter(
    'pointer', arrayhelpers.AsArrayOfType( 'pointer', 'type' ),
).setStoreValues(
    arrayhelpers.storePointerType( 'pointer', _simple.GL_INDEX_ARRAY_POINTER )
).setReturnValues(
    wrapper.returnPyArgument( 'pointer' )
)
glEdgeFlagPointer = wrapper.wrapper( _simple.glEdgeFlagPointer ).setPyConverter(
    # XXX type is wrong!
    'pointer', arrayhelpers.AsArrayTyped( 'pointer', arraydatatype.GLushortArray ),
).setStoreValues(
    arrayhelpers.storePointerType( 'pointer', _simple.GL_EDGE_FLAG_ARRAY_POINTER )
).setReturnValues(
    wrapper.returnPyArgument( 'pointer' )
)
glColorPointer = wrapper.wrapper( _simple.glColorPointer ).setPyConverter(
    'pointer', arrayhelpers.AsArrayOfType( 'pointer', 'type' ),
).setStoreValues(
    arrayhelpers.storePointerType( 'pointer', _simple.GL_COLOR_ARRAY_POINTER )
).setReturnValues(
    wrapper.returnPyArgument( 'pointer' )
)
glInterleavedArrays = wrapper.wrapper( _simple.glInterleavedArrays ).setStoreValues(
    arrayhelpers.storePointerType( 'pointer', GL_INTERLEAVED_ARRAY_POINTER )
).setReturnValues(
    wrapper.returnPyArgument( 'pointer' )
)


glDrawElements = wrapper.wrapper( _simple.glDrawElements ).setPyConverter(
    'indices', arrayhelpers.AsArrayOfType( 'indices', 'type' ),
).setReturnValues(
    wrapper.returnPyArgument( 'indices' )
)

def glDrawElementsTyped( type, suffix ):
    arrayType = arraydatatype.GL_CONSTANT_TO_ARRAY_TYPE[ type ]
    function = wrapper.wrapper(
        _simple.glDrawElements
    ).setPyConverter('type').setCConverter(
        'type', type
    ).setPyConverter('count').setCConverter(
        'count', arrayhelpers.AsArrayTypedSize( 'indices', arrayType ),
    ).setPyConverter(
        'indices', arrayhelpers.AsArrayTyped( 'indices', arrayType ),
    ).setReturnValues(
        wrapper.returnPyArgument( 'indices' )
    )
    return function
for type,suffix in ((_simple.GL_UNSIGNED_BYTE,'ub'),(_simple.GL_UNSIGNED_INT,'ui'),(_simple.GL_UNSIGNED_SHORT,'us')):
    globals()['glDrawElements%(suffix)s'%globals()] = glDrawElementsTyped( type,suffix )
try:
    del type,suffix,glDrawElementsTyped
except NameError as err:
    pass

# create buffer of given size and return it for future reference
# keep a per-context weakref around to allow us to return the original
# array we returned IFF the user has kept a reference as well...
def glSelectBuffer( size, buffer = None ):
    """Create a selection buffer of the given size
    """
    if buffer is None:
        buffer = arraydatatype.GLuintArray.zeros( (size,) )
    _simple.glSelectBuffer( size, buffer )
    contextdata.setValue( _simple.GL_SELECTION_BUFFER_POINTER, buffer )
    return buffer
def glFeedbackBuffer( size, type, buffer = None ):
    """Create a selection buffer of the given size
    """
    if buffer is None:
        buffer = arraydatatype.GLfloatArray.zeros( (size,) )
    _simple.glFeedbackBuffer( size, type, buffer )
    contextdata.setValue( _simple.GL_FEEDBACK_BUFFER_POINTER, buffer )
    contextdata.setValue( "GL_FEEDBACK_BUFFER_TYPE", type )
    return buffer

def glRenderMode( newMode ):
    """Change to the given rendering mode

    If the current mode is GL_FEEDBACK or GL_SELECT, return
    the current buffer appropriate to the mode
    """
    # must get the current mode to determine operation...
    from OpenGL.GL import glGetIntegerv
    from OpenGL.GL import selection, feedback
    currentMode = glGetIntegerv( _simple.GL_RENDER_MODE )
    try:
        currentMode = currentMode[0]
    except (TypeError,ValueError,IndexError) as err:
        pass
    if currentMode in (_simple.GL_RENDER,0):
        # no array needs to be returned...
        return _simple.glRenderMode( newMode )
    result = _simple.glRenderMode( newMode )
    # result is now an integer telling us how many elements were copied...

    if result < 0:
        if currentMode == _simple.GL_SELECT:
            raise error.GLError(
                _simple.GL_STACK_OVERFLOW,
                "glSelectBuffer too small to hold selection results",
            )
        elif currentMode == _simple.GL_FEEDBACK:
            raise error.GLError(
                _simple.GL_STACK_OVERFLOW,
                "glFeedbackBuffer too small to hold selection results",
            )
        else:
            raise error.GLError(
                _simple.GL_STACK_OVERFLOW,
                "Unknown glRenderMode buffer (%s) too small to hold selection results"%(
                    currentMode,
                ),
            )
    # Okay, now that the easy cases are out of the way...
    #  Do we have a pre-stored pointer about which the user already knows?
    context = platform.GetCurrentContext()
    if context == 0:
        raise error.Error(
            """Returning from glRenderMode without a valid context!"""
        )
    arrayConstant, wrapperFunction = {
        _simple.GL_FEEDBACK: (_simple.GL_FEEDBACK_BUFFER_POINTER,feedback.parseFeedback),
        _simple.GL_SELECT: (_simple.GL_SELECTION_BUFFER_POINTER, selection.GLSelectRecord.fromArray),
    }[ currentMode ]
    current = contextdata.getValue( arrayConstant )
    # XXX check to see if it's the *same* array we set currently!
    if current is None:
        current = glGetPointerv( arrayConstant )
    # XXX now, can turn the array into the appropriate wrapper type...
    if wrapperFunction:
        current = wrapperFunction( current, result )
    return current

# XXX this belongs in the GL module, not here!
def glGetPointerv( constant ):
    """Retrieve a stored pointer constant"""
    # do we have a cached version of the pointer?
    # get the base pointer from the underlying operation
    vp = ctypes.voidp()
    _simple.glGetPointerv( constant, ctypes.byref(vp) )
    current = contextdata.getValue( constant )
    if current is not None:
        if arraydatatype.ArrayDatatype.dataPointer( current ) == vp.value:
            return current
    # XXX should be coercing to the proper type and converting to an array
    return vp
