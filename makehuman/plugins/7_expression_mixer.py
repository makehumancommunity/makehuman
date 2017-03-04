#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius, Jonas Hauquier

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

Development tool for blending unit poses together in an expression pose.
"""

import os
import json

import algos3d
import gui3d
import animation
import bvh
import gui
import getpath
import mh
import log


# TODO make right click reset slider to 0
class ExprSlider(gui.Slider):

    def __init__(self, posename, taskview):
        super(ExprSlider, self).__init__(label=posename.capitalize(), min=0.0, max=1.0)
        self.posename = posename
        self.eventType = 'expression'
        self.taskview = taskview

    def _changed(self, value):
        #print 'caller', self
        self.callEvent('onChange', self)
        # TODO temporary
        print json.dumps(dict([(m,v) for m, v in self.taskview.modifiers.iteritems() if v != 0]))
        self.taskview.sliderChanged()

    def _changing(self, value):
        value = self._i2f(value)
        self._sync(value)
        self.changingValue = value
        self.callEvent('onChanging', self)


class TextEdit(gui.GroupBox):
    def __init__(self, name, value=""):
        super(TextEdit, self).__init__(name)
        self.edit = self.addWidget(gui.TextEdit(value))

    def setValue(self, value):
        self.edit.setText(value)

    def getValue(self):
        return self.edit.getText()


class ExpressionMixerTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Expression mixer')

        self.human = gui3d.app.selectedHuman

        self.base_bvh = None
        self.base_anim = None

        self.sliders = []
        self.modifiers = {}

        savebox = self.addRightWidget(gui.GroupBox("Save"))

        self.nameField = savebox.addWidget(TextEdit("Name"))
        self.descrField = savebox.addWidget(TextEdit("Description"))
        self.tagsField = savebox.addWidget(TextEdit("Tags (separate with ;)"))
        self.authorField = savebox.addWidget(TextEdit("Author"))
        self.copyrightField = savebox.addWidget(TextEdit("Copyright"))
        self.licenseField = savebox.addWidget(TextEdit("License"))
        self.websiteField = savebox.addWidget(TextEdit("Website"))

        lic = mh.getAssetLicense()
        self.authorField.setValue(lic.author)
        self.copyrightField.setValue(lic.copyright)
        self.licenseField.setValue(lic.license)
        self.websiteField.setValue(lic.homepage)
        self.descrField.setValue("No description set")
        self.tagsField.setValue("no tag;expression")

        self.saveBtn = savebox.addWidget(gui.BrowseButton('save', "Save pose"))
        self.saveBtn.setFilter("MakeHuman blend pose file (*.mhpose)")
        savepath = getpath.getDataPath('expressions')
        if not os.path.exists(savepath):
            os.makedirs(savepath)
        self.saveBtn.setDirectory(getpath.getDataPath('expressions'))

        @self.saveBtn.mhEvent
        def onClicked(path):
            if path:
                if not os.path.splitext(path)[1]:
                    path = path + ".mhpose"
                self.saveCurrentPose(path)

    def updatePose(self):
        posenames = []
        posevalues = []
        for pname,pval in self.modifiers.items():
            if pval != 0:
                posenames.append(pname)
                posevalues.append(pval)
        if len(posenames) == 0:
            return

        panim = self.base_poseunit.getBlendedPose(posenames, posevalues)
        panim.disableBaking = True  # Faster for realtime updating a single pose
        self.human.addAnimation(panim)
        self.human.setActiveAnimation(panim.name)
        self.human.refreshPose()

    def _load_pose_units(self):
        from collections import OrderedDict
        self.base_bvh = bvh.load(getpath.getSysDataPath('poseunits/face-poseunits.bvh'), allowTranslation="none")
        self.base_anim = self.base_bvh.createAnimationTrack(self.human.getBaseSkeleton(), name="Expression-Face-PoseUnits")

        poseunit_json = json.load(open(getpath.getSysDataPath('poseunits/face-poseunits.json'),'rb'), object_pairs_hook=OrderedDict)
        self.poseunit_names = poseunit_json['framemapping']
        log.message('unit pose frame count:%s', len(self.poseunit_names))

        self.modifiers = dict(zip(self.poseunit_names, len(self.poseunit_names)*[0.0]))
        self.base_poseunit = animation.PoseUnit(self.base_anim.name, self.base_anim.data[:self.base_anim.nBones*len(self.poseunit_names)], self.poseunit_names)

        self._load_gui()

    def _load_gui(self):
        # Create box
        box = self.addLeftWidget(gui.SliderBox("Expressions"))
        # Create sliders
        for posename in self.poseunit_names:
            slider = box.addWidget(ExprSlider(posename, self))
            @slider.mhEvent
            def onChange(event):
                slider = event
                self.modifiers[slider.posename] = slider.getValue()
                self.updatePose()

            @slider.mhEvent
            def onChanging(event):
                slider = event
                self.modifiers[slider.posename] = slider.changingValue
                self.updatePose()

            self.sliders.append(slider)

    def updateGui(self):
        for slider in self.sliders:
            slider.update()
        self.sliderChanged()

    def sliderChanged(self):
        if sum(v for m, v in self.modifiers.iteritems()) == 0:
            self.saveBtn.setEnabled(False)
        else:
            self.saveBtn.setEnabled(True)

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)

        if self.base_bvh is None:
            self._load_pose_units()

        self.updateGui()

        if gui3d.app.getSetting('cameraAutoZoom'):
            gui3d.app.setFaceCamera()


    def onHumanChanging(self, event):
        if event.change not in ['expression', 'material']:
            self.resetTargets()

    def saveCurrentPose(self, filename):
        import makehuman
        unitpose_values = dict([(m,v) for m, v in self.modifiers.iteritems() if v != 0])
        if len(unitpose_values) == 0:
            raise RuntimeError("Requires at least one pose to be specified")
        tags = [t.strip() for t in self.tagsField.getValue().split(';')]

        data = { "name": self.nameField.getValue(),
                 "description": self.descrField.getValue(),
                 "tags": tags,
                 "unit_poses": unitpose_values,
                 "author": self.authorField.getValue(),
                 "copyright": self.copyrightField.getValue(),
                 "license": self.licenseField.getValue(),
                 "homepage": self.websiteField.getValue()
                }
        json.dump(data, open(filename, 'w'), indent=4)
        log.message("Saved pose as %s" % filename)

    def resetTargets(self):
        return

        #log.debug("EXPRESSION RESET %d targets" % len(self.targets))
        if self.targets:
            human = gui3d.app.selectedHuman
            for target in self.targets:
                human.setDetail(target, 0)
            try:
                del algos3d._targetBuffer[target]
            except KeyError:
                pass
            self.targets = {}
            human.applyAllTargets()

    def onHumanChanged(self, event):
        # TODO reset?
        for slider in self.sliders:
            slider.update()


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements

def load(app):
    category = app.getCategory('Utilities')
    taskview = ExpressionMixerTaskView(category)
    taskview.sortOrder = 6
    category.addTask(taskview)


# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements

def unload(app):
    pass
