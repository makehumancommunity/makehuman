'''OpenGL extension ARB.shader_objects

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.shader_objects to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension adds API calls that are necessary to manage shader
	objects and program objects as defined in the OpenGL 2.0 white papers by
	3Dlabs.
	
	The generation of an executable that runs on one of OpenGL's
	programmable units is modeled to that of developing a typical C/C++
	application. There are one or more source files, each of which are
	stored by OpenGL in a shader object. Each shader object (source file)
	needs to be compiled and attached to a program object. Once all shader
	objects are compiled successfully, the program object needs to be linked
	to produce an executable. This executable is part of the program object,
	and can now be loaded onto the programmable units to make it part of the
	current OpenGL state. Both the compile and link stages generate a text
	string that can be queried to get more information. This information
	could be, but is not limited to, compile errors, link errors,
	optimization hints, etc. Values for uniform variables, declared in a
	shader, can be set by the application and used to control a shader's
	behavior.
	
	This extension defines functions for creating shader objects and program
	objects, for compiling shader objects, for linking program objects, for
	attaching shader objects to program objects, and for using a program
	object as part of current state. Functions to load uniform values are
	also defined. Some house keeping functions, like deleting an object and
	querying object state, are also provided.
	
	Although this extension defines the API for creating shader objects, it
	does not define any specific types of shader objects. It is assumed that
	this extension will be implemented along with at least one such
	additional extension for creating a specific type of OpenGL 2.0 shader
	(e.g., the ARB_fragment_shader extension or the ARB_vertex_shader
	extension).

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/shader_objects.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.shader_objects import *
from OpenGL.raw.GL.ARB.shader_objects import _EXTENSION_NAME

def glInitShaderObjectsARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glShaderSourceARB.length size not checked against count
# INPUT glShaderSourceARB.string size not checked against count
glShaderSourceARB=wrapper.wrapper(glShaderSourceARB).setInputArraySize(
    'length', None
).setInputArraySize(
    'string', None
)
# INPUT glUniform1fvARB.value size not checked against count
glUniform1fvARB=wrapper.wrapper(glUniform1fvARB).setInputArraySize(
    'value', None
)
# INPUT glUniform2fvARB.value size not checked against count*2
glUniform2fvARB=wrapper.wrapper(glUniform2fvARB).setInputArraySize(
    'value', None
)
# INPUT glUniform3fvARB.value size not checked against count*3
glUniform3fvARB=wrapper.wrapper(glUniform3fvARB).setInputArraySize(
    'value', None
)
# INPUT glUniform4fvARB.value size not checked against count*4
glUniform4fvARB=wrapper.wrapper(glUniform4fvARB).setInputArraySize(
    'value', None
)
# INPUT glUniform1ivARB.value size not checked against count
glUniform1ivARB=wrapper.wrapper(glUniform1ivARB).setInputArraySize(
    'value', None
)
# INPUT glUniform2ivARB.value size not checked against count*2
glUniform2ivARB=wrapper.wrapper(glUniform2ivARB).setInputArraySize(
    'value', None
)
# INPUT glUniform3ivARB.value size not checked against count*3
glUniform3ivARB=wrapper.wrapper(glUniform3ivARB).setInputArraySize(
    'value', None
)
# INPUT glUniform4ivARB.value size not checked against count*4
glUniform4ivARB=wrapper.wrapper(glUniform4ivARB).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix2fvARB.value size not checked against count*4
glUniformMatrix2fvARB=wrapper.wrapper(glUniformMatrix2fvARB).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix3fvARB.value size not checked against count*9
glUniformMatrix3fvARB=wrapper.wrapper(glUniformMatrix3fvARB).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix4fvARB.value size not checked against count*16
glUniformMatrix4fvARB=wrapper.wrapper(glUniformMatrix4fvARB).setInputArraySize(
    'value', None
)
glGetObjectParameterfvARB=wrapper.wrapper(glGetObjectParameterfvARB).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetObjectParameterivARB=wrapper.wrapper(glGetObjectParameterivARB).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetInfoLogARB=wrapper.wrapper(glGetInfoLogARB).setOutput(
    'infoLog',size=lambda x:(x,),pnameArg='maxLength',orPassIn=True
).setOutput(
    'length',size=(1,),orPassIn=True
)
glGetAttachedObjectsARB=wrapper.wrapper(glGetAttachedObjectsARB).setOutput(
    'count',size=(1,),orPassIn=True
).setOutput(
    'obj',size=lambda x:(x,),pnameArg='maxCount',orPassIn=True
)
glGetActiveUniformARB=wrapper.wrapper(glGetActiveUniformARB).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'name',size=lambda x:(x,),pnameArg='maxLength',orPassIn=True
).setOutput(
    'size',size=(1,),orPassIn=True
).setOutput(
    'type',size=(1,),orPassIn=True
)
# OUTPUT glGetUniformfvARB.params COMPSIZE(programObj, location) 
# OUTPUT glGetUniformivARB.params COMPSIZE(programObj, location) 
glGetShaderSourceARB=wrapper.wrapper(glGetShaderSourceARB).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'source',size=lambda x:(x,),pnameArg='maxLength',orPassIn=True
)
### END AUTOGENERATED SECTION
import OpenGL
from OpenGL._bytes import bytes, _NULL_8_BYTE, as_8_bit
from OpenGL.raw.GL import _errors
from OpenGL.lazywrapper import lazy as _lazy
from OpenGL import converters, error
GL_INFO_LOG_LENGTH_ARB = constant.Constant( 'GL_INFO_LOG_LENGTH_ARB', 0x8B84 )

glShaderSourceARB = platform.createExtensionFunction(
    'glShaderSourceARB', dll=platform.PLATFORM.GL,
    resultType=None,
    argTypes=(_types.GLhandleARB, _types.GLsizei, ctypes.POINTER(ctypes.c_char_p), arrays.GLintArray,),
    doc = 'glShaderSourceARB( GLhandleARB(shaderObj), [bytes(string),...] ) -> None',
    argNames = ('shaderObj', 'count', 'string', 'length',),
    extension = _EXTENSION_NAME,
)
conv = converters.StringLengths( name='string' )
glShaderSourceARB = wrapper.wrapper(
    glShaderSourceARB
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

def _afterCheck( key ):
    """Generate an error-checking function for compilation operations"""
    def GLSLCheckError(
        result,
        baseOperation=None,
        cArguments=None,
        *args
    ):
        result = _errors._error_checker.glCheckError( result, baseOperation, cArguments, *args )
        status = glGetObjectParameterivARB(
            cArguments[0], key
        )
        if not status:
            raise error.GLError(
                result = result,
                baseOperation = baseOperation,
                cArguments = cArguments,
                description= glGetInfoLogARB( cArguments[0] )
            )
        return result
    return GLSLCheckError

if OpenGL.ERROR_CHECKING:
    glCompileShaderARB.errcheck = _afterCheck( GL_OBJECT_COMPILE_STATUS_ARB )
if OpenGL.ERROR_CHECKING:
    glLinkProgramARB.errcheck = _afterCheck( GL_OBJECT_LINK_STATUS_ARB )
## Not sure why, but these give invalid operation :(
##if glValidateProgramARB and OpenGL.ERROR_CHECKING:
##	glValidateProgramARB.errcheck = _afterCheck( GL_OBJECT_VALIDATE_STATUS_ARB )

@_lazy( glGetInfoLogARB )
def glGetInfoLogARB( baseOperation, obj ):
    """Retrieve the program/shader's error messages as a Python string

    returns string which is '' if no message
    """
    length = int(glGetObjectParameterivARB(obj, GL_INFO_LOG_LENGTH_ARB))
    if length > 0:
        log = ctypes.create_string_buffer(length)
        baseOperation(obj, length, None, log)
        return log.value.strip(_NULL_8_BYTE) # null-termination
    return ''

@_lazy( glGetAttachedObjectsARB )
def glGetAttachedObjectsARB( baseOperation, obj ):
    """Retrieve the attached objects as an array of GLhandleARB instances"""
    length= glGetObjectParameterivARB( obj, GL_OBJECT_ATTACHED_OBJECTS_ARB )
    if length > 0:
        storage = arrays.GLuintArray.zeros( (length,))
        baseOperation( obj, length, None, storage )
        return storage
    return arrays.GLuintArray.zeros( (0,))

@_lazy( glGetShaderSourceARB )
def glGetShaderSourceARB( baseOperation, obj ):
    """Retrieve the program/shader's source code as a Python string

    returns string which is '' if no source code
    """
    length = int(glGetObjectParameterivARB(obj, GL_OBJECT_SHADER_SOURCE_LENGTH_ARB))
    if length > 0:
        source = ctypes.create_string_buffer(length)
        baseOperation(obj, length, None, source)
        return source.value.strip(_NULL_8_BYTE) # null-termination
    return ''

@_lazy( glGetActiveUniformARB )
def glGetActiveUniformARB(baseOperation,program, index,bufSize=None):
    """Retrieve the name, size and type of the uniform of the index in the program"""
    max_index = int(glGetObjectParameterivARB( program, GL_OBJECT_ACTIVE_UNIFORMS_ARB ))
    if bufSize is None:
        bufSize = int(glGetObjectParameterivARB( program, GL_OBJECT_ACTIVE_UNIFORM_MAX_LENGTH_ARB))
    if index < max_index and index >= 0:
        length,name,size,type = baseOperation( program, index, bufSize )
        if hasattr(name,'tostring'):
            name = name.tostring().rstrip(b'\000')
        elif hasattr(name,'value'):
            name = name.value
        return name,size,type
    raise IndexError( 'Index %s out of range 0 to %i' % (index, max_index - 1, ) )

@_lazy( glGetUniformLocationARB )
def glGetUniformLocationARB( baseOperation, program, name ):
    """Check that name is a string with a null byte at the end of it"""
    if not name:
        raise ValueError( """Non-null name required""" )
    name = as_8_bit( name )
    if name[-1] != _NULL_8_BYTE:
        name = name + _NULL_8_BYTE
    return baseOperation( program, name )
