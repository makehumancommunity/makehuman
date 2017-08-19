# Makehuman (python3)

This is now a near viable port of the current MakeHuman 1.1.1 stable branch to a Python 3 dependency version.  The port 
includes support for the pyside binding to QT4.  This late addition recognizes the end of availability of the pyQt4 Python binding from Riverbank, and it allows testing to proceed.  However, the intention is ultimately to move to QT5 support as final bugs are fixed.

The testing vision for this code is to build a community release that includes the ported code and often-used, user-contributed 
plug-ins.  We hope that the utility of this integrated functionality is sufficient to entice a larger cohort of testers who get
value-added in exchange for the possibility of uncovering deficiencies in our port. When  testing verifies it's robustness it should a suitable replacement for the current bitbucket code extending the future of MakeHuman beyond the Python 2 "end-of-life".


## Branches

There are three standard branches and some additional developer working branches:

* master: This is originally a branch of the code in bitbucket-stable (see below). This is where the python3 conversion happens, and it contains the latest version of MakeHuman

Reference branches
* bitbucket-stable: This is the code as it looks in the stable branch at bitbucket
* bitbucket-default: This is the code as it looks in the default branch at bitbucket

Developer branches
* Aranuvir's branch

A bug tracker for this port can be found at: http://bugtracker.makehumancommunity.org/projects/py3port/activity

Early binary builds for Windows platforms can be downloaded at: http://download.tuxfamily.org/makehuman/nightly/makehuman-python3-20170401-win32.zip
