#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MakeHuman build prepare

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Prepares an export folder ready to build packages from.
"""

### Configuration ##############################################################

# Path to hg executable
HG_PATH = "hg"

# Filter of files from source folder to exclude (glob syntax)
EXCLUDES = ['.hgignore', '.hgeol', '*.target', '*.obj', '*.pyc', '*.pyd', 'maketarget-standalone', 'plugins/4_rendering_mitsuba', 'plugins/4_rendering_povray', 'plugins/4_rendering_aqsis.py', 'plugins/0_modeling_5_editing.py', 'plugins/0_modeling_8_random.py', 'plugins/3_libraries_animation.py', 'compile_*.py', 'build_prepare.py', 'download_assets.py', '*~', '*.bak', 'setup.nsi', 'clean*.sh', 'makehuman.sh', 'clean*.bat', 'makehuman/docs', 'makehuman/icons', 'makehuman.rc', '*_contents.txt', 'buildscripts']
# Same as above, but applies to release mode only
EXCLUDES_RELEASE = ['testsuite']

# Include filter for additional asset files (not on hg) to copy (glob syntax)
ASSET_INCLUDES = ['*.npz', '*.list', '*.thumb', '*.png', '*.json', '*.mhmat', '*.mhclo', '*.proxy', 'glsl/*.txt', 'languages/*.ini', "*.mhp", "*.mhm", "*.qss", "*.mht", "*.svg"]

# Even if empty, create these folders (relative to export path)
CREATE_FOLDERS = ['makehuman/data/backgrounds', 'makehuman/data/clothes', 'makehuman/data/teeth', 'makehuman/data/eyelashes', 'makehuman/data/tongue']

# Files and folders to exclude as a last step, to correct things that still fall through, but shouldn't (relative path to export path, no wildcards allowed) For example folders affected during build
POST_REMOVE = ['makehuman/icons', 'makehuman/docs', 'buildscripts']

# Finally copy all files from these source folders, effectively ignoring all exclude filters
COPY_ALL = ['blendertools']

# Root folder after rearranging all. All folders in root except this one will be copied inside this folder, as new root.
REARRANGE_ROOT_FOLDER = 'makehuman'


# == Following settings relate to freezing a py package, paths are referenced in rearranged folder state, relative to REARRANGE_ROOT_FOLDER ==

# Files and paths that have to be declared as data (when freezing)
DATAS = ['blendertools', 'data', 'plugins', 'license.txt', 'licenses']

# Entry point for the MakeHuman application
MAIN_EXECUTABLE = 'makehuman.py'

# Extension to python path, folders containing MH modules
PYTHON_PATH_EX = ['lib','core','shared','apps','apps/gui', 'plugins']


################################################################################


import sys
import os
import subprocess
import shutil


VERSION_FILE_PATH = 'makehuman/data/VERSION'


class MHAppExporter(object):
    def __init__(self, sourceFolder, exportFolder='export', skipHG=False, skipScripts=False):
        self.sourceFolder = sourceFolder
        self.targetFolder = exportFolder
        self.skipHG = skipHG
        self.skipScripts = skipScripts

        sys.path = sys.path + [self.sourceFile('makehuman'), self.sourceFile('makehuman/lib')]

    def isRelease(self):
        import makehuman
        return makehuman.isRelease()

    def export(self):
        # Sanity checks
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

        # Obtain exact revision
        # TODO perhaps try to obtain hg tags instead of node id for releases
        HGREV, REVID = self.processRevision()
        VERSION = self.getVersion() # TODO 'A8 RC1'
        print "Retrieved version information: %s (revision info: r%s %s [%s])\n" % (VERSION, HGREV, REVID, os.environ['HGREVISION_SOURCE'])

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

        # Try to copy old VERSION file to export folder
        if self.skipHG:
            print "Skipped getting HG revision, attempting to copy already existing VERSION file to export"
            try:
                shutil.copy(self.sourceFile(VERSION_FILE_PATH), 
                            self.targetFile(VERSION_FILE_PATH))
            except Exception as e:
                print "Failed to copy %s file to export (%s)" % (VERSION_FILE_PATH, e)
            print "\n"

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

        resultInfo = ExportInfo(VERSION, HGREV, REVID, self.targetFile(), self.isRelease())
        resultInfo.rootSubpath = REARRANGE_ROOT_FOLDER
        resultInfo.datas = [os.path.join(REARRANGE_ROOT_FOLDER, d) for d in DATAS]
        resultInfo.pathEx = [os.path.join(REARRANGE_ROOT_FOLDER, p) for p in PYTHON_PATH_EX]
        resultInfo.mainExecutable = os.path.join(REARRANGE_ROOT_FOLDER, MAIN_EXECUTABLE)
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
        # TODO still causes svn warnings with current version of makehuman
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

    def getExcludes(self):
        if self.isRelease():
            return EXCLUDES + EXCLUDES_RELEASE
        else:
            return EXCLUDES

    def exportHGFiles(self):
        print "Exporting files from hg repo (hg archive)"
        excludes = self.getExcludes()
        exclarg = [item for pair in zip(len(excludes)*['--exclude'], EXCLUDES) for item in pair]

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

            ### Write VERSION file
            versionFile = self.targetFile(VERSION_FILE_PATH)
            if not os.path.isdir(os.path.dirname( versionFile )):
                os.makedirs(os.path.dirname( versionFile ))
            vfile = open(versionFile, "w")
            vfile.write("%s:%s" % (HGREV, REVID))
            vfile.close()

        return HGREV, REVID

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

def export(sourcePath = '.', exportFolder = 'export', skipHG = False, skipScripts = False):
    """
    Perform export

    sourcePath      The root of the hg repository (it contains folders makehuman, blendertools, ...)
    exportFolder    The folder to export to. Should not exist before running.
    skipScripts     Set to true to skip executing asset compile scripts
    skipHG          Set to true to skip verifying HG revision status (tries to read from data/VERSION)

    Returns a summary object with members: version, revision, path (exported path), isRelease
    containing information on the exported release.
    """
    exporter = MHAppExporter(sourcePath, exportFolder, skipHG, skipScripts)
    return exporter.export()


def _parse_args():
    if len(sys.argv) < 2:
        return dict()

    import argparse    # requires python >= 2.7
    parser = argparse.ArgumentParser()

    # optional arguments
    parser.add_argument("--skipscripts", action="store_true", help="Skip running scripts for compiling assets")
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

    print export(args['sourcePath'], args['targetPath'], args.get('skiphg', False), args.get('skipscripts', False))
