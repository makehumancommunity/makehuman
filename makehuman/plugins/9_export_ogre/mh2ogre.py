#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Export to the Ogre3d mesh format.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

The is an exporter that exports the human mesh to the Ogre3d mesh XML format.
(http://www.ogre3d.org/)
Supports both mesh and skeleton export.
A description of this format can be found here: https://bitbucket.org/sinbad/ogre/src/aebcd1e27621d9135c9355cb981838d46bf3835d/Tools/XMLConverter/docs/
"""

__docformat__ = 'restructuredtext'

import os
from progress import Progress
import codecs
import transformations
import exportutils
import skeleton
import log


def exportOgreMesh(human, filepath, config, progressCallback = None):
    progress = Progress.begin(logging = True, timing = True)

    progress(0, 0.05, "Setting properties")
    config.setHuman(human)
    feetOnGround = config.feetOnGround
    config.feetOnGround = False
    # TODO account for config.scale in skeleton
    config.setupTexFolder(filepath)
    filename = os.path.basename(filepath)
    name = formatName(config.goodName(os.path.splitext(filename)[0]))

    progress(0.05, 0.2, "Collecting Objects")
    rmeshes = exportutils.collect.setupMeshes(
        name,
        human,
        config=config,
        subdivide=config.subdivide)

    config.feetOnGround = feetOnGround

    progress(0.2, 0.95 - 0.35*bool(human.getSkeleton()))
    writeMeshFile(human, filepath, rmeshes, config)
    if human.getSkeleton():
        progress(0.6, 0.95, "Writing Skeleton")
        writeSkeletonFile(human, filepath, config)
    progress(0.95, 0.99, "Writing Materials")
    writeMaterialFile(human, filepath, rmeshes, config)
    progress(1.0, None, "Ogre export finished.")


def writeMeshFile(human, filepath, rmeshes, config, progressCallback = None):
    progress = Progress(len(rmeshes))

    filename = os.path.basename(filepath)
    name = formatName(config.goodName(os.path.splitext(filename)[0]))

    f = codecs.open(filepath, 'w', encoding="utf-8")
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<!-- Exported from MakeHuman (www.makehuman.org) -->\n')
    f.write('<mesh>\n')
    f.write('    <submeshes>\n')

    for rmeshIdx, rmesh in enumerate(rmeshes):
        loopprog = Progress() (0.0, 0.1, "Writing %s mesh." % rmesh.name)
        obj = rmesh.object
        # Make sure vertex normals are calculated
        obj.calcFaceNormals()
        obj.calcVertexNormals()
        # Calculate rendering data so we can use the unwelded vertices
        obj.updateIndexBuffer()
        numVerts = len(obj.r_coord)

        if obj.vertsPerPrimitive == 4:
            # Quads
            numFaces = len(obj.r_faces) * 2
        else:
            # Tris
            numFaces = len(obj.r_faces)

        loopprog(0.1, 0.3, "Writing faces of %s." % rmesh.name)
        f.write('        <submesh material="%s_%s_%s" usesharedvertices="false" use32bitindexes="false" operationtype="triangle_list">\n' % (formatName(name), rmeshIdx, formatName(rmesh.name) if formatName(rmesh.name) != name else "human"))

        # Faces
        f.write('            <faces count="%s">\n' % numFaces)
        for fv in obj.r_faces:
            f.write('                <face v1="%s" v2="%s" v3="%s" />\n' % (fv[0], fv[1], fv[2]))
            if obj.vertsPerPrimitive == 4:
                f.write('                <face v1="%s" v2="%s" v3="%s" />\n' % (fv[2], fv[3], fv[0]))
        f.write('            </faces>\n')

        loopprog(0.3, 0.7, "Writing vertices of %s." % rmesh.name)
        # Vertices
        f.write('            <geometry vertexcount="%s">\n' % numVerts)
        f.write('                <vertexbuffer positions="true" normals="true">\n')
        #f.write('                <vertexbuffer positions="true">\n')
        for vIdx, co in enumerate(obj.r_coord):
            if config.feetOnGround:
                co = co.copy()
                co[1] += getFeetOnGroundOffset(human)

            # Note: Ogre3d uses a y-up coordinate system (just like MH)
            norm = obj.r_vnorm[vIdx]
            f.write('                    <vertex>\n')
            f.write('                        <position x="%s" y="%s" z="%s" />\n' % (co[0], co[1], co[2]))
            f.write('                        <normal x="%s" y="%s" z="%s" />\n' % (norm[0], norm[1], norm[2]))
            f.write('                    </vertex>\n')
        f.write('                </vertexbuffer>\n')

        loopprog(0.8 - 0.1*bool(human.getSkeleton()), 0.9, "Writing UVs of %s." % rmesh.name)
        # UV Texture Coordinates
        f.write('                <vertexbuffer texture_coord_dimensions_0="2" texture_coords="1">\n')
        for vIdx in xrange(numVerts):
            if obj.has_uv:
                u, v = obj.r_texco[vIdx]
                v = 1-v
            else:
                u, v = 0, 0
            f.write('                    <vertex>\n')
            f.write('                        <texcoord u="%s" v="%s" />\n' % (u, v))
            f.write('                    </vertex>\n')
        f.write('                </vertexbuffer>\n')
        f.write('            </geometry>\n')

        if human.getSkeleton():
            loopprog(0.9, 0.99, "Writing bone assignments of %s." % rmesh.name)
        else:
            loopprog(0.99, None, "Written %s." % rmesh.name)
        # Skeleton bone assignments
        if human.getSkeleton():
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

            f.write('            <boneassignments>\n')
            boneNames = [ bone.name for bone in human.getSkeleton().getBones() ]
            for (boneName, (verts,ws)) in weights.items():
                bIdx = boneNames.index(boneName)
                for i, vIdx in enumerate(verts):
                    w = ws[i]
                    try:
                        for r_vIdx in originalToUnweldedMap[vIdx]:
                            f.write('                <vertexboneassignment vertexindex="%s" boneindex="%s" weight="%s" />\n' % (r_vIdx, bIdx, w))
                    except:
                        # unused coord
                        pass
            f.write('            </boneassignments>\n')

        progress.step()
        f.write('        </submesh>\n')

    f.write('    </submeshes>\n')
    f.write('    <submeshnames>\n')
    for rmeshIdx, rmesh in enumerate(rmeshes):
        f.write('        <submeshname name="%s" index="%s" />\n' % (formatName(rmesh.name) if formatName(rmesh.name) != name else "human", rmeshIdx))
    f.write('    </submeshnames>\n')

    if human.getSkeleton():
        f.write('    <skeletonlink name="%s.skeleton" />\n' % name)
    f.write('</mesh>')
    f.close()


def writeSkeletonFile(human, filepath, config):
    Pprogress = Progress(3)  # Parent.
    filename = os.path.basename(filepath)
    name = formatName(config.goodName(os.path.splitext(filename)[0]))
    filename = name + ".skeleton.xml"
    filepath = os.path.join(os.path.dirname(filepath), filename)

    skel = human.getSkeleton()

    f = codecs.open(filepath, 'w', encoding="utf-8")
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<!-- Exported from MakeHuman (www.makehuman.org) -->\n')
    f.write('<skeleton>\n')
    f.write('    <bones>\n')
    progress = Progress(len(skel.getBones()))
    for bIdx, bone in enumerate(skel.getBones()):
        pos = bone.getRestOffset()
        if config.feetOnGround and not bone.parent:
            pos[1] += getFeetOnGroundOffset(human)
        f.write('        <bone id="%s" name="%s">\n' % (bIdx, bone.name))
        f.write('            <position x="%s" y="%s" z="%s" />\n' % (pos[0], pos[1], pos[2]))
        f.write('            <rotation angle="0">\n')
        f.write('                <axis x="1" y="0" z="0" />\n')
        f.write('            </rotation>\n')
        f.write('        </bone>\n')
        progress.step()
    f.write('    </bones>\n')
    Pprogress.step()

    f.write('    <bonehierarchy>\n')
    progress = Progress(len(skel.getBones()))
    for bone in skel.getBones():
        if bone.parent:
            f.write('        <boneparent bone="%s" parent="%s" />\n' % (bone.name, bone.parent.name))
        progress.step()
    f.write('    </bonehierarchy>\n')
    Pprogress.step()

    if hasattr(human, 'animations'):
        f.write('    <animations>\n')
        for anim in human.animations:
            writeAnimation(human, f, anim.getAnimationTrack())
        f.write('    </animations>\n')
        f.write('</skeleton>')
        f.close()
    Pprogress.finish()


def writeMaterialFile(human, filepath, rmeshes, config):
    progress = Progress(len(rmeshes))
    folderpath = os.path.dirname(filepath)
    name = formatName(config.goodName(os.path.splitext(os.path.basename(filepath))[0]))
    filename = name + ".material"
    filepath = os.path.join(folderpath, filename)

    f = codecs.open(filepath, 'w', encoding="utf-8")
    for rmeshIdx, rmesh in enumerate(rmeshes):
        if rmeshIdx > 0:
            f.write('\n')
        f.write('material %s_%s_%s\n' % (formatName(name), rmeshIdx, formatName(rmesh.name) if formatName(rmesh.name) != name else "human"))
        f.write('{\n')
        f.write('    receive_shadows on\n\n')
        f.write('    technique\n')
        f.write('    {\n')
        f.write('        pass\n')
        f.write('        {\n')
        f.write('            lighting on\n\n')
        f.write('            ambient 0.8 0.8 0.8 1\n')
        f.write('            diffuse 0.8 0.8 0.8 1\n')
        f.write('            specular 0.1 0.1 0.1 1\n')
        f.write('            emissive 0 0 0\n\n')
        if not rmesh.type:
            # Enable transparency rendering on human
            f.write('            depth_write on\n')
            f.write('            alpha_rejection greater 128\n\n')

        if rmesh.material.diffuseTexture is not None:
            texfile = os.path.basename(rmesh.material.diffuseTexture)
            f.write('            texture_unit\n')
            f.write('            {\n')
            f.write('                texture %s\n' % texfile)
            f.write('            }\n')

        # TODO add support for normal maps, material properties, ...
        f.write('        }\n')
        f.write('    }\n')
        f.write('}\n')
        progress.step()
    f.close()

def writeAnimation(human, fp, animTrack):
    progress = Progress(len(human.getSkeleton().getBones()))
    log.message("Exporting animation %s.", animTrack.name)
    fp.write('        <animation name="%s" length="%s">\n' % (animTrack.name, animTrack.getPlaytime()))
    fp.write('            <tracks>\n')
    for bIdx, bone in enumerate(human.getSkeleton().getBones()):
        # Note: OgreXMLConverter will optimize out unused (not moving) animation tracks
        fp.write('                <track bone="%s">\n' % bone.name)
        fp.write('                    <keyframes>\n')
        frameTime = 1.0/float(animTrack.frameRate)
        for frameIdx in xrange(animTrack.nFrames):
            poseMat = animTrack.getAtFramePos(frameIdx)[bIdx]
            translation = poseMat[:3,3]
            angle, axis, _ = transformations.rotation_from_matrix(poseMat)
            fp.write('                        <keyframe time="%s">\n' % (float(frameIdx) * frameTime))
            fp.write('                            <translate x="%s" y="%s" z="%s" />\n' % (translation[0], translation[1], translation[2]))
            # TODO account for scale
            fp.write('                            <rotate angle="%s">\n' % angle)
            fp.write('                                <axis x="%s" y="%s" z="%s" />\n' % (axis[0], axis[1], axis[2]))
            fp.write('                            </rotate>\n')
            fp.write('                        </keyframe>\n')
        fp.write('                    </keyframes>\n')
        fp.write('                </track>\n')
        progress.step()
    fp.write('            </tracks>\n')
    fp.write('        </animation>\n')



def formatName(name):
    if name.endswith('.mesh'):
        return name[:-5]
    else:
        return name


def getFeetOnGroundOffset(human):
    return -human.getJointPosition('ground')[1]
