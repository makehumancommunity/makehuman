"""Convenience API for using Frame Buffer Objects"""
from OpenGL.extensions import alternate
from OpenGL.GL.ARB.framebuffer_object import *
from OpenGL.GL.EXT.framebuffer_object import *
from OpenGL.GL.EXT.framebuffer_multisample import *
from OpenGL.GL.EXT.framebuffer_blit import *

glBindFramebuffer = alternate(glBindFramebuffer,glBindFramebufferEXT)
glBindRenderbuffer = alternate( glBindRenderbuffer, glBindRenderbufferEXT )
glCheckFramebufferStatus = alternate( glCheckFramebufferStatus, glCheckFramebufferStatusEXT )
glDeleteFramebuffers = alternate( glDeleteFramebuffers, glDeleteFramebuffersEXT )
glDeleteRenderbuffers = alternate( glDeleteRenderbuffers, glDeleteRenderbuffersEXT )
glFramebufferRenderbuffer = alternate( glFramebufferRenderbuffer, glFramebufferRenderbufferEXT )
glFramebufferTexture1D = alternate( glFramebufferTexture1D, glFramebufferTexture1DEXT )
glFramebufferTexture2D = alternate( glFramebufferTexture2D, glFramebufferTexture2DEXT )
glFramebufferTexture3D = alternate( glFramebufferTexture3D, glFramebufferTexture3DEXT )
glGenFramebuffers = alternate( glGenFramebuffers, glGenFramebuffersEXT )
glGenRenderbuffers = alternate( glGenRenderbuffers, glGenRenderbuffersEXT )
glGenerateMipmap = alternate( glGenerateMipmap, glGenerateMipmapEXT )
glGetFramebufferAttachmentParameteriv = alternate( glGetFramebufferAttachmentParameteriv, glGetFramebufferAttachmentParameterivEXT )
glGetRenderbufferParameteriv = alternate( glGetRenderbufferParameteriv, glGetRenderbufferParameterivEXT )
glIsFramebuffer = alternate( glIsFramebuffer, glIsFramebufferEXT )
glIsRenderbuffer = alternate( glIsRenderbuffer, glIsRenderbufferEXT )
glRenderbufferStorage = alternate( glRenderbufferStorage, glRenderbufferStorageEXT )

glBlitFramebuffer = alternate( glBlitFramebuffer, glBlitFramebufferEXT )  
glRenderbufferStorageMultisample = alternate( glRenderbufferStorageMultisample, glRenderbufferStorageMultisampleEXT )

# this entry point is new to the ARB version of the extensions
#glFramebufferTextureLayer = alternate( glFramebufferTextureLayer, glFramebufferTextureLayerEXT )


def checkFramebufferStatus():
    """Utility method to check status and raise errors"""
    status = glCheckFramebufferStatus( GL_FRAMEBUFFER )
    if status == GL_FRAMEBUFFER_COMPLETE:
        return True 
    from OpenGL.error import GLError
    description = None
    for error_constant in [
        GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT,
        GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT,
        GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS,
        GL_FRAMEBUFFER_INCOMPLETE_FORMATS,
        GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER,
        GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER,
        GL_FRAMEBUFFER_UNSUPPORTED,
    ]:
        if status == error_constant:
            status = error_constant
            description = str(status)
    raise GLError( 
        err=status, 
        result=status, 
        baseOperation=glCheckFramebufferStatus, 
        description=description,
    )
