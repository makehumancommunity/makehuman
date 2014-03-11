#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

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
        if image is not None:
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
            # Right clicking reset the slider to default position
            if self.modifier.getValue() == self.modifier.getDefaultValue():
                return False

            # Reset slider to default action
            import humanmodifier
            G.app.do(humanmodifier.ModifierAction(self.modifier, 
                                                  self.modifier.getValue(), 
                                                  self.modifier.getDefaultValue(), 
                                                  self.update))
            return False
        else:
            # Default behaviour
            return True

    def onChanging(self, value):
        if self.changing is not None:
            self.changing = value
            return
        self.changing = value
        G.app.callAsync(self._onChanging)

    def _onChanging(self):
        value = self.changing
        self.changing = None

        if G.app.settings.get('realtimeUpdates', True):
            human = G.app.selectedHuman
            if self.value is None:
                self.value = self.modifier.getValue()
                if human.isSubdivided():
                    if human.isProxied():
                        human.getProxyMesh().setVisibility(1)
                    else:
                        human.getSeedMesh().setVisibility(1)
                    human.getSubdivisionMesh(False).setVisibility(0)
            self.modifier.updateValue(value, G.app.settings.get('realtimeNormalUpdates', True))
            human.updateProxyMesh()  # Is this not too slow?


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
        if self.value != value:
            G.app.do(humanmodifier.ModifierAction(self.modifier, self.value, value, self.update))
        else:
            # Indicate that onChanging event is ended with onChanged event (type == 'modifier', not 'targets')
            import events3d
            event = events3d.HumanEvent(human, self.modifier.eventType)
            event.modifier = self.modifier.fullName
            human.callEvent('onChanged', event)
        if human.isSubdivided():
            if human.isProxied():
                human.getProxyMesh().setVisibility(0)
            else:
                human.getSeedMesh().setVisibility(0)
            human.getSubdivisionMesh(False).setVisibility(1)
        self.value = None

    def onRelease(self, w):
        G.app.callAsync(self._onChange)
        #self._onChange()

    def onFocus(self, event):
        if self.view:
            if G.app.settings.get('cameraAutoZoom', True):
                self.view()

    def update(self):
        """Synchronize slider value with value of its modifier, make it up to
        date.
        """
        human = G.app.selectedHuman
        self.blockSignals(True)
        if not self.slider.isSliderDown():
            # Only update slider position when it is not being clicked or dragged
            self.setValue(self.modifier.getValue())
        self.blockSignals(False)

