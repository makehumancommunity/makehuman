#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MakeHuman python entry-point.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Joel Palmius

**Copyright(c):**      MakeHuman Team 2016 - 2019

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

This file downloads asset from github

"""

import sys
import os
import subprocess
import shutil

__author__ = "Joel Palmius"
__copyright__ = "Copyright 2017 Data Collection AB and listed authors"
__license__ = "AGPLv3"
__maintainer__ = "Joel Palmius"

syspath = ["./", "./lib", "./apps", "./shared", "./apps/gui","./core"]
syspath.extend(sys.path)
sys.path = syspath

import getpath
import gitutils

class DownloadAssetsGit:

    _git_official_assets_repo = "https://github.com/makehumancommunity/makehuman-assets.git"
    _git_official_assets_branch = "master"

    _makehuman_data_directory = os.path.abspath(os.path.realpath(getpath.getSysDataPath()))

    _user_dir = None
    _user_data_dir = None

    _git_official_clone_location = None

    _git_command = "git"

    _dry_run = True
    _copy_debug_assets = False

    def __init__(self):

        self._git_command = gitutils.findPathToGit()

        self._user_dir = getpath.getPath()
        if not os.path.isdir(self._user_dir):
            os.makedirs(self._user_dir)

        self._user_data_dir = getpath.getDataPath()
        if not os.path.isdir(self._user_data_dir):
            os.makedirs(self._user_data_dir)
            
        self._git_official_clone_location = os.path.abspath(os.path.realpath(os.path.join(self._user_dir,'official_assets')))

        self.readOverridesFromEnvironment()

        if not os.path.isfile(self._git_command):
            print("\n\n\nCould not find git command\n\n")
            sys.exit(1)

        if not gitutils.hasGitLFSSupport():
            print("\n\n\nGIT LFS not detected. This routine requires LFS. See https://git-lfs.github.com/\n\n")
            sys.exit(1)

        if os.path.isdir(self._git_official_clone_location):
            gitutils.pullRepo(self._git_official_clone_location,self._git_official_assets_branch)
        else:
            gitutils.cloneRepo(self._git_official_assets_repo,self._git_official_clone_location,self._git_official_assets_branch)

        self.copyOfficialAssets()

    def copyOfficialAssets(self):

        os.chdir(self._git_official_clone_location)

        for root, dirs, files in os.walk('base'): 
            
            for name in dirs:
                fullname = name
                if root != "base":
                    fullname = os.path.relpath(os.path.join(root,name),os.path.join(self._git_official_clone_location,"base"))
                dest = os.path.join(self._makehuman_data_directory,fullname)
                if not os.path.isdir(dest):
                    print("Creating directory " + dest)
                    os.makedirs(dest)

            for name in files:
                fullname = name
                if root != "base":
                    a = os.path.abspath(os.path.join(root,name))
                    b = os.path.abspath(os.path.join(self._git_official_clone_location,"base"))
                    fullname = os.path.relpath(a,b)

                source = os.path.abspath(os.path.join(self._git_official_clone_location,"base",fullname))
                dest = os.path.abspath(os.path.join(self._makehuman_data_directory,fullname))

                print("copying " + source + " to " + dest)
                shutil.copy2(source,dest)

        if self._copy_debug_assets:

            for root, dirs, files in os.walk('debug'): 
            
                for name in dirs:
                    fullname = name
                    if root != "debug":
                        fullname = os.path.relpath(os.path.join(root,name),os.path.join(self._git_official_clone_location,"debug"))
                    dest = os.path.join(self._makehuman_data_directory,fullname)
                    if not os.path.isdir(dest):
                        print("Creating directory " + dest)
                        os.makedirs(dest)
    
                for name in files:
                    fullname = name
                    if root != "debug":
                        fullname = os.path.relpath(os.path.join(root,name),os.path.join(self._git_official_clone_location,"debug"))
    
                    source = os.path.abspath(os.path.join(self._git_official_clone_location,"debug",fullname))
                    dest = os.path.abspath(os.path.join(self._makehuman_data_directory,fullname))
    
                    print("copying " + source + " to " + dest)
                    shutil.copy2(source,dest)


    def readOverridesFromEnvironment(self):

        if 'GIT_OFFICIAL_ASSETS_REPO' in os.environ:
            self._git_official_assets_repo = os.environ['GIT_OFFICIAL_ASSETS_REPO']

        if 'GIT_OFFICIAL_ASSETS_BRANCH' in os.environ:
            self._git_official_assets_branch = os.environ['GIT_OFFICIAL_ASSETS_BRANCH']

        if 'MAKEHUMAN_DATA_DIRECTORY' in os.environ:
            self._makehuman_data_directory = os.environ['MAKEHUMAN_DATA_DIRECTORY']

        if 'GIT_OFFICIAL_CLONE_LOCATION' in os.environ:
            self._git_official_clone_location = os.environ['GIT_OFFICIAL_CLONE_LOCATION']

        if 'DRY_RUN' in os.environ:
            self._dry_run = True

        if 'COPY_DEBUG_ASSETS' in os.environ:
            self._copy_debug_assets = True


DownloadAssetsGit()

