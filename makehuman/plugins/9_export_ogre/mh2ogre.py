#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Export to the Ogre3d mesh format.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3

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
import log

# TODO support different mesh orientations, scale and different bone local axis

def exportOgreMesh(filepath, config):
    progress = Progress.begin()

    progress(0, 0.05, "Preparing export")
    human = config.human

    # TODO account for config.scale in skeleton
    config.setupTexFolder(filepath) # TODO unused

    progress(0.05, 0.2, "Collecting Objects")
    objects = human.getObjects(excludeZeroFaceObjs=True)

    progress(0.2, 0.95 - 0.35*bool(human.getSkeleton()))
    writeMeshFile(human, filepath, objects, config)
    if human.getSkeleton():
        progress(0.6, 0.95, "Writing Skeleton")
        writeSkeletonFile(human, filepath, config)
    progress(0.95, 0.99, "Writing Materials")
    writeMaterialFile(human, filepath, objects, config)
    progress(1.0, None, "Ogre export finished.")


def writeMeshFile(human, filepath, objects, config):
    progress = Progress(len(objects))

    filename = os.path.basename(filepath)
    name = formatName(os.path.splitext(filename)[0])

    f = codecs.open(filepath, 'w', encoding="utf-8")
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<!-- Exported from MakeHuman (www.makehuman.org) -->')
    lines.append('<mesh>')
    lines.append('    <submeshes>')

    if human.getSkeleton():
        bodyWeights = human.getVertexWeights(human.getSkeleton())

    for objIdx, obj in enumerate(objects):
        loopprog = Progress()

        loopprog(0.0, 0.1, "Writing %s mesh.", obj.name)

        pxy = obj.proxy
        mesh = obj.mesh

        # Scale and filter out masked vertices/faces
        mesh = mesh.clone(scale=config.scale, filterMaskedVerts=True)  # here obj.parent is set to the original obj

        numVerts = len(mesh.r_coord)

        if mesh.vertsPerPrimitive == 4:
            # Quads
            numFaces = len(mesh.r_faces) * 2
        else:
            # Tris
            numFaces = len(mesh.r_faces)

        loopprog(0.1, 0.3, "Writing faces of %s.", obj.name)
        # TODO add proxy type name in material name as well
        lines.append('        <submesh material="%s_%s_%s" usesharedvertices="false" use32bitindexes="false" operationtype="triangle_list">' % (name, objIdx, formatName(obj.name) if formatName(obj.name) != name else "human"))

        # Faces
        lines.append('            <faces count="%s">' % numFaces)
        if mesh.vertsPerPrimitive == 4:
            lines.extend( ['''\
                <face v1="%s" v2="%s" v3="%s" />
                <face v1="%s" v2="%s" v3="%s" />''' % (fv[0], fv[1], fv[2],
                                                       fv[2], fv[3], fv[0]) \
                for fv in mesh.r_faces ] )
        else:
            lines.extend( ['                <face v1="%s" v2="%s" v3="%s" />' % (fv[0], fv[1], fv[2]) for fv in mesh.r_faces])
        lines.append('            </faces>')

        loopprog(0.3, 0.7, "Writing vertices of %s.", obj.name)
        # Vertices
        lines.append('            <geometry vertexcount="%s">' % numVerts)
        lines.append('                <vertexbuffer positions="true" normals="true">')
        coords = mesh.r_coord.copy()
        if config.feetOnGround:
            coords[:] += config.offset
        # Note: Ogre3d uses a y-up coordinate system (just like MH)
        lines.extend(['''\
                    <vertex>
                        <position x="%s" y="%s" z="%s" />
                        <normal x="%s" y="%s" z="%s" />
                    </vertex>''' % (coords[vIdx,0], coords[vIdx,1], coords[vIdx,2],
                                    mesh.r_vnorm[vIdx,0], mesh.r_vnorm[vIdx,1], mesh.r_vnorm[vIdx,2]) \
            for vIdx in xrange(coords.shape[0]) ])
        lines.append('                </vertexbuffer>')


        loopprog(0.8 - 0.1*bool(human.getSkeleton()), 0.9, "Writing UVs of %s.", obj.name)
        # UV Texture Coordinates
        lines.append('                <vertexbuffer texture_coord_dimensions_0="2" texture_coords="1">')
        if mesh.has_uv:
            uvs = mesh.r_texco.copy()
            uvs[:,1] = 1-uvs[:,1]  # v = 1 - v
        else:
            import numpy as np
            uvs = np.zeros((numVerts,2), dtype=np.float32)

        lines.extend( ['''\
                    <vertex>
                        <texcoord u="%s" v="%s" />
                    </vertex>''' % (u, v) for u, v in uvs ] )
        lines.append('                </vertexbuffer>')
        lines.append('            </geometry>')

        if human.getSkeleton():
            loopprog(0.9, 0.99, "Writing bone assignments of %s.", obj.name)
        else:
            loopprog(0.99, None, "Written %s.", obj.name)

        # Skeleton bone assignments
        if human.getSkeleton():
            if pxy:
                # Determine vertex weights for proxy (map to unfiltered proxy mesh)
                weights = pxy.getVertexWeights(bodyWeights, human.getSkeleton())
            else:
                # Use vertex weights for human body
                weights = bodyWeights

            # Remap vertex weights to account for hidden vertices that are 
            # filtered out, and remap to multiple vertices if mesh is subdivided
            weights = mesh.getVertexWeights(weights)

            # Remap vertex weights to the unwelded vertices of the object (mesh.coord to mesh.r_coord)
            originalToUnweldedMap = mesh.inverse_vmap

            lines.append('            <boneassignments>')
            boneNames = [ bone.name for bone in human.getSkeleton().getBones() ]
            for (boneName, (verts,ws)) in weights.data.items():
                bIdx = boneNames.index(boneName)
                for i, vIdx in enumerate(verts):
                    w = ws[i]
                    try:
                        lines.extend( ['                <vertexboneassignment vertexindex="%s" boneindex="%s" weight="%s" />' % (r_vIdx, bIdx, w)
                                        for r_vIdx in originalToUnweldedMap[vIdx]] )
                    except:
                        # unused coord
                        pass
            lines.append('            </boneassignments>')

        progress.step()
        lines.append('        </submesh>')

    lines.append('    </submeshes>')
    lines.append('    <submeshnames>')
    for objIdx, obj in enumerate(objects):
        lines.append('        <submeshname name="%s" index="%s" />' % (formatName(obj.name) if formatName(obj.name) != name else "human", objIdx))
    lines.append('    </submeshnames>')

    if human.getSkeleton():
        lines.append('    <skeletonlink name="%s.skeleton" />' % getbasefilename(filename))
    lines.append('</mesh>')

    f.write("\n".join(lines))
    f.close()


def writeSkeletonFile(human, filepath, config):
    import transformations as tm
    Pprogress = Progress(3)  # Parent.
    filename = os.path.basename(filepath)
    filename = getbasefilename(filename)
    filename = filename + ".skeleton.xml"
    filepath = os.path.join(os.path.dirname(filepath), filename)

    skel = human.getSkeleton()
    if config.scale != 1:
        skel = skel.scaled(config.scale)

    f = codecs.open(filepath, 'w', encoding="utf-8")
    lines = []

    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<!-- Exported from MakeHuman (www.makehuman.org) -->')
    lines.append('<!-- Skeleton: %s -->' % skel.name)
    lines.append('<skeleton>')
    lines.append('    <bones>')
    progress = Progress(len(skel.getBones()))
    for bIdx, bone in enumerate(skel.getBones()):
        mat = bone.getRelativeMatrix(offsetVect=config.offset)  # TODO adapt offset if mesh orientation is different

        # Bone positions are in parent bone space
        pos = mat[:3,3]

        angle, axis, _ = tm.rotation_from_matrix(mat)

        lines.append('        <bone id="%s" name="%s">' % (bIdx, bone.name))
        lines.append('            <position x="%s" y="%s" z="%s" />' % (pos[0], pos[1], pos[2]))
        lines.append('            <rotation angle="%s">' % angle)
        lines.append('                <axis x="%s" y="%s" z="%s" />' % (axis[0], axis[1], axis[2]))
        lines.append('            </rotation>')
        lines.append('        </bone>')
        progress.step()
    lines.append('    </bones>')
    Pprogress.step()

    lines.append('    <bonehierarchy>')
    progress = Progress(len(skel.getBones()))
    for bone in skel.getBones():
        if bone.parent:
            lines.append('        <boneparent bone="%s" parent="%s" />' % (bone.name, bone.parent.name))
        progress.step()
    lines.append('    </bonehierarchy>')
    Pprogress.step()

    animations = [human.getAnimation(name) for name in human.getAnimations()]
    # TODO compensate animations for alternate rest pose
    if len(animations) > 0:
        lines.append('    <animations>')
        for anim in animations:
            # Use pose matrices, not skinning matrices
            anim.resetBaked()
            #anim = bvhanim.getAnimationTrack()
            writeAnimation(human, lines, anim, config)
        lines.append('    </animations>')

    lines.append('</skeleton>')

    f.write("\n".join(lines))
    f.close()
    Pprogress.finish()


def writeMaterialFile(human, filepath, objects, config):
    progress = Progress(len(objects))
    folderpath = os.path.dirname(filepath)
    filename = getbasefilename(os.path.basename(filepath))
    name = formatName(filename)
    filename = filename + ".material"
    filepath = os.path.join(folderpath, filename)

    f = codecs.open(filepath, 'w', encoding="utf-8")
    lines = []

    for objIdx, obj in enumerate(objects):
        mat = obj.material
        if objIdx > 0:
            lines.append('')
        lines.append('material %s_%s_%s' % (name, objIdx, formatName(obj.name) if formatName(obj.name) != name else "human"))
        lines.append('{')
        lines.append('    receive_shadows %s\n' % ("on" if mat.receiveShadows else "off"))
        lines.append('    technique')
        lines.append('    {')
        lines.append('        pass')
        lines.append('        {')
        lines.append('            lighting on\n')
        lines.append('            ambient %f %f %f 1' % mat.ambientColor.asTuple())
        lines.append('            diffuse %f %f %f %f' % tuple(mat.diffuseColor.asTuple() + (mat.opacity,)))
        lines.append('            specular %f %f %f %f' % tuple(mat.specularColor.asTuple() + (128*(mat.shininess), )))
        lines.append('            emissive %f %f %f\n' % mat.emissiveColor.asTuple())

        lines.append('            depth_write %s' % ("off" if mat.transparent else "on"))
        if mat.transparent:
            lines.append('            alpha_rejection greater 128')
        lines.append('')

        textures = mat.exportTextures(os.path.join(folderpath, 'textures'))

        for textureType, texturePath in textures.items():
            if config.exportShaders:
                include = True
            else:
                include = (textureType == 'diffuseTexture')
            texfile = "textures/" + os.path.basename(texturePath)
            pre = '' if include else '//'
            lines.append('            %stexture_unit %s' % (pre, textureType))
            lines.append('            %s{' % pre)
            lines.append('            %s    texture %s' % (pre, texfile))
            lines.append('            %s}\n' % pre)

        lines.append('        }')
        lines.append('    }')
        lines.append('}')
        progress.step()

    f.write("\n".join(lines))
    f.close()

def writeAnimation(human, linebuffer, animTrack, config):
    # TODO animations need to be adapted to rest pose and retargeted to user skeleton
    import numpy as np
    progress = Progress(len(human.getSkeleton().getBones()))
    log.message("Exporting animation %s.", animTrack.name)
    linebuffer.append('        <animation name="%s" length="%s">' % (animTrack.name, animTrack.getPlaytime()))
    linebuffer.append('            <tracks>')
    I = np.identity(4, dtype=np.float32)
    axis_ = np.asarray([0,0,0,1], dtype=np.float32)
    for bIdx, bone in enumerate(human.getSkeleton().getBones()):
        # Note: OgreXMLConverter will optimize out unused (not moving) animation tracks
        linebuffer.append('                <track bone="%s">' % bone.name)
        linebuffer.append('                    <keyframes>')
        frameTime = 1.0/float(animTrack.frameRate)
        for frameIdx in xrange(animTrack.nFrames):
            poseMat = animTrack.getAtFramePos(frameIdx)[bIdx]
            I[:3,:4] = poseMat[:3,:4]
            poseMat = I
            translation = poseMat[:3,3]
            angle, axis, _ = transformations.rotation_from_matrix(poseMat)
            axis_[:3] = axis[:3]
            axis = np.asarray(axis_ * np.matrix(bone.getRestMatrix(offsetVect=config.offset)))[0]
            linebuffer.append('                        <keyframe time="%s">' % (float(frameIdx) * frameTime))
            linebuffer.append('                            <translate x="%s" y="%s" z="%s" />' % (translation[0], translation[1], translation[2]))
            # TODO account for scale
            linebuffer.append('                            <rotate angle="%s">' % angle)
            linebuffer.append('                                <axis x="%s" y="%s" z="%s" />' % (axis[0], axis[1], axis[2]))
            linebuffer.append('                            </rotate>')
            linebuffer.append('                        </keyframe>')
        linebuffer.append('                    </keyframes>')
        linebuffer.append('                </track>')
        progress.step()
    linebuffer.append('            </tracks>')
    linebuffer.append('        </animation>')



def formatName(name):
    def _goodName(name):
        return name.replace(" ", "_").replace("-","_").lower()

    if name.endswith('.mesh'):
        return _goodName(name[:-5])
    elif name.endswith('.mesh.xml'):
        return _goodName(name[:-9])
    elif name.endswith('.xml'):
        return _goodName(name[:-4])
    elif name.endswith('.obj'):
        return _goodName(name[:-4])
    else:
        return _goodName(name)

def getbasefilename(filename):
    if filename.endswith('.mesh.xml'):
        return filename[:-9]
    elif filename.endswith('.mesh'):
        return filename[:-5]
    return filename
