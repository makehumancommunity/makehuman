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
