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

Contorl bone definitions
"""

from .flags import *


Joints = [
    ('l-ankle-tip',         'o', ('l-ankle', (0,0,-1))),
    ('r-ankle-tip',         'o', ('r-ankle', (0,0,-1))),

    ('l-heel-y',            'v', 12877),
    ('l-heel-z',            'v', 12442),
    ('l-heel',              'p', ('l-toe-2', 'l-foot-1', 'l-heel-z')),
    ('r-heel-y',            'v', 6280),
    ('r-heel-z',            'v', 5845),
    ('r-heel',              'p', ('r-toe-2', 'r-foot-1', 'r-heel-z')),

    ('eyes',                'l', ((0.5, 'r-eye'), (0.5,'l-eye'))),
    ('gaze',                'o', ('eyes', (0,0,5))),

    ('l-rock-2',            'v', 12872),
    ('l-rock-1',            'v', 12859),
    ('r-rock-2',            'v', 6275),
    ('r-rock-1',            'v', 6262),

    ('l-foot-pt',           'l', ((0.5, 'l-ankle'), (0.5, 'l-toe-2'))),
    ('r-foot-pt',           'l', ((0.5, 'r-ankle'), (0.5, 'r-toe-2'))),
]

PlaneJoints = [
    ('l-knee-pt',           ('l-knee', 'PlaneLeg.L', 3)),
    ('r-knee-pt',           ('r-knee', 'PlaneLeg.R', 3)),
    ('l-elbow-pt',          ('l-elbow', 'PlaneArm.L', 3)),
    ('r-elbow-pt',          ('r-elbow', 'PlaneArm.R', 3)),

]

HeadsTails = {
    'master' :             ('ground', ('ground', (0,0,-1))),

    # Head

    'eyes' :            ('eyes', ('eyes', (0,0,1))),
    'gaze' :            ('gaze', ('gaze', (0,0,1))),
    'gaze_parent' :     ('head', 'head-2'),

    # Leg

    'leg_base.L' :      ('l-upper-leg', ('l-upper-leg', ysmall)),
    'leg_hinge.L' :     ('l-upper-leg', ('l-upper-leg', ysmall)),
    'leg_socket.L' :    ('l-upper-leg', ('l-upper-leg', ysmall)),

    'leg_base.R' :      ('r-upper-leg', ('r-upper-leg', ysmall)),
    'leg_hinge.R' :     ('r-upper-leg', ('r-upper-leg', ysmall)),
    'leg_socket.R' :    ('r-upper-leg', ('r-upper-leg', ysmall)),

    'ankle.L' :         ('l-ankle', 'l-ankle-tip'),
    'ankle.ik.L' :      ('l-ankle', 'l-ankle-tip'),

    'ankle.R' :         ('r-ankle', 'r-ankle-tip'),
    'ankle.ik.R' :      ('r-ankle', 'r-ankle-tip'),

    # Pole Targets
    'knee.pt.ik.L' :    ('l-knee-pt', ('l-knee-pt', ysmall)),
    'knee.link.L' :     ('l-knee', 'l-knee-pt'),

    'knee.pt.ik.R' :    ('r-knee-pt', ('r-knee-pt', ysmall)),
    'knee.link.R' :     ('r-knee', 'r-knee-pt'),

    # Arm

    'arm_base.L' :      ('l-shoulder', ('l-shoulder', ysmall)),
    'arm_hinge.L' :     ('l-shoulder', ('l-shoulder', ysmall)),
    'arm_socket.L' :    ('l-shoulder', ('l-shoulder', ysmall)),

    'arm_base.R' :      ('r-shoulder', ('r-shoulder', ysmall)),
    'arm_hinge.R' :     ('r-shoulder', ('r-shoulder', ysmall)),
    'arm_socket.R' :    ('r-shoulder', ('r-shoulder', ysmall)),

    'hand.ik.L' :       ('l-hand', 'l-hand-end'),
    'elbow.pt.ik.L' :   ('l-elbow-pt', ('l-elbow-pt', ysmall)),
    'elbow.link.L' :    ('l-elbow', 'l-elbow-pt'),

    'hand.ik.R' :       ('r-hand', 'r-hand-end'),
    'elbow.pt.ik.R' :   ('r-elbow-pt', ('r-elbow-pt', ysmall)),
    'elbow.link.R' :    ('r-elbow', 'r-elbow-pt'),

    # Finger

    'thumb.L' :         ('l-finger-1-2', 'l-finger-1-4'),
    'index.L' :         ('l-finger-2-1', 'l-finger-2-4'),
    'middle.L' :        ('l-finger-3-1', 'l-finger-3-4'),
    'ring.L' :          ('l-finger-4-1', 'l-finger-4-4'),
    'pinky.L' :         ('l-finger-5-1', 'l-finger-5-4'),

    'thumb.R' :         ('r-finger-1-2', 'r-finger-1-4'),
    'index.R' :         ('r-finger-2-1', 'r-finger-2-4'),
    'middle.R' :        ('r-finger-3-1', 'r-finger-3-4'),
    'ring.R' :          ('r-finger-4-1', 'r-finger-4-4'),
    'pinky.R' :         ('r-finger-5-1', 'r-finger-5-4'),

    # Markers

    'ball.marker.L' :   ('l-foot-1', ('l-foot-1', (0,0.5,0))),
    'toe.marker.L' :    ('l-toe-2', ('l-toe-2', (0,0.5,0))),
    'heel.marker.L' :   ('l-heel', ('l-heel', (0,0.5,0))),

    'ball.marker.R' :   ('r-foot-1', ('r-foot-1', (0,0.5,0))),
    'toe.marker.R' :    ('r-toe-2', ('r-toe-2', (0,0.5,0))),
    'heel.marker.R' :   ('r-heel', ('r-heel', (0,0.5,0))),
}

"""
    # Directions
    ('DirUpLegFwd.L' :    ('l-upper-leg', ('l-upper-leg', (0,0,1))),
    ('DirUpLegFwd.R' :    ('r-upper-leg', ('r-upper-leg', (0,0,1))),
    ('DirUpLegBack.L' :   ('l-upper-leg', ('l-upper-leg', (0,0,-1))),
    ('DirUpLegBack.R' :   ('r-upper-leg', ('r-upper-leg', (0,0,-1))),
    ('DirUpLegOut.L' :    ('l-upper-leg', ('l-upper-leg', (1,0,0))),
    ('DirUpLegOut.R' :    ('r-upper-leg', ('r-upper-leg', (-1,0,0))),

    ('DirKneeBack.L' :    ('l-knee', ('l-knee', (0,0,-1))),
    ('DirKneeBack.R' :    ('r-knee', ('r-knee', (0,0,-1))),
    ('DirKneeInv.L' :     ('l-knee', ('l-knee', (0,1,0))),
    ('DirKneeInv.R' :     ('r-knee', ('r-knee', (0,1,0))),
"""

MasterArmature = {
    'master' :             (0, None, F_WIR, L_MAIN),
}

SocketArmature = {
    'arm_base.L' :      (0, 'deltoid.L', 0, L_HELP),
    'arm_hinge.L' :     (0, 'root', 0, L_HELP),
    'arm_socket.L' :    (0, 'arm_hinge.L', F_WIR|F_NOLOCK, L_TWEAK),

    'arm_base.R' :      (0, 'deltoid.R', 0, L_HELP),
    'arm_hinge.R' :     (0, 'root', 0, L_HELP),
    'arm_socket.R' :    (0, 'arm_hinge.R', F_WIR|F_NOLOCK, L_TWEAK),

    'leg_base.L' :      (0, 'hips', 0, L_HELP),
    'leg_hinge.L' :     (0, 'root', 0, L_HELP),
    'leg_socket.L' :    (0, 'leg_hinge.L', F_WIR|F_NOLOCK, L_TWEAK),

    'leg_base.R' :      (0, 'hips', 0, L_HELP),
    'leg_hinge.R' :     (0, 'root', 0, L_HELP),
    'leg_socket.R' :    (0, 'leg_hinge.R', F_WIR|F_NOLOCK, L_TWEAK),
}

HeadArmature = {
    'eye_parent.R' :    ('PlaneEye.R', 'head', 0, L_HELP),
    'eye_parent.L' :    ('PlaneEye.L', 'head', 0, L_HELP),
    'eye.R' :           ('PlaneEye.R', 'eye_parent.R', F_DEF, L_HEAD),
    'eye.L' :           ('PlaneEye.L', 'eye_parent.L', F_DEF, L_HEAD),
    'gaze_parent' :     (0, None, 0, L_HELP),
    'gaze' :            (180*D, 'gaze_parent', F_NOLOCK, L_HEAD),
    'eyes' :            (0, 'head', 0, L_HELP),
}

MarkerArmature = {
    'ball.marker.L' :   (0, 'foot.L', 0, L_TWEAK),
    'toe.marker.L' :    (0, 'toe.L', 0, L_TWEAK),
    'heel.marker.L' :   (0, 'foot.L', 0, L_TWEAK),

    'ball.marker.R' :   (0, 'foot.R', 0, L_TWEAK),
    'toe.marker.R' :    (0, 'toe.R', 0, L_TWEAK),
    'heel.marker.R' :   (0, 'foot.R', 0, L_TWEAK),
}

RevFootHeadsTails = {
    'foot.ik.L' :       ('l-heel', 'l-toe-2'),
    'toe.rev.L' :       ('l-toe-2', 'l-foot-1'),
    'foot.rev.L' :      ('l-foot-1', 'l-ankle'),
    'foot.pt.ik.L' :    ('l-foot-pt', ('l-foot-pt', (0,1,0))),

    'foot.ik.R' :       ('r-heel', 'r-toe-2'),
    'toe.rev.R' :       ('r-toe-2', 'r-foot-1'),
    'foot.rev.R' :      ('r-foot-1', 'r-ankle'),
    'foot.pt.ik.R' :    ('r-foot-pt', ('r-foot-pt', (0,1,0))),
}

RevFootArmature = {
    'foot.ik.L' :      (180*D, None, F_WIR|F_NOLOCK, L_LLEGIK),
    'toe.rev.L' :      ("PlaneFoot.L", 'foot.ik.L', F_WIR, L_LLEGIK),
    'foot.rev.L' :     ("PlaneFoot.L", 'toe.rev.L', F_WIR, L_LLEGIK, P_XYZ),
    'foot.pt.ik.L' :   (0, 'foot.rev.L', 0, L_HELP2),
    'ankle.L' :        (0, None, F_WIR, L_LEXTRA),
    'ankle.ik.L' :     (0, 'foot.rev.L', F_NOLOCK, L_HELP2),

    'foot.ik.R' :      (180*D, None, F_WIR|F_NOLOCK, L_RLEGIK),
    'toe.rev.R' :      ("PlaneFoot.R", 'foot.ik.R', F_WIR, L_RLEGIK),
    'foot.rev.R' :     ("PlaneFoot.R", 'toe.rev.R', F_WIR, L_RLEGIK, P_XYZ),
    'foot.pt.ik.R' :   (0, 'foot.rev.R', 0, L_HELP2),
    'ankle.R' :        (0, None, F_WIR, L_REXTRA),
    'ankle.ik.R' :     (0, 'foot.rev.R', F_NOLOCK, L_HELP2),

    'knee.pt.ik.L' :   (0, 'ankle.ik.L', F_WIR|F_NOLOCK, L_LLEGIK+L_LEXTRA),
    'knee.link.L' :    (0, 'thigh.ik.L', F_RES, L_LLEGIK+L_LEXTRA),

    'knee.pt.ik.R' :   (0, 'ankle.ik.R', F_WIR|F_NOLOCK, L_RLEGIK+L_REXTRA),
    'knee.link.R' :    (0, 'thigh.ik.R', F_RES, L_RLEGIK+L_REXTRA),
}

IkArmArmature = {
    'hand.ik.L' :      ('hand.L', None, F_WIR|F_NOLOCK, L_LARMIK),
    'elbow.pt.ik.L' :  (0, 'clavicle.L', F_WIR|F_NOLOCK, L_LARMIK),
    'elbow.link.L' :   (0, 'upper_arm.ik.L', F_RES, L_LARMIK),

    'hand.ik.R' :      ('hand.R', None, F_WIR|F_NOLOCK, L_RARMIK),
    'elbow.pt.ik.R' :  (0, 'clavicle.R', F_WIR|F_NOLOCK, L_RARMIK),
    'elbow.link.R' :   (0, 'upper_arm.ik.R', F_RES, L_RARMIK),
}

SocketParents = {
    'upper_arm.L' :     'arm_socket.L',
    'upper_arm.R' :     'arm_socket.R',

    'thigh.L' :         'leg_socket.L',
    'thigh.R' :         'leg_socket.R',
}


RotationLimits = {
    #'arm_socket.L' :    (0,0, 0,0, 0,0),
    #'arm_socket.R' :    (0,0, 0,0, 0,0),
    #'leg_socket.L' :    (0,0, 0,0, 0,0),
    #'leg_socket.R' :    (0,0, 0,0, 0,0),
    #'foot.rev.L' :   (-20,60, 0,0, 0,0),
    #'foot.rev.R' :   (-20,60, 0,0, 0,0),
    #'toe.rev.L' :    (-10,45, 0,0, 0,0),
    #'toe.rev.R' :    (-10,45, 0,0, 0,0),
}


FingerArmature = {
    'thumb.L' :        ('thumb.02.L', 'thumb.01.L', F_WIR, L_LHANDIK),
    'index.L' :        ('f_index.01.L', 'palm_index.L', F_WIR, L_LHANDIK),
    'middle.L' :       ('f_middle.01.L', 'palm_middle.L', F_WIR, L_LHANDIK),
    'ring.L' :         ('f_ring.01.L', 'palm_ring.L', F_WIR, L_LHANDIK),
    'pinky.L' :        ('f_pinky.01.L', 'palm_pinky.L', F_WIR, L_LHANDIK),

    'thumb.R' :        ('thumb.02.R', 'thumb.01.R', F_WIR, L_RHANDIK),
    'index.R' :        ('f_index.01.R', 'palm_index.R', F_WIR, L_RHANDIK),
    'middle.R' :       ('f_middle.01.R', 'palm_middle.R', F_WIR, L_RHANDIK),
    'ring.R' :         ('f_ring.01.R', 'palm_ring.R', F_WIR, L_RHANDIK),
    'pinky.R' :        ('f_pinky.01.R', 'palm_pinky.R', F_WIR, L_RHANDIK),
}

CoordinateSystems = [
    ("upper_arm.L", "forearm.L"),
    ("forearm.L", "hand.L"),
    ("upper_arm.R", "forearm.R"),
    ("forearm.R", "hand.R"),
]


CustomShapes = {
    'master' :          'GZM_Master',

    # Head

    'gaze' :            'GZM_Gaze',

    # Leg

    'leg_socket.L' :    'GZM_Ball025',
    'leg_socket.R' :    'GZM_Ball025',
    'foot.rev.L' :      'GZM_RevFoot',
    'foot.rev.R' :      'GZM_RevFoot',
    'foot.ik.L' :       'GZM_FootIK',
    'foot.ik.R' :       'GZM_FootIK',
    'toe.rev.L' :       'GZM_RevToe',
    'toe.rev.R' :       'GZM_RevToe',
    'ankle.L' :         'GZM_Ball025',
    'ankle.R' :         'GZM_Ball025',
    'knee.pt.ik.L' :    'GZM_Cube025',
    'knee.pt.ik.R' :    'GZM_Cube025',

    # Arm

    'arm_socket.L' :    'GZM_Ball025',
    'arm_socket.R' :    'GZM_Ball025',
    'hand.ik.L' :       'GZM_HandIK',
    'hand.ik.R' :       'GZM_HandIK',
    'elbow.pt.ik.L' :   'GZM_Cube025',
    'elbow.pt.ik.R' :   'GZM_Cube025',

    # Finger

    'thumb.L' :         'GZM_Knuckle',
    'index.L' :         'GZM_Knuckle',
    'middle.L' :        'GZM_Knuckle',
    'ring.L' :          'GZM_Knuckle',
    'pinky.L' :         'GZM_Knuckle',

    'thumb.R' :         'GZM_Knuckle',
    'index.R' :         'GZM_Knuckle',
    'middle.R' :        'GZM_Knuckle',
    'ring.R' :          'GZM_Knuckle',
    'pinky.R' :         'GZM_Knuckle',
}

IkArmChains = {
    "upper_arm" :   ("Upstream", L_LARMIK, "Arm"),
    "forearm" :     ("Leaf", L_LARMIK, L_HELP, 2, "Arm", "hand", "elbow.pt", -90, -90),
    "hand" :        ("DownStream", L_LARMIK, "Arm"),
}

IkLegChains = {
    "thigh" :       ("Upstream", L_LLEGIK, "Leg"),
    "shin" :        ("Leaf", L_LLEGIK, L_TWEAK, 2, "Leg", "ankle", "knee.pt", -90, -90),
    "foot" :        ("DownStream", L_LLEGIK, "Leg"),
    "toe" :         ("DownStream", L_LLEGIK, "Leg"),
}

LegMarkers = [
    'toe', 'ball', 'heel'
]


Hint = 18


HeadConstraints = {
    'gaze_parent' : [
         ('CopyTrans', 0, 1, ['head', 'head', 0])
         ],
    'eyes' : [
        ('IK', 0, 1, ['IK', 'gaze', 1, None, (True, False,False), 1.0])
        ],
    'eye_parent.L' : [
        ('CopyRot', C_LOCAL, 1, ['eyes', 'eyes', (1,1,1), (0,0,0), True])
        ],
    'eye_parent.R' : [
        ('CopyRot', C_LOCAL, 1, ['eyes', 'eyes', (1,1,1), (0,0,0), True])
        ],
}

RevFootConstraints = {
    'shin.ik.L' :   [
        ('LimitRot', C_OW_LOCAL, 1, ['Hint', (Hint,Hint, 0,0, 0,0), (1,0,0)])
        ],
    'shin.ik.R' :   [
        ('LimitRot', C_OW_LOCAL, 1, ['Hint', (Hint,Hint, 0,0, 0,0), (1,0,0)])
        ],
    'foot.L' : [
         ('IK', 0, 0, ['LegIK', 'foot.rev.L', 1, (-90, 'foot.pt.ik.L'), (1,0,1)]),
         #('IK', 0, 0, ['FreeIK', None, 2, None, (True, False,True)])
        ],
    'foot.R' : [
         ('IK', 0, 0, ['LegIK', 'foot.rev.R', 1, (-90, 'foot.pt.ik.R'), (1,0,1)]),
         #('IK', 0, 0, ['FreeIK', None, 2, None, (True, False,True)])
        ],
    'toe.L' : [
         ('IK', 0, 0, ['LegIK', 'toe.rev.L', 1, (-90, 'foot.pt.ik.L'), (1,0,1)]),
        ],
    'toe.R' : [
         ('IK', 0, 0, ['LegIK', 'toe.rev.R', 1, (-90, 'foot.pt.ik.R'), (1,0,1)]),
        ],
    'ankle.ik.L' : [
         ('CopyLoc', 0, 1, ['Foot', 'foot.rev.L', (1,1,1), (0,0,0), 1, False]),
         ('CopyLoc', 0, 0, ['Ankle', 'ankle.L', (1,1,1), (0,0,0), 0, False])
        ],
    'ankle.ik.R' :  [
         ('CopyLoc', 0, 1, ['Foot', 'foot.rev.R', (1,1,1), (0,0,0), 1, False]),
         ('CopyLoc', 0, 0, ['Ankle', 'ankle.R', (1,1,1), (0,0,0), 0, False])
        ],
    'knee.link.L' : [
         ('StretchTo', 0, 1, ['Stretch', 'knee.pt.ik.L', 0, 1, 3.0])
        ],
    'knee.link.R' : [
         ('StretchTo', 0, 1, ['Stretch', 'knee.pt.ik.R', 0, 1, 3.0])
        ],
}


SocketConstraints = {
    'arm_hinge.L' : [
        ('CopyLoc', 0, 1, ['Location', 'arm_base.L', (1,1,1), (0,0,0), 0, False]),
        ('CopyTrans', 0, 0, ['Hinge', 'arm_base.L', 0])
        ],
    'arm_hinge.R' : [
        ('CopyLoc', 0, 1, ['Location', 'arm_base.R', (1,1,1), (0,0,0), 0, False]),
        ('CopyTrans', 0, 0, ['Hinge', 'arm_base.R', 0])
        ],

    'leg_hinge.L' : [
        ('CopyLoc', 0, 1, ['Location', 'leg_base.L', (1,1,1), (0,0,0), 0, False]),
        ('CopyTrans', 0, 0, ['Hinge', 'leg_base.L', 0])
        ],
    'leg_hinge.R' : [
        ('CopyLoc', 0, 1, ['Location', 'leg_base.R', (1,1,1), (0,0,0), 0, False]),
        ('CopyTrans', 0, 0, ['Hinge', 'leg_base.R', 0])
        ],
}


IkArmConstraints = {
    'forearm.ik.L' :   [
        ('LimitRot', C_OW_LOCAL, 1, ['Hint', (Hint,Hint, 0,0, 0,0), (1,0,0)])
        ],
    'forearm.ik.R' :   [
        ('LimitRot', C_OW_LOCAL, 1, ['Hint', (Hint,Hint, 0,0, 0,0), (1,0,0)])
        ],
    'hand.L' : [
         #('IK', 0, 0, ['FreeIK', None, 2, None, (True, False,False)]),
         ('CopyLoc', 0, 0, ['HandLoc', 'hand.ik.L', (1,1,1), (0,0,0), 0, False]),
         ('CopyRot', 0, 0, ['HandRot', 'hand.ik.L', (1,1,1), (0,0,0), False]),
        ],
    'hand.R' : [
         #('IK', 0, 0, ['FreeIK', None, 2, None, (True, False,False)]),
         ('CopyLoc', 0, 0, ['HandLoc', 'hand.ik.R', (1,1,1), (0,0,0), 0, False]),
         ('CopyRot', 0, 0, ['HandRot', 'hand.ik.R', (1,1,1), (0,0,0), False]),
        ],
    'elbow.link.L' : [
        ('StretchTo', 0, 1, ['Stretch', 'elbow.pt.ik.L', 0, 1, 3.0])
        ],
    'elbow.link.R' : [
        ('StretchTo', 0, 1, ['Stretch', 'elbow.pt.ik.R', 0, 1, 3.0])
        ],
}

FingerConstraints = {
     'thumb.02.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'thumb.L', (1,0,1), (0,0,0), True])],
     'thumb.03.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'thumb.L', (1,0,0), (0,0,0), True])],

     'f_index.01.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'index.L', (1,0,1), (0,0,0), True])],
     'f_index.02.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'index.L', (1,0,0), (0,0,0), True])],
     'f_index.03.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'index.L', (1,0,0), (0,0,0), True])],

     'f_middle.01.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'middle.L', (1,0,1), (0,0,0), True])],
     'f_middle.02.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'middle.L', (1,0,0), (0,0,0), True])],
     'f_middle.03.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'middle.L', (1,0,0), (0,0,0), True])],

     'f_ring.01.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'ring.L', (1,0,1), (0,0,0), True])],
     'f_ring.02.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'ring.L', (1,0,0), (0,0,0), True])],
     'f_ring.03.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'ring.L', (1,0,0), (0,0,0), True])],

     'f_pinky.01.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'pinky.L', (1,0,1), (0,0,0), True])],
     'f_pinky.02.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'pinky.L', (1,0,0), (0,0,0), True])],
     'f_pinky.03.L' : [('CopyRot', C_LOCAL, 1, ['Rot', 'pinky.L', (1,0,0), (0,0,0), True])],

     'thumb.02.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'thumb.R', (1,0,1), (0,0,0), True])],
     'thumb.03.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'thumb.R', (1,0,0), (0,0,0), True])],

     'f_index.01.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'index.R', (1,0,1), (0,0,0), True])],
     'f_index.02.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'index.R', (1,0,0), (0,0,0), True])],
     'f_index.03.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'index.R', (1,0,0), (0,0,0), True])],

     'f_middle.01.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'middle.R', (1,0,1), (0,0,0), True])],
     'f_middle.02.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'middle.R', (1,0,0), (0,0,0), True])],
     'f_middle.03.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'middle.R', (1,0,0), (0,0,0), True])],

     'f_ring.01.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'ring.R', (1,0,1), (0,0,0), True])],
     'f_ring.02.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'ring.R', (1,0,0), (0,0,0), True])],
     'f_ring.03.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'ring.R', (1,0,0), (0,0,0), True])],

     'f_pinky.01.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'pinky.R', (1,0,1), (0,0,0), True])],
     'f_pinky.02.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'pinky.R', (1,0,0), (0,0,0), True])],
     'f_pinky.03.R' : [('CopyRot', C_LOCAL, 1, ['Rot', 'pinky.R', (1,0,0), (0,0,0), True])],

}

#
#   PropLRDrivers
#   (Bone, Name, Props, Expr)
#

SocketPropLRDrivers = [
    ('arm_hinge', 'Hinge', ['ArmHinge'], '1-x1'),
    ('leg_hinge', 'Hinge', ['LegHinge'], '1-x1'),
]


IkLegPropLRDrivers = [
    ('thigh', 'LegIK', ['LegIk'], 'x1'),
    ('thigh', 'LegFK', ['LegIk'], '1-x1'),
    ('shin', 'LegIK', ['LegIk'], 'x1'),
    ('shin', 'LegFK', ['LegIk'], '1-x1'),
    ('foot', 'LegFK', ['LegIk'], '1-x1'),
    ('foot', 'LegIK', ['LegIk', 'LegIkToAnkle'], 'x1*(1-x2)'),
    ('toe', 'LegFK', ['LegIk'], '1-x1'),
    ('toe', 'LegIK', ['LegIk', 'LegIkToAnkle'], 'x1*(1-x2)'),
    ('ankle.ik', 'Foot', ['LegIkToAnkle'], '1-x1'),
    ('ankle.ik', 'Ankle', ['LegIkToAnkle'], 'x1'),
]

IkArmPropLRDrivers = [
    #('shoulder', 'Elbow', ['ElbowPlant'], 'x1'),
    ('upper_arm', 'ArmIK', ['ArmIk', 'ElbowPlant'], 'x1*(1-x2)'),
    ('upper_arm', 'ArmFK', ['ArmIk', 'ElbowPlant'], '1-x1*(1-x2)'),
    #('upper_arm', 'Elbow', ['ElbowPlant'], 'x1'),
    ('forearm', 'ArmIK', ['ArmIk', 'ElbowPlant'], 'x1*(1-x2)'),
    ('forearm', 'ArmFK', ['ArmIk', 'ElbowPlant'], '1-x1*(1-x2)'),
    #('forearm', 'Hand', ['ArmIk', 'ElbowPlant'], 'x1*x2'),
    ('hand', 'ArmFK', ['ArmIk'], '1-x1'),
    #('hand', 'FreeIK', ['ArmIk', 'ElbowPlant'], '(1-x1)*(1-x2)'),
    #('hand', 'HandLoc', ['ArmIk'], 'x1'),
    ('hand', 'HandRot', ['ArmIk'], 'x1'),
    #('HlpLoArm', 'HandRot', ['ArmIk'], 'x1'),
]

FingerPropLRDrivers = [
    ('thumb.02', 'Rot', ['FingerControl'], 'x1'),
    ('thumb.03', 'Rot', ['FingerControl'], 'x1'),
    ('f_index.01', 'Rot', ['FingerControl'], 'x1'),
    ('f_index.02', 'Rot', ['FingerControl'], 'x1'),
    ('f_index.03', 'Rot', ['FingerControl'], 'x1'),
    ('f_middle.01', 'Rot', ['FingerControl'], 'x1'),
    ('f_middle.02', 'Rot', ['FingerControl'], 'x1'),
    ('f_middle.03', 'Rot', ['FingerControl'], 'x1'),
    ('f_ring.01', 'Rot', ['FingerControl'], 'x1'),
    ('f_ring.02', 'Rot', ['FingerControl'], 'x1'),
    ('f_ring.03', 'Rot', ['FingerControl'], 'x1'),
    ('f_pinky.01', 'Rot', ['FingerControl'], 'x1'),
    ('f_pinky.02', 'Rot', ['FingerControl'], 'x1'),
    ('f_pinky.03', 'Rot', ['FingerControl'], 'x1'),
]

IkLegSoftPropLRDrivers = [
    #('KneePT', 'Foot', ['KneeFollowsFoot'], 'x1'),
    #('KneePT', 'Hip', ['KneeFollowsHip', 'KneeFollowsFoot'], 'x1*(1-x2)'),
]

IkArmSoftPropLRDrivers = [
    #('ElbowPT', 'Hand', ['ElbowFollowsHand'], 'x1'),
    #('ElbowPT', 'Shoulder', ['ElbowFollowsHand'], '(1-x1)'),

]

HeadPropDrivers = [
    ('gaze_parent', 'head', ['GazeFollowsHead'], 'x1'),
]

LegPropDrivers = [
    ('thigh.L', 'LimitRot', ['RotationLimits', 'LegIk.L'], 'x1*(1-x2)'),
    ('shin.L', 'LimitRot', ['RotationLimits', 'LegIk.L'], 'x1*(1-x2)'),
    ('foot.L', 'LimitRot', ['RotationLimits', 'LegIk.L'], 'x1*(1-x2)'),

    ('thigh.R', 'LimitRot', ['RotationLimits', 'LegIk.R'], 'x1*(1-x2)'),
    ('shin.R', 'LimitRot', ['RotationLimits', 'LegIk.R'], 'x1*(1-x2)'),
    ('foot.R', 'LimitRot', ['RotationLimits', 'LegIk.R'], 'x1*(1-x2)'),
]

ArmPropDrivers = [
    ('upper_arm.L', 'LimitRot', ['RotationLimits', 'ArmIk.L'], 'x1*(1-x2)'),
    #('LoArm.L', 'LimitRot', ['RotationLimits', 'ArmIk.L'], 'x1*(1-x2)'),
    ('hand.L', 'LimitRot', ['RotationLimits', 'ArmIk.L'], 'x1*(1-x2)'),

    ('upper_arm.R', 'LimitRot', ['RotationLimits', 'ArmIk.R'], 'x1*(1-x2)'),
    #('LoArm.R', 'LimitRot', ['RotationLimits', 'ArmIk.R'], 'x1*(1-x2)'),
    ('hand.R', 'LimitRot', ['RotationLimits', 'ArmIk.R'], 'x1*(1-x2)'),
]

#
#   DeformDrivers
#   Bone : (constraint, driver, rotdiff, keypoints)
#

DeformDrivers = []

#
#   ShapeDrivers
#   Shape : (driver, rotdiff, keypoints)
#

ShapeDrivers = {
}

expr90 = "%.3f*(1-%.3f*x1)" % (90.0/90.0, 2/pi)
expr70 = "%.3f*(1-%.3f*x1)" % (90.0/70.0, 2/pi)
expr60 = "%.3f*(1-%.3f*x1)" % (90.0/60.0, 2/pi)
expr45 = "%.3f*(1-%.3f*x1)" % (90.0/45.0, 2/pi)
expr90_90 = "%.3f*max(1-%.3f*x1,0)*max(1-%.3f*x2,0)" % (90.0/90.0, 2/pi, 2/pi)


HipTargetDrivers = []
"""
    ("legs-forward-90", "LR", expr90,
        [("UpLegVec", "DirUpLegFwd")]),
    ("legs-back-60", "LR", expr60,
        [("UpLegVec", "DirUpLegBack")]),
    ("legs-out-90", "LR", expr90_90,
        [("UpLegVec", "DirUpLegOut"),
         ("UpLeg", "UpLegVec")]),
    ("legs-out-90-neg-90", "LR", expr90_90,
        [("UpLegVec", "DirUpLegOut"),
         ("UpLeg", "UpLegVecNeg")]),
]
"""
KneeTargetDrivers = [
#    ("lolegs-back-90", "LR", expr90,
#        [("LoLeg", "DirKneeBack")]),
#    ("lolegs-back-135", "LR", expr45,
#        [("LoLeg", "DirKneeInv")]),
]


'''
    'MCH-hips_rh_ns_ch.L' :          (0, 'root', F_WIR, L_TWEAK),
    'MCH-knee_hose_parent.L' :          (0, 'MCH-hips_rh_ns_ch.L', F_WIR, L_TWEAK),
    'knee_hose.L' :          (0, 'MCH-knee_hose_parent.L', F_WIR, L_TWEAK),
    'MCH-shin_hose_parent.L' :          (0, 'MCH-hips_rh_ns_ch.L', F_WIR, L_TWEAK),
    'shin_hose.L' :          (0, 'MCH-shin_hose_parent.L', F_WIR, L_TWEAK),
    'DEF-thigh.01.L' :          (0, 'MCH-hips_rh_ns_ch.L', F_WIR, L_TWEAK),
    'MCH-thigh_hose_parent.L' :          (0, '', F_WIR, L_TWEAK),
    'thigh_hose.L' :          (0, 'MCH-thigh_hose_parent.L', F_WIR, L_TWEAK),

    'MCH-hips_ik_ns_ch.L' :          (0, 'root', F_WIR, L_TWEAK),
    'MCH-shin.stretch.ik.L' :          (0, 'MCH-hips_ik_ns_ch.L', F_WIR, L_TWEAK),
    'MCH-thigh.ik.L' :          (0, 'MCH-hips_ik_ns_ch.L', F_WIR, L_TWEAK),
    'MCH-shin.ik.L' :          (0, 'MCH-thigh.ik.L', F_WIR, L_TWEAK),
    'MCH-thigh.nostr.ik.L' :          (0, 'MCH-hips_ik_ns_ch.L', F_WIR, L_TWEAK),
    'MCH-shin.nostr.ik.L' :          (0, 'MCH-thigh.nostr.ik.L', F_WIR, L_TWEAK),
    'MCH-thigh.stretch.ik.L' :          (0, 'MCH-hips_ik_ns_ch.L', F_WIR, L_TWEAK),
    'knee_target.ik.L' :          (0, 'MCH-hips_ik_ns_ch.L', F_WIR, L_TWEAK),

    'MCH-hips_fk_ns_ch.L' :          (0, 'root', F_WIR, L_TWEAK),
    'MCH-thigh.fk.L.socket1' :          (0, 'MCH-hips_fk_ns_ch.L', F_WIR, L_TWEAK),
'''
