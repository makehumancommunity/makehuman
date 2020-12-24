'''OpenGL extension EXT.direct_state_access

This module customises the behaviour of the 
OpenGL.raw.GL.EXT.direct_state_access to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension introduces a set of new "direct state access"
	commands (meaning no selector is involved) to access (update and
	query) OpenGL state that previously depended on the OpenGL state
	selectors for access.  These new commands supplement the existing
	selector-based OpenGL commands to access the same state.
	
	The intent of this extension is to make it more efficient for
	libraries to avoid disturbing selector and latched state.  The
	extension also allows more efficient command usage by eliminating
	the need for selector update commands.
	
	Two derivative advantages of this extension are 1) display lists
	can be executed using these commands that avoid disturbing selectors
	that subsequent commands may depend on, and 2) drivers implemented
	with a dual-thread partitioning with OpenGL command buffering from
	an application thread and then OpenGL command dispatching in a
	concurrent driver thread can avoid thread synchronization created by
	selector saving, setting, command execution, and selector restoration.
	
	This extension does not itself add any new OpenGL state.
	
	We call a state variable in OpenGL an "OpenGL state selector" or
	simply a "selector" if OpenGL commands depend on the state variable
	to determine what state to query or update.  The matrix mode and
	active texture are both selectors.  Object bindings for buffers,
	programs, textures, and framebuffer objects are also selectors.
	
	We call OpenGL state "latched" if the state is set by one OpenGL
	command but then that state is saved by a subsequent command or the
	state determines how client memory or buffer object memory is accessed
	by a subsequent command.  The array and element array buffer bindings
	are latched by vertex array specification commands to determine
	which buffer a given vertex array uses.  Vertex array state and pixel
	pack/unpack state decides how client memory or buffer object memory is
	accessed by subsequent vertex pulling or image specification commands.
	
	The existence of selectors and latched state in the OpenGL API
	reduces the number of parameters to various sets of OpenGL commands
	but complicates the access to state for layered libraries which seek
	to access state without disturbing other state, namely the state of
	state selectors and latched state.  In many cases, selectors and
	latched state were introduced by extensions as OpenGL evolved to
	minimize the disruption to the OpenGL API when new functionality,
	particularly the pluralization of existing functionality as when
	texture objects and later multiple texture units, was introduced.
	
	The OpenGL API involves several selectors (listed in historical
	order of introduction):
	
	  o  The matrix mode.
	
	  o  The current bound texture for each supported texture target.
	
	  o  The active texture.
	
	  o  The active client texture.
	
	  o  The current bound program for each supported program target.
	
	  o  The current bound buffer for each supported buffer target.
	
	  o  The current GLSL program.
	
	  o  The current framebuffer object.
	
	The new selector-free update commands can be compiled into display
	lists.
	
	The OpenGL API has latched state for vertex array buffer objects
	and pixel store state.  When an application issues a GL command to
	unpack or pack pixels (for example, glTexImage2D or glReadPixels
	respectively), the current unpack and pack pixel store state
	determines how the pixels are unpacked from/packed to client memory
	or pixel buffer objects.  For example, consider:
	
	  glPixelStorei(GL_UNPACK_SWAP_BYTES, GL_TRUE);
	  glPixelStorei(GL_UNPACK_ROW_LENGTH, 640);
	  glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 47);
	  glDrawPixels(100, 100, GL_RGB, GL_FLOAT, pixels);
	
	The unpack swap bytes and row length state set by the preceding
	glPixelStorei commands (as well as the 6 other unpack pixel store
	state variables) control how data is read (unpacked) from buffer of
	data pointed to by pixels.  The glBindBuffer command also specifies
	an unpack buffer object (47) so the pixel pointer is actually treated
	as a byte offset into buffer object 47.
	
	When an application issues a command to configure a vertex array,
	the current array buffer state is latched as the binding for the
	particular vertex array being specified.  For example, consider:
	
	  glBindBuffer(GL_ARRAY_BUFFER, 23);
	  glVertexPointer(3, GL_FLOAT, 12, pointer);
	
	The glBindBuffer command updates the array buffering binding
	(GL_ARRAY_BUFFER_BINDING) to the buffer object named 23.  The
	subsequent glVertexPointer command specifies explicit parameters
	for the size, type, stride, and pointer to access the position
	vertex array BUT ALSO latches the current array buffer binding for
	the vertex array buffer binding (GL_VERTEX_ARRAY_BUFFER_BINDING).
	Effectively the current array buffer binding buffer object becomes
	an implicit fifth parameter to glVertexPointer and this applies to
	all the gl*Pointer vertex array specification commands.
	
	Selectors and latched state create problems for layered libraries
	using OpenGL because selectors require the selector state to be
	modified to update some other state and latched state means implicit
	state can affect the operation of commands specifying, packing, or
	unpacking data through pointers/offsets.  For layered libraries,
	a state update performed by the library may attempt to save the
	selector state, set the selector, update/query some state the
	selector controls, and then restore the selector to its saved state.
	Layered libraries can skip the selector save/restore but this risks
	introducing uncertainty about the state of a selector after calling
	layered library routines.  Such selector side-effects are difficult
	to document and lead to compatibility issues as the layered library
	evolves or its usage varies.  For latched state, layered libraries
	may find commands such as glDrawPixels do not work as expected
	because latched pixel store state is not what the library expects.
	Querying or pushing the latched state, setting the latched state
	explicitly, performing the operation involving latched state, and
	then restoring or popping the latched state avoids entanglements
	with latched state but at considerable cost.
	
	EXAMPLE USAGE OF THIS EXTENSION'S FUNCTIONALITY
	
	Consider the following routine to set the modelview matrix involving
	the matrix mode selector:
	
	  void setModelviewMatrix(const GLfloat matrix[16])
	  {
	    GLenum savedMatrixMode;
	
	    glGetIntegerv(GL_MATRIX_MODE, &savedMatrixMode);
	    glMatrixMode(GL_MODELVIEW);
	    glLoadMatrixf(matrix);
	    glMatrixMode(savedMatrixMode);
	  }
	
	Notice that four OpenGL commands are required to update the current
	modelview matrix without disturbing the matrix mode selector.
	
	OpenGL query commands can also substantially reduce the performance
	of modern OpenGL implementations which may off-load OpenGL state
	processing to another CPU core/thread or to the GPU itself.
	
	An alternative to querying the selector is to use the
	glPushAttrib/glPopAttrib commands.  However this approach typically
	involves pushing far more state than simply the one or two selectors
	that need to be saved and restored.  Because so much state is
	associated with a given push/pop attribute bit, the glPushAttrib
	and glPopAttrib commands are considerably more costly than the
	save/restore approach.  Additionally glPushAttrib risks overflowing
	the attribute stack.
	
	The reliability and performance of layered libraries and applications
	can be improved by adding to the OpenGL API a new set of commands
	to access directly OpenGL state that otherwise involves selectors
	to access.
	
	The above example can be reimplemented more efficiently and without
	selector side-effects:
	
	  void setModelviewMatrix(const GLfloat matrix[16])
	  {
	    glMatrixLoadfEXT(GL_MODELVIEW, matrix);
	  }
	
	Consider a layered library seeking to load a texture:
	
	  void loadTexture(GLint texobj, GLint width, GLint height,
	                   void *data)
	  {
	    glBindTexture(GL_TEXTURE_2D, texobj);
	    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8,
	                 width, height, GL_RGB, GL_FLOAT, data);
	  }
	
	The library expects the data to be packed into the buffer pointed
	to by data.  But what if the current pixel unpack buffer binding
	is not zero so the current pixel unpack buffer, rather than client
	memory, will be read?  Or what if the application has modified
	the GL_UNPACK_ROW_LENGTH pixel store state before loadTexture
	is called?  
	
	We can fix the routine by calling glBindBuffer(GL_PIXEL_UNPACK_BUFFER,
	0) and setting all the pixel store unpack state to the initial state
	the loadTexture routine expects, but this is expensive.  It also risks
	disturbing the state so when loadTexture returns to the application,
	the application doesn't realize the current texture object (for
	whatever texture unit the current active texture happens to be) and
	pixel store state has changed.
	
	We can more efficiently implement this routine without disturbing
	selector or latched state as follows:
	
	  void loadTexture(GLint texobj, GLint width, GLint height,
	                   void *data)
	  {
	    glPushClientAttribDefaultEXT(GL_CLIENT_PIXEL_STORE_BIT);
	    glTextureImage2D(texobj, GL_TEXTURE_2D, 0, GL_RGB8,
	                     width, height, GL_RGB, GL_FLOAT, data);
	    glPopClientAttrib();
	  }
	
	Now loadTexture does not have to worry about inappropriately
	configured pixel store state or a non-zero pixel unpack buffer
	binding.  And loadTexture has no unintended side-effects for
	selector or latched state (assuming the client attrib state does
	not overflow).

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/direct_state_access.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.EXT.direct_state_access import *
from OpenGL.raw.GL.EXT.direct_state_access import _EXTENSION_NAME

def glInitDirectStateAccessEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glMatrixLoadfEXT=wrapper.wrapper(glMatrixLoadfEXT).setInputArraySize(
    'm', 16
)
glMatrixLoaddEXT=wrapper.wrapper(glMatrixLoaddEXT).setInputArraySize(
    'm', 16
)
glMatrixMultfEXT=wrapper.wrapper(glMatrixMultfEXT).setInputArraySize(
    'm', 16
)
glMatrixMultdEXT=wrapper.wrapper(glMatrixMultdEXT).setInputArraySize(
    'm', 16
)
# INPUT glTextureParameterfvEXT.params size not checked against 'pname'
glTextureParameterfvEXT=wrapper.wrapper(glTextureParameterfvEXT).setInputArraySize(
    'params', None
)
# INPUT glTextureParameterivEXT.params size not checked against 'pname'
glTextureParameterivEXT=wrapper.wrapper(glTextureParameterivEXT).setInputArraySize(
    'params', None
)
# INPUT glTextureImage1DEXT.pixels size not checked against 'format,type,width'
glTextureImage1DEXT=wrapper.wrapper(glTextureImage1DEXT).setInputArraySize(
    'pixels', None
)
# INPUT glTextureImage2DEXT.pixels size not checked against 'format,type,width,height'
glTextureImage2DEXT=wrapper.wrapper(glTextureImage2DEXT).setInputArraySize(
    'pixels', None
)
# INPUT glTextureSubImage1DEXT.pixels size not checked against 'format,type,width'
glTextureSubImage1DEXT=wrapper.wrapper(glTextureSubImage1DEXT).setInputArraySize(
    'pixels', None
)
# INPUT glTextureSubImage2DEXT.pixels size not checked against 'format,type,width,height'
glTextureSubImage2DEXT=wrapper.wrapper(glTextureSubImage2DEXT).setInputArraySize(
    'pixels', None
)
# OUTPUT glGetTextureImageEXT.pixels COMPSIZE(target, level, format, type) 
glGetTextureParameterfvEXT=wrapper.wrapper(glGetTextureParameterfvEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTextureParameterivEXT=wrapper.wrapper(glGetTextureParameterivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTextureLevelParameterfvEXT=wrapper.wrapper(glGetTextureLevelParameterfvEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTextureLevelParameterivEXT=wrapper.wrapper(glGetTextureLevelParameterivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glTextureImage3DEXT.pixels size not checked against 'format,type,width,height,depth'
glTextureImage3DEXT=wrapper.wrapper(glTextureImage3DEXT).setInputArraySize(
    'pixels', None
)
# INPUT glTextureSubImage3DEXT.pixels size not checked against 'format,type,width,height,depth'
glTextureSubImage3DEXT=wrapper.wrapper(glTextureSubImage3DEXT).setInputArraySize(
    'pixels', None
)
# INPUT glMultiTexCoordPointerEXT.pointer size not checked against 'size,type,stride'
glMultiTexCoordPointerEXT=wrapper.wrapper(glMultiTexCoordPointerEXT).setInputArraySize(
    'pointer', None
)
# INPUT glMultiTexEnvfvEXT.params size not checked against 'pname'
glMultiTexEnvfvEXT=wrapper.wrapper(glMultiTexEnvfvEXT).setInputArraySize(
    'params', None
)
# INPUT glMultiTexEnvivEXT.params size not checked against 'pname'
glMultiTexEnvivEXT=wrapper.wrapper(glMultiTexEnvivEXT).setInputArraySize(
    'params', None
)
# INPUT glMultiTexGendvEXT.params size not checked against 'pname'
glMultiTexGendvEXT=wrapper.wrapper(glMultiTexGendvEXT).setInputArraySize(
    'params', None
)
# INPUT glMultiTexGenfvEXT.params size not checked against 'pname'
glMultiTexGenfvEXT=wrapper.wrapper(glMultiTexGenfvEXT).setInputArraySize(
    'params', None
)
# INPUT glMultiTexGenivEXT.params size not checked against 'pname'
glMultiTexGenivEXT=wrapper.wrapper(glMultiTexGenivEXT).setInputArraySize(
    'params', None
)
glGetMultiTexEnvfvEXT=wrapper.wrapper(glGetMultiTexEnvfvEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetMultiTexEnvivEXT=wrapper.wrapper(glGetMultiTexEnvivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetMultiTexGendvEXT=wrapper.wrapper(glGetMultiTexGendvEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetMultiTexGenfvEXT=wrapper.wrapper(glGetMultiTexGenfvEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetMultiTexGenivEXT=wrapper.wrapper(glGetMultiTexGenivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glMultiTexParameterivEXT.params size not checked against 'pname'
glMultiTexParameterivEXT=wrapper.wrapper(glMultiTexParameterivEXT).setInputArraySize(
    'params', None
)
# INPUT glMultiTexParameterfvEXT.params size not checked against 'pname'
glMultiTexParameterfvEXT=wrapper.wrapper(glMultiTexParameterfvEXT).setInputArraySize(
    'params', None
)
# INPUT glMultiTexImage1DEXT.pixels size not checked against 'format,type,width'
glMultiTexImage1DEXT=wrapper.wrapper(glMultiTexImage1DEXT).setInputArraySize(
    'pixels', None
)
# INPUT glMultiTexImage2DEXT.pixels size not checked against 'format,type,width,height'
glMultiTexImage2DEXT=wrapper.wrapper(glMultiTexImage2DEXT).setInputArraySize(
    'pixels', None
)
# INPUT glMultiTexSubImage1DEXT.pixels size not checked against 'format,type,width'
glMultiTexSubImage1DEXT=wrapper.wrapper(glMultiTexSubImage1DEXT).setInputArraySize(
    'pixels', None
)
# INPUT glMultiTexSubImage2DEXT.pixels size not checked against 'format,type,width,height'
glMultiTexSubImage2DEXT=wrapper.wrapper(glMultiTexSubImage2DEXT).setInputArraySize(
    'pixels', None
)
# OUTPUT glGetMultiTexImageEXT.pixels COMPSIZE(target, level, format, type) 
glGetMultiTexParameterfvEXT=wrapper.wrapper(glGetMultiTexParameterfvEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetMultiTexParameterivEXT=wrapper.wrapper(glGetMultiTexParameterivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetMultiTexLevelParameterfvEXT=wrapper.wrapper(glGetMultiTexLevelParameterfvEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetMultiTexLevelParameterivEXT=wrapper.wrapper(glGetMultiTexLevelParameterivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glMultiTexImage3DEXT.pixels size not checked against 'format,type,width,height,depth'
glMultiTexImage3DEXT=wrapper.wrapper(glMultiTexImage3DEXT).setInputArraySize(
    'pixels', None
)
# INPUT glMultiTexSubImage3DEXT.pixels size not checked against 'format,type,width,height,depth'
glMultiTexSubImage3DEXT=wrapper.wrapper(glMultiTexSubImage3DEXT).setInputArraySize(
    'pixels', None
)
glGetFloatIndexedvEXT=wrapper.wrapper(glGetFloatIndexedvEXT).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
glGetDoubleIndexedvEXT=wrapper.wrapper(glGetDoubleIndexedvEXT).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
glGetPointerIndexedvEXT=wrapper.wrapper(glGetPointerIndexedvEXT).setOutput(
    'data',size=(1,),orPassIn=True
)
glGetIntegerIndexedvEXT=wrapper.wrapper(glGetIntegerIndexedvEXT).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
glGetBooleanIndexedvEXT=wrapper.wrapper(glGetBooleanIndexedvEXT).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
# INPUT glCompressedTextureImage3DEXT.bits size not checked against imageSize
glCompressedTextureImage3DEXT=wrapper.wrapper(glCompressedTextureImage3DEXT).setInputArraySize(
    'bits', None
)
# INPUT glCompressedTextureImage2DEXT.bits size not checked against imageSize
glCompressedTextureImage2DEXT=wrapper.wrapper(glCompressedTextureImage2DEXT).setInputArraySize(
    'bits', None
)
# INPUT glCompressedTextureImage1DEXT.bits size not checked against imageSize
glCompressedTextureImage1DEXT=wrapper.wrapper(glCompressedTextureImage1DEXT).setInputArraySize(
    'bits', None
)
# INPUT glCompressedTextureSubImage3DEXT.bits size not checked against imageSize
glCompressedTextureSubImage3DEXT=wrapper.wrapper(glCompressedTextureSubImage3DEXT).setInputArraySize(
    'bits', None
)
# INPUT glCompressedTextureSubImage2DEXT.bits size not checked against imageSize
glCompressedTextureSubImage2DEXT=wrapper.wrapper(glCompressedTextureSubImage2DEXT).setInputArraySize(
    'bits', None
)
# INPUT glCompressedTextureSubImage1DEXT.bits size not checked against imageSize
glCompressedTextureSubImage1DEXT=wrapper.wrapper(glCompressedTextureSubImage1DEXT).setInputArraySize(
    'bits', None
)
# OUTPUT glGetCompressedTextureImageEXT.img COMPSIZE(target, lod) 
# INPUT glCompressedMultiTexImage3DEXT.bits size not checked against imageSize
glCompressedMultiTexImage3DEXT=wrapper.wrapper(glCompressedMultiTexImage3DEXT).setInputArraySize(
    'bits', None
)
# INPUT glCompressedMultiTexImage2DEXT.bits size not checked against imageSize
glCompressedMultiTexImage2DEXT=wrapper.wrapper(glCompressedMultiTexImage2DEXT).setInputArraySize(
    'bits', None
)
# INPUT glCompressedMultiTexImage1DEXT.bits size not checked against imageSize
glCompressedMultiTexImage1DEXT=wrapper.wrapper(glCompressedMultiTexImage1DEXT).setInputArraySize(
    'bits', None
)
# INPUT glCompressedMultiTexSubImage3DEXT.bits size not checked against imageSize
glCompressedMultiTexSubImage3DEXT=wrapper.wrapper(glCompressedMultiTexSubImage3DEXT).setInputArraySize(
    'bits', None
)
# INPUT glCompressedMultiTexSubImage2DEXT.bits size not checked against imageSize
glCompressedMultiTexSubImage2DEXT=wrapper.wrapper(glCompressedMultiTexSubImage2DEXT).setInputArraySize(
    'bits', None
)
# INPUT glCompressedMultiTexSubImage1DEXT.bits size not checked against imageSize
glCompressedMultiTexSubImage1DEXT=wrapper.wrapper(glCompressedMultiTexSubImage1DEXT).setInputArraySize(
    'bits', None
)
# OUTPUT glGetCompressedMultiTexImageEXT.img COMPSIZE(target, lod) 
glMatrixLoadTransposefEXT=wrapper.wrapper(glMatrixLoadTransposefEXT).setInputArraySize(
    'm', 16
)
glMatrixLoadTransposedEXT=wrapper.wrapper(glMatrixLoadTransposedEXT).setInputArraySize(
    'm', 16
)
glMatrixMultTransposefEXT=wrapper.wrapper(glMatrixMultTransposefEXT).setInputArraySize(
    'm', 16
)
glMatrixMultTransposedEXT=wrapper.wrapper(glMatrixMultTransposedEXT).setInputArraySize(
    'm', 16
)
# INPUT glNamedBufferDataEXT.data size not checked against 'size'
glNamedBufferDataEXT=wrapper.wrapper(glNamedBufferDataEXT).setInputArraySize(
    'data', None
)
# INPUT glNamedBufferSubDataEXT.data size not checked against 'size'
glNamedBufferSubDataEXT=wrapper.wrapper(glNamedBufferSubDataEXT).setInputArraySize(
    'data', None
)
glGetNamedBufferParameterivEXT=wrapper.wrapper(glGetNamedBufferParameterivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetNamedBufferPointervEXT=wrapper.wrapper(glGetNamedBufferPointervEXT).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetNamedBufferSubDataEXT=wrapper.wrapper(glGetNamedBufferSubDataEXT).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='size',orPassIn=True
)
# INPUT glProgramUniform1fvEXT.value size not checked against count
glProgramUniform1fvEXT=wrapper.wrapper(glProgramUniform1fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2fvEXT.value size not checked against count*2
glProgramUniform2fvEXT=wrapper.wrapper(glProgramUniform2fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3fvEXT.value size not checked against count*3
glProgramUniform3fvEXT=wrapper.wrapper(glProgramUniform3fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4fvEXT.value size not checked against count*4
glProgramUniform4fvEXT=wrapper.wrapper(glProgramUniform4fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform1ivEXT.value size not checked against count
glProgramUniform1ivEXT=wrapper.wrapper(glProgramUniform1ivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2ivEXT.value size not checked against count*2
glProgramUniform2ivEXT=wrapper.wrapper(glProgramUniform2ivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3ivEXT.value size not checked against count*3
glProgramUniform3ivEXT=wrapper.wrapper(glProgramUniform3ivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4ivEXT.value size not checked against count*4
glProgramUniform4ivEXT=wrapper.wrapper(glProgramUniform4ivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2fvEXT.value size not checked against count*4
glProgramUniformMatrix2fvEXT=wrapper.wrapper(glProgramUniformMatrix2fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3fvEXT.value size not checked against count*9
glProgramUniformMatrix3fvEXT=wrapper.wrapper(glProgramUniformMatrix3fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4fvEXT.value size not checked against count*16
glProgramUniformMatrix4fvEXT=wrapper.wrapper(glProgramUniformMatrix4fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x3fvEXT.value size not checked against count*6
glProgramUniformMatrix2x3fvEXT=wrapper.wrapper(glProgramUniformMatrix2x3fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x2fvEXT.value size not checked against count*6
glProgramUniformMatrix3x2fvEXT=wrapper.wrapper(glProgramUniformMatrix3x2fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x4fvEXT.value size not checked against count*8
glProgramUniformMatrix2x4fvEXT=wrapper.wrapper(glProgramUniformMatrix2x4fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x2fvEXT.value size not checked against count*8
glProgramUniformMatrix4x2fvEXT=wrapper.wrapper(glProgramUniformMatrix4x2fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x4fvEXT.value size not checked against count*12
glProgramUniformMatrix3x4fvEXT=wrapper.wrapper(glProgramUniformMatrix3x4fvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x3fvEXT.value size not checked against count*12
glProgramUniformMatrix4x3fvEXT=wrapper.wrapper(glProgramUniformMatrix4x3fvEXT).setInputArraySize(
    'value', None
)
# INPUT glTextureParameterIivEXT.params size not checked against 'pname'
glTextureParameterIivEXT=wrapper.wrapper(glTextureParameterIivEXT).setInputArraySize(
    'params', None
)
# INPUT glTextureParameterIuivEXT.params size not checked against 'pname'
glTextureParameterIuivEXT=wrapper.wrapper(glTextureParameterIuivEXT).setInputArraySize(
    'params', None
)
glGetTextureParameterIivEXT=wrapper.wrapper(glGetTextureParameterIivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTextureParameterIuivEXT=wrapper.wrapper(glGetTextureParameterIuivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glMultiTexParameterIivEXT.params size not checked against 'pname'
glMultiTexParameterIivEXT=wrapper.wrapper(glMultiTexParameterIivEXT).setInputArraySize(
    'params', None
)
# INPUT glMultiTexParameterIuivEXT.params size not checked against 'pname'
glMultiTexParameterIuivEXT=wrapper.wrapper(glMultiTexParameterIuivEXT).setInputArraySize(
    'params', None
)
glGetMultiTexParameterIivEXT=wrapper.wrapper(glGetMultiTexParameterIivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetMultiTexParameterIuivEXT=wrapper.wrapper(glGetMultiTexParameterIuivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glProgramUniform1uivEXT.value size not checked against count
glProgramUniform1uivEXT=wrapper.wrapper(glProgramUniform1uivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2uivEXT.value size not checked against count*2
glProgramUniform2uivEXT=wrapper.wrapper(glProgramUniform2uivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3uivEXT.value size not checked against count*3
glProgramUniform3uivEXT=wrapper.wrapper(glProgramUniform3uivEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4uivEXT.value size not checked against count*4
glProgramUniform4uivEXT=wrapper.wrapper(glProgramUniform4uivEXT).setInputArraySize(
    'value', None
)
# INPUT glNamedProgramLocalParameters4fvEXT.params size not checked against count*4
glNamedProgramLocalParameters4fvEXT=wrapper.wrapper(glNamedProgramLocalParameters4fvEXT).setInputArraySize(
    'params', None
)
glNamedProgramLocalParameterI4ivEXT=wrapper.wrapper(glNamedProgramLocalParameterI4ivEXT).setInputArraySize(
    'params', 4
)
# INPUT glNamedProgramLocalParametersI4ivEXT.params size not checked against count*4
glNamedProgramLocalParametersI4ivEXT=wrapper.wrapper(glNamedProgramLocalParametersI4ivEXT).setInputArraySize(
    'params', None
)
glNamedProgramLocalParameterI4uivEXT=wrapper.wrapper(glNamedProgramLocalParameterI4uivEXT).setInputArraySize(
    'params', 4
)
# INPUT glNamedProgramLocalParametersI4uivEXT.params size not checked against count*4
glNamedProgramLocalParametersI4uivEXT=wrapper.wrapper(glNamedProgramLocalParametersI4uivEXT).setInputArraySize(
    'params', None
)
glGetNamedProgramLocalParameterIivEXT=wrapper.wrapper(glGetNamedProgramLocalParameterIivEXT).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetNamedProgramLocalParameterIuivEXT=wrapper.wrapper(glGetNamedProgramLocalParameterIuivEXT).setOutput(
    'params',size=(4,),orPassIn=True
)
# INPUT glGetFloati_vEXT.params size not checked against 'pname'
glGetFloati_vEXT=wrapper.wrapper(glGetFloati_vEXT).setInputArraySize(
    'params', None
)
# INPUT glGetDoublei_vEXT.params size not checked against 'pname'
glGetDoublei_vEXT=wrapper.wrapper(glGetDoublei_vEXT).setInputArraySize(
    'params', None
)
glGetPointeri_vEXT=wrapper.wrapper(glGetPointeri_vEXT).setInputArraySize(
    'params', 1
)
# INPUT glNamedProgramStringEXT.string size not checked against len
glNamedProgramStringEXT=wrapper.wrapper(glNamedProgramStringEXT).setInputArraySize(
    'string', None
)
glNamedProgramLocalParameter4dvEXT=wrapper.wrapper(glNamedProgramLocalParameter4dvEXT).setInputArraySize(
    'params', 4
)
glNamedProgramLocalParameter4fvEXT=wrapper.wrapper(glNamedProgramLocalParameter4fvEXT).setInputArraySize(
    'params', 4
)
glGetNamedProgramLocalParameterdvEXT=wrapper.wrapper(glGetNamedProgramLocalParameterdvEXT).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetNamedProgramLocalParameterfvEXT=wrapper.wrapper(glGetNamedProgramLocalParameterfvEXT).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetNamedProgramivEXT=wrapper.wrapper(glGetNamedProgramivEXT).setOutput(
    'params',size=(1,),orPassIn=True
)
# OUTPUT glGetNamedProgramStringEXT.string COMPSIZE(program, pname) 
glGetNamedRenderbufferParameterivEXT=wrapper.wrapper(glGetNamedRenderbufferParameterivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetNamedFramebufferAttachmentParameterivEXT=wrapper.wrapper(glGetNamedFramebufferAttachmentParameterivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glFramebufferDrawBuffersEXT.bufs size not checked against n
glFramebufferDrawBuffersEXT=wrapper.wrapper(glFramebufferDrawBuffersEXT).setInputArraySize(
    'bufs', None
)
glGetFramebufferParameterivEXT=wrapper.wrapper(glGetFramebufferParameterivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetVertexArrayPointervEXT=wrapper.wrapper(glGetVertexArrayPointervEXT).setInputArraySize(
    'param', 1
)
# INPUT glNamedBufferStorageEXT.data size not checked against size
glNamedBufferStorageEXT=wrapper.wrapper(glNamedBufferStorageEXT).setInputArraySize(
    'data', None
)
# INPUT glClearNamedBufferDataEXT.data size not checked against 'format,type'
glClearNamedBufferDataEXT=wrapper.wrapper(glClearNamedBufferDataEXT).setInputArraySize(
    'data', None
)
# INPUT glClearNamedBufferSubDataEXT.data size not checked against 'format,type'
glClearNamedBufferSubDataEXT=wrapper.wrapper(glClearNamedBufferSubDataEXT).setInputArraySize(
    'data', None
)
glGetNamedFramebufferParameterivEXT=wrapper.wrapper(glGetNamedFramebufferParameterivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glProgramUniform1dvEXT.value size not checked against count
glProgramUniform1dvEXT=wrapper.wrapper(glProgramUniform1dvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2dvEXT.value size not checked against count*2
glProgramUniform2dvEXT=wrapper.wrapper(glProgramUniform2dvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3dvEXT.value size not checked against count*3
glProgramUniform3dvEXT=wrapper.wrapper(glProgramUniform3dvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4dvEXT.value size not checked against count*4
glProgramUniform4dvEXT=wrapper.wrapper(glProgramUniform4dvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2dvEXT.value size not checked against count*4
glProgramUniformMatrix2dvEXT=wrapper.wrapper(glProgramUniformMatrix2dvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3dvEXT.value size not checked against count*9
glProgramUniformMatrix3dvEXT=wrapper.wrapper(glProgramUniformMatrix3dvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4dvEXT.value size not checked against count*16
glProgramUniformMatrix4dvEXT=wrapper.wrapper(glProgramUniformMatrix4dvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x3dvEXT.value size not checked against count*6
glProgramUniformMatrix2x3dvEXT=wrapper.wrapper(glProgramUniformMatrix2x3dvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x4dvEXT.value size not checked against count*8
glProgramUniformMatrix2x4dvEXT=wrapper.wrapper(glProgramUniformMatrix2x4dvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x2dvEXT.value size not checked against count*6
glProgramUniformMatrix3x2dvEXT=wrapper.wrapper(glProgramUniformMatrix3x2dvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x4dvEXT.value size not checked against count*12
glProgramUniformMatrix3x4dvEXT=wrapper.wrapper(glProgramUniformMatrix3x4dvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x2dvEXT.value size not checked against count*8
glProgramUniformMatrix4x2dvEXT=wrapper.wrapper(glProgramUniformMatrix4x2dvEXT).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x3dvEXT.value size not checked against count*12
glProgramUniformMatrix4x3dvEXT=wrapper.wrapper(glProgramUniformMatrix4x3dvEXT).setInputArraySize(
    'value', None
)
### END AUTOGENERATED SECTION