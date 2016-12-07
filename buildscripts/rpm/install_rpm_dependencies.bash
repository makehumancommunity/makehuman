#!/bin/sh 
installer="dnf"
packages="numpy PyOpenGL PyQt4"

if command_exist="$(type -p "$installer")" || [ -z "$command_exist" ]; then
  installer="yum"
fi

$installer install $packages
