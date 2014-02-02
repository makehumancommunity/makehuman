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
'''
    ('l-uplid0',        'p', ('l-eye', 'l-upperlid', 'l-upperlid')),
    ('r-uplid0',        'p', ('r-eye', 'r-upperlid', 'r-upperlid')),
    ('l-lolid0',        'p', ('l-eye', 'l-lowerlid', 'l-lowerlid')),
    ('r-lolid0',        'p', ('r-eye', 'r-lowerlid', 'r-lowerlid')),

    ('l-uplid',         'l', ((LidPct, 'l-uplid0'), (1-LidPct, 'l-eye'))),
    ('r-uplid',         'l', ((LidPct, 'r-uplid0'), (1-LidPct, 'r-eye'))),
    ('l-lolid',         'l', ((LidPct, 'l-lolid0'), (1-LidPct, 'l-eye'))),
    ('r-lolid',         'l', ((LidPct, 'r-lolid0'), (1-LidPct, 'r-eye'))),

    ('m-uplip-0',       'v', 467),
    ('l-uplip-1',       'v', 7255),
    ('r-uplip-1',       'v', 506),
    ('l-uplip-2',       'v', 7253),
    ('r-uplip-2',       'v', 504),

    ('m-lolip-0',       'v', 495),
    ('l-lolip-1',       'vl', ((0.4, 7238), (0.6, 7244))),
    ('r-lolip-1',       'vl', ((0.4, 483), (0.6, 489))),
    ('l-lolip-2',       'vl', ((0.1, 7238), (0.9, 7232))),
    ('r-lolip-2',       'vl', ((0.1, 483), (0.9, 477))),

    ('l-lip-3',        'v', 7249),
    ('r-lip-3',        'v', 500),

    ('l-mouthside-1',   'v', 11770),
    ('r-mouthside-1',   'v', 5156),
    ('l-mouthside-2',   'vl', ((0.5, 11904), (0.5, 11905))),
    ('r-mouthside-2',   'vl', ((0.5, 5299), (0.5, 5300))),

    ('l-noseside-1',    'v', 11673),
    ('r-noseside-1',    'v', 5056),
    ('l-noseside-2',    'v', 11764),
    ('r-noseside-2',    'v', 5150),

    ('l-loeye-1',       'v', 6920),
    ('r-loeye-1',       'v', 142),
    ('l-loeye-2',       'v', 6917),
    ('r-loeye-2',       'v', 139),
    ('l-loeye-3',       'v', 11714),
    ('r-loeye-3',       'v', 5099),

    ('l-brow-1',        'vl', ((0.5, 6957), (0.5, 6983))),
    ('r-brow-1',        'vl', ((0.5, 181), (0.5, 208))),
    ('l-brow-2',        'v', 6979),
    ('r-brow-2',        'v', 204),
    ('l-brow-3',        'v', 6982),
    ('r-brow-3',        'v', 207),
'''

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

'''
Markers = [
    ('lip_upper_mid',       'm-uplip-0', 'head_back'),
    ('lip_upper_1.L',       'l-uplip-1', 'head_back'),
    ('lip_upper_1.R',       'r-uplip-1', 'head_back'),
    ('lip_upper_2.L',       'l-uplip-2', 'head_back'),
    ('lip_upper_2.R',       'r-uplip-2', 'head_back'),

    ('lip_lower_mid',       'm-lolip-0', 'jaw'),
    ('lip_lower_1.L',       'l-lolip-1', 'jaw'),
    ('lip_lower_1.R',       'r-lolip-1', 'jaw'),
    ('lip_lower_2.L',       'l-lolip-2', 'jaw'),
    ('lip_lower_2.R',       'r-lolip-2', 'jaw'),

    ('lip_3.L',             'l-lip-3', 'head_jaw'),
    ('lip_3.R',             'r-lip-3', 'head_jaw'),
    ('mouthside_1.L',       'l-mouthside-1', 'head_jaw'),
    ('mouthside_1.R',       'r-mouthside-1', 'head_jaw'),
    ('mouthside_2.L',       'l-mouthside-2', 'head_jaw'),
    ('mouthside_2.R',       'r-mouthside-2', 'head_jaw'),

    ('noseside_1.L',        'l-noseside-1', 'head_back'),
    ('noseside_1.R',        'r-noseside-1', 'head_back'),
    ('noseside_2.L',        'l-noseside-2', 'head_back'),
    ('noseside_2.R',        'r-noseside-2', 'head_back'),

    ('eye_below_1.L',       'l-loeye-1', 'head_back'),
    ('eye_below_1.R',       'r-loeye-1', 'head_back'),
    ('eye_below_2.L',       'l-loeye-2', 'head_back'),
    ('eye_below_2.R',       'r-loeye-2', 'head_back'),
    ('eye_below_3.L',       'l-loeye-3', 'head_back'),
    ('eye_below_3.R',       'r-loeye-3', 'head_back'),

    ('eyebrow_1.L',         'l-brow-1', 'head_back'),
    ('eyebrow_1.R',         'r-brow-1', 'head_back'),
    ('eyebrow_2.L',         'l-brow-2', 'head_back'),
    ('eyebrow_2.R',         'r-brow-2', 'head_back'),
    ('eyebrow_3.L',         'l-brow-3', 'head_back'),
    ('eyebrow_3.R',         'r-brow-3', 'head_back'),
]


FaceRigHeadsTails = {
    'head_back' :           ('mouth', ('mouth', (0,1,0))),
    'head_jaw' :            ('mouth', 'jaw'),
}

posOffs = (0,0,0.01)
negOffs = (0,0,-0.05)

if UseTranslationBones:
    for bone,marker,_ in Markers:
        FaceRigHeadsTails[bone] = ((marker, posOffs), (marker, negOffs))
else:
    for bone,marker,parent in Markers:
        Joints.append( (bone, 'p', (marker, marker, 'mouth')) )
        FaceRigHeadsTails[bone] = (bone, (marker, posOffs))
'''

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

'''
FaceRigArmature = {
    'head_back' :           (0, 'head', 0, L_HELP),
    'head_jaw' :            (0, 'head', 0, L_HELP),
}

if UseTranslationBones:
    for bone,marker,parent in Markers:
        FaceRigArmature[bone] = (0, parent, F_DEF|F_WIR|F_NOLOCK|F_LOCKROT, L_PANEL)
else:
    for bone,marker,parent in Markers:
        FaceRigArmature[bone] = (0, parent, F_DEF|F_WIR|F_LOCKY, L_PANEL)
'''

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

'''
FaceRigConstraints = {
     'head_jaw' : [('CopyTrans', 0, 0.5, ['Jaw', 'jaw', 0])],
}

FaceRigCustomShapes = {}
FaceRigLocationLimits = {}
FaceRigRotationLimits = {}

if UseTranslationBones:
    for bone,_,_ in Markers:
        FaceRigCustomShapes[bone] = 'GZM_Cube025'
        FaceRigLocationLimits[bone] = (-0.1,0.1, -0.1,0.1, -0.1,0.1)
else:
    for bone,_,_ in Markers:
        FaceRigCustomShapes[bone] = 'GZM_FaceJaw'
'''

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

