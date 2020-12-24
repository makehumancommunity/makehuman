'''OpenGL extension ARB.separate_shader_objects

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.separate_shader_objects to provide a more 
Python-friendly API

Overview (from the spec)
	
	Conventional GLSL requires multiple shader stages (vertex,
	fragment, geometry, tessellation control, and tessellation
	evaluation) to be linked into a single monolithic program object to
	specify a GLSL shader for each stage.
	
	While GLSL's monolithic approach has some advantages for
	optimizing shaders as a unit that span multiple stages, all
	existing GPU hardware supports the more flexible mix-and-match
	approach.
	
	Shaders written for HLSL9, Cg, the prior OpenGL assembly program
	extensions, and game console favor a more flexible "mix-and-match"
	approach to specifying shaders independently for these different
	shader stages.  Many developers build their shader content around
	the mix-and-match approach where they can use a single vertex shader
	with multiple fragment shaders (or vice versa).
	
	This extension adopts a "mix-and-match" shader stage model for GLSL
	allowing multiple different GLSL program objects to be bound at once
	each to an individual rendering pipeline stage independently of
	other stage bindings. This allows program objects to contain only
	the shader stages that best suit the applications needs.
	
	This extension introduces the program pipeline object that serves as
	a container for the program bound to any particular rendering stage.
	It can be bound, unbound, and rebound to simply save and restore the
	complete shader stage to program object bindings.  Like framebuffer
	and vertex array objects, program pipeline objects are "container"
	objects that are not shared between contexts.
	
	To bind a program object to a specific shader stage or set of
	stages, UseProgramStages is used.  The VERTEX_SHADER_BIT,
	GEOMETRY_SHADER_BIT, FRAGMENT_SHADER_BIT, TESS_CONTROL_SHADER_BIT,
	and TESS_EVALUATION_SHADER_BIT tokens refer to the conventional
	vertex, geometry, fragment, tessellation control and tessellation
	evaluation stages respectively. ActiveShaderProgram specifies the
	program that Uniform* commands will update.
	
	While ActiveShaderProgram allows the use of conventional Uniform*
	commands to update uniform variable values for separable program
	objects, this extension provides a preferrable interface in a set
	of ProgramUniform* commands that update the same uniform variables
	but take a parameter indicating the program object to be updated,
	rather than updating the currently active program object. These
	commands mirror those introduced in EXT_direct_state_access.
	
	While glActiveShaderProgram provides a selector for setting and
	querying uniform values of a program object, the glProgramUniform*
	commands provide a selector-free way to modify uniforms of a GLSL
	program object without an explicit bind. This selector-free model
	reduces API overhead and provides a cleaner interface for
	applications.
	
	Separate linking creates the possibility that certain output varyings
	of a shader may go unread by the subsequent shader inputting varyings.
	In this case, the output varyings are simply ignored.  It is also
	possible input varyings from a shader may not be written as output
	varyings of a preceding shader.  In this case, the unwritten input
	varying values are undefined.
	
	This extension builds on the proof-of-concept provided by
	EXT_separate_shader_objects which demonstrated that separate
	shader objects can work for GLSL.  EXT_separate_shader_objects
	was a response to repeated requests for this functionality from
	3D developers.
	
	This ARB version addresses several "loose ends" in the prior
	EXT extension.  In particular, it allows user-defined varyings
	with explicitly defined locations or implicitly assigned locations.
	
	This ARB extension extends the GLSL language's use of layout
	qualifiers to provide cross-stage interfacing.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/separate_shader_objects.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.separate_shader_objects import *
from OpenGL.raw.GL.ARB.separate_shader_objects import _EXTENSION_NAME

def glInitSeparateShaderObjectsARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glCreateShaderProgramv.strings size not checked against count
glCreateShaderProgramv=wrapper.wrapper(glCreateShaderProgramv).setInputArraySize(
    'strings', None
)
# INPUT glDeleteProgramPipelines.pipelines size not checked against n
glDeleteProgramPipelines=wrapper.wrapper(glDeleteProgramPipelines).setInputArraySize(
    'pipelines', None
)
glGenProgramPipelines=wrapper.wrapper(glGenProgramPipelines).setOutput(
    'pipelines',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGetProgramPipelineiv=wrapper.wrapper(glGetProgramPipelineiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glProgramUniform1iv.value size not checked against count
glProgramUniform1iv=wrapper.wrapper(glProgramUniform1iv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform1fv.value size not checked against count
glProgramUniform1fv=wrapper.wrapper(glProgramUniform1fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform1dv.value size not checked against count
glProgramUniform1dv=wrapper.wrapper(glProgramUniform1dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform1uiv.value size not checked against count
glProgramUniform1uiv=wrapper.wrapper(glProgramUniform1uiv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2iv.value size not checked against count*2
glProgramUniform2iv=wrapper.wrapper(glProgramUniform2iv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2fv.value size not checked against count*2
glProgramUniform2fv=wrapper.wrapper(glProgramUniform2fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2dv.value size not checked against count*2
glProgramUniform2dv=wrapper.wrapper(glProgramUniform2dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform2uiv.value size not checked against count*2
glProgramUniform2uiv=wrapper.wrapper(glProgramUniform2uiv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3iv.value size not checked against count*3
glProgramUniform3iv=wrapper.wrapper(glProgramUniform3iv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3fv.value size not checked against count*3
glProgramUniform3fv=wrapper.wrapper(glProgramUniform3fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3dv.value size not checked against count*3
glProgramUniform3dv=wrapper.wrapper(glProgramUniform3dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform3uiv.value size not checked against count*3
glProgramUniform3uiv=wrapper.wrapper(glProgramUniform3uiv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4iv.value size not checked against count*4
glProgramUniform4iv=wrapper.wrapper(glProgramUniform4iv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4fv.value size not checked against count*4
glProgramUniform4fv=wrapper.wrapper(glProgramUniform4fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4dv.value size not checked against count*4
glProgramUniform4dv=wrapper.wrapper(glProgramUniform4dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniform4uiv.value size not checked against count*4
glProgramUniform4uiv=wrapper.wrapper(glProgramUniform4uiv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2fv.value size not checked against count*4
glProgramUniformMatrix2fv=wrapper.wrapper(glProgramUniformMatrix2fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3fv.value size not checked against count*9
glProgramUniformMatrix3fv=wrapper.wrapper(glProgramUniformMatrix3fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4fv.value size not checked against count*16
glProgramUniformMatrix4fv=wrapper.wrapper(glProgramUniformMatrix4fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2dv.value size not checked against count*4
glProgramUniformMatrix2dv=wrapper.wrapper(glProgramUniformMatrix2dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3dv.value size not checked against count*9
glProgramUniformMatrix3dv=wrapper.wrapper(glProgramUniformMatrix3dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4dv.value size not checked against count*16
glProgramUniformMatrix4dv=wrapper.wrapper(glProgramUniformMatrix4dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x3fv.value size not checked against count*6
glProgramUniformMatrix2x3fv=wrapper.wrapper(glProgramUniformMatrix2x3fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x2fv.value size not checked against count*6
glProgramUniformMatrix3x2fv=wrapper.wrapper(glProgramUniformMatrix3x2fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x4fv.value size not checked against count*8
glProgramUniformMatrix2x4fv=wrapper.wrapper(glProgramUniformMatrix2x4fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x2fv.value size not checked against count*8
glProgramUniformMatrix4x2fv=wrapper.wrapper(glProgramUniformMatrix4x2fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x4fv.value size not checked against count*12
glProgramUniformMatrix3x4fv=wrapper.wrapper(glProgramUniformMatrix3x4fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x3fv.value size not checked against count*12
glProgramUniformMatrix4x3fv=wrapper.wrapper(glProgramUniformMatrix4x3fv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x3dv.value size not checked against count*6
glProgramUniformMatrix2x3dv=wrapper.wrapper(glProgramUniformMatrix2x3dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x2dv.value size not checked against count*6
glProgramUniformMatrix3x2dv=wrapper.wrapper(glProgramUniformMatrix3x2dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix2x4dv.value size not checked against count*8
glProgramUniformMatrix2x4dv=wrapper.wrapper(glProgramUniformMatrix2x4dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x2dv.value size not checked against count*8
glProgramUniformMatrix4x2dv=wrapper.wrapper(glProgramUniformMatrix4x2dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix3x4dv.value size not checked against count*12
glProgramUniformMatrix3x4dv=wrapper.wrapper(glProgramUniformMatrix3x4dv).setInputArraySize(
    'value', None
)
# INPUT glProgramUniformMatrix4x3dv.value size not checked against count*12
glProgramUniformMatrix4x3dv=wrapper.wrapper(glProgramUniformMatrix4x3dv).setInputArraySize(
    'value', None
)
glGetProgramPipelineInfoLog=wrapper.wrapper(glGetProgramPipelineInfoLog).setOutput(
    'infoLog',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'length',size=(1,),orPassIn=True
)
### END AUTOGENERATED SECTION