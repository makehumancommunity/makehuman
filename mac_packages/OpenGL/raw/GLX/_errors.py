from OpenGL.platform import PLATFORM as _p
from OpenGL.error import _ErrorChecker
if _ErrorChecker:
    _error_checker = _ErrorChecker( _p, None )
else:
    _error_checker = None
