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

Pose
"""

import math
import log
from collections import OrderedDict

import numpy as np
import numpy.linalg as la
import transformations as tm
import numpy as np

from .flags import *
from .armature import Armature
from .parser import Parser
from .options import ArmatureOptions
from .utils import *

#-------------------------------------------------------------------------------
#   Pose
#-------------------------------------------------------------------------------

class Pose:

    def __init__(self, human, options):
        self.human = human
        self.posebones = OrderedDict()
        self.modifier = None
        self.restPosition = False
        self.dirty = True
        self.frames = []
        self.controls = []
        self.deforms = []

        amt = self.armature = Armature("Armature", options)
        amt.parser = Parser(amt, human)
        debugCoords("Pose1")
        amt.setup()
        log.debug("Head %s" % amt.bones["head"].head)
        amt.normalizeVertexWeights(human)
        self.matrixGlobal = tm.identity_matrix()

        self.deforms = []
        for bone in amt.bones.values():
            pb = self.posebones[bone.name] = PoseBone(self, bone)
            pb.build()
            if pb.bone.deform:
                self.deforms.append(pb)

        self.storeCoords()
        nVerts = len(human.meshData.coord)
        self.restCoords = np.zeros((nVerts,4), float)
        self.restCoords[:,3] = 1
        self.syncRestVerts("rest")
        debugCoords("Pose2")


    def storeCoords(self):
        self._storedCoord = np.array(self.human.meshData.coord)


    def restoreCoords(self):
        self.human.meshData.coord = self._storedCoord


    def __repr__(self):
        return ("  <Pose %s>" % self.armature.name)


    def display(self):
        log.debug("<Pose %s", self.armature.name)
        for bone in self.posebones.values():
            bone.display()
        log.debug(">")


    def printLocs(self, words):
        return
        string = ""
        for word in words:
            string += ("%s " % word)
        log.debug("%s", string)
        coord = self.human.meshData.coord
        for vn in [3825]:
            x = coord[vn]
            y = self.restCoords[vn]
            log.debug("   %d (%.4f %.4f %.4f) (%.4f %.4f %.4f)", vn, x[0], x[1], x[2], y[0], y[1], y[2])


    def listPose(self):
        for pb in self.posebones.values():
            quat = tm.quaternion_from_matrix(pb.matrixPose)
            log.debug("  %s %s", pb.name, quat)


    def clear(self, update=False):
        log.message("Clear armature")
        for pb in self.posebones.values():
            pb.matrixPose = tm.identity_matrix()
        if update:
            halt
            self.update()
            self.removeModifier()


    def store(self):
        shadowBones = {}
        for pb in self.posebones.values():
            shadowBones[pb.name] = pb.matrixPose
            pb.matrixPose = tm.identity_matrix()
        #self.listPose()
        return shadowBones


    def restore(self, shadowBones):
        for pb in self.bones.values():
            pb.matrixPose = shadowBones[pb.name]
        #self.listPose()


    def adapt(self):
        shadowBones = self.store()
        self.syncRestVerts("adapt")
        self.restore(shadowBones)
        self.update()


    def syncRestVerts(self, caller):
        log.message("Sync rest verts: %s", caller)
        self.restCoords[:,:3] = self._storedCoord


    def removeModifier(self):
        if self.modifier:
            self.modifier.updateValue(self.human, 0.0)
            self.modifier = None
            self.human.meshData.update()
            self.syncRestVerts("removeModifier")
            self.printLocs(["Remove", self.modifier])


    def updateModifier(self):
        if self.modifier:
            self.modifier.updateValue(self.human, 1.0)
            self.human.meshData.update()
            self.syncRestVerts("updateModifier")
            self.printLocs(["Update", self.modifier])


    def setModifier(self, modifier):
        self.removeModifier()
        self.modifier = modifier
        if modifier:
            modifier.updateValue(self.human, 1.0)
        self.syncRestVerts("setModifier")
        self.printLocs(["setModifier", self.modifier])


    def update(self):
        human = self.human
        obj = human.meshData
        self.printLocs(["Update", self])

        for pb in self.posebones.values():
            pb.updateBone()
            pb.updateConstraints()
        self.printLocs(["Bones updated"])

        self.updateObj()
        self.printLocs(["Updated", human])

        if human.proxy:
            human.updateProxyMesh()

        for proxy,obj in human.getProxiesAndObjects():
            mesh = obj.getSeedMesh()
            proxy.update(mesh)
            mesh.update()
            if obj.isSubdivided():
                obj.getSubdivisionMesh()


    def updateObj(self):
        obj = self.human.meshData
        nVerts = len(obj.coord)
        amt = self.armature
        coords = np.zeros((nVerts,4), float)
        for pb in self.deforms:
            try:
                verts,weights = amt.vertexWeights[pb.name]
            except KeyError:
                continue
            vec = np.dot(pb.matrixVerts, self.restCoords[verts].transpose())
            wvec = weights*vec
            coords[verts] += wvec.transpose()
        obj.changeCoords(coords[:,:3])
        obj.calcNormals()
        obj.update()


    def checkDirty(self):
        dirty = False
        for pb in self.bones.values():
            pb.dirty = False

        for pb in self.bones.values():
            pb.dirty = True
            for cns in pb.constraints:
                bnames = []
                try:
                    bnames.append( cns.subtar )
                except AttributeError:
                    pass
                try:
                    bnames.append( cns.ptar )
                except AttributeError:
                    pass
                for bname in bnames:
                    if bname:
                        target = self.bones[bname]
                        if not target.dirty:
                            log.debug("Dirty %s before %s" % (pb.name, target.name))
                            dirty = True
        if dirty:
            raise NameError("Dirty bones encountered")


    def readMhpFile(self, filepath):
        log.message("Loading MHP file %s", filepath)
        amt = self.armature
        fp = open(filepath, "rU")
        bname = None
        mat = np.identity(4, float)
        for line in fp:
            words = line.split()
            if len(words) < 4:
                continue
            if words[0] != bname:
                self.setMatrixPose(bname, mat)
                bname = words[0]
                mat = np.identity(4, float)
            if words[1] in ["quat", "gquat"]:
                quat = float(words[2]),float(words[3]),float(words[4]),float(words[5])
                mat = tm.quaternion_matrix(quat)
                if words[1] == "gquat":
                    pb = self.posebones[words[0]]
                    mat = np.dot(la.inv(pb.bone.matrixRelative), mat)
            elif words[1] == "scale":
                scale = 1+float(words[2]), 1+float(words[3]), 1+float(words[4])
                smat = tm.compose_matrix(scale=scale)
                mat = np.dot(smat, mat)
            elif words[1] == "matrix":
                rows = []
                n = 2
                for i in range(4):
                    rows.append((float(words[n]), float(words[n+1]), float(words[n+2]), float(words[n+3])))
                    n += 4
                mat = np.array(rows)
        self.setMatrixPose(bname, mat)
        fp.close()
        self.update()


    def setMatrixPose(self, bname, mat):
        if bname:
            pb = self.posebones[bname]
            pb.matrixPose[:,:3] = mat[:,:3]


    def readBvhFile(self, filepath):
        log.message("Bvh %s", filepath)
        amt = self.armature
        fp = open(filepath, "rU")
        bones = []
        motion = False
        frames = []
        for line in fp:
            words = line.split()
            if len(words) < 1:
                continue
            if motion:
                frame = []
                for word in words:
                    frame.append(float(word))
                frames.append(frame)
            elif words[0] == "ROOT":
                joint = words[1]
                isRoot = True
            elif words[0] == "JOINT":
                try:
                    pb = self.posebones[joint]
                except KeyError:
                    pb = None
                if not pb:
                    raise NameError("Missing pb: %s" % joint)
                data = (pb, offset, channels, isRoot)
                bones.append(data)
                joint = words[1]
                isRoot = False
            elif words[0] == "OFFSET":
                if isRoot:
                    offset = (float(words[1]), float(words[2]), float(words[3]))
                else:
                    offset = (0,0,0)
            elif words[0] == "CHANNELS":
                nchannels = int(words[1])
                channels = words[2:]
            elif words[0] == "Frame":
                try:
                    pb = self.posebones[joint]
                except KeyError:
                    pb = None
                data = (pb, offset, channels, isRoot)
                bones.append(data)
                motion = True
        fp.close()

        frame = frames[0]
        for pb, offset, channels, isRoot in bones:
            order = ""
            angles = []
            for channel in channels:
                value = frame[0]
                if channel == "Xposition":
                    rx = value
                elif channel == "Yposition":
                    ry = value
                elif channel == "Zposition":
                    rz = value
                elif channel == "Xrotation":
                    ax = value*D
                    order = "x" + order
                    angles.append(ax)
                elif channel == "Yrotation":
                    ay = -value*D
                    order = "z" + order
                    angles.append(ay)
                elif channel == "Zrotation":
                    az = value*D
                    order = "y" + order
                    angles.append(az)
                frame = frame[1:]
            if pb:
                ak,aj,ai = angles
                order = "s" + order
                mat1 = tm.euler_matrix(ai, aj, ak, axes=order)
                mat2 = np.dot(np.dot(la.inv(pb.bone.matrixRest), mat1), pb.bone.matrixRest)
                pb.matrixPose[:3,:3] = mat2[:3,:3]
                if isRoot and False:
                    pb.matrixPose[0,3] = rx
                    pb.matrixPose[1,3] = ry
                    pb.matrixPose[2,3] = rz

            if pb.name in []:
                log.debug("%s %s", pb.name, order)
                log.debug("%s", str(channels))
                log.debug("%s %s %s", ax/D, ay/D, az/D)
                log.debug("R %s", pb.bone.matrixRest)
                log.debug("M1 %s", mat1)
                log.debug("M2 %s", mat2)
                log.debug("P %s", pb.matrixPose)
                log.debug("G %s", pb.matrixGlobal)

        self.update()

#-------------------------------------------------------------------------------
#   PoseBone
#-------------------------------------------------------------------------------

class PoseBone:
    def __init__(self, pose, bone):
        self.pose = pose
        self.bone = bone
        self.name = bone.name
        if self.bone.parent:
            self.parent = pose.posebones[self.bone.parent]
        else:
            self.parent = None
        self.dirty = False
        self.head4 = None
        self.tail4 = None
        self.yvector4 = None
        self.matrixPose = None
        self.matrixGlobal = None
        self.matrixVerts = None
        self.constraints = bone.constraints


    def __repr__(self):
        return ("  <PoseBone %s>" % self.name)


    def build(self):
        self.matrixPose = tm.identity_matrix()
        x,y,z = self.bone.head
        self.head4 = np.array((x,y,z,1.0))
        x,y,z = self.bone.tail
        self.tail4 = np.array((x,y,z,1.0))
        self.vector4 = self.tail4 - self.head4
        self.yvector4 = np.array((0, self.bone.length, 0, 1))

        self.bone.calcRestMatrix()
        if self.parent:
            self.matrixGlobal = np.dot(self.parent.matrixGlobal, self.bone.matrixRelative)
        else:
            self.matrixGlobal = self.bone.matrixRest
        try:
            self.matrixVerts = np.dot(self.matrixGlobal, la.inv(self.bone.matrixRest))
        except:
            log.debug("%s\n  %s\n  %s", self.name, self.head4, self.tail4)
            log.debug("%s", self.bone.matrixRest)
            log.debug("%s", self.matrixPose)
            log.debug("%s", self.matrixGlobal)
            halt

        #if self.name == "head":
        #    log.debug("Build matrices:\n%s\n%s" % (self.bone.matrixRest, self.matrixVerts))

    def getHead(self):
        return self.matrixGlobal[:3,3]


    def getTail(self):
        return np.dot(self.matrixGlobal, self.yvector4)[:3]


    def quatAngles(self, quat):
        qw = quat[0]
        if abs(qw) < 1e-4:
            return (0,0,0)
        else:
            return ( 2*math.atan(quat[1]/qw),
                     2*math.atan(quat[2]/qw),
                     2*math.atan(quat[3]/qw)
                   )


    def zeroTransformation(self):
        self.matrixPose = np.identity(4, float)


    def setRotationIndex(self, index, angle, useQuat):
        if useQuat:
            quat = tm.quaternion_from_matrix(self.matrixPose)
            log.debug("%s", str(quat))
            quat[index] = angle/1000
            log.debug("%s", str(quat))
            normalizeQuaternion(quat)
            log.debug("%s", str(quat))
            self.matrixPose = tm.quaternion_matrix(quat)
            return quat[0]*1000
        else:
            angle = angle*D
            ax,ay,az = tm.euler_from_matrix(self.matrixPose, axes='sxyz')
            if index == 1:
                ax = angle
            elif index == 2:
                ay = angle
            elif index == 3:
                az = angle
            mat = tm.euler_matrix(ax, ay, az, axes='sxyz')
            self.matrixPose[:3,:3] = mat[:3,:3]
            return 1000.0


    Axes = [
        np.array((1,0,0)),
        np.array((0,1,0)),
        np.array((0,0,1))
    ]

    def rotate(self, angle, axis, rotWorld):
        mat = tm.rotation_matrix(angle*D, CBone.Axes[axis])
        if rotWorld:
            mat = np.dot(mat, self.matrixGlobal)
            self.matrixGlobal[:3,:3] = mat[:3,:3]
            self.matrixPose = self.getPoseFromGlobal()
        else:
            mat = np.dot(mat, self.matrixPose)
            self.matrixPose[:3,:3] = mat[:3,:3]


    def stretchTo(self, goal, doStretch):
        length, self.matrixGlobal = getMatrix(self.getHead(), goal, 0)
        if doStretch:
            factor = length/self.length
            self.matrixGlobal[:3,1] *= factor
        pose = self.getPoseFromGlobal()

        if 0 and self.name in ["DfmKneeBack_L", "DfmLoLeg_L"]:
            log.debug("Stretch %s", self.name)
            log.debug("G %s", goal)
            log.debug("M1 %s", self.matrixGlobal)
            log.debug("P1 %s", pose)

        az,ay,ax = tm.euler_from_matrix(pose, axes='szyx')
        rot = tm.rotation_matrix(-ay + self.roll, CBone.Axes[1])
        self.matrixGlobal[:3,:3] = np.dot(self.matrixGlobal[:3,:3], rot[:3,:3])
        pose2 = self.getPoseFromGlobal()

        if 0 and self.name in ["DfmKneeBack_L", "DfmLoLeg_L"]:
            log.debug("A %s %s %s", ax, ay, az)
            log.debug("R %s", rot)
            log.debug("M2 %s", self.matrixGlobal)
            log.debug("P2 %s", pose)
            log.debug("")


    def poleTargetCorrect(self, head, goal, pole, angle):
        yvec = goal-head
        xvec = pole-head
        xy = np.dot(xvec, yvec)/np.dot(yvec,yvec)
        xvec = xvec - xy * yvec
        xlen = math.sqrt(np.dot(xvec,xvec))
        if xlen > 1e-6:
            xvec = xvec / xlen
            zvec = self.matrixGlobal[:3,2]
            zlen = math.sqrt(np.dot(zvec,zvec))
            zvec = zvec / zlen
            angle0 = math.asin( np.dot(xvec,zvec) )
            rot = tm.rotation_matrix(angle - angle0, CBone.Axes[1])
            #m0 = self.matrixGlobal.copy()
            self.matrixGlobal[:3,:3] = np.dot(self.matrixGlobal[:3,:3], rot[:3,:3])

            if 0 and self.name == "DfmUpArm2_L":
                log.debug("")
                log.debug("IK %s", self.name)
                log.debug("X %s", xvec)
                log.debug("Y %s", yvec)
                log.debug("Z %s", zvec)
                log.debug("A0 %s", angle0)
                log.debug("A %s", angle)
                log.debug("R %s", rot)
                log.debug("M0 %s", m0)
                log.debug("M %s", self.matrixGlobal)


    def getPoseFromGlobal(self):
        if self.parent:
            return np.dot(la.inv(self.bone.matrixRelative), np.dot(la.inv(self.parent.matrixGlobal), self.matrixGlobal))
        else:
            return np.dot(la.inv(self.bone.matrixRelative), self.matrixGlobal)


    def setRotation(self, angles):
        ax,ay,az = angles
        mat = tm.euler_matrix(ax, ay, az, axes='szyx')
        self.matrixPose[:3,:3] = mat[:3,:3]


    def getRotation(self):
        qw,qx,qy,qz = tm.quaternion_from_matrix(self.matrixPose)
        ax,ay,az = tm.euler_from_matrix(self.matrixPose, axes='sxyz')
        return (1000*qw,1000*qx,1000*qy,1000*qz, ax/D,ay/D,az/D)


    def getPoseQuaternion(self):
        return tm.quaternion_from_matrix(self.matrixPose)

    def setPoseQuaternion(self, quat):
        self.matrixPose = tm.quaternion_matrix(quat)


    def updateBone(self):
        if self.parent:
            self.matrixGlobal = np.dot(self.parent.matrixGlobal, np.dot(self.bone.matrixRelative, self.matrixPose))
        else:
            self.matrixGlobal = np.dot(self.bone.matrixRelative, self.matrixPose)


    def updateConstraints(self):
        for cns in self.constraints:
            cns.update(self.amtInfo, self)
        self.matrixVerts = np.dot(self.matrixGlobal, la.inv(self.bone.matrixRest))



    #
    #   Prisms
    #

    PrismVectors = {
        'Prism': [
            np.array((0, 0, 0, 0)),
            np.array((0.14, 0.25, 0, 0)),
            np.array((0, 0.25, 0.14, 0)),
            np.array((-0.14, 0.25, 0, 0)),
            np.array((0, 0.25, -0.14, 0)),
            np.array((0, 1, 0, 0)),
        ],
        'Box' : [
            np.array((-0.10, 0, -0.10, 0)),
            np.array((-0.10, 0, 0.10, 0)),
            np.array((-0.10, 1, -0.10, 0)),
            np.array((-0.10, 1, 0.10, 0)),
            np.array((0.10, 0, -0.10, 0)),
            np.array((0.10, 0, 0.10, 0)),
            np.array((0.10, 1, -0.10, 0)),
            np.array((0.10, 1, 0.10, 0)),
        ],
        'Cube' : [
            np.array((-1, 0, -1, 0)),
            np.array((-1, 0, 1, 0)),
            np.array((-1, 1, -1, 0)),
            np.array((-1, 1, 1, 0)),
            np.array((1, 0, -1, 0)),
            np.array((1, 0, 1, 0)),
            np.array((1, 1, -1, 0)),
            np.array((1, 1, 1, 0)),
        ],
        'Line' : [
            np.array((-0.03, 0, -0.03, 0)),
            np.array((-0.03, 0, 0.03, 0)),
            np.array((-0.03, 1, -0.03, 0)),
            np.array((-0.03, 1, 0.03, 0)),
            np.array((0.03, 0, -0.03, 0)),
            np.array((0.03, 0, 0.03, 0)),
            np.array((0.03, 1, -0.03, 0)),
            np.array((0.03, 1, 0.03, 0)),
        ]
    }

    PrismFaces = {
        'Prism': [ (0,1,4,0), (0,4,3,0), (0,3,2,0), (0,2,1,0),
                   (5,4,1,5), (5,1,2,5), (5,2,3,5), (5,3,4,5) ],
        'Box' : [ (0,1,3,2), (4,6,7,5), (0,2,6,4),
                   (1,5,7,3), (1,0,4,5), (2,3,7,6) ],
        'Line' : [ (0,1,3,2), (4,6,7,5), (0,2,6,4),
                   (1,5,7,3), (1,0,4,5), (2,3,7,6) ],
    }

    HeadVec = np.array((0,0,0,1))

    def prismPoints(self, type):
        if self.amtInfo.restPosition:
            mat = self.bone.matrixRest
            length = self.length
            self.matrixGlobal = mat
            self.yvector4[1] = length
        else:
            mat = self.matrixGlobal
            length = self.yvector4[1]
        vectors = CBone.PrismVectors[type]
        points = []
        for vec in vectors:
            p = np.dot(mat, (vec*length + CBone.HeadVec))
            points.append(p[:3])
        return points, CBone.PrismFaces[type]

    #
    #   Display
    #

    def display(self):
        log.debug("  <CBone %s", self.name)
        log.debug("    head: (%.4g %.4g %.4g)", self.head[0], self.head[1], self.head[2])
        log.debug("    tail: (%.4g %.4g %.4g)", self.tail[0], self.tail[1], self.tail[2])
        log.debug("    roll: %s", self.roll)
        log.debug("    parent: %s", self.parent)
        log.debug("    conn: %s", self.conn)
        log.debug("    deform: %s", self.deform)

        log.debug("    constraints: [")
        for cns in self.constraints:
            cns.display()
        log.debug("    ]")
        log.debug("    drivers: [")
        for drv in self.drivers:
            drv.display()
        log.debug("    ]")
        log.debug("  >")


    def printMats(self):
        log.debug(self.name)
        log.debug("H4 %s", self.head4)
        log.debug("T4 %s", self.tail4)
        log.debug("RM %s", self.bone.matrixRest)
        log.debug("RV %s", np.dot(self.bone.matrixRest, self.yvector4))
        log.debug("P %s", self.matrixPose)
        log.debug("Rel %s", self.bone.matrixRelative)
        log.debug("G %s", self.matrixGlobal)
        log.debug("GV %s", np.dot(self.matrixGlobal, self.yvector4))

#
#
#


def createPoseRig(human):
    options = ArmatureOptions()
    options.useMuscles = True
    options.addConnectingBones = True
    amt = Pose(human, options)
    return amt


