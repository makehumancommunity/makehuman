#!/bin/sh 
installer="dnf"
packages="numpy PyOpenGL PyQt4"

if ! command_exists="$(type -p "$installer")" || [ -z "$command_exists" ]; then
  installer="yum"
fi

$installer install $packages
