#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import atexit
from cProfile import Profile

_sort = 'cumulative'
_profiler = None
_show = None

def run(cmd, globals, locals):
    prof = Profile()
    try:
        prof.runctx(cmd, globals, locals)
    finally:
        show(prof)

def active():
    return _profiler is not None

def start():
    global _profiler
    if active():
        return
    _profiler = Profile()

def stop():
    global _profiler
    if not active():
        return
    show(_profiler)
    _profiler = None

def accum(cmd, globals, locals):
    if not active():
        return
    _profiler.runctx(cmd, globals, locals)

def show(prof):
    try:
        if _show is not None:
            _show(prof)
        else:
            prof.print_stats(_sort)
    except TypeError:
        pass

def set_sort(sort):
    global _sort
    _sort = sort

def set_show(show):
    global _show
    _show = show

atexit.register(stop)
