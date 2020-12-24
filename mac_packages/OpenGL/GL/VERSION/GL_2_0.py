'''OpenGL extension VERSION.GL_2_0

This module customises the behaviour of the 
OpenGL.raw.GL.VERSION.GL_2_0 to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/VERSION/GL_2_0.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.VERSION.GL_2_0 import *
from OpenGL.raw.GL.VERSION.GL_2_0 import _EXTENSION_NAME

def glInitGl20VERSION():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDrawBuffers.bufs size not checked against n
glDrawBuffers=wrapper.wrapper(glDrawBuffers).setInputArraySize(
    'bufs', None
)
glGetActiveAttrib=wrapper.wrapper(glGetActiveAttrib).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'name',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'size',size=(1,),orPassIn=True
).setOutput(
    'type',size=(1,),orPassIn=True
)
glGetActiveUniform=wrapper.wrapper(glGetActiveUniform).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'name',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'size',size=(1,),orPassIn=True
).setOutput(
    'type',size=(1,),orPassIn=True
)
# glGetAttachedShaders.obj is OUTPUT without known output size
# INPUT glGetAttachedShaders.shaders size not checked against maxCount
glGetAttachedShaders=wrapper.wrapper(glGetAttachedShaders).setOutput(
    'count',size=(1,),orPassIn=True
).setInputArraySize(
    'shaders', None
)
glGetProgramiv=wrapper.wrapper(glGetProgramiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetProgramInfoLog=wrapper.wrapper(glGetProgramInfoLog).setOutput(
    'infoLog',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'length',size=(1,),orPassIn=True
)
glGetShaderiv=wrapper.wrapper(glGetShaderiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetShaderInfoLog=wrapper.wrapper(glGetShaderInfoLog).setOutput(
    'infoLog',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'length',size=(1,),orPassIn=True
)
glGetShaderSource=wrapper.wrapper(glGetShaderSource).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'source',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
# glGetUniformfv.params is OUTPUT without known output size
# glGetUniformiv.params is OUTPUT without known output size
glGetVertexAttribdv=wrapper.wrapper(glGetVertexAttribdv).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetVertexAttribfv=wrapper.wrapper(glGetVertexAttribfv).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetVertexAttribiv=wrapper.wrapper(glGetVertexAttribiv).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetVertexAttribPointerv=wrapper.wrapper(glGetVertexAttribPointerv).setOutput(
    'pointer',size=(1,),orPassIn=True
)
# INPUT glShaderSource.length size not checked against count
# INPUT glShaderSource.string size not checked against count
glShaderSource=wrapper.wrapper(glShaderSource).setInputArraySize(
    'length', None
).setInputArraySize(
    'string', None
)
# INPUT glUniform1fv.value size not checked against count
glUniform1fv=wrapper.wrapper(glUniform1fv).setInputArraySize(
    'value', None
)
# INPUT glUniform2fv.value size not checked against count*2
glUniform2fv=wrapper.wrapper(glUniform2fv).setInputArraySize(
    'value', None
)
# INPUT glUniform3fv.value size not checked against count*3
glUniform3fv=wrapper.wrapper(glUniform3fv).setInputArraySize(
    'value', None
)
# INPUT glUniform4fv.value size not checked against count*4
glUniform4fv=wrapper.wrapper(glUniform4fv).setInputArraySize(
    'value', None
)
# INPUT glUniform1iv.value size not checked against count
glUniform1iv=wrapper.wrapper(glUniform1iv).setInputArraySize(
    'value', None
)
# INPUT glUniform2iv.value size not checked against count*2
glUniform2iv=wrapper.wrapper(glUniform2iv).setInputArraySize(
    'value', None
)
# INPUT glUniform3iv.value size not checked against count*3
glUniform3iv=wrapper.wrapper(glUniform3iv).setInputArraySize(
    'value', None
)
# INPUT glUniform4iv.value size not checked against count*4
glUniform4iv=wrapper.wrapper(glUniform4iv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix2fv.value size not checked against count*4
glUniformMatrix2fv=wrapper.wrapper(glUniformMatrix2fv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix3fv.value size not checked against count*9
glUniformMatrix3fv=wrapper.wrapper(glUniformMatrix3fv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix4fv.value size not checked against count*16
glUniformMatrix4fv=wrapper.wrapper(glUniformMatrix4fv).setInputArraySize(
    'value', None
)
glVertexAttrib1dv=wrapper.wrapper(glVertexAttrib1dv).setInputArraySize(
    'v', 1
)
glVertexAttrib1fv=wrapper.wrapper(glVertexAttrib1fv).setInputArraySize(
    'v', 1
)
glVertexAttrib1sv=wrapper.wrapper(glVertexAttrib1sv).setInputArraySize(
    'v', 1
)
glVertexAttrib2dv=wrapper.wrapper(glVertexAttrib2dv).setInputArraySize(
    'v', 2
)
glVertexAttrib2fv=wrapper.wrapper(glVertexAttrib2fv).setInputArraySize(
    'v', 2
)
glVertexAttrib2sv=wrapper.wrapper(glVertexAttrib2sv).setInputArraySize(
    'v', 2
)
glVertexAttrib3dv=wrapper.wrapper(glVertexAttrib3dv).setInputArraySize(
    'v', 3
)
glVertexAttrib3fv=wrapper.wrapper(glVertexAttrib3fv).setInputArraySize(
    'v', 3
)
glVertexAttrib3sv=wrapper.wrapper(glVertexAttrib3sv).setInputArraySize(
    'v', 3
)
glVertexAttrib4Nbv=wrapper.wrapper(glVertexAttrib4Nbv).setInputArraySize(
    'v', 4
)
glVertexAttrib4Niv=wrapper.wrapper(glVertexAttrib4Niv).setInputArraySize(
    'v', 4
)
glVertexAttrib4Nsv=wrapper.wrapper(glVertexAttrib4Nsv).setInputArraySize(
    'v', 4
)
glVertexAttrib4Nubv=wrapper.wrapper(glVertexAttrib4Nubv).setInputArraySize(
    'v', 4
)
glVertexAttrib4Nuiv=wrapper.wrapper(glVertexAttrib4Nuiv).setInputArraySize(
    'v', 4
)
glVertexAttrib4Nusv=wrapper.wrapper(glVertexAttrib4Nusv).setInputArraySize(
    'v', 4
)
glVertexAttrib4bv=wrapper.wrapper(glVertexAttrib4bv).setInputArraySize(
    'v', 4
)
glVertexAttrib4dv=wrapper.wrapper(glVertexAttrib4dv).setInputArraySize(
    'v', 4
)
glVertexAttrib4fv=wrapper.wrapper(glVertexAttrib4fv).setInputArraySize(
    'v', 4
)
glVertexAttrib4iv=wrapper.wrapper(glVertexAttrib4iv).setInputArraySize(
    'v', 4
)
glVertexAttrib4sv=wrapper.wrapper(glVertexAttrib4sv).setInputArraySize(
    'v', 4
)
glVertexAttrib4ubv=wrapper.wrapper(glVertexAttrib4ubv).setInputArraySize(
    'v', 4
)
glVertexAttrib4uiv=wrapper.wrapper(glVertexAttrib4uiv).setInputArraySize(
    'v', 4
)
glVertexAttrib4usv=wrapper.wrapper(glVertexAttrib4usv).setInputArraySize(
    'v', 4
)
# INPUT glVertexAttribPointer.pointer size not checked against 'size,type,stride'
glVertexAttribPointer=wrapper.wrapper(glVertexAttribPointer).setInputArraySize(
    'pointer', None
)
### END AUTOGENERATED SECTION
import OpenGL
from OpenGL import _configflags
from OpenGL._bytes import bytes, _NULL_8_BYTE, as_8_bit
from OpenGL.raw.GL.ARB.shader_objects import GL_OBJECT_COMPILE_STATUS_ARB as GL_OBJECT_COMPILE_STATUS
from OpenGL.raw.GL.ARB.shader_objects import GL_OBJECT_LINK_STATUS_ARB as GL_OBJECT_LINK_STATUS
from OpenGL.raw.GL.ARB.shader_objects import GL_OBJECT_ACTIVE_UNIFORMS_ARB as GL_OBJECT_ACTIVE_UNIFORMS
from OpenGL.raw.GL.ARB.shader_objects import GL_OBJECT_ACTIVE_UNIFORM_MAX_LENGTH_ARB as GL_OBJECT_ACTIVE_UNIFORM_MAX_LENGTH
from OpenGL.lazywrapper import lazy as _lazy
from OpenGL.raw.GL import _errors

from OpenGL import converters, error, contextdata
from OpenGL.arrays.arraydatatype import ArrayDatatype, GLenumArray
GL_INFO_LOG_LENGTH = constant.Constant( 'GL_INFO_LOG_LENGTH', 0x8B84 )

glShaderSource = platform.createExtensionFunction(
    'glShaderSource', dll=platform.PLATFORM.GL,
    resultType=None,
    argTypes=(_types.GLhandle, _types.GLsizei, ctypes.POINTER(ctypes.c_char_p), arrays.GLintArray,),
    doc = 'glShaderSource( GLhandle(shaderObj),[bytes(string),...]) -> None',
    argNames = ('shaderObj', 'count', 'string', 'length',),
    extension = _EXTENSION_NAME,
)
conv = converters.StringLengths( name='string' )
glShaderSource = wrapper.wrapper(
    glShaderSource
).setPyConverter(
    'count' # number of strings
).setPyConverter(
    'length' # lengths of strings
).setPyConverter(
    'string', conv.stringArray
).setCResolver(
    'string', conv.stringArrayForC,
).setCConverter(
    'length', conv,
).setCConverter(
    'count', conv.totalCount,
)
try:
    del conv
except NameError as err:
    pass

@_lazy( glGetShaderiv )
def glGetShaderiv( baseOperation, shader, pname, status=None ):
    """Retrieve the integer parameter for the given shader

    shader -- shader ID to query
    pname -- parameter name
    status -- pointer to integer to receive status or None to
        return the parameter as an integer value

    returns
        integer if status parameter is None
        status if status parameter is not None
    """
    if status is None:
        status = arrays.GLintArray.zeros( (1,))
        status[0] = 1
        baseOperation(
            shader, pname, status
        )
        return status[0]
    else:
        baseOperation(
            shader, pname, status
        )
        return status

def _afterCheck( key ):
    """Generate an error-checking function for compilation operations"""
    if key == GL_OBJECT_COMPILE_STATUS:
        getter = glGetShaderiv
    else:
        getter = glGetProgramiv
    def GLSLCheckError(
        result,
        baseOperation=None,
        cArguments=None,
        *args
    ):
        result = _errors._error_checker.glCheckError( result, baseOperation, cArguments, *args )
        status = ctypes.c_int()
        getter( cArguments[0], key, ctypes.byref(status))
        status = status.value
        if not status:
            raise error.GLError(
                result = result,
                baseOperation = baseOperation,
                cArguments = cArguments,
                description= glGetShaderInfoLog( cArguments[0] )
            )
        return result
    return GLSLCheckError

if _configflags.ERROR_CHECKING:
    glCompileShader.errcheck = _afterCheck( GL_OBJECT_COMPILE_STATUS )
if _configflags.ERROR_CHECKING:
    glLinkProgram.errcheck = _afterCheck( GL_OBJECT_LINK_STATUS )
## Not sure why, but these give invalid operation :(
##if glValidateProgram and OpenGL.ERROR_CHECKING:
##	glValidateProgram.errcheck = _afterCheck( GL_OBJECT_VALIDATE_STATUS )

@_lazy( glGetShaderInfoLog )
def glGetShaderInfoLog( baseOperation, obj ):
    """Retrieve the shader's error messages as a Python string

    returns string which is '' if no message
    """
    length = int(glGetShaderiv(obj, GL_INFO_LOG_LENGTH))
    if length > 0:
        log = ctypes.create_string_buffer(length)
        baseOperation(obj, length, None, log)
        return log.value.strip(_NULL_8_BYTE) # null-termination
    return ''
@_lazy( glGetProgramInfoLog )
def glGetProgramInfoLog( baseOperation, obj ):
    """Retrieve the shader program's error messages as a Python string

    returns string which is '' if no message
    """
    length = int(glGetProgramiv(obj, GL_INFO_LOG_LENGTH))
    if length > 0:
        log = ctypes.create_string_buffer(length)
        baseOperation(obj, length, None, log)
        return log.value.strip(_NULL_8_BYTE) # null-termination
    return ''

@_lazy( glGetAttachedShaders )
def glGetAttachedShaders( baseOperation, obj ):
    """Retrieve the attached objects as an array of GLhandle instances"""
    length= glGetProgramiv( obj, GL_ATTACHED_SHADERS )
    if length > 0:
        storage = arrays.GLuintArray.zeros( (length,))
        baseOperation( obj, length, None, storage )
        return storage
    return arrays.GLuintArray.zeros( (0,))


@_lazy( glGetShaderSource )
def glGetShaderSource( baseOperation, obj ):
    """Retrieve the program/shader's source code as a Python string

    returns string which is '' if no source code
    """
    length = int(glGetShaderiv(obj, GL_SHADER_SOURCE_LENGTH))
    if length > 0:
        source = ctypes.create_string_buffer(length)
        baseOperation(obj, length, None, source)
        return source.value.strip(_NULL_8_BYTE) # null-termination
    return ''

@_lazy( glGetActiveAttrib )
def glGetActiveAttrib(baseOperation, program, index, bufSize=None,*args):
    """Retrieves information about the attribute variable.

    program -- specifies the program to be queried
    index -- index of the attribute to be queried 
    
    Following parameters are optional:
    
    bufSize -- determines the size of the buffer (limits number of bytes written),
               if not provided, will be GL_ACTIVE_ATTRIBUTE_MAX_LENGTH
    length -- pointer-to-GLsizei that will hold the resulting length of the name
    size -- pointer-to-GLint that will hold the size of the attribute
    type -- pointer-to-GLenum that will hold the type constant of the attribute
    name -- pointer-to-GLchar that will hold the (null-terminated) name string
    
    returns (bytes) name, (int)size, (enum)type
    """
    if bufSize is None:
        bufSize = int(glGetProgramiv( program, GL_ACTIVE_ATTRIBUTE_MAX_LENGTH))
    if bufSize <= 0:
        raise RuntimeError( 'Active attribute length reported', bufsize )
    name,size,type = baseOperation( program, index, bufSize, *args )[1:]
    if hasattr(name,'tostring'):
        name = name.tostring().rstrip(b'\000')
    elif hasattr(name,'value'):
        name = name.value
    return name,size,type

@_lazy( glGetActiveUniform )
def glGetActiveUniform(baseOperation,program, index,bufSize=None,*args):
    """Retrieve the name, size and type of the uniform of the index in the program
    
    program -- specifies the program to be queried
    index -- index of the uniform to be queried 
    
    Following parameters are optional:
    
    bufSize -- determines the size of the buffer (limits number of bytes written),
               if not provided, will be GL_OBJECT_ACTIVE_UNIFORM_MAX_LENGTH
    length -- pointer-to-GLsizei that will hold the resulting length of the name
    size -- pointer-to-GLint that will hold the size of the attribute
    type -- pointer-to-GLenum that will hold the type constant of the attribute
    name -- pointer-to-GLchar that will hold the (null-terminated) name string
    
    returns (bytes) name, (int)size, (enum)type
    """
    max_index = int(glGetProgramiv( program, GL_ACTIVE_UNIFORMS ))
    if bufSize is None:
        bufSize = int(glGetProgramiv( program, GL_ACTIVE_UNIFORM_MAX_LENGTH))
    if index < max_index and index >= 0:
        length,name,size,type = baseOperation( program, index, bufSize, *args )
        if hasattr(name,'tostring'):
            name = name.tostring().rstrip(b'\000')
        elif hasattr(name,'value'):
            name = name.value
        return name,size,type
    raise IndexError( 'Index %s out of range 0 to %i' % (index, max_index - 1, ) )

@_lazy( glGetUniformLocation )
def glGetUniformLocation( baseOperation, program, name ):
    """Check that name is a string with a null byte at the end of it"""
    if not name:
        raise ValueError( """Non-null name required""" )
    name = as_8_bit( name )
    if name[-1] != _NULL_8_BYTE:
        name = name + _NULL_8_BYTE
    return baseOperation( program, name )
@_lazy( glGetAttribLocation )
def glGetAttribLocation( baseOperation, program, name ):
    """Check that name is a string with a null byte at the end of it"""
    if not name:
        raise ValueError( """Non-null name required""" )
    
    name = as_8_bit( name )
    if name[-1] != _NULL_8_BYTE:
        name = name + _NULL_8_BYTE
    return baseOperation( program, name )

@_lazy( glVertexAttribPointer )
def glVertexAttribPointer(
    baseOperation, index, size, type,
    normalized, stride, pointer,
):
    """Set an attribute pointer for a given shader (index)

    index -- the index of the generic vertex to bind, see
        glGetAttribLocation for retrieval of the value,
        note that index is a global variable, not per-shader
    size -- number of basic elements per record, 1,2,3, or 4
    type -- enum constant for data-type
    normalized -- whether to perform int to float
        normalization on integer-type values
    stride -- stride in machine units (bytes) between
        consecutive records, normally used to create
        "interleaved" arrays
    pointer -- data-pointer which provides the data-values,
        normally a vertex-buffer-object or offset into the
        same.

    This implementation stores a copy of the data-pointer
    in the contextdata structure in order to prevent null-
    reference errors in the renderer.
    """
    array = ArrayDatatype.asArray( pointer, type )
    key = ('vertex-attrib',index)
    contextdata.setValue( key, array )
    return baseOperation(
        index, size, type,
        normalized, stride,
        ArrayDatatype.voidDataPointer( array )
    )

@_lazy( glDrawBuffers )
def glDrawBuffers( baseOperation, n=None, bufs=None ):
    """glDrawBuffers( bufs ) -> bufs

    Wrapper will calculate n from dims of bufs if only
    one argument is provided...
    """
    if bufs is None:
        bufs = n
        n = None
    bufs = arrays.GLenumArray.asArray( bufs )
    if n is None:
        n = arrays.GLenumArray.arraySize( bufs )
    return baseOperation( n,bufs )
