#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

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

        # Add event listeners to skeleton mesh for bone highlighting
        @mainLib.mhEvent
        def onMouseEntered(event):
            """
            Event fired when mouse hovers over a skeleton mesh facegroup
            """
            gui3d.TaskView.onMouseEntered(self, event)
            mainLib.removeBoneHighlights()
            mainLib.highlightBone(event.group.name)

        @mainLib.mhEvent
        def onMouseExited(event):
            """
            Event fired when mouse hovers off of a skeleton mesh facegroup
            """
            gui3d.TaskView.onMouseExited(self, event)
            mainLib.removeBoneHighlights()

            # Highlight bone selected in bone explorer again
            for rdio in self.boneSelector:
                if rdio.selected:
                    mainLib.clearBoneWeights()
                    mainLib.highlightBone(str(rdio.text()))

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


