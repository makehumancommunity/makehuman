#!/bin/bash

##
# PyInstaller build script for MakeTarget standalone by Jonas Hauquier
# Part of Makehuman (www.makehuman.org)
# 
# This script builds a linux one-file executable package (might also work for 
# MacOS, not tested).
# You need to download and extract pyinstaller in the pyinstaller folder 
# (tested with pyinstaller 1.5.1).
# Known to work with python 2.6
# Will compress the distributable with UPX if it is installed.
#
##

pushd pyinstaller

if [[ -e maketarget/dist ]]; then
	rm -R -f maketarget/dist
fi
mkdir maketarget/dist

python Configure.py

python Makespec.py --onefile --upx --name=maketarget ../maketarget-gui.py

python Build.py maketarget/maketarget.spec

if [[ ! -e ../dist ]]; then
	mkdir ../dist
fi

cp maketarget/dist/maketarget ../dist
cp ../maketarget.xrc ../dist

# Copy needed resource files from svn checkout to dist/ folder
if [[ ! -e ../dist/resources ]]; then
	mkdir ../dist/resources
fi

cp ../resources/*png ../dist/resources
cp ../resources/makehuman.ico ../dist/resources
cp ../../makehuman/data/3dobjs/base.obj ../dist/resources
cp ../Readme.txt ../dist
cp ../../makehuman/license.txt ../dist

popd
