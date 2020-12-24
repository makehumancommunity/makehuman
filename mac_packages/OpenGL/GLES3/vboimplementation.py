from OpenGL.arrays import vbo
from OpenGL.GLES3.VERSION import GLES3_3_0
from OpenGL.GLES3.OES import mapbuffer

class Implementation( vbo.Implementation ):
    """OpenGL-based implementation of VBO interfaces"""
    def __init__( self ):
        for name in self.EXPORTED_NAMES:
            for source in [ GLES3_3_0, mapbuffer ]:
                for possible in (name,name+'OES'):
                    try:
                        setattr( self, name, getattr( source, possible ))
                    except AttributeError as err:
                        pass 
                    else:
                        found = True
                assert found, name
        if GLES3_3_0.glBufferData:
            self.available = True
Implementation.register()
