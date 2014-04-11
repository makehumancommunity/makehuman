#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

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

Skeleton library.
Allows a selection of skeletons which can be exported with the MH character.
Skeletons are used for skeletal animation (skinning) and posing.
"""

from collections import OrderedDict

import mh
import gui
import gui3d
import armature

#------------------------------------------------------------------------------------------
#   class SkeletonDebugLibrary
#------------------------------------------------------------------------------------------

class SkeletonDebugLibrary(gui3d.TaskView):

    def __init__(self, category, mainLib):
        gui3d.TaskView.__init__(self, category, 'Skeleton Debug')
        self.mainLib = mainLib
        mainLib.debugLib = self

        '''
        displayBox = mainLib.displayBox
        mainLib.showWeightsTggl = displayBox.addWidget(gui.CheckBox("Show bone weights"))
        @mainLib.showWeightsTggl.mhEvent
        def onClicked(event):
            if mainLib.showWeightsTggl.selected:
                # Highlight bone selected in bone explorer again
                for rdio in self.boneSelector:
                    if rdio.selected:
                        mainLib.highlightBone(str(rdio.text()))
            else:
                mainLib.clearBoneWeights()
        mainLib.showWeightsTggl.setSelected(True)
        '''

        self.boneBox = self.addRightWidget(gui.GroupBox('Bones'))
        self.boneSelector = []

        #
        #   Options. For fine-tuning
        #
        self.optionsBox = self.addLeftWidget(gui.GroupBox('Rig Options'))
        selector = mainLib.optionsSelector = armature.options.ArmatureSelector(self.optionsBox)
        selector.fromOptions(mainLib.amtOptions)

        self.amtUpdateBtn = self.optionsBox.addWidget(gui.Button("Update Bones"))
        @self.amtUpdateBtn.mhEvent
        def onClicked(event):
            mainLib.updateSkeleton()
            mainLib.descrLbl.setText("No description available")


    def reloadBoneExplorer(self):
        # Remove old radio buttons
        for radioBtn in self.boneSelector:
            radioBtn.hide()
            radioBtn.destroy()
        self.boneSelector = []

        human = self.mainLib.human
        skel = human.getSkeleton()
        if not skel:
            return

        for bone in skel.getBones():
            radioBtn = self.boneBox.addWidget(gui.RadioButton(self.boneSelector, bone.name))
            @radioBtn.mhEvent
            def onClicked(event):
                for rdio in self.boneSelector:
                    if rdio.selected:
                        self.mainLib.removeBoneHighlights()
                        self.mainLib.highlightBone(str(rdio.text()))


    def onShow(self, event):
        self.mainLib.onShow(event)

    def onHide(self, event):
        self.mainLib.onHide(event)


