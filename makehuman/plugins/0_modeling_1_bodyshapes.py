#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin to apply bodyshapes targets.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Joel Palmius, punkduck

**Copyright(c):**      MakeHuman Team 2001-2020

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

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

Plugin to work with bodyshape modifiers

"""

__docformat__ = 'restructuredtext'

import humanmodifier
import guimodifier
import getpath


def load(app):
    category = app.getCategory('Modelling')

    humanmodifier.loadModifiers(getpath.getSysDataPath('modifiers/bodyshapes_modifiers.json'), app.selectedHuman)
    guimodifier.loadModifierTaskViews(getpath.getSysDataPath('modifiers/bodyshapes_sliders.json'), app.selectedHuman, category)


def unload(app):
    pass
