"""Convenience module providing common shader entry points

The point of this module is to allow client code to use
OpenGL Core names to reference shader-related operations
even if the local hardware only supports ARB extension-based
shader rendering.

There are also two utility methods compileProgram and compileShader
which make it easy to create demos which are shader-using.
"""
import logging
log = logging.getLogger( __name__ )
from OpenGL import GL
from OpenGL.GL.ARB import (
    shader_objects, fragment_shader, vertex_shader, vertex_program,
    geometry_shader4, separate_shader_objects, get_program_binary,
)
from OpenGL.extensions import alternate
from OpenGL._bytes import bytes,unicode,as_8_bit

__all__ = [
    'glAttachShader',
    'glDeleteShader',
    'glGetProgramInfoLog',
    'glGetShaderInfoLog',
    'glGetProgramiv',
    'glGetShaderiv',
    'compileProgram',
    'compileShader',
    'GL_VALIDATE_STATUS',
    'GL_LINK_STATUS',
    'ShaderCompilationError', 
    'ShaderValidationError', 
    'ShaderLinkError',
    # automatically added stuff here...
]

def _alt( base, name ):
    if hasattr( GL, base ):
        root = getattr( GL, base )
        if hasattr(root,'__call__'):
            globals()[base] = alternate(
                getattr(GL,base),
                getattr(module,name)
            )
            __all__.append( base )
        else:
            globals()[base] = root
            __all__.append( base )
        return True
    return False
_excludes = ['glGetProgramiv']
for module in (
    shader_objects,fragment_shader,vertex_shader,vertex_program,
   geometry_shader4,
):
    for name in dir(module):
        found = None
        for suffix in ('ObjectARB','_ARB','ARB'):
            if name.endswith( suffix ):
                found = False
                base = name[:-(len(suffix))]
                if base not in _excludes:
                    if _alt( base, name ):
                        found = True
                        break
        if found is False:
            log.debug( '''Found no alternate for: %s.%s''',
                module.__name__,name,
            )

glAttachShader = alternate( GL.glAttachShader,shader_objects.glAttachObjectARB )
glDetachShader = alternate( GL.glDetachShader,shader_objects.glDetachObjectARB )
glDeleteShader = alternate( GL.glDeleteShader,shader_objects.glDeleteObjectARB )
glGetAttachedShaders = alternate( GL.glGetAttachedShaders, shader_objects.glGetAttachedObjectsARB )

glGetProgramInfoLog = alternate( GL.glGetProgramInfoLog, shader_objects.glGetInfoLogARB )
glGetShaderInfoLog = alternate( GL.glGetShaderInfoLog, shader_objects.glGetInfoLogARB )

glGetShaderiv = alternate( GL.glGetShaderiv, shader_objects.glGetObjectParameterivARB )
glGetProgramiv = alternate( GL.glGetProgramiv, shader_objects.glGetObjectParameterivARB )

GL_VALIDATE_STATUS = GL.GL_VALIDATE_STATUS
GL_COMPILE_STATUS = GL.GL_COMPILE_STATUS
GL_LINK_STATUS = GL.GL_LINK_STATUS
GL_FALSE = GL.GL_FALSE
GL_TRUE = GL.GL_TRUE

class ShaderProgram( int ):
    """Integer sub-class with context-manager operation"""
    validated = False
    def __enter__( self ):
        """Start use of the program"""
        glUseProgram( self )
    def __exit__( self, typ, val, tb ):
        """Stop use of the program"""
        glUseProgram( 0 )
    
    def check_validate( self ):
        """Check that the program validates
        
        Validation has to occur *after* linking/loading
        
        raises ShaderValidationError on failures
        """
        glValidateProgram( self )
        validation = glGetProgramiv( self, GL_VALIDATE_STATUS )
        if validation == GL_FALSE:
            raise ShaderValidationError(
                """Validation failure (%r): %s"""%(
                validation,
                glGetProgramInfoLog( self ),
            ))
        self.validated = True
        return self

    def check_linked( self ):
        """Check link status for this program
        
        raises ShaderLinkError on failures
        """
        link_status = glGetProgramiv( self, GL_LINK_STATUS )
        if link_status == GL_FALSE:
            raise ShaderLinkError(
                """Link failure (%s): %s"""%(
                link_status,
                glGetProgramInfoLog( self ),
            ))
        return self

    def retrieve( self ):
        """Attempt to retrieve binary for this compiled shader
        
        Note that binaries for a program are *not* generally portable,
        they should be used solely for caching compiled programs for 
        local use; i.e. to reduce compilation overhead.
        
        returns (format,binaryData) for the shader program
        """
        from OpenGL.raw.GL._types import GLint,GLenum 
        from OpenGL.arrays import GLbyteArray
        size = GLint()
        glGetProgramiv( self, get_program_binary.GL_PROGRAM_BINARY_LENGTH, size )
        result = GLbyteArray.zeros( (size.value,))
        size2 = GLint()
        format = GLenum()
        get_program_binary.glGetProgramBinary( self, size.value, size2, format, result )
        return format.value, result 
    def load( self, format, binary, validate=True ):
        """Attempt to load binary-format for a pre-compiled shader
        
        See notes in retrieve
        """
        get_program_binary.glProgramBinary( self, format, binary, len(binary))
        if validate:
            self.check_validate()
        self.check_linked()
        return self

def compileProgram(*shaders, **named):
    """Create a new program, attach shaders and validate

    shaders -- arbitrary number of shaders to attach to the
        generated program.
    separable (keyword only) -- set the separable flag to allow 
        for partial installation of shader into the pipeline (see 
        glUseProgramStages)
    retrievable (keyword only) -- set the retrievable flag to 
        allow retrieval of the program binary representation, (see 
        glProgramBinary, glGetProgramBinary)
    validate (keyword only) -- if False, suppress automatic 
        validation against current GL state. In advanced usage 
        the validation can produce spurious errors. Note: this 
        function is *not* really intended for advanced usage,
        if you're finding yourself specifying this flag you 
        likely should be using your own shader management code.

    This convenience function is *not* standard OpenGL,
    but it does wind up being fairly useful for demos
    and the like.  You may wish to copy it to your code
    base to guard against PyOpenGL changes.

    Usage:

        shader = compileProgram(
            compileShader( source, GL_VERTEX_SHADER ),
            compileShader( source2, GL_FRAGMENT_SHADER ),
        )
        glUseProgram( shader )

    Note:
        If (and only if) validation of the linked program
        *passes* then the passed-in shader objects will be
        deleted from the GL.

    returns ShaderProgram() (GLuint) program reference
    raises RuntimeError subclasses {
        ShaderCompilationError, ShaderValidationError, ShaderLinkError,
    } when a link/validation failure occurs
    """
    program = glCreateProgram()
    if named.get('separable'):
        glProgramParameteri( program, separate_shader_objects.GL_PROGRAM_SEPARABLE, GL_TRUE )
    if named.get('retrievable'):
        glProgramParameteri( program, get_program_binary.GL_PROGRAM_BINARY_RETRIEVABLE_HINT, GL_TRUE )
    for shader in shaders:
        glAttachShader(program, shader)
    program = ShaderProgram( program )
    glLinkProgram(program)
    if named.get('validate', True):
        program.check_validate()
    program.check_linked()
    for shader in shaders:
        glDeleteShader(shader)
    return program
def compileShader( source, shaderType ):
    """Compile shader source of given type

    source -- GLSL source-code for the shader
    shaderType -- GLenum GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, etc,

    returns GLuint compiled shader reference
    raises RuntimeError when a compilation failure occurs
    """
    if isinstance( source, (bytes,unicode)):
        source = [ source ]
    source = [ as_8_bit(s) for s in source ]
    shader = glCreateShader(shaderType)
    glShaderSource( shader, source )
    glCompileShader( shader )
    result = glGetShaderiv( shader, GL_COMPILE_STATUS )
    if not(result):
        # TODO: this will be wrong if the user has
        # disabled traditional unpacking array support.
        raise ShaderCompilationError(
            """Shader compile failure (%s): %s"""%(
                result,
                glGetShaderInfoLog( shader ),
            ),
            source,
            shaderType,
        )
    return shader

class ShaderCompilationError(RuntimeError):
    """Raised when a shader compilation fails"""
class ShaderValidationError(RuntimeError):
    """Raised when a program fails to validate"""
class ShaderLinkError(RuntimeError):
    """Raised when a shader link fails"""