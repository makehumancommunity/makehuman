LICENSE
=======

Table of contents
-----------------
A. The overall license setup for MakeHuman
B. The license for the source code as such
C. The license for the bundled assets
D. Concerning the output from MakeHuman


A. The overall license setup for MakeHuman
------------------------------------------

The MakeHuman application consists of two separate parts:

* Source code: the program logic that powers the application. 
* Assets: The graphical data that the application operates on

B. The license for the source code as such
------------------------------------------

The MakeHuman source code is defined as files that contain program logic.
This includes python files, bat scripts, shell scripts and glsl shaders.

Image files required for the user interface as such are also covered. This
includes images for buttons, icons, and slider images.

The MakeHuman source (as defined per the above) is released under AGPL.

Copyright (C) 2001-2020  MakeHuman Team (www.makehumancommunity.org)

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
   
For the full text of the source code license, see 
[LICENSE.CODE.md](LICENSE.CODE.md)

C. The license for the bundled assets
-------------------------------------

The assets are defined as any data contributing to the graphical output of
MakeHuman. This includes:

* The base mesh and proxies
* Targets and modifiers
* Textures
* Clothes (any MHCLO-based asset)
* Poses and expressions

These assets have been released under CC0 1.0 Universal. In summary this means
that to the fullest extent possible, it is the intention of the MakeHuman 
project that anyone can do whatever they want with it.

For the full text of the legal statement regarding the assets, see
[LICENSE.ASSETS.md](LICENSE.ASSETS.md)

D. Concerning the output from MakeHuman
---------------------------------------

It is the opinion of the MakeHuman project that no output from MakeHuman
contains any trace of program logic. That is, regardless of whether you use
the UI as such or if you call functions of MakeHuman via a script (such as 
via the blender importer), what you get is a combination of assets and your
own creative input. As the assets have been released under CC0, there is no
limitation on what you can do with this combined output.

To make it clear, the MakeHuman project makes no claim whatsoever over output
such as:

* Exports to files (FBX, OBJ, DAE, MHX2...)
* Exports via direct integration (import via MPFB)
* Graphical data generated via scripting or plugins
* Renderings
* Screenshots
* Saved model files

We regard these things as your data, which is yours to handle as you see
fit.

Note that what is discussed here are only assets bundled in the MakeHuman 
distribution. If you use a third part asset, such as one downloaded from the 
asset repositories, it is your own responsibility to make sure you abide by
its specific license. That license might be different from the one covering
the assets bundled by MakeHuman.
