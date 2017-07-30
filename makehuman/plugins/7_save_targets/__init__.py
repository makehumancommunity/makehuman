#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius, Aranuvir

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehuman.org).

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


Abstract
--------

TODO
"""
import os
import log
from .savetargets import SaveTargetsTaskView


def load(app):
    category = app.getCategory('Utilities')
    taskview = category.addTask(SaveTargetsTaskView(category))


def unload(app):
    meta_file_path = os.path.join(os.path.dirname(__file__), 'cache', 'meta.target')

    if os.path.isfile(meta_file_path):
        try:
            os.remove(meta_file_path)
        except:
            log.error('cannot delete meta target file : %',  meta_file_path)

    if os.path.isdir(os.path.dirname(meta_file_path)):
        try:
            os.rmdir(os.path.dirname(meta_file_path))
        except:
            log.error('cannot delete 7_save_target cache : %',  os.path.dirname(meta_file_path))

