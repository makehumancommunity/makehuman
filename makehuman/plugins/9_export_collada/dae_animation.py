#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

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

Animation export

"""

import log
import numpy as np
import numpy.linalg as la
import transformations as tm
from .dae_node import goodBoneName
import animation

#----------------------------------------------------------------------
#   library_animations
#----------------------------------------------------------------------

def writeLibraryAnimations(fp, human, skel, animations, config):
    if skel is None:
        return

    # Use pose matrices, not skinning matrices
    for anim in animations:
        anim.resetBaked()

    joined_anim = animations[0]
    for anim in animations[1:]:
        print 'join anims'
        joined_anim = animation.joinAnimations(joined_anim, anim)

    fp.write('\n  <library_animations>\n')
    writeAnimation(fp, skel, joined_anim, config)
    fp.write('  </library_animations>\n')

    # Write animation clips (not supported by all importers)
    fp.write('\n  <library_animation_clips>\n')
    timeOffset = 0.0
    for anim in animations:
        fp.write('    <animation_clip id="AnimationClip_%s" name="%s" start="%.3f" end="%.3f">\n' % (anim.name, anim.name, timeOffset, timeOffset+anim.getPlaytime()))
        for bone in skel.getBones():
            aname = "Anim_%s_%s" % (joined_anim.name, goodBoneName(bone.name))
            fp.write('      <instance_animation url="#%s_pose_matrix"/>\n' % aname)
        fp.write('    </animation_clip>\n')
        # TODO it's also possible to export animations to separate files:
        #    <animation_clip="name" name="name">
        #      <instance_animation url="file://animation_file.dae#animationName"/>
        #    </animation_clip>
        timeOffset += anim.getPlaytime()
    fp.write('\n  </library_animation_clips>\n')

def writeAnimation(fp, skel, anim, config):
    for bIdx, bone in enumerate(skel.getBones()):
        writeAnimationBone(fp, bone, anim, config)

def writeAnimationBone(fp, bone, anim, config):
    aname = "Anim_%s_%s" % (anim.name, goodBoneName(bone.name))

    fp.write(
        '    <animation id="%s_pose_matrix">\n' % aname +
        '      <source id="%s_pose_matrix-input">\n' % aname +
        '        <float_array id="%s_pose_matrix-input-array" count="%d">' % (aname, anim.nFrames))

    # TIME POINTS
    timepoints = np.asarray(range(anim.nFrames), dtype=np.float32) * (1.0/anim.frameRate)
    fp.write(' '.join(["%g" % t for t in timepoints]))

    fp.write(
        '</float_array>\n' +
        '        <technique_common>\n' +
        '          <accessor source="#%s_pose_matrix-input-array" count="%d" stride="1">\n' % (aname, anim.nFrames) +
        '            <param name="TIME" type="float"/>\n' +
        '          </accessor>\n' +
        '        </technique_common>\n' +
        '      </source>\n' +
        '      <source id="%s_pose_matrix-output">\n' % aname +
        '        <float_array id="%s_pose_matrix-output-array" count="%d">\n' % (aname, 16*anim.nFrames))

    string = '          '
    relmat = bone.getRelativeMatrix(config.meshOrientation, config.localBoneAxis, config.offset)
    restmat = bone.getRestMatrix(config.meshOrientation, config.localBoneAxis, config.offset)
    #print bone.index, anim.nBones
    mats = anim.data[bone.index::anim.nBones]  # Get all pose matrices for this bone
    I = np.identity(4, dtype=np.float32)
    parents = []
    bone_ = bone
    while bone_.parent:
        relmat = bone_.parent.getRelativeMatrix(config.meshOrientation, config.localBoneAxis, config.offset)
        parents.append((bone_.parent.index, relmat))
        bone_ = bone_.parent
    for f_idx, mat0 in enumerate(mats):
        # TODO poses currently only work for default local bone axis
        #I[:3,:4] = mat0[:3,:4]
        #relmat[:3,:3] = np.identity(3, dtype=np.float32)
        #if 'clavicle' in bone.name or 'shoulder' in bone.name:
        #if bone.level < 6:
        #    I = np.identity(4, dtype=np.float32)
        #mat = np.dot(relmat, I)
        '''
        mat = I.copy()
        for b_idx in reversed(parents):
            I[:3,:4] = anim.data[f_idx * anim.nBones + b_idx]
            #mat = np.dot(np.dot(relmat, I), mat)
            mat = np.dot(mat,la.inv(I))
        mat = np.dot(relmat, mat)
        '''

        mat = np.identity(4, dtype=np.float32)
        for b_idx, rel in reversed(parents):
            #rel = parent.getRelativeMatrix(config.meshOrientation, config.localBoneAxis, config.offset)
            #b_idx = parent.index
            I[:3,:4] = anim.data[f_idx * anim.nBones + b_idx]
            #mat = np.dot(la.inv(rel), np.dot(mat, np.dot(rel, I)))
            #mat = np.dot(mat, I)
            mat = np.dot(I, mat)

        I[:3,:4] = mat0[:3,:4]
        mat = np.dot(mat, np.dot(relmat, I))

        '''
        if self.parent:
            self.matPoseGlobal = np.dot(self.parent.matPoseGlobal, np.dot(self.matRestRelative, self.matPose))
        else:
            self.matPoseGlobal = np.dot(self.matRestRelative, self.matPose)
        '''

        '''
        # R * K * iR * R_dae = M
        mat = np.dot(la.inv(relmat), restmat)
        mat = np.dot(I, mat)
        mat = np.dot(relmat, I)
        '''

        string += ''.join(['%g %g %g %g  ' % tuple(mat[i,:]) for i in range(4)])
        string += '\n          '
    fp.write(string)
    def _to_degrees(rad):
        return 180*rad/3.14
    I = np.identity(4, dtype=np.float32)
    I[:3,:3] = mats[0,:3,:3]
    print bone.name, map(_to_degrees, tm.euler_from_matrix(I))

    fp.write(
        '</float_array>\n' +
        '        <technique_common>\n' +
        '          <accessor source="#%s_pose_matrix-output-array" count="%d" stride="16">\n' % (aname, anim.nFrames) +
        '            <param name="TRANSFORM" type="float4x4"/>\n' +
        '          </accessor>\n' +
        '        </technique_common>\n' +
        '      </source>\n' +
        '      <source id="%s_pose_matrix-interpolation">\n' % aname +
        '        <Name_array id="%s_pose_matrix-interpolation-array" count="%d">' % (aname, anim.nFrames))

    fp.write(anim.nFrames * 'LINEAR ')

    fp.write(
        '</Name_array>\n' +
        '        <technique_common>\n' +
        '          <accessor source="#%s_pose_matrix-interpolation-array" count="%d" stride="1">\n' % (aname, anim.nFrames) +
        '            <param name="INTERPOLATION" type="name"/>\n' +
        '          </accessor>\n' +
        '        </technique_common>\n' +
        '      </source>\n' +
        '      <sampler id="%s_pose_matrix-sampler">\n' % aname +
        '        <input semantic="INPUT" source="#%s_pose_matrix-input"/>\n' % aname +
        '        <input semantic="OUTPUT" source="#%s_pose_matrix-output"/>\n' % aname +
        '        <input semantic="INTERPOLATION" source="#%s_pose_matrix-interpolation"/>\n' % aname +
        '      </sampler>\n' +
        '      <channel source="#%s_pose_matrix-sampler" target="%s/transform"/>\n' % (aname, goodBoneName(bone.name)) +
        '    </animation>\n')
