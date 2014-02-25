#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Needed for gui controls
TODO
"""


import os
import sys

import log

def which(program):
    """
    Checks whether a program exists, similar to http://en.wikipedia.org/wiki/Which_(Unix)
    """
    if sys.platform == "win32" and not program.endswith(".exe"):
        program += ".exe"
        
    log.message("looking for %s", program)
        
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            log.message("%s", exe_file)
            if is_exe(exe_file):
                return exe_file

    return None
