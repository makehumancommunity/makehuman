"""Image-handling routines

### Unresolved:

    Following methods are not yet resolved due to my not being sure how the
    function should be wrapped:

        glCompressedTexImage3D
        glCompressedTexImage2D
        glCompressedTexImage1D
        glCompressedTexSubImage3D
        glCompressedTexSubImage2D
        glCompressedTexSubImage1D
"""
from OpenGL.raw.GL.VERSION import GL_1_1,GL_1_2, GL_3_0
from OpenGL import images, arrays, wrapper
from OpenGL.arrays import arraydatatype
from OpenGL._bytes import bytes,integer_types
from OpenGL.raw.GL import _types
import ctypes

def asInt( value ):
    if isinstance( value, float ):
        return int(round(value,0))
    return value

## update the image tables with standard image types...
images.COMPONENT_COUNTS.update( {
    GL_1_1.GL_BITMAP : 1, # must be GL_UNSIGNED_BYTE

    GL_1_1.GL_RED : 1,
    GL_1_1.GL_GREEN : 1,
    GL_1_1.GL_BLUE : 1,
    GL_1_1.GL_ALPHA : 1,
    GL_3_0.GL_RED_INTEGER : 1,
    GL_3_0.GL_GREEN_INTEGER : 1,
    GL_3_0.GL_BLUE_INTEGER : 1,
    GL_3_0.GL_ALPHA_INTEGER : 1,
    GL_1_1.GL_LUMINANCE : 1,
    GL_1_1.GL_LUMINANCE_ALPHA : 2,
    GL_1_1.GL_COLOR_INDEX : 1,
    GL_1_1.GL_STENCIL_INDEX : 1,
    GL_1_1.GL_DEPTH_COMPONENT : 1,

    GL_1_1.GL_RGB : 3,
    GL_1_2.GL_BGR : 3,
    GL_3_0.GL_RGB16F : 3,
    GL_3_0.GL_RGB16I : 3,
    GL_3_0.GL_RGB16UI : 3,
    GL_3_0.GL_RGB32F : 3,
    GL_3_0.GL_RGB32I : 3,
    GL_3_0.GL_RGB32UI : 3,
    GL_3_0.GL_RGB8I : 3,
    GL_3_0.GL_RGB8UI : 3,
    GL_3_0.GL_RGB9_E5 : 3,
    GL_3_0.GL_RGB_INTEGER : 3,

    GL_1_1.GL_RGBA : 4,
    GL_1_2.GL_BGRA : 4,
    GL_3_0.GL_RGBA16F : 4,
    GL_3_0.GL_RGBA16I : 4,
    GL_3_0.GL_RGBA16UI : 4,
    GL_3_0.GL_RGBA32F : 4,
    GL_3_0.GL_RGBA32I : 4,
    GL_3_0.GL_RGBA32UI : 4,
    GL_3_0.GL_RGBA8I : 4,
    GL_3_0.GL_RGBA8UI : 4,
    GL_3_0.GL_RGBA_INTEGER : 4,
} )

images.TYPE_TO_ARRAYTYPE.update( {
    GL_1_2.GL_UNSIGNED_BYTE_3_3_2 : GL_1_1.GL_UNSIGNED_BYTE,
    GL_1_2.GL_UNSIGNED_BYTE_2_3_3_REV : GL_1_1.GL_UNSIGNED_BYTE,
    GL_1_2.GL_UNSIGNED_SHORT_4_4_4_4 : GL_1_1.GL_UNSIGNED_SHORT,
    GL_1_2.GL_UNSIGNED_SHORT_4_4_4_4_REV : GL_1_1.GL_UNSIGNED_SHORT,
    GL_1_2.GL_UNSIGNED_SHORT_5_5_5_1 : GL_1_1.GL_UNSIGNED_SHORT,
    GL_1_2.GL_UNSIGNED_SHORT_1_5_5_5_REV : GL_1_1.GL_UNSIGNED_SHORT,
    GL_1_2.GL_UNSIGNED_SHORT_5_6_5 : GL_1_1.GL_UNSIGNED_SHORT,
    GL_1_2.GL_UNSIGNED_SHORT_5_6_5_REV : GL_1_1.GL_UNSIGNED_SHORT,
    GL_1_2.GL_UNSIGNED_INT_8_8_8_8 : GL_1_1.GL_UNSIGNED_INT,
    GL_1_2.GL_UNSIGNED_INT_8_8_8_8_REV : GL_1_1.GL_UNSIGNED_INT,
    GL_1_2.GL_UNSIGNED_INT_10_10_10_2 : GL_1_1.GL_UNSIGNED_INT,
    GL_1_2.GL_UNSIGNED_INT_2_10_10_10_REV : GL_1_1.GL_UNSIGNED_INT,
    GL_1_1.GL_UNSIGNED_BYTE : GL_1_1.GL_UNSIGNED_BYTE,
    GL_1_1.GL_BYTE: GL_1_1.GL_BYTE,
    GL_1_1.GL_UNSIGNED_SHORT : GL_1_1.GL_UNSIGNED_SHORT,
    GL_1_1.GL_SHORT :  GL_1_1.GL_SHORT,
    GL_1_1.GL_UNSIGNED_INT : GL_1_1.GL_UNSIGNED_INT,
    GL_1_1.GL_INT : GL_1_1.GL_INT,
    GL_1_1.GL_FLOAT : GL_1_1.GL_FLOAT,
    GL_1_1.GL_DOUBLE : GL_1_1.GL_DOUBLE,
    GL_1_1.GL_BITMAP : GL_1_1.GL_UNSIGNED_BYTE,
} )
images.TIGHT_PACK_FORMATS.update({
    GL_1_2.GL_UNSIGNED_BYTE_3_3_2 : 3,
    GL_1_2.GL_UNSIGNED_BYTE_2_3_3_REV : 3,
    GL_1_2.GL_UNSIGNED_SHORT_4_4_4_4 : 4,
    GL_1_2.GL_UNSIGNED_SHORT_4_4_4_4_REV : 4,
    GL_1_2.GL_UNSIGNED_SHORT_5_5_5_1 : 4,
    GL_1_2.GL_UNSIGNED_SHORT_1_5_5_5_REV : 4,
    GL_1_2.GL_UNSIGNED_SHORT_5_6_5 : 3,
    GL_1_2.GL_UNSIGNED_SHORT_5_6_5_REV : 3,
    GL_1_2.GL_UNSIGNED_INT_8_8_8_8 : 4,
    GL_1_2.GL_UNSIGNED_INT_8_8_8_8_REV : 4,
    GL_1_2.GL_UNSIGNED_INT_10_10_10_2 : 4,
    GL_1_2.GL_UNSIGNED_INT_2_10_10_10_REV : 4,
    GL_1_1.GL_BITMAP: 8, # single bits, 8 of them...
})

images.RANK_PACKINGS.update( {
    4: [
        # Note the sgis parameters are skipped here unless you import 
        # the sgis texture4D extension...
        (GL_1_1.glPixelStorei,GL_1_1.GL_PACK_ALIGNMENT, 1),
    ],
    3: [
        (GL_1_1.glPixelStorei,GL_1_2.GL_PACK_SKIP_IMAGES, 0),
        (GL_1_1.glPixelStorei,GL_1_2.GL_PACK_IMAGE_HEIGHT, 0),
        (GL_1_1.glPixelStorei,GL_1_1.GL_PACK_ALIGNMENT, 1),
    ],
    2: [
        (GL_1_1.glPixelStorei,GL_1_1.GL_PACK_ROW_LENGTH, 0),
        (GL_1_1.glPixelStorei,GL_1_1.GL_PACK_SKIP_ROWS, 0),
        (GL_1_1.glPixelStorei,GL_1_1.GL_PACK_ALIGNMENT, 1),
    ],
    1: [
        (GL_1_1.glPixelStorei,GL_1_1.GL_PACK_SKIP_PIXELS, 0),
        (GL_1_1.glPixelStorei,GL_1_1.GL_PACK_ALIGNMENT, 1),
    ],
} )


__all__ = (
    'glReadPixels',
    'glReadPixelsb',
    'glReadPixelsd',
    'glReadPixelsf',
    'glReadPixelsi',
    'glReadPixelss',
    'glReadPixelsub',
    'glReadPixelsui',
    'glReadPixelsus',

    'glGetTexImage',

    'glDrawPixels',
    'glDrawPixelsb',
    'glDrawPixelsf',
    'glDrawPixelsi',
    'glDrawPixelss',
    'glDrawPixelsub',
    'glDrawPixelsui',
    'glDrawPixelsus',


    'glTexSubImage2D',
    'glTexSubImage1D',
    #'glTexSubImage3D',

    'glTexImage1D',
    'glTexImage2D',
    #'glTexImage3D',

    'glGetTexImageb',
    'glGetTexImaged',
    'glGetTexImagef',
    'glGetTexImagei',
    'glGetTexImages',
    'glGetTexImageub',
    'glGetTexImageui',
    'glGetTexImageus',
    'glTexImage1Db',
    'glTexImage2Db',
    #'glTexImage3Db',
    'glTexSubImage1Db',
    'glTexSubImage2Db',
    #'glTexSubImage3Db',
    'glTexImage1Df',
    'glTexImage2Df',
    #'glTexImage3Df',
    'glTexSubImage1Df',
    'glTexSubImage2Df',
    #'glTexSubImage3Df',
    'glTexImage1Di',
    'glTexImage2Di',
    #'glTexImage3Di',
    'glTexSubImage1Di',
    'glTexSubImage2Di',
    #'glTexSubImage3Di',
    'glTexImage1Ds',
    'glTexImage2Ds',
    #'glTexImage3Ds',
    'glTexSubImage1Ds',
    'glTexSubImage2Ds',
    #'glTexSubImage3Ds',
    'glTexImage1Dub',
    'glTexImage2Dub',
    #'glTexImage3Dub',
    'glTexSubImage1Dub',
    'glTexSubImage2Dub',
    #'glTexSubImage3Dub',
    'glTexImage1Dui',
    'glTexImage2Dui',
    #'glTexImage3Dui',
    'glTexSubImage1Dui',
    'glTexSubImage2Dui',
    #'glTexSubImage3Dui',
    'glTexImage1Dus',
    'glTexImage2Dus',
    #'glTexImage3Dus',
    'glTexSubImage1Dus',
    'glTexSubImage2Dus',
    #'glTexSubImage3Dus',

    #'glColorTable',
    #'glGetColorTable',
    #'glColorSubTable',

    #'glConvolutionFilter1D',
    #'glConvolutionFilter2D',
    #'glGetConvolutionFilter',
    #'glSeparableFilter2D',
    #'glGetSeparableFilter',

    #'glGetMinmax',
)

def _get_texture_level_dims(target,level):
    """Retrieve texture dims for given level and target"""
    dims = []
    dim = _types.GLuint()
    GL_1_1.glGetTexLevelParameteriv( target, level, GL_1_1.GL_TEXTURE_WIDTH, dim )
    dims = [dim.value]
    if target != GL_1_1.GL_TEXTURE_1D:
        GL_1_1.glGetTexLevelParameteriv( target, level, GL_1_1.GL_TEXTURE_HEIGHT, dim )
        dims.append( dim.value )
        if target != GL_1_1.GL_TEXTURE_2D:
            GL_1_1.glGetTexLevelParameteriv( target, level, GL_1_1.GL_TEXTURE_DEPTH, dim )
            dims.append( dim.value )
    return dims

for suffix,type in [
    ('b',GL_1_1.GL_BYTE),
    ('d',GL_1_1.GL_DOUBLE),
    ('f',GL_1_1.GL_FLOAT),
    ('i',GL_1_1.GL_INT),
    ('s',GL_1_1.GL_SHORT),
    ('ub',GL_1_1.GL_UNSIGNED_BYTE),
    ('ui',GL_1_1.GL_UNSIGNED_INT),
    ('us',GL_1_1.GL_UNSIGNED_SHORT),
]:
    def glReadPixels( x,y,width,height,format,type=type, array=None, outputType=bytes ):
        """Read specified pixels from the current display buffer

        This typed version returns data in your specified default
        array data-type format, or in the passed array, which will
        be converted to the array-type required by the format.
        """
        x,y,width,height = asInt(x),asInt(y),asInt(width),asInt(height)
        arrayType = arrays.GL_CONSTANT_TO_ARRAY_TYPE[ images.TYPE_TO_ARRAYTYPE.get(type,type) ]
        
        if array is None:
            array = imageData = images.SetupPixelRead( format, (width,height), type )
            owned = True
        else:
            if isinstance( array, integer_types):
                imageData = ctypes.c_void_p( array )
            else:
                array = arrayType.asArray( array )
                imageData = arrayType.voidDataPointer( array )
            owned = False
        GL_1_1.glReadPixels(
            x,y,
            width, height,
            format,type,
            imageData
        )
        if owned and outputType is bytes:
            return images.returnFormat( array, type )
        else:
            return array
    globals()["glReadPixels%s"%(suffix,)] = glReadPixels
    def glGetTexImage( target, level,format,type=type, array=None, outputType=bytes ):
        """Get a texture-level as an image
        
        target -- enum constant for the texture engine to be read
        level -- the mip-map level to read
        format -- image format to read out the data
        type -- data-type into which to read the data
        array -- optional array/offset into which to store the value

        outputType -- default (bytes) provides string output of the
            results iff OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING is True
            and type == GL_UNSIGNED_BYTE.  Any other value will cause
            output in the default array output format.

        returns the pixel data array in the format defined by the
        format, type and outputType
        """
        arrayType = arrays.GL_CONSTANT_TO_ARRAY_TYPE[ images.TYPE_TO_ARRAYTYPE.get(type,type) ]
        if array is None:
            dims = _get_texture_level_dims(target,level)
            array = imageData = images.SetupPixelRead( format, tuple(dims), type )
            owned = True
        else:
            if isinstance( array, integer_types):
                imageData = ctypes.c_void_p( array )
            else:
                array = arrayType.asArray( array )
                imageData = arrayType.voidDataPointer( array )
            owned = False
        GL_1_1.glGetTexImage(
            target, level, format, type, imageData
        )
        if owned and outputType is bytes:
            return images.returnFormat( array, type )
        else:
            return array
    globals()["glGetTexImage%s"%(suffix,)] = glGetTexImage
##	def glGetTexSubImage( target, level,format,type ):
##		"""Get a texture-level as an image"""
##		dims = [GL_1_1.glGetTexLevelParameteriv( target, level, GL_1_1.GL_TEXTURE_WIDTH )]
##		if target != GL_1_1.GL_TEXTURE_1D:
##			dims.append( GL_1_1.glGetTexLevelParameteriv( target, level, GL_1_1.GL_TEXTURE_HEIGHT ) )
##			if target != GL_1_1.GL_TEXTURE_2D:
##				dims.append( GL_1_1.glGetTexLevelParameteriv( target, level, GL_1_2.GL_TEXTURE_DEPTH ) )
##		array = images.SetupPixelRead( format, tuple(dims), type )
##		arrayType = arrays.GL_CONSTANT_TO_ARRAY_TYPE[ images.TYPE_TO_ARRAYTYPE.get(type,type) ]
##		GL_1_1.glGetTexImage(
##			target, level, format, type, ctypes.c_void_p( arrayType.dataPointer(array))
##		)
##		return array
##	"%s = glGetTexImage"%(suffix)
    try:
        del suffix,type
    except NameError as err:
        pass
# Now the real glReadPixels...
def glReadPixels( x,y,width,height,format,type, array=None, outputType=bytes ):
    """Read specified pixels from the current display buffer

    x,y,width,height -- location and dimensions of the image to read
        from the buffer
    format -- pixel format for the resulting data
    type -- data-format for the resulting data
    array -- optional array/offset into which to store the value
    outputType -- default (bytes) provides string output of the
        results iff OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING is True
        and type == GL_UNSIGNED_BYTE.  Any other value will cause
        output in the default array output format.

    returns the pixel data array in the format defined by the
    format, type and outputType
    """
    x,y,width,height = asInt(x),asInt(y),asInt(width),asInt(height)

    arrayType = arrays.GL_CONSTANT_TO_ARRAY_TYPE[ images.TYPE_TO_ARRAYTYPE.get(type,type) ]
    if array is None:
        array = imageData = images.SetupPixelRead( format, (width,height), type )
        owned = True
    else:
        if isinstance( array, integer_types):
            imageData = ctypes.c_void_p( array )
        else:
            array = arrayType.asArray( array )
            imageData = arrayType.voidDataPointer( array )
        owned = False

    GL_1_1.glReadPixels(
        x,y,width,height,
        format,type,
        imageData
    )
    if owned and outputType is bytes:
        return images.returnFormat( array, type )
    else:
        return array

def glGetTexImage( target, level,format,type, array=None, outputType=bytes ):
    """Get a texture-level as an image

    target -- enum constant for the texture engine to be read
    level -- the mip-map level to read
    format -- image format to read out the data
    type -- data-type into which to read the data
    array -- optional array/offset into which to store the value

    outputType -- default (bytes) provides string output of the
        results iff OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING is True
        and type == GL_UNSIGNED_BYTE.  Any other value will cause
        output in the default array output format.

    returns the pixel data array in the format defined by the
    format, type and outputType
    """
    arrayType = arrays.GL_CONSTANT_TO_ARRAY_TYPE[ images.TYPE_TO_ARRAYTYPE.get(type,type) ]
    if array is None:
        dims = _get_texture_level_dims(target,level)
        array = imageData = images.SetupPixelRead( format, tuple(dims), type )
    else:
        if isinstance( array, integer_types):
            imageData = ctypes.c_void_p( array )
        else:
            array = arrayType.asArray( array )
            imageData = arrayType.voidDataPointer( array )
    GL_1_1.glGetTexImage(
        target, level, format, type, imageData
    )
    if outputType is bytes:
        return images.returnFormat( array, type )
    else:
        return array


INT_DIMENSION_NAMES = [
    'width','height','depth','x','y','z',
    'xoffset','yoffset','zoffset',
    'start', 'count',
]
def asWrapper( value ):
    if not isinstance( value, wrapper.Wrapper ):
        return wrapper.wrapper( value )
    return value

def asIntConverter( value, *args ):
    if isinstance( value, float ):
        return int(round(value,0))
    return value

def setDimensionsAsInts( baseOperation ):
    """Set arguments with names in INT_DIMENSION_NAMES to asInt processing"""
    baseOperation = asWrapper( baseOperation )
    argNames = getattr( baseOperation, 'pyConverterNames', baseOperation.argNames )
    for i,argName in enumerate(argNames):
        if argName in INT_DIMENSION_NAMES:
            baseOperation.setPyConverter( argName, asIntConverter )
    return baseOperation



class ImageInputConverter( object ):
    def __init__( self, rank, pixelsName=None, typeName='type' ):
        self.rank = rank
        self.typeName = typeName
        self.pixelsName = pixelsName
    def finalise( self, wrapper ):
        """Get our pixel index from the wrapper"""
        self.typeIndex = wrapper.pyArgIndex( self.typeName )
        self.pixelsIndex = wrapper.pyArgIndex( self.pixelsName )
    def __call__( self, arg, baseOperation, pyArgs ):
        """pyConverter for the pixels argument"""
        images.setupDefaultTransferMode()
        images.rankPacking( self.rank )
        type = pyArgs[ self.typeIndex ]
        arrayType = arrays.GL_CONSTANT_TO_ARRAY_TYPE[ images.TYPE_TO_ARRAYTYPE[ type ] ]
        return arrayType.asArray( arg )
#	def cResolver( self, array ):
#		return array
#		return ctypes.c_void_p( arrays.ArrayDatatype.dataPointer( array ) )

class TypedImageInputConverter( ImageInputConverter ):
    def __init__( self, rank, pixelsName, arrayType, typeName=None ):
        self.rank = rank
        self.arrayType = arrayType
        self.pixelsName = pixelsName
        self.typeName = typeName
    def __call__( self, arg, baseOperation, pyArgs ):
        """The pyConverter for the pixels"""
        images.setupDefaultTransferMode()
        images.rankPacking( self.rank )
        return self.arrayType.asArray( arg )
    def finalise( self, wrapper ):
        """Get our pixel index from the wrapper"""
        self.pixelsIndex = wrapper.pyArgIndex( self.pixelsName )
    def width( self, pyArgs, index, wrappedOperation ):
        """Extract the width from the pixels argument"""
        return self.arrayType.dimensions( pyArgs[self.pixelsIndex] )[0]
    def height( self, pyArgs, index, wrappedOperation ):
        """Extract the height from the pixels argument"""
        return self.arrayType.dimensions( pyArgs[self.pixelsIndex] )[1]
    def depth( self, pyArgs, index, wrappedOperation ):
        """Extract the depth from the pixels argument"""
        return self.arrayType.dimensions( pyArgs[self.pixelsIndex] )[2]
    def type( self, pyArgs, index, wrappedOperation ):
        """Provide the item-type argument from our stored value

        This is used for pre-bound processing where we want to provide
        the type by implication...
        """
        return self.typeName

class CompressedImageConverter( object ):
    def finalise( self, wrapper ):
        """Get our pixel index from the wrapper"""
        self.dataIndex = wrapper.pyArgIndex( 'data' )
    def __call__( self, pyArgs, index, wrappedOperation ):
        """Create a data-size measurement for our image"""
        arg = pyArgs[ self.dataIndex ]
        return arraydatatype.ArrayDatatype.arrayByteCount(arg)



DIMENSION_NAMES = (
    'width','height','depth'
)
PIXEL_NAMES = (
    'pixels', 'row', 'column',
)
DATA_SIZE_NAMES = (
    'imageSize',
)

def setImageInput(
    baseOperation, arrayType=None, dimNames=DIMENSION_NAMES,
    pixelName="pixels", typeName=None
):
    """Determine how to convert "pixels" into an image-compatible argument"""
    baseOperation = asWrapper( baseOperation )
    # rank is the count of width,height,depth arguments...
    rank = len([
        # rank is the number of dims we want, not the number we give...
        argName for argName in baseOperation.argNames
        if argName in dimNames
    ]) + 1
    if arrayType:
        converter = TypedImageInputConverter( rank, pixelName, arrayType, typeName=typeName )
        for i,argName in enumerate(baseOperation.argNames):
            if argName in dimNames:
                baseOperation.setPyConverter( argName )
                baseOperation.setCConverter( argName, getattr(converter,argName) )
            elif argName == 'type' and typeName is not None:
                baseOperation.setPyConverter( argName )
                baseOperation.setCConverter( argName, converter.type )
    else:
        converter = ImageInputConverter( rank, pixelsName=pixelName, typeName=typeName or 'type' )
    for argName in baseOperation.argNames:
        if argName in DATA_SIZE_NAMES:
            baseOperation.setPyConverter( argName )
            baseOperation.setCConverter( argName, converter.imageDataSize )
    baseOperation.setPyConverter(
        pixelName, converter,
    )
#	baseOperation.setCResolver(
#		pixelName, converter.cResolver
#	)
    return baseOperation

glDrawPixels = setDimensionsAsInts(
    setImageInput(
        GL_1_1.glDrawPixels
    )
)
glTexSubImage2D = setDimensionsAsInts(
    setImageInput(
        GL_1_1.glTexSubImage2D
    )
)
glTexSubImage1D = setDimensionsAsInts(
    setImageInput(
        GL_1_1.glTexSubImage1D
    )
)
glTexImage2D = setDimensionsAsInts(
    setImageInput(
        GL_1_1.glTexImage2D
    )
)
glTexImage1D = setDimensionsAsInts(
    setImageInput(
        GL_1_1.glTexImage1D
    )
)

def typedImageFunction( suffix, arrayConstant,  baseFunction ):
    """Produce a typed version of the given image function"""
    functionName = baseFunction.__name__
    functionName = '%(functionName)s%(suffix)s'%locals()
    arrayType = arrays.GL_CONSTANT_TO_ARRAY_TYPE[ arrayConstant ]
    function = setDimensionsAsInts(
        setImageInput(
            baseFunction,
            arrayType,
            typeName = arrayConstant,
        )
    )
    return functionName, function

def _setDataSize( baseFunction, argument='imageSize' ):
    """Set the data-size value to come from the data field"""
    converter = CompressedImageConverter()
    return asWrapper( baseFunction ).setPyConverter(
        argument
    ).setCConverter( argument, converter )

def compressedImageFunction( baseFunction ):
    """Set the imageSize and dimensions-as-ints converters for baseFunction"""
    return setDimensionsAsInts(
        _setDataSize(
            baseFunction, argument='imageSize'
        )
    )

for suffix,arrayConstant in [
    ('b', GL_1_1.GL_BYTE),
    ('f', GL_1_1.GL_FLOAT),
    ('i', GL_1_1.GL_INT),
    ('s', GL_1_1.GL_SHORT),
    ('ub', GL_1_1.GL_UNSIGNED_BYTE),
    ('ui', GL_1_1.GL_UNSIGNED_INT),
    ('us', GL_1_1.GL_UNSIGNED_SHORT),
]:
    for functionName in (
        'glTexImage1D','glTexImage2D',
        'glTexSubImage1D','glTexSubImage2D',
        'glDrawPixels',
        #'glTexSubImage3D','glTexImage3D', # extension/1.2 standard
    ):
        functionName, function = typedImageFunction(
            suffix, arrayConstant, getattr(GL_1_1,functionName),
        )
        globals()[functionName] = function
        try:
            del function, functionName
        except NameError as err:
            pass
    try:
        del suffix,arrayConstant
    except NameError as err:
        pass
