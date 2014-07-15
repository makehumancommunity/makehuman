#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
MakeHuman python entry-point.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements, Joel Palmius, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This file starts the MakeHuman python application.
"""

from __future__ import absolute_import  # Fix 'from . import x' statements on python 2.6
import sys
import os
import re
import subprocess

## Version information #########################################################
version = [1, 0, 1]                     # Major, minor and patch version number
release = False                         # False for nightly
versionSub = ""                         # Short version description
meshVersion = "hm08"                    # Version identifier of the basemesh
################################################################################

def getVersionDigitsStr():
    """
    String representation of the version number only (no additional info)
    """
    return ".".join( [str(v) for v in version] )

def _versionStr():
    if versionSub:
        return getVersionDigitsStr() + " " + versionSub
    else:
        return getVersionDigitsStr()

def isRelease():
    """
    True when release version, False for nightly (dev) build
    """
    return release

def isBuild():
    """
    Determine whether the app is frozen using pyinstaller/py2app.
    Returns True when this is a release or nightly build (eg. it is build as a
    distributable package), returns False if it is a source checkout.
    """
    return getattr(sys, 'frozen', False)

def getVersion():
    """
    Comparable version as list of ints
    """
    return version

def getVersionStr(verbose=True):
    """
    Verbose version as string, for displaying and information
    """
    if isRelease():
        return _versionStr()
    else:
        if 'HGREVISION' not in os.environ:
            get_hg_revision()
        result = _versionStr() + " (r%s %s)" % (os.environ['HGREVISION'], os.environ['HGNODEID'])
        if verbose:
            result += (" [%s]" % os.environ['HGREVISION_SOURCE'])
        return result

def getShortVersion():
    """
    Useful for tagging assets
    """
    if versionSub:
        return versionSub.replace(' ', '_').lower()
    else:
        return "v" + getVersionDigitsStr()

def getBasemeshVersion():
    """
    Version of the human basemesh
    """
    return meshVersion

def unicode(msg):
    """
    Override default unicode constructor to try and resolve some issues with
    mismatched string codecs.
    Perhaps this is overkill, but better safe than sorry.
    """
    try:
        # First attempt the builtin unicode() function without interference
        return __builtins__.unicode(msg)
    except:
        pass
    try:
        # In case msg is an exception, attempt to decode its message
        return unicode(msg.message)
    except:
        pass
    try:
        # Try decoding as utf-8 bytestring
        return __builtins__.unicode(msg, encoding="utf-8")
    except:
        pass
    try:
        # Try guessing system default encoding and decode as such
        import locale
        return __builtins__.unicode(msg, encoding=locale.getpreferredencoding())
    except:
        pass
    try:
        # Attempt to decode object's __str__ into unicode
        return str(msg).decode("utf-8", errors="replace")
    except:
        pass
    return u"unable to encode message"

def getCwd():
    """
    Retrieve the folder where makehuman.py or makehuman.exe is located.
    This is not necessarily the CWD (current working directory), but it is what
    the CWD should be.
    """
    if isBuild():
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.realpath(__file__))

def getHgRoot(subpath=''):
    cwd = getCwd()
    return os.path.realpath(os.path.join(cwd, '..', subpath))

def get_revision_hg_info():
    # Return local revision number of hg parent
    hgRoot = getHgRoot()
    output = subprocess.Popen(["hg","-q","parent","--template","{rev}:{node|short}"], stdout=subprocess.PIPE, stderr=sys.stderr, cwd=hgRoot).communicate()[0]
    output = output.strip().split(':')
    rev = output[0].strip().replace('+', '')
    revid = output[1].strip().replace('+', '')
    try:
        branch = subprocess.Popen(["hg","-q","branch"], stdout=subprocess.PIPE, stderr=sys.stderr, cwd=hgRoot).communicate()[0].replace('\n','').strip()
    except:
        branch = None
    return (rev, revid, branch)

def get_revision_entries(folder=None):
    # First fallback: try to parse the files in .hg manually
    cachefile = open(getHgRoot('.hg/cache/tags'), 'r')
    for line in iter(cachefile):
        if line == "\n":
            break
        line = line.split()
        rev = int(line[0].strip())
        nodeid = line[1].strip()
        nodeid_short = nodeid[:12]
        # Tip is at the top of the file
        return (str(rev), nodeid_short)
    raise RuntimeError("No tip revision found in tags cache file")

def get_revision_hglib():
    # The following only works if python-hglib is installed.
    import hglib
    hgclient = hglib.open(getHgRoot())
    parent = hgclient.parents()[0]
    branch = hgclient.branch()
    return (parent.rev.replace('+',''), parent.node[:12], branch)

def get_revision_file():
    # Default fallback to use if we can't figure out HG revision in any other
    # way: Use this file's hg revision.
    pattern = re.compile(r'[^0-9]')
    return pattern.sub("", "$Revision: 6893 $")

def get_hg_revision_1():
    """
    Retrieve (local) revision number and short nodeId for current tip.
    """
    hgrev = None

    try:
        hgrev = get_revision_hg_info()
        os.environ['HGREVISION_SOURCE'] = "hg tip command"
        os.environ['HGREVISION'] = str(hgrev[0])
        os.environ['HGNODEID'] = str(hgrev[1])
        if hgrev[2]:
            os.environ['HGBRANCH'] = hgrev[2]
        return hgrev
    except Exception as e:
        print >> sys.stderr,  u"NOTICE: Failed to get hg version number from command line: " + format(unicode(e)) + u" (This is just a head's up, not a critical error)"

    try:
        hgrev = get_revision_hglib()
        os.environ['HGREVISION_SOURCE'] = "python-hglib"
        os.environ['HGREVISION'] = str(hgrev[0])
        os.environ['HGNODEID'] = str(hgrev[1])
        if hgrev[2]:
            os.environ['HGBRANCH'] = hgrev[2]
        return hgrev
    except Exception as e:
        print >> sys.stderr,  u"NOTICE: Failed to get hg version number using hglib: " + format(unicode(e)) + u" (This is just a head's up, not a critical error)"

    try:
        hgrev = get_revision_entries()
        os.environ['HGREVISION_SOURCE'] = ".hg cache file"
        os.environ['HGREVISION'] = str(hgrev[0])
        os.environ['HGNODEID'] = str(hgrev[1])
        return hgrev
    except Exception as e:
        print >> sys.stderr,  u"NOTICE: Failed to get hg version from file: " + format(unicode(e)) + u" (This is just a head's up, not a critical error)"

    #TODO Disabled this fallback for now, it's possible to do this using the hg keyword extension, but not recommended and this metric was never really reliable (it only caused more confusion)
    '''
    print >> sys.stderr,  "NOTICE: Using HG rev from file stamp. This is likely outdated, so the number in the title bar might be off by a few commits."
    hgrev = get_revision_file()
    os.environ['HGREVISION_SOURCE'] = "approximated from file stamp"
    os.environ['HGREVISION'] = hgrev[0]
    os.environ['HGNODEID'] = hgrev[1]
    return hgrev
    '''

    if hgrev is None:
        rev = "?"
        revid = "UNKNOWN"
        hgrev = (rev, revid)
    else:
        rev, revid = hgrev
    os.environ['HGREVISION_SOURCE'] = "none found"
    os.environ['HGREVISION'] = str(rev)
    os.environ['HGNODEID'] = str(revid)

    return hgrev

def get_hg_revision():
    # Use the data/VERSION file if it exists. This is created and managed by build scripts
    import getpath
    versionFile = getpath.getSysDataPath("VERSION")
    if os.path.exists(versionFile):
        version_ = open(versionFile).read().strip()
        print >> sys.stderr,  u"data/VERSION file detected using value from version file: %s" % version_
        os.environ['HGREVISION'] = str(version_.split(':')[0])
        os.environ['HGNODEID'] = str(version_.split(':')[1])
        os.environ['HGREVISION_SOURCE'] = "data/VERSION static revision data"
    elif not isBuild():
        print >> sys.stderr,  u"NO VERSION file detected retrieving revision info from HG"
        # Set HG rev in environment so it can be used elsewhere
        hgrev = get_hg_revision_1()
        print >> sys.stderr,  u"Detected HG revision: r%s (%s)" % (hgrev[0], hgrev[1])
    else:
        # Don't bother trying to retrieve HG info for a build release, there should be a data/VERSION file
        os.environ['HGREVISION'] = ""
        os.environ['HGNODEID'] = ""
        os.environ['HGREVISION_SOURCE'] = "skipped for build"

    return (os.environ['HGREVISION'], os.environ['HGNODEID'])

def set_sys_path():
    """
    Append local module folders to python search path.
    """
    #[BAL 07/11/2013] make sure we're in the right directory
    if sys.platform != 'darwin': # Causes issues with py2app builds on MAC
        os.chdir(getCwd())
    syspath = ["./", "./lib", "./apps", "./shared", "./apps/gui","./core"]
    syspath.extend(sys.path)
    sys.path = syspath

stdout_filename = None
stderr_filename = None

def get_platform_paths():
    global stdout_filename, stderr_filename
    import getpath

    home = getpath.getPath()

    if sys.platform == 'win32':
        stdout_filename = os.path.join(home, "python_out.txt")
        stderr_filename = os.path.join(home, "python_err.txt")

    elif sys.platform.startswith("darwin"):
        stdout_filename = os.path.join(home, "makehuman-output.txt")
        stderr_filename = os.path.join(home, "makehuman-error.txt")

def redirect_standard_streams():
    from codecs import open
    import locale
    encoding = locale.getpreferredencoding()
    if stdout_filename:
        sys.stdout = open(stdout_filename, "w", encoding=encoding, errors="replace")
    if stderr_filename:
        sys.stderr = open(stderr_filename, "w", encoding=encoding, errors="replace")

def close_standard_streams():
    sys.stdout.close()
    sys.stderr.close()

def make_user_dir():
    """
    Make sure MakeHuman folder storing per-user files exists.
    """
    import getpath
    userDir = getpath.getPath()
    if not os.path.isdir(userDir):
        os.makedirs(userDir)
    userDataDir = getpath.getPath('data')
    if not os.path.isdir(userDataDir):
        os.makedirs(userDataDir)

def init_logging():
    import log
    log.init()
    log.message('Initialized logging')

def debug_dump():
    try:
        import debugdump
        debugdump.dump.reset()
    except debugdump.DependencyError as e:
        print >> sys.stderr,  u"Dependency error: " + format(unicode(e))
        import log
        log.error("Dependency error: %s", e)
        sys.exit(-1)
    except Exception as _:
        import log
        log.error("Could not create debug dump", exc_info=True)

def parse_arguments():
    if len(sys.argv) < 2:
        return dict()

    import argparse    # requires python >= 2.7
    parser = argparse.ArgumentParser()

    # optional arguments
    parser.add_argument('-v', '--version', action='version', version=getVersionStr())
    parser.add_argument("--noshaders", action="store_true", help="disable shaders")
    parser.add_argument("--nomultisampling", action="store_true", help="disable multisampling (used for anti-aliasing and alpha-to-coverage transparency rendering)")
    parser.add_argument("--debugopengl", action="store_true", help="enable OpenGL error checking and logging (slow)")
    parser.add_argument("--fullloggingopengl", action="store_true", help="log all OpenGL calls (very slow)")
    parser.add_argument("--debugnumpy", action="store_true", help="enable numpy runtime error messages")
    if not isRelease():
        parser.add_argument("-t", "--runtests", action="store_true", help="run test suite (for developers)")

    # optional positional arguments
    parser.add_argument("mhmFile", default=None, nargs='?', help=".mhm file to load (optional)")

    argOptions = vars(parser.parse_args())
    return argOptions

def main():
    try:
        set_sys_path()
        make_user_dir()
        get_platform_paths()
        redirect_standard_streams()
        get_hg_revision()
        os.environ['MH_VERSION'] = getVersionStr()
        os.environ['MH_SHORT_VERSION'] = getShortVersion()
        os.environ['MH_MESH_VERSION'] = getBasemeshVersion()
        args = parse_arguments()
        init_logging()
    except Exception as e:
        print >> sys.stderr,  "error: " + format(unicode(e))
        import traceback
        bt = traceback.format_exc()
        print >> sys.stderr, bt
        return

    # Pass release info to debug dump using environment variables
    os.environ['MH_FROZEN'] = "Yes" if isBuild() else "No"
    os.environ['MH_RELEASE'] = "Yes" if isRelease() else "No"

    debug_dump()
    from core import G
    G.args = args

    # Set numpy properties
    if not args.get('debugnumpy', False):
        import numpy
        # Suppress runtime errors
        numpy.seterr(all = 'ignore')

    # Here pyQt and PyOpenGL will be imported
    from mhmain import MHApplication
    application = MHApplication()
    application.run()

    #import cProfile
    #cProfile.run('application.run()')

    close_standard_streams()

if __name__ == '__main__':
    main()
