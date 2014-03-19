#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

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

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Rigify-specific non-deform bones
"""

from armature.flags import *

Joints = [
    ('l-ball-1',            'vo', (12889, -0.5, 0, 0)),
    ('l-ball-2',            'vo', (12889, 0.5, 0, 0)),
    ('r-ball-1',            'vo', (6292, 0.5, 0, 0)),
    ('r-ball-2',            'vo', (6292, -0.5, 0, 0)),
]

HeadsTails = {
    'heel.L' :             ('l-ankle', 'l-heel'),
    'heel.02.L' :          ('l-ball-1', 'l-ball-2'),

    'heel.R' :             ('r-ankle', 'r-heel'),
    'heel.02.R' :          ('r-ball-1', 'r-ball-2'),
}

Armature = {
    'heel.L' :             (180*D, 'shin.L', F_CON, L_HELP2),
    'heel.02.L' :          (0, 'heel.L', 0, L_HELP2),
    'heel.R' :             (180*D, 'shin.R', F_CON, L_HELP2),
    'heel.02.R' :          (0, 'heel.R', 0, L_HELP2),
}
