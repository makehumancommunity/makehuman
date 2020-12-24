'''OpenGL extension OES.fixed_point

This module customises the behaviour of the 
OpenGL.raw.GLES1.OES.fixed_point to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides the capability, for platforms that do
	not have efficient floating-point support, to input data in a
	fixed-point format, i.e.,  a scaled-integer format.  There are
	several ways a platform could try to solve the problem, such as
	using integer only commands, but there are many OpenGL commands
	that have only floating-point or double-precision floating-point
	parameters.  Also, it is likely that any credible application
	running on such a platform will need to perform some computations
	and will already be using some form of fixed-point representation.
	This extension solves the problem by adding new ``fixed', and
	``clamp fixed''  data types based on a a two's complement
	S15.16 representation.  New versions of commands are created
	with an 'x' suffix that take fixed or clampx parameters.
	

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/OES/fixed_point.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES1 import _types, _glgets
from OpenGL.raw.GLES1.OES.fixed_point import *
from OpenGL.raw.GLES1.OES.fixed_point import _EXTENSION_NAME

def glInitFixedPointOES():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

glClipPlanexOES=wrapper.wrapper(glClipPlanexOES).setInputArraySize(
    'equation', 4
)
# INPUT glFogxvOES.param size not checked against 'pname'
glFogxvOES=wrapper.wrapper(glFogxvOES).setInputArraySize(
    'param', None
)
glGetClipPlanexOES=wrapper.wrapper(glGetClipPlanexOES).setOutput(
    'equation',size=(4,),orPassIn=True
)
glGetFixedvOES=wrapper.wrapper(glGetFixedvOES).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexEnvxvOES=wrapper.wrapper(glGetTexEnvxvOES).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexParameterxvOES=wrapper.wrapper(glGetTexParameterxvOES).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glLightModelxvOES.param size not checked against 'pname'
glLightModelxvOES=wrapper.wrapper(glLightModelxvOES).setInputArraySize(
    'param', None
)
# INPUT glLightxvOES.params size not checked against 'pname'
glLightxvOES=wrapper.wrapper(glLightxvOES).setInputArraySize(
    'params', None
)
glLoadMatrixxOES=wrapper.wrapper(glLoadMatrixxOES).setInputArraySize(
    'm', 16
)
# INPUT glMaterialxvOES.param size not checked against 'pname'
glMaterialxvOES=wrapper.wrapper(glMaterialxvOES).setInputArraySize(
    'param', None
)
glMultMatrixxOES=wrapper.wrapper(glMultMatrixxOES).setInputArraySize(
    'm', 16
)
# INPUT glPointParameterxvOES.params size not checked against 'pname'
glPointParameterxvOES=wrapper.wrapper(glPointParameterxvOES).setInputArraySize(
    'params', None
)
# INPUT glTexEnvxvOES.params size not checked against 'pname'
glTexEnvxvOES=wrapper.wrapper(glTexEnvxvOES).setInputArraySize(
    'params', None
)
# INPUT glTexParameterxvOES.params size not checked against 'pname'
glTexParameterxvOES=wrapper.wrapper(glTexParameterxvOES).setInputArraySize(
    'params', None
)
# INPUT glGetLightxvOES.params size not checked against 'pname'
glGetLightxvOES=wrapper.wrapper(glGetLightxvOES).setInputArraySize(
    'params', None
)
# INPUT glGetMaterialxvOES.params size not checked against 'pname'
glGetMaterialxvOES=wrapper.wrapper(glGetMaterialxvOES).setInputArraySize(
    'params', None
)
# INPUT glBitmapxOES.bitmap size not checked against 'width,height'
glBitmapxOES=wrapper.wrapper(glBitmapxOES).setInputArraySize(
    'bitmap', None
)
glColor3xvOES=wrapper.wrapper(glColor3xvOES).setInputArraySize(
    'components', 3
)
glColor4xvOES=wrapper.wrapper(glColor4xvOES).setInputArraySize(
    'components', 4
)
# INPUT glConvolutionParameterxvOES.params size not checked against 'pname'
glConvolutionParameterxvOES=wrapper.wrapper(glConvolutionParameterxvOES).setInputArraySize(
    'params', None
)
glEvalCoord1xvOES=wrapper.wrapper(glEvalCoord1xvOES).setInputArraySize(
    'coords', 1
)
glEvalCoord2xvOES=wrapper.wrapper(glEvalCoord2xvOES).setInputArraySize(
    'coords', 2
)
# INPUT glFeedbackBufferxOES.buffer size not checked against n
glFeedbackBufferxOES=wrapper.wrapper(glFeedbackBufferxOES).setInputArraySize(
    'buffer', None
)
glGetConvolutionParameterxvOES=wrapper.wrapper(glGetConvolutionParameterxvOES).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetHistogramParameterxvOES=wrapper.wrapper(glGetHistogramParameterxvOES).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetLightxOES=wrapper.wrapper(glGetLightxOES).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetMapxvOES=wrapper.wrapper(glGetMapxvOES).setOutput(
    'v',size=_glgets._glget_size_mapping,pnameArg='query',orPassIn=True
)
glGetPixelMapxv=wrapper.wrapper(glGetPixelMapxv).setOutput(
    'values',size=lambda x:(x,),pnameArg='size',orPassIn=True
)
glGetTexGenxvOES=wrapper.wrapper(glGetTexGenxvOES).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexLevelParameterxvOES=wrapper.wrapper(glGetTexLevelParameterxvOES).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glIndexxvOES=wrapper.wrapper(glIndexxvOES).setInputArraySize(
    'component', 1
)
glLoadTransposeMatrixxOES=wrapper.wrapper(glLoadTransposeMatrixxOES).setInputArraySize(
    'm', 16
)
glMultTransposeMatrixxOES=wrapper.wrapper(glMultTransposeMatrixxOES).setInputArraySize(
    'm', 16
)
glMultiTexCoord1xvOES=wrapper.wrapper(glMultiTexCoord1xvOES).setInputArraySize(
    'coords', 1
)
glMultiTexCoord2xvOES=wrapper.wrapper(glMultiTexCoord2xvOES).setInputArraySize(
    'coords', 2
)
glMultiTexCoord3xvOES=wrapper.wrapper(glMultiTexCoord3xvOES).setInputArraySize(
    'coords', 3
)
glMultiTexCoord4xvOES=wrapper.wrapper(glMultiTexCoord4xvOES).setInputArraySize(
    'coords', 4
)
glNormal3xvOES=wrapper.wrapper(glNormal3xvOES).setInputArraySize(
    'coords', 3
)
# INPUT glPixelMapx.values size not checked against size
glPixelMapx=wrapper.wrapper(glPixelMapx).setInputArraySize(
    'values', None
)
# INPUT glPrioritizeTexturesxOES.priorities size not checked against n
# INPUT glPrioritizeTexturesxOES.textures size not checked against n
glPrioritizeTexturesxOES=wrapper.wrapper(glPrioritizeTexturesxOES).setInputArraySize(
    'priorities', None
).setInputArraySize(
    'textures', None
)
glRasterPos2xvOES=wrapper.wrapper(glRasterPos2xvOES).setInputArraySize(
    'coords', 2
)
glRasterPos3xvOES=wrapper.wrapper(glRasterPos3xvOES).setInputArraySize(
    'coords', 3
)
glRasterPos4xvOES=wrapper.wrapper(glRasterPos4xvOES).setInputArraySize(
    'coords', 4
)
glRectxvOES=wrapper.wrapper(glRectxvOES).setInputArraySize(
    'v1', 2
).setInputArraySize(
    'v2', 2
)
glTexCoord1xvOES=wrapper.wrapper(glTexCoord1xvOES).setInputArraySize(
    'coords', 1
)
glTexCoord2xvOES=wrapper.wrapper(glTexCoord2xvOES).setInputArraySize(
    'coords', 2
)
glTexCoord3xvOES=wrapper.wrapper(glTexCoord3xvOES).setInputArraySize(
    'coords', 3
)
glTexCoord4xvOES=wrapper.wrapper(glTexCoord4xvOES).setInputArraySize(
    'coords', 4
)
# INPUT glTexGenxvOES.params size not checked against 'pname'
glTexGenxvOES=wrapper.wrapper(glTexGenxvOES).setInputArraySize(
    'params', None
)
glVertex2xvOES=wrapper.wrapper(glVertex2xvOES).setInputArraySize(
    'coords', 2
)
glVertex3xvOES=wrapper.wrapper(glVertex3xvOES).setInputArraySize(
    'coords', 3
)
glVertex4xvOES=wrapper.wrapper(glVertex4xvOES).setInputArraySize(
    'coords', 4
)
### END AUTOGENERATED SECTION