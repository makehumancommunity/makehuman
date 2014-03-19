#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers

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

TODO
"""

import codecs
import gui3d
from progress import Progress

def exportSkel(filename):

    human = gui3d.app.selectedHuman
    if not human.getSkeleton():
        gui3d.app.prompt('Error', 'You did not select a skeleton from the library.', 'OK')
        return

    f = codecs.open(filename, 'w', encoding="utf-8")

    bones = human.getSkeleton().getBones()
    gui3d.app.status("Writing Bones")

    progress = Progress()
    for bone in bones:
        writeBone(f, bone)
        progress.step()

    f.close()
    gui3d.app.status("Skeleton export finished")

def writeBone(f, bone):

    if bone.parent:
        parentIndex = bone.parent.index
    else:
        parentIndex = -1

    position = bone.getRestHeadPos()
    f.write('%d %f %f %f %d\n' % (bone.index, position[0], position[1], position[2], parentIndex))

