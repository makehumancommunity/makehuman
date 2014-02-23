# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; eimcp.r version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See mcp.
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2014
# Coding Standards:    See http://www.makehuman.org/node/165



import bpy
import os
from collections import OrderedDict
from math import pi
from mathutils import *
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

from .utils import *


class CArmature:

    def __init__(self):
        self.name = "Automatic"
        self.boneNames = OrderedDict()
        self.tposeFile = None
        self.rig = None


    def display(self, type):
        print("%s Armature: %s" % (type, self.name))
        for bname,mhx in self.boneNames.items():
            print("  %14s %14s" % (bname, mhx))


    def findArmature(self, rig, ignoreHiddenLayers=True):
        if ignoreHiddenLayers:
            self.rig = rig
        else:
            self.rig = None

        roots = []
        for pb in rig.pose.bones:
            if pb.parent is None:
                roots.append(pb)

        hipsChildren = roots
        nChildren = len(roots)
        first = True
        hips = None
        while first or nChildren != 3:
            if not first and nChildren == 2 and rig.MhReverseHip:
                break
            elif nChildren == 0:
                raise MocapError("Hip bone must have children: %s" % hips.name)
            elif nChildren == 1:
                hips = hipsChildren[0]
                hipsChildren = self.validChildren(hips)
                nChildren = len(hipsChildren)
            elif nChildren == 2:
                counts = self.getChildCount(hipsChildren)
                #for m,n,pb in counts:
                #    print(m,n,pb.name)
                hips = counts[-1][2]
                hipsChildren = self.validChildren(hips)
                nChildren = len(hipsChildren)
            else:
                counts = self.getChildCount(hipsChildren)
                hipsChildren = [counts[-3][2], counts[-2][2], counts[-1][2]]
                nChildren = 3
            if hips is not None:
                print("  Try hips: %s, children: %d" % (hips.name, nChildren))
            first = False

        if hips is None:
            raise MocapError("Found no candidate hip bone")

        print("Mapping bones automatically:")
        print("  hips:", hips.name)
        self.setBone("hips", hips)
        hiphead,hiptail,_ = getHeadTailDir(hips)

        if rig.MhReverseHip and len(hipsChildren) == 2:
            legroot = hipsChildren[1]
            spine = hipsChildren[0]
            _,terminal = self.chainEnd(legroot)
            head,tail,vec = getHeadTailDir(terminal)
            if tail[2] > hiptail[2]:
                legroot = hipsChildren[0]
                spine = hipsChildren[1]
            hipsChildren = [spine] + self.validChildren(legroot)

        if len(hipsChildren) < 3:
            string = "Hips %s has %d children:\n" % (hips.name, len(hipsChildren))
            for child in hipsChildren:
                string += "  %s\n" % child.name
            raise MocapError(string)

        spine = None
        spineTail = hiptail
        leftLeg = None
        leftLegTail = hiptail
        rightLeg = None
        rightLegTail = hiptail

        limbs = []
        for pb in hipsChildren:
            _,terminal = self.chainEnd(pb)
            _,tail,_ = getHeadTailDir(terminal)
            limbs.append((tail[0], pb))
        limbs.sort()
        _,rightLeg = limbs[0]
        _,spine = limbs[1]
        _,leftLeg = limbs[2]

        print("  spine:", spine.name)
        print("  right leg:", rightLeg.name)
        print("  left leg:", leftLeg.name)
        self.findSpine(spine)
        self.findLeg(leftLeg, ".L")
        self.findLeg(rightLeg, ".R")


    def errLimb(self, name, pb, tail):
        if pb is None:
            return ("  No %s\n" % name)
        else:
            return ("  %s = %s, tail = %s\n" % (name, pb.name, tuple(tail)))


    def setBone(self, bname, pb):
        pb.McpBone = bname
        self.boneNames[canonicalName(pb.name)] = bname


    def findTerminal(self, pb, bnames, prefnames=None):
        if prefnames is None:
            prefnames = bnames
        self.setBone(bnames[0], pb)
        bnames = bnames[1:]
        prefnames = prefnames[1:]
        children = self.validChildren(pb)
        if bnames:
            if len(children) >= 1:
                child = children[0]
                for pb in children[1:]:
                    if prefnames[0] in pb.name.lower():
                        child = pb
                        break
                return self.findTerminal(child, bnames, prefnames)
            else:
                return None
        else:
            while len(children) == 1:
                pb = children[0]
                children = self.validChildren(pb)
            return pb


    def findLeg(self, hip, suffix):
        bnames = ["hip"+suffix, "thigh"+suffix, "shin"+suffix, "foot"+suffix, "toe"+suffix]
        prefnames = ["X", "X", "X", "foot", "toe"]
        print("  hip%s:" % suffix, hip.name)
        try:
            thigh = self.validChildren(hip)[0]
        except IndexError:
            raise MocapError("Hip %s has no children" % hip.name)
        shins = self.validChildren(thigh, True)
        if len(shins) == 0:
            raise MocapError("Thigh %s has no children" % thigh.name)
        elif len(shins) > 1:
            shin = thigh
            thigh = hip
            print("  thigh%s:" % suffix, thigh.name)
            print("  shin%s:" % suffix, shin.name)
            bnames = bnames[1:]
            prefnames = prefnames[1:]
        else:
            shin = shins[0]
            foot = None
            if hip.length > shin.length:
                foot = shin
                shin = thigh
                thigh = hip
                bnames = bnames[1:]
                prefnames = prefnames[1:]
            else:
                feet = self.validChildren(shin)
                if feet:
                    foot = feet[0]
            print("  thigh%s:" % suffix, thigh.name)
            print("  shin%s:" % suffix, shin.name)
            if foot:
                print("  foot%s:" % suffix, foot.name)

        self.findTerminal(hip, bnames, prefnames)


    def findArm(self, shoulder, suffix):
        bnames = ["shoulder"+suffix, "upper_arm"+suffix, "forearm"+suffix, "hand"+suffix]
        print("  shoulder%s:" % suffix, shoulder.name)
        try:
            upperarm = self.validChildren(shoulder)[0]
        except IndexError:
            raise MocapError("Shoulder %s has no children" % shoulder.name)
        print("  upper_arm%s:" % suffix, upperarm.name)
        try:
            forearm = self.validChildren(upperarm, True)[0]
        except IndexError:
            raise MocapError("Upper arm %s has no children" % upperarm.name)
        print("  forearm%s:" % suffix, forearm.name)
        hands = self.validChildren(forearm)
        if hands:
            hand = hands[0]
            print("  hand%s:" % suffix, hand.name)
            if upperarm.bone.length < hand.bone.length:
                bnames = ["shoulder"+suffix] + bnames
        self.findTerminal(shoulder, bnames)


    def findHead(self, neck):
        bnames = ["neck", "head"]
        print("  neck:", neck.name)
        self.findTerminal(neck, bnames)


    def findSpine(self, spine1):
        n,spine2 = self.spineEnd(spine1)
        print("  spine:", spine1.name)
        print("  chest:", spine2.name)
        if n == 1:
            bnames = ["spine"]
        elif n == 2:
            bnames = ["spine", "chest"]
        elif n == 3:
            bnames = ["spine", "spine-1", "chest"]
        else:
            bnames = ["spine", "spine-1", "chest", "chest-1"]

        self.findTerminal(spine1, bnames)
        spine2Children = self.validChildren(spine2)
        if len(spine2Children) == 3:
            _,stail,_ = getHeadTailDir(spine2)
            limbs = []
            for pb in spine2Children:
                _,tail,_ = getHeadTailDir(pb)
                limbs.append((tail[0],pb))
            limbs.sort()
            self.findArm(limbs[0][1], ".R")
            self.findHead(limbs[1][1])
            self.findArm(limbs[2][1], ".L")
        else:
            string = ("Could not auto-detect armature because:\nTop of spine %s has %d children:\n" % (spine2.name, len(spine2Children)))
            for child in spine2Children:
                string += "  %s\n" % child.name
            raise MocapError(string)


    def validChildren(self, pb, muteIk=False):
        children = []
        for child in pb.children:
            if validBone(child, self.rig, muteIk):
                children.append(child)
        return children


    def getChildCount(self, children):
        counts = []
        for n,child in enumerate(children):
            counts.append((self.countChildren(child, 5), n, child))
        counts.sort()
        return counts


    def countChildren(self, pb, depth):
        if depth < 0:
            return 0
        n = 1
        for child in pb.children:
            n += self.countChildren(child, depth-1)
        return n


    def chainEnd(self, pb):
        n = 1
        while pb and (len(self.validChildren(pb)) == 1):
            n += 1
            pb = self.validChildren(pb)[0]
        return n,pb


    def spineEnd(self, pb):
        n = 1
        while pb:
            children = self.validChildren(pb)
            if len(children) == 1:
                n += 1
                pb = children[0]
            elif len(children) == 0 and len(pb.children) == 1:
                n += 1
                pb = pb.children[0]
            else:
                return n,pb
        return n,pb


def validBone(pb, rig=None, muteIk=False):
    if rig is not None:
        hidden = True
        for n in range(len(rig.data.layers)):
            if rig.data.layers[n] and pb.bone.layers[n]:
                hidden = False
                break
        if hidden:
            #print("Hidden", pb.name)
            return False

    for cns in pb.constraints:
        if cns.mute or cns.influence < 0.2:
            pass
        elif cns.type[0:5] == 'LIMIT':
            #cns.influence = 0
            pass
        elif cns.type == 'IK':
            if muteIk:
                cns.mute = True
            elif cns.target is None:
                pass
            else:
                return False
        else:
            return False
    return True


def getHeadTailDir(pb):
    mat = pb.bone.matrix_local
    head = Vector(mat.col[3][:3])
    vec = Vector(mat.col[1][:3])
    tail = head + pb.bone.length * vec
    return head, tail, vec
