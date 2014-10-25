#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
MakeHuman python entry-point.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Manuel Bastioni, Glynn Clements, Jonas Hauquier, Joel Palmius

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
version = [1, 1, 0]                     # Major, minor and patch version number
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
    output = subprocess.Popen(["hg","-q","parents","--template","{rev}:{node|short}"], stdout=subprocess.PIPE, stderr=sys.stderr, cwd=hgRoot).communicate()[0]
    output = output.strip().split(':')
    rev = output[0].strip().replace('+', '')
    revid = output[1].strip().replace('+', '')
    try:
        branch = subprocess.Popen(["hg","-q","branch"], stdout=subprocess.PIPE, stderr=sys.stderr, cwd=hgRoot).communicate()[0].replace('\n','').strip()
    except:
        branch = None
    return (rev, revid, branch)

def get_revision_dirstate_parent(folder=None):
    # First fallback: try to parse the dirstate file in .hg manually
    import binascii

    dirstatefile = open(getHgRoot('.hg/dirstate'), 'rb')
    st = dirstatefile.read(40)
    dirstatefile.close()
    l = len(st)
    if l == 40:
        nodeid = binascii.hexlify(st)[:20]
        nodeid_short = nodeid[:12]
    elif l > 0 and l < 40:
        raise RuntimeError('Hg working directory state appears damaged!')

    # Build mapping of nodeid to local revision number
    node_rev_map = dict()
    revlogfile = open(getHgRoot('.hg/store/00changelog.i'), 'rb')
    st = revlogfile.read(32)

    rev_idx = 0
    while st:
        st = revlogfile.read(10)
        if st:
            _nodeid = binascii.hexlify(st)
            node_rev_map[_nodeid] = rev_idx

        rev_idx += 1
        st = revlogfile.read(54)

    revlogfile.close()
    if nodeid not in node_rev_map:
        raise RuntimeError("Failed to lookup local revision number for node %s" % nodeid)
    rev = node_rev_map[nodeid]
    return (str(rev), nodeid_short)


def get_revision_cache_tip(folder=None):
    # Second fallback: try to parse the cache file in .hg manually
    # Retrieves revision of tip, which might not actually be the working dir parent revision
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
    Retrieve (local) revision number and short nodeId of current working dir
    parent.
    """
    hgrev = None

    try:
        hgrev = get_revision_hg_info()
        os.environ['HGREVISION_SOURCE'] = "hg parents command"
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
        hgrev = get_revision_dirstate_parent()
        os.environ['HGREVISION_SOURCE'] = ".hg dirstate file"
        os.environ['HGREVISION'] = str(hgrev[0])
        os.environ['HGNODEID'] = str(hgrev[1])
        return hgrev
    except Exception as e:
        print >> sys.stderr,  u"NOTICE: Failed to get hg parent version from dirstate file: " + format(unicode(e)) + u" (This is just a head's up, not a critical error)"

    try:
        hgrev = get_revision_cache_tip()
        os.environ['HGREVISION_SOURCE'] = ".hg cache file tip"
        os.environ['HGREVISION'] = str(hgrev[0])
        os.environ['HGNODEID'] = str(hgrev[1])
        return hgrev
    except Exception as e:
        print >> sys.stderr,  u"NOTICE: Failed to get hg tip version from cache file: " + format(unicode(e)) + u" (This is just a head's up, not a critical error)"

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
    parser.add_argument("--license", action="store_true", help="Show full copyright notice and software license")
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

    if argOptions.get('license', False):
        print "\n" + getCopyrightMessage() + "\n"
        sys.exit(0)

    return argOptions

def getCopyrightMessage(short=False):
    if short:
        return """MakeHuman Copyright (C) 2001-2014 http://www.makehuman.org
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions. For details use the option --license"""

    return """Makehuman is a completely free, open source, innovative and 
professional software for the modelling of 3-Dimensional humanoid characters
Copyright (C) 2001-2014  www.makehuman.org

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


MakeHuman's source code and its mesh data is distributed freely under 
the AGPL3 license (see license.txt). Content created using the MakeHuman 
application is released under the liberal CC0 license. For more details, 
refer to these pages:

    http://www.makehuman.org/doc/node/the_makehuman_application.html
    http://www.makehuman.org/doc/node/makehuman_mesh_license.html

Licenses for dependencies are included in the licenses folder.


For further help, have a look at our documentation at 
    http://www.makehuman.org/documentation
Frequently asked questions are found at
    http://www.makehuman.org/faq


The MakeHuman team can be contacted at http://www.makehuman.org
If you have other questions, feel free to ask them on our forums at 
    http://www.makehuman.org/forum/
Bugs can be reported on the project's bug tracker
    http://bugtracker.makehuman.org
"""

def getAssetLicense(properties=None):
    """
    Retrieve the license information for MakeHuman assets.
    If no custom properties are specified, the license object retrieved specifies
    the licensing information that applies to the assets included in the
    official MakeHuman release.
    We consider assets to be the basemesh, targets, proxy definitions and their
    fitting data, in general all the files in the data folder with the exclusion
    of the data in the form as retained by the official exporters to which the
    CC0 exception clause applies.
    Assets created by third parties can be bound to different licensing conditions,
    which is why properties can be set as a dict of format:
        {"author": ..., "license": ..., "copyright": ..., "homepage": ...}
    """
    class LicenseInfo:
        def __init__(self):
            self.author = "MakeHuman Team"
            self.license = "AGPL3 (see also http://www.makehuman.org/doc/node/external_tools_license.html)"
            self.homepage = "http://www.makehuman.org"
            self.copyright = "(c) MakeHuman.org 2011-2014"
            self._keys = ["author", "license", "copyright", "homepage"]
            self._customized = False

        def setProperty(self, name, value):
            if name in self._keys:
                if getattr(self, name) != value:
                    self._customized = True
                    setattr(self, name, value)

        def isCustomized(self):
            return self._customized

        def __str__(self):
            return """MakeHuman asset license:
    Author: %s
    License: %s
    Copyright: %s
    Homepage: %s""" % (self.author, self.license, self.copyright, self.homepage)

        def asDict(self):
            return dict( [(pname, getattr(self, pname)) for pname in self._keys] )

        def fromDict(self, propDict):
            for prop,val in propDict.items():
                self.setProperty(prop, val)
            return self

        def updateFromComment(self, commentLine):
            commentLine = commentLine.strip()
            if commentLine.startswith('#'):
                commentLine = commentLine[1:]
            elif commentLine.startswith('//'):
                commentLine = commentLine[2:]
            commentLine = commentLine.strip()

            words = commentLine.split()
            if len(words) < 1:
                return

            key = words[0]
            value = " ".join(words[1:])

            self.setProperty(key,value)

        def toNumpyString(self):
            def _packStringDict(stringDict):
                import numpy as np
                text = ''
                index = []
                for key,value in stringDict.items():
                    index.append(len(key))
                    index.append(len(value))
                    text += key + value
                text = np.fromstring(text, dtype='S1')
                index = np.array(index, dtype=np.uint32)
                return text, index

            return _packStringDict(self.asDict())

        def fromNumpyString(self, text, index=None):
            def _unpackStringDict(text, index):
                stringDict = dict()
                last = 0
                for i in range(0,len(index), 2):
                    l_key = index[i]
                    l_val = index[i+1]

                    key = text[last:last+l_key].tostring()
                    val = text[last+l_key:last+l_key+l_val].tostring()
                    stringDict[key] = val

                    last += (l_key + l_val)
                return stringDict

            if index is None:
                text, index = text
            return self.fromDict( _unpackStringDict(text, index) )


    result = LicenseInfo()
    if properties is not None:
        result.fromDict(properties)
        result._customized = False
    return result


def main():
    print getCopyrightMessage(short=True) + "\n"

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
