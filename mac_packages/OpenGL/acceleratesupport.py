"""Common code for accelerated modules"""
import logging
from OpenGL import _configflags
needed_version = (3,1,5)
_log = logging.getLogger( 'OpenGL.acceleratesupport' )
try:
    import OpenGL_accelerate
    if _configflags.USE_ACCELERATE:
        if OpenGL_accelerate.__version_tuple__ <  needed_version:
            _log.warning( """Incompatible version of OpenGL_accelerate found, need at least %s found %s""", needed_version, OpenGL_accelerate.__version_tuple__)
            raise ImportError( """Old version of OpenGL_accelerate""" )
        ACCELERATE_AVAILABLE = True
        _log.info( """OpenGL_accelerate module loaded""" )
    else:
        raise ImportError( """Acceleration disabled""" )
except ImportError as err:
    _log.info( """No OpenGL_accelerate module loaded: %s""", err )
    ACCELERATE_AVAILABLE = False
