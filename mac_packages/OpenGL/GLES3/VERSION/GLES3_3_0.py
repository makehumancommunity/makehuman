'''OpenGL extension VERSION.GLES3_3_0

This module customises the behaviour of the 
OpenGL.raw.GLES3.VERSION.GLES3_3_0 to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/VERSION/GLES3_3_0.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES3 import _types, _glgets
from OpenGL.raw.GLES3.VERSION.GLES3_3_0 import *
from OpenGL.raw.GLES3.VERSION.GLES3_3_0 import _EXTENSION_NAME

def glInitGles330VERSION():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glDrawRangeElements.indices size not checked against 'count,type'
glDrawRangeElements=wrapper.wrapper(glDrawRangeElements).setInputArraySize(
    'indices', None
)
# INPUT glTexImage3D.pixels size not checked against 'format,type,width,height,depth'
glTexImage3D=wrapper.wrapper(glTexImage3D).setInputArraySize(
    'pixels', None
)
# INPUT glTexSubImage3D.pixels size not checked against 'format,type,width,height,depth'
glTexSubImage3D=wrapper.wrapper(glTexSubImage3D).setInputArraySize(
    'pixels', None
)
# INPUT glCompressedTexImage3D.data size not checked against imageSize
glCompressedTexImage3D=wrapper.wrapper(glCompressedTexImage3D).setInputArraySize(
    'data', None
)
# INPUT glCompressedTexSubImage3D.data size not checked against imageSize
glCompressedTexSubImage3D=wrapper.wrapper(glCompressedTexSubImage3D).setInputArraySize(
    'data', None
)
glGenQueries=wrapper.wrapper(glGenQueries).setOutput(
    'ids',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
# INPUT glDeleteQueries.ids size not checked against n
glDeleteQueries=wrapper.wrapper(glDeleteQueries).setInputArraySize(
    'ids', None
)
glGetQueryiv=wrapper.wrapper(glGetQueryiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetQueryObjectuiv=wrapper.wrapper(glGetQueryObjectuiv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetBufferPointerv=wrapper.wrapper(glGetBufferPointerv).setOutput(
    'params',size=(1,),orPassIn=True
)
# INPUT glDrawBuffers.bufs size not checked against n
glDrawBuffers=wrapper.wrapper(glDrawBuffers).setInputArraySize(
    'bufs', None
)
# INPUT glUniformMatrix2x3fv.value size not checked against count*6
glUniformMatrix2x3fv=wrapper.wrapper(glUniformMatrix2x3fv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix3x2fv.value size not checked against count*6
glUniformMatrix3x2fv=wrapper.wrapper(glUniformMatrix3x2fv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix2x4fv.value size not checked against count*8
glUniformMatrix2x4fv=wrapper.wrapper(glUniformMatrix2x4fv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix4x2fv.value size not checked against count*8
glUniformMatrix4x2fv=wrapper.wrapper(glUniformMatrix4x2fv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix3x4fv.value size not checked against count*12
glUniformMatrix3x4fv=wrapper.wrapper(glUniformMatrix3x4fv).setInputArraySize(
    'value', None
)
# INPUT glUniformMatrix4x3fv.value size not checked against count*12
glUniformMatrix4x3fv=wrapper.wrapper(glUniformMatrix4x3fv).setInputArraySize(
    'value', None
)
# INPUT glDeleteVertexArrays.arrays size not checked against n
glDeleteVertexArrays=wrapper.wrapper(glDeleteVertexArrays).setInputArraySize(
    'arrays', None
)
glGenVertexArrays=wrapper.wrapper(glGenVertexArrays).setOutput(
    'arrays',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGetIntegeri_v=wrapper.wrapper(glGetIntegeri_v).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
# INPUT glTransformFeedbackVaryings.varyings size not checked against count
glTransformFeedbackVaryings=wrapper.wrapper(glTransformFeedbackVaryings).setInputArraySize(
    'varyings', None
)
glGetTransformFeedbackVarying=wrapper.wrapper(glGetTransformFeedbackVarying).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'name',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'size',size=(1,),orPassIn=True
).setOutput(
    'type',size=(1,),orPassIn=True
)
# INPUT glVertexAttribIPointer.pointer size not checked against 'size,type,stride'
glVertexAttribIPointer=wrapper.wrapper(glVertexAttribIPointer).setInputArraySize(
    'pointer', None
)
glGetVertexAttribIiv=wrapper.wrapper(glGetVertexAttribIiv).setOutput(
    'params',size=(1,),orPassIn=True
)
glGetVertexAttribIuiv=wrapper.wrapper(glGetVertexAttribIuiv).setOutput(
    'params',size=(1,),orPassIn=True
)
glVertexAttribI4iv=wrapper.wrapper(glVertexAttribI4iv).setInputArraySize(
    'v', 4
)
glVertexAttribI4uiv=wrapper.wrapper(glVertexAttribI4uiv).setInputArraySize(
    'v', 4
)
# OUTPUT glGetUniformuiv.params COMPSIZE(program, location) 
# INPUT glGetFragDataLocation.name size not checked against 'name'
glGetFragDataLocation=wrapper.wrapper(glGetFragDataLocation).setInputArraySize(
    'name', None
)
# INPUT glUniform1uiv.value size not checked against count
glUniform1uiv=wrapper.wrapper(glUniform1uiv).setInputArraySize(
    'value', None
)
# INPUT glUniform2uiv.value size not checked against count*2
glUniform2uiv=wrapper.wrapper(glUniform2uiv).setInputArraySize(
    'value', None
)
# INPUT glUniform3uiv.value size not checked against count*3
glUniform3uiv=wrapper.wrapper(glUniform3uiv).setInputArraySize(
    'value', None
)
# INPUT glUniform4uiv.value size not checked against count*4
glUniform4uiv=wrapper.wrapper(glUniform4uiv).setInputArraySize(
    'value', None
)
# INPUT glClearBufferiv.value size not checked against 'buffer'
glClearBufferiv=wrapper.wrapper(glClearBufferiv).setInputArraySize(
    'value', None
)
# INPUT glClearBufferuiv.value size not checked against 'buffer'
glClearBufferuiv=wrapper.wrapper(glClearBufferuiv).setInputArraySize(
    'value', None
)
# INPUT glClearBufferfv.value size not checked against 'buffer'
glClearBufferfv=wrapper.wrapper(glClearBufferfv).setInputArraySize(
    'value', None
)
# INPUT glGetUniformIndices.uniformNames size not checked against 'uniformCount'
glGetUniformIndices=wrapper.wrapper(glGetUniformIndices).setOutput(
    'uniformIndices',size=_glgets._glget_size_mapping,pnameArg='uniformCount',orPassIn=True
).setInputArraySize(
    'uniformNames', None
)
# OUTPUT glGetActiveUniformsiv.params COMPSIZE(uniformCount, pname) 
# INPUT glGetActiveUniformsiv.uniformIndices size not checked against uniformCount
glGetActiveUniformsiv=wrapper.wrapper(glGetActiveUniformsiv).setInputArraySize(
    'uniformIndices', None
)
# INPUT glGetUniformBlockIndex.uniformBlockName size not checked against ''
glGetUniformBlockIndex=wrapper.wrapper(glGetUniformBlockIndex).setInputArraySize(
    'uniformBlockName', None
)
# OUTPUT glGetActiveUniformBlockiv.params COMPSIZE(program, uniformBlockIndex, pname) 
glGetActiveUniformBlockName=wrapper.wrapper(glGetActiveUniformBlockName).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'uniformBlockName',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
# INPUT glDrawElementsInstanced.indices size not checked against 'count,type'
glDrawElementsInstanced=wrapper.wrapper(glDrawElementsInstanced).setInputArraySize(
    'indices', None
)
glGetInteger64v=wrapper.wrapper(glGetInteger64v).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetSynciv=wrapper.wrapper(glGetSynciv).setOutput(
    'length',size=(1,),orPassIn=True
).setOutput(
    'values',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
glGetInteger64i_v=wrapper.wrapper(glGetInteger64i_v).setOutput(
    'data',size=_glgets._glget_size_mapping,pnameArg='target',orPassIn=True
)
glGetBufferParameteri64v=wrapper.wrapper(glGetBufferParameteri64v).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGenSamplers=wrapper.wrapper(glGenSamplers).setOutput(
    'samplers',size=lambda x:(x,),pnameArg='count',orPassIn=True
)
# INPUT glDeleteSamplers.samplers size not checked against count
glDeleteSamplers=wrapper.wrapper(glDeleteSamplers).setInputArraySize(
    'samplers', None
)
# INPUT glSamplerParameteriv.param size not checked against 'pname'
glSamplerParameteriv=wrapper.wrapper(glSamplerParameteriv).setInputArraySize(
    'param', None
)
# INPUT glSamplerParameterfv.param size not checked against 'pname'
glSamplerParameterfv=wrapper.wrapper(glSamplerParameterfv).setInputArraySize(
    'param', None
)
glGetSamplerParameteriv=wrapper.wrapper(glGetSamplerParameteriv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetSamplerParameterfv=wrapper.wrapper(glGetSamplerParameterfv).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glDeleteTransformFeedbacks.ids size not checked against n
glDeleteTransformFeedbacks=wrapper.wrapper(glDeleteTransformFeedbacks).setInputArraySize(
    'ids', None
)
glGenTransformFeedbacks=wrapper.wrapper(glGenTransformFeedbacks).setOutput(
    'ids',size=lambda x:(x,),pnameArg='n',orPassIn=True
)
glGetProgramBinary=wrapper.wrapper(glGetProgramBinary).setOutput(
    'binary',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
).setOutput(
    'binaryFormat',size=(1,),orPassIn=True
).setOutput(
    'length',size=(1,),orPassIn=True
)
# INPUT glProgramBinary.binary size not checked against length
glProgramBinary=wrapper.wrapper(glProgramBinary).setInputArraySize(
    'binary', None
)
# INPUT glInvalidateFramebuffer.attachments size not checked against numAttachments
glInvalidateFramebuffer=wrapper.wrapper(glInvalidateFramebuffer).setInputArraySize(
    'attachments', None
)
# INPUT glInvalidateSubFramebuffer.attachments size not checked against numAttachments
glInvalidateSubFramebuffer=wrapper.wrapper(glInvalidateSubFramebuffer).setInputArraySize(
    'attachments', None
)
glGetInternalformativ=wrapper.wrapper(glGetInternalformativ).setOutput(
    'params',size=lambda x:(x,),pnameArg='bufSize',orPassIn=True
)
### END AUTOGENERATED SECTION

