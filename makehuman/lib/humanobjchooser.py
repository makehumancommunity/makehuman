#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Human Object Chooser widget.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

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

A widget for selecting the human object or any of the proxies attached to it.
"""

from PyQt4 import QtCore, QtGui

import qtgui as gui
import log

import proxy


class HumanObjectSelector(gui.QtGui.QWidget, gui.Widget):
    """
    A widget for selecting the human object or any of the proxies attached to it.
    """

    def __init__(self, human):
        super(HumanObjectSelector, self).__init__()
        self.human = human
        self._selected = 'skin'

        self.layout = gui.QtGui.QGridLayout(self)

        self.objectSelector = []
        self.humanBox = gui.GroupBox('Human')
        self.layout.addWidget(self.humanBox)
        self.skinRadio = self.humanBox.addWidget(gui.RadioButton(self.objectSelector, "Skin", selected=True))
        self.skinRadio.selectionName = 'skin'

        for pType in proxy.SimpleProxyTypes:
            self._addSelectorItem(pType.lower(), pType, self.humanBox, False)

        @self.skinRadio.mhEvent
        def onClicked(event):
            if self.skinRadio.selected:
                self.selected = 'skin'
                self.callEvent('onActivate', self.selected)

        self.humanObjectCount = len(self.objectSelector)
        self.clothesBox = gui.GroupBox('Clothes')
        self.layout.addWidget(self.clothesBox)

    def getSelected(self):
        if self._selected in proxy.SimpleProxyTypesLower:
            pxy = self.human.getTypedSimpleProxies(self._selected)
            if pxy and pxy.object:
                return self._selected
            else:
                return 'skin'

        if self._selected in self.human.clothesProxies.keys():
            return self._selected
        else:
            return 'skin'

    def setSelected(self, value):
        if value in proxy.SimpleProxyTypesLower:
            pxy = self.human.getTypedSimpleProxies(value)
            if pxy.object:
                self._selected = value
            else:
                self._selected = 'skin'
        elif value in self.human.clothesProxies.keys():
            self._selected = value
        else:
            self._selected = 'skin'

    selected = property(getSelected, setSelected)

    def getSelectedObject(self):
        objType = self.selected
        if not objType:
            return None

        if objType == 'skin':
            return self.human
        elif objType in proxy.SimpleProxyTypesLower:
            pxy = self.human.getTypedSimpleProxies(objType)
            return pxy.object
        else:
            uuid = objType
            if uuid in self.human.clothesProxies:
                pxy = self.human.clothesProxies[uuid]
                return pxy.object
            else:
                return None

    def getSelectedProxy(self):
        objType = self.selected
        if not objType:
            return None

        if objType == 'skin':
            if self.human.isProxied():
                return self.human.proxy
            else:
                return None
        elif objType in proxy.SimpleProxyTypesLower:
            return self.human.getTypedSimpleProxies(objType)
        else:
            uuid = objType
            if uuid in self.human.clothesProxies:
                return self.human.clothesProxies[uuid]
            else:
                return None

    def onShow(self, event):
        self.refresh()

    def refresh(self):
        selected = self.selected

        self.skinRadio.setChecked(selected == 'skin')

        for radio in self.objectSelector[1:self.humanObjectCount]:
            pxy = self.human.getTypedSimpleProxies(radio.selectionName)
            radio.setEnabled(pxy is not None)
            radio.setChecked(selected == radio.selectionName)

        self._populateClothesSelector()

    def _populateClothesSelector(self):
        """
        Builds a list of all available clothes.
        """
        human = self.human
        # Only keep first 3 radio btns (human body parts)
        for radioBtn in self.objectSelector[self.humanObjectCount:]:
            radioBtn.hide()
            radioBtn.destroy()
        del self.objectSelector[self.humanObjectCount:]

        for uuid,pxy in human.clothesProxies.items():
            self._addSelectorItem(uuid, pxy.name, self.clothesBox, (self.selected == uuid))

        '''
        self.clothesSelections = []
        selected = self.selected
        for i, uuid in enumerate(clothesList):
            radioBtn = self.clothesBox.addWidget(gui.RadioButton(self.objectSelector, human.clothesProxies[uuid].name, selected=(selected == uuid)))
            self.clothesSelections.append( (radioBtn, uuid) )

            @radioBtn.mhEvent
            def onClicked(event):
                for radio, uuid in self.clothesSelections:
                    if radio.selected:
                        self.selected = uuid
                        log.debug( 'Selected clothing "%s" (%s)' % (radio.text(), uuid) )
                        self.callEvent('onActivate', self.selected)
                        return
        '''

    def _addSelectorItem(self, selectionName, label, parentWidget, isSelected = False):
        radioBtn = parentWidget.addWidget(gui.RadioButton(self.objectSelector, label, selected=isSelected))
        radioBtn.selectionName = selectionName

        @radioBtn.mhEvent
        def onClicked(event):
            for radio in self.objectSelector:
                if radio.selected:
                    self.selected = radio.selectionName
                    log.debug( 'Selected clothing "%s" (%s)' % (radio.text(), radio.selectionName) )
                    self.callEvent('onActivate', self.selected)
                    return


