#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
MakeHuman redhat package build script

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

Create a redhat RPM package for the MakeHuman application.
"""


#
# Do NOT run this as root
#
# Settings can be changed in ../build.conf


# --- CONFIGURATION SETTINGS --- 
package_name = "makehuman"  # Note: 'hg' will be appended if this is a nightly build

package_version = None

# ------------------------------

import sys
import os
import subprocess
import shutil


def buildRpm():
  global package_name
  global package_version

  if os.geteuid() == 0:
    print "You are not allowed to run this script as root. You must run it as a normal user."
    exit(1)

  rpmdir = os.path.dirname(os.path.abspath(__file__))         # / rpm build script root path

  hgrootdir = os.path.normpath(os.path.realpath( os.path.join(rpmdir, '..', '..') ))

  print "HG root directory: " + hgrootdir
  if not os.path.isdir( os.path.join(hgrootdir, '.hg') ):
    print "Error, the hg root folder %s does not contain .hg folder! Make sure you are running this script from buildscripts/rpm in the hg repository." % hgrootdir
    exit(1)


  # Parse build.conf (in buildscripts folder)
  configure(os.path.join(hgrootdir, 'buildscripts', 'build.conf'))


  # Folder where hg contents are exported and prepared for packaging (scripts are run)
  exportdir = os.path.normpath(os.path.realpath( os.path.join(hgrootdir, '..', 'mh-export-rpm') ))
  print "Source export directory: " + exportdir

  homedir = os.getenv('HOME', None)
  if not homedir:
    print "ERROR: cannot get HOME directory from $HOME environment var."
    exit(1)


  # Export source to export folder and run scripts
  sys.path = [os.path.join(rpmdir, '..')] + sys.path
  try:
    import build_prepare
  except:
    print "Failed to import build_prepare, expected to find it at %s. Make sure to run this script from hgroot/buildscripts/rpm/" % os.path.normpath(os.path.realpath(os.path.join(rpmdir, '..')))
    exit(1)
  if os.path.exists(exportdir):
    shutil.rmtree(exportdir)

  exportInfo = build_prepare.export(sourcePath = hgrootdir, exportFolder = exportdir)


  # Copy extra files
  svgIco = os.path.join(hgrootdir, 'makehuman', 'icons', 'makehuman.svg')
  shutil.copy(svgIco, os.path.join(exportdir, 'makehuman', 'makehuman.svg'))

  desktopFile = os.path.join(hgrootdir, 'buildscripts', 'deb', 'debian', 'MakeHuman.desktop')
  desktopDest = os.path.join(exportdir, 'makehuman', 'MakeHuman.desktop')
  shutil.copy(desktopFile, desktopDest)
  subprocess.check_call(['sed', '-i', '-e', 's/VERSION/%s/' % exportInfo.version, desktopDest])
  
  execFile = os.path.join(hgrootdir, 'buildscripts', 'rpm', 'makehuman')
  execDest = os.path.join(exportdir, 'makehuman', 'makehuman')
  if os.path.isfile(execDest):
    os.remove(execDest)
  shutil.copy(execFile, execDest)

  os.remove(os.path.join(exportdir, 'makehuman', 'blendertools', 'copy2blender.bat'))


  # Setup RPM environment
  for d in ['SRPMS', 'BUILD', 'SPECS', 'SOURCES', 'lib', 'RPMS/i386', 'RPMS/noarch']:
    if not os.path.isdir( os.path.join(homedir, 'rpms', d) ):
      os.makedirs( os.path.join(homedir, 'rpms', d) )

  subprocess.check_call(['rpm', '--initdb', '--dbpath', os.path.join(homedir, 'rpms', 'lib')])

  f = open(os.path.join(homedir, '.rpmmacros'), 'wb')
  f.write("%_topdir %(echo $HOME)/rpms")
  f.close()


  # Execute build
  if exportInfo.isRelease:
    os.environ["MH_PKG_NAME"] = package_name
  else:
    os.environ["MH_PKG_NAME"] = package_name + 'hg'
  if package_version is None:
    version = exportInfo.version.replace(" ", ".")
  else:
    version = package_version
  print "RPM PACKAGE VERSION: %s\n" % version
  os.environ["MH_VERSION"] = version
  os.environ["MH_EXPORT_PATH"] = exportdir
  print '\n\nBuilding RPM package "%s" of version "%s"\n\n' % (os.environ["MH_PKG_NAME"], version)
  subprocess.check_call(['bash', 'make_rpm.bash'])


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

    package_name = _conf_get(conf, 'Rpm', 'packageName', package_name)
    package_version = _conf_get(conf, 'Rpm', 'packageVersion', package_version)


if __name__ == '__main__':
  buildRpm()
