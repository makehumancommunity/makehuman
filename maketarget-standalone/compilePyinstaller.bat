:: PyInstaller build script for MakeTarget standalone by Jonas Hauquier
:: Part of Makehuman (www.makehuman.org)
::
:: This script builds a windows one-file executable for the maketarget app.
:: To run this you need to download and extract pyinstaller in the pyinstaller
:: folder (tested with pyinstaller 1.5.1).
:: Also pywin32 needs to be installed. I recommend using python 2.7 as pywin32 
:: had problems installing with python 2.6. Will compress the distributable 
:: with UPX if it is installed (to install it, copy upx.exe to 
:: C:\WINDOWS\system32)
:: NOTE: you will need at least UPX 1.92 beta due to incompatibilites
:: with the Visual Studio compiler, with which newer versions of python are 
:: compiled on windows.
:: You also need the wxPython 2.8 package for windows.
::
:: Remove the --windowed parameter for debugging or for enabling cmd version.

cd pyinstaller

c:\python27\python.exe Configure.py

:: Adding an icon file that does not exist results in a corrupted .exe
set iconpath=..\resources\makehuman.ico
IF EXIST %iconpath% (
	:: Remove the --windowed parameter if you need a version that works on cmdline
	c:\python27\python.exe Makespec.py --onefile --windowed --upx --name=maketarget --icon=%iconpath% ..\maketarget-gui.py
) ELSE (
	:: Remove the --windowed parameter if you need a version that works on cmdline
	c:\python27\python.exe Makespec.py --onefile --windowed --upx --name=maketarget ..\maketarget-gui.py
)
c:\python27\python.exe Build.py maketarget\maketarget.spec

IF NOT EXIST "..\dist" mkdir "..\dist"

copy maketarget\dist\maketarget.exe ..\dist
copy ..\maketarget.xrc ..\dist

:: Copy needed resource files from svn checkout to dist\ folder
IF NOT EXIST "..\dist\resources" mkdir "..\dist\resources"
copy ..\resources\*png ..\dist\resources
copy %iconpath% ..\dist\resources
copy ..\..\makehuman\data\3dobjs\base.obj ..\dist\resources
copy ..\..\makehuman\license.txt ..\dist
copy ..\Readme.txt ..\dist

cd ..
