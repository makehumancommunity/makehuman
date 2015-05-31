Commandline MakeTarget tool
---------------------------

This is a commandline version implementing the basic MakeTarget functionality.

Maketarget is a tool that can be used by artists for creating specific
targets that are used in the Makehuman program.
A target contains the offsets by which vertices of the human base model 
(base.obj) deviate from the original to achieve a specific feature.
eg. a long nose could be a target.

These targets are used within Makehuman by blending them with others and
gradually applying them to the basemesh.

This tool allows wavefront .obj files to be used that were edited using any
3D program. The only limitations are that the edit stems from the original
base.obj and that no additional vertices are added or removed. The 3D program
used also needs to preserve the exact order of the vertices.
There are no other limitations on the obj files used.


Usage:
------

There are a commandline version and a version with graphic user interface.
Both do exactly the same thing.
Here follows the explanation of how to use the commandline version.

Options:
    -i --in     input obj or target
    -o --out    output obj or target
    -s --sub    target to subtract from obj
    -a --add    target to add to obj
    -d --dir    input folder to load all objs or targets from
    --intype    type of file to be input, obj (default) or target
                only applicable if --dir is used
    --outtype   type of file that will be output, obj or target (default)
    -h --help   this info
    -v --verbose    verbose mode, shows extra information
    
Usage scenarios:
    maketarget -i foo.obj -o foo.target
        Load foo.obj as input, compare it with base.obj and output the 
        difference as foo.target.
    maketarget --sub=foo1.target -i foo.obj -o foo.target
        Load foo.obj, subtract foo1.target from it, and output the difference
        between the resulting obj and base.obj as foo.target.
    maketarget --add=foo1.target -i foo.obj -o foo.target
        Load foo.obj, add foo1.target to it, and output the difference
        between the resulting obj and base.obj as foo.target.
    maketarget --dir=myfolder
        Load all objs from myfolder, save the difference between the base.obj 
        and each of the input objs to a target file with the same name as the 
        input obj.
    maketarget --dir=myfolder --sub=foo1.target
        Load all objs from myfolder, subtract foo1.target from each of them, and
        save the difference between base.obj and each of the resulting objs to 
        atarget file with the same name as the input obj.
    maketarget --dir=myfolder --add=foo1.target
        Load all objs from myfolder, add foo1.target to each of them, and
        save the difference between base.obj and each of the resulting objs to 
        a target file with the same name as the input obj.
    maketarget --outtype=obj -i foo.target -o foo.obj
        Load foo.target, apply it to base.obj and output the resulting obj as
        foo.obj.
    maketarget --outtype=obj --dir=myfolder --intype=target
        Load all target files from myfolder, apply each of them to base.obj and
        save the result of each to obj with the same name as the target file.
    maketarget --outtype obj --dir myfolder --intype target --sub foo1.target
        Load all target files in myfolder, apply each of them to base.obj while
        also subtracting foo1.target from the result. Save each combination to
        an obj with the same name as the input target.
    maketarget --outtype obj --dir myfolder --intype target --add foo1.target
        Load all target files in myfolder, apply each of them to base.obj while
        also adding foo1.target to the result. Save each combination to an obj 
        with the same name as the input target.

This is the usage information as can be obtained by running the
"maketarget.py --help" command.
Some additional scenarios that are not documented are possible with the tool.
The user is protected from issuing commands that make no sense (eg. do nothing)
as the tool will warn you about this.

Also note that files are never overwritten. Upon encountering an already 
existing file this file is backed up as original_filename.bak. Additional 
backups of the same file are named in order original_filename.bak.0 
original_filename.bak.1 etc.

The GUI version of the tool does exactly the same thing. The exact same options
(except help and verbose) are available in the GUI. The only difference between
commandline and GUI version is that the GUI demands you specify an --in or --dir
parameter. With the commandline tool you can do without as long as you specify
some --add or --sub targets.


Compiling binaries:
-------------------

For the ease of distribution a pyinstaller configuration is supplied to create
a self-contained binary executable for both windows and linux. (MAC OS might 
work but is untested)
For running this executable, the user does not need to install python or any 
other libraries (such as wxwidgets) on his computer.
For building the package, however, you need to have those dependencies 
installed, and need to build the package on the target OS.

There are two build files available:

compilePyinstaller.bat		for building a windows executable
	

compilePyinstaller.sh		for building a linux executable (might work for OSX
							too)

In order to use them you need to create a folder called "pyinstaller" in the
makehuman/tools/standalone/maketarget folder.
The build configs were tested with pyinstaller 1.5.1, but might work on future
or older versions too.

Additionally these dependencies are needed for the respective operating systems:

Windows:
	Python 2.7
		http://python.org/
		I recommend using python 2.7 as I had issues with 2.6 and pyinstaller
		The tool works fine with python 2.6, however
	pywin32
		http://sourceforge.net/projects/pywin32/
		Python extensions for windows. Needed for pyinstaller to work.
	wxpython2.8
		http://www.wxpython.org/
		WX Widgets libraries and python wrappers for windows. Installable as one
		singe package.
		I recommend using the wxPython2.8 win32 unicode package for python 2.7.
	UPX (optional)
		http://upx.sourceforge.net/
		This is a tool for compressing the executable and reduce its size
		Compression will happen automatically if UPX is installed
		To install UPX copy upx.exe to C:\WINDOWS\system32
		
		Note: you will need at least UPX 1.92 beta due to incompatibilites
		with the Visual Studio compiler, with which newer versions of python are 
		compiled on windows.
	
Linux:
	Python 2.6
		http://python.org/
		Version 2.7 works fine too.
		
	python-wxgtk2.8
	libwxgtk2.8
		http://www.wxpython.org/
		http://www.wxwidgets.org/
		WX Widgets libraries and python wrappers for wx
	UPX (optional)
		http://upx.sourceforge.net/
		This is a tool for compressing the executable and reduce its size
		Compression will happen automatically if UPX is installed
		
The pyinstaller script will create all the files that need to be distributed in
a folder called dist/ (this will be an .xrc file, the executable, and a 
resources/ folder containing images used in the GUI).
You can archive the contents of the dist/ folder and distribute these freely
as a standalone application.
		
		
wxWidgets specific information:
-------------------------------

The GUI of this tool has been made using the python version of wxWidgets.
The GUI form itself is not created using application code, but is instead
loaded from the maketarget.xrc file that declares the GUI.
This file was built using wxFormBuilder (http://wxformbuilder.org/). The file
maketarget_gui.fbp is the source file that can be opened in formbuilder. The
xrc file is output generated using the formbuilder application. However, the xrc
could be edited manually too (but this would cause fbp and xrc file to go out of
sync).


More information:
-----------------

For more specific details you can contact the author Jonas Hauquier at the
makehuman.org website.

