#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Export to id Software's MD5 format.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

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
import exportutils
import skeleton
import log
from progress import Progress

ZYRotation = np.array(((1,0,0,0),(0,0,-1,0),(0,1,0,0),(0,0,0,1)), dtype=np.float32)

scale = 5  # Override scale setting to a sensible default for doom-style engines


def exportMd5(human, filepath, config):
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

    progress = Progress()

    obj = human.meshData
    config.setHuman(human)
    config.zUp = True
    config.feetOnGround = True    # TODO this only works when exporting MHX mesh (a design error in exportutils)
    config.scale = 1
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])

    humanBBox = human.meshData.calcBBox()

    progress(0, 0.2, "Collecting Objects")
    rmeshes = exportutils.collect.setupMeshes(
        name,
        human,
        config=config,
        subdivide=config.subdivide)

    if human.getSkeleton():
        numJoints = human.getSkeleton().getBoneCount() +1 # Amount of joints + the hardcoded origin below
    else:
        numJoints = 1

    f = codecs.open(filepath, 'w', encoding="utf-8")
    f.write('MD5Version 10\n')
    f.write('commandline ""\n\n')
    f.write('numJoints %d\n' % numJoints)
    f.write('numMeshes %d\n\n' % (len(rmeshes)))

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
    loopprog = Progress(len(rmeshes))
    for rmeshIdx, rmesh in enumerate(rmeshes):
        # rmesh.type: None is human, "Proxymeshes" is human proxy, "Clothes" for clothing and "Hair" for hair
        objprog = Progress()

        obj = rmesh.object

        obj.calcFaceNormals()
        obj.calcVertexNormals()
        obj.updateIndexBuffer()

        numVerts = len(obj.r_coord)
        if obj.vertsPerPrimitive == 4:
            # Quads
            numFaces = len(obj.r_faces) * 2
        else:
            # Tris
            numFaces = len(obj.r_faces)

        f.write('mesh {\n')
        mat = rmesh.material
        if mat.diffuseTexture:
            tex = copyTexture(mat.diffuseTexture, human, config)
            f.write('\tshader "%s"\n' % tex)

        f.write('\n\tnumverts %d\n' % numVerts)

        # Collect vertex weights
        if human.getSkeleton():
            objprog(0, 0.2)
            bodyWeights = human.getVertexWeights()

            if rmesh.type:
                # Determine vertex weights for proxy
                weights = skeleton.getProxyWeights(rmesh.proxy, bodyWeights, obj)
            else:
                # Use vertex weights for human body
                weights = bodyWeights
                # Account for vertices that are filtered out
                if rmesh.vertexMapping != None:
                    filteredVIdxMap = rmesh.vertexMapping
                    weights2 = {}
                    for (boneName, (verts,ws)) in weights.items():
                        verts2 = []
                        ws2 = []
                        for i, vIdx in enumerate(verts):
                            if vIdx in filteredVIdxMap:
                                verts2.append(filteredVIdxMap[vIdx])
                                ws2.append(ws[i])
                        weights2[boneName] = (verts2, ws2)
                    weights = weights2

            # Remap vertex weights to the unwelded vertices of the object (obj.coord to obj.r_coord)
            originalToUnweldedMap = {}
            for unweldedIdx, originalIdx in enumerate(obj.vmap):
                if originalIdx not in originalToUnweldedMap.keys():
                    originalToUnweldedMap[originalIdx] = []
                originalToUnweldedMap[originalIdx].append(unweldedIdx)

            # Build a weights list indexed per vertex
            jointIndexes = {}
            jointIndexes['origin'] = 0
            joints = [None] + human.getSkeleton().getBones() # origin joint is None
            for idx,bone in enumerate(joints):
                if bone:
                    jointIndexes[bone.name] = idx
            vertWeights = {}    # = dict( vertIdx: [ (jointIdx1, weight1), ...])
            for (jointName, (verts,ws)) in weights.items():
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
            objprog(0.2, 0.3)
        else:
            vertWeights = None
            objprog(0, 0.3)

        # Write vertices
        wCount = 0
        for vert in xrange(numVerts):
            if obj.has_uv:
                u, v = obj.r_texco[vert]
            else:
                u, v = 0, 0
            if vertWeights == None:
                numWeights = 1
            else:
                numWeights = len(vertWeights[vert])
            # vert [vertIndex] ( [texU] [texV] ) [weightIndex] [weightElem]
            f.write('\tvert %d ( %f %f ) %d %d\n' % (vert, u, 1.0-v, wCount, numWeights))
            wCount = wCount + numWeights
        objprog(0.3, 0.5)

        # Write faces
        f.write('\n\tnumtris %d\n' % numFaces)
        fn = 0
        for fv in obj.r_faces:
            # tri [triIndex] [vertIndex1] [vertIndex2] [vertIndex3]
            f.write('\ttri %d %d %d %d\n' % (fn, fv[2], fv[1], fv[0]))
            fn += 1
            if fv[0] != fv[3]:
                f.write('\ttri %d %d %d %d\n' % (fn, fv[0], fv[3], fv[2]))
                fn += 1
        objprog(0.5, 0.99)

        # Write bone weighting
        bwprog = Progress(len(obj.r_coord)).HighFrequency(200)
        if human.getSkeleton():
            f.write('\n\tnumweights %d\n' % wCount)
            wCount = 0
            for idx,co in enumerate(obj.r_coord):
                for (jointIdx, jointWght) in vertWeights[idx]:
                    # Get vertex position in bone space
                    if joints[jointIdx]:
                        invbonematrix = joints[jointIdx].matRestGlobal.copy()
                        invbonematrix[:3,3] = [0,0,0]
                        invbonematrix = la.inv(invbonematrix)
                        relPos = np.ones(4, dtype=np.float32)
                        relPos[:3] = co[:3]
                        relPos[:3] -= joints[jointIdx].getRestHeadPos()
                        relPos[:3] *= scale
                        #relPos = np.dot(relPos, invbonematrix)
                    else:
                        relPos = co[:3] * scale

                    if config.zUp:
                        relPos[:3] = relPos[[0,2,1]] * [1,-1,1]

                    # weight [weightIndex] [jointIndex] [weightValue] ( [xPos] [yPos] [zPos] )
                    f.write('\tweight %d %d %f ( %f %f %f )\n' % (wCount, jointIdx, jointWght, relPos[0], relPos[1], relPos[2]))
                    wCount = wCount +1
                bwprog.step()
        else:
            # No skeleton selected: Attach all vertices to the root with weight 1.0
            f.write('\n\tnumweights %d\n' % (numVerts))
            for idx,co in enumerate(obj.r_coord):
                # weight [weightIndex] [jointIndex] [weightValue] ( [xPos] [yPos] [zPos] )
                co = co.copy() * scale

                if config.feetOnGround:
                    co[1] += (getFeetOnGroundOffset(human) * scale)

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

    progress(1, None, "MD5 export finished. Exported file: %s" % filepath)

def writeBone(f, bone, human, config):
    """
    This function writes out information describing one joint in MD5 format.

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
    pos = bone.getRestHeadPos() * scale

    if config.feetOnGround:
        pos[1] += (getFeetOnGroundOffset(human) * scale)

    if config.zUp:
        #transformationMat = bone.matRestGlobal.copy()
        #transformationMat = np.dot(ZYRotation, np.dot(transformationMat,la.inv(ZYRotation)))
        #orientationQuat = aljabr.matrix2Quaternion(transformationMat)
        pos = pos[[0,2,1]] * [1,-1,1]
    #else:
    #    orientationQuat = bone.getRestOrientationQuat()

    #qx = orientationQuat[0]
    #qy = orientationQuat[1]
    #qz = orientationQuat[2]
    #w = orientationQuat[3]

    # TODO currently all bones have a global z-up orientation, maybe orient them along y axis
    qx = qy = qz = 0.0

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
    bounds = humanBBox
    if config.feetOnGround:
        bounds[:][1] += getFeetOnGroundOffset(human)
    if config.zUp:
        bounds[0] = bounds[0][[0,2,1]] * [1,-1,1]
        bounds[1] = bounds[1][[0,2,1]] * [1,-1,1]
    bounds = bounds * scale
    # TODO use bounds calculated for every frame
    for frameIdx in xrange(animTrack.nFrames):
        #( vec3:boundMin ) ( vec3:boundMax )
        f.write('\t( %f %f %f ) ( %f %f %f )\n' % (bounds[0][0], bounds[0][1], bounds[0][2], bounds[1][0], bounds[1][1], bounds[1][2]))
    f.write('}\n\n')

    f.write('baseframe {\n')
    f.write('\t( %f %f %f ) ( %f %f %f )\n' % (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    bases = []
    for bone in skel.getBones():
        pos = bone.getRestOffset() * scale
        if config.feetOnGround and not bone.parent:
            pos[1] += (getFeetOnGroundOffset(human) * scale)

        transformationMat = bone.matRestRelative.copy()
        if config.zUp:
            transformationMat = np.dot(ZYRotation, np.dot(transformationMat,la.inv(ZYRotation)))
            pos = pos[[0,2,1]] * [1,-1,1]
        orientationQuat = tm.quaternion_from_matrix(transformationMat)

        qx = orientationQuat[0]
        qy = orientationQuat[1]
        qz = orientationQuat[2]
        w = orientationQuat[3]

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
            pos = transformationMat[:3,3] * scale
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
