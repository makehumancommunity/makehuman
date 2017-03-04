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

GUI slider widgets for controlling modifiers.
"""

import gui
import targets
import os
from core import G

class ModifierSlider(gui.Slider):

    def __init__(self, modifier, label=None, valueConverter=None, image=None, cameraView=None):
        if label is None:
            # Guess a suitable slider label from target name
            tlabel = modifier.name.split('-')
            if "|" in tlabel[len(tlabel)-1]:
                tlabel = tlabel[:-1]
            if len(tlabel) > 1 and tlabel[0] == modifier.groupName:
                label = tlabel[1:]
            else:
                label = tlabel
            label = ' '.join([word.capitalize() for word in label])

        if image is None:
            tlabel = modifier.name.replace('|', '-').split('-')
            # Guess a suitable image path from target name
            image = ('%s.png' % '-'.join(tlabel)).lower()
        if not os.path.isfile(image):
            image = self.findImage(image)
        if not os.path.isfile(image):
            image = None

        super(ModifierSlider, self).__init__(modifier.getValue(), modifier.getMin(), modifier.getMax(), label, valueConverter=valueConverter, image=image)
        self.modifier = modifier
        self.value = None
        self.changing = None
        if cameraView:
            self.view = getattr(G.app, cameraView)
        else:
            self.view = None


    @staticmethod
    def findImage(name):
        if name is None:
            return None
        name = name.lower()
        return targets.getTargets().images.get(name, name)

    def mousePressEvent(self, event):
        if self._handleMousePress(event):
            super(ModifierSlider, self).mousePressEvent(event)

    def sliderMousePressEvent(self, event):
        return self._handleMousePress(event)

    def _handleMousePress(self, event):
        if event.button() == gui.QtCore.Qt.RightButton:
            self.resetValue()
            return False
        else:
            # Default behaviour
            return True

    def resetValue(self):
        """
        Reset value of slider to default.
        """
        # Right clicking reset the slider to default position
        if self.modifier.getValue() == self.modifier.getDefaultValue():
            return False

        # Reset slider to default action
        import humanmodifier
        G.app.do(humanmodifier.ModifierAction(self.modifier, 
                                              self.modifier.getValue(), 
                                              None,  # Reset 
                                              self.update))

    def onChanging(self, value):
        if self.changing is not None:
            # Avoid concurrent updates
            self.changing = value
            return
        self.changing = value
        G.app.callAsync(self._onChanging)

    def _onChanging(self):
        value = self.changing
        self.changing = None

        if G.app.getSetting('realtimeUpdates'):
            human = G.app.selectedHuman
            if self.value is None:
                self.value = self.modifier.getValue()
                if human.isSubdivided():
                    if human.isProxied():
                        human.getProxyMesh().setVisibility(1)
                    else:
                        human.getSeedMesh().setVisibility(1)
                    human.getSubdivisionMesh(False).setVisibility(0)
            self.modifier.updateValue(value, G.app.getSetting('realtimeNormalUpdates'))
            human.updateProxyMesh(fit_to_posed=True, fast=True)


    def onChange(self, value):
        #G.app.callAsync(self._onChange)
        pass

    def _onChange(self):
        import humanmodifier

        if self.slider.isSliderDown():
            # Don't do anything when slider is being clicked or dragged (onRelease triggers it)
            return

        value = self.getValue()
        human = self.modifier.human
        if self.value is None:
            self.value = self.modifier.getValue()
        action = humanmodifier.ModifierAction(self.modifier, self.value, value, self.update)
        if self.value != value:
            G.app.do(action)
        else:
            # Apply the change anyway, to make sure everything's updated
            # Perform the action without adding it to the undo stack
            action.do()

        if human.isSubdivided():
            if human.isProxied():
                human.getProxyMesh().setVisibility(0)
            else:
                human.getSeedMesh().setVisibility(0)
            human.getSubdivisionMesh(False).setVisibility(1)
        self.value = None

    def onRelease(self, w):
        G.app.callAsync(self._onChange)

    def onFocus(self, event):
        if self.view:
            if G.app.getSetting('cameraAutoZoom'):
                self.view()

    def update(self):
        """Synchronize slider value with value of its modifier, make it up to
        date.
        """
        self.blockSignals(True)
        if not self.slider.isSliderDown():
            # Only update slider position when it is not being clicked or dragged
            self.setValue(self.modifier.getValue())
        self.blockSignals(False)

