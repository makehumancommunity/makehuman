from OpenGL.arrays import vbo
from OpenGL.GL.ARB import vertex_buffer_object
from OpenGL.GL.ARB import uniform_buffer_object
from OpenGL.GL.ARB import texture_buffer_object
from OpenGL.GL.ARB import enhanced_layouts

class Implementation( vbo.Implementation ):
    """OpenGL ARB extension-based implementation of VBO interfaces"""
    def __init__( self ):
        for name in self.EXPORTED_NAMES:
            source = name
            if name.startswith( 'GL_'):
                source = name + '_ARB'
            else:
                source = name + 'ARB'
            found = False
            for source_extension in (
                vertex_buffer_object,
                uniform_buffer_object,
                texture_buffer_object,
                enhanced_layouts,
            ):
                try:
                    setattr( self, name, getattr( source_extension, source ))
                except AttributeError as err:
                    try:
                        setattr( self, name, getattr( source_extension, name ))
                    except AttributeError as err:
                        pass 
                    else:
                        found = True
                else:
                    found =True 
                    break
            assert found, name
        if self.glGenBuffers:
            self.available = True
Implementation.register()
