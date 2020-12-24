'''OpenGL extension ARB.gpu_shader_fp64

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.gpu_shader_fp64 to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension allows GLSL shaders to use double-precision floating-point
	data types, including vectors and matrices of doubles.  Doubles may be
	used as inputs, outputs, and uniforms.  
	
	The shading language supports various arithmetic and comparison operators
	on double-precision scalar, vector, and matrix types, and provides a set
	of built-in functions including:
	
	  * square roots and inverse square roots;
	
	  * fused floating-point multiply-add operations;
	
	  * splitting a floating-point number into a significand and exponent
	    (frexp), or building a floating-point number from a significand and
	    exponent (ldexp);
	
	  * absolute value, sign tests, various functions to round to an integer
	    value, modulus, minimum, maximum, clamping, blending two values, step
	    functions, and testing for infinity and NaN values;
	
	  * packing and unpacking doubles into a pair of 32-bit unsigned integers;
	
	  * matrix component-wise multiplication, and computation of outer
	    products, transposes, determinants, and inverses; and
	
	  * vector relational functions.
	
	Double-precision versions of angle, trigonometry, and exponential
	functions are not supported.
	
	Implicit conversions are supported from integer and single-precision
	floating-point values to doubles, and this extension uses the relaxed
	function overloading rules specified by the ARB_gpu_shader5 extension to
	resolve ambiguities.
	
	This extension provides API functions for specifying double-precision
	uniforms in the default uniform block, including functions similar to the
	uniform functions added by EXT_direct_state_access (if supported).
	
	This extension provides an "LF" suffix for specifying double-precision
	constants.  Floating-point constants without a suffix in GLSL are treated
	as single-precision values for backward compatibility with versions not
	supporting doubles; similar constants are treated as double-precision
	values in the "C" programming language.
	
	This extension does not support interpolation of double-precision values;
	doubles used as fragment shader inputs must be qualified as "flat".
	Additionally, this extension does not allow vertex attributes with 64-bit
	components.  That support is added separately by EXT_vertex_attrib_64bit.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/gpu_shader_fp64.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.gpu_shader_fp64 import *
from OpenGL.raw.GL.ARB.gpu_shader_fp64 import _EXTENSION_NAME

def glInitGpuShaderFp64ARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glUniform1dv.value size not checked against count
glUniform1dv=wrapper.wrapper(glUniform1dv).setInputArraySize(
    'value', None
)
# INPUT glUniform2dv.value size not checked against count*2
glUniform2dv=wrapper.wrapper(glUniform2dv).setInputArraySize(
    'value', None
)
# INPUT glUniform3dv.value size not checked against count*3
glUniform3dv=wrapper.wrapper(glUniform3dv).setInputArraySize(
    'value', None
)
# INPUT glUniform4dv.value size not checked against count*4
glUniform4dv=wrapper.wrapper(glUniform4dv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix2dv.value size not checked against count*4
glUniformMatrix2dv=wrapper.wrapper(glUniformMatrix2dv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix3dv.value size not checked against count*9
glUniformMatrix3dv=wrapper.wrapper(glUniformMatrix3dv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix4dv.value size not checked against count*16
glUniformMatrix4dv=wrapper.wrapper(glUniformMatrix4dv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix2x3dv.value size not checked against count*6
glUniformMatrix2x3dv=wrapper.wrapper(glUniformMatrix2x3dv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix2x4dv.value size not checked against count*8
glUniformMatrix2x4dv=wrapper.wrapper(glUniformMatrix2x4dv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix3x2dv.value size not checked against count*6
glUniformMatrix3x2dv=wrapper.wrapper(glUniformMatrix3x2dv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix3x4dv.value size not checked against count*12
glUniformMatrix3x4dv=wrapper.wrapper(glUniformMatrix3x4dv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix4x2dv.value size not checked against count*8
glUniformMatrix4x2dv=wrapper.wrapper(glUniformMatrix4x2dv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix4x3dv.value size not checked against count*12
glUniformMatrix4x3dv=wrapper.wrapper(glUniformMatrix4x3dv).setInputArraySize(
    'value', None
)
# OUTPUT glGetUniformdv.params COMPSIZE(program, location) 
### END AUTOGENERATED SECTION