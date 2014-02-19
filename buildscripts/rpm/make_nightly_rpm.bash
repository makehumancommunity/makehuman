#!/bin/bash

STARTDIR=`pwd`

if [ ! -e /bin/rpmbuild ]; then
  echo "/bin/rpmbuild does not exist. Maybe you need to install, for example, fedora-packager?"
  cd $STARTDIR
  return 1 
fi

  
ID=`id -u`
if [ $ID == "0" ]; then
  echo "You are not allowed to run this script as root. You must run it as a normal user."
  cd $STARTDIR
  return 1 
fi

cd ..

if [ ! -d "rpm" ]; then
  echo "This script is supposed to be run from inside the makehuman/rpm directory"
  cd $STARTDIR
  return 1 
fi

REV=`svn info | grep Revision | cut --delimiter=" " -f 2`

cd ..

if [ ! -d "$HOME/rpms" ]; then
  echo "$HOME/rpms does not exist. Did you run the setup script?"
  cd $STARTDIR
  return 1 
fi

if [ ! -d "$HOME/rpms/SOURCES" ]; then
  echo "$HOME/rpms/SOURCES does not exist. Did you run the setup script?"
  cd $STARTDIR
  return 1 
fi

SOURCE=$HOME/rpms/SOURCES/makehumansvn-$REV-1.tar.gz

tar --exclude-vcs -cvzf $SOURCE makehuman

cd $STARTDIR

sed -e "s/REV/$REV/g" makehuman.spec > $HOME/rpms/SPECS/makehuman-$REV-1.spec

rpmbuild --target noarch -bb $HOME/rpms/SPECS/makehuman-$REV-1.spec

