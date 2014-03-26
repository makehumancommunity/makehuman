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

import os
import math
import numpy as np
import gui3d
import module3d
import humanmodifier
import modifierslider
import mh
import gui
import log

class MeasurementValueConverter(object):

    def __init__(self, task, measure, modifier):

        self.task = task
        self.measure = measure
        self.modifier = modifier
        self.value = 0.0

    @property
    def units(self):
        return 'cm' if gui3d.app.settings['units'] == 'metric' else 'in'

    def dataToDisplay(self, value):
        self.value = value
        return self.task.getMeasure(self.measure)

    def displayToData(self, value):
        goal = float(value)
        measure = self.task.getMeasure(self.measure)
        minValue = -1.0
        maxValue = 1.0
        if math.fabs(measure - goal) < 0.01:
            return self.value
        else:
            tries = 10
            while tries:
                if math.fabs(measure - goal) < 0.01:
                    break;
                if goal < measure:
                    maxValue = self.value
                    if value == minValue:
                        break
                    self.value = minValue + (self.value - minValue) / 2.0
                    self.modifier.updateValue(self.value, 0)
                    measure = self.task.getMeasure(self.measure)
                else:
                    minValue = self.value
                    if value == maxValue:
                        break
                    self.value = self.value + (maxValue - self.value) / 2.0
                    self.modifier.updateValue(self.value, 0)
                    measure = self.task.getMeasure(self.measure)
                tries -= 1
        return self.value

class GroupBoxRadioButton(gui.RadioButton):
    def __init__(self, task, group, label, groupBox, selected=False):
        super(GroupBoxRadioButton, self).__init__(group, label, selected)
        self.groupBox = groupBox
        self.task = task

    def onClicked(self, event):
        self.task.groupBox.showWidget(self.groupBox)
        self.task.onSliderFocus(self.groupBox.children[0])

class MeasureTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Measure')

        self.ruler = Ruler()

        self.measureMesh = module3d.Object3D('measure', 2)
        self.measureMesh.createFaceGroup('measure')

        names = []
        for n,v in self.ruler.Measures.items():
            if len(v) % 2 != 0:
                names.append(n)
        if len(names) > 0:
            raise RuntimeError("One or more measurement rulers contain an uneven number of vertex indices. It's required that they are pairs indicating the begin and end point of every line to draw. Rulers with uneven index count: %s" % ", ".join(names))
        del names
        count = max([len(vertIdx) for vertIdx in self.ruler.Measures.values()])

        self.measureMesh.setCoords(np.zeros((count, 3), dtype=np.float32))
        self.measureMesh.setUVs(np.zeros((1, 2), dtype=np.float32))
        self.measureMesh.setFaces(np.arange(count).reshape((-1,2)))

        self.measureMesh.setCameraProjection(0)
        self.measureMesh.setShadeless(True)
        self.measureMesh.setDepthless(True)
        self.measureMesh.setColor([255, 255, 255, 255])
        self.measureMesh.setPickable(0)
        self.measureMesh.updateIndexBuffer()
        self.measureMesh.priority = 50

        self.measureObject = self.addObject(gui3d.Object(self.measureMesh))

        measurements = [
            ('neck', ['neckcirc', 'neckheight']),
            ('upperarm', ['upperarm', 'upperarmlenght']),
            ('lowerarm', ['lowerarmlenght', 'wrist']),
            ('torso', ['frontchest', 'bust', 'underbust', 'waist', 'napetowaist', 'waisttohip', 'shoulder']),
            ('hips', ['hips']),
            ('upperleg', ['upperlegheight', 'thighcirc']),
            ('lowerleg', ['lowerlegheight', 'calf']),
            ('ankle', ['ankle']),
        ]

        sliderLabel = {
            'neckcirc':'Neck circum',
            'neckheight':'Neck height',
            'upperarm':'Upper arm circum',
            'upperarmlenght':'Upperarm length',
            'lowerarmlenght':'Lowerarm length',
            'wrist':'Wrist circum',
            'frontchest':'Front chest dist',
            'bust':'Bust circum',
            'underbust':'Underbust circum',
            'waist':'Waist circum',
            'napetowaist':'Nape to waist',
            'waisttohip':'Waist to hip',
            'shoulder':'Shoulder dist',
            'hips':'Hips circum',
            'upperlegheight':'Upperleg height',
            'thighcirc':'Thigh circ.',
            'lowerlegheight':'Lowerleg height',
            'calf':'Calf circum',
            'ankle':'Ankle circum'
        }

        self.groupBoxes = {}
        self.radioButtons = []
        self.sliders = []
        self.active_slider = None

        self.modifiers = {}

        measureDataPath = mh.getSysDataPath("targets/measure/")

        self.categoryBox = self.addRightWidget(gui.GroupBox('Category'))
        self.groupBox = self.addLeftWidget(gui.StackedBox())

        for name, subnames in measurements:
            # Create box
            box = self.groupBox.addWidget(gui.SliderBox(name.capitalize()))
            self.groupBoxes[name] = box

            # Create radiobutton
            box.radio = self.categoryBox.addWidget(GroupBoxRadioButton(self, self.radioButtons, name.capitalize(), box, selected=len(self.radioButtons) == 0))

            # Create sliders
            for subname in subnames:
                # TODO use another modifier
                modifier = humanmodifier.Modifier(
                    os.path.join(measureDataPath, "measure-%s-decrease.target" % subname),
                    os.path.join(measureDataPath, "measure-%s-increase.target" % subname))
                modifier.setHuman(gui3d.app.selectedHuman)
                self.modifiers[subname] = modifier
                slider = box.addWidget(modifierslider.ModifierSlider(modifier, sliderLabel[subname], MeasurementValueConverter(self, subname, modifier)))
                slider.measure = subname
                @slider.mhEvent
                def onBlur(event):
                    slider = event
                    self.onSliderBlur(slider)
                @slider.mhEvent
                def onFocus(event):
                    slider = event
                    self.onSliderFocus(slider)
                @slider.mhEvent
                def onChange(event):
                    self.syncGUIStats()
                self.sliders.append(slider)
        self.lastActive = None

        self.statsBox = self.addRightWidget(gui.GroupBox('Statistics'))
        self.height = self.statsBox.addWidget(gui.TextView('Height: '))
        self.chest = self.statsBox.addWidget(gui.TextView('Chest: '))
        self.waist = self.statsBox.addWidget(gui.TextView('Waist: '))
        self.hips = self.statsBox.addWidget(gui.TextView('Hips: '))

        '''
        self.braBox = self.addRightWidget(gui.GroupBox('Brassiere size'))
        self.eu = self.braBox.addWidget(gui.TextView('EU: '))
        self.jp = self.braBox.addWidget(gui.TextView('JP: '))
        self.us = self.braBox.addWidget(gui.TextView('US: '))
        self.uk = self.braBox.addWidget(gui.TextView('UK: '))
        '''

        self.groupBox.showWidget(self.groupBoxes['neck'])

    def showGroup(self, name):
        self.groupBoxes[name].radio.setSelected(True)
        self.groupBox.showWidget(self.groupBoxes[name])
        self.groupBoxes[name].children[0].setFocus()

    def getMeasure(self, measure):

        human = gui3d.app.selectedHuman
        measure = self.ruler.getMeasure(human, measure, gui3d.app.settings['units'])
        return measure

    def hideAllBoxes(self):

        for box in self.groupBoxes.values():
            box.hide()

    def onShow(self, event):

        gui3d.TaskView.onShow(self, event)
        if not self.lastActive:
            self.lastActive = self.groupBoxes['neck'].children[0]
        self.lastActive.setFocus()

        self.syncSliders()
        self.syncGUIStats()
        self.updateMeshes()
        human = gui3d.app.selectedHuman
        self.cloPickableProps = dict()
        for uuid, pxy in human.clothesProxies.items():
            obj = pxy.object
            self.cloPickableProps[uuid] = clo.mesh.pickable
            clo.mesh.setPickable(False)

    def onHide(self, event):
        human = gui3d.app.selectedHuman
        for uuid, pickable in self.cloPickableProps.items():
            pxy = human.clothesProxies[uuid]
            pxy.object.mesh.setPickable(pickable)

    def onSliderFocus(self, slider):
        self.lastActive = slider
        self.active_slider = slider
        self.updateMeshes()
        self.measureObject.show()

    def onSliderBlur(self, slider):
        self.lastActive = slider
        if self.active_slider is slider:
            self.active_slider = None
        self.measureObject.hide()

    def updateMeshes(self):
        if self.active_slider is None:
            return

        human = gui3d.app.selectedHuman

        vertidx = self.ruler.Measures[self.active_slider.measure]

        coords = human.meshData.coord[vertidx]
        self.measureMesh.coord[:len(vertidx),:] = coords
        self.measureMesh.coord[len(vertidx):,:] = coords[-1:]
        self.measureMesh.markCoords(coor = True)
        self.measureMesh.update()

    def onHumanChanged(self, event):
        if gui3d.app.currentTask == self:
            self.updateMeshes()
            self.syncSliders()

    def onHumanTranslated(self, event):

        self.measureObject.setPosition(gui3d.app.selectedHuman.getPosition())

    def onHumanRotated(self, event):

        self.measureObject.setRotation(gui3d.app.selectedHuman.getRotation())

    def syncSliders(self):
        for slider in self.sliders:
            slider.update()

    def syncGUIStats(self):
        self.syncStatistics()
        #self.syncBraSizes()

    def syncStatistics(self):

        human = gui3d.app.selectedHuman

        height = human.getHeightCm()
        if gui3d.app.settings['units'] == 'metric':
            height = '%.2f cm' % height
        else:
            height = '%.2f in' % (height * 0.393700787)

        self.height.setTextFormat('Height: %s', height)
        self.chest.setTextFormat('Chest: %s', self.getMeasure('bust'))
        self.waist.setTextFormat('Waist: %s', self.getMeasure('waist'))
        self.hips.setTextFormat('Hips: %s', self.getMeasure('hips'))

    def syncBraSizes(self):

        human = gui3d.app.selectedHuman

        bust = self.ruler.getMeasure(human, 'bust', 'metric')
        underbust = self.ruler.getMeasure(human, 'underbust', 'metric')

        eucups = ['AA', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']

        mod = int(underbust)%5
        band = underbust - mod if mod < 2.5 else underbust - mod + 5
        cup = min(max(0, int(round(((bust - underbust - 10) / 2)))), len(eucups)-1)
        self.eu.setTextFormat('EU: %d%s', band, eucups[cup])

        jpcups = ['AAA', 'AA', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']

        mod = int(underbust)%5
        band = underbust - mod if mod < 2.5 else underbust - mod + 5
        cup = min(max(0, int(round(((bust - underbust - 5) / 2.5)))), len(jpcups)-1)
        self.jp.setTextFormat('JP: %d%s', band, jpcups[cup])

        uscups = ['AA', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']

        band = underbust * 0.393700787
        band = band + 5 if int(band)%2 else band + 4
        cup = min(max(0, int(round((bust - underbust - 10) / 2))), len(uscups)-1)
        self.us.setTextFormat('US: %d%s', band, uscups[cup])

        ukcups = ['AA', 'A', 'B', 'C', 'D', 'DD', 'E', 'F', 'FF', 'G', 'GG', 'H']

        self.uk.setTextFormat('UK: %d%s', band, ukcups[cup])

    def loadHandler(self, human, values):
        if values[0] == 'status':
            return

        modifier = self.modifiers.get(values[1], None)
        if modifier:
            modifier.setValue(float(values[2]))

    def saveHandler(self, human, file):

        for name, modifier in self.modifiers.iteritems():
            value = modifier.getValue()
            if value:
                file.write('measure %s %f\n' % (name, value))

def load(app):
    """
    Plugin load function, needed by design.
    """
    category = app.getCategory('Modelling')
    taskview = category.addTask(MeasureTaskView(category))

    app.addLoadHandler('measure', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)

    @taskview.mhEvent
    def onMouseDown(event):
        part = app.getSelectedFaceGroup()
        bodyZone = app.selectedHuman.getPartNameForGroupName(part.name)
        log.message("body zone %s", bodyZone)
        if bodyZone in app.selectedHuman.bodyZones:
            if bodyZone == "neck":
                taskview.showGroup('neck')
            elif (bodyZone == "r-upperarm") or (bodyZone == "l-upperarm"):
                taskview.showGroup('upperarm')
            elif (bodyZone == "r-lowerarm") or (bodyZone == "l-lowerarm"):
                taskview.showGroup('lowerarm')
            elif (bodyZone == "torso") or (bodyZone == "pelvis"):
                taskview.showGroup('torso')
            elif bodyZone == "hip":
                taskview.showGroup('hips')
            elif (bodyZone == "l-upperleg") or (bodyZone == "r-upperleg"):
                taskview.showGroup('upperleg')
            elif (bodyZone == "l-lowerleg") or (bodyZone == "r-lowerleg"):
                taskview.showGroup('lowerleg')
            elif (bodyZone == "l-foot") or (bodyZone == "r-foot"):
                taskview.showGroup('ankle')

    taskview.showGroup('neck')

def unload(app):
    pass

class Ruler:

    """
  This class contains ...
  """

    def __init__(self):

    # these are tables of vertex indices for each body measurement of interest

        self.Measures = {}
        self.Measures['thighcirc'] = [11071,11080,11081,11086,11076,11077,11074,11075,11072,11073,11069,11070,11087,11085,11084,12994,11083,11082,11079,11071]
        self.Measures['neckcirc'] = [7514,10358,7631,7496,7488,7489,7474,7475,7531,7537,7543,7549,7555,7561,7743,7722,856,1030,1051,850,844,838,832,826,820,756,755,770,769,777,929,3690,804,800,808,801,799,803,7513,7515,7521,7514]
        self.Measures['neckheight'] = [853,854,855,856,857,858,1496,1491]

        self.Measures['upperarm']=[8383,8393,8392,8391,8390,8394,8395,8399,10455,10516,8396,8397,8398,8388,8387,8386,10431,8385,8384,8389]
        self.Measures['wrist']=[10208,10211,10212,10216,10471,10533,10213,10214,10215,10205,10204,10203,10437,10202,10201,10206,10200,10210,10209,10208]
        self.Measures['frontchest']=[1437,8125]
        self.Measures['bust']=[8439,8455,8462,8446,8478,8494,8557,8510,8526,8542,10720,10601,10603,10602,10612,10611,10610,10613,10604,10605,10606,3942,3941,3940,3950,3947,3948,3949,3938,3939,3937,4065,1870,1854,1838,1885,1822,1806,1774,1790,1783,1767,1799,8471]
        self.Measures['napetowaist']=[1491,4181]
        self.Measures['waisttohip']=[4121,4341]
        self.Measures['shoulder'] = [7478,8274]
        self.Measures['underbust'] = [10750,10744,10724,10725,10748,10722,10640,10642,10641,10651,10650,10649,10652,10643,10644,10645,10646,10647,10648,3988,3987,3986,3985,3984,3983,3982,3992,3989,3990,3991,3980,3981,3979,4067,4098,4073,4072,4094,4100,4082,4088, 4088]
        self.Measures['waist'] = [4121,10760,10757,10777,10776,10779,10780,10778,10781,10771,10773,10772,10775,10774,10814,10834,10816,10817,10818,10819,10820,10821,4181,4180,4179,4178,4177,4176,4175,4196,4173,4131,4132,4129,4130,4128,4138,4135,4137,4136,4133,4134,4108,4113,4118,4121]
        self.Measures['upperlegheight'] = [10970,11230]
        self.Measures['lowerlegheight'] = [11225,12820]
        self.Measures['calf'] = [11339,11336,11353,11351,11350,13008,11349,11348,11345,11337,11344,11346,11347,11352,11342,11343,11340,11341,11338,11339]
        self.Measures['ankle'] = [11460,11464,11458,11459,11419,11418,12958,12965,12960,12963,12961,12962,12964,12927,13028,12957,11463,11461,11457,11460]
        self.Measures['upperarmlenght'] = [8274,10037]
        self.Measures['lowerarmlenght'] = [10040,10548]
        self.Measures['hips'] = [4341,10968,10969,10971,10970,10967,10928,10927,10925,10926,10923,10924,10868,10875,10861,10862,4228,4227,4226,4242,4234,4294,4293,4296,4295,4297,4298,4342,4345,4346,4344,4343,4361,4341]


    def getMeasure(self, human, measurementname, mode):
        measure = 0
        vindex1 = self.Measures[measurementname][0]
        for vindex2 in self.Measures[measurementname]:
            vec = human.meshData.coord[vindex1] - human.meshData.coord[vindex2]
            measure += math.sqrt(vec.dot(vec))
            vindex1 = vindex2

        if mode == 'metric':
            return 10.0 * measure
        else:
            return 10.0 * measure * 0.393700787
