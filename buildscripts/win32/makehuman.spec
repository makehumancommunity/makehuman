# -*- mode: python -*-

### Config #########
skipHg = False
skipScripts = False
####################


import sys
import subprocess
import zipfile
import os
import shutil

sys.path = sys.path + ['..']
import build_prepare

def hgRootPath(subpath=""):
    """
    The source location, root folder of the hg repository.
    (we assume cwd is in buildscripts/win32 relative to hg root)
    """
    return os.path.join('..', '..', subpath)

def exportPath(subpath=""):
    """
    The export path, where the source files to be packaged are exported.
    """
    global hgRootPath
    return os.path.join(hgRootPath(), '..', 'mh_export_win32', subpath)

def distPath(subpath=""):
    """
    The distribution path, where the compiled files are stored and additional
    data from export path is copied. This folder will eventually be packaged
    for distribution.
    """
    return os.path.join('dist', subpath)

# Export source to export folder and run scripts
if os.path.exists(exportPath()):
    shutil.rmtree(exportPath())
i = exportInfo = build_prepare.export(sourcePath = hgRootPath(), exportFolder = exportPath(), skipHG = skipHg, skipScripts = skipScripts)

# Copy extra windows-specific files to export folder
shutil.copy(hgRootPath('makehuman/icons/makehuman.ico'), i.applicationPath('makehuman.ico'))
exportInfo.datas.append(os.path.join(i.rootSubpath, 'makehuman.ico'))

# Change to the export dir for building
#os.chdir(exportPath())


VERSION = exportInfo.version
HGREV = exportInfo.revision
NODEID = exportInfo.nodeid

if exportInfo.isRelease:
    VERSION_FN = VERSION.replace('.', '_').replace(' ', '-').lower()
else:
    VERSION_FN= str(HGREV) + '-' + NODEID


appExecutable = exportPath( i.mainExecutable )

a = Analysis([appExecutable] + i.getPluginFiles(),
             pathex= [ exportPath(p) for p in i.pathEx ],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None
             )

##### include mydir in distribution #######
def extra_datas(mydir):
    global exportInfo
    global exportPath
    def rec_glob(p, files):
        import os
        import glob
        for d in glob.glob(p):
            if os.path.isfile(d):
                files.append(d)
            rec_glob("%s/*" % d, files)
    files = []
    rec_glob("%s/*" % mydir, files)
    extra_datas = []
    for f in files:
        ft = os.path.relpath(f, exportInfo.applicationPath())
        fs = os.path.normpath(os.path.realpath(f))
        extra_datas.append((ft, fs, 'DATA'))

    return extra_datas
###########################################

# append all of our necessary subdirectories
for p in exportInfo.datas:
    a.datas += extra_datas(exportPath(p))


### Build
pyz = PYZ(a.pure)
if sys.platform == 'darwin':
    # MAC OSX
    exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='makehuman',
          debug=False,
          strip=None,
          upx=False,
          console=False )
    coll = COLLECT(exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=None,
        upx=True,
        name='makehuman')
    app = BUNDLE(coll,
        name='MakeHuman.app',
        icon='icons/makehuman.icns')
    if os.path.exists(os.path.join("dist","MakeHuman.dmg")):
        os.remove(os.path.join("dist","MakeHuman.dmg"))
    subprocess.check_call(["hdiutil","create","dist/MakeHuman.dmg","-srcfolder","dist/MakeHuman.app","-volname","'MakeHuman for Mac OS X'"])
        
elif sys.platform == 'win32':
    # WINDOWS
    exe = EXE(pyz,
        a.scripts,
        exclude_binaries=True,
        name='makehuman.exe',
        icon=i.applicationPath('makehuman.ico'),
        debug=False,
        strip=None,
        upx=True,
        console=False )
    coll = COLLECT(exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=None,
        upx=True,
        name='makehuman')
    target_dir = distPath('makehuman')
    zipfilename = distPath('makehuman-%s-win32.zip' % VERSION_FN)
    zip = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zip.write(fn, fn[rootlen:])


