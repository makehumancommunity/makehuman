#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius

**Copyright(c):**      MakeHuman Team 2001-2017

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

Utility module for getting version information about makehuman
"""

import sys
import os
import getpath
import subprocess
import gitutils
import makehuman

class MHVersion:

    def __init__(self):

        self.currentShortCommit = "UNKNOWN"
        self.currentLongCommit = "UNKNOWN"
        self.currentBranch = "UNKNOWN"
        self.title = "MakeHuman Community"
        self.version = makehuman.getVersionDigitsStr()
        self.isRelease = makehuman.isRelease()
        self.fullTitle = None

        self._checkForGitInfo()
        self._checkForVersionFile()

        if self.fullTitle is None:
            if self.isRelease:
                self.fullTitle = self.title + " " + self.version
            else:
                self.fullTitle = self.title + " (" + self.currentBranch + ":" + self.currentShortCommit + ")"

    def _checkForGitInfo(self):

        gd = gitutils.findGitDir()
        if not gd is None:
            # There is a .git dir. Assume we're running from source

            self.isRelease = False

            branch = gitutils.getCurrentBranch()
            if not branch is None:
                self.currentBranch = branch

            commit = gitutils.getCurrentCommit(True)
            if not commit is None:
                self.currentShortCommit = commit

    def _checkForVersionFile(self):
        pass
