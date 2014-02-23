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
Constraints

"""

import math
import numpy as np
import numpy.linalg as la
import transformations as tm
import log

from .flags import *

#
#   Master class
#


class CConstraint:
    def __init__(self, type, name, flags, inf):
        self.name = name
        self.type = type
        self.influence = inf
        self.active = (flags & C_ACT == 0)
        self.expanded = (flags & C_EXP != 0)

        ow = flags & C_OW_MASK
        if ow == 0:
            self.ownsp = 'WORLD'
        elif ow == C_OW_LOCAL:
            self.ownsp = 'LOCAL'
        elif ow == C_OW_LOCPAR:
            self.ownsp = 'LOCAL_WITH_PARENT'
        elif ow == C_OW_POSE:
            self.ownsp = 'POSE'

        tg = flags & C_TG_MASK
        if tg == 0:
            self.targsp = 'WORLD'
        elif tg == C_TG_LOCAL:
            self.targsp = 'LOCAL'
        elif tg == C_TG_LOCPAR:
            self.targsp = 'LOCAL_WITH_PARENT'
        elif tg == C_TG_POSE:
            self.targsp = 'POSE'


    def update(self, amt, bone):
        raise NameError("Unknown constraint: bone %s cns %s type %s" % (bone.name, self.name, self.type))


    def display(self):
        log.debug("    <Constraint %s %s %.3g>", self.type, self.name, self.influence)


    def __repr__(self):
        return ("<CConstraint %s %s>" % (self.name, self.type))


    def writeMhx(self, fp):
        fp.write(
            "      influence %s ;\n" % self.influence +
            "      is_proxy_local False ;\n" +
            "      active %s ;\n" % self.active +
            "      show_expanded %s ;\n" % self.expanded +
            "      target_space '%s' ;\n" % self.targsp +
            "      owner_space '%s' ;\n" % self.ownsp +
            "    end Constraint\n")

#
#   Constraint subclasses
#

class CIkConstraint(CConstraint):
    def __init__(self, flags, inf, data, lockLoc, lockRot):
        CConstraint.__init__(self, "IK", data[0], flags, inf)
        self.subtar = data[1]
        self.chainlen = data[2]
        self.pole = data[3]
        if self.pole:
            (self.angle, self.ptar) = self.pole
        else:
            (self.angle, self.ptar) = (0, None)
        (self.useLoc, self.useRot, self.useStretch) = data[4]
        self.lockLoc = lockLoc
        self.lockRot = lockRot
        (lockRotX, lockRotY, lockRotZ) = lockRot

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s IK True\n" % self.name)

        if self.subtar:
            fp.write(
            "      target Refer Object %s ;\n" % (amt.name) +
            "      subtarget '%s' ;\n" % self.subtar +
            "      use_tail True ;\n")
        else:
            fp.write(
            "      use_tail False ;\n")

        fp.write(
            "      pos_lock Array 1 1 1  ;\n" +
            "      rot_lock Array 1 1 1  ;\n" +
            "      reference_axis 'BONE' ;\n" +
            "      chain_count %d ;\n" % self.chainlen +
            "      ik_type 'COPY_POSE' ;\n" +
            "      iterations 500 ;\n" +
            "      limit_mode 'LIMITDIST_INSIDE' ;\n" +
            "      orient_weight 1 ;\n")

        if self.pole:
            fp.write(
            "      pole_angle %.6g ;\n" % (self.angle*D) +
            "      pole_subtarget '%s' ;\n" % self.ptar +
            "      pole_target Refer Object %s ;\n" % (amt.name))

        fp.write(
            "      use_location %s ;\n" % self.useLoc +
            "      use_rotation %s ;\n" % self.useRot +
            "      use_stretch %s ;\n" % self.useStretch +
            "      weight 1 ;\n")
        CConstraint.writeMhx(self, fp)


    def update(self, amt, bone):
        if self.chainlen == 1:
            target = amt.bones[self.subtar]
            head = bone.getHead()
            goal = target.getHead()
            vec = goal - head
            dist = math.sqrt(np.dot(vec,vec))
            goal = head + vec*(bone.length/dist)
            bone.stretchTo(goal, False)

            if self.ptar:
                pole = amt.bones[self.ptar].getHead()
                bone.poleTargetCorrect(head, goal, pole, self.angle)
        else:
            raise NameError("IK chainlen %d %s" % (self.chainlen, bone.name))


class CActionConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "Action", data[0], flags, inf)
        self.type = "Action"
        self.action = data[1]
        self.subtar = data[2]
        self.channel = data[3]
        (self.sframe, self.eframe) = data[4]
        (self.amin, self.amax) = data[5]

    def writeMhx(self, amt, fp):
        scale = amt.scale
        fp.write(
            "    Constraint %s ACTION True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name)+
            "      action Refer Action %s ; \n" % self.action+
            "      frame_start %s ; \n" % self.sframe +
            "      frame_end %d ; \n" % self.eframe)
        if channel[0:3] == 'LOC':
            fp.write(
            "      maximum %.4f*theScale ; \n" % self.amax*scale +
            "      minimum %.4f*theScale ; \n" % self.amin*scale)
        else:
            fp.write(
            "      maximum %.4f ; \n" % self.amax +
            "      minimum %.4f ; \n" % self.amin)
        fp.write(
            "      subtarget '%s' ; \n" % self.subtar +
            "      transform_channel '%s' ;\n" % self.channel)
        CConstraint.writeMhx(self, fp)


class CCopyRotConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "CopyRot", data[0], flags, inf)
        self.subtar = data[1]
        (self.usex, self.usey, self.usez) = data[2]
        (self.invertX, self.invertY, self.invertZ) = data[3]
        self.useOffs = data[4]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s COPY_ROTATION True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name)+
            "      invert Array %d %d %d ; \n" % (self.invertX, self.invertY, self.invertZ)+
            "      use Array %d %d %d  ; \n" % (self.usex, self.usey, self.usez)+
            "      subtarget '%s' ;\n" % self.subtar +
            "      use_offset %s ; \n" % self.useOffs)
        CConstraint.writeMhx(self, fp)

    def update(self, amt, bone):
        target = amt.bones[self.subtar]
        if self.ownsp == 'WORLD':
            mat = target.matrixGlobal
            bone.matrixGlobal[0,:3] += self.influence*(mat[:3,:3] - bone.matrixGlobal[:3,:3])
        else:
            ay,ax,az = tm.euler_from_matrix(bone.matrixPose, axes='syxz')
            by,bx,bz = tm.euler_from_matrix(target.matrixPose, axes='syxz')
            if self.usex:
                ax += self.influence*(bx-ax)
            if self.usey:
                ay += self.influence*(by-ay)
            if self.usez:
                az += self.influence*(bz-az)
            testbones = ["DfmUpArm1_L", "DfmUpArm2_L", "DfmLoArm1_L", "DfmLoArm2_L", "DfmLoArm3_L"]
            if bone.name in testbones:
                log.debug("%s %s", bone.name, target.name)
                log.debug("%s", str(bone.matrixPose))
                log.debug("%s", str(target.matrixPose))
            bone.matrixPose = tm.euler_matrix(ay, ax, az, axes='syxz')
            if bone.name in testbones:
                log.debug("%s", str(bone.matrixPose))
            bone.updateBone()



class CCopyLocConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "CopyLoc", data[0], flags, inf)
        self.subtar = data[1]
        (self.usex, self.usey, self.usez) = data[2]
        (self.invertX, self.invertY, self.invertZ) = data[3]
        self.head_tail = data[4]
        self.useOffs = data[5]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s COPY_LOCATION True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name)+
            "      invert Array %d %d %d ; \n" % (self.invertX, self.invertY, self.invertZ)+
            "      use Array %d %d %d  ; \n" % (self.usex, self.usey, self.usez)+
            "      head_tail %.3f ;\n" % self.head_tail +
            "      subtarget '%s' ;\n" % self.subtar +
            "      use_offset %s ; \n" % self.useOffs)
        CConstraint.writeMhx(self, fp)

    def update(self, amt, bone):
        target = amt.bones[self.subtar]
        if self.ownsp == 'WORLD':
            mat = target.matrixGlobal
            bone.matrixGlobal[:3,3] += self.influence*(mat[:3,3] - bone.matrixGlobal[:3,3])
        else:
            halt
            mat = target.matrixPose
            bone.matrixPose[:3,3] += self.influence*(mat[:3,3] - bone.matrixPose[:3,3])
            bone.updateBone()


class CCopyScaleConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "CopyScale", data[0], flags, inf)
        self.subtar = data[1]
        (self.usex, self.usey, self.usez) = data[2]
        self.useOffs = data[3]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s COPY_ROTATION True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name) +
            "      use Array %d %d %d  ; \n" % (self.usex, self.usey, self.usez)+
            "      subtarget '%s' ;\n" % self.subtar +
            "      use_offset %s ;\n" % self.useOffs)
        CConstraint.writeMhx(self, fp)

    def update(self, amt, bone):
        target = amt.bones[self.subtar]
        if self.ownsp == 'WORLD':
            mat = target.matrixGlobal
            bone.matrixGlobal[3,:3] += self.influence*(mat[3,:3] - bone.matrixGlobal[3,:3])
        else:
            halt
            mat = target.matrixPose
            if self.usex:
                bone.matrixPose[3,0] += self.influence*(mat[3,0] - bone.matrixPose[3,0])
            if self.usey:
                bone.matrixPose[3,1] += self.influence*(mat[3,1] - bone.matrixPose[3,1])
            if self.usez:
                bone.matrixPose[3,2] += self.influence*(mat[3,2] - bone.matrixPose[3,2])
            bone.updateBone()


class CCopyTransConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "CopyTrans", data[0], flags, inf)
        self.subtar = data[1]
        self.head_tail = data[2]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s COPY_TRANSFORMS True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name) +
            "      head_tail %.3f ;\n" % self.head_tail +
            "      subtarget '%s' ;\n" % self.subtar)
        CConstraint.writeMhx(self, fp)

    def update(self, amt, bone):
        if self.ownsp == 'WORLD':
            mat = amt.bones[self.subtar].matrixGlobal
            bone.matrixGlobal += self.influence*(mat - bone.matrixGlobal)
        else:
            mat = amt.bones[self.subtar].matrixPose
            bone.matrixPose = self.influence*(mat - bone.matrixPose)
            bone.updateBone()


class CLimitRotConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "LimitRot", data[0], flags, inf)
        (self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax) = data[1]
        (self.usex, self.usey, self.usez) = data[2]
        self.ltra = (flags & C_LTRA != 0)

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s LIMIT_ROTATION True\n" % self.name +
            "      use_transform_limit %s ; \n" % self.ltra+
            "      max_x %.4g ;\n" % (self.xmax*D) +
            "      max_y %.4g ;\n" % (self.ymax*D) +
            "      max_z %.4g ;\n" % (self.zmax*D) +
            "      min_x %.4g ;\n" % (self.xmin*D) +
            "      min_y %.4g ;\n" % (self.ymin*D) +
            "      min_z %.4g ;\n" % (self.zmin*D) +
            "      use_limit_x %s ; \n" % self.usex +
            "      use_limit_y %s ; \n" % self.usey +
            "      use_limit_z %s ; \n" % self.usez)
        CConstraint.writeMhx(self, fp)

    def update(self, amt, bone):
        quat = bone.getPoseQuaternion()
        rx,ry,rz = bone.quatAngles(quat)
        if self.usex:
            if rx > self.xmax:
                quat[1] = math.tan(self.xmax/2)
            if rx < self.xmin:
                quat[1] = math.tan(self.xmin/2)
        if self.usey:
            if ry > self.ymax:
                quat[2] = math.tan(self.ymax/2)
            if ry < self.ymin:
                quat[2] = math.tan(self.ymin/2)
        if self.usez:
            if rz > self.zmax:
                quat[3] = math.tan(self.zmax/2)
            if rz < self.zmin:
                quat[3] = math.tan(self.zmin/2)
        bone.setPoseQuaternion(quat)
        bone.updateBone()


class CLimitLocConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "LimitLoc", data[0], flags, inf)
        (self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax) = data[1]
        (self.useminx, self.usemaxx, self.useminy, self.usemaxy, self.useminz, self.usemaxz) = data[2]

    def writeMhx(self, amt, fp):
        scale = amt.scale

        fp.write(
            "    Constraint %s LIMIT_LOCATION True\n" % self.name +
            "      use_transform_limit True ;\n" +
            "      max_x %s*theScale ;\n" % (self.xmax*scale) +
            "      max_y %s*theScale ;\n" % (self.ymax*scale) +
            "      max_z %s*theScale ;\n" % (self.zmax*scale) +
            "      min_x %s*theScale ;\n" % (self.xmin*scale) +
            "      min_y %s*theScale ;\n" % (self.ymin*scale) +
            "      min_z %s*theScale ;\n" % (self.zmin*scale) +
            "      use_max_x %s ;\n" % self.usemaxx +
            "      use_max_y %s ;\n" % self.usemaxy +
            "      use_max_z %s ;\n" % self.usemaxz +
            "      use_min_x %s ;\n" % self.useminx +
            "      use_min_y %s ;\n" % self.useminy +
            "      use_min_z %s ;\n" % self.useminz)
        CConstraint.writeMhx(self, fp)

    def update(self, amt, bone):
        pass


class CLimitScaleConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "LimitScale", data[0], flags, inf)
        (self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax) = data[1]
        (self.usex, self.usey, self.usez) = data[2]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s LIMIT_SCALE True\n" % self.name +
            "      max_x %.4g ;\n" % self.xmax +
            "      max_y %.4g ;\n" % self.ymax +
            "      max_z %.4g ;\n" % self.zmax +
            "      min_x %.4g ;\n" % self.xmin +
            "      min_y %.4g ;\n" % self.ymin +
            "      min_z %.4g ;\n" % self.zmin +
            "      use_max_x %s ;\n" % self.usex +
            "      use_max_y %s ;\n" % self.usey +
            "      use_max_z %s ;\n" % self.usez +
            "      use_min_x %s ;\n" % self.usex +
            "      use_min_y %s ;\n" % self.usey +
            "      use_min_z %s ;\n" % self.usez)
        CConstraint.writeMhx(self, fp)

    def update(self, amt, bone):
        pass


class CTransformConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "Transform", data[0], flags, inf)
        self.subtar = data[1]
        self.map_from = data[2]
        self.from_min = data[3]
        self.from_max = data[4]
        self.map_to_from = data[5]
        self.map_to = data[6]
        self.to_min = data[7]
        self.to_max = data[8]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s TRANSFORM True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name) +
            "      subtarget '%s' ;\n" % self.subtar +
            "      map_from '%s' ;\n" % self.map_from +
            "      from_min_x %s ;\n" % self.from_min[0] +
            "      from_min_y %s ;\n" % self.from_min[1] +
            "      from_min_z %s ;\n" % self.from_min[2] +
            "      from_max_x %s ;\n" % self.from_max[0] +
            "      from_max_y %s ;\n" % self.from_max[1] +
            "      from_max_z %s ;\n" % self.from_max[2] +
            "      map_to '%s' ;\n" % self.map_to +
            "      map_to_x_from '%s' ;\n" % self.map_to_from[0] +
            "      map_to_y_from '%s' ;\n" % self.map_to_from[1] +
            "      map_to_z_from '%s' ;\n" % self.map_to_from[2] +
            "      to_min_x %s ;\n" % self.to_min[0] +
            "      to_min_y %s ;\n" % self.to_min[1] +
            "      to_min_z %s ;\n" % self.to_min[2] +
            "      to_max_x %s ;\n" % self.to_max[0] +
            "      to_max_y %s ;\n" % self.to_max[1] +
            "      to_max_z %s ;\n" % self.to_max[2])
        CConstraint.writeMhx(self, fp)

    def update(self, amt, bone):
        target = amt.bones[self.subtar]
        if self.ownsp == 'WORLD':
            halt
        else:
            if self.map_from != 'ROTATION' or self.map_to != 'ROTATION':
                halt
            brad = tm.euler_from_matrix(target.matrixPose, axes='sxyz')
            arad = []
            for n in range(3):
                if self.from_max[n] == self.from_min[n]:
                    cdeg = self.from_max[n]
                else:
                    bdeg = brad[n]/D
                    if bdeg < self.from_min[n]: bdeg = self.from_min[n]
                    if bdeg > self.from_max[n]: bdeg = self.from_max[n]
                    slope = (self.to_max[n] - self.to_min[n])/float(self.from_max[n] - self.from_min[n])
                    adeg = slope*(bdeg - self.from_min[n]) + self.to_min[n]
                arad.append( adeg*D )
            mat = tm.euler_matrix(arad[0], arad[1], arad[2], axes='sxyz')
            bone.matrixPose[:3,:3] = mat[:3,:3]
            bone.updateBone()
        return
        log.debug("Transform %s %s", bone.name, target.name)
        log.debug("Arad %s", arad)
        log.debug("Brad %s", brad)
        log.debug("P %s", bone.matrixPose)
        log.debug("R %s", bone.matrixRest)
        log.debug("G %s", bone.matrixGlobal)
        pass


class CDampedTrackConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "DampedTrack", data[0], flags, inf)
        self.subtar = data[1]
        self.track = data[2]
        self.headtail = data[3]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s DAMPED_TRACK True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name) +
            "      subtarget '%s' ;\n" % self.subtar +
            "      head_tail %.3g ;\n" % self.headtail +
            "      track_axis '%s' ;\n" % self.track)
        CConstraint.writeMhx(self, fp)


class CLockedTrackConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "LockedTrack", data[0], flags, inf)
        self.subtar = data[1]
        self.trackAxis = data[2]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s LOCKED_TRACK True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name) +
            "      subtarget '%s' ;\n" % self.subtar +
            "      track_axis '%s' ;\n" % self.trackAxis)
        CConstraint.writeMhx(self, fp)


class CStretchToConstraint(CConstraint):
    def __init__(self, flags, inf, data, amt=None):
        CConstraint.__init__(self, "StretchTo", data[0], flags, inf)
        self.subtar = data[1]
        self.head_tail = data[2]
        self.bulge = data[3]
        if (amt != None) and (len(data) > 4):
            if isinstance(data[4], tuple):
                start,end = data[4]
                self.rest_length = amt.parser.distance(start,end)
            else:
                self.rest_length = data[4]
        else:
            self.rest_length = None
        if flags & C_VOLXZ:
            self.volume = 'VOLUME_XZX'
        elif flags & C_VOLX:
            self.volume = 'VOLUME_X'
        elif flags & C_VOLZ:
            self.volume = 'VOLUME_Z'
        else:
            self.volume = 'NO_VOLUME'
        if flags & C_PLANEZ:
            self.axis = 'PLANE_Z'
        else:
            self.axis = 'PLANE_X'

    def writeMhx(self, amt, fp):
        scale = amt.scale
        fp.write(
            "    Constraint %s STRETCH_TO True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name) +
            "      bulge %.2f ;\n" % self.bulge +
            "      head_tail %s ;\n" % self.head_tail +
            "      keep_axis '%s' ;\n" % self.axis +
            "      subtarget '%s' ;\n" % self.subtar +
            "      volume '%s' ;\n" % self.volume)
        if self.rest_length != None:
            fp.write("      rest_length %s*theScale ;\n" % (self.rest_length*scale))
        CConstraint.writeMhx(self, fp)

    def update(self, amt, bone):
        target = amt.bones[self.subtar]
        goal = (1-self.head_tail)*target.getHead() + self.head_tail*target.getTail()
        bone.stretchTo(goal, True)


class CTrackToConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "TrackTo", data[0], flags, inf)
        self.subtar = data[1]
        self.head_tail = data[2]
        self.track_axis = data[3]
        self.up_axis = data[4]
        self.use_target_z = data[5]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s TRACK_TO True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name) +
            "      head_tail %s ;\n" % self.head_tail +
            "      track_axis '%s' ;\n" % self.track_axis +
            "      up_axis '%s' ;\n" % self.up_axis +
            "      subtarget '%s' ;\n" % self.subtar +
            "      use_target_z %s ;\n" % self.use_target_z)
        CConstraint.writeMhx(self, fp)


class CLimitDistConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "LimitDist", data[0], flags, inf)
        self.subtar = data[1]
        self.limit_mode = data[2]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s LIMIT_DISTANCE True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name) +
            "      limit_mode '%s' ;\n" % self.limit_mode +
            "      subtarget '%s' ;\n" % self.subtar)
        CConstraint.writeMhx(self, fp)

    def update(self, amt, bone):
        pass


class CChildOfConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "ChildOf", data[0], flags, inf)
        subtar = data[1]
        (self.locx, self.locy, self.locz) = data[2]
        (self.rotx, self.roty, self.rotz) = data[3]
        (self.scalex, self.scaley, self.scalez) = data[4]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s CHILD_OF True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name) +
            "      subtarget '%s' ;\n" % self.subtar +
            "      use_location_x %s ;\n" % self.locx +
            "      use_location_y %s ;\n" % self.locy +
            "      use_location_z %s ;\n" % self.locz +
            "      use_rotation_x %s ;\n" % self.rotx +
            "      use_rotation_y %s ;\n" % self.roty +
            "      use_rotation_z %s ;\n" % self.rotz +
            "      use_scale_x %s ;\n" % self.scalex +
            "      use_scale_y %s ;\n" % self.scaley +
            "      use_scale_z %s ;\n" % self.scalez)
        CConstraint.writeMhx(self, fp)


class CSplineIkConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "SplineIk", data[0], flags, inf)
        self.target = data[1]
        self.count = data[2]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s SPLINE_IK True\n" % self.name +
            "      target Refer Object %s ;\n" % self.target +
            "      chain_count %d ;\n" % self.count +
            "      use_chain_offset False ;\n" +
            "      use_curve_radius True ;\n" +
            "      use_even_divisions False ;\n" +
            "      use_y_stretch True ;\n" +
            "      xz_scale_mode 'NONE' ;\n")
        CConstraint.writeMhx(self, fp)


class CFloorConstraint(CConstraint):
    def __init__(self, flags, inf, data):
        CConstraint.__init__(self, "Floor", data[0], flags, inf)
        self.subtar = data[1]
        self.floor_location = data[2]
        self.offset = data[3]
        self.use_rotation = data[4]
        self.use_sticky = data[5]

    def writeMhx(self, amt, fp):
        fp.write(
            "    Constraint %s FLOOR True\n" % self.name +
            "      target Refer Object %s ;\n" % (amt.name) +
            "      floor_location '%s' ;\n" % self.floor_location +
            "      offset %.4f ;\n" % self.offset +
            "      subtarget '%s' ;\n" % self.subtar +
            "      use_rotation %s ;\n" % self.use_rotation +
            "      use_sticky %s ;\n" % self.use_sticky)
        CConstraint.writeMhx(self, fp)


def addConstraint(cdef, lockLoc=(False,False,False), lockRot=(False,False,False)):
    (type, flags, inf, data) = cdef
    if type == 'IK':
        return CIkConstraint(flags, inf, data, lockLoc, lockRot)
    elif type == 'Action':
        return CActionConstraint(flags, inf, data)
    elif type == 'CopyRot':
        return CCopyRotConstraint(flags, inf, data)
    elif type == 'CopyLoc':
        return CCopyLocConstraint(flags, inf, data)
    elif type == 'CopyScale':
        return CCopyScaleConstraint(flags, inf, data)
    elif type == 'CopyTrans':
        return CCopyTransConstraint(flags, inf, data)
    elif type == 'LimitRot':
        return CLimitRotConstraint(flags, inf, data)
    elif type == 'LimitLoc':
        return CLimitLocConstraint(flags, inf, data)
    elif type == 'LimitScale':
        return CLimitScaleConstraint(flags, inf, data)
    elif type == 'Transform':
        return CTransformConstraint(flags, inf, data)
    elif type == 'LockedTrack':
        return CLockedTrackConstraint(flags, inf, data)
    elif type == 'DampedTrack':
        return CDampedTrackConstraint(flags, inf, data)
    elif type == 'StretchTo':
        return CStretchToConstraint(flags, inf, data)
    elif type == 'TrackTo':
        return CTrackToConstraint(flags, inf, data)
    elif type == 'LimitDist':
        return CLimitDistConstraint(flags, inf, data)
    elif type == 'ChildOf':
        return CChildOfConstraint(flags, inf, data)
    elif type == 'SplineIK':
        return CSplineIkConstraint(flags, inf, data)
    elif type == 'Floor':
        return CFloorConstraint(flags, inf, data)
    else:
        log.message("%s", label)
        log.message("%s", type)
        raise NameError("Unknown constraint type %s" % type)




