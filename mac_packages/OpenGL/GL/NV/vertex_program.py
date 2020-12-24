'''OpenGL extension NV.vertex_program

This module customises the behaviour of the 
OpenGL.raw.GL.NV.vertex_program to provide a more 
Python-friendly API

Overview (from the spec)
	
	Unextended OpenGL mandates a certain set of configurable per-vertex
	computations defining vertex transformation, texture coordinate
	generation and transformation, and lighting.  Several extensions
	have added further per-vertex computations to OpenGL.  For example,
	extensions have defined new texture coordinate generation modes
	(ARB_texture_cube_map, NV_texgen_reflection, NV_texgen_emboss), new
	vertex transformation modes (EXT_vertex_weighting), new lighting modes
	(OpenGL 1.2's separate specular and rescale normal functionality),
	several modes for fog distance generation (NV_fog_distance), and
	eye-distance point size attenuation (EXT_point_parameters).
	
	Each such extension adds a small set of relatively inflexible
	per-vertex computations.
	
	This inflexibility is in contrast to the typical flexibility provided
	by the underlying programmable floating point engines (whether
	micro-coded vertex engines, DSPs, or CPUs) that are traditionally used
	to implement OpenGL's per-vertex computations.  The purpose of this
	extension is to expose to the OpenGL application writer a significant
	degree of per-vertex programmability for computing vertex parameters.
	
	For the purposes of discussing this extension, a vertex program is
	a sequence of floating-point 4-component vector operations that
	determines how a set of program parameters (defined outside of
	OpenGL's begin/end pair) and an input set of per-vertex parameters
	are transformed to a set of per-vertex output parameters.
	
	The per-vertex computations for standard OpenGL given a particular
	set of lighting and texture coordinate generation modes (along with
	any state for extensions defining per-vertex computations) is, in
	essence, a vertex program.  However, the sequence of operations is
	defined implicitly by the current OpenGL state settings rather than
	defined explicitly as a sequence of instructions.
	
	This extension provides an explicit mechanism for defining vertex
	program instruction sequences for application-defined vertex programs.
	In order to define such vertex programs, this extension defines
	a vertex programming model including a floating-point 4-component
	vector instruction set and a relatively large set of floating-point
	4-component registers.
	
	The extension's vertex programming model is designed for efficient
	hardware implementation and to support a wide variety of vertex
	programs.  By design, the entire set of existing vertex programs
	defined by existing OpenGL per-vertex computation extensions can be
	implemented using the extension's vertex programming model.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/vertex_program.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.NV.vertex_program import *
from OpenGL.raw.GL.NV.vertex_program import _EXTENSION_NAME

def glInitVertexProgramNV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glAreProgramsResidentNV.programs size not checked against n
glAreProgramsResidentNV=wrapper.wrapper(glAreProgramsResidentNV).setInputArraySize(
    'programs', None
).setOutput(
    'residences',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
# INPUT glDeleteProgramsNV.programs size not checked against n
glDeleteProgramsNV=wrapper.wrapper(glDeleteProgramsNV).setInputArraySize(
    'programs', None
)
glExecuteProgramNV=wrapper.wrapper(glExecuteProgramNV).setInputArraySize(
    'params', 4
)
glGenProgramsNV=wrapper.wrapper(glGenProgramsNV).setOutput(
    'programs',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGetProgramParameterdvNV=wrapper.wrapper(glGetProgramParameterdvNV).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetProgramParameterfvNV=wrapper.wrapper(glGetProgramParameterfvNV).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetProgramivNV=wrapper.wrapper(glGetProgramivNV).setOutput(
    'params',size=(4,),orPassIn=True
)
# OUTPUT glGetProgramStringNV.program COMPSIZE(id, pname) 
glGetTrackMatrixivNV=wrapper.wrapper(glGetTrackMatrixivNV).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetVertexAttribdvNV=wrapper.wrapper(glGetVertexAttribdvNV).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetVertexAttribfvNV=wrapper.wrapper(glGetVertexAttribfvNV).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetVertexAttribivNV=wrapper.wrapper(glGetVertexAttribivNV).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetVertexAttribPointervNV=wrapper.wrapper(glGetVertexAttribPointervNV).setOutput(
    'pointer',size=(1,),orPassIn=True
)
# INPUT glLoadProgramNV.program size not checked against len
glLoadProgramNV=wrapper.wrapper(glLoadProgramNV).setInputArraySize(
    'program', None
)
glProgramParameter4dvNV=wrapper.wrapper(glProgramParameter4dvNV).setInputArraySize(
    'v', 4
)
glProgramParameter4fvNV=wrapper.wrapper(glProgramParameter4fvNV).setInputArraySize(
    'v', 4
)
# INPUT glProgramParameters4dvNV.v size not checked against count*4
glProgramParameters4dvNV=wrapper.wrapper(glProgramParameters4dvNV).setInputArraySize(
    'v', None
)
# INPUT glProgramParameters4fvNV.v size not checked against count*4
glProgramParameters4fvNV=wrapper.wrapper(glProgramParameters4fvNV).setInputArraySize(
    'v', None
)
# INPUT glRequestResidentProgramsNV.programs size not checked against n
glRequestResidentProgramsNV=wrapper.wrapper(glRequestResidentProgramsNV).setInputArraySize(
    'programs', None
)
# INPUT glVertexAttribPointerNV.pointer size not checked against 'fsize,type,stride'
glVertexAttribPointerNV=wrapper.wrapper(glVertexAttribPointerNV).setInputArraySize(
    'pointer', None
)
glVertexAttrib1dvNV=wrapper.wrapper(glVertexAttrib1dvNV).setInputArraySize(
    'v', 1
)
glVertexAttrib1fvNV=wrapper.wrapper(glVertexAttrib1fvNV).setInputArraySize(
    'v', 1
)
glVertexAttrib1svNV=wrapper.wrapper(glVertexAttrib1svNV).setInputArraySize(
    'v', 1
)
glVertexAttrib2dvNV=wrapper.wrapper(glVertexAttrib2dvNV).setInputArraySize(
    'v', 2
)
glVertexAttrib2fvNV=wrapper.wrapper(glVertexAttrib2fvNV).setInputArraySize(
    'v', 2
)
glVertexAttrib2svNV=wrapper.wrapper(glVertexAttrib2svNV).setInputArraySize(
    'v', 2
)
glVertexAttrib3dvNV=wrapper.wrapper(glVertexAttrib3dvNV).setInputArraySize(
    'v', 3
)
glVertexAttrib3fvNV=wrapper.wrapper(glVertexAttrib3fvNV).setInputArraySize(
    'v', 3
)
glVertexAttrib3svNV=wrapper.wrapper(glVertexAttrib3svNV).setInputArraySize(
    'v', 3
)
glVertexAttrib4dvNV=wrapper.wrapper(glVertexAttrib4dvNV).setInputArraySize(
    'v', 4
)
glVertexAttrib4fvNV=wrapper.wrapper(glVertexAttrib4fvNV).setInputArraySize(
    'v', 4
)
glVertexAttrib4svNV=wrapper.wrapper(glVertexAttrib4svNV).setInputArraySize(
    'v', 4
)
glVertexAttrib4ubvNV=wrapper.wrapper(glVertexAttrib4ubvNV).setInputArraySize(
    'v', 4
)
# INPUT glVertexAttribs1dvNV.v size not checked against count
glVertexAttribs1dvNV=wrapper.wrapper(glVertexAttribs1dvNV).setInputArraySize(
    'v', None
)
# INPUT glVertexAttribs1fvNV.v size not checked against count
glVertexAttribs1fvNV=wrapper.wrapper(glVertexAttribs1fvNV).setInputArraySize(
    'v', None
)
# INPUT glVertexAttribs1svNV.v size not checked against count
glVertexAttribs1svNV=wrapper.wrapper(glVertexAttribs1svNV).setInputArraySize(
    'v', None
)
# INPUT glVertexAttribs2dvNV.v size not checked against count*2
glVertexAttribs2dvNV=wrapper.wrapper(glVertexAttribs2dvNV).setInputArraySize(
    'v', None
)
# INPUT glVertexAttribs2fvNV.v size not checked against count*2
glVertexAttribs2fvNV=wrapper.wrapper(glVertexAttribs2fvNV).setInputArraySize(
    'v', None
)
# INPUT glVertexAttribs2svNV.v size not checked against count*2
glVertexAttribs2svNV=wrapper.wrapper(glVertexAttribs2svNV).setInputArraySize(
    'v', None
)
# INPUT glVertexAttribs3dvNV.v size not checked against count*3
glVertexAttribs3dvNV=wrapper.wrapper(glVertexAttribs3dvNV).setInputArraySize(
    'v', None
)
# INPUT glVertexAttribs3fvNV.v size not checked against count*3
glVertexAttribs3fvNV=wrapper.wrapper(glVertexAttribs3fvNV).setInputArraySize(
    'v', None
)
# INPUT glVertexAttribs3svNV.v size not checked against count*3
glVertexAttribs3svNV=wrapper.wrapper(glVertexAttribs3svNV).setInputArraySize(
    'v', None
)
# INPUT glVertexAttribs4dvNV.v size not checked against count*4
glVertexAttribs4dvNV=wrapper.wrapper(glVertexAttribs4dvNV).setInputArraySize(
    'v', None
)
# INPUT glVertexAttribs4fvNV.v size not checked against count*4
glVertexAttribs4fvNV=wrapper.wrapper(glVertexAttribs4fvNV).setInputArraySize(
    'v', None
)
# INPUT glVertexAttribs4svNV.v size not checked against count*4
glVertexAttribs4svNV=wrapper.wrapper(glVertexAttribs4svNV).setInputArraySize(
    'v', None
)
# INPUT glVertexAttribs4ubvNV.v size not checked against count*4
glVertexAttribs4ubvNV=wrapper.wrapper(glVertexAttribs4ubvNV).setInputArraySize(
    'v', None
)
### END AUTOGENERATED SECTION