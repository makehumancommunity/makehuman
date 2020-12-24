from OpenGL.platform import PLATFORM as _p
from OpenGL.error import _ErrorChecker
if _p.GLES1 and _p.GLES1.glGetError and _ErrorChecker:
    _error_checker = _ErrorChecker( _p, _p.GLES1.glGetError )
else:
    _error_checker = None
