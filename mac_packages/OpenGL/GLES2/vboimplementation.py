from OpenGL.arrays import vbo
from OpenGL.GLES2.VERSION import GLES2_2_0
from OpenGL.GLES2.OES import mapbuffer

class Implementation( vbo.Implementation ):
    """OpenGL-based implementation of VBO interfaces"""
    def __init__( self ):
        for name in self.EXPORTED_NAMES:
            for source in [ GLES2_2_0, mapbuffer ]:
                for possible in (name,name+'OES'):
                    try:
                        setattr( self, name, getattr( source, possible ))
                    except AttributeError as err:
                        pass 
                    else:
                        found = True
                assert found, name
        if GLES2_2_0.glBufferData:
            self.available = True
Implementation.register()
