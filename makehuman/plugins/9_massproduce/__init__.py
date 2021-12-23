#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman community mass produce

**Product Home Page:** TBD

**Code Home Page:**    TBD

**Authors:**           Joel Palmius

**Copyright(c):**      Joel Palmius 2016

**Licensing:**         MIT

Abstract
--------

This plugin generates and exports series of characters

"""

from .massproduce import MassProduceTaskView

category = None
mpView = None

def load(app):
    category = app.getCategory('Community')
    downloadView = category.addTask(MassProduceTaskView(category))

def unload(app):
    pass

