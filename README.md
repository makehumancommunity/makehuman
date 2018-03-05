# Makehuman

This is a port of MakeHuman to Python 3 and PyQt5. 

The testing vision for this code is to build a community release that includes the ported code and often-used, user-contributed 
plug-ins.  We hope that the utility of this integrated functionality is sufficient to entice a larger cohort of testers who get
value-added in exchange for the possibility of uncovering deficiencies in our port. When  testing verifies it's robustness it should a suitable replacement for the current bitbucket code extending the future of MakeHuman beyond the Python 2 "end-of-life".

## Current status

WARNING: THE CODE IN THIS REPOSITORY IS CURRENTLY NOT FIT FOR PRODUCTION USE!

If you want a stable release of MakeHuman, see http://www.makehumancommunity.org/content/downloads.html

This said, the code in the master branch will work if a few basic requirements are met:

* NumPy must be at the most version 1.12.1. Versions 1.13.0 and later will not work.
* You must use a graphics card capable of using the opengl calls MH rely on. It is currently not easy to say exactly which these are, but a rule of thumb is that discreet graphics cards from nVidia will work, whereas integrated chips from intel are likely to not work. 

## Getting started

Builds for Windows platforms can be downloaded at: http://download.tuxfamily.org/makehuman/nightly/. These builds include all required dependencies. 

If you rather run the code from source:

* Install git (https://git-scm.com/) with LFS support (https://git-lfs.github.com/). Modern git clients have LFS support included per default. 
* Make sure the command "git" is available via the PATH variable.
* Install python 3.5.x or later from https://www.python.org/ (or via your system's package management)
* Figure out how to run "pip": https://pip.pypa.io/en/stable/ (it should have been installed automatically by python)
* Use "pip" to install dependencies:
  * "pip install numpy==1.12.1"
  * "pip install pyqt5"
  * "pip install numpy"
* Use git to clone https://github.com/makehumancommunity/makehuman.git (or download the source as a zip)
* Run the "download\_assets\_git.py" script in the "makehuman" subdirectory of the source code.
* Optionally also run:
  * compile\_models.py
  * compile\_proxies.py
  * compile\_targets.py

Having done this, you can now start MakeHuman by running the makehuman.py script. 

## Branches

There are three standard branches and some additional developer working branches:

* master: This is where you will find the latest version of MakeHuman.

Read-only reference branches

* bitbucket-stable: This is the code as it looks in the "stable" branch at bitbucket. This is the ancestor of what is now the "master" branch.
* bitbucket-default: This is the code as it looks in the "default" branch at bitbucket.

In addition you may from time to time see feature branches (usually named \_feature...), which are removed after having been merged to the master branch. 



