#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

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

