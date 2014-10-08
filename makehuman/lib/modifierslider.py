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

GUI slider widgets for controlling modifiers.
"""

import gui
import targets
import os
from core import G

class ModifierSlider(gui.Slider):

    def __init__(self, value=0.0, min=0.0, max=1.0, label=None, modifier=None, valueConverter=None, image=None):
        super(ModifierSlider, self).__init__(value, min, max, label, valueConverter=valueConverter, image=image)
        self.modifier = modifier
        self.value = None
        self.changing = None

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

    def update(self):
        human = G.app.selectedHuman
        self.blockSignals(True)
        if not self.slider.isSliderDown():
            # Only update slider position when it is not being clicked or dragged
            self.setValue(self.modifier.getValue())
        self.blockSignals(False)


class GenericSlider(ModifierSlider):
    @staticmethod
    def findImage(name):
        if name is None:
            return None
        name = name.lower()
        return targets.getTargets().images.get(name, name)

    def __init__(self, min, max, modifier, label, image, view):
        image = self.findImage(image)
        if not os.path.isfile(image):
            image = None
        super(GenericSlider, self).__init__(min=min, max=max, label=label, modifier=modifier, image=image)
        self.view = getattr(G.app, view)

    def onFocus(self, event):
        super(GenericSlider, self).onFocus(event)
        if G.app.settings.get('cameraAutoZoom', True):
            self.view()

class MacroSlider(GenericSlider):
    def __init__(self, modifier, label, image, view, min = 0.0, max = 1.0):
        super(MacroSlider, self).__init__(min=min, max=max, modifier=modifier, label=label, image=image, view=view)

class UniversalSlider(GenericSlider):
    def __init__(self, modifier, label, image, view, min = None, max = 1.0):
        if min is None:
            min = -1.0 if modifier.left is not None else 0.0
        super(UniversalSlider, self).__init__(min, max, modifier, label, image, view)

