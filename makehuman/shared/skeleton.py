#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

General skeleton, rig or armature class.
A skeleton is a hierarchic structure of bones, defined between a head and tail
joint position. Bones can be detached from each other (their head joint doesn't
necessarily need to be at the same position as the tail joint of their parent
bone).

A pose can be applied to the skeleton by setting a pose matrix for each of the
bones, allowing static posing or animation playback.
The skeleton supports skinning of a mesh using a list of vertex-to-bone
assignments.
"""

import math
from math import pi

import numpy as np
import numpy.linalg as la
import transformations as tm
import matrix

import log

D = pi/180


class Skeleton(object):

    def __init__(self, name="Skeleton"):
        self.name = name

        self.origin = np.zeros(3, dtype=np.float32)   # TODO actually use origin somewhere?

        self.bones = {}     # Bone lookup list by name
        self.boneslist = []  # Breadth-first ordered list of all bones
        self.roots = []     # Root bones of this skeleton, a skeleton can have multiple root bones.

    def __repr__(self):
        return ("  <Skeleton %s>" % self.name)

    def display(self):
        log.debug("<Skeleton %s", self.name)
        for bone in self.getBones():
            bone.display()
        log.debug(">")

    def canonalizeBoneNames(self):
        newBones = {}
        for bName, bone in self.bones.items():
            canonicalName = bName.lower().replace(' ','_').replace('-','_')
            bone.name = canonicalName
            newBones[bone.name] = bone
        self.bones = newBones

    def fromOptions(self, options, mesh):
        """
        Create armature from option set.
        Convert to skeleton.
        TODO: Merge Armature and Skeleton classes one day.
        """

        from armature.armature import setupArmature
        from core import G

        amt = setupArmature("python", G.app.selectedHuman, options)
        for bone in amt.bones.values():
            self.addBone(bone.name, bone.parent, bone.head, bone.tail, bone.roll)

        self.build()

        # Normalize weights and put them in np format
        boneWeights = {}
        wtot = np.zeros(mesh.getVertexCount(), np.float32)
        for vgroup in amt.vertexWeights.values():
            for vn,w in vgroup:
                wtot[vn] += w

        for bname,vgroup in amt.vertexWeights.items():
            weights = np.zeros(len(vgroup), np.float32)
            verts = []
            n = 0
            for vn,w in vgroup:
                verts.append(vn)
                weights[n] = w/wtot[vn]
                n += 1
            boneWeights[bname] = (verts, weights)

        # Assign unweighted vertices to root bone with weight 1
        rootBone = self.roots[0].name
        informed = False
        if rootBone not in boneWeights.keys():
            boneWeights[rootBone] = ([], [])
        else:
            vs,ws = boneWeights[rootBone]
            boneWeights[rootBone] = (list(vs), list(ws))
        vs,ws = boneWeights[rootBone]
        for vIdx, wCount in enumerate(wtot):
            if wCount == 0:
                vs.append(vIdx)
                ws.append(1.0)
                if not informed:
                    log.debug("Adding trivial bone weights to bone %s for unweighted vertices.", rootBone)
                    informed = True
        boneWeights[rootBone] = (vs, np.asarray(ws, dtype=np.float32))

        return boneWeights

    def addBone(self, name, parentName, head, tail, roll=0):
        if name in self.bones.keys():
            raise RuntimeError("The skeleton %s already contains a bone named %s." % (self.__repr__(), name))
        bone = Bone(self, name, parentName, head, tail, roll)
        self.bones[name] = bone
        if not parentName:
            self.roots.append(bone)

    def build(self):
        self.__cacheGetBones()
        for bone in self.getBones():
            bone.build()

    def update(self):
        for bone in self.getBones():
            bone.update()

    def getBoneCount(self):
        return len(self.getBones())

    def getPose(self):
        """
        Retrieves the current pose of this skeleton as a list of pose matrices,
        one matrix per bone, bones in breadth-first order (same order as
        getBones()).

        returns     np.array((nBones, 4, 4), dtype=float32)
        """
        nBones = self.getBoneCount()
        poseMats = np.zeros((nBones,4,4),dtype=np.float32)

        for bIdx, bone in enumerate(self.getBones()):    # TODO eliminate loop?
            poseMats[bIdx] = bone.matPose

        return poseMats

    def setPose(self, poseMats):
        """
        Set pose of this skeleton as a list of pose matrices, one matrix per
        bone with bones in breadth-first order (same order as getBones()).

        poseMats    np.array((nBones, 4, 4), dtype=float32)
        """
        for bIdx, bone in enumerate(self.getBones()):
            bone.matPose = np.identity(4, dtype=np.float32)

            # Calculate rotations
            bone.matPose[:3,:3] = poseMats[bIdx,:3,:3]
            invRest = la.inv(bone.matRestGlobal)
            bone.matPose = np.dot(np.dot(invRest, bone.matPose), bone.matRestGlobal)

            # Add translations from original
            bone.matPose[:3,3] = poseMats[bIdx,:3,3]
        # TODO avoid this loop, eg by storing a pre-allocated poseMats np array in skeleton and keeping a reference to a sub-array in each bone. It would allow batch processing of all pose matrices in one np call
        self.update()

    def isInRestPose(self):
        for bone in self.getBones():
            if not bone.isInRestPose():
                return False
        return True

    def setToRestPose(self):
        for bone in self.getBones():
            bone.setToRestPose()

    def skinMesh(self, meshCoords, vertBoneMapping):
        """
        Update (pose) assigned mesh using linear blend skinning.
        """
        nVerts = len(meshCoords)
        coords = np.zeros((nVerts,4), float)
        for bname, mapping in vertBoneMapping.items():
            bone = self.getBone(bname)
            verts,weights = mapping
            vec = np.dot(bone.matPoseVerts, meshCoords[verts].transpose())
            wvec = weights*vec
            coords[verts] += wvec.transpose()

        return coords

    def getBones(self):
        """
        Returns linear list of all bones in breadth-first order.
        """
        return self.boneslist

    def __cacheGetBones(self):
        from Queue import deque

        result = []
        queue = deque(self.roots)
        while len(queue) > 0:
            bone = queue.popleft()
            bone.index = len(result)
            result.append(bone)
            queue.extend(bone.children)
        self.boneslist = result

    def getJointNames(self):
        """
        Returns a list of all joints defining the bone positions (minus end
        effectors for leaf bones). The names are the same as the corresponding
        bones in this skeleton.
        List is in depth-first order (usually the order of joints in a BVH file)
        """
        return self._retrieveJointNames(self.roots[0])

    def _retrieveJointNames(self, parentBone):
        result = [parentBone.name]
        for child in parentBone.children:
            result.extend(self._retrieveJointNames(child))
        return result

    def getBone(self, name):
        return self.bones[name]

    def containsBone(self, name):
        return name in self.bones.keys()

    def getBoneToIdxMapping(self):
        result = {}
        boneNames = [ bone.name for bone in self.getBones() ]
        for idx, name in enumerate(boneNames):
            result[name] = idx
        return result

    def loadPoseFromMhpFile(self, filepath):
        """
        Load a MHP pose file that contains a static pose. Posing data is defined
        with quaternions to indicate rotation angles.
        Sets current pose to
        """
        log.message("Mhp %s", filepath)
        fp = open(filepath, "rU")

        boneMap = self.getBoneToIdxMapping()
        nBones = len(boneMap.keys())
        poseMats = np.zeros((nBones,4,4),dtype=np.float32)
        poseMats[:] = np.identity(4, dtype=np.float32)

        for line in fp:
            words = line.split()
            if len(words) < 5:
                continue
            elif words[1] in ["quat", "gquat"]:
                boneIdx = boneMap[words[0]]
                quat = float(words[2]),float(words[3]),float(words[4]),float(words[5])
                mat = tm.quaternion_matrix(quat)
                if words[1] == "gquat":
                    bone = self.bones[boneIdx]
                    mat = np.dot(la.inv(bone.matRestRelative), mat)
                poseMats[boneIdx] = mat[:3,:3]

        fp.close()
        self.setPose(poseMats)

    def compare(self, other):
        pass
        # TODO compare two skeletons (structure only)


class Bone(object):

    def __init__(self, skel, name, parentName, headPos, tailPos, roll=0):
        """
        Construct a new bone for specified skeleton.
        headPos and tailPos should be in world space coordinates (relative to root).
        parentName should be None for a root bone.
        """
        self.name = name
        self.skeleton = skel

        self.headPos = np.zeros(3,dtype=np.float32)
        self.headPos[:] = headPos[:3]
        self.tailPos = np.zeros(3,dtype=np.float32)
        self.tailPos[:] = tailPos[:3]

        self.roll = float(roll)
        self.length = 0
        self.yvector4 = None    # Direction vector of this bone

        self.children = []
        if parentName:
            self.parent = skel.getBone(parentName)
            self.parent.children.append(self)
        else:
            self.parent = None

        self.index = None   # The index of this bone in the breadth-first bone list

        # Matrices:
        # static
        #  matRestGlobal:     4x4 rest matrix, relative world
        #  matRestRelative:   4x4 rest matrix, relative parent
        # posed
        #  matPose:           4x4 pose matrix, relative parent and own rest pose
        #  matPoseGlobal:     4x4 matrix, relative world
        #  matPoseVerts:      4x4 matrix, relative world and own rest pose

        self.matRestGlobal = None
        self.matRestRelative = None
        self.matPose = None
        self.matPoseGlobal = None
        self.matPoseVerts = None

    def __repr__(self):
        return ("  <Bone %s>" % self.name)

    def build(self):
        """
        Set matPoseVerts, matPoseGlobal and matRestRelative... TODO
        needs to happen after changing skeleton structure
        """
        # Set pose matrix to rest pose
        self.matPose = np.identity(4, np.float32)

        self.head3 = np.array(self.headPos[:3], dtype=np.float32)
        self.head4 = np.append(self.head3, 1.0)

        self.tail3 = np.array(self.tailPos[:3], dtype=np.float32)
        self.tail4 = np.append(self.head3, 1.0)

        # Update rest matrices
        self.length, self.matRestGlobal = getMatrix(self.head3, self.tail3, self.roll)
        if self.parent:
            self.matRestRelative = np.dot(la.inv(self.parent.matRestGlobal), self.matRestGlobal)
        else:
            self.matRestRelative = self.matRestGlobal

        self.vector4 = self.tail4 - self.head4
        self.yvector4 = np.array((0, self.length, 0, 1))

        # Update pose matrices
        self.update()

    def update(self):
        """
        Recalculate global pose matrix ... TODO
        Needs to happen after setting pose matrix
        Should be called after changing pose (matPose)
        """
        if self.parent:
            self.matPoseGlobal = np.dot(self.parent.matPoseGlobal, np.dot(self.matRestRelative, self.matPose))
        else:
            self.matPoseGlobal = np.dot(self.matRestRelative, self.matPose)

        try:
            self.matPoseVerts = np.dot(self.matPoseGlobal, la.inv(self.matRestGlobal))
        except:
            log.debug("Cannot calculate pose verts matrix for bone %s %s %s", self.name, self.getRestHeadPos(), self.getRestTailPos())
            log.debug("Non-singular rest matrix %s", self.matRestGlobal)

    def getHead(self):
        """
        The head position of this bone in world space.
        """
        return self.matPoseGlobal[:3,3].copy()

    def getTail(self):
        """
        The tail position of this bone in world space.
        """
        tail4 = np.dot(self.matPoseGlobal, self.yvector4)
        return tail4[:3].copy()

    def getLength(self):
        return self.yvector4[1]

    def getRestHeadPos(self):
        return self.headPos.copy()

    def getRestTailPos(self):
        return self.tailPos.copy()

    def getRestOffset(self):
        if self.parent:
            return self.getRestHeadPos() - self.parent.getRestHeadPos()
        else:
            return self.getRestHeadPos()

    def getRestDirection(self):
        return matrix.normalize(self.getRestOffset())

    def getRestOrientationQuat(self):
        return tm.quaternion_from_matrix(self.matRestGlobal)

    def getRoll(self):
        """
        The roll angle of this bone. (in rest)
        """
        R = self.matRestGlobal
        qy = R[0,2] - R[2,0];
        qw = R[0,0] + R[1,1] + R[2,2] + 1;

        if qw < 1e-4:
            roll = pi
        else:
            roll = 2*math.atan2(qy, qw);
        return roll

    def getName(self):
        return self.name

    def hasParent(self):
        return self.parent != None

    def isRoot(self):
        return not self.hasParent()

    def hasChildren(self):
        return len(self.children) > 0

    def setToRestPose(self):   # used to be zeroTransformation()
        """
        Reset bone pose matrix to default (identity).
        """
        self.matPose = np.identity(4, np.float32)
        self.update()

    def isInRestPose(self):
        return (self.matPose == np.identity(4, np.float32)).all()

    def setRotationIndex(self, index, angle, useQuat):
        """
        Set the rotation for one of the three rotation channels, either as
        quaternion or euler matrix. index should be 1,2 or 3 and represents
        x, y and z axis accordingly
        """
        if useQuat:
            quat = tm.quaternion_from_matrix(self.matPose)
            log.debug("%s", str(quat))
            quat[index] = angle/1000
            log.debug("%s", str(quat))
            _normalizeQuaternion(quat)
            log.debug("%s", str(quat))
            self.matPose = tm.quaternion_matrix(quat)
            return quat[0]*1000
        else:
            angle = angle*D
            ax,ay,az = tm.euler_from_matrix(self.matPose, axes='sxyz')
            if index == 1:
                ax = angle
            elif index == 2:
                ay = angle
            elif index == 3:
                az = angle
            mat = tm.euler_matrix(ax, ay, az, axes='sxyz')
            self.matPose[:3,:3] = mat[:3,:3]
            return 1000.0

    Axes = [
        np.array((1,0,0)),
        np.array((0,1,0)),
        np.array((0,0,1))
    ]

    def rotate(self, angle, axis, rotWorld):
        """
        Rotate bone with specified angle around given axis.
        Set rotWorld to true to rotate in world space, else rotation happens in
        local coordinates.
        Axis should be 0, 1 or 2 for rotation around x, y or z axis.
        """
        mat = tm.rotation_matrix(angle*D, Bone.Axes[axis])
        if rotWorld:
            mat = np.dot(mat, self.matPoseGlobal)
            self.matPoseGlobal[:3,:3] = mat[:3,:3]
            self.matPose = self.getPoseFromGlobal()
        else:
            mat = np.dot(mat, self.matPose)
            self.matPose[:3,:3] = mat[:3,:3]

    def setRotation(self, angles):
        """
        Sets rotation of this bone (in local space) as Euler rotation
        angles x,y and z.
        """
        ax,ay,az = angles
        mat = tm.euler_matrix(ax, ay, az, axes='szyx')
        self.matPose[:3,:3] = mat[:3,:3]

    def getRotation(self):
        """
        Get rotation matrix of rotation of this bone in local space.
        """
        qw,qx,qy,qz = tm.quaternion_from_matrix(self.matPose)
        ax,ay,az = tm.euler_from_matrix(self.matPose, axes='sxyz')
        return (1000*qw,1000*qx,1000*qy,1000*qz, ax/D,ay/D,az/D)

    def getPoseQuaternion(self):
        """
        Get quaternion of orientation of this bone in local space.
        """
        return tm.quaternion_from_matrix(self.matPose)

    def setPoseQuaternion(self, quat):
        """
        Set orientation of this bone in local space as quaternion.
        """
        self.matPose = tm.quaternion_matrix(quat)

    def stretchTo(self, goal, doStretch):
        """
        Orient bone to point to goal position. Set doStretch to true to
        position the tail joint at goal, false to maintain length of this bone.
        """
        length, self.matPoseGlobal = getMatrix(self.getHead(), goal, 0)
        if doStretch:
            factor = length/self.length
            self.matPoseGlobal[:3,1] *= factor
        pose = self.getPoseFromGlobal()

        az,ay,ax = tm.euler_from_matrix(pose, axes='szyx')
        rot = tm.rotation_matrix(-ay + self.roll, Bone.Axes[1])
        self.matPoseGlobal[:3,:3] = np.dot(self.matPoseGlobal[:3,:3], rot[:3,:3])
        #pose2 = self.getPoseFromGlobal()

    ## TODO decouple this specific method from general armature?
    ## It is used by constraints.py and is related to IK
    ## TODO maybe place in an extra IK armature class or a separate module?
    def poleTargetCorrect(self, head, goal, pole, angle):
        """
        Resolve a pole target type of IK constraint.
        http://www.blender.org/development/release-logs/blender-246/inverse-kinematics/
        """
        yvec = goal-head
        xvec = pole-head
        xy = np.dot(xvec, yvec)/np.dot(yvec,yvec)
        xvec = xvec - xy * yvec
        xlen = math.sqrt(np.dot(xvec,xvec))
        if xlen > 1e-6:
            xvec = xvec / xlen
            zvec = self.matPoseGlobal[:3,2]
            zlen = math.sqrt(np.dot(zvec,zvec))
            zvec = zvec / zlen
            angle0 = math.asin( np.dot(xvec,zvec) )
            rot = tm.rotation_matrix(angle - angle0, Bone.Axes[1])
            self.matPoseGlobal[:3,:3] = np.dot(self.matPoseGlobal[:3,:3], rot[:3,:3])

    def getPoseFromGlobal(self):
        """
        Returns the pose matrix for this bone (relative to parent and rest pose)
        calculated from its global pose matrix.
        """
        if self.parent:
            return np.dot(la.inv(self.matRestRelative), np.dot(la.inv(self.parent.matPoseGlobal), self.matPoseGlobal))
        else:
            return np.dot(la.inv(self.matRestRelative), self.matPoseGlobal)


YZRotation = np.array(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
ZYRotation = np.array(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)))

def toZisUp3(vec):
    """
    Convert vector from MH coordinate system (y is up) to Blender coordinate
    system (z is up).
    """
    return np.dot(ZYRotation[:3,:3], vec)

def fromZisUp4(mat):
    """
    Convert matrix from Blender coordinate system (z is up) to MH coordinate
    system (y is up).
    """
    return np.dot(YZRotation, mat)

YUnit = np.array((0,1,0))

## TODO do y-z conversion inside this method or require caller to do it?
def getMatrix(head, tail, roll):
    """
    Calculate an orientation (rest) matrix for a bone between specified head
    and tail positions with given bone roll angle.
    Returns length of the bone and rest orientation matrix in global coordinates.
    """
    vector = toZisUp3(tail - head)
    length = math.sqrt(np.dot(vector, vector))
    if length == 0:
        vector = [0,0,1]
    else:
        vector = vector/length
    yproj = np.dot(vector, YUnit)

    if yproj > 1-1e-6:
        axis = YUnit
        angle = 0
    elif yproj < -1+1e-6:
        axis = YUnit
        angle = pi
    else:
        axis = np.cross(YUnit, vector)
        axis = axis / math.sqrt(np.dot(axis,axis))
        angle = math.acos(yproj)
    mat = tm.rotation_matrix(angle, axis)
    if roll:
        mat = np.dot(mat, tm.rotation_matrix(roll, YUnit))
    mat = fromZisUp4(mat)
    mat[:3,3] = head
    return length, mat

## TODO unused?  this is used by constraints.py, maybe should be moved there
def quatAngles(quat):
    """
    Convert a quaternion to euler angles.
    """
    qw = quat[0]
    if abs(qw) < 1e-4:
        return (0,0,0)
    else:
        return ( 2*math.atan(quat[1]/qw),
                 2*math.atan(quat[2]/qw),
                 2*math.atan(quat[3]/qw)
               )

def _normalizeQuaternion(quat):
    r2 = quat[1]*quat[1] + quat[2]*quat[2] + quat[3]*quat[3]
    if r2 > 1:
        r2 = 1
    if quat[0] >= 0:
        sign = 1
    else:
        sign = -1
    quat[0] = sign*math.sqrt(1-r2)

def getHumanJointPosition(mesh, jointName):
    """
    Get the position of a joint from the human mesh.
    This position is determined by the center of the joint helper with the
    specified name.
    """
    fg = mesh.getFaceGroup(jointName)
    verts = mesh.getCoords(mesh.getVerticesForGroups([fg.name]))
    return verts.mean(axis=0)

def loadRig(options, mesh):
    """
    Initializes a skeleton from an option set
    Returns the skeleton and vertex-to-bone weights.
    Weights are of format: {"boneName": [ (vertIdx, weight), ...], ...}
    """
    from armature.options import ArmatureOptions

    #rigName = os.path.splitext(os.path.basename(filename))[0]
    if not isinstance(options, ArmatureOptions):
        options = ArmatureOptions()
    skel = Skeleton("python")
    weights = skel.fromOptions(options, mesh)
    return skel, weights

def getProxyWeights(proxy, humanWeights, mesh):

    # Zip vertex indices and weights
    rawWeights = {}
    for (key, val) in humanWeights.items():
        indxs, weights = val
        rawWeights[key] = zip(indxs, weights)
    vertexWeights = proxy.getWeights(rawWeights)

    # Unzip and normalize weights (and put them in np format)
    boneWeights = {}
    wtot = np.zeros(mesh.getVertexCount(), np.float32)
    for vgroup in vertexWeights.values():
        for vn,w in vgroup:
            wtot[vn] += w

    for bname,vgroup in vertexWeights.items():
        weights = np.zeros(len(vgroup), np.float32)
        verts = []
        n = 0
        for vn,w in vgroup:
            verts.append(vn)
            weights[n] = w/wtot[vn]
            n += 1
        boneWeights[bname] = (verts, weights)

    return boneWeights

# TODO code replication is not nice...
def loadTargetMapping(rigName, skel):
    """
    Returns mapping of skeleton bones to reference rig bone names.
    Return format is a breadth-first ordered list with for each bone in the
    skeleton respectively a reference bone name. Entries can be None if no
    mapping to a bone exists.
    This reference rig to skeleton mapping assumes both rigs have the same rest
    pose.
    """
    import os

    path = os.path.join("tools/blender26x/mh_mocap_tool/target_rigs/", "%s.trg" % rigName)
    if not os.path.isfile(path):
        raise RuntimeError("File %s with skeleton rig mapping does not exist.", path)

    fp = open(path, "r")
    status = 0
    bones = []
    renames = {}
    ikbones = []
    for line in fp:
        words = line.split()
        if len(words) > 0:
            key = words[0].lower()
            if key[0] == "#":
                continue
            elif key == "name:":
                name = words[1]
            elif key == "bones:":
                status = 1
            elif key == "ikbones:":
                status = 2
            elif key == "renames:":
                status = 3
            elif len(words) != 2:
                log.debug("Ignored illegal line", line)
            elif status == 1:
                bones.append( (words[0], nameOrNone(words[1])) )
            elif status == 2:
                ikbones.append( (words[0], nameOrNone(words[1])) )
            elif status == 3:
                renames[words[0]] = nameOrNone(words[1])
    fp.close()
    #return (name, bones,renames,ikbones)

    boneMap = {}
    for (skelBone, refBone) in bones:
        boneMap[skelBone] = refBone
    return boneMap

def loadTargetJointsMapping(rigName, skel):
    boneMap = loadTargetMapping(rigName, skel)
    # TODO add compensation rotation (retarget to target rig)
    return [boneMap[bone.name] if bone.name in boneMap.keys() else None  for bone in skel.getBones()]

def nameOrNone(string):
    return string if string != "None" else None

def loadSourceMapping(srcName):
    import os

    path = os.path.join("tools/blender26x/mh_mocap_tool/source_rigs/", "%s.src" % srcName)
    if not os.path.isfile(path):
        raise RuntimeError("File %s with skeleton source rig mapping does not exist.", path)

    log.message("Read source file %s", path)
    sourceMapping = {}
    fp = open(path, "r")
    status = 0
    for line in fp:
        words = line.split()
        if len(words) > 0:
            key = words[0].lower()
            if key[0] == "#":
                continue
            elif key == "name:":
                name = words[1]
            elif key == "armature:":
                status = 1
            elif len(words) < 3:
                log.warning("Ignored illegal line %s", line)
            elif status == 1:
                for n in range(1,len(words)-2):
                    key += "_" + words[n]
                srcBone = nameOrNone(words[-2])
                if srcBone:
                    sourceMapping[srcBone] = (canonicalSrcName(key), float(words[-1]))
    fp.close()
    return sourceMapping

def canonicalSrcName(string):
    return string.lower().replace(' ','_').replace('-','_')

def __getRotation(bone, sourceMapping, targetMapping):
    """
    Hack to fix the fact that .src definition files ignore the rotation of the
    parent bones, requiring each bone to be rotated completely indepentent from
    its parent. This is not the case here.
    """
    if bone:
        if targetMapping:
            if bone.name in targetMapping:
                refBone = targetMapping[bone.name]
            else:
                refBone = None
        else:
            refBone = bone.name
        if refBone and refBone in sourceMapping:
            _, rot = sourceMapping[refBone]
            return rot
    return 0.0

def getRetargetMapping(sourceRig, targetRig, skel):
    sourceMapping = None
    targetMapping = None
    result = []

    # Load source to reference rig mapping
    if sourceRig:
        sourceMapping = loadSourceMapping(sourceRig)

    # Remap from reference rig to target rig
    if targetRig and targetRig != "soft1" and targetRig != "rigid" and targetRig != "mhx":
        targetMapping = loadTargetMapping(targetRig, skel)

    # Combine source and target mappings
    if sourceMapping and targetMapping:
        for bone in skel.getBones():
            if bone.name in targetMapping:
                refBone = targetMapping[bone.name]
                if refBone and refBone in sourceMapping:
                    srcBone, rotate = sourceMapping[refBone]
                    rotate = rotate - __getRotation(bone.parent, sourceMapping, targetMapping)
                    result.append( (srcBone, rotate) )
                else:
                    result.append( (refBone, 0.0) )
            else:
                result.append( (None, 0.0) )
    # Only remap from reference rig to custom rig
    elif targetMapping:
        for bone in skel.getBones():
            if bone.name in targetMapping:
                result.append( (targetMapping[bone.name], 0.0) )
            else:
                result.append( (None, 0.0) )
    # Only remap source rig to reference rig
    elif sourceMapping:
        for bone in skel.getBones():
            if bone.name in sourceMapping:
                srcBone, rot = sourceMapping[bone.name]
                rot = rot - __getRotation(bone.parent, sourceMapping, None)
                result.append( (srcBone, rot) )
            else:
                result.append( (None, 0.0) )
    # No remapping, return trivial 1-1 mapping
    else:
        return [(bone.name, 0.0) for bone in skel.getBones()]

    return result

def getRestPoseCompensation(srcSkel, tgtSkel, boneMapping, excludedTgtBones = ["Root", "Hips", "Spine1", "Spine2", "Spine3"]):
    """
    Determine compensation orientations for all bones of a target skeleton
    to be able to map motion from the specified source skeleton to the target
    skeleton, if their rest poses (or bone angles in rest pose) differ.
    The result will be the given boneMapping, as a list of tuples with a
    compensation transformation matrix as second item in each tuple.
    This matrix should be multiplied with each frame for the intended bone, so
    that the animation on srcSkel can be transferred to tgtSkel.
    ExcludedTgtBones is a list of target bone names that should be excluded
    from the process (not compensated for). Usually this is done with the spine
    bones (you could consider removing "Hips" from the list, though).
    The target skeleton will be set to its rest pose.
    """
    result = []

    # Determine pose to place target rig in the same rest pose as src rig
    #import animation
    #pose = animation.emptyPose(tgtSkel.getBoneCount())

    tgtSkel.setToRestPose()

    for bIdx, tgtBone in enumerate(tgtSkel.getBones()):
        boneMap = boneMapping[bIdx]
        if isinstance(boneMap, tuple):
            srcName, _ = boneMap
        else:
            srcName = boneMap

        result.append( (srcName, np.mat(np.identity(4))) )

        if not srcName:
            continue
        srcBone = srcSkel.getBone(srcName)
        srcGlobalOrient = srcBone.matRestGlobal.copy()
        srcGlobalOrient[:3,3] = 0.0  # No translation, only rotation
        tgtGlobalOrient = np.mat(tgtBone.matPoseGlobal.copy()) # Depends on pose compensation of parent bones
        tgtGlobalOrient[:3,3] = 0.0

        if srcBone.length == 0:
            # Safeguard because this always leads to wrong pointing target bones
            # I have no idea why, but for some reason the skeleton created from the BVH
            # has some zero-sized bones (this is probably a bug)
            log.message("skipping zero-length (source) bone %s", srcBone.name)
            continue

        if tgtBone.length == 0:
            log.message("skipping zero-length (target) bone %s", tgtBone.name)
            continue

        # Never compensate for spine bones, as this ususally deforms the mesh heavily
        if tgtBone.name in excludedTgtBones:
            log.message("Skipping non-compensated bone %s", tgtBone.name)
            continue

        log.message("compensating %s", tgtBone.name)
        log.debug(str(srcGlobalOrient))
        log.debug(str(tgtGlobalOrient))

        diff = np.mat(la.inv(tgtGlobalOrient)) * srcGlobalOrient
        # Rotation only
        diff[:3,3] = 0.0
        diffPose = tgtGlobalOrient * diff * np.mat(la.inv(tgtGlobalOrient))
        log.debug(str(diffPose))

        result[bIdx] = (srcName, diffPose)

        # Set pose that orients target bone in the same orientation as the source bone in rest
        tgtBone.matPose = np.mat(la.inv(tgtBone.matRestGlobal)) * diffPose * np.mat(tgtBone.matRestGlobal)

        tgtSkel.update()   # Update skeleton after each modification of a bone
    return result
