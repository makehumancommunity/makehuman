#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MakeHuman source tree end-of-line (EOL) verification

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Validate the MH source code and detect and report any files containing windows
line endings.
"""

import sys
import os
import mimetypes

EXCLUDE_FOLDERS = ['.hg']

mimetypes.add_type('text/mhfile', '.mhclo')
mimetypes.add_type('text/mhfile', '.proxy')
mimetypes.add_type('text/mhfile', '.mhmat')
mimetypes.add_type('text/mhfile', '.obj')
mimetypes.add_type('text/mhfile', '.json')
mimetypes.add_type('text/mhfile', '.mhm')
mimetypes.add_type('text/mhfile', '.bvh')
mimetypes.add_type('text/mhfile', '.rig')
mimetypes.add_type('text/mhfile', '.target')

def check_dos_eol(path):
    global _recurse_files
    result = []
    for f in _recurse_get_ascii_files(path):
        if "\r\n" in open(f, 'rb').read():
            result.append( f )
    return result

def fix_dos_eol(filepaths):
    for f in filepaths:
        fh = open(f, 'rb')
        contents = fh.read()
        fh.close()
        contents = contents.replace('\r\n', '\n')
        contents = contents.replace('\r', '\n')
        fh = open(f, 'wb')
        fh.write(contents)
        fh.close()

def _isASCII(filepath):
    mtype = mimetypes.guess_type(filepath)[0]
    if mtype:
        return mtype.split("/")[0] == "text"
    else:
        return None

def _recurse_get_ascii_files(path, result = None):
    """
    Recurse specified path, return list of all files.
    """
    global _isASCII
    if result is None:
        result = []
    if os.path.isdir(path):
        if os.path.basename(path) not in EXCLUDE_FOLDERS:
            files = os.listdir(path)
            for f in files:
                _recurse_get_ascii_files(os.path.join(path, f), result)
    elif os.path.isfile(path):
        if _isASCII(path):
            result.append(path)
    return result


def _parse_args():
    if len(sys.argv) < 2:
        return dict()

    import argparse    # requires python >= 2.7
    parser = argparse.ArgumentParser()

    # optional arguments
    parser.add_argument("--fix", action="store_true", help="Fix line endings of encountered files")

    # positional arguments
    parser.add_argument("path", default=None, nargs='?', help="Path to folder or file to check")

    argOptions = vars(parser.parse_args())
    return argOptions


if __name__ == '__main__':
    args = _parse_args()

    if args.get('path', None) is None:
        raise RuntimeError("path argument not specified")

    path = args['path']
    fix = args.get('fix', False)
    print "Files containing DOS line endings:"
    detected = check_dos_eol(path)
    print "\n".join( detected )

    if fix:
        print "\nFixing files..."
        fix_dos_eol(detected)
        print "All done"
