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

TODO
"""

import log
import armature
from armature.flags import *


def writePoseBone(fp, amt, bone, customShape, boneGroup, locArg, lockRot, lockScale, ik_dof, poseFlags, constraints):
    try:
        (lockLoc, location) = locArg
    except:
        lockLoc = locArg
        location = (0,0,0)

    (locX, locY, locZ) = location
    (lockLocX, lockLocY, lockLocZ) = lockLoc
    (lockRotX, lockRotY, lockRotZ) = lockRot
    (lockScaleX, lockScaleY, lockScaleZ) = lockScale

    ikLin = (poseFlags & P_IKLIN != 0)
    ikRot = (poseFlags & P_IKROT != 0)
    lkRot4 = (poseFlags & P_LKROT4 != 0)
    lkRotW = (poseFlags & P_LKROTW != 0)
    hide = (poseFlags & P_HID != 0)

    if not fp:
        #amt.createdArmature.bones[bone].constraints = mhx_constraints.getConstraints(bone, constraints, lockLoc, lockRot)
        return

    fp.write("\n  Posebone %s %s \n" % (bone, True))

    if boneGroup:
        #index = boneGroupIndex(boneGroup, amt)
        fp.write("    bone_group Refer BoneGroup %s ;\n" % boneGroup)

    uses = (0,0,0)
    mins = (-pi, -pi, -pi)
    maxs = (pi, pi, pi)
    for cns in amt.bones[bone].constraints:
        cns.writeMhx(amt, fp)


    ik_stretch = None
    ik_stiff = None
    ik_lim = None
    try:
        (ik_dof_x, ik_dof_y, ik_dof_z) = ik_dof
    except:
        (ik_dof1, ik_stiff, ik_stretch, ik_lim) = ik_dof
        (ik_dof_x, ik_dof_y, ik_dof_z) = ik_dof1

    fp.write(
"    lock_ik_x %d ;\n" % (1-ik_dof_x) +
"    lock_ik_y %d ;\n" % (1-ik_dof_y) +
"    lock_ik_z %d ;\n" % (1-ik_dof_z))


    if ik_lim:
        (xmin,xmax, ymin,ymax, zmin,zmax) = ik_lim
        fp.write(
"    use_ik_limit_x True ;\n" +
"    use_ik_limit_y True ;\n" +
"    use_ik_limit_z True ;\n" +
"    ik_max Array %.4f %.4f %.4f ; \n" % (xmax, ymax, zmax) +
"    ik_min Array %.4f %.4f %.4f ; \n" % (xmin, ymin, zmin))

    if ik_stiff:
        (ik_stiff_x, ik_stiff_y, ik_stiff_z) = ik_stiff
        fp.write("    ik_stiffness  Array %.4f %.4f %.4f ;\n" % (ik_stiff_x, ik_stiff_y, ik_stiff_z))
    else:
        fp.write("    ik_stiffness Array 0.0 0.0 0.0  ; \n")

    if customShape:
        fp.write("    custom_shape Refer Object %s ; \n" % customShape)

    rotMode = getRotationMode(poseFlags, amt.options)
    fp.write("    rotation_mode '%s' ;\n" % rotMode)

    fp.write(
"    use_ik_linear_control %s ; \n" % ikLin +
"    ik_linear_weight 0 ; \n"+
"    use_ik_rotation_control %s ; \n" % ikRot +
"    ik_rotation_weight 0 ; \n" +
"    hide %s ; \n" % hide)

    if ik_stretch:
        fp.write("    ik_stretch %.3f ; \n" % ik_stretch)
    else:
        fp.write("    ik_stretch 0 ; \n")

    fp.write(
"    location Array %.3f %.3f %.3f ; \n" % (locX, locY, locZ) +
"    lock_location Array %d %d %d ;\n"  % (lockLocX, lockLocY, lockLocZ)+
"    lock_rotation Array %d %d %d ;\n"  % (lockRotX, lockRotY, lockRotZ) +
"    lock_rotation_w %s ; \n" % lkRotW +
"    lock_rotations_4d %s ; \n" % False +
"    lock_scale Array %d %d %d  ; \n" % (lockScaleX, lockScaleY, lockScaleZ)+
"  end Posebone \n")
    return


def getRotationMode(poseFlags, options):
    if options.useQuaternionsOnly:
        return 'QUATERNION'
    else:
        modes = ['QUATERNION', 'XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']
        return modes[(poseFlags&P_ROTMODE) >> 8]

