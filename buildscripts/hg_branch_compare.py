#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Mercurial branch compare and graft tool

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Tool for comparing the differences in changesets between two branches for
grafting selected changesets to the other.

Exclusions are changesets that are decided not to be merged with stable yet, and
are postponed to a next release. These are stored in graft_exclude.conf file.
"""

import hglib
from hglib.util import cmdbuilder
import re
import os

def compare(sourceBranch="default", targetBranch="stable"):
    excludeFile = None
    excludes = []
    if os.path.isfile('graft_exclude.conf'):
        excludeFile = 'graft_exclude.conf'
    elif os.path.isfile('buildscripts/graft_exclude.conf'):
        excludeFile = 'buildscripts/graft_exclude.conf'

    if excludeFile:
        for L in open(excludeFile, 'r'):
            L = L.strip()
            if L:
                if L.startswith('#'):
                    continue
                Ls = L.split()
                if len(Ls[0]) > 12:
                    Ls[0] = Ls[0][:12]
                excludes.append(Ls[0])
        print 'Loaded %s exclusions from %s\n' % (len(excludes), excludeFile)

    try:
        # Try if cwd is buildscripts/ folder
        c = hglib.open('../')
    except:
        # Try whether we are in hg root folder
        c = hglib.open('.')

    # Difference in changesets between branches
    cDiff = c.log("ancestors(%s) and not ancestors(%s)" % (sourceBranch, targetBranch))

    # Filter out already grafted commits
    stdOut = c.rawcommand(cmdbuilder('log', debug=True, b=targetBranch))
    grafted = []
    r = re.compile('.*source=([a-zA-Z0-9]*)')
    for outL in stdOut.split('\n'):
        if outL.strip().startswith('extra') and ' source=' in outL:
            sourceRev = r.match(outL).groups()[0]
            grafted.append(sourceRev)

    # Filtered result
    return [cs for cs in cDiff if (cs.node not in grafted and cs.node[:12] not in excludes)]


def formatChangeset(cs):
    return """changeset:   %s
revision:    %s
user:        %s
date:        %s
description:
%s""" % (cs.node[:12], cs.rev, cs.author, cs.date, cs.desc)



def _parse_args():
    if len(sys.argv) < 2:
        return dict()

    import argparse    # requires python >= 2.7
    parser = argparse.ArgumentParser()

    # optional arguments
    parser.add_argument("--graft", action="store_true", help="Generate graft command for merging remaining changesets")
    parser.add_argument("--sourceBranch", default="default", nargs='?', help="Branch to pick commits from")
    parser.add_argument("--targetBranch", default="stable", nargs='?', help="Branch to merge commits to")

    argOptions = vars(parser.parse_args())
    return argOptions


if __name__ == '__main__':
    import sys
    args = _parse_args()

    sourceBranch=args.get("sourceBranch", "default")
    targetBranch=args.get("targetBranch", "stable")

    result = compare(sourceBranch, targetBranch)

    if args.get('graft', False):
        import subprocess
        print 'To graft %s changesets from %s to %s, execute:' % (len(result), sourceBranch, targetBranch)
        revs = [r.node for r in result]
        dargs = [item for pair in zip(len(revs)*['-D'], revs) for item in pair]
        print 'hg graft %s' % " ".join(dargs)

        print "\n\nSummary:\n--------\n"

    for r in result:
        print formatChangeset(r)
        print '\n'

