#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Export to id Software's MD5 format.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers, Jonas Hauquier

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

This module implements a plugin to export MakeHuman mesh and skeleton data to id Software's MD5 format.
See http://www.modwiki.net/wiki/MD5MESH_(file_format) for information on the format.

Requires:

- base modules

"""

__docformat__ = 'restructuredtext'

import os
import codecs
import numpy as np
import numpy.linalg as la
import transformations as tm
import log
from progress import Progress

ZYRotation = np.array(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)), dtype=np.float32)

def exportMd5(filepath, config):
    """
    This function exports MakeHuman mesh and skeleton data to id Software's MD5 format.

    Parameters
    ----------

    human:
      *Human*.  The object whose information is to be used for the export.
    filepath:
      *string*.  The filepath of the file to export the object to.
    config:
      *Config*.  Export configuration.
    """

    progress = Progress.begin(logging=True, timing=True)

    human = config.human
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    # TODO this should probably be the only option
    config.zUp = True
    config.feetOnGround = True
    config.scale = 5  # Override scale setting to a sensible default for doom-style engines

    humanBBox = human.meshData.calcBBox()

    objects = human.getObjects(excludeZeroFaceObjs=True)
    meshes = [obj.mesh.clone(config.scale, True) for obj in objects]
    # TODO set good names for meshes

    if human.getSkeleton():
        numJoints = human.getSkeleton().getBoneCount() +1 # Amount of joints + the hardcoded origin below
    else:
        numJoints = 1

    f = codecs.open(filepath, 'w', encoding="utf-8")
    f.write('MD5Version 10\n')
    f.write('commandline ""\n\n')
    f.write('numJoints %d\n' % numJoints)
    f.write('numMeshes %d\n\n' % (len(meshes)))

    f.write('joints {\n')
    # Hardcoded root joint
    f.write('\t"%s" %d ( %f %f %f ) ( %f %f %f )\n' % ('origin', -1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    progress(0.2, 0.3, "Writing Bones")
    if human.getSkeleton():
        bones = human.getSkeleton().getBones()
        boneprog = Progress(len(bones))
        for bone in bones:
            writeBone(f, bone, human, config)
            boneprog.step()
    f.write('}\n\n')

    progress(0.3, 0.8, "Writing Objects")
    loopprog = Progress(len(meshes))
    for meshIdx, mesh in enumerate(meshes):
        objprog = Progress()
        objprog(0.0, 0.1, "Writing %s mesh." % mesh.name)

        obj = mesh.object

        # Make sure r_... members are initiated
        mesh.updateIndexBuffer()

        numVerts = len(mesh.r_coord)
        if mesh.vertsPerPrimitive == 4:
            # Quads
            numFaces = len(mesh.r_faces) * 2
        else:
            # Tris
            numFaces = len(mesh.r_faces)

        f.write('mesh {\n')
        mat = mesh.material
        if mat.diffuseTexture:
            tex = copyTexture(mat.diffuseTexture, human, config)
            f.write('\tshader "%s"\n' % tex)

        f.write('\n\tnumverts %d\n' % numVerts)

        # Collect vertex weights
        if human.getSkeleton():
            objprog(0.1, 0.2, "Writing skeleton")
            rawWeights = human.getVertexWeights()

            # Remap vertex weights to mesh
            if obj.proxy:
                # Determine vertex weights for proxy
                parentWeights = obj.proxy.getVertexWeights(rawWeights)
            else:
                parentWeights = rawWeights
            # Account for vertices that are filtered out
            weights = mesh.getVertexWeights(parentWeights)

            # Remap vertex weights to the unwelded vertices of the object (mesh.coord to mesh.r_coord)
            originalToUnweldedMap = mesh.inverse_vmap

            # Build a weights list indexed per vertex  # TODO this can be done easier by compiling VertexBoneWeights data
            jointIndexes = {}
            jointIndexes['origin'] = 0
            joints = [None] + human.getSkeleton().getBones() # origin joint is None
            for idx,bone in enumerate(joints):
                if bone:
                    jointIndexes[bone.name] = idx
            vertWeights = {}    # = dict( vertIdx: [ (jointIdx1, weight1), ...])
            for (jointName, (verts,ws)) in weights.data.items():
                jointIdx = jointIndexes[jointName]
                for idx,v in enumerate(verts):
                    try:
                        for r_vIdx in originalToUnweldedMap[v]:
                            if r_vIdx not in vertWeights:
                                vertWeights[r_vIdx] = []
                            vertWeights[r_vIdx].append((jointIdx, ws[idx]))
                    except:
                        # unused coord
                        pass
            for vert in xrange(numVerts):
                if vert not in vertWeights:
                    # Weight vertex completely to origin joint
                    vertWeights[vert] = [(0, 1.0)]
        else:
            vertWeights = None

        objprog(0.3, 0.7, "Writing vertices for %s." % mesh.name)
        # Write vertices
        wCount = 0
        for vert in xrange(numVerts):
            if mesh.has_uv:
                u, v = mesh.r_texco[vert]
            else:
                u, v = 0, 0
            if vertWeights == None:
                numWeights = 1
            else:
                numWeights = len(vertWeights[vert])
            # vert [vertIndex] ( [texU] [texV] ) [weightIndex] [weightElem]
            f.write('\tvert %d ( %f %f ) %d %d\n' % (vert, u, 1.0-v, wCount, numWeights))
            wCount = wCount + numWeights

        objprog(0.7, 0.8, "Writing faces for %s." % mesh.name)
        # Write faces
        f.write('\n\tnumtris %d\n' % numFaces)
        fn = 0
        for fv in mesh.r_faces:
            # tri [triIndex] [vertIndex1] [vertIndex2] [vertIndex3]
            f.write('\ttri %d %d %d %d\n' % (fn, fv[2], fv[1], fv[0]))
            fn += 1
            if fv[0] != fv[3]:
                f.write('\ttri %d %d %d %d\n' % (fn, fv[0], fv[3], fv[2]))
                fn += 1

        objprog(0.8, 0.99, "Writing bone weights for %s." % mesh.name)
        # Write bone weighting
        bwprog = Progress(len(mesh.r_coord)).HighFrequency(200)
        if human.getSkeleton():
            f.write('\n\tnumweights %d\n' % wCount)
            wCount = 0
            for idx,co in enumerate(mesh.r_coord):
                for (jointIdx, jointWght) in vertWeights[idx]:
                    # Get vertex position in bone space
                    if joints[jointIdx]:
                        invbonematrix = joints[jointIdx].matRestGlobal.copy()
                        invbonematrix[:3,3] = [0,0,0]
                        invbonematrix = la.inv(invbonematrix)
                        relPos = np.ones(4, dtype=np.float32)
                        relPos[:3] = co[:3]
                        relPos[:3] -= joints[jointIdx].getRestHeadPos()
                        relPos[:3] *= config.scale
                        #relPos = np.dot(relPos, invbonematrix)
                    else:
                        relPos = co[:3] * config.scale

                    if config.zUp:
                        relPos[:3] = relPos[[0,2,1]] * [1,-1,1]

                    # weight [weightIndex] [jointIndex] [weightValue] ( [xPos] [yPos] [zPos] )
                    f.write('\tweight %d %d %f ( %f %f %f )\n' % (wCount, jointIdx, jointWght, relPos[0], relPos[1], relPos[2]))
                    wCount = wCount +1
                bwprog.step()
        else:
            # No skeleton selected: Attach all vertices to the root with weight 1.0
            f.write('\n\tnumweights %d\n' % (numVerts))
            for idx,co in enumerate(mesh.r_coord):
                # weight [weightIndex] [jointIndex] [weightValue] ( [xPos] [yPos] [zPos] )
                co = co.copy()

                if config.feetOnGround:
                    co += config.offset

                if config.zUp:
                    co = co[[0,2,1]] * [1,-1,1]

                f.write('\tweight %d %d %f ( %f %f %f )\n' % (idx, 0, 1.0, co[0], co[1], co[2]))
                # Note: MD5 has a z-up coordinate system
                bwprog.step()
        f.write('}\n\n')
        loopprog.step()
    f.close()

    progress(0.8, 0.99, "Writing Animations")
    if human.getSkeleton() and hasattr(human, 'animations'):
        animprog = Progress(len(human.animations))
        for anim in human.animations:
            writeAnimation(filepath, human, humanBBox, config, anim.getAnimationTrack())
            animprog.step()

    progress(1, None, "MD5 export finished. Exported file: %s", filepath)

def writeBone(f, bone, human, config):
    """
    This function writes out information describing one joint in MD5 format and bind pose of bones.

    Parameters
    ----------

    f:
    *file handle*.  The handle of the file being written to.
    joint:
    *Bone object*.  The bone object to be processed by this function call.
    """
    if bone.parent:
        parentIndex = bone.parent.index + 1
    else:
        parentIndex = 0 # Refers to the hard-coded root joint

    # Bind pose joint orientation is in world space
    mat = bone.getRestMatrix(offsetVect=config.offset)
    pos = mat[:3,3]

    w, qx, qy, qz = tm.quaternion_from_matrix(mat)

    # "[boneName]"   [parentIndex] ( [xPos] [yPos] [zPos] ) ( [xOrient] [yOrient] [zOrient] )
    f.write('\t"%s" %d ( %f %f %f ) ( %f %f %f )\n' % (bone.name, parentIndex,
        pos[0], pos[1], pos[2],
        qx, qy, qz))

def writeAnimation(filepath, human, humanBBox, config, animTrack):
    log.message("Exporting animation %s.", animTrack.name)
    numJoints = len(human.getSkeleton().getBones()) + 1

    animfilename = os.path.splitext(os.path.basename(filepath))[0]
    animfilename = animfilename + "_%s.md5anim" % (animTrack.name)
    foldername = os.path.dirname(filepath)
    animfilepath = os.path.join(foldername, animfilename)
    f = codecs.open(animfilepath, 'w', encoding="utf-8")
    f.write('MD5Version 10\n')
    f.write('commandline ""\n\n')
    f.write('numFrames %d\n' % animTrack.nFrames)
    f.write('numJoints %d\n' % numJoints)
    f.write('frameRate %d\n' % int(animTrack.frameRate))
    f.write('numAnimatedComponents %d\n\n' % (numJoints * 6))

    skel = human.getSkeleton()
    if skel:
        if config.scale != 1:
            skel = skel.scaled(config.scale)
        if not skel.isInRestPose():
            # Export skeleton with the current pose as rest pose
            skel = skel.createFromPose()

    flags = 63
    f.write('hierarchy {\n')
    f.write('\t"origin" -1 %d 0\n' % flags)
    arrayIdx = 6
    for bIdx, bone in enumerate(skel.getBones()):
        #<string:jointName> <int:parentIndex> <int:flags> <int:startIndex>
        if bone.parent:
            f.write('\t"%s" %d %d %d\n' % (bone.name, bone.parent.index+1, flags, arrayIdx))
        else:
            f.write('\t"%s" %d %d %d\n' % (bone.name, 0, flags, arrayIdx))
        arrayIdx = arrayIdx + 6
    f.write('}\n\n')

    f.write('bounds {\n')
    bounds = humanBBox.copy()
    bounds = bounds * config.scale
    if config.feetOnGround:
        bounds[:][1] += config.offset
    if config.zUp:
        bounds[0] = bounds[0][[0,2,1]] * [1,-1,1]
        bounds[1] = bounds[1][[0,2,1]] * [1,-1,1]
    # TODO use bounds calculated for every frame
    for frameIdx in xrange(animTrack.nFrames):
        #( vec3:boundMin ) ( vec3:boundMax )
        f.write('\t( %f %f %f ) ( %f %f %f )\n' % (bounds[0][0], bounds[0][1], bounds[0][2], bounds[1][0], bounds[1][1], bounds[1][2]))
    f.write('}\n\n')

    f.write('baseframe {\n')
    f.write('\t( %f %f %f ) ( %f %f %f )\n' % (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    bases = []
    for bone in skel.getBones():
        mat = bone.getRelativeMatrix(offsetVect=config.offset)
        pos = mat[:3,3]

        w, qx, qy, qz = tm.quaternion_from_matrix(mat)

        #( vec3:position ) ( vec3:orientation )
        f.write('\t( %f %f %f ) ( %f %f %f )\n' % (pos[0], pos[1], pos[2], qx, qy, qz))
        bases.append((pos, [qx, qy, qz, w]))
    f.write('}\n\n')

    for frameIdx in xrange(animTrack.nFrames):
        frame = animTrack.getAtFramePos(frameIdx)
        f.write('frame %d {\n' % frameIdx)
        f.write('\t%f %f %f %f %f %f\n' % (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))  # Transformation for origin joint
        for bIdx in xrange(numJoints-1):
            transformationMat = frame[bIdx].copy()
            pos = transformationMat[:3,3] * config.scale
            transformationMat[:3,3] = [0.0, 0.0, 0.0]

            if config.zUp:
                transformationMat = np.dot(ZYRotation, np.dot(transformationMat,la.inv(ZYRotation)))
                pos = pos[[0,2,1]] * [1,-1,1]

            #baseRot = aljabr.quaternion2Matrix(bases[bIdx][1])
            #transformationMat = np.dot(transformationMat[:3,:3], baseRot)

            pos += bases[bIdx][0]
            orientationQuat = tm.quaternion_from_matrix(transformationMat)
            qx = orientationQuat[0]
            qy = orientationQuat[1]
            qz = orientationQuat[2]
            w = orientationQuat[3]

            if w > 0:
                qx = -qx
                qy = -qy
                qz = -qz

            # vec3:position vec3:orientation
            f.write('\t%f %f %f %f %f %f\n' % (pos[0], pos[1], pos[2], qx, qy, qz))
        f.write('}\n\n')

    f.close()


def copyTexture(texture, human, config):
    if not texture:
        return
    # Contrary to what you might expect, this function actually copies the texture to its new location...
    newpath = config.copyTextureToNewLocation(texture)
    return newpath


def getFeetOnGroundOffset(human):
    return human.getJointPosition('ground')[1]
