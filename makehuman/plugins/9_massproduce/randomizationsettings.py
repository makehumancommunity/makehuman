#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
import sys
import qtgui

class RandomizationSettings:

    def __init__(self):

        self._ui = dict()

    def addUI(self, category, name, widget, subName=None):

        if widget is None:
            raise ValueError("Trying to add None widget")

        if not category in self._ui:
            self._ui[category] = dict()

        if not subName is None:
            if not name in self._ui[category]:
                self._ui[category][name] = dict()
            self._ui[category][name][subName] = widget
        else:
            self._ui[category][name] = widget

        return widget

    def getUI(self, category, name, subName=None):

        if not category in self._ui:
            print("No such category: " + category)
            self.dumpValues()
            sys.exit()

        if not name in self._ui[category]:
            print("No such name: " + category + "/" + name)
            self.dumpValues()
            sys.exit()

        if not subName is None:
            if not subName in self._ui[category][name]:
                print("No such subName: " + category + "/" + name + "/" + subName)
                self.dumpValues()
                sys.exit()
            widget = self._ui[category][name][subName]
        else:
            widget = self._ui[category][name]

        if widget is None:
            print("Got None widget for " + category + "/" + name + "/" + str(subName))
        return widget

    def getValue(self, category, name, subName=None):

        widget = self.getUI(category, name, subName)

        if isinstance(widget, QCheckBox) or isinstance(widget, qtgui.CheckBox):
            return widget.selected
        if isinstance(widget, QTextEdit) or isinstance(widget, qtgui.TextEdit):
            return widget.getText()
        if isinstance(widget, qtgui.Slider):
            return widget.getValue()
        if isinstance(widget, QComboBox):
            return str(widget.getCurrentItem())
        if isinstance(widget, str):
            return widget

        print("Unknown widget type")
        print(type(widget))
        sys.exit(1)

    def getValueHash(self, category, name):

        if not category in self._ui:
            print("No such category: " + category)
            self.dumpValues()
            sys.exit()

        if not name in self._ui[category]:
            print("No such name: " + category + "/" + name)
            self.dumpValues()
            sys.exit()

        subCat = self._ui[category][name]

        if not isinstance(subCat, dict):
            print(category + "/" + name + " is not a dict")
            self.dumpValues()
            sys.exit(1)

        values = dict()
        for subName in subCat:
            values[subName] = self.getValue(category, name, subName)

        return values

    def getNames(self, category):
        return self._ui[category].keys()

    def setValue(self, category, name, value, subName=None):
        pass

    def dumpValues(self):

        for category in self._ui:
            print(category)
            for name in self._ui[category]:
                widget = self.getUI(category, name)
                if isinstance(widget, dict):
                    print("  " + name)
                    for subName in widget:
                        subWidget = self.getUI(category, name, subName)
                        value = self.getValue(category, name, subName)
                        print("    " + subName + " (" + str(type(subWidget)) + ") = " + str(value))
                else:
                    value = self.getValue(category, name)
                    print("  " + name + " (" + str(type(widget)) + ") = " + str(value))
