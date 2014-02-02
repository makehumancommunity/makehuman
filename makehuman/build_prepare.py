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
EXCLUDES = ['.hgignore', '*.target', '*.obj', '*.pyc', 'maketarget/standalone', 'plugins/4_rendering_mitsuba', 'plugins/4_rendering_povray', 'plugins/4_rendering_aqsis.py', 'plugins/0_modeling_5_editing.py', 'plugins/0_modeling_8_random.py', 'plugins/3_libraries_animation.py', 'compile_*.py', 'download_assets.py', '*~', '*.bak']

# Include filter for additional asset files (not on hg) to copy (glob syntax)
ASSET_INCLUDES = ['*.npz', '*.thumb', '*.png', '*.json', '*.mhmat', '*.mhclo', '*.proxy', 'glsl/*.txt', 'languages/*.ini', "*.mhp", "*.mhm", "*.qss", "*.mht", "*.svg"]

# Even if empty, create these folders (relative to export path)
CREATE_FOLDERS = ['makehuman/data/backgrounds']

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

    def export(self):
        # Run scripts to prepare assets
        if not self.skipScripts:
            self.runScripts()

        self.exportHGFiles()

        # Export other non-hg files
        self.exportCompiledAssets(self.sourceFile())

        # Create extra folders
        for f in CREATE_FOLDERS:
            os.makedirs(self.targetFile(f))

        # Obtain exact revision
        HGREV = self.processRevision()
        VERSION = self.getVersion()

        # Copy VERSION file to export folder
        try:
            shutil.copy(self.sourceFile(VERSION_FILE_PATH), 
                        self.targetFile(VERSION_FILE_PATH))
        except:
            print "Failed to set %s file" % VERSION_FILE_PATH

        import makehuman
        resultInfo = ExportInfo(VERSION, HGREV, self.targetFile(), makehuman.isRelease())
        return resultInfo

    def sourceFile(self, path=""):
        return os.path.normpath( os.path.join(self.sourceFolder, path) )

    def targetFile(self, path=""):
        return os.path.normpath( os.path.join(self.targetFolder, path) )

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

    def exportHGFiles(self):
        if not os.path.exists(self.targetFile()):
            print 'creating folder %s' % self.targetFile()
            os.makedirs(self.targetFile())
        else:
            # TODO what to do here? continue? stop?
            raise RuntimeError("An export older called %s already exists" % self.targetFile())

        excludes = [item for pair in zip(len(EXCLUDES)*['--exclude'], EXCLUDES) for item in pair]
        self.runProcess( ["hg", "archive"] + excludes + [self.targetFile()])

        # Because the --excludes option does not appear to be working all too well (at least not with wildcards):
        # Gather files
        files = []
        _recursive_glob(self.targetFile(), EXCLUDES, files)
        for f in files:
            print "Removing excluded file from export folder %s" % f
            # TODO this probably does not work for folders, luckily until now, folder excludes did not have wildcards
            os.remove(self.targetFile(f))

    def exportCompiledAssets(self, path):
        # Gather files
        files = []
        _recursive_glob(path, ASSET_INCLUDES, files)

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
        self.path = path
        self.isRelease = isRelease

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

