'''OpenGL extension NV.blend_equation_advanced

This module customises the behaviour of the 
OpenGL.raw.GL.NV.blend_equation_advanced to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension adds a number of "advanced" blending equations that can be
	used to perform new color blending operations, many of which are more
	complex than the standard blend modes provided by unextended OpenGL.  This
	extension provides two different extension string entries:
	
	- NV_blend_equation_advanced:  Provides the new blending equations, but
	  guarantees defined results only if each sample is touched no more than
	  once in any single rendering pass.  The command BlendBarrierNV() is
	  provided to indicate a boundary between passes.
	
	- NV_blend_equation_advanced_coherent:  Provides the new blending
	  equations, and guarantees that blending is done coherently and in API
	  primitive ordering.  An enable is provided to allow implementations to
	  opt out of fully coherent blending and instead behave as though only
	  NV_blend_equation_advanced were supported.
	
	Some implementations may support NV_blend_equation_advanced without
	supporting NV_blend_equation_advanced_coherent.
	
	In unextended OpenGL, the set of blending equations is limited, and can be
	expressed very simply.  The MIN and MAX blend equations simply compute
	component-wise minimums or maximums of source and destination color
	components.  The FUNC_ADD, FUNC_SUBTRACT, and FUNC_REVERSE_SUBTRACT
	multiply the source and destination colors by source and destination
	factors and either add the two products together or subtract one from the
	other.  This limited set of operations supports many common blending
	operations but precludes the use of more sophisticated transparency and
	blending operations commonly available in many dedicated imaging APIs.
	
	This extension provides a number of new "advanced" blending equations.
	Unlike traditional blending operations using the FUNC_ADD equation, these
	blending equations do not use source and destination factors specified by
	BlendFunc.  Instead, each blend equation specifies a complete equation
	based on the source and destination colors.  These new blend equations are
	used for both RGB and alpha components; they may not be used to perform
	separate RGB and alpha blending (via functions like
	BlendEquationSeparate).
	
	These blending operations are performed using premultiplied colors, where
	RGB colors stored in the framebuffer are considered to be multiplied by
	alpha (coverage).  The fragment color may be considered premultiplied or
	non-premultiplied, according the BLEND_PREMULTIPLIED_SRC_NV blending
	parameter (as specified by the new BlendParameteriNV function).  If
	fragment color is considered non-premultiplied, the (R,G,B) color
	components are multiplied by the alpha component prior to blending.  For
	non-premultiplied color components in the range [0,1], the corresponding
	premultiplied color component would have values in the range [0*A,1*A].
	
	Many of these advanced blending equations are formulated where the result
	of blending source and destination colors with partial coverage have three
	separate contributions:  from the portions covered by both the source and
	the destination, from the portion covered only by the source, and from the
	portion covered only by the destination.  The blend parameter
	BLEND_OVERLAP_NV can be used to specify a correlation between source and
	destination pixel coverage.  If set to CONJOINT_NV, the source and
	destination are considered to have maximal overlap, as would be the case
	if drawing two objects on top of each other.  If set to DISJOINT_NV, the
	source and destination are considered to have minimal overlap, as would be
	the case when rendering a complex polygon tessellated into individual
	non-intersecting triangles.  If set to UNCORRELATED_NV (default), the
	source and destination coverage are assumed to have no spatial correlation
	within the pixel.
	
	In addition to the coherency issues on implementations not supporting
	NV_blend_equation_advanced_coherent, this extension has several
	limitations worth noting.  First, the new blend equations are not
	supported while rendering to more than one color buffer at once; an
	INVALID_OPERATION will be generated if an application attempts to render
	any primitives in this unsupported configuration.  Additionally, blending
	precision may be limited to 16-bit floating-point, which could result in a
	loss of precision and dynamic range for framebuffer formats with 32-bit
	floating-point components, and in a loss of precision for formats with 12-
	and 16-bit signed or unsigned normalized integer components.

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/blend_equation_advanced.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.NV.blend_equation_advanced import *
from OpenGL.raw.GL.NV.blend_equation_advanced import _EXTENSION_NAME

def glInitBlendEquationAdvancedNV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION