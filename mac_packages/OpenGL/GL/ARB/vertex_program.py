'''OpenGL extension ARB.vertex_program

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.vertex_program to provide a more 
Python-friendly API

Overview (from the spec)
	
	Unextended OpenGL mandates a certain set of configurable per-vertex
	computations defining vertex transformation, texture coordinate generation
	and transformation, and lighting.  Several extensions have added further
	per-vertex computations to OpenGL.  For example, extensions have defined
	new texture coordinate generation modes (ARB_texture_cube_map,
	NV_texgen_reflection, NV_texgen_emboss), new vertex transformation modes
	(ARB_vertex_blend, EXT_vertex_weighting), new lighting modes (OpenGL 1.2's
	separate specular and rescale normal functionality), several modes for fog
	distance generation (NV_fog_distance), and eye-distance point size
	attenuation (EXT/ARB_point_parameters).
	
	Each such extension adds a small set of relatively inflexible
	per-vertex computations.
	
	This inflexibility is in contrast to the typical flexibility provided by
	the underlying programmable floating point engines (whether micro-coded
	vertex engines, DSPs, or CPUs) that are traditionally used to implement
	OpenGL's per-vertex computations.  The purpose of this extension is to
	expose to the OpenGL application writer a significant degree of per-vertex
	programmability for computing vertex parameters.
	
	For the purposes of discussing this extension, a vertex program is a
	sequence of floating-point 4-component vector operations that determines
	how a set of program parameters (defined outside of OpenGL's Begin/End
	pair) and an input set of per-vertex parameters are transformed to a set
	of per-vertex result parameters.
	
	The per-vertex computations for standard OpenGL given a particular set of
	lighting and texture coordinate generation modes (along with any state for
	extensions defining per-vertex computations) is, in essence, a vertex
	program.  However, the sequence of operations is defined implicitly by the
	current OpenGL state settings rather than defined explicitly as a sequence
	of instructions.
	
	This extension provides an explicit mechanism for defining vertex program
	instruction sequences for application-defined vertex programs.  In order
	to define such vertex programs, this extension defines a vertex
	programming model including a floating-point 4-component vector
	instruction set and a relatively large set of floating-point 4-component
	registers.
	
	The extension's vertex programming model is designed for efficient
	hardware implementation and to support a wide variety of vertex programs.
	By design, the entire set of existing vertex programs defined by existing
	OpenGL per-vertex computation extensions can be implemented using the
	extension's vertex programming model.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/vertex_program.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.vertex_program import *
from OpenGL.raw.GL.ARB.vertex_program import _EXTENSION_NAME

def glInitVertexProgramARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glVertexAttrib1dvARB=wrapper.wrapper(glVertexAttrib1dvARB).setInputArraySize(
    'v', 1
)
glVertexAttrib1fvARB=wrapper.wrapper(glVertexAttrib1fvARB).setInputArraySize(
    'v', 1
)
glVertexAttrib1svARB=wrapper.wrapper(glVertexAttrib1svARB).setInputArraySize(
    'v', 1
)
glVertexAttrib2dvARB=wrapper.wrapper(glVertexAttrib2dvARB).setInputArraySize(
    'v', 2
)
glVertexAttrib2fvARB=wrapper.wrapper(glVertexAttrib2fvARB).setInputArraySize(
    'v', 2
)
glVertexAttrib2svARB=wrapper.wrapper(glVertexAttrib2svARB).setInputArraySize(
    'v', 2
)
glVertexAttrib3dvARB=wrapper.wrapper(glVertexAttrib3dvARB).setInputArraySize(
    'v', 3
)
glVertexAttrib3fvARB=wrapper.wrapper(glVertexAttrib3fvARB).setInputArraySize(
    'v', 3
)
glVertexAttrib3svARB=wrapper.wrapper(glVertexAttrib3svARB).setInputArraySize(
    'v', 3
)
glVertexAttrib4NbvARB=wrapper.wrapper(glVertexAttrib4NbvARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4NivARB=wrapper.wrapper(glVertexAttrib4NivARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4NsvARB=wrapper.wrapper(glVertexAttrib4NsvARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4NubvARB=wrapper.wrapper(glVertexAttrib4NubvARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4NuivARB=wrapper.wrapper(glVertexAttrib4NuivARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4NusvARB=wrapper.wrapper(glVertexAttrib4NusvARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4bvARB=wrapper.wrapper(glVertexAttrib4bvARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4dvARB=wrapper.wrapper(glVertexAttrib4dvARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4fvARB=wrapper.wrapper(glVertexAttrib4fvARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4ivARB=wrapper.wrapper(glVertexAttrib4ivARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4svARB=wrapper.wrapper(glVertexAttrib4svARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4ubvARB=wrapper.wrapper(glVertexAttrib4ubvARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4uivARB=wrapper.wrapper(glVertexAttrib4uivARB).setInputArraySize(
    'v', 4
)
glVertexAttrib4usvARB=wrapper.wrapper(glVertexAttrib4usvARB).setInputArraySize(
    'v', 4
)
# INPUT glVertexAttribPointerARB.pointer size not checked against 'size,type,stride'
glVertexAttribPointerARB=wrapper.wrapper(glVertexAttribPointerARB).setInputArraySize(
    'pointer', None
)
# INPUT glProgramStringARB.string size not checked against len
glProgramStringARB=wrapper.wrapper(glProgramStringARB).setInputArraySize(
    'string', None
)
# INPUT glDeleteProgramsARB.programs size not checked against n
glDeleteProgramsARB=wrapper.wrapper(glDeleteProgramsARB).setInputArraySize(
    'programs', None
)
glGenProgramsARB=wrapper.wrapper(glGenProgramsARB).setOutput(
    'programs',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glProgramEnvParameter4dvARB=wrapper.wrapper(glProgramEnvParameter4dvARB).setInputArraySize(
    'params', 4
)
glProgramEnvParameter4fvARB=wrapper.wrapper(glProgramEnvParameter4fvARB).setInputArraySize(
    'params', 4
)
glProgramLocalParameter4dvARB=wrapper.wrapper(glProgramLocalParameter4dvARB).setInputArraySize(
    'params', 4
)
glProgramLocalParameter4fvARB=wrapper.wrapper(glProgramLocalParameter4fvARB).setInputArraySize(
    'params', 4
)
glGetProgramEnvParameterdvARB=wrapper.wrapper(glGetProgramEnvParameterdvARB).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetProgramEnvParameterfvARB=wrapper.wrapper(glGetProgramEnvParameterfvARB).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetProgramLocalParameterdvARB=wrapper.wrapper(glGetProgramLocalParameterdvARB).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetProgramLocalParameterfvARB=wrapper.wrapper(glGetProgramLocalParameterfvARB).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetProgramivARB=wrapper.wrapper(glGetProgramivARB).setOutput(
    'params',size=(1,),orPassIn=True
)
# OUTPUT glGetProgramStringARB.string COMPSIZE(target, pname) 
glGetVertexAttribdvARB=wrapper.wrapper(glGetVertexAttribdvARB).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetVertexAttribfvARB=wrapper.wrapper(glGetVertexAttribfvARB).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetVertexAttribivARB=wrapper.wrapper(glGetVertexAttribivARB).setOutput(
    'params',size=(4,),orPassIn=True
)
glGetVertexAttribPointervARB=wrapper.wrapper(glGetVertexAttribPointervARB).setOutput(
    'pointer',size=(1,),orPassIn=True
)
### END AUTOGENERATED SECTION
from OpenGL.lazywrapper import lazy as _lazy

from OpenGL import converters, error, contextdata
from OpenGL.arrays.arraydatatype import ArrayDatatype
# Note: sizes here are == the only documented sizes I could find,
# may need a lookup table some day...

@_lazy( glVertexAttribPointerARB )
def glVertexAttribPointerARB( 
    baseOperation, index, size, type,
    normalized, stride, pointer,
):
    """Set an attribute pointer for a given shader (index)
    
    index -- the index of the generic vertex to bind, see 
        glGetAttribLocation for retrieval of the value,
        note that index is a global variable, not per-shader
    size -- number of basic elements per record, 1,2,3, or 4
    type -- enum constant for data-type 
    normalized -- whether to perform int to float 
        normalization on integer-type values
    stride -- stride in machine units (bytes) between 
        consecutive records, normally used to create 
        "interleaved" arrays 
    pointer -- data-pointer which provides the data-values,
        normally a vertex-buffer-object or offset into the 
        same.
    
    This implementation stores a copy of the data-pointer 
    in the contextdata structure in order to prevent null-
    reference errors in the renderer.
    """
    array = ArrayDatatype.asArray( pointer, type )
    key = ('vertex-attrib',index)
    contextdata.setValue( key, array )
    return baseOperation(
        index, size, type,
        normalized, stride, 
        ArrayDatatype.voidDataPointer( array ) 
    )
