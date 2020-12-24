"""Utility module to parse a Feedback buffer"""
from OpenGL import contextdata
from OpenGL.GL.VERSION import GL_1_1 as _simple

def parseFeedback( buffer, entryCount ):
    """Parse the feedback buffer into Python object records"""
    bufferIndex = 0
    result = []
    getVertex = createGetVertex( )
    while bufferIndex < entryCount:
        token = int(buffer[bufferIndex])
        bufferIndex += 1
        if token in SINGLE_VERTEX_TOKENS:
            vData, bufferIndex = getVertex( buffer, bufferIndex )
            result.append( (SINGLE_VERTEX_TOKENS.get(token), Vertex(*vData)) )
        elif token in DOUBLE_VERTEX_TOKENS:
            vData, bufferIndex = getVertex( buffer, bufferIndex )
            vData2, bufferIndex = getVertex( buffer, bufferIndex )
            result.append( (
                DOUBLE_VERTEX_TOKENS.get(token), 
                Vertex(*vData),
                Vertex(*vData2),
            ) )
        elif token == _simple.GL_PASS_THROUGH_TOKEN:
            result.append( (_simple.GL_PASS_THROUGH_TOKEN, buffer[bufferIndex]))
            bufferIndex += 1
        elif token == _simple.GL_POLYGON_TOKEN:
            temp = [_simple.GL_POLYGON_TOKEN]
            count = int(buffer[bufferIndex])
            bufferIndex += 1
            for item in range(count):
                vData,bufferIndex = getVertex( buffer, bufferIndex )
                temp.append( Vertex(*vData))
            result.append( tuple(temp))
        else:
            raise ValueError( 
                """Unrecognised token %r in feedback stream"""%(token,)
            )
    return result

SINGLE_VERTEX_TOKENS = {
    _simple.GL_BITMAP_TOKEN: _simple.GL_BITMAP_TOKEN,
    _simple.GL_COPY_PIXEL_TOKEN: _simple.GL_COPY_PIXEL_TOKEN,
    _simple.GL_DRAW_PIXEL_TOKEN: _simple.GL_DRAW_PIXEL_TOKEN,
    _simple.GL_POINT_TOKEN: _simple.GL_POINT_TOKEN,
}
DOUBLE_VERTEX_TOKENS = {
    _simple.GL_LINE_TOKEN: _simple.GL_LINE_TOKEN,
    _simple.GL_LINE_RESET_TOKEN: _simple.GL_LINE_RESET_TOKEN,
}
class Vertex( object ):
    """Simplistic holder for vertex data from a feedback buffer"""
    __slots__ = ('vertex','color','texture')
    def __init__( self, vertex,color=None,texture=None):
        """Store values for access"""
        self.vertex = vertex 
        self.color = color 
        self.texture = texture 
def createGetVertex( ):
    mode = contextdata.getValue( "GL_FEEDBACK_BUFFER_TYPE" )
    indexMode = _simple.glGetBooleanv( _simple.GL_INDEX_MODE )
    colorSize = [ 4,1 ][ int(indexMode) ]
    if mode in (_simple.GL_2D,_simple.GL_3D):
        if mode == _simple.GL_2D:
            size = 2
        else:
            size = 3
        def getVertex( buffer, bufferIndex ):
            end = bufferIndex+size
            return (buffer[bufferIndex:end],None,None),end 
    elif mode == _simple.GL_3D_COLOR:
        def getVertex( buffer, bufferIndex ):
            end = bufferIndex+3
            colorEnd = end + colorSize
            return (buffer[bufferIndex:end],buffer[end:colorEnd],None),colorEnd 
    else:
        if mode == _simple.GL_3D_COLOR_TEXTURE:
            size = 3
        else:
            size = 4
        def getVertex( buffer, bufferIndex ):
            end = bufferIndex+size
            colorEnd = end + colorSize
            textureEnd = colorEnd + 4
            return (buffer[bufferIndex:end],buffer[end:colorEnd],buffer[colorEnd:textureEnd]),textureEnd
    return getVertex
