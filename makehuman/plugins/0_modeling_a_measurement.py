#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers

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

TODO
"""

import math
import numpy as np
import guicommon
import module3d
import humanmodifier
import gui
import log
import getpath
from core import G
import guimodifier
import language

class MeasureTaskView(guimodifier.ModifierTaskView):

    def __init__(self, category, name, label=None, saveName=None, cameraView=None):
        super(MeasureTaskView, self).__init__(category, name, label, saveName, cameraView)

        self.ruler = Ruler()
        self._createMeasureMesh()

        self.active_slider = None
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

    def addSlider(self, sliderCategory, slider, enabledCondition):
        super(MeasureTaskView, self).addSlider(sliderCategory, slider, enabledCondition)

        slider.valueConverter = MeasurementValueConverter(self, slider.modifier)

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

    def _createMeasureMesh(self):
        self.measureMesh = module3d.Object3D('measure', 2)
        self.measureMesh.createFaceGroup('measure')

        count = max([len(vertIdx) for vertIdx in self.ruler.Measures.values()])

        self.measureMesh.setCoords(np.zeros((count, 3), dtype=np.float32))
        self.measureMesh.setUVs(np.zeros((1, 2), dtype=np.float32))
        self.measureMesh.setFaces(np.arange(count).reshape((-1,2)))

        self.measureMesh.setColor([255, 255, 255, 255])
        self.measureMesh.setPickable(0)
        self.measureMesh.updateIndexBuffer()
        self.measureMesh.priority = 50

        self.measureObject = self.addObject(guicommon.Object(self.measureMesh))
        self.measureObject.setShadeless(True)
        self.measureObject.setDepthless(True)

    def showGroup(self, name):
        self.groupBoxes[name].radio.setSelected(True)
        self.groupBox.showWidget(self.groupBoxes[name])
        self.groupBoxes[name].children[0].setFocus()

    def getMeasure(self, measure):
        human = G.app.selectedHuman
        measure = self.ruler.getMeasure(human, measure, G.app.getSetting('units'))
        return measure

    def hideAllBoxes(self):
        for box in self.groupBoxes.values():
            box.hide()

    def onShow(self, event):
        super(MeasureTaskView, self).onShow(event)

        if not self.lastActive:
            self.lastActive = self.groupBoxes['Neck'].children[0]
        self.lastActive.setFocus()

        self.syncGUIStats()
        self.updateMeshes()
        human = G.app.selectedHuman

    def onHide(self, event):
        human = G.app.selectedHuman

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

        human = G.app.selectedHuman

        vertidx = self.ruler.Measures[self.active_slider.modifier.fullName]

        coords = human.meshData.coord[vertidx]
        self.measureMesh.coord[:len(vertidx),:] = coords
        self.measureMesh.coord[len(vertidx):,:] = coords[-1:]
        self.measureMesh.markCoords(coor = True)
        self.measureMesh.update()

    def onHumanChanged(self, event):
        if G.app.currentTask == self:
            self.updateMeshes()
            self.syncSliders()

    def onHumanTranslated(self, event):
        self.measureObject.setPosition(G.app.selectedHuman.getPosition())

    def onHumanRotated(self, event):
        self.measureObject.setRotation(G.app.selectedHuman.getRotation())

    def loadHandler(self, human, values, strict):
        pass

    def saveHandler(self, human, file):
        pass

    def syncGUIStats(self):
        self.syncStatistics()
        #self.syncBraSizes()

    def syncStatistics(self):
        human = G.app.selectedHuman

        height = human.getHeightCm()
        if G.app.getSetting('units') == 'metric':
            height = '%.2f cm' % height
        else:
            height = '%.2f in' % (height * 0.393700787)

        lang = language.language
        self.height.setTextFormat(lang.getLanguageString('Height') + ': %s', height)
        self.chest.setTextFormat(lang.getLanguageString('Chest') + ': %s', self.getMeasure('measure/measure-bust-circ-decr|incr'))
        self.waist.setTextFormat(lang.getLanguageString('Waist') + ': %s', self.getMeasure('measure/measure-waist-circ-decr|incr'))
        self.hips.setTextFormat(lang.getLanguageString('Hips') + ': %s', self.getMeasure('measure/measure-hips-circ-decr|incr'))

    def syncBraSizes(self):
        # TODO unused
        human = G.app.selectedHuman

        bust = self.ruler.getMeasure(human, 'measure/measure-bust-circ-decr|incr', 'metric')
        underbust = self.ruler.getMeasure(human, 'measure/measure-underbust-circ-decr|incr', 'metric')

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


class MeasurementValueConverter(object):

    def __init__(self, task, modifier):
        self.task = task
        self.modifier = modifier
        self.value = 0.0

    @property
    def units(self):
        return 'cm' if G.app.getSetting('units') == 'metric' else 'in'

    @property
    def measure(self):
        return self.modifier.fullName

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


class Ruler:

    """
  This class contains ...
  """

    def __init__(self):

        # these are tables of vertex indices for each body measurement of interest
        # TODO define in data file?

        self.Measures = {}
        self.Measures['measure/measure-neck-circ-decr|incr'] = [7514,10358,7631,7496,7488,7489,7474,7475,7531,7537,7543,7549,7555,7561,7743,7722,856,1030,1051,850,844,838,832,826,820,756,755,770,769,777,929,3690,804,800,808,801,799,803,7513,7515,7521,7514]
        self.Measures['measure/measure-neck-height-decr|incr'] = [853,854,855,856,857,858,1496,1491]


        self.Measures['measure/measure-upperarm-circ-decr|incr']=[8383,8393,8392,8391,8390,8394,8395,8399,10455,10516,8396,8397,8398,8388,8387,8386,10431,8385,8384,8389]
        self.Measures['measure/measure-upperarm-length-decr|incr'] = [8274,10037]

        self.Measures['measure/measure-lowerarm-length-decr|incr'] = [10040,10548]
        self.Measures['measure/measure-wrist-circ-decr|incr']=[10208,10211,10212,10216,10471,10533,10213,10214,10215,10205,10204,10203,10437,10202,10201,10206,10200,10210,10209,10208]

        self.Measures['measure/measure-frontchest-dist-decr|incr']=[1437,8125]
        self.Measures['measure/measure-bust-circ-decr|incr']=[8439,8455,8462,8446,8478,8494,8557,8510,8526,8542,10720,10601,10603,10602,10612,10611,10610,10613,10604,10605,10606,3942,3941,3940,3950,3947,3948,3949,3938,3939,3937,4065,1870,1854,1838,1885,1822,1806,1774,1790,1783,1767,1799,8471]
        self.Measures['measure/measure-underbust-circ-decr|incr'] = [10750,10744,10724,10725,10748,10722,10640,10642,10641,10651,10650,10649,10652,10643,10644,10645,10646,10647,10648,3988,3987,3986,3985,3984,3983,3982,3992,3989,3990,3991,3980,3981,3979,4067,4098,4073,4072,4094,4100,4082,4088, 4088]
        self.Measures['measure/measure-waist-circ-decr|incr'] = [4121,10760,10757,10777,10776,10779,10780,10778,10781,10771,10773,10772,10775,10774,10814,10834,10816,10817,10818,10819,10820,10821,4181,4180,4179,4178,4177,4176,4175,4196,4173,4131,4132,4129,4130,4128,4138,4135,4137,4136,4133,4134,4108,4113,4118,4121]
        self.Measures['measure/measure-napetowaist-dist-decr|incr']=[1491,4181]
        self.Measures['measure/measure-waisttohip-dist-decr|incr']=[4121,4341]
        self.Measures['measure/measure-shoulder-dist-decr|incr'] = [7478,8274]

        self.Measures['measure/measure-hips-circ-decr|incr'] = [4341,10968,10969,10971,10970,10967,10928,10927,10925,10926,10923,10924,10868,10875,10861,10862,4228,4227,4226,4242,4234,4294,4293,4296,4295,4297,4298,4342,4345,4346,4344,4343,4361,4341]

        self.Measures['measure/measure-upperleg-height-decr|incr'] = [10970,11230]
        self.Measures['measure/measure-thigh-circ-decr|incr'] = [11071,11080,11081,11086,11076,11077,11074,11075,11072,11073,11069,11070,11087,11085,11084,12994,11083,11082,11079,11071]

        self.Measures['measure/measure-lowerleg-height-decr|incr'] = [11225,12820]
        self.Measures['measure/measure-calf-circ-decr|incr'] = [11339,11336,11353,11351,11350,13008,11349,11348,11345,11337,11344,11346,11347,11352,11342,11343,11340,11341,11338,11339]

        self.Measures['measure/measure-ankle-circ-decr|incr'] = [11460,11464,11458,11459,11419,11418,12958,12965,12960,12963,12961,12962,12964,12927,13028,12957,11463,11461,11457,11460]
        self.Measures['measure/measure-knee-circ-decr|incr'] = [11223,11230,11232,11233,11238,11228,11229,11226,11227,11224,11225,11221,11222,11239,11237,11236,13002,11235,11234,11223]



   
        self._validate()

    def _validate(self):
        """        
        Verify currectness of ruler specification
        """
        names = []
        for n,v in self.Measures.items():
            if len(v) % 2 != 0:
                names.append(n)
        if len(names) > 0:
            raise RuntimeError("One or more measurement rulers contain an uneven number of vertex indices. It's required that they are pairs indicating the begin and end point of every line to draw. Rulers with uneven index count: %s" % ", ".join(names))

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



def load(app):
    """
    Plugin load function, needed by design.
    """
    category = app.getCategory('Modelling')

    humanmodifier.loadModifiers(getpath.getSysDataPath('modifiers/measurement_modifiers.json'), app.selectedHuman)
    guimodifier.loadModifierTaskViews(getpath.getSysDataPath('modifiers/measurement_sliders.json'), app.selectedHuman, category, taskviewClass=MeasureTaskView)


    # TODO ??
    #taskview.showGroup('neck')

def unload(app):
    pass

