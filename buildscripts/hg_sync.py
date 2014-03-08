#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MakeHuman build HG synch

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Synchronize local hg copy to latest upstream version before building MakeHuman
nightly or release package
"""

import os

HG_REPO = "https://bitbucket.org/MakeHuman/makehuman"

def sync(hgRoot, hgUrl=None)
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
