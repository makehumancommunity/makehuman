'''OpenGL extension VERSION.GL_1_0

This module customises the behaviour of the 
OpenGL.raw.GL.VERSION.GL_1_0 to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/VERSION/GL_1_0.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.VERSION.GL_1_0 import *
from OpenGL.raw.GL.VERSION.GL_1_0 import _EXTENSION_NAME

def glInitGl10VERSION():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glTexParameterfv.params size not checked against 'pname'
glTexParameterfv=wrapper.wrapper(glTexParameterfv).setInputArraySize(
    'params', None
)
# INPUT glTexParameteriv.params size not checked against 'pname'
glTexParameteriv=wrapper.wrapper(glTexParameteriv).setInputArraySize(
    'params', None
)
# INPUT glTexImage1D.pixels size not checked against 'format,type,width'
glTexImage1D=wrapper.wrapper(glTexImage1D).setInputArraySize(
    'pixels', None
)
# INPUT glTexImage2D.pixels size not checked against 'format,type,width,height'
glTexImage2D=wrapper.wrapper(glTexImage2D).setInputArraySize(
    'pixels', None
)
# OUTPUT glReadPixels.pixels COMPSIZE(format, type, width, height) 
glGetBooleanv=wrapper.wrapper(glGetBooleanv).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetDoublev=wrapper.wrapper(glGetDoublev).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetFloatv=wrapper.wrapper(glGetFloatv).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetIntegerv=wrapper.wrapper(glGetIntegerv).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# OUTPUT glGetTexImage.pixels COMPSIZE(target, level, format, type) 
glGetTexParameterfv=wrapper.wrapper(glGetTexParameterfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexParameteriv=wrapper.wrapper(glGetTexParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexLevelParameterfv=wrapper.wrapper(glGetTexLevelParameterfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexLevelParameteriv=wrapper.wrapper(glGetTexLevelParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glCallLists.lists size not checked against 'n,type'
glCallLists=wrapper.wrapper(glCallLists).setInputArraySize(
    'lists', None
)
# INPUT glBitmap.bitmap size not checked against 'width,height'
glBitmap=wrapper.wrapper(glBitmap).setInputArraySize(
    'bitmap', None
)
glColor3bv=wrapper.wrapper(glColor3bv).setInputArraySize(
    'v', 3
)
glColor3dv=wrapper.wrapper(glColor3dv).setInputArraySize(
    'v', 3
)
glColor3fv=wrapper.wrapper(glColor3fv).setInputArraySize(
    'v', 3
)
glColor3iv=wrapper.wrapper(glColor3iv).setInputArraySize(
    'v', 3
)
glColor3sv=wrapper.wrapper(glColor3sv).setInputArraySize(
    'v', 3
)
glColor3ubv=wrapper.wrapper(glColor3ubv).setInputArraySize(
    'v', 3
)
glColor3uiv=wrapper.wrapper(glColor3uiv).setInputArraySize(
    'v', 3
)
glColor3usv=wrapper.wrapper(glColor3usv).setInputArraySize(
    'v', 3
)
glColor4bv=wrapper.wrapper(glColor4bv).setInputArraySize(
    'v', 4
)
glColor4dv=wrapper.wrapper(glColor4dv).setInputArraySize(
    'v', 4
)
glColor4fv=wrapper.wrapper(glColor4fv).setInputArraySize(
    'v', 4
)
glColor4iv=wrapper.wrapper(glColor4iv).setInputArraySize(
    'v', 4
)
glColor4sv=wrapper.wrapper(glColor4sv).setInputArraySize(
    'v', 4
)
glColor4ubv=wrapper.wrapper(glColor4ubv).setInputArraySize(
    'v', 4
)
glColor4uiv=wrapper.wrapper(glColor4uiv).setInputArraySize(
    'v', 4
)
glColor4usv=wrapper.wrapper(glColor4usv).setInputArraySize(
    'v', 4
)
glEdgeFlagv=wrapper.wrapper(glEdgeFlagv).setInputArraySize(
    'flag', 1
)
glIndexdv=wrapper.wrapper(glIndexdv).setInputArraySize(
    'c', 1
)
glIndexfv=wrapper.wrapper(glIndexfv).setInputArraySize(
    'c', 1
)
glIndexiv=wrapper.wrapper(glIndexiv).setInputArraySize(
    'c', 1
)
glIndexsv=wrapper.wrapper(glIndexsv).setInputArraySize(
    'c', 1
)
glNormal3bv=wrapper.wrapper(glNormal3bv).setInputArraySize(
    'v', 3
)
glNormal3dv=wrapper.wrapper(glNormal3dv).setInputArraySize(
    'v', 3
)
glNormal3fv=wrapper.wrapper(glNormal3fv).setInputArraySize(
    'v', 3
)
glNormal3iv=wrapper.wrapper(glNormal3iv).setInputArraySize(
    'v', 3
)
glNormal3sv=wrapper.wrapper(glNormal3sv).setInputArraySize(
    'v', 3
)
glRasterPos2dv=wrapper.wrapper(glRasterPos2dv).setInputArraySize(
    'v', 2
)
glRasterPos2fv=wrapper.wrapper(glRasterPos2fv).setInputArraySize(
    'v', 2
)
glRasterPos2iv=wrapper.wrapper(glRasterPos2iv).setInputArraySize(
    'v', 2
)
glRasterPos2sv=wrapper.wrapper(glRasterPos2sv).setInputArraySize(
    'v', 2
)
glRasterPos3dv=wrapper.wrapper(glRasterPos3dv).setInputArraySize(
    'v', 3
)
glRasterPos3fv=wrapper.wrapper(glRasterPos3fv).setInputArraySize(
    'v', 3
)
glRasterPos3iv=wrapper.wrapper(glRasterPos3iv).setInputArraySize(
    'v', 3
)
glRasterPos3sv=wrapper.wrapper(glRasterPos3sv).setInputArraySize(
    'v', 3
)
glRasterPos4dv=wrapper.wrapper(glRasterPos4dv).setInputArraySize(
    'v', 4
)
glRasterPos4fv=wrapper.wrapper(glRasterPos4fv).setInputArraySize(
    'v', 4
)
glRasterPos4iv=wrapper.wrapper(glRasterPos4iv).setInputArraySize(
    'v', 4
)
glRasterPos4sv=wrapper.wrapper(glRasterPos4sv).setInputArraySize(
    'v', 4
)
glRectdv=wrapper.wrapper(glRectdv).setInputArraySize(
    'v1', 2
).setInputArraySize(
    'v2', 2
)
glRectfv=wrapper.wrapper(glRectfv).setInputArraySize(
    'v1', 2
).setInputArraySize(
    'v2', 2
)
glRectiv=wrapper.wrapper(glRectiv).setInputArraySize(
    'v1', 2
).setInputArraySize(
    'v2', 2
)
glRectsv=wrapper.wrapper(glRectsv).setInputArraySize(
    'v1', 2
).setInputArraySize(
    'v2', 2
)
glTexCoord1dv=wrapper.wrapper(glTexCoord1dv).setInputArraySize(
    'v', 1
)
glTexCoord1fv=wrapper.wrapper(glTexCoord1fv).setInputArraySize(
    'v', 1
)
glTexCoord1iv=wrapper.wrapper(glTexCoord1iv).setInputArraySize(
    'v', 1
)
glTexCoord1sv=wrapper.wrapper(glTexCoord1sv).setInputArraySize(
    'v', 1
)
glTexCoord2dv=wrapper.wrapper(glTexCoord2dv).setInputArraySize(
    'v', 2
)
glTexCoord2fv=wrapper.wrapper(glTexCoord2fv).setInputArraySize(
    'v', 2
)
glTexCoord2iv=wrapper.wrapper(glTexCoord2iv).setInputArraySize(
    'v', 2
)
glTexCoord2sv=wrapper.wrapper(glTexCoord2sv).setInputArraySize(
    'v', 2
)
glTexCoord3dv=wrapper.wrapper(glTexCoord3dv).setInputArraySize(
    'v', 3
)
glTexCoord3fv=wrapper.wrapper(glTexCoord3fv).setInputArraySize(
    'v', 3
)
glTexCoord3iv=wrapper.wrapper(glTexCoord3iv).setInputArraySize(
    'v', 3
)
glTexCoord3sv=wrapper.wrapper(glTexCoord3sv).setInputArraySize(
    'v', 3
)
glTexCoord4dv=wrapper.wrapper(glTexCoord4dv).setInputArraySize(
    'v', 4
)
glTexCoord4fv=wrapper.wrapper(glTexCoord4fv).setInputArraySize(
    'v', 4
)
glTexCoord4iv=wrapper.wrapper(glTexCoord4iv).setInputArraySize(
    'v', 4
)
glTexCoord4sv=wrapper.wrapper(glTexCoord4sv).setInputArraySize(
    'v', 4
)
glVertex2dv=wrapper.wrapper(glVertex2dv).setInputArraySize(
    'v', 2
)
glVertex2fv=wrapper.wrapper(glVertex2fv).setInputArraySize(
    'v', 2
)
glVertex2iv=wrapper.wrapper(glVertex2iv).setInputArraySize(
    'v', 2
)
glVertex2sv=wrapper.wrapper(glVertex2sv).setInputArraySize(
    'v', 2
)
glVertex3dv=wrapper.wrapper(glVertex3dv).setInputArraySize(
    'v', 3
)
glVertex3fv=wrapper.wrapper(glVertex3fv).setInputArraySize(
    'v', 3
)
glVertex3iv=wrapper.wrapper(glVertex3iv).setInputArraySize(
    'v', 3
)
glVertex3sv=wrapper.wrapper(glVertex3sv).setInputArraySize(
    'v', 3
)
glVertex4dv=wrapper.wrapper(glVertex4dv).setInputArraySize(
    'v', 4
)
glVertex4fv=wrapper.wrapper(glVertex4fv).setInputArraySize(
    'v', 4
)
glVertex4iv=wrapper.wrapper(glVertex4iv).setInputArraySize(
    'v', 4
)
glVertex4sv=wrapper.wrapper(glVertex4sv).setInputArraySize(
    'v', 4
)
glClipPlane=wrapper.wrapper(glClipPlane).setInputArraySize(
    'equation', 4
)
# INPUT glFogfv.params size not checked against 'pname'
glFogfv=wrapper.wrapper(glFogfv).setInputArraySize(
    'params', None
)
# INPUT glFogiv.params size not checked against 'pname'
glFogiv=wrapper.wrapper(glFogiv).setInputArraySize(
    'params', None
)
# INPUT glLightfv.params size not checked against 'pname'
glLightfv=wrapper.wrapper(glLightfv).setInputArraySize(
    'params', None
)
# INPUT glLightiv.params size not checked against 'pname'
glLightiv=wrapper.wrapper(glLightiv).setInputArraySize(
    'params', None
)
# INPUT glLightModelfv.params size not checked against 'pname'
glLightModelfv=wrapper.wrapper(glLightModelfv).setInputArraySize(
    'params', None
)
# INPUT glLightModeliv.params size not checked against 'pname'
glLightModeliv=wrapper.wrapper(glLightModeliv).setInputArraySize(
    'params', None
)
# INPUT glMaterialfv.params size not checked against 'pname'
glMaterialfv=wrapper.wrapper(glMaterialfv).setInputArraySize(
    'params', None
)
# INPUT glMaterialiv.params size not checked against 'pname'
glMaterialiv=wrapper.wrapper(glMaterialiv).setInputArraySize(
    'params', None
)
# INPUT glPolygonStipple.mask size not checked against ''
glPolygonStipple=wrapper.wrapper(glPolygonStipple).setInputArraySize(
    'mask', None
)
# INPUT glTexEnvfv.params size not checked against 'pname'
glTexEnvfv=wrapper.wrapper(glTexEnvfv).setInputArraySize(
    'params', None
)
# INPUT glTexEnviv.params size not checked against 'pname'
glTexEnviv=wrapper.wrapper(glTexEnviv).setInputArraySize(
    'params', None
)
# INPUT glTexGendv.params size not checked against 'pname'
glTexGendv=wrapper.wrapper(glTexGendv).setInputArraySize(
    'params', None
)
# INPUT glTexGenfv.params size not checked against 'pname'
glTexGenfv=wrapper.wrapper(glTexGenfv).setInputArraySize(
    'params', None
)
# INPUT glTexGeniv.params size not checked against 'pname'
glTexGeniv=wrapper.wrapper(glTexGeniv).setInputArraySize(
    'params', None
)
glFeedbackBuffer=wrapper.wrapper(glFeedbackBuffer).setOutput(
    'buffer',size=lambda x:(x,),pnameArg='size',orPassIn=True
)
glSelectBuffer=wrapper.wrapper(glSelectBuffer).setOutput(
    'buffer',size=lambda x:(x,),pnameArg='size',orPassIn=True
)
# INPUT glMap1d.points size not checked against 'target,stride,order'
glMap1d=wrapper.wrapper(glMap1d).setInputArraySize(
    'points', None
)
# INPUT glMap1f.points size not checked against 'target,stride,order'
glMap1f=wrapper.wrapper(glMap1f).setInputArraySize(
    'points', None
)
# INPUT glMap2d.points size not checked against 'target,ustride,uorder,vstride,vorder'
glMap2d=wrapper.wrapper(glMap2d).setInputArraySize(
    'points', None
)
# INPUT glMap2f.points size not checked against 'target,ustride,uorder,vstride,vorder'
glMap2f=wrapper.wrapper(glMap2f).setInputArraySize(
    'points', None
)
glEvalCoord1dv=wrapper.wrapper(glEvalCoord1dv).setInputArraySize(
    'u', 1
)
glEvalCoord1fv=wrapper.wrapper(glEvalCoord1fv).setInputArraySize(
    'u', 1
)
glEvalCoord2dv=wrapper.wrapper(glEvalCoord2dv).setInputArraySize(
    'u', 2
)
glEvalCoord2fv=wrapper.wrapper(glEvalCoord2fv).setInputArraySize(
    'u', 2
)
# INPUT glPixelMapfv.values size not checked against mapsize
glPixelMapfv=wrapper.wrapper(glPixelMapfv).setInputArraySize(
    'values', None
)
# INPUT glPixelMapuiv.values size not checked against mapsize
glPixelMapuiv=wrapper.wrapper(glPixelMapuiv).setInputArraySize(
    'values', None
)
# INPUT glPixelMapusv.values size not checked against mapsize
glPixelMapusv=wrapper.wrapper(glPixelMapusv).setInputArraySize(
    'values', None
)
# INPUT glDrawPixels.pixels size not checked against 'format,type,width,height'
glDrawPixels=wrapper.wrapper(glDrawPixels).setInputArraySize(
    'pixels', None
)
glGetClipPlane=wrapper.wrapper(glGetClipPlane).setOutput(
    'equation',size=(4,),orPassIn=True
)
glGetLightfv=wrapper.wrapper(glGetLightfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetLightiv=wrapper.wrapper(glGetLightiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# OUTPUT glGetMapdv.v COMPSIZE(target, query) 
# OUTPUT glGetMapfv.v COMPSIZE(target, query) 
# OUTPUT glGetMapiv.v COMPSIZE(target, query) 
glGetMaterialfv=wrapper.wrapper(glGetMaterialfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetMaterialiv=wrapper.wrapper(glGetMaterialiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetPixelMapfv=wrapper.wrapper(glGetPixelMapfv).setOutput(
    'values',size=_glgets._glget_size_mapping,pnameArg='map',orPassIn=True
)
glGetPixelMapuiv=wrapper.wrapper(glGetPixelMapuiv).setOutput(
    'values',size=_glgets._glget_size_mapping,pnameArg='map',orPassIn=True
)
glGetPixelMapusv=wrapper.wrapper(glGetPixelMapusv).setOutput(
    'values',size=_glgets._glget_size_mapping,pnameArg='map',orPassIn=True
)
glGetPolygonStipple=wrapper.wrapper(glGetPolygonStipple).setOutput(
    'mask',size=lambda x:(x,),pnameArg='128.0',orPassIn=True
)
glGetTexEnvfv=wrapper.wrapper(glGetTexEnvfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexEnviv=wrapper.wrapper(glGetTexEnviv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexGendv=wrapper.wrapper(glGetTexGendv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexGenfv=wrapper.wrapper(glGetTexGenfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexGeniv=wrapper.wrapper(glGetTexGeniv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glLoadMatrixf=wrapper.wrapper(glLoadMatrixf).setInputArraySize(
    'm', 16
)
glLoadMatrixd=wrapper.wrapper(glLoadMatrixd).setInputArraySize(
    'm', 16
)
glMultMatrixf=wrapper.wrapper(glMultMatrixf).setInputArraySize(
    'm', 16
)
glMultMatrixd=wrapper.wrapper(glMultMatrixd).setInputArraySize(
    'm', 16
)
### END AUTOGENERATED SECTION