#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MakeHuman python entry-point.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Glynn Clements, Jonas Hauquier, Joel Palmius

**Copyright(c):**      MakeHuman Team 2001-2020

**Licensing:**         AGPL3

    This file is part of MakeHuman Community (www.makehumancommunity.org).

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

Abstract
--------

This file starts the MakeHuman python application.
"""

import sys
import os
import re
import subprocess

#from PyQt5 import QtCore

## Version information #########################################################
__version__ = "1.3.0"                   # Major, minor and patch version number
release = False                         # False for nightly
versionSub = "alpha"                    # Short version description
meshVersion = "hm08"                    # Version identifier of the basemesh
################################################################################

__author__ = "Jonas Hauquier, Joel Palmius, Glynn Clements, Thomas Larsson et al."
__copyright__ = "Copyright 2020 Data Collection AB and listed authors"
__credits__ = ["See http://www.makehumancommunity.org/halloffame"]
__license__ = "AGPLv3"
__maintainer__ = "Joel Palmius, Jonas Hauquier"
__status__ = "Production" if release else "Development"


def getVersionDigitsStr():
    """
    String representation of the version number only (no additional info)
    """
    return __version__

def getVersionSubStr():
    return versionSub

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
    return __version__.split('.')

version = getVersion()  # For backward compat.

def getVersionStr(verbose=True, full=False):
    """
    Verbose version as string, for displaying and information
    """
    if isRelease() and not full:
        return _versionStr()
    else:
        from mhversion import MHVersion
        mhv = MHVersion()
        return mhv.currentBranch + ":" + mhv.currentShortCommit

def getShortVersion(noSub=False):
    """
    Useful for tagging assets
    """
    if not noSub and versionSub:
        return versionSub.replace(' ', '_').lower()
    else:
        return "v" + getVersionDigitsStr()

def getBasemeshVersion():
    """
    Version of the human basemesh
    """
    return meshVersion


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

def set_sys_path():
    """
    Append local module folders to python search path.
    """
    #[BAL 07/11/2013] make sure we're in the right directory
    if not sys.platform.startswith('darwin'): # Causes issues with py2app builds on MAC
        os.chdir(getCwd())
        syspath = ["./", "./lib", "./apps", "./shared", "./apps/gui","./core"]
        syspath.extend(sys.path)
        sys.path = syspath
    else:
        data_path = "../Resources/makehuman"
        if(os.path.isdir(data_path)):
            os.chdir(data_path)
        syspath = ["./lib", "./apps", "./shared", "./apps/gui", "./core", "../lib", "../"]
        syspath.extend(sys.path)
        sys.path = syspath

    if isBuild():
        # Make sure we load packaged DLLs instead of those present on the system
        os.environ["PATH"] = '.' + os.path.pathsep + getCwd() + os.path.pathsep + os.environ["PATH"]

stdout_filename = None
stderr_filename = None

def get_platform_paths():
    global stdout_filename, stderr_filename
    import getpath

    home = getpath.getPath()

    if sys.platform.startswith('win'):
        stdout_filename = os.path.join(home, "python_out.txt")
        stderr_filename = os.path.join(home, "python_err.txt")

    elif sys.platform.startswith("darwin"):
        stdout_filename = os.path.join(home, "makehuman-output.txt")
        stderr_filename = os.path.join(home, "makehuman-error.txt")

def redirect_standard_streams():
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
    userPluginsDir = getpath.getPath('plugins')
    if not os.path.isdir(userPluginsDir):
        os.makedirs(userPluginsDir)

def init_logging():
    import log
    log.init()
    log.message('Initialized logging')

def debug_dump():
    try:
        import debugdump
        debugdump.dump.reset()
    except debugdump.DependencyError as e:
        print("Dependency error: " + format(str(e)), file=sys.stderr)
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
    parser.add_argument("--multisampling", action="store_true", help="enable multisampling (used for anti-aliasing and alpha-to-coverage transparency rendering)")
    parser.add_argument("--debugopengl", action="store_true", help="enable OpenGL error checking and logging (slow)")
    parser.add_argument("--fullloggingopengl", action="store_true", help="log all OpenGL calls (very slow)")
    parser.add_argument("--debugnumpy", action="store_true", help="enable numpy runtime error messages")

    if not isRelease():
        parser.add_argument("-t", "--runtests", action="store_true", help="run test suite (for developers)")

    # optional positional arguments
    parser.add_argument("mhmFile", default=None, nargs='?', help=".mhm file to load (optional)")

    argOptions = vars(parser.parse_args())

    if argOptions.get('license', False):
        print("\n" + getCopyrightMessage() + "\n")
        sys.exit(0)

    return argOptions

def getCopyrightMessage(short=False):
    if short:
        return """MakeHuman Copyright (C) 2001-2020 http://www.makehumancommunity.org
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions. For details use the option --license"""

    return """Makehuman is a completely free, open source, innovative and
professional software for the modelling of 3-Dimensional humanoid characters
Copyright (C) 2001-2020  www.makehumancommunity.org

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

The MakeHuman source code is released under the AGPL license.
The graphical assets bundled with MakeHuman have been released as CC0.

A human readable explanation of the license terms can be found via
the MakeHuman home page:

    http://www.makehumancommunity.org

Licenses for dependencies are included in the licenses folder.

Frequently asked questions are found at:

    http://www.makehumancommunity.org/wiki/FAQ:Index

For further help, have a look in the community wiki at:

    http://www.makehumancommunity.org/wiki/Main_Page

If you have other questions or need support, feel free to ask on our
forums at:

    http://www.makehumancommunity.org/forum/

The forums is also where you can contact the MakeHuman team.

Bugs can be reported on the project's bug tracker(s):

    http://www.makehumancommunity.org/content/bugtracker.html
"""


class LicenseInfo(object):
    """
    License information for MakeHuman assets.
    Assets bundled with the official MakeHuman binary have been released as CC0.
    Assets created by third parties can be bound to different licensing conditions,
    which is why properties can be set as a dict of format:
        {"author": ..., "license": ..., "copyright": ..., "homepage": ...}
    """

    def __init__(self):
        """Create the default MakeHuman asset license. Can be modified for
        user-created assets.
        """
        self.author = "MakeHuman Team"
        self.license = "CC0"
        self.homepage = "http://www.makehumancommunity.org"
        self.copyright = "(c) www.makehumancommunity.org 2001-2020"
        self._keys = ["author", "license", "copyright", "homepage"]
        self._customized = False

    @property
    def properties(self):
        return list(self._keys)

    def setProperty(self, name, value):
        if name in self._keys:
            if getattr(self, name) != value:
                self._customized = True
                object.__setattr__(self, name, value)

    def __setattr__(self, name, value):
        # Assume that the LicenseInfo is not yet inited until self._customized is set
        if not hasattr(self, '_customized'):
            object.__setattr__(self, name, value)
            return
        if not hasattr(self, name):
            raise KeyError("Not allowed to add new properties to LicenseInfo")
        if name in self._keys:
            self.setProperty(name, value)
        else:
            object.__setattr__(self, name, value)

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
        for prop,val in list(propDict.items()):
            self.setProperty(prop, val)
        return self

    def fromJson(self, json_data):
        for prop in self.properties:
            if prop in json_data:
                self.setProperty(prop, json_data[prop])
        return self

    def copy(self):
        result = LicenseInfo()
        result.fromDict(self.asDict())
        result._customized = self.isCustomized()
        return result

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

        key = words[0].rstrip(":")
        value = " ".join(words[1:])

        self.setProperty(key,value)

    def toNumpyString(self):
        def _packStringDict(stringDict):
            import numpy as np
            text = ''
            index = []
            for key,value in list(stringDict.items()):
                index.append(len(key))
                index.append(len(value))
                text += key + value
            text = np.fromstring(text, dtype='S1')
            index = np.array(index, dtype=np.uint32)
            return np.array([text, index], dtype=object)

        return _packStringDict(self.asDict())

    def fromNumpyString(self, text, index=None):
        def _unpackStringDict(text, index):
            stringDict = dict()
            last = 0
            for i in range(0,len(index), 2):
                l_key = index[i]
                l_val = index[i+1]

                key = str(text[last:last+l_key].tostring(), 'utf8')
                val = str(text[last+l_key:last+l_key+l_val].tostring(), 'utf8')
                stringDict[key] = val

                last += (l_key + l_val)
            return stringDict

        if index is None:
            text, index = text
        return self.fromDict( _unpackStringDict(text, index) )


def getAssetLicense(properties=None):
    """
    Retrieve the license information for MakeHuman assets.
    Assets bundled with the official MakeHuman binary have been released as CC0.
    Assets created by third parties can be bound to different licensing conditions,
    which is why properties can be set as a dict of format:
        {"author": ..., "license": ..., "copyright": ..., "homepage": ...}
    """
    result = LicenseInfo()
    if properties is not None:
        result.fromDict(properties)
        result._customized = False
    return result

def _wordwrap(text, chars_per_line=80):
    """Split the lines of a text between whitespaces when a line length exceeds
    the specified number of characters. Newlines already present in text are
    kept.
    """
    text_ = text.split('\n')
    text = []
    for l in text_:
        if len(l) > chars_per_line:
            l = l.split()
            c = 0
            i = 0
            _prev_i = 0
            while i < len(l):
                while c <= chars_per_line and i < len(l):
                    c += len(l[i])
                    if i < (len(l) - 1):
                        c += 1  # whitespace char
                    i += 1
                if c > chars_per_line:
                    i -= 1
                text.append(' '.join(l[_prev_i:i]))
                _prev_i = i
                c = 0
        else:
            text.append(l)
    # drop any trailing empty lines
    while not text[-1].strip():
        text.pop()
    return '\n'.join(text)

def getSoftwareLicense(richtext=False):
    import getpath
    from io import open
    lfile = getpath.getSysPath('license.txt')
    if not os.path.isfile(lfile):
        if richtext:
            return '\n<span style="color: red;">Error: License file %s is not found, this is an incomplete MakeHuman distribution!</span>\n' % lfile
        else:
            return "Error: License file %s is not found, this is an incomplete MakeHuman distribution!" % lfile
    f = open(lfile, encoding='utf-8')
    text = f.read()
    f.close()
    if richtext:
        result = '<h2>MakeHuman software license</h2>'
    else:
        result = ""
    return result + _wordwrap(text)

def getThirdPartyLicenses(richtext=False):
    import getpath
    from collections import OrderedDict
    def _title(name, url, license):
        if richtext:
            return '<a id="%s"><h3>%s</h3></a>%s<br>Licensed under %s license.<br>' % (name, name, url, license)
        else:
            return "%s (%s) licensed under %s license." % (name, url, license)

    def _error(text):
        if richtext:
            return '<span style="color: red;">%s</span>' % text
        else:
            return text

    def _block(text):
        if richtext:
            return '%s<hr style="border: 1px solid #ffa02f;">' % text
            #return '%s<div style="border: none; background-color #ffa02f; height: 1px; width: 100%%">a</div>' % text
        else:
            return text

    if richtext:
        result = '<h2>Third-party licenses</h2>'
    else:
        result = ""
    result += """MakeHuman includes a number of third part software components, which have
their own respective licenses. We express our gratitude to the developers of
those libraries, without which MakeHuman would not have been made possible.
Here follows a list of the third-party open source libraries that MakeHuman
makes use of.\n"""
    license_folder = getpath.getSysPath('licenses')
    if not os.path.isdir(license_folder):
        return result + _error("Error: external licenses folder is not found, this is an incomplete MakeHuman distribution!")
    external_licenses = [ ("PyQt5", ("pyQt5-license.txt", "http://www.riverbankcomputing.com", "GPLv3")),
                          ("Qt5", ("qt5-license.txt", "http://www.qt.io", "GPLv3")),
                          ("Numpy", ("numpy-license.txt", "http://www.numpy.org", "BSD (3-clause)")),
                          ("PyOpenGL", ("pyOpenGL-license.txt", "http://pyopengl.sourceforge.net", "BSD (3-clause)")),
                          ("Transformations", ("transformations-license.txt", "http://www.lfd.uci.edu/~gohlke/", "BSD (3-clause)")),
                          ("pyFBX", ("pyFbx-license.txt", "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Import-Export/Autodesk_FBX", "GPLv2"))
                        ]
    external_licenses = OrderedDict(external_licenses)

    for name, (lic_file, url, lic_type) in external_licenses.items():
        result += _title(name, url, lic_type)

        lfile = os.path.join(license_folder, lic_file)
        if not os.path.isfile(lfile):
            result += "\n%s\n" % _error("Error: License file %s is not found, this is an incomplete MakeHuman distribution!" % lfile)
            continue
        with open(lfile, encoding='utf-8') as f:
            text = f.read()

        text = _wordwrap(text)
        result += "\n%s\n" % _block(text)

    return result

def getCredits(richtext=False):
    import getpath

    def _error(text):
        if richtext:
            return '<span style="color: red;">%s</span>' % text
        else:
            return text

    def _block(text):
        if richtext:
            return '%s<hr style="border: 1px solid #ffa02f;">' % text
        else:
            return text

    license_folder = getpath.getSysPath('licenses')
    cfile = os.path.join(license_folder, "credits.txt")
    if not os.path.isfile(cfile):
        return ( _error("Error: Credits file %s is not found, this is an incomplete MakeHuman distribution!" % cfile))
    with open(cfile, encoding='utf-8') as f:
        text = f.read()

    text = _wordwrap(text)
    return( _block(text))

def main():
    print(getCopyrightMessage(short=True) + "\n")

    try:
        set_sys_path()
        make_user_dir()
        get_platform_paths()
        redirect_standard_streams()
        os.environ['MH_VERSION'] = getVersionStr()
        os.environ['MH_SHORT_VERSION'] = getShortVersion()
        os.environ['MH_MESH_VERSION'] = getBasemeshVersion()
        args = parse_arguments()
        init_logging()
    except Exception as e:
        print("error: " + format(str(e)), file=sys.stderr)
        import traceback
        bt = traceback.format_exc()
        print(bt, file=sys.stderr)
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
