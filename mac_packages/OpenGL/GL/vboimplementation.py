from OpenGL.arrays import vbo
from OpenGL.GL.VERSION import GL_1_5, GL_3_0, GL_3_1

class Implementation( vbo.Implementation ):
    """OpenGL-based implementation of VBO interfaces"""
    def __init__( self ):
        for name in self.EXPORTED_NAMES:
            found = False
            for source in (GL_1_5,GL_3_0, GL_3_1):
                try:
                    setattr( self, name, getattr( source, name ))
                except AttributeError as err:
                    pass 
                else:
                    found = True 
                    break 
            assert found, name
        if GL_1_5.glBufferData:
            self.available = True

Implementation.register()
