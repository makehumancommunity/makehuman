"""Convenience module providing common shader entry points

The point of this module is to allow client code to use
OpenGL Core names to reference shader-related operations
even if the local hardware only supports ARB extension-based
shader rendering.

There are also two utility methods compileProgram and compileShader
which make it easy to create demos which are shader-using.
"""
import logging
logging.basicConfig()
log = logging.getLogger( __name__ )
from OpenGL.GLES2 import *
from OpenGL._bytes import bytes,unicode,as_8_bit

__all__ = [
    'compileProgram',
    'compileShader',
]

class ShaderProgram( int ):
    """Integer sub-class with context-manager operation"""
    def __enter__( self ):
        """Start use of the program"""
        glUseProgram( self )
    def __exit__( self, typ, val, tb ):
        """Stop use of the program"""
        glUseProgram( 0 )
    
    def check_validate( self ):
        """Check that the program validates
        
        Validation has to occur *after* linking/loading
        
        raises RuntimeError on failures
        """
        glValidateProgram( self )
        validation = glGetProgramiv( self, GL_VALIDATE_STATUS )
        if validation == GL_FALSE:
            raise RuntimeError(
                """Validation failure (%s): %s"""%(
                validation,
                glGetProgramInfoLog( self ),
            ))
        return self

    def check_linked( self ):
        """Check link status for this program
        
        raises RuntimeError on failures
        """
        link_status = glGetProgramiv( self, GL_LINK_STATUS )
        if link_status == GL_FALSE:
            raise RuntimeError(
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
    def load( self, format, binary ):
        """Attempt to load binary-format for a pre-compiled shader
        
        See notes in retrieve
        """
        get_program_binary.glProgramBinary( self, format, binary, len(binary))
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
    raises RuntimeError when a link/validation failure occurs
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
    if result == GL_FALSE:
        # TODO: this will be wrong if the user has
        # disabled traditional unpacking array support.
        raise RuntimeError(
            """Shader compile failure (%s): %s"""%(
                result,
                glGetShaderInfoLog( shader ),
            ),
            source,
            shaderType,
        )
    return shader
