'''OpenGL extension NV.texture_shader

This module customises the behaviour of the 
OpenGL.raw.GL.NV.texture_shader to provide a more 
Python-friendly API

Overview (from the spec)
	
	Standard OpenGL and the ARB_multitexture extension define a
	straightforward direct mechanism for mapping sets of texture
	coordinates to filtered colors.  This extension provides a more
	functional mechanism.
	
	OpenGL's standard texturing mechanism defines a set of texture
	targets.  Each texture target defines how the texture image
	is specified and accessed via a set of texture coordinates.
	OpenGL 1.0 defines the 1D and 2D texture targets.  OpenGL 1.2
	(and/or the EXT_texture3D extension) defines the 3D texture target.
	The ARB_texture_cube_map extension defines the cube map texture
	target.  Each texture unit's texture coordinate set is mapped to a
	color using the unit's highest priority enabled texture target.
	
	This extension introduces texture shader stages.  A sequence of
	texture shader stages provides a more flexible mechanism for mapping
	sets of texture coordinates to texture unit RGBA results than standard
	OpenGL.
	
	When the texture shader enable is on, the extension replaces the
	conventional OpenGL mechanism for mapping sets of texture coordinates
	to filtered colors with this extension's sequence of texture shader
	stages.  
	
	Each texture shader stage runs one of 21 canned texture shader
	programs.  These programs support conventional OpenGL texture
	mapping but also support dependent texture accesses, dot product
	texture programs, and special modes.  (3D texture mapping
	texture shader operations are NOT provided by this extension;
	3D texture mapping texture shader operations are added by the
	NV_texture_shader2 extension that is layered on this extension.
	See the NV_texture_shader2 specification.)
	
	To facilitate the new texture shader programs, this extension
	introduces several new texture formats and variations on existing
	formats.  Existing color texture formats are extended by introducing
	new signed variants.  Two new types of texture formats (beyond colors)
	are also introduced.  Texture offset groups encode two signed offsets,
	and optionally a magnitude or a magnitude and an intensity.  The new
	HILO (pronounced high-low) formats provide possibly signed, high
	precision (16-bit) two-component textures.
	
	Each program takes as input the stage's interpolated texture
	coordinate set (s,t,r,q).  Each program generates two results:
	a shader stage result that may be used as an input to subsequent
	shader stage programs, and a texture unit RGBA result that becomes the
	texture color used by the texture unit's texture environment function
	or becomes the initial value for the corresponding texture register
	for register combiners. The texture unit RGBA result is always
	an RGBA color, but the shader stage result may be one of an RGBA
	color, a HILO value, a texture offset group, a floating-point value,
	or an invalid result.  When both results are RGBA colors, the shader
	stage result and the texture unit RGBA result are usually identical
	(though not in all cases).
	
	Additionally, certain programs have a side-effect such as culling
	the fragment or replacing the fragment's depth value.
	
	The twenty-one programs are briefly described:
	
	<none>
	
	1.   NONE - Always generates a (0,0,0,0) texture unit RGBA result.
	     Equivalent to disabling all texture targets in conventional
	     OpenGL.
	
	<conventional textures>
	
	2.   TEXTURE_1D - Accesses a 1D texture via (s/q).
	
	3.   TEXTURE_2D - Accesses a 2D texture via (s/q,t/q).
	
	4.   TEXTURE_RECTANGLE_NV - Accesses a rectangular texture via (s/q,t/q).
	
	5.   TEXTURE_CUBE_MAP_ARB - Accesses a cube map texture via (s,t,r).
	
	<special modes>
	
	6.   PASS_THROUGH_NV - Converts a texture coordinate (s,t,r,q)
	     directly to a [0,1] clamped (r,g,b,a) texture unit RGBA result.
	
	7.   CULL_FRAGMENT_NV - Culls the fragment based on the whether each
	     (s,t,r,q) is "greater than or equal to zero" or "less than zero".
	
	<offset textures>
	
	8.   OFFSET_TEXTURE_2D_NV - Transforms the signed (ds,dt) components
	     of a previous texture unit by a 2x2 floating-point matrix and
	     then uses the result to offset the stage's texture coordinates
	     for a 2D non-projective texture.
	
	9.   OFFSET_TEXTURE_2D_SCALE_NV - Same as above except the magnitude
	     component of the previous texture unit result scales the red,
	     green, and blue components of the unsigned RGBA texture 2D
	     access.
	
	10.  OFFSET_TEXTURE_RECTANGLE_NV - Similar to OFFSET_TEXTURE_2D_NV
	     except that the texture access is into a rectangular
	     non-projective texture.
	
	11.  OFFSET_TEXTURE_RECTANGLE_SCALE_NV - Similar to
	     OFFSET_TEXTURE_2D_SCALE_NV except that the texture access is
	     into a rectangular non-projective texture.
	
	<dependent textures>
	
	12.  DEPENDENT_AR_TEXTURE_2D_NV - Converts the alpha and red
	     components of a previous shader result into an (s,t) texture
	     coordinate set to access a 2D non-projective texture.
	
	13.  DEPENDENT_GB_TEXTURE_2D_NV - Converts the green and blue
	     components of a previous shader result into an (s,t) texture
	     coordinate set to access a 2D non-projective texture.
	
	<dot product textures>
	
	14.  DOT_PRODUCT_NV - Computes the dot product of the texture
	     shader's texture coordinate set (s,t,r) with some mapping of the
	     components of a previous texture shader result.  The component
	     mapping depends on the type (RGBA or HILO) and signedness of
	     the stage's previous texture input.  Other dot product texture
	     programs use the result of this program to compose a texture
	     coordinate set for a dependent texture access.  The color result
	     is undefined.
	
	15.  DOT_PRODUCT_TEXTURE_2D_NV - When preceded by a DOT_PRODUCT_NV
	     program in the previous texture shader stage, computes a second
	     similar dot product and composes the two dot products into (s,t)
	     texture coordinate set to access a 2D non-projective texture.
	
	16.  DOT_PRODUCT_TEXTURE_RECTANGLE_NV - Similar to
	     DOT_PRODUCT_TEXTURE_2D_NV except that the texture acces is into
	     a rectangular non-projective texture.  
	
	17.  DOT_PRODUCT_TEXTURE_CUBE_MAP_NV - When preceded by two
	     DOT_PRODUCT_NV programs in the previous two texture shader
	     stages, computes a third similar dot product and composes the
	     three dot products into (s,t,r) texture coordinate set to access
	     a cube map texture.
	
	18.  DOT_PRODUCT_REFLECT_CUBE_MAP_NV - When preceded by two
	     DOT_PRODUCT_NV programs in the previous two texture shader
	     stages, computes a third similar dot product and composes the
	     three dot products into a normal vector (Nx,Ny,Nz).  An eye
	     vector (Ex,Ey,Ez) is composed from the q texture coordinates of
	     the three stages.  A reflection vector (Rx,Ry,Rz) is computed
	     based on the normal and eye vectors.  The reflection vector
	     forms an (s,t,r) texture coordinate set to access a cube map
	     texture.
	
	19.  DOT_PRODUCT_CONST_EYE_REFLECT_CUBE_MAP_NV - Operates like
	     DOT_PRODUCT_REFLECT_CUBE_MAP_NV except that the eye vector
	     (Ex,Ey,Ez) is a user-defined constant rather than composed from
	     the q coordinates of the three stages.
	
	20.  DOT_PRODUCT_DIFFUSE_CUBE_MAP_NV - When used instead of the second
	     DOT_PRODUCT_NV program preceding
	     a DOT_PRODUCT_REFLECT_CUBE_MAP_NV or
	     DOT_PRODUCT_CONST_EYE_REFLECT_CUBE_MAP_NV stage, the normal
	     vector forms an (s,t,r) texture  coordinate set to access a
	     cube map texture.
	
	<dot product depth replace>
	
	21.  DOT_PRODUCT_DEPTH_REPLACE_NV - When preceded by a DOT_PRODUCT_NV
	     program in the previous texture shader stage, computes a second
	     similar dot product and replaces the fragment's window-space
	     depth value with the first dot product results divided by
	     the second.  The texture unit RGBA result is (0,0,0,0).

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/texture_shader.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.NV.texture_shader import *
from OpenGL.raw.GL.NV.texture_shader import _EXTENSION_NAME

def glInitTextureShaderNV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION
GL_OFFSET_TEXTURE_2D_BIAS_NV = GL_OFFSET_TEXTURE_BIAS_NV # alias
GL_OFFSET_TEXTURE_2D_MATRIX_NV = GL_OFFSET_TEXTURE_MATRIX_NV # alias
GL_OFFSET_TEXTURE_2D_SCALE_NV = GL_OFFSET_TEXTURE_SCALE_NV # alias
