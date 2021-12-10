#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MakeHuman build prepare

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Jonas Hauquier, Joel Palmius

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

Prepares an export folder ready to build packages from.
"""

### Configuration ##############################################################

# Path to git executable
GIT_PATH = "git"

# Path to hg executable
HG_PATH = "hg"

# Filter of files from source folder to exclude (glob syntax)
EXCLUDES = ['.gitignore','.hgignore', '.hgtags', '.hgeol', '*.target', '*.obj', '*.pyc', '*.mhclo', '*.proxy', '*.pyd', 'maketarget-standalone', 'plugins/4_rendering_mitsuba', 'plugins/4_rendering_povray', 'plugins/4_rendering_aqsis.py', 'plugins/0_modeling_5_editing.py', 'compile_*.py', 'build_prepare.py', 'download_assets.py', 'download_assets_git.py', '*~', '*.bak', 'setup.nsi', 'clean*.sh', 'makehuman.sh', 'makehuman/makehuman', 'pylintrc', 'clean*.bat', 'makehuman/docs', 'makehuman/icons/*psd', 'makehuman/icons/*bmp', 'makehuman/icons/*ico', 'makehuman/icons/*icns', 'makehuman/icons/*xcf', 'makehuman/icons/makehuman.svg', 'makehuman.rc', '*_contents.txt', 'buildscripts', '.build_prepare.out']
# Same as above, but applies to release mode only
EXCLUDES_RELEASE = ['testsuite']

# Include filter for additional asset files (not on hg) to copy (glob syntax)
ASSET_INCLUDES = ['*.npz', '*.mhpxy', '*.list', '*.thumb', '*.png', '*.json', '*.csv', '*.meta', '*.mhskel', '*.mhw', '*.mhmat', '*.mhclo', '*.proxy', 'glsl/*.txt', 'languages/*.ini', "*.bvh", "*.mhm", "*.qss", "*.mht", "*.svg", "*.mhpose", "icons/makehuman_bg.svg", "icons/makehuman.png", "logging.ini"]

# Even if empty, create these folders (relative to export path)
CREATE_FOLDERS = ['makehuman/data/backgrounds', 'makehuman/data/clothes', 'makehuman/data/teeth', 'makehuman/data/eyelashes', 'makehuman/data/tongue']

# Files and folders to exclude as a last step, to correct things that still fall through, but shouldn't (relative path to export path, no wildcards allowed) For example folders affected during build
POST_REMOVE = ['makehuman/docs', 'buildscripts', 'maketarget-standalone']

# Finally copy all files from these source folders, effectively ignoring all exclude filters
COPY_ALL = ['blendertools']

# Root folder after rearranging all. All folders in root except this one will be copied inside this folder, as new root.
REARRANGE_ROOT_FOLDER = 'makehuman'


# == Following settings relate to freezing a py package, paths are referenced in rearranged folder state, relative to REARRANGE_ROOT_FOLDER ==

# Files and paths that have to be declared as data (when freezing)
DATAS = ['blendertools', 'data', 'plugins', 'license.txt', 'licenses', 'icons']

# Entry point for the MakeHuman application
MAIN_EXECUTABLE = 'makehuman.py'

# Extension to python path, folders containing MH modules
PYTHON_PATH_EX = ['lib','core','shared','apps','apps/gui', 'plugins']


################################################################################

# TODO copies could be made more efficient with rsync

import sys
import os
import subprocess
import shutil
import inspect

pth = os.path.dirname(inspect.stack()[0][1])

syspath = ["../makehuman","../makehuman/lib","../makehuman/apps","../makehuman/shared","../makehuman/core"]
syspath2 = []
for p in syspath:
    syspath2.append( os.path.abspath( os.path.join(pth, p) ) )
syspath2.extend(sys.path)
sys.path = syspath2

import getpath
import gitutils
import mhversion


VERSION_FILE_PATH = 'makehuman/data/VERSION'
BUILD_CONF_FILE_PATH = 'buildscripts/build.conf'



class MHAppExporter(object):
    def __init__(self, sourceFolder, exportFolder='export', skipScripts=False, noDownload=False):
        self.sourceFolder = sourceFolder
        self.targetFolder = exportFolder
        self.skipScripts = skipScripts
        self.noDownload = noDownload
        self.assetRepoLocation = None

        sys.path = [self.sourceFile('makehuman'), self.sourceFile('makehuman/lib')] + sys.path

        self.configure()

    def configure(self):
        self.HGREV = self.REVID = None
        self.VERSION = None
        self.IS_RELEASE = None
        self.VERSION_SUB = None

        self.overrideTitle = None
        self.overrideVersion = None
        self.overrideGitBranch = None
        self.overrideGitCommit = None

        def _conf_get(config, section, option, defaultVal):
            try:
                return config.get(section, option)
            except:
                return defaultVal

        self.config = parseConfig(self.sourceFile(BUILD_CONF_FILE_PATH))
        if self.config is None:
            print("No config file at %s" % self.sourceFile(BUILD_CONF_FILE_PATH))
            sys.exit(1)
        else:
            print("Using config file at %s. NOTE: properties in config file will override any other settings!" % self.sourceFile(BUILD_CONF_FILE_PATH))

            global GIT_PATH

            GIT_PATH = _conf_get(self.config, 'General', 'gitPath', GIT_PATH)

            self.VERSION_SUB = _conf_get(self.config, 'BuildPrepare', 'versionSub', None)

            isRelease = _conf_get(self.config, 'BuildPrepare', 'isRelease', None)
            if isRelease is not None:
                self.IS_RELEASE = ( isRelease.lower() in ['yes', 'true'] )

            skipScripts = _conf_get(self.config, 'BuildPrepare', 'skipScripts', None)
            if skipScripts is not None:
                self.skipScripts = skipScripts.lower() in ['yes', 'true']

            noDownload = _conf_get(self.config, 'BuildPrepare', 'noDownload', None)
            if noDownload is not None:
                self.noDownload = noDownload.lower() in ['yes', 'true']

            self.assetRepoLocation = _conf_get(self.config, 'BuildPrepare', 'assetRepoLocation', None)
            self.overrideTitle = _conf_get(self.config, 'BuildPrepare', 'title', None)
            self.overrideVersion = _conf_get(self.config, 'BuildPrepare', 'version', None)
            self.overrideGitBranch = _conf_get(self.config, 'BuildPrepare', 'gitBranch', None)
            self.overrideGitCommit = _conf_get(self.config, 'BuildPrepare', 'gitCommit', None)

    def isRelease(self):
        if self.IS_RELEASE is not None:
            return self.IS_RELEASE

        import makehuman
        return makehuman.isRelease()

    def export(self):
        # Sanity checks
        if not os.path.isdir(self.sourceFile('.git')):
            raise RuntimeError("The root source folder %s is not valid, the source folder argument should be the root of the git repository." % self.sourceFile('.git'))
        if self.isSubPath(self.targetFile(), self.sourceFile()):
            raise RuntimeError("The export folder is a subfolder of the source folder, this is not allowed.")
        if os.path.exists(self.targetFile()):
            raise RuntimeError("An export folder called %s already exists" % self.targetFile())
        if not os.path.exists(self.sourceFile()):
            raise RuntimeError("Specified source folder %s does not exist" % self.sourceFile())
        if not os.path.isfile(self.sourceFile('makehuman/makehuman.py')):
            raise RuntimeError("The specified source folder %s does not appear to be a valid MakeHuman root folder (cannot find file %s)" % (self.sourceFile(), self.sourceFile('makehuman/makehuman.py')))

        print('Creating folder %s' % self.targetFile())
        os.makedirs(self.targetFile())

        print("Exporting")
        print("  from: %s" % self.sourceFile())
        print("  to:   %s\n" % self.targetFile())

        print("\n\n%s build\n\n" % ("RELEASE" if self.isRelease() else "NIGHTLY"))

        # Run scripts to prepare assets
        if not self.skipScripts:
            self.runScripts()

        self.exportGITFiles()

        print("\n")

        # Export other non-hg files
        self.exportCompiledAssets(self.sourceFile())
        print("\n")

        # Create extra folders
        print("Creating extra folders")
        for f in CREATE_FOLDERS:
            try:
                print(self.targetFile(f))
                os.makedirs(self.targetFile(f))
            except:
                pass
        print("\n")

        # Perform post-remove step
        print("Post removing excluded folders")
        for f in POST_REMOVE:
            if not os.path.exists(self.targetFile(f)):
                continue
            print("Post-removing excluded file from export folder %s" % f)
            if os.path.isdir(self.targetFile(f)):
                shutil.rmtree(self.targetFile(f))
            else:
                os.remove(self.targetFile(f))
        print("\n")

        # Perform post-copy step
        print("Post copying extra included files")
        for f in COPY_ALL:
            if not os.path.exists(self.sourceFile(f)):
                continue
            print("Post-including file or folder %s" % f)
            _recursive_cp(self.sourceFile(f), self.targetFile(f))
        print("\n")

        # If RELEASE status or version-sub was set in config, update it in exported mh source file
        if (self.IS_RELEASE is not None) or (self.VERSION_SUB is not None) :
            f = open(self.targetFile('makehuman/makehuman.py'), 'r')
            release_replaced = False
            versionsub_replaced = False
            lines = []
            for lIdx, line in enumerate(f):
                if self.IS_RELEASE is not None and not release_replaced and line.strip().startswith('release ='):
                    line = line.replace('release = True', 'release = %s' % self.IS_RELEASE)
                    line = line.replace('release = False', 'release = %s' % self.IS_RELEASE)
                    print("Replaced release declaration in makehuman/makehuman.py at line %s." % (lIdx+1))
                    release_replaced = True
                if self.VERSION_SUB is not None and not versionsub_replaced and line.strip().startswith('versionSub ='):
                    import re
                    line = re.sub(r'versionSub = ".*"','versionSub = "%s"' % self.VERSION_SUB, line)
                    print("Replaced version-sub declaration in makehuman/makehuman.py at line %s." % (lIdx+1))
                    versionsub_replaced = True
                lines.append(line)
            f.close()
            f = open(self.targetFile('makehuman/makehuman.py'), 'w')
            f.write(''.join(lines))
            f.close()
            print('\n')

        # Write VERSION file to export folder
        print("Writing data/VERSION file to export folder\n")
        self.writeVersionFile()

        # Re-arrange folders
        for f in os.listdir( self.targetFile() ):
            if f == REARRANGE_ROOT_FOLDER:
                continue
            path = self.targetFile(f)
            if os.path.isdir(path):
                # Move folder in new root folder
                print("Moving folder %s into new root %s" % (f, REARRANGE_ROOT_FOLDER))
                shutil.move(path, self.targetFile(os.path.join(REARRANGE_ROOT_FOLDER, f)))

        print("\n")

        resultInfo = ExportInfo(self.VERSION, self.targetFile(), self.isRelease())
        resultInfo.rootSubpath = REARRANGE_ROOT_FOLDER
        resultInfo.datas = [os.path.join(REARRANGE_ROOT_FOLDER, d) for d in DATAS]
        resultInfo.pathEx = [os.path.join(REARRANGE_ROOT_FOLDER, p) for p in PYTHON_PATH_EX]
        resultInfo.mainExecutable = os.path.join(REARRANGE_ROOT_FOLDER, MAIN_EXECUTABLE)

        # Write export info to file for easy retrieving by external processes
        f = open(self.sourceFile('.build_prepare.out'), 'wt')
        f.write(str(resultInfo))
        f.close()

        return resultInfo

    def sourceFile(self, path=""):
        return os.path.abspath(os.path.normpath( os.path.join(self.sourceFolder, path) ))

    def targetFile(self, path=""):
        return os.path.abspath(os.path.normpath( os.path.join(self.targetFolder, path) ))

    def getRevision(self):
        import makehuman
        return makehuman.get_hg_revision_1()

    def getVersion(self):
        import makehuman
        if self.VERSION_SUB is not None:
            makehuman.versionSub = self.VERSION_SUB
        if self.IS_RELEASE is not None:
            makehuman.release = self.IS_RELEASE

        return makehuman.getVersionStr(verbose=False)

    def getCWD(self):
        return os.path.normpath(os.path.realpath( os.path.join(self.sourceFolder, 'makehuman') ))

    def isSubPath(self, subpath, path):
        """
        Determines whether subpath is a sub-path of path, returns True if it is.
        """
        import getpath
        return getpath.isSubPath(subpath, path)

    def runProcess(self, args):
        print("Running %s from %s" % (args, self.getCWD()))
        return subprocess.check_call(args, cwd=self.getCWD())

    def runScripts(self):

        pythonCmd = shutil.which("python3")
        if pythonCmd is None:
            pythonCmd = shutil.which("python")
        if pythonCmd is None:
            pythonCmd = "python"

        if not self.noDownload:
            ###DOWNLOAD ASSETS
            try:
                if not self.assetRepoLocation is None:
                    os.environ["GIT_OFFICIAL_CLONE_LOCATION"] = self.assetRepoLocation
                self.runProcess( [pythonCmd,"download_assets_git.py"] )
            except subprocess.CalledProcessError:
                print("check that download_assets_git.py is working correctly")
                sys.exit(1)
            print("\n")

        ###COMPILE TARGETS
        try:
            self.runProcess( [pythonCmd,"compile_targets.py"] )
        except subprocess.CalledProcessError:
            print("check that compile_targets.py is working correctly")
            sys.exit(1)
        print("\n")

        ###COMPILE MODELS
        try:
            self.runProcess( [pythonCmd,"compile_models.py"] )
        except subprocess.CalledProcessError:
            print("check that compile_models.py is working correctly")
            sys.exit(1)
        print("\n")

        ###COMPILE PROXIES
        try:
            self.runProcess( [pythonCmd,"compile_proxies.py"] )
        except subprocess.CalledProcessError:
            print("check that compile_proxies.py is working correctly")
            sys.exit(1)
        print("\n")

    def getExcludes(self):
        if self.isRelease():
            return EXCLUDES + EXCLUDES_RELEASE
        else:
            return EXCLUDES

    def exportGITFiles(self):
        print("Exporting files from git repo")

        tf = self.targetFile()
        if os.path.exists(tf):
            shutil.rmtree(tf);

        shutil.copytree(self.sourceFile(),tf, ignore=shutil.ignore_patterns(".git",".idea","__pycache__"))

        files = []
        _recursive_glob(self.targetFile(), self.getExcludes(), files)
        for f in files:
            print("Removing excluded file from export folder %s" % f)
            if os.path.isdir(self.targetFile(f)):
                shutil.rmtree(self.targetFile(f))
            else:
                os.remove(self.targetFile(f))

    def exportCompiledAssets(self, path):
        print("Copying extra files in source tree")
        # Gather files
        files = []
        _recursive_glob(path, ASSET_INCLUDES, files)
        # Exclude files matching exclude patterns
        excludes = []
        _recursive_glob(path, self.getExcludes(), excludes)
        files = set(files).difference(excludes)

        # Copy them
        for f in files:
            targetDir = os.path.dirname(self.targetFile(f))
            if not os.path.isdir(targetDir):
                os.makedirs(targetDir)
            print("Copying %s" % self.sourceFile(f))
            shutil.copy(self.sourceFile(f), self.targetFile(f))

    def writeVersionFile(self):
        ### Write VERSION file
        versionFile = self.targetFile(VERSION_FILE_PATH)
        if not os.path.isdir(os.path.dirname( versionFile )):
            os.makedirs(os.path.dirname( versionFile ))

        mhv = mhversion.MHVersion()

        if not self.overrideVersion is None:
            mhv.version = self.overrideVersion

        if not self.overrideTitle is None:
            mhv.title = self.overrideTitle

        if not self.overrideGitBranch is None:
            mhv.currentBranch = self.overrideGitBranch

        if not self.overrideGitCommit is None:
            mhv.currentShortCommit = self.overrideGitcommit
            mhv.currentLongCommit = self.overrideGitcommit

        mhv.isRelease = (self.IS_RELEASE is not None) and self.IS_RELEASE

        mhv.writeVersionFile(versionFile)

class ExportInfo(object):
    def __init__(self, version, path, isRelease):

        mhv = mhversion.MHVersion()

        self.version = version
        self.branch = mhv.currentBranch
        self.commit = mhv.currentShortCommit
        self.path = os.path.abspath(path)
        self.isRelease = isRelease
        self.datas = []
        self.pathEx = []
        self.rootSubpath = ""

    def exportFolder(self, subpath = ""):
        """
        Get absolute path to folder that contains the export.
        """
        return os.path.abspath(os.path.normpath( os.path.join(self.path, subpath) ))

    def applicationPath(self, subpath = ""):
        """
        Get the absolute path to export path containing the app main executable.
        This is the direct subfolder specified in rootSubpath of the export folder.
        """
        return self.exportFolder( os.path.join(self.rootSubpath, subpath) )

    def relPath(self, path):
        """
        Get subpath relative to export folder
        """
        return os.path.relpath(path, self.exportFolder())

    def getPluginFiles(self):
        """
        Returns all python modules (.py) and python packages (subfolders containing 
        a file called __init__.py) in the plugins/ folder.
        Useful for including as extra modules to compile when freezing.
        """
        import glob
        rootpath = self.exportFolder('makehuman/plugins')

        # plugin modules
        pluginModules = glob.glob(os.path.join(rootpath,'[!_]*.py'))

        # plugin packages
        for fname in os.listdir(rootpath):
            if fname[0] != "_":
                folder = os.path.join(rootpath, fname)
                if os.path.isdir(folder) and ("__init__.py" in os.listdir(folder)):
                    pluginModules.append(os.path.join(folder, "__init__.py"))

        return pluginModules

    def __str__(self):
        return """MH source export
  version:  %s
  commit:   %s (%s)
  path:     %s
  type:     %s""" % (self.version, self.commit, self.branch, self.path, "RELEASE" if self.isRelease else "NIGHTLY")

def _recursive_glob(p, matchPatterns, files, root = None):
    import os
    import glob
    if root is None:
        root = p
    for searchExpr in matchPatterns:
        for d in glob.glob(os.path.join(p, searchExpr)):
            if os.path.isfile(d):
                files.append(os.path.relpath(d, root))

    # Recurse subfolders
    for fname in os.listdir(p):
        folder = os.path.join(p, fname)
        if os.path.isdir(folder):
            _recursive_glob(folder, matchPatterns, files, root)

def _recursive_cp(src, dest):
    """
    Copy operation that behaves like unix cp -rf
    Overwrites copied files, leaves other files in target folder intact.
    """
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        for f in files:
            _recursive_cp(os.path.join(src, f), os.path.join(dest, f))
    else:
        shutil.copyfile(src, dest)

    # Copy permissions and times
    try:
        shutil.copystat(src, dest)
    except OSError as e:
        # Copying file access times may fail on Windows (WindowsError)
        pass

def parseConfig(configPath):
    if os.path.isfile(configPath):
        import configparser
        config = configparser.ConfigParser()
        config.read(configPath)
        return config
    else:
        return None

def export(sourcePath = '.', exportFolder = 'export', skipScripts = False, noDownload = False):
    """
    Perform export

    sourcePath      The root of the hg repository (it contains folders makehuman, blendertools, ...)
    exportFolder    The folder to export to. Should not exist before running.
    skipScripts     Set to true to skip executing asset compile scripts
    noDownload      Skip downloading files (has no effect when skipScripts is already enabled)

    Returns a summary object with members: version, revision, path (exported path), isRelease
    containing information on the exported release.
    """
    exporter = MHAppExporter(sourcePath, exportFolder, skipScripts, noDownload)
    return exporter.export()


def _parse_args():
    if len(sys.argv) < 2:
        return dict()

    import argparse    # requires python >= 2.7
    parser = argparse.ArgumentParser()

    # optional arguments
    parser.add_argument("--skipscripts", action="store_true", help="Skip running scripts for compiling assets")
    parser.add_argument("--nodownload", action="store_true", help="Do not run download assets script")

    # positional arguments
    parser.add_argument("sourcePath", default=None, nargs='?', help="Root path of makehuman source directory")
    parser.add_argument("targetPath", default=getpath.getPath("build-prepare-export"), nargs='?', help="Path to export to")

    argOptions = vars(parser.parse_args())
    return argOptions

if __name__ == '__main__':
    args = _parse_args()

    if args.get('sourcePath', None) is None:
        raise RuntimeError("sourcePath argument not specified")
    if args.get('targetPath', None) is None:
        raise RuntimeError("targetPath argument not specified")

    print(export(args['sourcePath'], args['targetPath'], args.get('skipscripts', False), args.get('nodownload', False)))
