#!/bin/sh 
# Tries to use dnf
installer="dnf"
packages="numpy PyOpenGL PyQt4"

# If dnf is not found, uses yum
if ! command_exists="$(type -p "$installer")" || [ -z "$command_exists" ]; then
  installer="yum"
fi

# Install the packages
$installer install $packages
