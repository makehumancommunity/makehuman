#!/bin/bash

STARTDIR=`pwd`

if [ -z "$MH_EXPORT_PATH" ]; then
    echo "ERROR: No export path specified (MH_EXPORT_PATH env variable)!"
    exit 1
else
    EXPORT_PATH=$MH_EXPORT_PATH
fi

if [ -z "$MH_PKG_NAME" ]; then
    # Use default
    PACKAGE_NAME="makehuman"
else
    PACKAGE_NAME=$MH_PKG_NAME
fi

if [ -z "$MH_VERSION" ]; then
    echo "WARNING: No MH_VERSION env variable set! Using unknown."
    VERSION="unknown"
else
    VERSION=$MH_VERSION
fi


if [ ! -e EXPORT_PATH ]; then
  echo "$EXPORT_PATH folder does not exist. Make sure you run the build with ./buildRpm.py Do not run this script directly!!"
  return 1 
fi


if [ ! -e /bin/rpmbuild ]; then
  echo "/bin/rpmbuild does not exist. Maybe you need to install, for example, fedora-packager?"
  return 1 
fi

  
ID=`id -u`
if [ $ID == "0" ]; then
  echo "You are not allowed to run this script as root. You must run it as a normal user."
  return 1 
fi


if [ ! -e "makehuman.spec" ]; then
  echo "Cannot find ./makehuman.spec ! This script is supposed to be run from inside the buildscripts/rpm directory in the hg repository."
  return 1 
fi


if [ ! -d "$HOME/rpms" ]; then
  echo "$HOME/rpms does not exist. Did you run the buildRpm.py script?"
  return 1 
fi

if [ ! -d "$HOME/rpms/SOURCES" ]; then
  echo "$HOME/rpms/SOURCES does not exist. Did you run the buildRpm.py script?"
  return 1 
fi


echo "Creating source tarball"
cd $EXPORT_PATH
SOURCE=$HOME/rpms/SOURCES/$PACKAGE_NAME-$VERSION-1.tar.gz
tar --exclude-vcs -cvzf $SOURCE makehuman
cd $STARTDIR

sed -e "s/VER/$VERSION/g" makehuman.spec > $HOME/rpms/SPECS/makehuman-$VERSION-1.spec
sed -i "s/PACKAGE_NAME/$PACKAGE_NAME/g" $HOME/rpms/SPECS/makehuman-$VERSION-1.spec

echo "RPMBUILD"
rpmbuild --target noarch -bb $HOME/rpms/SPECS/makehuman-$VERSION-1.spec

