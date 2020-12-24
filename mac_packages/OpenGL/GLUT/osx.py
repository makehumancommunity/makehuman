"""OSX specific extensions to GLUT"""
from OpenGL import platform
from OpenGL import constant
from OpenGL.GLUT import special

GLUT_NO_RECOVERY = constant.Constant( 'GLUT_NO_RECOVERY', 1024)
GLUT_3_2_CORE_PROFILE = constant.Constant( 'GLUT_3_2_CORE_PROFILE', 2048)

glutCheckLoop = platform.createBaseFunction( 
    'glutCheckLoop', dll=platform.PLATFORM.GLUT, resultType=None, 
    argTypes=[],
    doc='glutCheckLoop(  ) -> None', 
    argNames=(),
)

glutWMCloseFunc = special.GLUTCallback(
    'WMClose', (), (),
)
