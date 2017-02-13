# -*- mode: python -*-

"""
MakeHuman pyinstaller spec file for Windows build

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier, Benjamin A Lau, Joel Palmius

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3


Abstract
--------

Create a windows executable package for the MakeHuman application."
"""


import sys
import subprocess
import zipfile
import os
import shutil

sys.path = sys.path + ['..']
import build_prepare

package_name = "makehuman"  
package_explicit = False 
package_version = None
dist_dir = None
hgpath = "hg"
hg_root_path = os.path.abspath( os.path.join("..","..") )

def hgRootPath(subpath=""):
    """
    The source location, root folder of the hg repository.
    (we assume cwd is in buildscripts/win32 relative to hg root)
    """
    global hg_root_path
    return os.path.join(hg_root_path, subpath)

def exportPath(subpath=""):
    """
    The export path, where the source files to be packaged are exported.
    """
    global hgRootPath
    global package_name
    global package_explicit
    if package_explicit:
        return os.path.abspath(os.path.join(hgRootPath(), '..', package_name + '_export_win32', subpath))
    else:
        return os.path.abspath(os.path.join(hgRootPath(), '..', 'mh_export_win32', subpath))

def distPath(subpath=""):
    """
    The distribution path, where the compiled files are stored and additional
    data from export path is copied. This folder will eventually be packaged
    for distribution.
    """
    global dist_dir

    if not dist_dir is None:
        return os.path.join(dist_dir, subpath)
    return os.path.join('dist', subpath)

def parseConfig(configPath):
    if os.path.isfile(configPath):
        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read(configPath)
        return config
    else:
        return None

def configure(confpath):
  global package_name
  global package_version
  global package_explicit
  global hgpath
  global dist_dir
  global parseConfig
  global exportPath

  def _conf_get(config, section, option, defaultVal):
    try:
        return config.get(section, option)
    except:
        return defaultVal

  conf = parseConfig(confpath)
  if conf is None:
    print "No config file at %s, using defaults or options passed on commandline." % confpath
  else:
    print "Using config file at %s. NOTE: properties in config file will override any other settings!" % confpath

    hgpath = _conf_get(conf, 'General', 'hgPath', hgpath)
    package_name = _conf_get(conf, 'Win32', 'packageName', package_name)
    package_version = _conf_get(conf, 'Win32', 'packageVersion', package_version)
    dist_dir = _conf_get(conf, 'Win32', 'distDir', dist_dir)
    if not (package_name == "makehuman"):
      package_explicit = True

configure("../build.conf")
if not dist_dir is None:
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)

# Export source to export folder and run scripts
if os.path.exists(exportPath()):
    shutil.rmtree(exportPath())
i = exportInfo = build_prepare.export(sourcePath = hgRootPath(), exportFolder = exportPath())

# Copy extra windows-specific files to export folder
## no extra files needed

# Create config file for the Qt libraries to be able to load plugins
# (such as for loading jpg and svg images)
qtConf = open(i.applicationPath('qt.conf'), 'wb')
qtConf.write('[Paths]\nPrefix = .\nPlugins = qt4_plugins')
qtConf.close()
exportInfo.datas.append(os.path.join(i.rootSubpath, 'qt.conf'))

# Change to the export dir for building
os.chdir(exportPath())

VERSION = exportInfo.version
HGREV = exportInfo.revision
NODEID = exportInfo.nodeid

if exportInfo.isRelease:
    VERSION_FN = VERSION.replace(' ', '-').lower()
else:
    VERSION_FN= str(HGREV) + '-' + NODEID

appExecutable = exportPath( 'makehuman\makehuman.py' )

a = Analysis([appExecutable] + i.getPluginFiles(),
             pathex= [ exportPath(p) for p in i.pathEx ],
             hiddenimports=["skeleton_drawing"],
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
    if os.path.isfile(mydir):
        files = [mydir]
    else:
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
        icon=hgRootPath('makehuman/icons/makehuman.ico'),
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
    target_dir = hgRootPath('buildscripts\win32\dist\makehuman')
    if package_explicit and not package_version is None and not package_name is None:
        label = package_name + "-" + package_version
    else:
        label = package_name + "-" + VERSION_FN;
    zipfilename = distPath('%s-win32.zip' % label)
    zip = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zip.write(fn, fn[rootlen:])
    zip.close()
    if not dist_dir is None:
        base = os.path.basename(zipfilename)
        dest = os.path.join(dist_dir,base)
        os.rename(zipfilename,dest)

