#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
MakeHuman build prepare

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2015

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

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

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Prepares an export folder ready to build packages from.
"""

### Configuration ##############################################################

# Path to hg executable
HG_PATH = "hg"

# Filter of files from source folder to exclude (glob syntax)
EXCLUDES = ['.hgignore', '.hgtags', '.hgeol', '*.target', '*.obj', '*.pyc', '*.mhclo', '*.proxy', '*.pyd', 'maketarget-standalone', 'plugins/4_rendering_mitsuba', 'plugins/4_rendering_povray', 'plugins/4_rendering_aqsis.py', 'plugins/0_modeling_5_editing.py', 'plugins/0_modeling_8_random.py', 'plugins/3_libraries_animation.py', 'compile_*.py', 'build_prepare.py', 'download_assets.py', '*~', '*.bak', 'setup.nsi', 'clean*.sh', 'makehuman.sh', 'makehuman/makehuman', 'pylintrc', 'clean*.bat', 'makehuman/docs', 'makehuman/icons/*psd', 'makehuman/icons/*bmp', 'makehuman/icons/*ico', 'makehuman/icons/*icns', 'makehuman/icons/*xcf', 'makehuman/icons/makehuman.svg', 'makehuman.rc', '*_contents.txt', 'buildscripts', '.build_prepare.out']
# Same as above, but applies to release mode only
EXCLUDES_RELEASE = ['testsuite']

# Include filter for additional asset files (not on hg) to copy (glob syntax)
ASSET_INCLUDES = ['*.npz', '*.mhpxy', '*.list', '*.thumb', '*.png', '*.json', '*.mhmat', '*.mhclo', '*.proxy', 'glsl/*.txt', 'languages/*.ini', "*.mhp", "*.mhm", "*.qss", "*.mht", "*.svg", "icons/makehuman_bg.svg", "icons/makehuman.png"]

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


VERSION_FILE_PATH = 'makehuman/data/VERSION'
BUILD_CONF_FILE_PATH = 'buildscripts/build.conf'



class MHAppExporter(object):
    def __init__(self, sourceFolder, exportFolder='export', skipHG=False, skipScripts=False, noDownload=False):
        self.sourceFolder = sourceFolder
        self.targetFolder = exportFolder
        self.skipHG = skipHG
        self.skipScripts = skipScripts
        self.noDownload = noDownload

        sys.path = [self.sourceFile('makehuman'), self.sourceFile('makehuman/lib')] + sys.path

        self.configure()

    def configure(self):
        self.HGREV = self.REVID = None
        self.VERSION = None
        self.IS_RELEASE = None
        self.VERSION_SUB = None

        def _conf_get(config, section, option, defaultVal):
            try:
                return config.get(section, option)
            except:
                return defaultVal

        self.config = parseConfig(self.sourceFile(BUILD_CONF_FILE_PATH))
        if self.config is None:
            print "No config file at %s, using defaults or options passed on commandline." % self.sourceFile(BUILD_CONF_FILE_PATH)
        else:
            print "Using config file at %s. NOTE: properties in config file will override any other settings!" % self.sourceFile(BUILD_CONF_FILE_PATH)

            global HG_PATH
            HG_PATH = _conf_get(self.config, 'General', 'hgPath', HG_PATH)

            hgrev = _conf_get(self.config, 'BuildPrepare', 'hgRev', None)
            if hgrev is not None:
                self.HGREV, self.REVID = hgrev.split(':')
            if self.HGREV and self.REVID:
                os.environ['HGREVISION_SOURCE'] = "build config file"
                os.environ['HGREVISION'] = self.HGREV
                os.environ['HGNODEID'] = self.REVID
            else:
                self.HGREV = None
                self.REVID = None

            self.VERSION_SUB = _conf_get(self.config, 'BuildPrepare', 'versionSub', None)

            isRelease = _conf_get(self.config, 'BuildPrepare', 'isRelease', None)
            if isRelease is not None:
                self.IS_RELEASE = ( isRelease.lower() in ['yes', 'true'] )

            skipHg = _conf_get(self.config, 'BuildPrepare', 'skipHg', None)
            if skipHg is not None:
                self.skipHG = skipHg.lower() in ['yes', 'true']

            skipScripts = _conf_get(self.config, 'BuildPrepare', 'skipScripts', None)
            if skipScripts is not None:
                self.skipScripts = skipScripts.lower() in ['yes', 'true']

            noDownload = _conf_get(self.config, 'BuildPrepare', 'noDownload', None)
            if noDownload is not None:
                self.noDownload = noDownload.lower() in ['yes', 'true']

    def isRelease(self):
        if self.IS_RELEASE is not None:
            return self.IS_RELEASE

        import makehuman
        return makehuman.isRelease()

    def export(self):
        # Sanity checks
        if not os.path.isdir(self.sourceFile('.hg')):
            raise RuntimeError("The export folder %s is not found, the source folder argument should be the root of the hg repository." % self.sourceFile('.hg'))
        if self.isSubPath(self.targetFile(), self.sourceFile()):
            raise RuntimeError("The export folder is a subfolder of the source folder, this is not allowed.")
        if os.path.exists(self.targetFile()):
            raise RuntimeError("An export folder called %s already exists" % self.targetFile())
        if not os.path.exists(self.sourceFile()):
            raise RuntimeError("Specified source folder %s does not exist" % self.sourceFile())
        if not os.path.isfile(self.sourceFile('makehuman/makehuman.py')):
            raise RuntimeError("The specified source folder %s does not appear to be a valid MakeHuman HG root folder (cannot find file %s)" % (self.sourceFile(), self.sourceFile('makehuman/makehuman.py')))

        # TODO perform hg pull?

        print 'Creating folder %s' % self.targetFile()
        os.makedirs(self.targetFile())

        print "Exporting"
        print "  from: %s" % self.sourceFile()
        print "  to:   %s\n" % self.targetFile()

        print "\n\n%s build\n\n" % ("RELEASE" if self.isRelease() else "NIGHTLY")

        # Obtain exact revision
        # TODO perhaps try to obtain hg tags instead of node id for releases
        if not self.HGREV or not self.REVID:
            self.HGREV, self.REVID = self.processRevision()
        self.VERSION = self.getVersion()
        print "Retrieved version information: %s (revision info: r%s %s [%s])\n" % (self.VERSION, self.HGREV, self.REVID, os.environ['HGREVISION_SOURCE'])

        # Run scripts to prepare assets
        if not self.skipScripts:
            self.runScripts()

        self.exportHGFiles()
        print "\n"

        # Export other non-hg files
        self.exportCompiledAssets(self.sourceFile())
        print "\n"

        # Create extra folders
        print "Creating extra folders"
        for f in CREATE_FOLDERS:
            try:
                print self.targetFile(f)
                os.makedirs(self.targetFile(f))
            except:
                pass
        print "\n"

        # Perform post-remove step
        print "Post removing excluded folders"
        for f in POST_REMOVE:
            if not os.path.exists(self.targetFile(f)):
                continue
            print "Post-removing excluded file from export folder %s" % f
            if os.path.isdir(self.targetFile(f)):
                shutil.rmtree(self.targetFile(f))
            else:
                os.remove(self.targetFile(f))
        print "\n"

        # Perform post-copy step
        print "Post copying extra included files"
        for f in COPY_ALL:
            if not os.path.exists(self.sourceFile(f)):
                continue
            print "Post-including file or folder %s" % f
            _recursive_cp(self.sourceFile(f), self.targetFile(f))
        print "\n"

        # Write VERSION file to export folder
        print "Writing data/VERSION file to export folder with contents: %s:%s\n" % (self.HGREV, self.REVID)
        self.writeVersionFile(self.HGREV, self.REVID)

        # If RELEASE status or version-sub was set in config, update it in exported mh source file
        if (self.IS_RELEASE is not None) or (self.VERSION_SUB is not None) :
            f = open(self.targetFile('makehuman/makehuman.py'), 'rb')
            release_replaced = False
            versionsub_replaced = False
            lines = []
            for lIdx, line in enumerate(f):
                if self.IS_RELEASE is not None and not release_replaced and line.strip().startswith('release ='):
                    line = line.replace('release = True', 'release = %s' % self.IS_RELEASE)
                    line = line.replace('release = False', 'release = %s' % self.IS_RELEASE)
                    print "Replaced release declaration in makehuman/makehuman.py at line %s." % (lIdx+1)
                    release_replaced = True
                if self.VERSION_SUB is not None and not versionsub_replaced and line.strip().startswith('versionSub ='):
                    import re
                    line = re.sub(r'versionSub = ".*"','versionSub = "%s"' % self.VERSION_SUB, line)
                    print "Replaced version-sub declaration in makehuman/makehuman.py at line %s." % (lIdx+1)
                    versionsub_replaced = True
                lines.append(line)
            f.close()
            f = open(self.targetFile('makehuman/makehuman.py'), 'wb')
            f.write(''.join(lines))
            f.close()
            print '\n'

        # Re-arrange folders
        for f in os.listdir( self.targetFile() ):
            if f == REARRANGE_ROOT_FOLDER:
                continue
            path = self.targetFile(f)
            if os.path.isdir(path):
                # Move folder in new root folder
                print "Moving folder %s into new root %s" % (f, REARRANGE_ROOT_FOLDER)
                shutil.move(path, self.targetFile(os.path.join(REARRANGE_ROOT_FOLDER, f)))
        '''
        # Move all contents of new root folder into dist root (overwrite if needed)
        _fixOnFinish = []
        for f in os.listdir( self.targetFile(REARRANGE_ROOT_FOLDER) ):
            path = self.targetFile(os.path.join(REARRANGE_ROOT_FOLDER, f))
            print "Moving %s to root" % os.path.join(REARRANGE_ROOT_FOLDER, f)
            if os.path.exists(self.targetFile(f)):
                #print "WARNING: overwriting folder of file %s with %s" % (f, os.path.join(REARRANGE_ROOT_FOLDER, f))
                _fixOnFinish.append(f)
                shutil.move(path, self.targetFile(f+'--fixOnFinish'))
            else:
                shutil.move(path, self.targetFile(f))
        # Remove the now empty root subfolder
        os.rmdir(self.targetFile(REARRANGE_ROOT_FOLDER))
        for f in _fixOnFinish:
            shutil.move(self.targetFile(f+'--fixOnFinish'), self.targetFile(f))
        '''
        print "\n"

        resultInfo = ExportInfo(self.VERSION, self.HGREV, self.REVID, self.targetFile(), self.isRelease())
        resultInfo.rootSubpath = REARRANGE_ROOT_FOLDER
        resultInfo.datas = [os.path.join(REARRANGE_ROOT_FOLDER, d) for d in DATAS]
        resultInfo.pathEx = [os.path.join(REARRANGE_ROOT_FOLDER, p) for p in PYTHON_PATH_EX]
        resultInfo.mainExecutable = os.path.join(REARRANGE_ROOT_FOLDER, MAIN_EXECUTABLE)

        # Write export info to file for easy retrieving by external processes
        f = open(self.sourceFile('.build_prepare.out'), 'wb')
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
        print "Running %s from %s" % (args, self.getCWD())
        return subprocess.check_call(args, cwd=self.getCWD())

    def runScripts(self):
        if not self.noDownload:
            ###DOWNLOAD ASSETS
            try:
                self.runProcess( ["python","download_assets.py"] )
            except subprocess.CalledProcessError:
                print "check that download_assets.py is working correctly"
                sys.exit(1)
            print "\n"

        ###COMPILE TARGETS
        try:
            self.runProcess( ["python","compile_targets.py"] )
        except subprocess.CalledProcessError:
            print "check that compile_targets.py is working correctly"
            sys.exit(1)
        print "\n"

        ###COMPILE MODELS
        try:
            self.runProcess( ["python","compile_models.py"] )
        except subprocess.CalledProcessError:
            print "check that compile_models.py is working correctly"
            sys.exit(1)
        print "\n"

        ###COMPILE PROXIES
        try:
            self.runProcess( ["python","compile_proxies.py"] )
        except subprocess.CalledProcessError:
            print "check that compile_proxies.py is working correctly"
            sys.exit(1)
        print "\n"

    def getExcludes(self):
        if self.isRelease():
            return EXCLUDES + EXCLUDES_RELEASE
        else:
            return EXCLUDES

    def exportHGFiles(self):
        print "Exporting files from hg repo (hg archive)"
        excludes = self.getExcludes()
        exclarg = [item for pair in zip(len(excludes)*['--exclude'], excludes) for item in pair]

        try:
            self.runProcess( [HG_PATH, "archive"] + exclarg + [self.targetFile()])
        except Exception as e:
            print "An error happened attempting to run 'hg archive'. Is Mercurial (commandline-tools) installed?"
            raise e

        # Because the --excludes option does not appear to be working all too well (at least not with wildcards):
        # Gather files
        files = []
        _recursive_glob(self.targetFile(), self.getExcludes(), files)
        for f in files:
            print "Removing excluded file from export folder %s" % f
            if os.path.isdir(self.targetFile(f)):
                shutil.rmtree(self.targetFile(f))
            else:
                os.remove(self.targetFile(f))

    def exportCompiledAssets(self, path):
        print "Copying extra files in source tree"
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
            print "Copying %s" % self.sourceFile(f)
            shutil.copy(self.sourceFile(f), self.targetFile(f))

    def processRevision(self):
        """
        Find revision, if source control is to be skipped, attempts to read it
        from data/VERSION which should be already present.
        """
        if self.skipHG:
            try:
                vfile = open(self.sourceFile(VERSION_FILE_PATH),"r")
                rIn = vfile.read().split(':')
                HGREV = int(rIn[0])
                REVID = rIn[1].strip()
                vfile.close()
            except:
                print 'Warning: no VERSION file found, HG revision unknown'
                HGREV = '?'
                REVID = 'UNKNOWN'

            # Store rev to prevent repeated revision queries in makehuman.py
            os.environ['HGREVISION_SOURCE'] = "data/VERSION static revision data"
            os.environ['HGREVISION'] = HGREV
            os.environ['HGNODEID'] = REVID
        else:
            rev = self.getRevision()
            if rev is None:
                HGREV = '?'
                REVID = 'UNKNOWN'
                return HGREV, REVID
            else:
                HGREV = rev[0]
                REVID = rev[1]

        return HGREV, REVID

    def writeVersionFile(self, hgrev, revid):
        ### Write VERSION file
        versionFile = self.targetFile(VERSION_FILE_PATH)
        if not os.path.isdir(os.path.dirname( versionFile )):
            os.makedirs(os.path.dirname( versionFile ))
        vfile = open(versionFile, "w")
        vfile.write("%s:%s" % (hgrev, revid))
        vfile.close()


class ExportInfo(object):
    def __init__(self, version, revision, nodeid, path, isRelease):
        self.version = version
        self.revision = revision
        self.nodeid = nodeid
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
  revision: %s (%s)
  path:     %s
  type:     %s""" % (self.version, self.revision, self.nodeid, self.path, "RELEASE" if self.isRelease else "NIGHTLY")

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
    except OSError, e:
        # Copying file access times may fail on Windows (WindowsError)
        pass

def parseConfig(configPath):
    if os.path.isfile(configPath):
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read(configPath)
        return config
    else:
        return None

def export(sourcePath = '.', exportFolder = 'export', skipHG = False, skipScripts = False, noDownload = False):
    """
    Perform export

    sourcePath      The root of the hg repository (it contains folders makehuman, blendertools, ...)
    exportFolder    The folder to export to. Should not exist before running.
    skipScripts     Set to true to skip executing asset compile scripts
    noDownload      Skip downloading files (has no effect when skipScripts is already enabled)
    skipHG          Set to true to skip verifying HG revision status (tries to read from data/VERSION)

    Returns a summary object with members: version, revision, path (exported path), isRelease
    containing information on the exported release.
    """
    exporter = MHAppExporter(sourcePath, exportFolder, skipHG, skipScripts, noDownload)
    return exporter.export()


def _parse_args():
    if len(sys.argv) < 2:
        return dict()

    import argparse    # requires python >= 2.7
    parser = argparse.ArgumentParser()

    # optional arguments
    parser.add_argument("--skipscripts", action="store_true", help="Skip running scripts for compiling assets")
    parser.add_argument("--nodownload", action="store_true", help="Do not run download assets script")
    parser.add_argument("--skiphg", action="store_true", help="Skip retrieving HG revision")

    # positional arguments
    parser.add_argument("sourcePath", default=None, nargs='?', help="Root path of HG source repository")
    parser.add_argument("targetPath", default=None, nargs='?', help="Path to export to")

    argOptions = vars(parser.parse_args())
    return argOptions


if __name__ == '__main__':
    args = _parse_args()

    if args.get('sourcePath', None) is None:
        raise RuntimeError("sourcePath argument not specified")
    if args.get('targetPath', None) is None:
        raise RuntimeError("targetPath argument not specified")

    print export(args['sourcePath'], args['targetPath'], args.get('skiphg', False), args.get('skipscripts', False), args.get('nodownload', False))
