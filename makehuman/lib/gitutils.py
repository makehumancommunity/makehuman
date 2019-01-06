#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Jonas Hauquier, Glynn Clements, Joel Palmius, Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2019

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

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

Utility module for various git routines
"""

import sys
import os
import getpath
import subprocess
import io

_gitcmd = None
_gitdir = None

def findPathToGit():

    global _gitcmd
    global _gitdir

    if not _gitcmd is None:
        return _gitcmd

    if 'GIT_COMMAND' in os.environ:
        _gitcmd = os.environ['GIT_COMMAND']
        return _gitcmd

    if sys.platform.startswith('win'):
        _findPathToGitWindows()
    else:
        _findPathToGitUnixoid()

    return _gitcmd

def _findPathToGitWindows():

    global _gitcmd
    global _gitdir

    for path in os.environ["PATH"].split(os.pathsep):
        path = path.strip('"')
        exe_file = os.path.join(path, 'git.exe')
        if os.path.isfile(exe_file):
            _gitcmd = os.path.abspath(exe_file)

def _findPathToGitUnixoid():

    global _gitcmd
    global _gitdir

    for path in os.environ["PATH"].split(os.pathsep):
        path = path.strip('"')
        exe_file = os.path.join(path, 'git')
        if os.path.isfile(exe_file):
            _gitcmd = os.path.abspath(exe_file)    

def findGitDir():

    global _gitcmd
    global _gitdir

    if not _gitdir is None:
        return _gitdir

    main = getpath.getSysPath()

    # If running from source, we're one subdir down from .git

    main = os.path.join(main, '..', '.git')
    main = os.path.abspath(main)

    if os.path.isdir(main):
        _gitdir = main

    return _gitdir

def _setup():

    global _gitcmd
    global _gitdir

    if _gitdir is None:
        findGitDir()
    if _gitcmd is None:
        findPathToGit()

def getBranchFromFile():

    global _gitdir

    branch = None

    if _gitdir:

        headFile = os.path.join(_gitdir, 'HEAD')

        if os.path.isfile(headFile):

            with io.open(headFile,'r', encoding='utf-8') as f:
                line = f.readline()
                if line:
                    if line.startswith('ref'):
                        branch = line.split('/')[-1].strip()
                    else:
                        branch = 'HEAD'

    return branch

def getCommitFromFile(short = True):

    global _gitdir

    branch = getBranchFromFile()
    commit = None

    if _gitdir and branch:

        if branch == 'HEAD':
            commitFile = os.path.join(_gitdir, 'HEAD')
        else:
            commitFile = os.path.join(_gitdir, 'refs', 'heads', branch)

        if os.path.isfile(commitFile):

            with io.open(commitFile, 'r', encoding='utf-8') as f:
                commit = f.readline().strip()

    if short and commit:
        return commit[:8]
    else:
        return commit


def getCurrentBranch():

    global _gitcmd
    global _gitdir

    _setup()

    branch = None

    if _gitcmd is None:

        if _gitdir:
            branch = getBranchFromFile()
            return branch

        else:
            return None

    args = [_gitcmd, "rev-parse", "--abbrev-ref", "HEAD"]


    try:
        branch = subprocess.check_output(args)
        branch = branch.decode('utf-8')
        branch = branch.strip()

        if "fatal:" in branch:
            return None

    except Exception as e:
        print(e)
        branch = None

    return branch

def getCurrentCommit(short = True):

    global _gitcmd
    global _gitdir

    _setup()

    if _gitcmd is None:

        if _gitdir:
            commit = getCommitFromFile(short)
            return commit
        else:
            return None

    args = [_gitcmd, "rev-parse"]
    if short:
        args.append("--short")
    args.append("HEAD")

    commit = None

    try:
        commit = subprocess.check_output(args)
        commit = commit.decode('utf-8')
        commit = commit.strip()

        if "fatal:" in commit:
            return None

    except Exception as e:
        print(e)
        commit = None

    return commit

def hasGitLFSSupport():

    global _gitcmd
    global _gitdir

    args = [_gitcmd,"lfs","install"]

    try:
        subprocess.check_call(args)
    except Exception as e:
        print(e)
        return False

    return True
 
def cloneRepo(repoUrl,repoDest,branch="master"):

    global _gitcmd
    global _gitdir

    currentwd = os.getcwd()

    args = [_gitcmd,"clone",repoUrl,repoDest]
    subprocess.check_call(args)

    os.chdir(repoDest)

    args = [_gitcmd,"checkout",branch]
    subprocess.check_call(args)

    os.chdir(currentwd)

def pullRepo(repoLoc,branch="master"):

    global _gitcmd
    global _gitdir

    currentwd = os.getcwd()
    os.chdir(repoLoc)

    args = [_gitcmd,"checkout",branch]
    subprocess.check_call(args)

    args = [_gitcmd,"pull","origin",branch]
    subprocess.check_call(args)

    os.chdir(currentwd)


