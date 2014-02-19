#!/bin/bash

STARTDIR=`pwd`

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

cd ~
mkdir -p $HOME/rpms/{SRPMS,BUILD,SPECS,SOURCES,RPMS,lib}
mkdir -p $HOME/rpms/RPMS/{i386,noarch}
rpm --initdb --dbpath $HOME/rpms/lib
echo "%_topdir $HOME/rpms" > $HOME/.rpmmacros

cp $STARTDIR/../makehuman.svg $HOME/rpms/SOURCES/

cd $STARTDIR

