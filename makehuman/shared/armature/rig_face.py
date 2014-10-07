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

Face bone definitions
"""

from .flags import *

UseTranslationBones = False
LidPct = 0.5
eyeOffs = (0,0,0.3)
dy = (0,1,0)

Joints = [
    ('head-end',        'l', ((2.0, 'head'), (-1.0, 'neck'))),
    #('head-back',       'v', 955),

    ('l-pupil',         'vl', ((0.5, 14625), (0.5, 14661))),
    ('r-pupil',         'vl', ((0.5, 14670), (0.5, 14706))),

    ('l-eye-end',        'l', ((1.5, 'l-pupil'), (-0.5, 'l-eye'))),
    ('r-eye-end',        'l', ((1.5, 'r-pupil'), (-0.5, 'r-eye'))),

    ('l-eye-top',       'o', ('l-eye-end', dy)),
    ('r-eye-top',       'o', ('r-eye-end', dy)),

    ('l-uplid1',       'v', 6785),
    ('l-lolid1',       'v', 11479),
    ('r-uplid1',       'v', 4847),
    ('r-lolid1',       'v', 4861),

    ('l-uplid0',        'p', ('l-uplid1', 'l-eye', 'l-eye')),
    ('l-lolid0',        'p', ('l-lolid1', 'l-eye', 'l-eye')),
    ('r-uplid0',        'p', ('r-uplid1', 'r-eye', 'r-eye')),
    ('r-lolid0',        'p', ('r-lolid1', 'r-eye', 'r-eye')),

    ('l-uplid',        'l', ((1.5, 'l-uplid1'), (-0.5, 'l-uplid0'))),
    ('l-lolid',        'l', ((1.5, 'l-lolid1'), (-0.5, 'l-lolid0'))),
    ('r-uplid',        'l', ((1.5, 'r-uplid1'), (-0.5, 'r-uplid0'))),
    ('r-lolid',        'l', ((1.5, 'r-lolid1'), (-0.5, 'r-lolid0'))),

    ('l-uplid-top',       'o', ('l-uplid', dy)),
    ('l-lolid-top',       'o', ('l-lolid', dy)),
    ('r-uplid-top',       'o', ('r-uplid', dy)),
    ('r-lolid-top',       'o', ('r-lolid', dy)),

]

Planes = {
    "PlaneEye.L" :         ('l-eye', 'l-eye-end', 'l-eye-top'),
    "PlaneEye.R" :         ('r-eye', 'r-eye-end', 'r-eye-top'),
}

HeadsTails = {
    'jaw' :                 ('mouth', 'jaw'),
    'tongue_base' :         ('tongue-1', 'tongue-2'),
    'tongue_mid' :          ('tongue-2', 'tongue-3'),
    'tongue_tip' :          ('tongue-3', 'tongue-4'),

    'eye.R' :               ('r-eye', 'r-eye-end'),
    'eye_parent.R' :        ('r-eye', 'r-eye-end'),
    'uplid.R' :             ('r-uplid0', 'r-uplid'),
    'lolid.R' :             ('r-lolid0', 'r-lolid'),

    'eye.L' :               ('l-eye', 'l-eye-end'),
    'eye_parent.L' :        ('l-eye', 'l-eye-end'),
    'uplid.L' :             ('l-uplid0', 'l-uplid'),
    'lolid.L' :             ('l-lolid0', 'l-lolid'),
}

Armature = {
    'jaw' :                 (0, 'head', F_DEF|F_NOLOCK, L_HEAD),
    'tongue_base' :         (0, 'jaw', F_DEF|F_SCALE, L_HEAD),
    'tongue_mid' :          (0, 'tongue_base', F_DEF|F_SCALE, L_HEAD),
    'tongue_tip' :          (0, 'tongue_mid', F_DEF|F_SCALE, L_HEAD),
    'eye.R' :               ('PlaneEye.L', 'head', F_DEF, L_HEAD),
    'eye.L' :               ('PlaneEye.R', 'head', F_DEF, L_HEAD),
    'uplid.R' :             (0, 'head', F_DEF|F_LOCKY, L_HEAD),
    'lolid.R' :             (0, 'head', F_DEF|F_LOCKY, L_HEAD),
    'uplid.L' :             (0, 'head', F_DEF|F_LOCKY, L_HEAD),
    'lolid.L' :             (0, 'head', F_DEF|F_LOCKY, L_HEAD),
}

Constraints = {}

CustomShapes = {
    'jaw' :             'GZM_Jaw',
    'eye.R' :           'GZM_Circle025',
    'eye.L' :           'GZM_Circle025',

    'uplid.L' :         'GZM_UpLid',
    'uplid.R' :         'GZM_UpLid',
    'lolid.L' :         'GZM_LoLid',
    'lolid.R' :         'GZM_LoLid',

    'tongue_base' :     'GZM_Tongue',
    'tongue_mid' :      'GZM_Tongue',
    'tongue_tip' :      'GZM_Tongue',
}

LocationLimits = {
    'jaw' :         (-0.2,0.2, -0.2,0.2, -0.2,0.2),
}

RotationLimits = {
    'jaw' :     (-5,45, 0,0, -20,20),
    'uplid.L':  (-10,45, 0,0, 0,0),
    'uplid.R':  (-10,45, 0,0, 0,0),
    'lolid.L':  (-45,10, 0,0, 0,0),
    'lolid.R':  (-45,10, 0,0, 0,0),
}

#
#    DeformDrivers(fp, amt):
#

def DeformDrivers(fp, amt):
    return []
    lidBones = [
    ('DEF_uplid.L', 'PUpLid_L', (0, 40*D)),
    ('DEF_lolid.L', 'PLoLid_L', (0, 20*D)),
    ('DEF_uplid.R', 'PUpLid_R', (0, 40*D)),
    ('DEF_lolid.R', 'PLoLid_R', (0, 20*D)),
    ]

    drivers = []
    for (driven, driver, coeff) in lidBones:
        drivers.append(    (driven, 'ROTQ', 'AVERAGE', None, 1, coeff,
         [("var", 'TRANSFORMS', [('OBJECT', amt.name, driver, 'LOC_Z', C_LOC)])]) )
    return drivers

