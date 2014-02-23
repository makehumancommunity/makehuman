These instruction have been written for and tested on Fedora 19 64-bit. 
You will never be able to run the MakeHuman SVN version on distros such
as RHEL/CentOS 6.4 or earlier, since they do not support python 2.7, 
not even if you enable RPMForge. The instructions may or may not work
on other RPM-based distros.


STEP 1 INSTALL SUBVERSION
-------------------------
Install subversion:

  yum install subversion


STEP 2 CHECK OUT CURRENT SVN
----------------------------
Check out the latest revision of the source code:

  svn checkout http://makehuman.googlecode.com/svn/trunk/makehuman/

(this will take a while)


STEP 3 INSTALL REQUIRED DEPENDENCIES
------------------------------------
As root, run the bash script for installing the required dependencies.

  makehuman/rpm/install_rpm_dependencies.bash

This script also installs optional but recommended dependencies. If you
only want the really required dependencies, run

  yum install numpy PyOpenGL PyQt4


STEP 4 RUN MAKEHUMAN
--------------------
Change working directory to the root of the makehuman tree:

  cd makehuman

Then run:

  python makehuman.py

You will most likely want to do this as your normal desktop user, not 
as root.


STEP 5 HOW TO REPORT ERRORS
---------------------------
If makehuman doesn't start, write a forum post under 

  http://www.makehuman.org/forum/index.php

In this report you should include exactly what linux distribution you
are using and at least the contents of the file

  ~/makehuman/makehuman-debug.txt

..which contains essential debugging information. You should probably 
also include the file

  ~/makehuman/makehuman.log

..at least if something crashed or the program did not start at all.


STEP x UPDATE TO LATEST SVN
---------------------------
If some time has passed since you did the above and you want the latest
version, cd into the makehuman root and run

  svn update

You can do this daily if you want to. It will only download the changes,
so it is normally a fast operation. You do not need to re-do the other
steps in order to get an updated version.

