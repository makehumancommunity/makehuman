# makehuman_stable_python3

This is now a near viable to backport of the current MakeHuman 1.1.1 stable branch to a python3 dependency.  The port 
includes support for the pyside binding to QT4.  This late addition recognizes the end of availability of the pyQt4 Python binding from Riverbank, and it allows testing proceed.  However, the intention is ultimately to move to QT5 support as final bugs are fixed.

The testing vision for this code is to build a community release that includes the ported code and often-used user-contributed 
plug-ins.  The utility of this integrated functionality is hoped to be sufficient to entice a larger cohort of testers who get
value-added in exchange for the possibility of uncovering defficiencies in our port.

## Branches

There are four branches and some working developer branches:

* master: At the time of creating the repo, this is the same code as in bitbucket-stable. Master is the branch is the branch
representing canonical development.

Reference branches
* bitbucket-stable: This is the code as it looks right the stable branch at bitbucket
* bitbucket-default: This is the code as it looks right default branch at bitbucket
* old_python3_for_unstable: This is a raw import of the code from the makehuman_python3 repo (static reference to initial effort)

Developer branches
* Aranuvir branch and user=plugins: Aranuvir 
* stable-master: Rob Baer
* pyside: Joel Palmius

A bug tracker for this port can be found at: http://bugtracker.makehumancommunity.org/projects/py3port/activity

Early binary builds for Windows platforms can be downloaded at: http://download.tuxfamily.org/makehuman/nightly/makehuman-python3-20170401-win32.zip
