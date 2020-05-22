#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Joel Palmius

**Copyright(c):**      MakeHuman Team 2001-2020

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
import json

class MHVersion:

    def __init__(self, versionPath = None):

        self.currentShortCommit = "UNKNOWN"
        self.currentLongCommit = "UNKNOWN"
        self.currentBranch = "UNKNOWN"
        self.title = "MakeHuman Community"
        self.version = makehuman.getVersionDigitsStr()
        self.versionSub = makehuman.getVersionSubStr()
        self.isRelease = makehuman.isRelease()
        self.fullTitle = None
        self.versionPath = versionPath

        self._checkForGitInfo()
        self._checkForVersionFile()

        if self.fullTitle is None:
            if self.isRelease:
                self.fullTitle = self.title + " " + self.version
            else:
                self.fullTitle = self.title + " " + self.getFullVersionStr()

    def getFullVersionStr(self):
        return "{:s} {:s} ({:s}:{:s})".format(self.version, self.versionSub, self.currentBranch, self.currentShortCommit)

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

            commit = gitutils.getCurrentCommit(False)
            if not commit is None:
                self.currentLongCommit = commit

    def _checkForVersionFile(self):
        path = self.versionPath
        if path is None:
            path = getpath.getSysDataPath("VERSION")

        if os.path.exists(path):
            jsonin = None
            with open(path, 'r', encoding='utf-8') as f:
                jsonin = json.load(f)

            if not jsonin is None:
                if "currentShortCommit" in jsonin:
                    self.currentShortCommit = jsonin["currentShortCommit"]

                if "currentLongCommit" in jsonin:
                    self.currentLongCommit = jsonin["currentLongCommit"]

                if "currentBranch" in jsonin:
                    self.currentBranch = jsonin["currentBranch"]

                if "title" in jsonin:
                    self.title = jsonin["title"]

                if "version" in jsonin:
                    self.version = jsonin["version"]

                if "isRelease" in jsonin:
                    self.isRelease = jsonin["isRelease"]

    def writeVersionFile(self, overrideVersionPath=None):
        path = overrideVersionPath
        if path is None:
            path = self.versionPath
        if path is None:
            path = getpath.getSysDataPath("VERSION")

        out = dict()

        if not self.currentShortCommit is None and not self.currentShortCommit == "UNKNOWN":
            out["currentShortCommit"] = self.currentShortCommit

        if not self.currentLongCommit is None and not self.currentLongCommit == "UNKNOWN":
            out["currentLongCommit"] = self.currentLongCommit

        if not self.currentBranch is None and not self.currentBranch == "UNKNOWN":
            out["currentBranch"] = self.currentBranch

        if not self.title is None and not self.title == "MakeHuman Community":
            out["title"] = self.title

        if not self.version is None:
            out["version"] = self.version

        if not self.isRelease is None:
            out["isRelease"] = self.isRelease

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(out,f, sort_keys=True, indent=4)

