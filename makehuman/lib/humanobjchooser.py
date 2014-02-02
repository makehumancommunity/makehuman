#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Human Object Chooser widget.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

A widget for selecting the human object or any of the proxies attached to it.
"""

from PyQt4 import QtCore, QtGui

import qtgui as gui
import log

import mh2proxy


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

        '''
        self.hairRadio = self.humanBox.addWidget(gui.RadioButton(self.objectSelector, "Hair", selected=False))
        self.eyesRadio = self.humanBox.addWidget(gui.RadioButton(self.objectSelector, "Eyes", selected=False))
        self.genitalsRadio = self.humanBox.addWidget(gui.RadioButton(self.objectSelector, "Genitals", selected=False))
        '''

        for pType in mh2proxy.SimpleProxyTypes:
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
        if self._selected in mh2proxy.SimpleProxyTypesLower:
            _proxy,obj = self.human.getTypedSimpleProxiesAndObjects(self._selected)
            if obj:
                return self._selected
            else:
                return 'skin'

        if self._selected in self.human.clothesObjs.keys():
            return self._selected
        else:
            return 'skin'

    def setSelected(self, value):
        if value in mh2proxy.SimpleProxyTypesLower:
            _proxy,obj = self.human.getTypedSimpleProxiesAndObjects(value)
            if obj:
                self._selected = value
            else:
                self._selected = 'skin'
        elif value in self.human.clothesObjs.keys():
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
        elif objType in mh2proxy.SimpleProxyTypesLower:
            _, obj = self.human.getTypedSimpleProxiesAndObjects(objType)
            return obj
        else:
            uuid = objType
            if uuid in self.human.clothesObjs:
                return self.human.clothesObjs[uuid]
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
        elif objType in mh2proxy.SimpleProxyTypesLower:
            pxy, _ = self.human.getTypedSimpleProxiesAndObjects(objType)
            return pxy
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
            _, obj = self.human.getTypedSimpleProxiesAndObjects(radio.selectionName)
            radio.setEnabled(obj is not None)
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

        for uuid in human.clothesObjs.keys():
            self._addSelectorItem(uuid, human.clothesProxies[uuid].name, self.clothesBox, (self.selected == uuid))

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


