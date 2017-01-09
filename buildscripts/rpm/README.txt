These instruction have been written for and tested on Fedora 24 64-bit. 
You will never be able to run the MakeHuman HG version on distros such
as RHEL/CentOS 6.4 or earlier, since they do not support python 2.7, 
not even if you enable RPMForge. The instructions may or may not work
on other RPM-based distros.


STEP 1 INSTALL MERCURIAL
------------------------
Install mercurial (hg):

  dnf install mercurial


STEP 2 CLONE THE CURRENT HG REPOSITORY
--------------------------------------
Check out the latest revision of the source code:

  hg clone https://bitbucket.org/MakeHuman/makehuman

(this will take a while)


STEP 3 INSTALL REQUIRED DEPENDENCIES
------------------------------------
As root, run the bash script for installing the required dependencies.

  makehuman/buildscripts/rpm/install_rpm_dependencies.bash

This script also installs optional but recommended dependencies. If you
only want the really required dependencies, run

  dnf install numpy PyOpenGL PyQt4


STEP 4 RUN MAKEHUMAN
--------------------
Change working directory to the root of the makehuman tree:

  cd makehuman/makehuman

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

  ~/makehuman/A8/makehuman-debug.txt

..which contains essential debugging information. You should probably 
also include the file

  ~/makehuman/A8/makehuman.log

..at least if something crashed or the program did not start at all.


STEP x UPDATE TO LATEST HG
--------------------------
If some time has passed since you did the above and you want the latest
version, cd into the makehuman root and run

  hg pull -u

You can do this daily if you want to. It will only download the changes,
so it is normally a fast operation. You do not need to re-do the other
steps in order to get an updated version.


BUILDING AN RPM PACKAGE
-----------------------
Make sure to have mercurial and rpmbuild installed on your system (updated to
stable branch if required).
With an intact hg copy, change working directory to the buildscripts/rpm folder.
Then execute 

  ./buildRpm.py

The file buildscripts/build.conf.example can be copied to 
buildscripts/build.conf to customize the build process (the sections General, 
BuildPrepare and Rpm apply to the RPM build).

After finishing, the RPM file will be in 
~/rpms/RPMS/noarch/makehuman*.rpm
