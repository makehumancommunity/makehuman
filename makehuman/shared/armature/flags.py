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

Dummy file to put global variables
"""

from math import pi, cos, sin

D = pi/180
C20 = cos(20*pi/180)
S20 = sin(20*pi/180)

MuscleBones = False

yunit = [0,1,0]
ysmall = [0,0.5,0]
zunit = [0,0,-1]
ybis = [0,2,0]

unlimited = (-pi,pi, -pi,pi, -pi,pi)
NoBB = (1,1,1)
NoBB = None
bbMarg = 0.05

AUTO = 10000

#
#    Bone layers
#

L_MAIN =    0x0001
L_CLO =     0x00010000

L_UPSPNFK = 0x0002
L_UPSPNIK = 0x00020000

L_LARMIK =  0x0004
L_LARMFK =  0x0008
L_LLEGIK =  0x0010
L_LLEGFK =  0x0020
L_LHANDIK = 0x0040
L_LHANDFK = 0x0080

L_RARMIK =  0x00040000
L_RARMFK =  0x00080000
L_RLEGIK =  0x00100000
L_RLEGFK =  0x00200000
L_RHANDIK = 0x00400000
L_RHANDFK = 0x00800000

L_PANEL =   0x0100
L_TWEAK =   0x0200
L_TOE =     0x0200
L_HEAD =    0x0400

L_LPALM =   0x0800
L_LEXTRA =  0x1000
L_RPALM =   0x08000000
L_REXTRA =  0x10000000

L_DNSPNFK = 0x2000
L_HAIR =    0x20000000

L_HELP =    0x4000
L_HELP2 =   0x8000
L_MSCL =    0x40000000
L_DEF =     0x80000000

#
#    Flags
#

F_CON = 0x0001
F_DEF = 0x0002
F_RES = 0x0004
F_WIR = 0x0008
F_NOLOC = 0x0020
F_LOCK = 0x0040
F_HID = 0x0080
F_NOCYC = 0x0100
F_NOSCALE = 0x0200
F_NOROT = 0x0400

F_SCALE = 0x0800

F_NOLOCK = 0x1000
F_LOCKROT = 0x2000
F_LOCKY = 0x4000

if MuscleBones:
    F_DEF1 = F_DEF
else:
    F_DEF1 = 0

P_LKROT4 = 0x0001
P_LKROTW = 0x0002
P_IKLIN = 0x0004
P_IKROT = 0x0008
P_HID = 0x0020

P_ROTMODE = 0x0f00
P_QUAT = 0x0000
P_XYZ = 0x0100
P_XZY = 0x0200
P_YXZ = 0x0300
P_YZX = 0x0400
P_ZXY = 0x0500
P_ZYX = 0x0600

C_LTRA = 0x001
C_LOC = 0x002
C_ACT = 0x0004
C_EXP = 0x0008

C_VOLXZ = 0x0010
C_VOLZ = 0x0020
C_VOLX = 0x0040
C_PLANEZ = 0x0080

C_OW_MASK = 0x0300
C_OW_WORLD = 0x0000
C_OW_LOCAL = 0x0100
C_OW_LOCPAR = 0x0200
C_OW_POSE = 0x0300

C_DEFRIG = 0x0400
C_TAIL = 0x0800

C_TG_MASK = 0x3000
C_TG_WORLD = 0x0000
C_TG_LOCAL = 0x1000
C_TG_LOCPAR = 0x2000
C_TG_POSE = 0x3000

C_CHILDOF = C_OW_POSE+C_TG_WORLD
C_LOCAL = C_OW_LOCAL+C_TG_LOCAL


U_LOC = 1
U_ROT = 2
U_SCALE = 4


Master = 'MasterFloor'
Origin = [0,0,0]

