'''OpenGL extension ARB.uniform_buffer_object

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.uniform_buffer_object to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension introduces the concept of a group of GLSL uniforms
	known as a "uniform block", and the API mechanisms to store "uniform
	blocks" in GL buffer objects.
	
	The extension also defines both a standard cross-platform layout in
	memory for uniform block data, as well as mechanisms to allow the GL
	to optimize the data layout in an implementation-defined manner.
	
	Prior to this extension, the existing interface for modification of
	uniform values allowed modification of large numbers of values using
	glUniform* calls, but only for a single uniform name (or a uniform
	array) at a time. However, updating uniforms in this manner may not
	map well to heterogenous uniform data structures defined for a GL
	application and in these cases, the application is forced to either:
	
	    A) restructure their uniform data definitions into arrays
	    or
	    B) make an excessive number of calls through the GL interface
	       to one of the Uniform* variants.
	
	These solutions have their disadvantages. Solution A imposes
	considerable development overhead on the application developer. 
	Solution B may impose considerable run-time overhead on the
	application if the number of uniforms modified in a given frame of
	rendering is sufficiently large.
	
	This extension provides a better alternative to either (A) or (B) by
	allowing buffer object backing for the storage associated with all
	uniforms of a given GLSL program.
	
	Storing uniform blocks in buffer objects enables several key use
	cases:
	
	 - sharing of uniform data storage between program objects and
	   between program stages
	
	 - rapid swapping of sets of previously defined uniforms by storing
	   sets of uniform data on the GL server
	
	 - rapid updates of uniform data from both the client and the server
	
	The data storage for a uniform block can be declared to use one of
	three layouts in memory: packed, shared, or std140.
	
	  - "packed" uniform blocks have an implementation-dependent data
	    layout for efficiency, and unused uniforms may be eliminated by
	    the compiler to save space.
	
	  - "shared" uniform blocks, the default layout, have an implementation- 
	    dependent data layout for efficiency, but the layout will be uniquely
	    determined by the structure of the block, allowing data storage to be
	    shared across programs.
	
	  - "std140" uniform blocks have a standard cross-platform cross-vendor
	    layout (see below). Unused uniforms will not be eliminated.
	
	Any uniforms not declared in a named uniform block are said to 
	be part of the "default uniform block".
	
	While uniforms in the default uniform block are updated with
	glUniform* entry points and can have static initializers, uniforms
	in named uniform blocks are not. Instead, uniform block data is updated
	using the routines that update buffer objects and can not use static
	initializers.
	
	Rules and Concepts Guiding this Specification:
	
	For reference, a uniform has a "uniform index" (subsequently
	referred to as "u_index) and also a "uniform location" to
	efficiently identify it in the uniform data store of the
	implementation. We subsequently refer to this uniform data store of
	the implementation as the "uniform database".
	
	A "uniform block" only has a "uniform block index" used for queries
	and connecting the "uniform block" to a buffer object. A "uniform
	block" has no "location" because "uniform blocks" are not updated
	directly. The buffer object APIs are used instead.
	
	Properties of Uniforms and uniform blocks:
	
	a) A uniform is "active" if it exists in the database and has a valid
	   u_index.
	b) A "uniform block" is "active" if it exists in the database and
	   has a valid ub_index.
	c) Uniforms and "uniform blocks" can be inactive because they don't
	   exist in the source, or because they have been removed by dead
	   code elimination.
	d) An inactive uniform has u_index == INVALID_INDEX.
	e) An inactive uniform block has ub_index == INVALID_INDEX.
	f) A u_index or ub_index of INVALID_INDEX generates the
	   INVALID_VALUE error if given as a function argument.
	g) The default uniform block, which is not assigned any ub_index, uses a
	   private, internal data storage, and does not have any buffer object
	   associated with it.
	h) An active uniform that is a member of the default uniform block has
	   location >= 0 and it has offset == stride == -1.
	i) An active uniform that is a member of a named uniform block has
	   location == -1.
	j) A uniform location of -1 is silently ignored if given as a function
	   argument.
	k) Uniform block declarations may not be nested

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/uniform_buffer_object.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.uniform_buffer_object import *
from OpenGL.raw.GL.ARB.uniform_buffer_object import _EXTENSION_NAME

def glInitUniformBufferObjectARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glGetUniformIndices.uniformNames size not checked against 'uniformCount'
glGetUniformIndices=wrapper.wrapper(glGetUniformIndices).setOutput(
    'uniformIndices',size=_glgets._glget_size_mapping,pnameArg='uniformCount',orPassIn=True
).setInputArraySize(
    'uniformNames', None
)
# OUTPUT glGetActiveUniformsiv.params COMPSIZE(uniformCount, pname) 
# INPUT glGetActiveUniformsiv.uniformIndices size not checked against uniformCount
glGetActiveUniformsiv=wrapper.wrapper(glGetActiveUniformsiv).setInputArraySize(
    'uniformIndices', None
)
glGetActiveUniformName=wrapper.wrapper(glGetActiveUniformName).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'uniformName',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
# INPUT glGetUniformBlockIndex.uniformBlockName size not checked against ''
glGetUniformBlockIndex=wrapper.wrapper(glGetUniformBlockIndex).setInputArraySize(
    'uniformBlockName', None
)
# OUTPUT glGetActiveUniformBlockiv.params COMPSIZE(program, uniformBlockIndex, pname) 
glGetActiveUniformBlockName=wrapper.wrapper(glGetActiveUniformBlockName).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'uniformBlockName',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetIntegeri_v=wrapper.wrapper(glGetIntegeri_v).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
### END AUTOGENERATED SECTION