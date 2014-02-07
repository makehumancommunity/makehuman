# -*- mode: python -*-

### Config #########
skipSvn = True
skipScripts = True
####################


import sys
import subprocess
import zipfile
import os
import shutil

sys.path = sys.path + ['.']
import build_prepare

def get_plugin_files(rootpath):
    """
    Returns all python modules (.py) and python packages (subfolders containing 
    a file called __init__.py) in the plugins/ folder.
    """
    import glob
    # plugin modules
    pluginModules = glob.glob(os.path.join(rootpath,'[!_]*.py'))

    # plugin packages
    for fname in os.listdir(rootpath):
        if fname[0] != "_":
            folder = os.path.join(rootpath, fname)
            if os.path.isdir(folder) and ("__init__.py" in os.listdir(folder)):
                pluginModules.append(os.path.join(folder, "__init__.py"))

    return pluginModules

def hgRootPath(subpath=""):
    return os.path.join('../..', subpath)

def exportPath(subpath=""):
    return os.path.join('export', subpath)

def distPath(subpath=""):
    return os.path.join('dist', subpath)


# Export source to new folder and run scripts
if os.path.exists(exportPath()):
    shutil.rmtree(exportPath())
exportInfo = build_prepare.export(sourcePath = hgRootPath(), exportFolder = exportPath(), skipHG = skipSvn, skipScripts = skipScripts)

# Copy extra windows-specific files to export folder
shutil.copy(hgRootPath('makehuman/icons/makehuman.ico'), exportPath('makehuman/makehuman.ico'))

# Change to the export dir for building
os.chdir(exportPath())


SVNREV = exportInfo.revision
VERSION= exportInfo.version

if exportInfo.isRelease:
    VERSION_FN = VERSION.replace('.', '_').replace(' ', '-').lower()
else:
    VERSION_FN= str(SVNREV)


appExecutable = exportPath('makehuman/makehuman.py')
pEx = ['lib','core','shared','apps','apps/gui', 'plugins']

a = Analysis([appExecutable] + get_plugin_files(exportPath("makehuman/plugins")),
             pathex=[ exportPath('makehuman/%s' % p) for p in pEx ],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None
             )

##### include mydir in distribution #######
def extra_datas(mydir):
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
        if mydir == 'data' and f.endswith(".target"):
            print "skipping %s" % f
        else:
            extra_datas.append((f, f, 'DATA'))

    return extra_datas
###########################################

# append all of our necessary subdirectories
EXTRA_DATA_PATHS = ['data', 'plugins', 'tools', 'icons']
#EXTRA_DATA_PATHS += ['lib', 'core', 'shared', 'apps', 'qt_menu.nib']
for p in EXTRA_DATA_PATHS:
    a.datas += extra_datas(exportPath("makehuman"), p)


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
        icon=exportPath('makehuman/icons/makehuman.ico'),
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
        
os.remove(VERSION_FILE_PATH)
