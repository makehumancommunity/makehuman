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

MHX compatibility
"""

from .flags import *


Renames = {
    'spine5' : ('hips', L_UPSPNFK),
    'spine4' : ('spine', L_UPSPNFK),
    'spine3' : ('spine-1', L_UPSPNFK),
    'spine2' : ('chest', L_UPSPNFK),
    'spine1' : ('chest-1', L_UPSPNFK),

    'pelvis.L' : ('pelvis.L', L_TWEAK),
    'pelvis.R' : ('pelvis.R', L_TWEAK),

    'clavicle.L' : ('clavicle.L', L_LARMFK|L_LARMIK),
    'shoulder01.L' : ('deltoid.L', L_LARMFK|L_LARMIK),
    'wrist.L' : ('hand.L', L_LARMFK),
    'finger1-1.L' : ('thumb.01.L', L_LPALM),
    'finger1-2.L' : ('thumb.02.L', L_LHANDFK),
    'finger1-3.L' : ('thumb.03.L', L_LHANDFK),

    'metacarpal1.L' : ('palm_index.L', L_LPALM),
    'finger2-1.L' : ('f_index.01.L', L_LHANDFK),
    'finger2-2.L' : ('f_index.02.L', L_LHANDFK),
    'finger2-3.L' : ('f_index.03.L', L_LHANDFK),

    'metacarpal2.L' : ('palm_middle.L', L_LPALM),
    'finger3-1.L' : ('f_middle.01.L', L_LHANDFK),
    'finger3-2.L' : ('f_middle.02.L', L_LHANDFK),
    'finger3-3.L' : ('f_middle.03.L', L_LHANDFK),

    'metacarpal3.L' : ('palm_ring.L', L_LPALM),
    'finger4-1.L' : ('f_ring.01.L', L_LHANDFK),
    'finger4-2.L' : ('f_ring.02.L', L_LHANDFK),
    'finger4-3.L' : ('f_ring.03.L', L_LHANDFK),

    'metacarpal4.L' : ('palm_pinky.L', L_LPALM),
    'finger5-1.L' : ('f_pinky.01.L', L_LHANDFK),
    'finger5-2.L' : ('f_pinky.02.L', L_LHANDFK),
    'finger5-3.L' : ('f_pinky.03.L', L_LHANDFK),

    'clavicle.R' : ('clavicle.R', L_RARMFK|L_RARMIK),
    'shoulder01.R' : ('deltoid.R', L_RARMFK|L_RARMIK),
    'wrist.R' : ('hand.R', L_RARMFK),
    'finger1-1.R' : ('thumb.01.R', L_RPALM),
    'finger1-2.R' : ('thumb.02.R', L_RHANDFK),
    'finger1-3.R' : ('thumb.03.R', L_RHANDFK),

    'metacarpal1.R' : ('palm_index.R', L_RPALM),
    'finger2-1.R' : ('f_index.01.R', L_RHANDFK),
    'finger2-2.R' : ('f_index.02.R', L_RHANDFK),
    'finger2-3.R' : ('f_index.03.R', L_RHANDFK),

    'metacarpal2.R' : ('palm_middle.R', L_RPALM),
    'finger3-1.R' : ('f_middle.01.R', L_RHANDFK),
    'finger3-2.R' : ('f_middle.02.R', L_RHANDFK),
    'finger3-3.R' : ('f_middle.03.R', L_RHANDFK),

    'metacarpal3.R' : ('palm_ring.R', L_RPALM),
    'finger4-1.R' : ('f_ring.01.R', L_RHANDFK),
    'finger4-2.R' : ('f_ring.02.R', L_RHANDFK),
    'finger4-3.R' : ('f_ring.03.R', L_RHANDFK),

    'metacarpal4.R' : ('palm_pinky.R', L_RPALM),
    'finger5-1.R' : ('f_pinky.01.R', L_RHANDFK),
    'finger5-2.R' : ('f_pinky.02.R', L_RHANDFK),
    'finger5-3.R' : ('f_pinky.03.R', L_RHANDFK),

}

HeadsTails = {
    'upper_arm.L' :        ('l-shoulder', 'l-elbow'),
    'forearm.L' :          ('l-elbow', 'l-hand'),
    'hand.L' :             ('l-hand', 'l-hand-end'),

    'upper_arm.R' :        ('r-shoulder', 'r-elbow'),
    'forearm.R' :          ('r-elbow', 'r-hand'),
    'hand.R' :             ('r-hand', 'r-hand-end'),

    'thigh.L' :            ('l-upper-leg', 'l-knee'),
    'shin.L' :             ('l-knee', 'l-ankle'),
    'foot.L' :             ('l-ankle', 'l-foot-1'),
    'toe.L' :              ('l-foot-1', 'l-toe-2'),

    'thigh.R' :            ('r-upper-leg', 'r-knee'),
    'shin.R' :             ('r-knee', 'r-ankle'),
    'foot.R' :             ('r-ankle', 'r-foot-1'),
    'toe.R' :              ('r-foot-1', 'r-toe-2'),
}

Armature = {
  'upper_arm.L' : ("PlaneArm.L", 'deltoid.L', F_CON, L_LARMFK),
  'forearm.L' : ("PlaneArm.L", 'upper_arm.L', F_CON, L_LARMFK),
  'hand.L' : ("PlaneHand.L", 'forearm.L', F_CON, L_LARMFK),

  'upper_arm.R' : ("PlaneArm.R", 'deltoid.R', F_CON, L_RARMFK),
  'forearm.R' : ("PlaneArm.R", 'upper_arm.R', F_CON, L_RARMFK),
  'hand.R' : ("PlaneHand.R", 'forearm.R', F_CON, L_RARMFK),

  'thigh.L' : ("PlaneLeg.L", 'pelvis.L', F_CON, L_LLEGFK),
  'shin.L' : ("PlaneLeg.L", 'thigh.L', F_CON, L_LLEGFK),
  'foot.L' : ("PlaneFoot.L", 'shin.L', F_CON|F_DEF, L_LLEGFK|L_DEF),
  'toe.L' : ("PlaneFoot.L", 'foot.L', F_CON|F_DEF, L_LLEGFK|L_DEF),

  'thigh.R' : ("PlaneLeg.R", 'pelvis.R', F_CON, L_RLEGFK),
  'shin.R' : ("PlaneLeg.R", 'thigh.R', F_CON, L_RLEGFK),
  'foot.R' : ("PlaneFoot.R", 'shin.R', F_CON|F_DEF, L_RLEGFK|L_DEF),
  'toe.R' : ("PlaneFoot.R", 'foot.R', F_CON|F_DEF, L_RLEGFK|L_DEF),
}

VertexWeights = {
    "foot.L": [],
    "foot.R": [],
    "toe.L": [],
    "toe.R": [],
}

SocketParents = {
    'shoulder02.L' :     'arm_socket.L',
    'shoulder02.R' :     'arm_socket.R',

    'upperleg01.L' :     'leg_socket.L',
    'upperleg01.R' :     'leg_socket.R',
}

Constraints = {

    'shoulder02.L' : [('CopyRot', C_LOCAL, 1, ['upper_arm', 'upper_arm.L', (1,1,1), (0,0,0), True])],
    'lowerarm01.L' : [('IK', 0, 1, ['IK', 'hand.L', 1, None, (True, False,True)])],
    'lowerarm02.L' : [('CopyRot', C_LOCAL, 1, ['hand', 'hand.L', (0,1,0), (0,0,0), True])],
    'upperleg01.L' : [('IK', 0, 1, ['IK', 'shin.L', 1, None, (True, False,True)])],
    'upperleg02.L' : [('CopyRot', C_LOCAL, 1, ['thigh', 'thigh.L', (0,1,0), (0,0,0), True])],
    'lowerleg01.L' : [('IK', 0, 1, ['IK', 'foot.L', 1, None, (True, False,True)])],
    'lowerleg02.L' : [('CopyRot', C_LOCAL, 1, ['shin', 'shin.L', (0,1,0), (0,0,0), True])],

    'shoulder02.R' : [('CopyRot', C_LOCAL, 1, ['upper_arm', 'upper_arm.R', (1,1,1), (0,0,0), True])],
    'lowerarm01.R' : [('IK', 0, 1, ['IK', 'hand.R', 1, None, (True, False,True)])],
    'lowerarm02.R' : [('CopyRot', C_LOCAL, 1, ['hand', 'forearm.R', (0,1,0), (0,0,0), True])],
    'upperleg01.R' : [('IK', 0, 1, ['IK', 'shin.R', 1, None, (True, False,True)])],
    'upperleg02.R' : [('CopyRot', C_LOCAL, 1, ['thigh', 'thigh.R', (0,1,0), (0,0,0), True])],
    'lowerleg01.R' : [('IK', 0, 1, ['IK', 'foot.R', 1, None, (True, False,True)])],
    'lowerleg02.R' : [('CopyRot', C_LOCAL, 1, ['shin', 'shin.R', (0,1,0), (0,0,0), True])],
}