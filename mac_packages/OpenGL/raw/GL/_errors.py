from OpenGL.platform import PLATFORM as _p
from OpenGL.error import _ErrorChecker
if _ErrorChecker:
    _error_checker = _ErrorChecker( _p, _p.GL.glGetError )
else:
    _error_checker = None
