#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**     MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:** http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**     MakeHuman Team 2001-2014

**Licensing:**       AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------
Read mhuv file

TODO
"""

import os

def readUvset(filename):
    try:
        fp = open(filename, "r")
    except:
        raise NameError("Cannot open %s" % filename)
        
    
