'''OpenGL extension NV.register_combiners

This module customises the behaviour of the 
OpenGL.raw.GL.NV.register_combiners to provide a more 
Python-friendly API

Overview (from the spec)
	
	NVIDIA's next-generation graphics processor and its derivative
	designs support an extremely configurable mechanism know as "register
	combiners" for computing fragment colors.
	
	The register combiner mechanism is a significant redesign of NVIDIA's
	original TNT combiner mechanism as introduced by NVIDIA's RIVA
	TNT graphics processor.  Familiarity with the TNT combiners will
	help the reader appreciate the greatly enhanced register combiners
	functionality (see the NV_texture_env_combine4 OpenGL extension
	specification for this background).  The register combiner mechanism
	has the following enhanced functionality: 
	
	  The numeric range of combiner computations is from [-1,1]
	  (instead of TNT's [0,1] numeric range),
	
	  The set of available combiner inputs is expanded to include the
	  secondary color, fog color, fog factor, and a second combiner
	  constant color (TNT's available combiner inputs consist of
	  only zero, a single combiner constant color, the primary color,
	  texture 0, texture 1, and, in the case of combiner 1, the result
	  of combiner 0).
	
	  Each combiner variable input can be independently scaled and
	  biased into several possible numeric ranges (TNT can only
	  complement combiner inputs).
	
	  Each combiner stage computes three distinct outputs (instead
	  TNT's single combiner output).
	
	  The output operations include support for computing dot products
	  (TNT has no support for computing dot products).
	
	  After each output operation, there is a configurable scale and bias
	  applied (TNT's combiner operations builds in a scale and/or bias
	  into some of its combiner operations).
	
	  Each input variable for each combiner stage is fetched from any
	  entry in a combiner register set.  Moreover, the outputs of each
	  combiner stage are written into the register set of the subsequent
	  combiner stage (TNT could only use the result from combiner 0 as
	  a possible input to combiner 1; TNT lacks the notion of an
	  input/output register set).
	
	  The register combiner mechanism supports at least two general
	  combiner stages and then a special final combiner stage appropriate
	  for applying a color sum and fog computation (TNT provides two
	  simpler combiner stages, and TNT's color sum and fog stages are
	  hard-wired and not subsumed by the combiner mechanism as in register
	  combiners).
	
	The register combiners fit into the OpenGL pipeline as a rasterization
	processing stage operating in parallel to the traditional OpenGL
	texture environment, color sum, AND fog application.  Enabling this
	extension bypasses OpenGL's existing texture environment, color
	sum, and fog application processing and instead use the register
	combiners.  The combiner and texture environment state is orthogonal
	so modifying combiner state does not change the traditional OpenGL
	texture environment state and the texture environment state is
	ignored when combiners are enabled.
	
	OpenGL application developers can use the register combiner mechanism
	for very sophisticated shading techniques.  For example, an
	approximation of Blinn's bump mapping technique can be achieved with
	the combiner mechanism.  Additionally, multi-pass shading models
	that require several passes with unextended OpenGL 1.2 functionality
	can be implemented in several fewer passes with register combiners.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/register_combiners.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.NV.register_combiners import *
from OpenGL.raw.GL.NV.register_combiners import _EXTENSION_NAME

def glInitRegisterCombinersNV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glCombinerParameterfvNV.params size not checked against 'pname'
glCombinerParameterfvNV=wrapper.wrapper(glCombinerParameterfvNV).setInputArraySize(
    'params', None
)
# INPUT glCombinerParameterivNV.params size not checked against 'pname'
glCombinerParameterivNV=wrapper.wrapper(glCombinerParameterivNV).setInputArraySize(
    'params', None
)
glGetCombinerInputParameterfvNV=wrapper.wrapper(glGetCombinerInputParameterfvNV).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetCombinerInputParameterivNV=wrapper.wrapper(glGetCombinerInputParameterivNV).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetCombinerOutputParameterfvNV=wrapper.wrapper(glGetCombinerOutputParameterfvNV).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetCombinerOutputParameterivNV=wrapper.wrapper(glGetCombinerOutputParameterivNV).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetFinalCombinerInputParameterfvNV=wrapper.wrapper(glGetFinalCombinerInputParameterfvNV).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetFinalCombinerInputParameterivNV=wrapper.wrapper(glGetFinalCombinerInputParameterivNV).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
### END AUTOGENERATED SECTION