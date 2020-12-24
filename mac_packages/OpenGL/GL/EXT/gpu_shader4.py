'''OpenGL extension EXT.gpu_shader4

This module customises the behaviour of the 
OpenGL.raw.GL.EXT.gpu_shader4 to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides a set of new features to the OpenGL Shading
	Language and related APIs to support capabilities of new hardware. In
	particular, this extension provides the following functionality:
	
	   * New texture lookup functions are provided that allow shaders to
	     access individual texels using integer coordinates referring to the
	     texel location and level of detail. No filtering is performed. These
	     functions allow applications to use textures as one-, two-, and
	     three-dimensional arrays.
	
	   * New texture lookup functions are provided that allow shaders to query
	     the dimensions of a specific level-of-detail image of a texture
	     object.
	
	   * New texture lookup functions variants are provided that allow shaders
	     to pass a constant integer vector used to offset the texel locations
	     used during the lookup to assist in custom texture filtering
	     operations.
	
	   * New texture lookup functions are provided that allow shaders to
	     access one- and two-dimensional array textures. The second, or third,
	     coordinate is used to select the layer of the array to access.
	
	   * New "Grad" texture lookup functions are provided that allow shaders
	     to explicitely pass in derivative values which are used by the GL to
	     compute the level-of-detail when performing a texture lookup.
	
	   * A new texture lookup function is provided to access a buffer texture.
	
	   * The existing absolute LOD texture lookup functions are no longer
	     restricted to the vertex shader only.
	
	   * The ability to specify and use cubemap textures with a
	     DEPTH_COMPONENT internal format. This also enables shadow mapping on
	     cubemaps. The 'q' coordinate is used as the reference value for
	     comparisons. A set of new texture lookup functions is provided to
	     lookup into shadow cubemaps.
	
	   * The ability to specify if varying variables are interpolated in a
	     non-perspective correct manner, if they are flat shaded or, if
	     multi-sampling, if centroid sampling should be performed.
	
	   * Full signed integer and unsigned integer support in the OpenGL
	     Shading Language:
	
	         - Integers are defined as 32 bit values using two's complement.
	
	         - Unsigned integers and vectors thereof are added.
	
	         - New texture lookup functions are provided that return integer
	           values. These functions are to be used in conjunction with new
	           texture formats whose components are actual integers, rather
	           than integers that encode a floating-point value. To support
	           these lookup functions, new integer and unsigned-integer
	           sampler types are introduced.
	
	         - Integer bitwise operators are now enabled.
	
	         - Several built-in functions and operators now operate on
	           integers or vectors of integers.
	
	         - New vertex attribute functions are added that load integer
	           attribute data and can be referenced in a vertex shader as
	           integer data.
	
	         - New uniform loading commands are added to load unsigned integer
	           data.
	
	         - Varying variables can now be (unsigned) integers. If declared
	           as such, they have to be flat shaded.
	
	         - Fragment shaders can define their own output variables, and
	           declare them to be of type floating-point, integer or unsigned
	           integer. These variables are bound to a fragment color index
	           with the new API command BindFragDataLocationEXT(), and directed
	           to buffers using the existing DrawBuffer or DrawBuffers API
	           commands.
	
	   * Added new built-in functions truncate() and round() to the shading
	     language.
	
	   * A new built-in variable accessible from within vertex shaders that
	     holds the index <i> implicitly passed to ArrayElement to specify the
	     vertex. This is called the vertex ID.
	
	   * A new built-in variable accessible from within fragment and geometry
	     shaders that hold the index of the currently processed
	     primitive. This is called the primitive ID.
	
	This extension also briefly mentions a new shader type, called a geometry
	shader. A geometry shader is run after vertices are transformed, but
	before clipping. A geometry shader begins with a single primitive (point,
	line, triangle. It can read the attributes of any of the vertices in the
	primitive and use them to generate new primitives. A geometry shader has a
	fixed output primitive type (point, line strip, or triangle strip) and
	emits vertices to define a new primitive. Geometry shaders are discussed
	in detail in the GL_EXT_geometry_shader4 specification.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/gpu_shader4.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.EXT.gpu_shader4 import *
from OpenGL.raw.GL.EXT.gpu_shader4 import _EXTENSION_NAME

def glInitGpuShader4EXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# OUTPUT glGetUniformuivEXT.params COMPSIZE(program, location) 
# INPUT glBindFragDataLocationEXT.name size not checked against 'name'
glBindFragDataLocationEXT=wrapper.wrapper(glBindFragDataLocationEXT).setInputArraySize(
    'name', None
)
# INPUT glGetFragDataLocationEXT.name size not checked against 'name'
glGetFragDataLocationEXT=wrapper.wrapper(glGetFragDataLocationEXT).setInputArraySize(
    'name', None
)
# INPUT glUniform1uivEXT.value size not checked against count
glUniform1uivEXT=wrapper.wrapper(glUniform1uivEXT).setInputArraySize(
    'value', None
)
# INPUT glUniform2uivEXT.value size not checked against count*2
glUniform2uivEXT=wrapper.wrapper(glUniform2uivEXT).setInputArraySize(
    'value', None
)
# INPUT glUniform3uivEXT.value size not checked against count*3
glUniform3uivEXT=wrapper.wrapper(glUniform3uivEXT).setInputArraySize(
    'value', None
)
# INPUT glUniform4uivEXT.value size not checked against count*4
glUniform4uivEXT=wrapper.wrapper(glUniform4uivEXT).setInputArraySize(
    'value', None
)
### END AUTOGENERATED SECTION