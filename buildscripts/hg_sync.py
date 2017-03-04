#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
MakeHuman build HG synch

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2015

**Licensing:**         AGPL3

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


Abstract
--------

Synchronize local hg copy to latest upstream version before building MakeHuman
nightly or release package
"""

import os
import sys

HG_REPO = "https://bitbucket.org/MakeHuman/makehuman"

def sync(hgRoot, hgUrl=None):
    if not os.path.isdir(hgRoot):
        raise RuntimeError('Faulty hg root repository , folder does not exist (%s)' % hgRoot)

    print "Synching with HG repository"

    if hgUrl is None:
        hgrepo = HG_REPO
    else:
        hgrepo = hgUrl
        print "Pulling from alternate repository %s" % hgUrl

    cwd = os.path.normpath(os.path.realpath( hgRoot ))
    try:
        # Try with python-hglib
        import hglib
        print "Using python-hglib"
        hgclient = hglib.open(cwd)
        branch = hgclient.branch()
        print "HG using branch %s" % branch
        if not hgclient.pull(update=True):
            print "Failed to pull -u using hglib"
            raise RuntimeError("Failed to pull -u using hglib")
    except:
        # If hglib is not installed, resort to commandline calls
        print "Using hg commandline tools"
        import subprocess
        branch = subprocess.Popen(["hg","-q","branch"], stdout=subprocess.PIPE, stderr=sys.stderr, cwd=cwd).communicate()[0].strip()
        print "HG using branch %s" % branch
        subprocess.check_call(["hg", "pull", "-u", hgrepo], cwd=cwd)

def _parse_args():
    if len(sys.argv) < 2:
        return dict()

    import argparse    # requires python >= 2.7
    parser = argparse.ArgumentParser()

    # positional arguments
    parser.add_argument("hgpath", default=None, nargs='?', help="Root path of HG source repository")

    # optional positional arguments
    parser.add_argument("hgurl", default=None, nargs='?', help="URL to upstream HG repo (optional)")

    argOptions = vars(parser.parse_args())
    return argOptions


if __name__ == '__main__':
    args = _parse_args()

    if args.get('hgpath', None) is None:
        raise RuntimeError("hgpath argument not specified")

    print sync(args['hgpath'], args.get('hgurl', None))
