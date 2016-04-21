#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
MakeHuman debian package build script

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2015

**Licensing:**         AGPL3

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


Abstract
--------

Create a debian DEB package for the MakeHuman application.
"""

# HINT: You need to run 
#
#   apt-get install devscripts equivs mercurial
#
# ... in order for this script to function at all
#
# script has to be run as root (sudo)
#
# Settings can be changed in ../build.conf


# --- CONFIGURATION SETTINGS --- 
package_name = "makehuman"  
package_explicit = False  # Add "hg" to package_name only if package_name was not explicitly set in build.conf
package_version = None
package_replaces = "makehuman-nightly,makehuman-alpha,makehumansvn"   # TODO for release, do we need to add 'makehumanhg' to the replaces as well?

hgpath = "/usr/bin/hg"

files_to_chmod_executable = [
    "usr/bin/makehuman",
    "usr/share/makehuman/makehuman",
    "usr/share/makehuman/makehuman.py",
    ]

# --- EVERYTHING BELOW THIS POINT IS LOGIC, HANDS OFF ---


import sys
import os
import re
import subprocess
import shutil

def _cp_files(folder, dest):
  """
  Copy files in folder to dest folder
  """
  for f in os.listdir(folder):
    fpath = os.path.join(folder, f)
    if os.path.isfile(fpath):
      print "Copy %s to %s" % (fpath, os.path.join(dest, f))
      shutil.copy(fpath, os.path.join(dest, f))

def _sed_replace(filepath, templateToken, replaceStr):
  subprocess.check_call(['sed', '-i', '-e', 's/%s/%s/' % (templateToken, replaceStr), filepath])

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
  global package_replaces
  global package_explicit
  global hgpath

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
    package_name = _conf_get(conf, 'Deb', 'packageName', package_name)
    package_replaces = _conf_get(conf, 'Deb', 'packageReplaces', package_replaces)
    package_version = _conf_get(conf, 'Deb', 'packageVersion', package_version)
    if not (package_name == "makehuman"):
      package_explicit = True


def buildDeb(dest = None):
  global package_name
  global package_version
  global package_replaces
  global package_explicit
  global hgpath
  global files_to_chmod_executable

  if os.geteuid() != 0:
    print "WARNING: You are not root. You should be running this script with root permissions!"

  if dest is None:
    dest = os.getenv('makehuman_dest',0)

    if dest == 0:
      print "You must explicitly set the makehuman_dest environment variable to point at a work directory, or specify it as argument. I will violently destroy and mutilate the contents of this directory."
      exit(1)

  destdir = os.path.normpath(os.path.realpath(dest))          # Folder to build deb package to
  if os.path.exists(destdir):
    # Ensure dest dir is empty
    shutil.rmtree(destdir)
  os.mkdir(destdir)

  debdir = os.path.dirname(os.path.abspath(__file__))         # / deb build script root path

  print "Destination directory: " + destdir

  hgrootdir = os.path.normpath(os.path.realpath( os.path.join(debdir, '..', '..') ))

  print "HG root directory: " + hgrootdir
  if not os.path.isdir( os.path.join(hgrootdir, '.hg') ):
    print "Error, the hg root folder %s does not contain .hg folder!" % hgrootdir
    exit(1)


  # Parse build.conf (in buildscripts folder)
  configure(os.path.join(hgrootdir, 'buildscripts', 'build.conf'))


  # Folder where hg contents are exported and prepared for packaging (scripts are run)
  exportdir = os.path.normpath(os.path.realpath( os.path.join(hgrootdir, '..', package_name + '-export-deb') ))
  print "Source export directory: " + exportdir


  print "\nABOUT TO PERFORM BUILD EXPORT\n"
  print "to: %s" % os.path.normpath(os.path.realpath(exportdir))

  # Export source to export folder and run scripts
  sys.path = [os.path.join(debdir, '..')] + sys.path
  try:
    import build_prepare
  except:
    print "Failed to import build_prepare, expected to find it at %s. Make sure to run this script from hgroot/buildscripts/deb/" % os.path.normpath(os.path.realpath(os.path.join(debdir, '..')))
    exit(1)
  if os.path.exists(exportdir):
    shutil.rmtree(exportdir)
  exportInfo = build_prepare.export(sourcePath = hgrootdir, exportFolder = exportdir)

  scriptdir = os.path.abspath( os.path.join(exportdir, 'makehuman') )    # .. Folder containing makehuman.py (source to package)
  print "Makehuman directory: " + scriptdir

  if not exportInfo.isRelease and not package_explicit:
    package_name = package_name + 'hg'

  target = os.path.join(destdir,"debroot")                    # /dest/debroot    contents of deb archive (= target)
  if not os.path.exists(target):
    os.mkdir(target)

  controldir = os.path.join(target,"DEBIAN")                  # /dest/debroot/DEBIAN   deb control files
  if not os.path.exists(controldir):
    os.mkdir(controldir)

  print "Control directory: " + controldir

  srccontrol = os.path.join(debdir,"debian");                 # /debian   source of DEBIAN control templates

  if not os.path.exists(srccontrol):
    print "The debian directory does not exist in the source deb folder. Something is likely horribly wrong. Eeeeek! Giving up and hiding..."
    exit(1)

  bindir = os.path.join(target, "usr", "bin")
  if not os.path.exists(bindir):
    os.makedirs(bindir)

  print "Bin directory: " + bindir

  srcbin = os.path.join(debdir,"bin");                        # /bin    src executable file

  if not os.path.exists(srcbin):
    print "The bin directory does not exist in the source deb folder. Something is likely horribly wrong. Eeeeek! Giving up and hiding..."
    exit(1)

  docdir = os.path.join(target, "usr", "share", "doc", package_name)
  if not os.path.exists(docdir):
    os.makedirs(docdir)

  print "Doc dir: " + docdir                                # /dest/share/doc/makehuman   docs export folder

  applications = os.path.join(target, "usr", "share", "applications")  # /dest/share/applications   app shortcut export folder
  if not os.path.exists(applications):
    os.mkdir(applications)

  print "Desktop shortcut dir: " + applications

  programdir = os.path.join(target, "usr", "share", "makehuman")    # /dest/share/makehuman   export folder of mh app and data
  if os.path.exists(programdir):
    shutil.rmtree(programdir) # Cannot exist because copytree requires it

  print "Program directory: " + programdir

  print "\nABOUT TO COPY CONTENTS TO DEB DEST\n"

  shutil.copytree(scriptdir, programdir)  # Copy exported makehuman/ folder to programdir

  # Copy icon file from hg to export folder
  svgIcon = os.path.join(hgrootdir, 'makehuman/icons/makehuman.svg')
  shutil.copy(svgIcon, os.path.join(programdir,"makehuman.svg"))

  # Copy files in src bin dir to dest bin dir
  _cp_files(srcbin, bindir)

  # Make a copy of hg revision in docs folder
  try:
    shutil.copy(os.path.join(programdir, 'data', 'VERSION'), os.path.join(docdir,"HGREV.txt"))
  except:
    print "ERROR did not find data/VERSION file (%s)! Your build is incomplete!! Verify your build_prepare settings." % os.path.join(programdir, 'data', 'VERSION')
    exit(1)

  # Copy files in src bin dir to dest bin dir (copy bash wrapper executable)
  _cp_files(srccontrol, controldir)

  hgrev = exportInfo.revision

  # Calculate package size
  # du -cks $target | cut -f 1 | uniq
  du_p = subprocess.Popen(['du', '-cks', target], stdout=subprocess.PIPE)
  cut_p = subprocess.Popen(['cut', '-f', '1'], stdin=du_p.stdout, stdout=subprocess.PIPE)
  uniq_p = subprocess.Popen(['uniq'], stdin=cut_p.stdout, stdout=subprocess.PIPE)
  # Allow producer processes to receive SIGPIPE if consumer process exits
  du_p.stdout.close()
  cut_p.stdout.close()
  # Retrieve output
  size = uniq_p.communicate()[0].strip().strip('\n')
  print "\nPackage size: %s\n" % size

  if package_version is None:
    if exportInfo.isRelease:
        # Conform to: http://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Version
        ver = "1:"+exportInfo.version.replace(' ', '.').lower()
    else:
        ver = hgrev
  else:
    ver = package_version

  print "DEB PACKAGE VERSION: %s\n" % ver

  # Replace fields in control file template
  controlFile = os.path.join(controldir, 'control')
  _sed_replace(controlFile, 'VERSION', ver)
  _sed_replace(controlFile, 'PKGNAME', package_name)
  _sed_replace(controlFile, 'REPLACES', package_replaces)
  _sed_replace(controlFile, 'SIZE', size)

  if exportInfo.isRelease:
      ver = exportInfo.version
  else:
      ver = hgrev
  # Create desktop shortcut
  shortcut = os.path.join(applications, "MakeHuman.desktop")
  shutil.move(os.path.join(controldir, "MakeHuman.desktop"), shortcut)
  _sed_replace(shortcut, 'VERSION', ver)


  # Generate changelog
  os.chdir(hgrootdir)
  changelog = os.path.join(docdir,"changelog")
  import glob
  for logfile in glob.glob(changelog+'*'):
    if os.path.isfile(logfile):
      os.remove(logfile)
  branch_p = subprocess.Popen([hgpath,'branch'], stdout=subprocess.PIPE)
  branch = branch_p.communicate()[0].strip().strip('\n')
  print "\nUsing HG branch: %s\n" % branch

  changelog_f = open(changelog, 'wb')
  subprocess.check_call([hgpath,'log','-b',branch], stdout=changelog_f)
  changelog_f.close()
  subprocess.check_call(['gzip', '-9v', changelog])


  os.chdir(target)

  # Move copyright file in place
  copysrc = os.path.join(controldir,"copyright")
  copydest = os.path.join(docdir,"copyright")
  shutil.move(copysrc, copydest)

  # Move license file in place
  lsrc = os.path.join(programdir,"license.txt")
  ldst = os.path.join(docdir,"LICENSE.txt")
  shutil.move(lsrc, ldst)

  try:
    subprocess.check_call(["chown", "-R", "0:0", target])
  except:
    print "Failed to chown to root. Operation not permitted?"
  try:
    subprocess.check_call(["chmod", "-R", "644", target])
    for path, dirs, files in os.walk(target):
      for d in dirs:
        dpath = os.path.join(target, path, d)
        try:
          subprocess.check_call(["chmod", "755", dpath])
        except:
          print "Failed to chmod 755 folder %s" % dpath
    subprocess.check_call(["chmod", "755", target])
  except:
    print "Failed to chmod."

  for x in files_to_chmod_executable:
    if os.path.exists(x):
      subprocess.check_call(["chmod", "755", x])

  outputdir = os.path.join(destdir,"output")

  if not os.path.exists(outputdir):
    os.mkdir(outputdir)

  os.chdir(outputdir)

  if package_version is None:
    if exportInfo.isRelease:
        ver = exportInfo.version.replace(' ', '.').lower()
    else:
        ver = hgrev
  else:
    ver = package_version
  debfile = os.path.join(outputdir,package_name + "-" + ver + "_all.deb")

  debcmd = ["dpkg-deb", "-Z", "bzip2", "-z", "9", "-b", "../debroot", debfile]

  print debcmd
  subprocess.check_call(debcmd)

  print "\n\n\nPackage is now available in " + debfile + "\n"
  print "If you are building for release, you should now run:\n"
  print "  lintian " + debfile + "\n"
  print "... in order to check the deb file.\n"


def _parse_args():
    if len(sys.argv) < 2:
        return dict()

    import argparse    # requires python >= 2.7
    parser = argparse.ArgumentParser()

    # positional arguments
    parser.add_argument("destination", default=None, nargs='?', help="Destination path for deb build, can also be set using makehuman_dest environment variable if this argument is left empty.")

    argOptions = vars(parser.parse_args())
    return argOptions


if __name__ == '__main__':
  args = _parse_args()
  buildDeb(args.get('destination', None))
