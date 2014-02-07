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

# Filter of files from source folder to exclude (glob syntax)
EXCLUDES = ['.hgignore', '*.target', '*.obj', '*.pyc', 'maketarget/standalone', 'plugins/4_rendering_mitsuba', 'plugins/4_rendering_povray', 'plugins/4_rendering_aqsis.py', 'plugins/0_modeling_5_editing.py', 'plugins/0_modeling_8_random.py', 'plugins/3_libraries_animation.py', 'compile_*.py', 'build_prepare.py', 'download_assets.py', '*~', '*.bak', 'setup.nsi', 'clean*.sh', 'clean*.bat', 'makehuman/docs', 'makehuman/icons', 'makehuman.rc', 'rpm', 'deb']
# Same as above, but applies to release mode only
EXCLUDES_RELEASE = ['testsuite']

# Include filter for additional asset files (not on hg) to copy (glob syntax)
ASSET_INCLUDES = ['*.npz', '*.thumb', '*.png', '*.json', '*.mhmat', '*.mhclo', '*.proxy', 'glsl/*.txt', 'languages/*.ini', "*.mhp", "*.mhm", "*.qss", "*.mht", "*.svg"]

# Even if empty, create these folders (relative to export path)
CREATE_FOLDERS = ['makehuman/data/backgrounds']

# Files and folders to exclude as a last step, to correct things that still fall through, but shouldn't (relative path to export path, no wildcards allowed)
POST_REMOVE = ['makehuman/icons', 'makehuman/docs']

################################################################################


import sys
import os
import subprocess
import shutil


VERSION_FILE_PATH = 'makehuman/data/VERSION'


class MHAppExporter(object):
    def __init__(self, sourceFolder, exportFolder='export', skipHG=False, skipScripts=False):
        self.sourceFolder = sourceFolder
        if not os.path.isdir(self.sourceFolder):
            raise RuntimeError("Source folder %s does not exist" % self.sourceFolder)
        self.targetFolder = exportFolder
        self.skipHG = skipHG
        self.skipScripts = skipScripts

        sys.path = sys.path + [self.sourceFile('makehuman'), self.sourceFile('makehuman/lib')]

    def isRelease(self):
        import makehuman
        return makehuman.isRelease()

    def export(self):
        # Sanity checks
        if os.path.exists(self.targetFile()):
            raise RuntimeError("An export folder called %s already exists" % self.targetFile())
        if not os.path.exists(self.sourceFile()):
            raise RuntimeError("Specified source folder %s does not exist" % self.sourceFile())
        if not os.path.isfile(self.sourceFile('makehuman/makehuman.py')):
            raise RuntimeError("The specified source folder %s does not appear to be a valid MakeHuman HG root folder (cannot find file %s)" % (self.sourceFile(), self.sourceFile('makehuman/makehuman.py')))

        print "Exporting"
        print "  from: %s" % self.sourceFile()
        print "  to:   %s\n" % self.targetFile()

        # Run scripts to prepare assets
        if not self.skipScripts:
            self.runScripts()

        self.exportHGFiles()

        # Export other non-hg files
        self.exportCompiledAssets(self.sourceFile())

        # Create extra folders
        for f in CREATE_FOLDERS:
            os.makedirs(self.targetFile(f))

        # Perform post-remove step
        for f in POST_REMOVE:
            if not os.path.exists(self.targetFile(f)):
                continue
            print "Post-removing excluded file from export folder %s" % f
            if os.path.isdir(self.targetFile(f)):
                shutil.rmtree(self.targetFile(f))
            else:
                os.remove(self.targetFile(f))

        # Obtain exact revision
        HGREV = self.processRevision()
        VERSION = self.getVersion()

        # Copy VERSION file to export folder
        try:
            shutil.copy(self.sourceFile(VERSION_FILE_PATH), 
                        self.targetFile(VERSION_FILE_PATH))
        except:
            print "Failed to set %s file" % VERSION_FILE_PATH

        resultInfo = ExportInfo(VERSION, HGREV, self.targetFile(), self.isRelease())
        return resultInfo

    def sourceFile(self, path=""):
        return os.path.abspath(os.path.normpath( os.path.join(self.sourceFolder, path) ))

    def targetFile(self, path=""):
        return os.path.abspath(os.path.normpath( os.path.join(self.targetFolder, path) ))

    def getRevision(self):
        import makehuman
        # TODO needs hg info now
        #return makehuman.get_svn_revision_1()

        # Return local revision number of hg tip
        # TODO in the future perhaps also return 7 characters of the exact hash for verification
        output = subprocess.Popen(["hg","head"], stdout=subprocess.PIPE, stderr=sys.stderr, cwd=self.getCWD()).communicate()[0]
        for line in output.splitlines():
            key, value = line.split(':', 1)
            if key.strip().lower() == 'changeset':
                return value.split(':')[0].strip()

    def getVersion(self):
        import makehuman
        # TODO still causes svn warnings with current version of makehuman
        return makehuman.getVersionStr(verbose=False)

    def getCWD(self):
        return os.path.normpath(os.path.realpath( os.path.join(self.sourceFolder, 'makehuman') ))

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

        ###COMPILE TARGETS
        try:
            self.runProcess( ["python","compile_targets.py"] )
        except subprocess.CalledProcessError:
            print "check that compile_targets.py is working correctly"
            sys.exit(1)

        ###COMPILE MODELS
        try:
            self.runProcess( ["python","compile_models.py"] )
        except subprocess.CalledProcessError:
            print "check that compile_models.py is working correctly"
            sys.exit(1)

    def getExcludes(self):
        if self.isRelease():
            return EXCLUDES + EXCLUDES_RELEASE
        else:
            return EXCLUDES

    def exportHGFiles(self):
        if not os.path.exists(self.targetFile()):
            print 'creating folder %s' % self.targetFile()
            os.makedirs(self.targetFile())
        else:
            # TODO what to do here? continue? stop?
            raise RuntimeError("An export older called %s already exists" % self.targetFile())

        excludes = self.getExcludes()
        exclarg = [item for pair in zip(len(excludes)*['--exclude'], EXCLUDES) for item in pair]
        self.runProcess( ["hg", "archive"] + exclarg + [self.targetFile()])

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
        # Gather files
        files = []
        _recursive_glob(path, ASSET_INCLUDES, files)
        # Exclude files matching exclude patterns
        excludes = []
        _recursive_glob(path, self.getExcludes(), excludes)
        print 'makehuman/icons/makehuman.png' in files
        print 'makehuman/icons/makehuman.png' in excludes
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
                HGREV = int(vfile.read())
                vfile.close()
            except:
                print 'Warning: no VERSION file found, HG revision unknown'
                HGREV = 'UNKNOWN'
        else:
            HGREV = self.getRevision()

            ### Write VERSION file
            vfile = open(self.targetFile(VERSION_FILE_PATH),"w")
            vfile.write(HGREV)
            vfile.close()

        return HGREV

class ExportInfo(object):
    def __init__(self, version, revision, path, isRelease):
        self.version = version
        self.revision = revision
        self.path = os.path.abspath(path)
        self.isRelease = isRelease

    def __str__(self):
        return """MH source export
  version:  %s
  revision: %s
  path:     %s
  type:     %s""" % (self.version, self.revision, self.path, "RELEASE" if self.isRelease else "NIGHTLY")

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
