#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
MakeHuman debian package build script

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2017

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

settings = dict()

settings["package_version"] = None
settings["package_sub"] = None
settings["signString"] = "Anonymous"
settings["performSign"] = False
settings["performUpload"] = False
settings["hgpath"] = "/usr/bin/hg"

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
import glob
import time

def _cp_files(folder, dest):
  """
  Copy files in folder to dest folder
  """
  for f in os.listdir(folder):
    fpath = os.path.join(folder, f)
    if os.path.isfile(fpath):
      print "Copy %s to %s" % (fpath, os.path.join(dest, f))
      shutil.copy(fpath, os.path.join(dest, f))

def _cp_pattern(srcFolder, destFolder, extIncludingDot):
  """
  Copy files matching pattern in folder to dest folder
  """

  for path, dirs, files in os.walk(srcFolder):
    rel = os.path.relpath(path,srcFolder)
    dest = os.path.join(destFolder,rel)

    for f in files:
      srcFile = os.path.abspath(os.path.join(path,f))

      fileName, fileExtension = os.path.splitext(srcFile)
      if fileExtension == extIncludingDot:
        destFile = os.path.abspath(os.path.join(dest,f))
        destDir = os.path.dirname(destFile)
        if not os.path.exists(destDir):
          os.makedirs(destDir)
          #print destDir
        shutil.copy(srcFile, destFile)

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

  def _conf_get(config, section, option, defaultVal):
    try:
        return config.get(section, option)
    except:
        return defaultVal

  conf = parseConfig(confpath)
  if conf is None:
    print "PPA build requires a build.conf file. %s " % confpath
    sys.exit(1)
  else:
    print "Using config file at %s. NOTE: properties in config file will override any other settings!" % confpath

    settings["hgpath"] = _conf_get(conf, 'General', 'hgPath', settings["hgpath"])
    settings["package_version"] = _conf_get(conf, 'PPA', 'packageVersion', settings["package_version"])
    settings["package_sub"] = _conf_get(conf, 'PPA', 'packageSub', settings["package_sub"])
    settings["signString"] = _conf_get(conf, 'PPA', 'signString', settings["signString"])
    settings["performSign"] = _conf_get(conf, 'PPA', 'performSign', settings["performSign"])
    settings["performUpload"] = _conf_get(conf, 'PPA', 'performUpload', settings["performUpload"])

  if settings["package_sub"] is None or settings["package_version"] is None:
    print "build.conf is incorrect"
    sys.exit(1)

  settings["timestamp"] = time.strftime("%Y%m%d%H%M%S")


def configurePaths():

  print settings

  print "### Starting to configure locations ###\n"

  # Where is the build root?
  print "Build root: " + settings["build_root"]

  # Where is the buildPPA script?
  settings["location_of_script"] = os.path.dirname(os.path.abspath(__file__))
  print "Script location: " + settings["location_of_script"]

  # Where is the source code located?
  settings["source_root"] = os.path.realpath( os.path.join(settings["location_of_script"], '..', '..') )
  print "Source root: " + settings["source_root"]
  if not os.path.isdir( os.path.join(settings["source_root"], '.hg') ):
    print "Error, the hg root folder %s does not contain .hg folder!" % settings["source_root"]
    print "Giving up.\n\n";
    sys.exit(1)

  # We can now read build.conf
  configure(os.path.join(settings["source_root"], 'buildscripts', 'build.conf'))

  # Folder where hg contents are exported and prepared for packaging (scripts are run)
  settings["build_prepare_destination"] = os.path.realpath( os.path.join(settings["build_root"],'build_prepare') )
  if not os.path.exists(settings["build_prepare_destination"]):
      os.mkdir(settings["build_prepare_destination"])
  print "Build_prepare destination: " + settings["build_prepare_destination"]

  # Where do we find deb build configuration files
  settings["deb_config_location"] = os.path.join(settings["location_of_script"],"packages")
  print "Location of deb build config files: " + settings["deb_config_location"]

  # Staging area for building source and binary debs
  settings["deb_staging_location"] = os.path.join(settings["build_root"],"deb_staging") 
  print "Staging area for deb build process: " + settings["deb_staging_location"]
  shutil.copytree(settings["deb_config_location"],settings["deb_staging_location"])

  # Final destination for specific build configs
  settings["main_deb_def"] = os.path.join(settings["deb_staging_location"],"makehuman")
  print "Target deb definition dir for main: " + settings["main_deb_def"]
  settings["dev_deb_def"] = os.path.join(settings["deb_staging_location"],"makehuman-dev")
  print "Target deb definition dir for dev: " + settings["dev_deb_def"]

  # Changelog locations
  settings["main_changelog"] = os.path.join(settings["main_deb_def"],"debian","changelog")
  print "Main changelog: " + settings["main_changelog"]
  settings["dev_changelog"] = os.path.join(settings["dev_deb_def"],"debian","changelog")
  print "Dev changelog: " + settings["dev_changelog"]

  # Directory with extra files to copy
  settings["extras_location"] = os.path.join(settings["location_of_script"],"extras")
  print "Location of various extra files: " + settings["extras_location"]

  # Where to copy extra files
  settings["extras_destination"] = os.path.join(settings["build_prepare_destination"],"extras")
  print "Destination for extras: " + settings["extras_destination"]

  # Staging area for files not managed by build_prepare
  settings["manual_export_location"] = os.path.realpath( os.path.join(settings["build_root"],'export_dev') )
  if os.path.exists(settings["manual_export_location"]):
    shutil.rmtree(settings["manual_export_location"])
  os.mkdir(settings["manual_export_location"])

  # Location of makehuman in source root
  settings["makehuman_source_root"] = os.path.join(settings["source_root"],"makehuman")
  print "Export dir for *-dev files: " + settings["manual_export_location"];

  # .orig tarballs to create
  fn = "makehuman_" + settings["package_version"]
  fn = fn + "+" + settings["timestamp"]
  fn = fn + ".orig.tar.gz"

  settings["main_tar_file"] = os.path.abspath(os.path.join(settings["deb_staging_location"], fn))
  print "Main source tarball: " + settings["main_tar_file"]

  fn = "makehuman-dev_" + settings["package_version"]
  fn = fn + "+" + settings["timestamp"]
  fn = fn + ".orig.tar.gz"

  settings["dev_tar_file"] = os.path.abspath(os.path.join(settings["deb_staging_location"], fn))
  print "Dev source tarball: " + settings["dev_tar_file"]
  
  # Final destination for source deb
  settings["source_final_dest"] = os.path.join(settings["build_root"],"dist_ppa")
  print "Final destination for source deb definition: " + settings["source_final_dest"]

  # Final destination for source deb
  settings["binary_final_dest"] = os.path.join(settings["build_root"],"dist_deb")
  print "Final destination for binary deb files: " + settings["binary_final_dest"]

  print "\n### Finished configuring locations ###\n"
  print ""

def buildSourceTree(dest = None):
  if os.geteuid() != 0:
    print "WARNING: You are not root. You should be running this script with root permissions!"

  if dest is None:
    dest = os.getenv('makehuman_dest',0)

    if dest == 0:
      print "You must explicitly set the makehuman_dest environment variable to point at a work directory, or specify it as argument. I will violently destroy and mutilate the contents of this directory."
      exit(1)

  settings["build_root"] = os.path.normpath(os.path.realpath(dest))          # Folder to build deb package to
  if os.path.exists(settings["build_root"]):
    # Ensure dest dir is empty
    shutil.rmtree(settings["build_root"])
  os.mkdir(settings["build_root"])

  configurePaths();


  print "\nABOUT TO PERFORM BUILD EXPORT\n"
  print "to: %s" % os.path.normpath(os.path.realpath(settings["build_prepare_destination"]))

  # Export source to export folder and run scripts
  sys.path = [os.path.join(settings["location_of_script"], '..')] + sys.path
  try:
    import build_prepare
  except:
    print "Failed to import build_prepare, expected to find it at %s. Make sure to run this script from hgroot/buildscripts/deb/" % os.path.normpath(os.path.realpath(os.path.join(settings["location_of_script"], '..')))
    exit(1)
  if os.path.exists(settings["build_prepare_destination"]):
    shutil.rmtree(settings["build_prepare_destination"])
  exportInfo = build_prepare.export(sourcePath = settings["source_root"], exportFolder = settings["build_prepare_destination"])

  #os.remove(os.path.join(settings["build_prepare_destination"], 'makehuman', 'blendertools'ender.bat'))

  print "\nABOUT TO COPY CONTENTS\n"

  try:
    subprocess.check_call(["chown", "-R", "0:0", settings["build_prepare_destination"]])
  except:
    print "Failed to chown to root. Operation not permitted?"
  try:
    subprocess.check_call(["chmod", "-R", "644", settings["build_prepare_destination"]])
    for path, dirs, files in os.walk(settings["build_prepare_destination"]):
      for d in dirs:
        dpath = os.path.join(settings["build_prepare_destination"], path, d)
        try:
          subprocess.check_call(["chmod", "755", dpath])
        except:
          print "Failed to chmod 755 folder %s" % dpath
    subprocess.check_call(["chmod", "755", settings["build_prepare_destination"]])
  except Exception as e:
    print "Failed to chmod " + settings["build_prepare_destination"]
    print e

  for x in files_to_chmod_executable:
    if os.path.exists(x):
      subprocess.check_call(["chmod", "755", x])

  shutil.copytree(settings["extras_location"],settings["extras_destination"])


  print "\nCOPYING RAW TARGETS FOR -dev\n"
  _cp_pattern(settings["makehuman_source_root"],settings["manual_export_location"],".target")

  print "\nCOPYING RAW OBJS FOR -dev\n"
  _cp_pattern(settings["makehuman_source_root"],settings["manual_export_location"],".obj")

  print "\nCOPYING RAW MHCLO FOR -dev\n"
  _cp_pattern(settings["makehuman_source_root"],settings["manual_export_location"],".mhclo")

  print "\nCOPYING RAW PROXIES FOR -dev\n"
  _cp_pattern(settings["makehuman_source_root"],settings["manual_export_location"],".proxy")

  dummy = os.path.join(settings["manual_export_location"],"dummy.txt")

  with open(dummy, "w") as text_file:
    text_file.write("This is only because moronic debuild cannot handle tarballs which doesn't have a non-dir entry in the root")

  try:
    subprocess.check_call(["chown", "-R", "0:0", settings["manual_export_location"]])
  except:
    print "Failed to chown to root. Operation not permitted?"
  try:
    subprocess.check_call(["chmod", "-R", "644", settings["manual_export_location"]])
    for path, dirs, files in os.walk(settings["manual_export_location"]):
      for d in dirs:
        dpath = os.path.join(settings["manual_export_location"], path, d)
        try:
          subprocess.check_call(["chmod", "755", dpath])
        except:
          print "Failed to chmod 755 folder %s" % dpath
    subprocess.check_call(["chmod", "755", settings["manual_export_location"]])
  except Exception as e:
    print "Failed to chmod " + settings["manual_export_location"]
    print e


def createSourceTarballs():
  print "\nABOUT TO CREATE SOURCE TARBALL FOR BUILD_PREPARE DATA\n\n";

  os.chdir(settings["build_prepare_destination"])

  print "Tarfile: " + settings["main_tar_file"]
  print "CWD: " + os.getcwd()

  subprocess.check_call(["tar","-C",settings["build_prepare_destination"],"-czf", settings["main_tar_file"], "makehuman","README","extras"])

  print "\nABOUT TO CREATE SOURCE TARBALL FOR -DEV DATA\n\n";

  os.chdir(settings["manual_export_location"])


  print "Tarfile: " + settings["dev_tar_file"]
  print "CWD: " + os.getcwd()

  subprocess.check_call(["tar","-C",settings["manual_export_location"],"-cvzf", settings["dev_tar_file"], "data", "dummy.txt"])


def createSourceDebs():

  print "\nWRITING CHANGELOGS\n"

  #ts = Mon, 01 Jun 2015 15:17:49 +0200

  ts = time.strftime("%a, %d %b %Y %H:%M:%S +0200")

  with open(settings["main_changelog"], "w") as text_file:
    text_file.write("makehuman (" + settings["package_version"] + "+" + settings["timestamp"] + "-" + settings["package_sub"] + ") trusty; urgency=low\n\n")
    text_file.write("  * Version bump\n\n")
    text_file.write(" -- " + settings["signString"] + "  " + ts + "\n\n")

  with open(settings["dev_changelog"], "w") as text_file:
    text_file.write("makehuman-dev (" + settings["package_version"] + "+" + settings["timestamp"] + "-" + settings["package_sub"] + ") trusty; urgency=low\n\n")
    text_file.write("  * Version bump\n\n")
    text_file.write(" -- " + settings["signString"] + "  " + ts + "\n\n")


  print "\nSTARTING TO BUILD SOURCE DEB DEFINITIONS\n"
  
  print "Unpacking " + settings["main_tar_file"]
  subprocess.check_call(["tar","-C",settings["main_deb_def"],"-xzf", settings["main_tar_file"]])

  print "Unpacking " + settings["dev_tar_file"]
  subprocess.check_call(["tar","-C",settings["dev_deb_def"],"-xzf", settings["dev_tar_file"]])

  os.chdir(settings["main_deb_def"])

  print "Debuilding in " + os.getcwd()

  if not settings["performSign"] is None and not settings["performSign"]:
    subprocess.check_call(["debuild","-S","-sa","-uc","-us"])
  else:
    subprocess.check_call(["debuild","-S","-sa"])

  os.chdir(settings["dev_deb_def"])

  print "Debuilding in " + os.getcwd()

  if not settings["performSign"] is None and not settings["performSign"]:
    subprocess.check_call(["debuild","-S","-sa","-uc","-us"])
  else:
    subprocess.check_call(["debuild","-S","-sa"])

  os.makedirs(settings["source_final_dest"])

  print "Copying source deb output to " + settings["source_final_dest"]

  for f in glob.glob(settings["deb_staging_location"] + "/*ppa*"):
    print f                                                                                                                                        
    shutil.copy(f, settings["source_final_dest"])

  print "Copying source tarballs to " + settings["source_final_dest"]

  for f in glob.glob(settings["deb_staging_location"] + "/*.orig.*"):
    print f                                                                                                                                        
    shutil.copy(f, settings["source_final_dest"])


def createBinaryDebs():
  print "\nSTARTING TO BUILD DEB FILES\n"
  
  os.chdir(settings["main_deb_def"])

  print "Debuilding in " + os.getcwd()

  if not settings["performSign"] is None and not settings["performSign"]:
    subprocess.check_call(["debuild","-uc","-us"])
  else:
    subprocess.check_call(["debuild"])

  os.chdir(settings["dev_deb_def"])

  print "Debuilding in " + os.getcwd()

  if not settings["performSign"] is None and not settings["performSign"]:
    subprocess.check_call(["debuild","-uc","-us"])
  else:
    subprocess.check_call(["debuild"])

  os.makedirs(settings["binary_final_dest"])

  print "Copying deb files to " + settings["binary_final_dest"]

  for f in glob.glob(settings["deb_staging_location"] + "/*.deb"):
    print f                                                                                                                                        
    shutil.copy(f, settings["binary_final_dest"])


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
  buildSourceTree(args.get('destination', None))
  createSourceTarballs()
  createSourceDebs()
  createBinaryDebs()

