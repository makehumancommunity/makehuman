#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2015

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

Animation export

"""

import log
import numpy as np
import numpy.linalg as la
import transformations as tm
from .dae_node import goodBoneName

#----------------------------------------------------------------------
#   library_animations
#----------------------------------------------------------------------

def writeLibraryAnimations(fp, human, config):
    return

    # TODO allow exporting poseunits
    skel = human.getSkeleton()
    if (skel is None or
        not config.useFaceRig):
        return

    fp.write('\n  <library_animations>\n')
    action,_ = loadAction()
    for bname in action.keys():
        bone = skel.getBone(bname)
        writeAnimation(fp, bone, action, config)
    fp.write('  </library_animations>\n')


def writeAnimation(fp, bone, action, config):
    aname = "Action_%s" % goodBoneName(bone.name)
    points = action[bone.name]
    npoints = len(points)

    fp.write(
        '    <animation id="%s_pose_matrix">\n' % aname +
        '      <source id="%s_pose_matrix-input">\n' % aname +
        '        <float_array id="%s_pose_matrix-input-array" count="%d">' % (aname, npoints))

    fp.write(''.join([" %g" % (0.04*(t+1)) for t in range(npoints)]))

    fp.write(
        '</float_array>\n' +
        '        <technique_common>\n' +
        '          <accessor source="#%s_pose_matrix-input-array" count="%d" stride="1">\n' % (aname, npoints) +
        '            <param name="TIME" type="float"/>\n' +
        '          </accessor>\n' +
        '        </technique_common>\n' +
        '      </source>\n' +
        '      <source id="%s_pose_matrix-output">\n' % aname +
        '        <float_array id="%s_pose_matrix-output-array" count="%d">\n' % (aname, 16*npoints))

    string = '          '
    relmat = bone.getRelativeMatrix(config.meshOrientation, config.localBoneAxis, config.offset)
    for quat in points:
        mat0 = tm.quaternion_matrix(quat)
        mat = np.dot(relmat, mat0)
        string += ''.join(['%g %g %g %g  ' % tuple(mat[i,:]) for i in range(4)])
        string += '\n          '
    fp.write(string)

    fp.write(
        '</float_array>\n' +
        '        <technique_common>\n' +
        '          <accessor source="#%s_pose_matrix-output-array" count="%d" stride="16">\n' % (aname, npoints) +
        '            <param name="TRANSFORM" type="float4x4"/>\n' +
        '          </accessor>\n' +
        '        </technique_common>\n' +
        '      </source>\n' +
        '      <source id="%s_pose_matrix-interpolation">\n' % aname +
        '        <Name_array id="%s_pose_matrix-interpolation-array" count="%d">' % (aname, npoints))

    fp.write(npoints * 'LINEAR ')

    fp.write(
        '</Name_array>\n' +
        '        <technique_common>\n' +
        '          <accessor source="#%s_pose_matrix-interpolation-array" count="%d" stride="1">\n' % (aname, npoints) +
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
