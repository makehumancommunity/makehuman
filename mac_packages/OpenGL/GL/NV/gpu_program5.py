'''OpenGL extension NV.gpu_program5

This module customises the behaviour of the 
OpenGL.raw.GL.NV.gpu_program5 to provide a more 
Python-friendly API

Overview (from the spec)
	
	This specification documents the common instruction set and basic
	functionality provided by NVIDIA's 5th generation of assembly instruction
	sets supporting programmable graphics pipeline stages.
	
	The instruction set builds upon the basic framework provided by the
	ARB_vertex_program and ARB_fragment_program extensions to expose
	considerably more capable hardware.  In addition to new capabilities for
	vertex and fragment programs, this extension provides new functionality
	for geometry programs as originally described in the NV_geometry_program4
	specification, and serves as the basis for the new tessellation control
	and evaluation programs described in the NV_tessellation_program5
	extension.
	
	Programs using the functionality provided by this extension should begin
	with the program headers "!!NVvp5.0" (vertex programs), "!!NVtcp5.0"
	(tessellation control programs), "!!NVtep5.0" (tessellation evaluation
	programs), "!!NVgp5.0" (geometry programs), and "!!NVfp5.0" (fragment
	programs).
	
	This extension provides a variety of new features, including:
	
	  * support for 64-bit integer operations;
	
	  * the ability to dynamically index into an array of texture units or
	    program parameter buffers;
	
	  * extending texel offset support to allow loading texel offsets from
	    regular integer operands computed at run-time, instead of requiring
	    that the offsets be constants encoded in texture instructions;
	
	  * extending TXG (texture gather) support to return the 2x2 footprint
	    from any component of the texture image instead of always returning
	    the first (x) component;
	
	  * extending TXG to support shadow comparisons in conjunction with a
	    depth texture, via the SHADOW* targets;
	
	  * further extending texture gather support to provide a new opcode
	    (TXGO) that applies a separate texel offset vector to each of the four
	    samples returned by the instruction; 
	
	  * bit manipulation instructions, including ones to find the position of
	    the most or least significant set bit, bitfield insertion and
	    extraction, and bit reversal;
	
	  * a general data conversion instruction (CVT) supporting conversion
	    between any two data types supported by this extension; and
	
	  * new instructions to compute the composite of a set of boolean
	    conditions a group of shader threads.
	
	This extension also provides some new capabilities for individual program
	types, including:
	
	  * support for instanced geometry programs, where a geometry program may
	    be run multiple times for each primitive;
	
	  * support for emitting vertices in a geometry program where each vertex
	    emitted may be directed at a specified vertex stream and captured
	    using the ARB_transform_feedback3 extension;
	
	  * support for interpolating an attribute at a programmable offset
	    relative to the pixel center (IPAO), at a programmable sample number
	    (IPAS), or at the fragment's centroid location (IPAC) in a fragment
	    program;
	
	  * support for reading a mask of covered samples in a fragment program;
	
	  * support for reading a point sprite coordinate directly in a fragment
	    program, without overriding a texture coordinate;
	
	  * support for reading patch primitives and per-patch attributes
	    (introduced by ARB_tessellation_shader) in a geometry program; and
	
	  * support for multiple output vectors for a single color output in a
	    fragment program (as used by ARB_blend_func_extended).
	
	This extension also provides optional support for 64-bit-per-component
	variables and 64-bit floating-point arithmetic.  These features are
	supported if and only if "NV_gpu_program_fp64" is found in the extension
	string.
	
	This extension incorporates the memory access operations from the
	NV_shader_buffer_load and NV_parameter_buffer_object2 extensions,
	originally built as add-ons to NV_gpu_program4.  It also provides the
	following new capabilities:
	
	  * support for the features without requiring a separate OPTION keyword;
	
	  * support for indexing into an array of constant buffers using the LDC
	    opcode added by NV_parameter_buffer_object2;
	
	  * support for storing into buffer objects at a specified GPU address
	    using the STORE opcode, an allowing applications to create READ_WRITE
	    and WRITE_ONLY mappings when making a buffer object resident using the
	    API mechanisms in the NV_shader_buffer_store extension;
	
	  * storage instruction modifiers to allow loading and storing 64-bit
	    component values;
	
	  * support for atomic memory transactions using the ATOM opcode, where
	    the instruction atomically reads the memory pointed to by a pointer,
	    performs a specified computation, stores the results of that
	    computation, and returns the original value read;
	
	  * support for memory barrier transactions using the MEMBAR opcode, which
	    ensures that all memory stores issued prior to the opcode complete
	    prior to any subsequent memory transactions; and
	
	  * a fragment program option to specify that depth and stencil tests are
	    performed prior to fragment program execution.
	
	Additionally, the assembly program languages supported by this extension
	include support for reading, writing, and performing atomic memory
	operations on texture image data using the opcodes and mechanisms
	documented in the "Dependencies on NV_gpu_program5" section of the
	EXT_shader_image_load_store extension.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/gpu_program5.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.NV.gpu_program5 import *
from OpenGL.raw.GL.NV.gpu_program5 import _EXTENSION_NAME

def glInitGpuProgram5NV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glProgramSubroutineParametersuivNV.params size not checked against count
glProgramSubroutineParametersuivNV=wrapper.wrapper(glProgramSubroutineParametersuivNV).setInputArraySize(
    'params', None
)
glGetProgramSubroutineParameteruivNV=wrapper.wrapper(glGetProgramSubroutineParameteruivNV).setOutput(
    'param',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
### END AUTOGENERATED SECTION