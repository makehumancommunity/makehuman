'''OpenGL extension ARB.gl_spirv

This module customises the behaviour of the 
OpenGL.raw.GL.ARB.gl_spirv to provide a more 
Python-friendly API

Overview (from the spec)
	
	This is version 100 of the GL_ARB_gl_spirv extension.
	
	This extension does two things:
	
	1. Allows a SPIR-V module to be specified as containing a programmable
	   shader stage, rather than using GLSL, whatever the source language
	   was used to create the SPIR-V module.
	
	2. Modifies GLSL to be a source language for creating SPIR-V modules
	   for OpenGL consumption. Such GLSL can be used to create such SPIR-V
	   modules, outside of the OpenGL runtime.
	
	Enabling GLSL SPIR-V Features
	-----------------------------
	
	This extension is not enabled with a #extension as other extensions are.
	It is also not enabled through use of a profile or #version.  The intended
	level of GLSL features comes from the traditional use of #version, profile,
	and #extension.
	
	Instead, use of this extension is an effect of using a GLSL front-end in a
	mode that has it generate SPIR-V for OpenGL.  Such tool use is outside the
	scope of using the OpenGL API and outside the definition of GLSL and this
	extension. See the documentation of the compiler to see how to request
	generation of SPIR-V for OpenGL.
	
	When a front-end is used to accept the GLSL features in this extension, it
	must error check and reject shaders not adhering to this specification, and
	accept those that do.  Implementation-dependent maximums and capabilities
	are supplied to, or part of, the front-end, so it can do error checking
	against them.
	
	A shader can query the level of GLSL SPIR-V support available, using the
	predefined
	
	    #define GL_SPIRV 100
	
	This allows shader code to say, for example,
	
	    #ifdef GL_SPIRV
	        layout(constant_id = 11) const int count = 4;
	        #if GL_SPIRV > 100
	            ...
	        #endif
	    #else
	        const int count = 6;
	    #endif
	
	SPIR-V Modules
	--------------
	
	An entire stage is held in a single SPIR-V module.  The SPIR-V model is
	that multiple (e.g., GLSL) compilation units forming a single stage
	in a high-level language are all compiled and linked together to form a
	single entry point (and its call tree) in a SPIR-V module.  This would be
	done prior to using the OpenGL API to create a program object containing the
	stage.
	
	The OpenGL API expects the SPIR-V module to have already been validated,
	and can return an error if it discovers anything invalid in
	the module.  An invalid SPIR-V module is allowed to result in undefined
	behavior.
	
	Specialization Constants
	------------------------
	
	SPIR-V specialization constants, which can be set later by the client API,
	can be declared using "layout(constant_id=...)". For example, to make a
	specialization constant with a default value of 12:
	
	    layout(constant_id = 17) const int arraySize = 12;
	
	Above, "17" is the ID by which the API or other tools can later refer to
	this specific specialization constant.  The API or an intermediate tool can
	then change its value to another constant integer before it is fully
	lowered to executable code.  If it is never changed before final lowering,
	it will retain the value of 12.
	
	Specialization constants have const semantics, except they don't fold.
	Hence, an array can be declared with 'arraySize' from above:
	
	    vec4 data[arraySize];  // legal, even though arraySize might change
	
	Specialization constants can be in expressions:
	
	    vec4 data2[arraySize + 2];
	
	This will make data2 be sized by 2 more than whatever constant value
	'arraySize' has when it is time to lower the shader to executable code.
	
	An expression formed with specialization constants also behaves in the
	shader like a specialization constant, not a like a constant.
	
	    arraySize + 2       // a specialization constant (with no constant_id)
	
	Such expressions can be used in the same places as a constant.
	
	The constant_id can only be applied to a scalar *int*, a scalar *float*
	or a scalar *bool*.
	
	Only basic operators and constructors can be applied to a specialization
	constant and still result in a specialization constant:
	
	    layout(constant_id = 17) const int arraySize = 12;
	    sin(float(arraySize));    // result is not a specialization constant
	
	While SPIR-V specialization constants are only for scalars, a vector
	can be made by operations on scalars:
	
	    layout(constant_id = 18) const int scX = 1;
	    layout(constant_id = 19) const int scZ = 1;
	    const vec3 scVec = vec3(scX, 1, scZ);  // partially specialized vector
	
	A built-in variable can have a 'constant_id' attached to it:
	
	    layout(constant_id = 18) gl_MaxImageUnits;
	
	This makes it behave as a specialization constant.  It is not a full
	redeclaration; all other characteristics are left intact from the
	original built-in declaration.
	
	The built-in vector gl_WorkGroupSize can be specialized using special
	layout local_size_{xyz}_id's applied to the "in" qualifier.  For example:
	
	    layout(local_size_x_id = 18, local_size_z_id = 19) in;
	
	This leaves gl_WorkGroupSize.y as a non-specialization constant, with
	gl_WorkGroupSize being a partially specialized vector.  Its x and z
	components can be later specialized using the ID's 18 and 19.
	
	gl_FragColor
	------------
	
	The fragment-stage built-in gl_FragColor, which implies a broadcast to all
	outputs, is not present in SPIR-V. Shaders where writing to gl_FragColor
	is allowed can still write to it, but it only means to write to an output:
	 - of the same type as gl_FragColor
	 - decorated with location 0
	 - not decorated as a built-in variable.
	There is no implicit broadcast.
	
	Mapping to SPIR-V
	-----------------
	
	For informational purposes (non-specification), the following is an
	expected way for an implementation to map GLSL constructs to SPIR-V
	constructs:
	
	Mapping of Storage Classes:
	
	  uniform sampler2D...;        -> UniformConstant
	  uniform variable (non-block) -> UniformConstant
	  uniform blockN { ... } ...;  -> Uniform, with Block decoration
	  in / out variable            -> Input/Output, possibly with block (below)
	  in / out block...            -> Input/Output, with Block decoration
	  buffer  blockN { ... } ...;  -> Uniform, with BufferBlock decoration
	  ... uniform atomic_uint ...  -> AtomicCounter
	  shared                       -> Workgroup
	  <normal global>              -> Private
	
	Mapping of input/output blocks or variables is the same for all versions
	of GLSL. To the extent variables or members are available in a
	version and a stage, its location is as follows:
	
	  These are mapped to SPIR-V individual variables, with similarly spelled
	  built-in decorations (except as noted):
	
	    General:
	
	        in gl_VertexID
	        in gl_InstanceID
	        in gl_InvocationID
	        in gl_PatchVerticesIn      (PatchVertices)
	        in gl_PrimitiveIDIn        (PrimitiveID)
	        in/out gl_PrimitiveID      (in/out based only on storage qualifier)
	        in gl_TessCoord
	
	        in/out gl_Layer
	        in/out gl_ViewportIndex
	
	        patch in/out gl_TessLevelOuter  (uses Patch decoration)
	        patch in/out gl_TessLevelInner  (uses Patch decoration)
	
	    Compute stage only:
	
	        in gl_NumWorkGroups
	        in gl_WorkGroupSize
	        in gl_WorkGroupID
	        in gl_LocalInvocationID
	        in gl_GlobalInvocationID
	        in gl_LocalInvocationIndex
	
	    Fragment stage only:
	
	        in gl_FragCoord
	        in gl_FrontFacing
	        in gl_ClipDistance
	        in gl_CullDistance
	        in gl_PointCoord
	        in gl_SampleID
	        in gl_SamplePosition
	        in gl_HelperInvocation
	        out gl_FragDepth
	        in gl_SampleMaskIn        (SampleMask)
	        out gl_SampleMask         (in/out based only on storage qualifier)
	
	  These are mapped to SPIR-V blocks, as implied by the pseudo code, with
	  the members decorated with similarly spelled built-in decorations:
	
	    Non-fragment stage:
	
	        in/out gl_PerVertex {  // some subset of these members will be used
	            gl_Position
	            gl_PointSize
	            gl_ClipDistance
	            gl_CullDistance
	        }                      // name of block is for debug only
	
	  There is at most one input and one output block per stage in SPIR-V.
	  The subset and order of members will match between stages sharing an
	  interface.
	
	Mapping of precise:
	
	  precise -> NoContraction
	
	Mapping of atomic_uint /offset/ layout qualifier
	
	  offset         ->  Offset (decoration)
	
	Mapping of images
	
	  imageLoad()   -> OpImageRead
	  imageStore()  -> OpImageWrite
	  texelFetch()  -> OpImageFetch
	
	  imageAtomicXXX(params, data)  -> %ptr = OpImageTexelPointer params
	                                          OpAtomicXXX %ptr, data
	
	  XXXQueryXXX(combined) -> %image = OpImage combined
	                                    OpXXXQueryXXX %image
	
	Mapping of layouts
	
	  std140/std430  ->  explicit *Offset*, *ArrayStride*, and *MatrixStride*
	                     Decoration on struct members
	  shared/packed  ->  not allowed
	  <default>      ->  not shared, but std140 or std430
	  xfb_offset     ->  *Offset* Decoration on the object or struct member
	  xfb_buffer     ->  *XfbBuffer* Decoration on the object
	  xfb_stride     ->  *XfbStride* Decoration on the object
	  any xfb_*      ->  the *Xfb* Execution Mode is set
	  captured XFB   ->  has both *XfbBuffer* and *Offset*
	  non-captured   ->  lacking *XfbBuffer* or *Offset*
	
	  max_vertices   ->  OutputVertices
	
	Mapping of barriers
	
	  barrier() (compute) -> OpControlBarrier(/*Execution*/Workgroup,
	                                          /*Memory*/Workgroup,
	                                          /*Semantics*/AcquireRelease |
	                                                       WorkgroupMemory)
	
	  barrier() (tess control) -> OpControlBarrier(/*Execution*/Workgroup,
	                                               /*Memory*/Invocation,
	                                               /*Semantics*/None)
	
	  memoryBarrier() -> OpMemoryBarrier(/*Memory*/Device,
	                                     /*Semantics*/AcquireRelease |
	                                                  UniformMemory |
	                                                  WorkgroupMemory |
	                                                  ImageMemory)
	
	  memoryBarrierBuffer() -> OpMemoryBarrier(/*Memory*/Device,
	                                           /*Semantics*/AcquireRelease |
	                                                        UniformMemory)
	
	  memoryBarrierShared() -> OpMemoryBarrier(/*Memory*/Device,
	                                           /*Semantics*/AcquireRelease |
	                                                        WorkgroupMemory)
	
	  memoryBarrierImage() -> OpMemoryBarrier(/*Memory*/Device,
	                                          /*Semantics*/AcquireRelease |
	                                                       ImageMemory)
	
	  groupMemoryBarrier() -> OpMemoryBarrier(/*Memory*/Workgroup,
	                                          /*Semantics*/AcquireRelease |
	                                                       UniformMemory |
	                                                       WorkgroupMemory |
	                                                       ImageMemory)
	
	Mapping of atomics
	
	  all atomic builtin functions -> Semantics = None(Relaxed)
	
	  atomicExchange()      -> OpAtomicExchange
	  imageAtomicExchange() -> OpAtomicExchange
	  atomicCompSwap()      -> OpAtomicCompareExchange
	  imageAtomicCompSwap() -> OpAtomicCompareExchange
	  NA                    -> OpAtomicCompareExchangeWeak
	
	  atomicCounterIncrement -> OpAtomicIIncrement
	  atomicCounterDecrement -> OpAtomicIDecrement (with post decrement)
	  atomicCounter          -> OpAtomicLoad
	
	Mapping of uniform initializers
	
	  Using the OpVariable initializer logic, but only from a constant
	  instruction (not a global one).
	
	Mapping of other instructions
	
	  %     -> OpUMod/OpSMod
	  mod() -> OpFMod
	  NA    -> OpSRem/OpFRem
	
	  pack/unpack (conversion)    -> pack/unpack in GLSL extended instructions
	  pack/unpack (no conversion) -> OpBitcast
	
	Differences Relative to Other Specifications
	--------------------------------------------
	
	The following summarizes the set of differences to existing specifications.
	
	Additional use of existing SPIR-V features, relative to Vulkan:
	  + The *UniformConstant* Storage Class can be used on individual
	    variables at global scope. (That is, uniforms don't have to be in a
	    block, unless they are built-in members that are in block in GLSL
	    version 4.5.)
	  + *AtomicCounter* Storage Class can use the *Offset* decoration
	  + OriginLowerLeft
	  + Uniforms support constant initializers.
	
	Corresponding features that GLSL keeps, despite GL_KHR_vulkan_glsl removal:
	  . default uniforms (those not inside a uniform block)
	  . atomic-counter bindings have the /offset/ layout qualifier
	  . special rules for locations for input doubles in the vertex shader
	  . origin_lower_left
	
	Addition of features to GLSL:
	  + specialization constants, as per GL_KHR_vulkan_glsl
	  + #define GL_SPIRV 100, when compiled for OpenGL and SPIR-V generation
	  + offset can organize members in a different order than declaration order
	
	Non-acceptance of SPIR-V features, relative to Vulkan:
	  - VertexIndex and InstanceIndex built-in decorations cannot be used
	  - Push-constant buffers cannot be used
	  - *DescriptorSet* must always be 0, if present
	  - input targets and input attachments
	  - OpTypeSampler
	
	Corresponding features not added to GLSL that GL_KHR_vulkan_glsl added:
	  . gl_VertexIndex and gl_InstanceIndex
	      (gl_VertexID and gl_InstanceID have same semantics as in GLSL)
	  . push_constant buffers
	  . descriptor sets
	  . input_attachment_index and accessing input targets
	  . shader-combining of textures and samplers
	
	Removal of features from GLSL, as removed by GL_KHR_vulkan_glsl:
	  - subroutines
	  - the already deprecated texturing functions (e.g., texture2D())
	  - the already deprecated noise functions (e.g., noise1())
	  - compatibility profile features
	  - gl_DepthRangeParameters and gl_NumSamples
	  - *shared* and *packed* block layouts
	
	Addition of features to The OpenGL Graphics System:
	  + a command to associate a SPIR-V module with a program (ShaderBinary)
	  + a command to select a SPIR-V entry point and set specialization
	    constants in a SPIR-V module (SpecializeShaderARB)
	  + a new appendix for SPIR-V validation rules, precision, etc.
	
	Changes of system features, relative to Vulkan:
	  . Vulkan uses only one binding point for a resource array, while OpenGL
	    still uses multiple binding points, so binding numbers are counted
	    differently for SPIR-V used in Vulkan and OpenGL
	  . gl_FragColor can be written to, but it won't broadcast, for versions of
	    OpenGL that support gl_FragColor
	  . Vulkan does not allow multi-dimensional arrays of resources like
	    UBOs and SSBOs in its SPIR-V environment spec. SPIR-V supports
	    it and OpenGL already allows this for GLSL shaders. SPIR-V
	    for OpenGL also allows it.
	
	Additions to the SPIR-V specification:
	  + *Offset* can also apply to an object, for transform feedback.
	  + *Offset* can also apply to a default uniform, for atomic_uint offset.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/ARB/gl_spirv.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.ARB.gl_spirv import *
from OpenGL.raw.GL.ARB.gl_spirv import _EXTENSION_NAME

def glInitGlSpirvARB():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION