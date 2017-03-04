#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements, Jonas Hauquier

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

import sys
import os
import re

from PyQt4 import QtCore, QtGui, QtSvg

from core import G
import events3d
import language
#import log
from getpath import getSysDataPath, getPath, isSubPath, pathToUnicode

def dummySvgCall():
    """Code which is here just so pyinstaller can discover we need SVG support"""
    dummy = QtSvg.QGraphicsSvgItem("some_svg.svg")
    
def getLanguageString(text, appendData=None, appendFormat=None):
    """Function to get the translation of a text according to the selected
    language.

    The function will look up the given text in the current language's
    dictionary and it will return the translated string.
    """
    if not text:
        return text
    return language.language.getLanguageString(text,appendData,appendFormat)


class Widget(events3d.EventHandler):
    def __init__(self):
        events3d.EventHandler.__init__(self)

    def callEvent(self, eventType, event):
        super(Widget, self).callEvent(eventType, event)

    def focusInEvent(self, event):
        self.callEvent('onFocus', self)
        super(type(self), self).focusInEvent(event)

    def focusOutEvent(self, event):
        self.callEvent('onBlur', self)
        super(type(self), self).focusOutEvent(event)

    def showEvent(self, event):
        self.callEvent('onShow', self)
        super(type(self), self).showEvent(event)

    def hideEvent(self, event):
        self.callEvent('onHide', self)
        super(type(self), self).hideEvent(event)

    def onFocus(self, event):
        pass

    def onBlur(self, event):
        pass

    def onShow(self, event):
        pass

    def onHide(self, event):
        pass

class Tab(Widget):
    def __init__(self, parent, name, label):
        super(Tab, self).__init__()
        self.parent = parent
        self.name = name
        self.label = label

    def onClicked(self, event):
        pass

class TabsBase(Widget):
    def __init__(self):
        super(TabsBase, self).__init__()
        self.tabBar().setExpanding(False)
        self.connect(self, QtCore.SIGNAL('currentChanged(int)'), self.tabChanged)
        self._tabs_by_idx = {}
        self._tabs_by_name = {}

    def _addTab(self, name, label, idx=None):
        label = getLanguageString(label)
        tab = Tab(self, name, label)
        tab.idx = self._makeTab(tab, idx)
        if idx != None:
            # Update index list when inserting tabs at arbitrary positions
            newIdxList = {}
            for tIdx, t in self._tabs_by_idx.items():
                if int(tIdx) >= idx:
                    t.idx += 1
                newIdxList[t.idx] = t
            self._tabs_by_idx = newIdxList
        self._tabs_by_idx[tab.idx] = tab
        self._tabs_by_name[tab.name] = tab
        return tab

    def tabChanged(self, idx):
        tab = self._tabs_by_idx.get(idx)
        if tab:
            self.callEvent('onTabSelected', tab)
            tab.callEvent('onClicked', tab)

    def findTab(self, name):
        return self._tabs_by_name.get(name)

    def changeTab(self, name):
        tab = self.findTab(name)
        if tab is None:
            return
        self.setCurrentIndex(tab.idx)

    def onTabSelected(self, event):
        pass

class Tabs(QtGui.QTabWidget, TabsBase):
    def __init__(self, parent = None):
        QtGui.QTabWidget.__init__(self, parent)
        TabsBase.__init__(self)

    def _makeTab(self, tab, idx=None):
        tab.child = TabBar(self)
        if idx != None:
            i = super(Tabs, self).insertTab(idx, tab.child, tab.label)
            if i == 0:
                self.setCurrentIndex(0)
            return i
        return super(Tabs, self).addTab(tab.child, tab.label)

    def addTab(self, name, label, idx = None):
        return super(Tabs, self)._addTab(name, label, idx)

    def tabChanged(self, idx):
        super(Tabs, self).tabChanged(idx)
        tab = self._tabs_by_idx.get(idx)
        if tab:
            tab.child.tabChanged(tab.child.currentIndex())

class TabBar(QtGui.QTabBar, TabsBase):
    def __init__(self, parent = None):
        QtGui.QTabBar.__init__(self, parent)
        TabsBase.__init__(self)
        self.setDrawBase(False)

    def tabBar(self):
        return self

    def _makeTab(self, tab, idx = None):
        if idx != None:
            i = super(TabBar, self).insertTab(idx, tab.label)
            if i == 0:
                self.setCurrentIndex(0)
            return i
        return super(TabBar, self).addTab(tab.label)

    def addTab(self, name, label, idx = None):
        return super(TabBar, self)._addTab(name, label, idx)

class GroupBox(QtGui.QGroupBox, Widget):
    def __init__(self, label = ''):
        label = getLanguageString(label) if label else ''
        QtGui.QGroupBox.__init__(self, label)
        Widget.__init__(self)
        self.layout = QtGui.QGridLayout(self)

    def __str__(self):
        return "%s - %s" % (type(self), unicode(self.title()))

    def addWidget(self, widget, row = None, column = 0, rowSpan = 1, columnSpan = 1, alignment = QtCore.Qt.Alignment(0)):
        # widget.setParent(self)
        if row is None:
            row = self.layout.count()
        self.layout.addWidget(widget, row, column, rowSpan, columnSpan, alignment)
        widget.show()
        return widget

    def removeWidget(self, widget):
        self.layout.removeWidget(widget)
        widget.setParent(None)

    @property
    def children(self):
        return list(self.layout.itemAt(i).widget() for i in xrange(self.count()))

    def count(self):
        return self.layout.count()

    def itemAt(self, idx):
        return self.layout.itemAt(idx)

# PyQt doesn't implement QProxyStyle so we have to do all this ...

class SliderStyle(QtGui.QCommonStyle):
    def __init__(self, parent):
        self.__parent = parent
        super(SliderStyle, self).__init__()

    def drawComplexControl(self, control, option, painter, widget = None):
        return self.__parent.drawComplexControl(control, option, painter, widget)

    def drawControl(self, element, option, painter, widget = None):
        return self.__parent.drawControl(element, option, painter, widget)

    def drawItemPixmap(self, painter, rectangle, alignment, pixmap):
        return self.__parent.drawItemPixmap(painter, rectangle, alignment, pixmap)

    def drawItemText(self, painter, rectangle, alignment, palette, enabled, text, textRole = QtGui.QPalette.NoRole):
        return self.__parent.drawItemText(painter, rectangle, alignment, palette, enabled, text, textRole)

    def drawPrimitive(self, element, option, painter, widget = None):
        return self.__parent.drawPrimitive(element, option, painter, widget)

    def generatedIconPixmap(self, iconMode, pixmap, option):
        return self.__parent.generatedIconPixmap(iconMode, pixmap, option)

    def hitTestComplexControl(self, control, option, position, widget = None):
        return self.__parent.hitTestComplexControl(control, option, position, widget)

    def itemPixmapRect(self, rectangle, alignment, pixmap):
        return self.__parent.itemPixmapRect(rectangle, alignment, pixmap)

    def itemTextRect(self, metrics, rectangle, alignment, enabled, text):
        return self.__parent.itemTextRect(metrics, rectangle, alignment, enabled, text)

    def pixelMetric(self, metric, option = None, widget = None):
        return self.__parent.pixelMetric(metric, option, widget)

    def polish(self, *args, **kwargs):
        return self.__parent.polish(*args, **kwargs)

    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QtGui.QStyle.SH_Slider_AbsoluteSetButtons:
            return QtCore.Qt.LeftButton | QtCore.Qt.MidButton | QtCore.Qt.RightButton
        return self.__parent.styleHint(hint, option, widget, returnData)

    def subControlRect(self, control, option, subControl, widget = None):
        return self.__parent.subControlRect(control, option, subControl, widget)

    def subElementRect(self, element, option, widget = None):
        return self.__parent.subElementRect(element, option, widget)

    def unpolish(self, *args, **kwargs):
        return self.__parent.unpolish(*args, **kwargs)

    def sizeFromContents(self, ct, opt, contentsSize, widget = None):
        return self.__parent.sizeFromContents(ct, opt, contentsSize, widget)

class NarrowLineEdit(QtGui.QLineEdit):
    def __init__(self, width=4, *args, **kwargs):
        super(NarrowLineEdit, self).__init__(*args, **kwargs)
        self.__cols = width

    def sizeHint(self):
        self.ensurePolished()
        fm = QtGui.QFontMetrics(self.font())
        leftMargin, topMargin, rightMargin, bottomMargin = self.getContentsMargins()
        textMargins = self.textMargins()
        h = max(fm.height(), 14) + 2 + textMargins.top() + textMargins.bottom() + topMargin + bottomMargin
        w = fm.width('0') * self.__cols + 4 + textMargins.left() + textMargins.right() + leftMargin + rightMargin

        opt = QtGui.QStyleOptionFrameV2()
        self.initStyleOption(opt)
        return self.style().sizeFromContents(
            QtGui.QStyle.CT_LineEdit, opt,
            QtCore.QSize(w, h).expandedTo(QtGui.QApplication.globalStrut()),
            self)

class _QSlider(QtGui.QSlider):
    """
    Mock object around QSlider that allows catching mouse press events and
    relaying them to the parent widget.
    """

    def __init__(self, parent, orientation):
        super(_QSlider, self).__init__(orientation)
        self.parent = parent

    def mousePressEvent(self, event):
        if self.parent:
            if not self.parent.sliderMousePressEvent(event):
                return
        super(_QSlider, self).mousePressEvent(event)

class Slider(QtGui.QWidget, Widget):
    _imageCache = {}
    _show_images = False
    _instances = set()
    _style = None

    @classmethod
    def _getImage(cls, path):
        if path not in cls._imageCache:
            cls._imageCache[path] = getPixmap(path)
        return cls._imageCache[path]

    def __init__(self, value=0.0, min=0.0, max=1.0, label=None, vertical=False, valueConverter=None, image=None, scale=1000):
        super(Slider, self).__init__()
        Widget.__init__(self)
        self.text = getLanguageString(label) or ''
        self.valueConverter = valueConverter

        orient = (QtCore.Qt.Vertical if vertical else QtCore.Qt.Horizontal)
        self.slider = _QSlider(self, orient)
        if Slider._style is None:
            Slider._style = SliderStyle(self.slider.style())
        self.slider.setStyle(Slider._style)

        self.min = min
        self.max = max
        self.scale = scale
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.scale)
        self.slider.setValue(self._f2i(value))
        self.slider.setTracking(False)
        self.connect(self.slider, QtCore.SIGNAL('sliderMoved(int)'), self._changing)
        self.connect(self.slider, QtCore.SIGNAL('valueChanged(int)'), self._changed)
        self.connect(self.slider, QtCore.SIGNAL('sliderReleased()'), self._released)
        self.connect(self.slider, QtCore.SIGNAL('sliderPressed()'), self._pressed)
        self.slider.installEventFilter(self)

        self.label = QtGui.QLabel(self.text)
        # Decrease vertical gap between label and slider
        #self.label.setContentsMargins(0, 0, 0, -1)
        self.layout = QtGui.QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setColumnMinimumWidth(1, 1)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 0)
        self.layout.setColumnStretch(2, 0)
        self.layout.addWidget(self.label, 1, 0, 1, 1)
        self.layout.addWidget(self.slider, 2, 0, 1, -1)
        if not self.text:
            self.label.hide()

        if image is not None:
            self.image = QtGui.QLabel()
            self.image.setPixmap(self._getImage(image))
            self.layout.addWidget(self.image, 0, 0, 1, -1)
        else:
            self.image = None

        self._sync(value)
        self._update_image()

        type(self)._instances.add(self)

    def setValueConverter(self, valueConverter):
        self._valueConverter = valueConverter
        if self.valueConverter:
            self.edit = NarrowLineEdit(5)
            self.edit.installEventFilter(self)
            self.connect(self.edit, QtCore.SIGNAL('returnPressed()'), self._enter)
            self.layout.addWidget(self.edit, 1, 1, 1, 1)
            if hasattr(self.valueConverter, 'units'):
                self.units = QtGui.QLabel(self.valueConverter.units)
                self.layout.addWidget(self.units, 1, 2, 1, 1)
            else:
                self.units = None
        else:
            self.edit = None
            self.units = None

    def getValueConverter(self):
        return self._valueConverter

    valueConverter = property(getValueConverter, setValueConverter)

    def sliderMousePressEvent(self, event):
        """
        Can be used to catch mouse press events from the attached QSlider widget.
        Return True to execute the default behaviour of the slider widget,
        return False to interrupt further handling of the event.
        Override this method when needed.
        """
        return True

    def __del__(self):
        type(self)._instances.remove(self)

    def _enter(self):
        text = unicode(self.edit.text())
        if not text:
            return
        oldValue = self.getValue()
        newValue = self.fromDisplay(float(text))
        self.setValue(newValue)
        if abs(oldValue - newValue) > 1e-3:
            self.callEvent('onChange', newValue)

    def toDisplay(self, value):
        if self.valueConverter is None:
            return value
        else:
            return self.valueConverter.dataToDisplay(value)

    def fromDisplay(self, value):
        if self.valueConverter is None:
            return value
        else:
            return self.valueConverter.displayToData(value)

    def eventFilter(self, object, event):
        if object != self.slider and object != self.edit:
            return
        result = False
        if object == self.edit:
            result = self.edit.eventFilter(object, event)
        if event.type() == QtCore.QEvent.FocusIn:
            self.callEvent('onFocus', self)
        elif event.type() == QtCore.QEvent.FocusOut:
            self.callEvent('onBlur', self)
        return result

    def _update_image(self):
        if self.image is None:
            return
        if type(self)._show_images:
            self.image.show()
        else:
            self.image.hide()

    @classmethod
    def imagesShown(cls):
        return cls._show_images

    @classmethod
    def showImages(cls, state):
        cls._show_images = state
        for w in cls._instances:
            w._update_image()

    def _changing(self, value):
        value = self._i2f(value)
        self._sync(value)
        self.callEvent('onChanging', value)

    def _changed(self, value):
        value = self._i2f(value)
        self._sync(value)
        self.callEvent('onChange', value)

    def _released(self):
        self.callEvent('onRelease', self)

    def _pressed(self):
        self.callEvent('onPress', self)

    def _sync(self, value):
        if '%' in self.text:
            self.label.setText(self.text % self.toDisplay(value))
        if self.edit is not None:
            self.edit.setText('%.2f' % self.toDisplay(value))
        if hasattr(self.valueConverter, 'units') and \
           self.valueConverter.units != unicode(self.units.text()):
            self.units.setText(self.valueConverter.units)

    def _f2i(self, x):
        return int(round(self.scale * (x - self.min) / (self.max - self.min)))

    def _i2f(self, x):
        return self.min + (x / float(self.scale)) * (self.max - self.min)

    def setValue(self, value):
        vmax = max(self.max, self.min)  # Virtual min and max values.
        vmin = min(self.max, self.min)  # Useful in case the slider is reversed.
        value = min(vmax, max(vmin, value))
        self._sync(value)
        if self._f2i(value) == self.slider.value():
            return
        self.slider.blockSignals(True)
        self.slider.setValue(self._f2i(value))
        self.slider.blockSignals(False)

    def getValue(self):
        return self._i2f(self.slider.value())

    def setMin(self, min):
        value = self.getValue()
        self.min = min
        self.setValue(value)

    def setMax(self, max):
        value = self.getValue()
        self.max = max
        self.setValue(value)

    def onChanging(self, event):
        pass

    def onChange(self, event):
        pass

class ButtonBase(Widget):
    def __init__(self):
        Widget.__init__(self)
        self.connect(self, QtCore.SIGNAL('clicked(bool)'), self._clicked)

    def getLabel(self):
        return unicode(self.text())

    def setLabel(self, label):
        label = getLanguageString(label)
        self.setText(label)

    def _clicked(self, state):
        self.callEvent('onClicked', None)

    @property
    def selected(self):
        return self.isChecked()

    def setSelected(self, value):
        self.setChecked(value)

    def onClicked(self, event):
        pass

class Button(QtGui.QPushButton, ButtonBase):
    def __init__(self, label=None, selected=False):
        label = getLanguageString(label)
        super(Button, self).__init__(label)
        ButtonBase.__init__(self)

class CheckBox(QtGui.QCheckBox, ButtonBase):
    def __init__(self, label=None, selected=False):
        label = getLanguageString(label)
        super(CheckBox, self).__init__(label)
        ButtonBase.__init__(self)
        self.setChecked(selected)

class RadioButton(QtGui.QRadioButton, ButtonBase):
    groups = {}

    def __init__(self, group, label=None, selected=False):
        label = getLanguageString(label)
        super(RadioButton, self).__init__(label)
        ButtonBase.__init__(self)
        self.group = group
        self.group.append(self)
        self.setChecked(selected)
        self._addToGroup(group)

    def __del__(self):
        self._removeFromGroup(self.group)

    def _addToGroup(self, group):
        if id(group) in type(self).groups:
            rbgroup = type(self).groups[id(group)]
        else:
            rbgroup = QtGui.QButtonGroup()
            rbgroup.setExclusive(True)
            type(self).groups[id(group)] = rbgroup
        rbgroup.addButton(self)

    def _removeFromGroup(self, group):
        if id(group) not in type(self).groups:
            return
        rbgroup = type(self).groups[id(group)]
        rbgroup.removeButton(self)
        if len(rbgroup.buttons()) == 0:
            del type(self).groups[id(group)]

    @property
    def selected(self):
        return self.isChecked()

    def getSelection(self):
        for radio in self.group:
            if radio.selected:
                return radio

class ListItem(QtGui.QListWidgetItem):
    def __init__(self, label, tooltip = True):
        super(ListItem, self).__init__(label)
        self.__hasCheckbox = False
        self.tooltip = tooltip

    def updateTooltip(self):
        """
        Attach a mouse-over tooltip for this item if the text is too long to fit
        the widget.
        """
        if not self.tooltip:
            return

        if not self.listWidget():
            return

        metrics = QtGui.QFontMetrics(self.font())

        labelWidth = self.listWidget().width()
        if self.icon():
            labelWidth -= self.listWidget().iconSize().width() + 10
            # pad size with 10px to account for margin between icon and text (this is an approximation)

        if metrics.width(self.text)/2 > labelWidth:
            self.setToolTip(self.text)
        else:
            self.setToolTip("")

    @property
    def hasCheckbox(self):
        return self.__hasCheckbox

    def setUserData(self, data):
        self.setData(QtCore.Qt.UserRole, data)

    def getUserData(self):
        return self.data(QtCore.Qt.UserRole)

    def setText(self, text):
        super(ListItem, self).setText(text)
        self.updateTooltip()

    @property
    def text(self):
        return unicode(super(ListItem, self).text())

    def enableCheckbox(self):
        self.__hasCheckbox = True
        self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable)
        self.setCheckState(QtCore.Qt.Unchecked)
        self.checkedState = False

    def setChecked(self, checked):
        if not self.hasCheckbox:
            self.setSelected(checked)
            return

        if checked:
            self.setCheckState(QtCore.Qt.Checked)
        else:
            self.setCheckState(QtCore.Qt.Unchecked)
        self.checkedState = self.checkState()

    def isChecked(self):
        return self.hasCheckbox and self.checkState() != QtCore.Qt.Unchecked

    def _clicked(self):
        owner = self.listWidget()
        if self.hasCheckbox:
            if self.checkState() != self.checkedState:
                self.checkedState = self.checkState()
                if self.checkState():
                    owner.callEvent('onItemChecked', self)
                else:
                    owner.callEvent('onItemUnchecked', self)
                return True
        return False

class ListView(QtGui.QListWidget, Widget):
    def __init__(self):
        super(ListView, self).__init__()
        Widget.__init__(self)
        self._vertical_scrolling = True
        self.connect(self, QtCore.SIGNAL('itemActivated(QListWidgetItem *)'), self._activate)
        self.connect(self, QtCore.SIGNAL('itemClicked(QListWidgetItem *)'), self._clicked)

    def _activate(self, item):
        self.callEvent('onActivate', item)

    def _clicked(self, item):
        if item._clicked():
            return
        if self.allowsMultipleSelection():
            if item.isSelected():
                self.callEvent('onItemChecked', item)
            else:
                self.callEvent('onItemUnchecked', item)
        else:
            self.callEvent('onClicked', item)

    def onActivate(self, event):
        pass

    def onClicked(self, event):
        pass

    def setData(self, items):
        self.clear()
        for item in items:
            self.addItem(item)

    def setVerticalScrollingEnabled(self, enabled):
        self._vertical_scrolling = enabled
        if enabled:
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        else:
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.updateGeometry()

    def rowCount(self):
        return len( [item for item in self.getItems() if not item.isHidden()] )

    def sizeHint(self):
        if self._vertical_scrolling:
            return super(ListView, self).sizeHint()
        else:
            rows = self.rowCount()
            if rows > 0:
                rowHeight = self.sizeHintForRow(0)
                rowHeight = max(rowHeight, self.iconSize().height())
            else:
                rowHeight = 0
            height = (rowHeight * rows)

            size = super(ListView,self).sizeHint()
            size.setHeight(height)
            return size

    _brushes = {}
    @classmethod
    def getBrush(cls, color):
        if color not in cls._brushes:
            cls._brushes[color] = QtGui.QBrush(QtGui.QColor(color))
        return cls._brushes[color]

    def addItem(self, text, color = None, data = None, checkbox = False, pos = None):
        item = ListItem(text)
        item.setText(text)
        if color is not None:
            item.setForeground(self.getBrush(color))
        if data is not None:
            item.setUserData(data)
        if checkbox:
            item.enableCheckbox()
        return self.addItemObject(item, pos)

    def addItemObject(self, item, pos = None):
        if pos is not None:
            super(ListView, self).insertItem(pos, item)
        else:
            super(ListView, self).addItem(item)
        if not self._vertical_scrolling:
            self.updateGeometry()
        return item

    def getSelectedItem(self):
        items = self.selectedItems()
        if len(items) > 0:
            return items[0].text
        return None

    def getSelectedItems(self):
        return [item.text for item in self.selectedItems()]

    def getItemData(self, row):
        return self.item(row).getUserData()

    def setItemColor(self, row, color):
        self.item(row).setForeground(self.getBrush(color))

    def showItem(self, row, state):
        self.item(row).setHidden(not state)

    def allowMultipleSelection(self, allow):
        self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection
                              if allow else
                              QtGui.QAbstractItemView.SingleSelection)

    def allowsMultipleSelection(self):
        return self.selectionMode() == QtGui.QAbstractItemView.MultiSelection

    def getItems(self):
        return [ self.item(row) for row in xrange(self.count()) ]

    def clearSelection(self):
        super(ListView, self).clearSelection()

        for item in self.getItems():
            if item.isChecked():
                item.setChecked(False)

        self.callEvent('onClearSelection', None)

class TextView(QtGui.QLabel, Widget):
    def __init__(self, label = ''):
        label = getLanguageString(label)
        super(TextView, self).__init__(label)
        Widget.__init__(self)

    def setText(self, text):
        text = getLanguageString(text)
        super(TextView,self).setText(text)

    def setTextFormat(self, text, *values):
        text = getLanguageString(text)
        super(TextView,self).setText(text % values)

class SliderBox(GroupBox):
    pass

def intValidator(text):
    return not text or text.isdigit() or (text[0] == '-' and (len(text) == 1 or text[1:].isdigit()))

def floatValidator(text):
    return not text or (text.replace('.', '').isdigit() and text.count('.') <= 1) or (text[0] == '-' and (len(text) == 1 or text[1:].replace('.', '').isdigit()) and text.count('.') <= 1) # Negative sign and optionally digits with optionally 1 decimal point

def filenameValidator(text):
    return not text or len(set(text) & set('\\/:*?"<>|')) == 0

class TextEdit(QtGui.QLineEdit, Widget):
    def __init__(self, text='', validator = None):
        super(TextEdit, self).__init__(text)
        Widget.__init__(self)
        self.setValidator(validator)
        self.connect(self, QtCore.SIGNAL('textEdited(QString)'), self._textChanged)
        self.connect(self, QtCore.SIGNAL('returnPressed()'), self._enter)
        self.installEventFilter(self)

    @property
    def text(self):
        return self.getText()

    def _textChanged(self, string):
        self.callEvent('onChange', string)

    def _enter(self):
        self.callEvent('onActivate', self.getText())

    def setText(self, text):
        super(TextEdit, self).setText(text)
        self.setCursorPosition(len(text))

    def getText(self):
        return unicode(super(TextEdit, self).text())

    def validateText(self, text):
        if self.__validator:
            return self.__validator(text)
        else:
            return True

    def setValidator(self, validator):
        self.__validator = validator
        if validator == intValidator:
            qvalidator = QtGui.QIntValidator()
        elif validator == floatValidator:
            qvalidator = QtGui.QDoubleValidator()
        elif validator == filenameValidator:
            qvalidator = QtGui.QRegExpValidator(QtCore.QRegExp(r'[^\/:*?"<>|]*'))
        else:
            qvalidator = None
        super(TextEdit, self).setValidator(qvalidator)

    def onChange(self, event):
        pass

    def eventFilter(self, object, event):
        if (object is self
            and event.type() == QtCore.QEvent.ShortcutOverride
            and event.key() in (QtCore.Qt.Key_Up, QtCore.Qt.Key_Down)):
            event.accept()
            return True
        return False

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Up:
            self._key_up()
            event.accept()
        elif key == QtCore.Qt.Key_Down:
            self._key_down()
            event.accept()
        elif key == QtCore.Qt.Key_Tab and self.tabPressed():
            event.accept()
        else:
            mod = int(event.modifiers())
            if mod > 0:
                self.callEvent('onModifier', (mod, key))
            super(TextEdit, self).keyPressEvent(event)

    def event(self, event):
        if event.type() == QtCore.QEvent.KeyPress and \
           event.key() == QtCore.Qt.Key_Tab and \
           self.tabPressed():
                return True

        return super(TextEdit, self).event(event)

    def tabPressed(self):
        """
        Override and return True to override custom behaviour when TAB key
        is pressed
        """
        return False  # Continue default event handling

    def _key_up(self):
        self.callEvent('onUpArrow', None)

    def _key_down(self):
        self.callEvent('onDownArrow', None)

class DocumentEdit(QtGui.QTextEdit, Widget):
    NoWrap          = QtGui.QTextEdit.NoWrap
    WidgetWidth     = QtGui.QTextEdit.WidgetWidth
    FixedPixelWidth = QtGui.QTextEdit.FixedPixelWidth
    FixedColumnWidth= QtGui.QTextEdit.FixedColumnWidth

    def __init__(self, text=''):
        super(DocumentEdit, self).__init__(text)
        Widget.__init__(self)
        self.setAcceptRichText(False)

    @property
    def text(self):
        return self.getText()

    def setText(self, text):
        self.setPlainText(text)

    def addText(self, text):
        self.moveCursor(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
        self.insertPlainText(text)

    def getText(self):
        return unicode(super(DocumentEdit, self).toPlainText())

class ProgressBar(QtGui.QProgressBar, Widget):
    def __init__(self, visible=True):
        super(ProgressBar, self).__init__()
        Widget.__init__(self)
        self.setVisible(visible)

    def setProgress(self, progress):
        min_ = self.minimum()
        max_ = self.maximum()
        self.setValue(min_ + progress * (max_ - min_))

class ShortcutEdit(QtGui.QLabel, Widget):
    def __init__(self, shortcut):
        if shortcut is not None:
            modifiers, key = shortcut
            text = self.shortcutToLabel(modifiers, key)
        else:
            text = ''
        super(ShortcutEdit, self).__init__(text)
        self.setAutoFillBackground(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)
        self.installEventFilter(self)

    def onFocus(self, arg):
        self.setBackgroundRole(QtGui.QPalette.Highlight)
        self.setForegroundRole(QtGui.QPalette.HighlightedText)

    def onBlur(self, arg):
        self.setBackgroundRole(QtGui.QPalette.Window)
        self.setForegroundRole(QtGui.QPalette.WindowText)

    def setShortcut(self, shortcut):
        modifiers, key = shortcut
        self.setText(self.shortcutToLabel(modifiers, key))

    def eventFilter(self, object, event):
        if object is self and event.type() == QtCore.QEvent.ShortcutOverride:
            event.accept()
            return True
        return False

    def keyPressEvent(self, event):
        key = event.key()
        mod = int(event.modifiers()) & ~QtCore.Qt.ShiftModifier
        if key in (QtCore.Qt.Key_Shift, QtCore.Qt.Key_Control, QtCore.Qt.Key_Alt, QtCore.Qt.Key_Meta):
            return
        self.setText(self.shortcutToLabel(mod, key))
        self.callEvent('onChanged', (mod, key))
        event.accept()

    def shortcutToLabel(self, mod, key):
        mod &= ~0x20000000 # Qt Bug #4022
        seq = QtGui.QKeySequence(key + mod)
        s = unicode(seq.toString(QtGui.QKeySequence.NativeText))
        return s

    def onChanged(self, shortcut):
        pass

class MouseActionEdit(QtGui.QLabel, Widget):
    def __init__(self, shortcut):
        modifiers, button = shortcut
        text = self.shortcutToLabel(modifiers, button)
        super(MouseActionEdit, self).__init__(text)
        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Raised)

    def setShortcut(self, shortcut):
        modifiers, button = shortcut
        self.setText(self.shortcutToLabel(modifiers, button))

    def mousePressEvent(self, event):
        button = event.button()
        modifiers = int(event.modifiers())
        self.setText(self.shortcutToLabel(modifiers, button))
        self.callEvent('onChanged', (modifiers, button))

    def shortcutToLabel(self, modifiers, button):
        labels = []

        if modifiers & QtCore.Qt.ControlModifier:
            labels.append('Ctrl')
        if modifiers & QtCore.Qt.AltModifier:
            labels.append('Alt')
        if modifiers & QtCore.Qt.MetaModifier:
            labels.append('Meta')
        if modifiers & QtCore.Qt.ShiftModifier:
            labels.append('Shift')

        if button & QtCore.Qt.LeftButton:
            labels.append('Left')
        elif button & QtCore.Qt.MidButton:
            labels.append('Middle')
        elif button & QtCore.Qt.RightButton:
            labels.append('Right')
        else:
            labels.append('[Unknown]')

        return '+'.join(labels)

    def onChanged(self, shortcut):
        pass

class StackedBox(QtGui.QStackedWidget, Widget):
    def __init__(self):
        super(StackedBox, self).__init__()
        Widget.__init__(self)
        self.layout().setAlignment(QtCore.Qt.AlignTop)
        self.autoResize = False
        self.connect(self, QtCore.SIGNAL('currentChanged(int)'), self.widgetChanged)

    def addWidget(self, widget):
        w = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        layout.addStretch()
        super(StackedBox, self).addWidget(w)
        self._updateSize()
        return widget

    def removeWidget(self, widget):
        w = widget.parentWidget()
        super(StackedBox, self).removeWidget(w)
        w.layout().removeWidget(widget)
        w.destroy()
        self._updateSize()

    def showWidget(self, widget):
        self.setCurrentWidget(widget.parentWidget())

    def setAutoResize(self, enabled):
        """
        Set to true to enable auto resizing the vertical dimensions of this
        widget to the height of the currently shown widget.
        """
        self.autoResize = enabled
        self._updateSize()

    def _updateSize(self):
        if self.autoResize:
            for i in xrange(self.count()):
                w = self.widget(i)
                if w: w.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
            w = self.widget(self.currentIndex())
            if w: w.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        else:
            for i in xrange(self.count()):
                w = self.widget(i)
                if w: w.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        self.layout().activate()

    def widgetChanged(self, widgetIdx):
        self._updateSize()

class Dialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(Dialog, self).__init__(parent)
        self.setModal(True)

        self.helpIds = set()

        icon = self.style().standardIcon(QtGui.QStyle.SP_MessageBoxWarning)

        self.layout = QtGui.QGridLayout(self)
        self.layout.setColumnStretch(0, 0)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 0)
        self.layout.setColumnStretch(3, 0)

        self.icon = QtGui.QLabel()
        self.icon.setPixmap(icon.pixmap(64))
        self.layout.addWidget(self.icon, 0, 0, 2, 1)

        self.text = TextView()
        self.layout.addWidget(self.text, 0, 1, 1, -1)

        self.check = QtGui.QCheckBox(getLanguageString("Don't show this again"))
        self.layout.addWidget(self.check, 1, 1, 1, -1)

        self.button1 = QtGui.QPushButton()
        self.layout.addWidget(self.button1, 2, 2)

        self.button2 = QtGui.QPushButton()
        self.layout.addWidget(self.button2, 2, 3)

        self.connect(self.button1, QtCore.SIGNAL('clicked(bool)'), self.accept)
        self.connect(self.button2, QtCore.SIGNAL('clicked(bool)'), self.reject)

    def prompt(self, title, text, button1Label, button2Label=None, button1Action=None, button2Action=None, helpId=None, fmtArgs = None):
        if helpId in self.helpIds:
            return

        if fmtArgs is None:
            fmtArgs = []
        elif isinstance(fmtArgs, basestring):
            fmtArgs = [fmtArgs]

        button1Label = getLanguageString(button1Label)
        button2Label = getLanguageString(button2Label)
        title = getLanguageString(title)

        self.setWindowTitle(title)
        self.text.setTextFormat(text, *fmtArgs)
        self.button1.setText(button1Label)

        if button2Label is not None:
            self.button2.setText(button2Label)
            self.button2.show()
        else:
            self.button2.hide()

        if helpId:
            self.check.show()
            self.check.setChecked(False)
        else:
            self.check.hide()

        which = self.exec_()

        if helpId and self.check.isChecked():
            self.helpIds.add(helpId)

        if which == QtGui.QDialog.Accepted:
            if button1Action:
                button1Action()
            return True
        elif which == QtGui.QDialog.Rejected:
            if button2Action:
                button2Action()
            return False


class AboutBox(QtGui.QMessageBox):
    def __init__(self, parent, title, text):
        super(AboutBox, self).__init__(title, text, QtGui.QMessageBox.Information, 0, 0, 0, parent)

        if sys.platform == 'darwin':
            self.setWindowFlags(QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowSystemMenuHint)
        # Grab window icon of parent
        icon = self.windowIcon()
        size = icon.actualSize(QtCore.QSize(64, 64))
        self.setIconPixmap(icon.pixmap(size))

        # Add an invisible spacer to make the dialog box size to fit the width
        chars_per_line = 80
        fm = QtGui.QFontMetrics(self.font())
        leftMargin, topMargin, rightMargin, bottomMargin = self.getContentsMargins()
        width = fm.width('0') * chars_per_line + 4 + leftMargin + rightMargin

        horizontalSpacer = QtGui.QSpacerItem(width, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        layout = self.layout()
        layout.addItem(horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

class AboutBoxScrollbars(QtGui.QDialog):
    def __init__(self, parent, title, text, versiontext):
        super(AboutBoxScrollbars, self).__init__(parent)

        def _replace_urls(text):
            re_match_urls = re.compile(r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(‌​([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))""", re.DOTALL)
            return re_match_urls.sub(lambda x: '<a href="%(url)s" style="color: #ffa02f;">%(url)s</a>' % dict(url=str(x.group())), text)

        if sys.platform == 'darwin':
            self.setWindowFlags(QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowSystemMenuHint)
        # Grab window icon of parent
        icon = self.windowIcon()
        size = icon.actualSize(QtCore.QSize(64, 64))

        self.setWindowTitle(title)

        label = QtGui.QLabel(self)
        label.setText(_replace_urls(text).replace('\n', '<br>'))
        label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        label.setOpenExternalLinks(True)
        label.setTextFormat(QtCore.Qt.RichText)

        if sys.platform == 'darwin':
            label.setContentsMargins(16, 0, 0, 0)
        else:
            label.setContentsMargins(2, 0, 0, 0)
            label.setIndent(9)

        versionLabel = QtGui.QLabel(self)
        versionLabel.setText(versiontext)
        versionLabel.setContentsMargins(0, 0, 0, 10)
        f = versionLabel.font()
        f.setBold(True)
        versionLabel.setFont(f)

        iconLabel = QtGui.QLabel(self)
        iconLabel.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        iconLabel.setPixmap(icon.pixmap(size))
        iconLabel.setContentsMargins(5, 0, 5, 0)

        scroll = QtGui.QScrollArea(self)
        scroll.setWidget(label)
        scroll.setWidgetResizable(True)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        self.connect(buttonBox, QtCore.SIGNAL("accepted()"), self.close)
        buttonBox.button(QtGui.QDialogButtonBox.Ok).setDefault(True)
        buttonBox.setContentsMargins(0, 0, 10, 0)

        grid = QtGui.QGridLayout()
        if sys.platform == 'darwin':
            grid.addWidget(versionLabel, 0, 1, 1, 1, QtCore.Qt.AlignTop)
            grid.addWidget(iconLabel, 0, 0, 2, 1, QtCore.Qt.AlignTop)
        else:
            grid.setMargin(0)
            grid.setVerticalSpacing(8)
            grid.setHorizontalSpacing(0)
            self.setContentsMargins(0, 15, 0, 20)
            grid.setRowStretch(1, 100)
            grid.setRowMinimumHeight(2, 6)

            grid.addWidget(versionLabel, 0, 1, 1, 1, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            grid.addWidget(iconLabel, 0, 0, 2, 1, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        grid.addWidget(scroll, 1, 1, 1, 1)
        grid.addWidget(buttonBox, 2, 0, 1, 2)

        if sys.platform == 'darwin':
            f = self.font()
            f.setBold(True)
            label.setFont(f)

        # Add an invisible spacer to make the dialog box size to fit the width
        chars_per_line = 83
        fm = QtGui.QFontMetrics(label.font())
        leftMargin, topMargin, rightMargin, bottomMargin = self.getContentsMargins()
        width = fm.width('#') * chars_per_line + 4 + leftMargin + rightMargin
        horizontalSpacer = QtGui.QSpacerItem(width, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        grid.addItem(horizontalSpacer, 3, 0, 1, 0)

        grid.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.setLayout(grid)

        self.setModal(True)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        size = QtCore.QSize(min(parent.size().width(), width + 60), 0.8 * parent.size().height())
        self.resize(size)


class FileEntryView(QtGui.QWidget, Widget):
    """Widget for entering paths and filenames.

    It can be used in file save / load task views,
    for browsing directories and opening or saving files.
    """

    class FileSelectedEvent(events3d.Event):
        """Event class for the the File Entry that defines an event type
        to be emitted once the user confirms their choice on the file name."""

        def __init__(self, path, source):
            """Constructor of the FileSelected event.

            The event consists of the path of the selected file
            as well as the source that triggered the event,
            which can be 'browse' for when the browse button is clicked,
            'return' for when the return key is pressed while writing in
            the text edit, or 'button' for when the widget's button is
            clicked."""

            events3d.Event.__init__(self)
            self.path = pathToUnicode(path)
            self.source = source

        def __repr__(self):
            return "FileSelectedEvent: Path: %s Source: '%s'" % (
                repr(self.path), repr(self.source))

    def __init__(self, buttonLabel, mode='open'):
        """FileEntryView constructor.

        The File Entry has a browse button on the left, which will open
        a standard save dialog. The center is occupied by an empty line edit,
        in which the user can simply enter a filename to save the file
        in the current directory. Finally, a button at the right can be used
        for accepting the filename and doing some action. You can control
        the button's caption with the buttonLabel parameter.

        By using the mode parameter, the widget will adapt to the needs,
        depending if it is used for opening a file, saving a file, or browsing
        a directory. Accordingly, its values can be: 'open', 'save', and 'dir'.

        If the mode is 'dir', there is no button. The final directory will be
        the path specified by the browse button.
        """

        super(FileEntryView, self).__init__()
        Widget.__init__(self)

        # Declare data

        self._directory = ""

        # Define controls

        self.browse = BrowseButton()

        self.edit = QtGui.QLineEdit()
        self.edit.setValidator(
            QtGui.QRegExpValidator(QtCore.QRegExp(r'[^\/:*?"<>|]*'), None))

        buttonLabel = getLanguageString(buttonLabel)
        self.confirm = QtGui.QPushButton(buttonLabel)

        # Register events

        @self.browse.mhEvent
        def beforeBrowse(event):
            """
            Before the browse dialog is shown, make sure to set
            its path properly.
            """
            if self.mode == 'dir' or not self.text:
                self.browse.directory = self.directory
            else:
                self.browse.path = self.path

        @self.browse.mhEvent
        def onClicked(path):
            """
            When the browse button is used, update the path in
            the line edit and confirm the entry.
            """
            if path:
                self.path = pathToUnicode(path)
                self._confirm('browse')

        self.connect(self.edit, QtCore.SIGNAL(' returnPressed()'),
            lambda: self._confirm('return'))

        self.connect(self.edit, QtCore.SIGNAL('textEdited(QString)'),
            lambda s: self.callEvent('onChange', unicode(s)))

        self.connect(self.confirm, QtCore.SIGNAL('clicked(bool)'),
            lambda _: self._confirm('button'))

        # Create GUI

        self.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Fixed)

        self.layout = QtGui.QGridLayout(self)

        self.layout.addWidget(self.browse, 0, 0)
        self.layout.setColumnStretch(0, 0)

        self.layout.addWidget(self.edit, 0, 1)
        self.layout.setColumnStretch(1, 1)

        self.mode = mode

        if self.mode != 'dir':
            self.layout.addWidget(self.confirm, 0, 2)
            self.layout.setColumnStretch(2, 0)

    def getMode(self):
        """Get the FileEntryView's mode of operation."""
        return self.browse.mode

    def setMode(self, mode):
        """Set the FileEntryView's mode of operation."""
        self.browse.mode = mode

    mode = property(getMode, setMode)

    def getDirectory(self):
        """Get the FileEntryView's current directory."""
        return pathToUnicode(self._directory)

    def setDirectory(self, directory):
        """Set the directory that the widget will use for saving or
        opening the filename, and as an initial path for browsing in
        the dialog. If the mode is 'dir', the given path is written
        in the line edit."""
        self._directory = pathToUnicode(directory)
        if self.mode == 'dir':
            self.text = self.directory

    directory = property(getDirectory, setDirectory)

    def getPath(self):
        """Get the FileEntryView's selected path."""
        if self.mode == 'dir':
            return self.directory
        else:
            return os.path.normpath(os.path.join(self.directory, self.text))

    def setPath(self, path):
        """Set the path of the FileEntryView.
        This will update the widget's current directory,
        as well as the file name in the text edit."""
        path = pathToUnicode(path)
        if self.mode == 'dir':
            self.directory = path
        else:
            self.directory = os.path.dirname(path)
            self.text = os.path.basename(path)

    path = property(getPath, setPath)

    def getText(self):
        return unicode(self.edit.text())

    def setText(self, text):
        self.edit.setText(text)

    text = property(getText, setText)

    def getFilter(self):
        """Get the extension filter the widget uses for browsing."""
        return self.browse.filter

    def setFilter(self, filter):
        """Set the extension filter the widget will use for browsing."""
        self.browse.filter = filter

    filter = property(getFilter, setFilter)

    def _confirm(self, source):
        """Method to be called once the user has confirmed their choice,
        either by pressing the confirmation button, by pressing the return
        button in the line edit, or by using the browser.
        It emits an onFileSelected event if the path is not empty."""
        if self.mode == 'dir' and source in ('return', 'button'):
            self.directory = pathToUnicode(self.text)

        if len(self.text):
            self.callEvent('onFileSelected',
                self.FileSelectedEvent(self.path, source))
        else:
            import log
            log.notice("The text box is empty. Please enter a valid file name.")
            self.setFocus()

    def onFocus(self, event):
        """Handler for the event of the widget being given focus. It passes
        the focus directly to the line edit."""
        self.edit.setFocus()


class SplashScreen(QtGui.QSplashScreen):
    def __init__(self, image, version=""):
        super(SplashScreen, self).__init__(G.app.mainwin, getPixmap(image), QtCore.Qt.WindowStaysOnTopHint)
        self._stdout = sys.stdout
        self.messageRect = QtCore.QRect(354, 531, 432, 41)
        self.messageAlignment = QtCore.Qt.AlignLeft
        self.message = ''
        self.progressBarRect = QtCore.QRect(660, 581, 124, 8)
        self._version = version
        self.versionRect = QtCore.QRect(186, 537, 88, 30)
        self.setProgress(0)

    def setProgress(self, progress):
        self.progress = float(progress)
        if self.progress < 0:
            self.progress == 0.0
        if self.progress > 1:
            self.progress = 1.0

    def getProgress(self):
        return self.progress

    def escape(self, text):
        return text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

    def logMessage(self, text):
        text = self.escape(text)
        self.showMessage(text, alignment = QtCore.Qt.AlignHCenter)
        self.message = text

    def drawContents(self, painter):
        color = QtGui.QColor()
        color.setNamedColor('#ffffff')
        painter.setPen(color)
        font = painter.font()
        font.setPixelSize(16)
        painter.setFont(font)
        painter.drawText(self.messageRect, self.messageAlignment, self.message);
        if self._version:
            font.setPixelSize(29)
            painter.setFont(font)
            painter.drawText(self.versionRect, QtCore.Qt.AlignLeft, self._version)
        color.setNamedColor('#000000')
        painter.setPen(color)
        color.setNamedColor('#f58220')
        painter.setBrush(QtGui.QBrush(color))
        pRect = self.progressBarRect
        if self.getProgress() == 0:
            progressedWidth = 0
        else:
            progressedWidth = int(pRect.width()*self.getProgress())
        painter.drawRect(pRect.x(), pRect.y(), progressedWidth, pRect.height())
        color.setNamedColor('#191718')
        painter.setBrush(QtGui.QBrush(color))
        painter.drawRect(pRect.x()+progressedWidth, pRect.y(), pRect.width()-progressedWidth, pRect.height())

class StatusBar(QtGui.QStatusBar, Widget):
    def __init__(self):
        super(StatusBar, self).__init__()
        Widget.__init__(self)
        self._perm = QtGui.QLabel()
        self.addWidget(self._perm, 1)
        self.duration = 2000

    def showMessage(self, text, *args):
        if isinstance(text,list):
            out = ""
            for part in text:
                out = out + getLanguageString(part)
            text = out
        else:
            text = getLanguageString(text)
        text = text % args
        super(StatusBar, self).showMessage(text, self.duration)

    def setMessage(self, text, *args):
        if isinstance(text,list):
            out = ""
            for part in text:
                out = out + getLanguageString(part)
            text = out
        else:
            text = getLanguageString(text)
        text = text % args
        self._perm.setText(text)

class VScrollLayout(QtGui.QLayout):
    def __init__(self, parent = None):
        super(VScrollLayout, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self._child = None
        self._position = 0

    def addItem(self, item):
        if self._child is not None:
            raise RuntimeError('layout already has a child')
        self._child = item
        self._update()

    def count(self):
        return int(self._child is not None)

    def itemAt(self, index):
        if index != 0:
            return None
        if self._child is None:
            return None
        return self._child

    def takeAt(self, index):
        if self.child is None:
            return None
        child = self._child
        self._child = None
        self._update()
        return child

    def minimumSize(self):
        if self._child is None:
            return super(VScrollLayout, self).minimumSize()
        # log.debug('VScrollLayout.minimumSize(child): %d %d', self._child.sizeHint().width(), self._child.sizeHint().height())
        left, top, right, bottom = self.getContentsMargins()
        return QtCore.QSize(self._child.minimumSize().width() + left + right, 0)

    def maximumSize(self):
        if self._child is None:
            return super(VScrollLayout, self).maximumSize()
        # log.debug('VScrollLayout.maximumSize(child): %d %d', self._child.sizeHint().width(), self._child.sizeHint().height())
        left, top, right, bottom = self.getContentsMargins()
        return self._child.maximumSize() + QtCore.QSize(left + right, top + bottom)

    def sizeHint(self):
        if self._child is None:
            return super(VScrollLayout, self).sizeHint()
        # log.debug('VScrollLayout.sizeHint(child): %d %d', self._child.sizeHint().width(), self._child.sizeHint().height())
        left, top, right, bottom = self.getContentsMargins()
        return self._child.sizeHint() + QtCore.QSize(left + right, top + bottom)

    def setGeometry(self, rect):
        super(VScrollLayout, self).setGeometry(rect)
        # log.debug('VScrollLayout.setGeometry: position: %d', self._position)
        # log.debug('VScrollLayout.setGeometry: %d %d %d %d', rect.x(), rect.y(), rect.width(), rect.height())
        if self._child is None:
            return
        size = self._child.sizeHint()
        left, top, right, bottom = self.getContentsMargins()
        # log.debug('VScrollLayout.getContentsMargins: %d %d %d %d', left, top, right, bottom)

        rect = rect.adjusted(left, top, -right, -bottom)
        rect.adjust(0, -self._position, 0, -self._position)
        # log.debug("%x", int(self._child.widget().sizePolicy().horizontalPolicy()))
        if not self._child.widget().sizePolicy().horizontalPolicy() & QtGui.QSizePolicy.ExpandFlag:
            rect.setWidth(size.width())
        if not self._child.widget().sizePolicy().verticalPolicy() & QtGui.QSizePolicy.ExpandFlag:
            rect.setHeight(size.height())
        else:
            rect.setHeight(max(rect.height(), size.height()))

        # log.debug('VScrollLayout.setGeometry(child): %d %d %d %d', rect.x(), rect.y(), rect.width(), rect.height())
        self._child.setGeometry(rect)

    def expandingDirections(self):
        if self._child is None:
            return 0
        return self._child.expandingDirections()

    def hasHeightForWidth(self):
        if self._child is None:
            return super(VScrollLayout, self).hasHeightForWidth()
        return self._child.hasHeightForWidth()

    def heightForWidth(self, width):
        if self._child is None:
            return super(VScrollLayout, self).heightForWidth(width)
        return self._child.heightForWidth(width)

    def setPosition(self, value):
        self._position = value
        self._update()

    def _update(self):
        self.update()

    def childHeight(self):
        if self._child is None:
            return 0
        left, top, right, bottom = self.getContentsMargins()
        return self._child.sizeHint().height() + top + bottom

class Viewport(QtGui.QWidget):
    def __init__(self):
        super(Viewport, self).__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = VScrollLayout(self)
        self._layout.setContentsMargins(1, 20, 1, 20)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._child = None

    def setWidget(self, widget):
        if widget is None:
            self._layout.removeWidget(self._child)
        else:
            self._layout.addWidget(widget)
        self._child = widget
        self.updateGeometry()

    def childHeight(self):
        return self._layout.childHeight()

    def setPosition(self, value):
        self._layout.setPosition(value)

class VScrollArea(QtGui.QWidget, Widget):
    def __init__(self):
        super(VScrollArea, self).__init__()
        Widget.__init__(self)

        self._viewport = Viewport()
        self._scrollbar = QtGui.QScrollBar(QtCore.Qt.Vertical)
        self._scrollbar.setRange(0, 0)
        self._scrollbar.setMinimumHeight(0)
        self._scrollbar.setSingleStep(10)
        self._layout = QtGui.QBoxLayout(QtGui.QBoxLayout.RightToLeft, self)
        self._layout.addWidget(self._scrollbar, 0)
        self._layout.addWidget(self._viewport, 1)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._scrollbar.setTracking(True)
        self._widget = None
        self.connect(self._scrollbar, QtCore.SIGNAL('valueChanged(int)'), self._changed)

    def setWidget(self, widget):
        if self._widget is not None:
            self._widget.removeEventFilter(self)
        self._widget = widget
        self._viewport.setWidget(self._widget)
        self.updateGeometry()
        self._updateScrollSize()
        if self._widget is not None:
            self._widget.installEventFilter(self)

    def resizeEvent(self, event):
        # log.debug('resizeEvent: %d, %d', event.size().width(), event.size().height())
        super(VScrollArea, self).resizeEvent(event)
        self._updateScrollSize()
        self._updateScrollPosition()

    def _updateScrollSize(self):
        cheight = self._viewport.childHeight()
        vheight = self._viewport.size().height()
        # log.debug('_updateScrollSize: %d, %d', cheight, vheight)
        self._scrollbar.setRange(0, cheight - vheight)
        self._scrollbar.setPageStep(vheight)

    def _changed(self, value):
        # log.debug('VScrollArea_changed: %d', value)
        self._updateScrollPosition()

    def _updateScrollPosition(self):
        value = self._scrollbar.value()
        # log.debug('_updateScrollPosition: %d', value)
        self._viewport.setPosition(value)

    def eventFilter(self, object, event):
        if object == self._widget and event.type() != QtCore.QEvent.Resize:
            # log.debug('Viewport child resize: %d,%d -> %d,%d',
            #           event.oldSize().width(), event.oldSize().height(),
            #           event.size().width(), event.size().height())
            self._updateScrollSize()
        return False

    def getClassName(self):
        """
        Classname for this widet, useful for styling using qss.
        """
        return str(self.metaObject().className())

class TreeItem(QtGui.QTreeWidgetItem):
    def __init__(self, text, parent=None, isDir=False):
        super(TreeItem, self).__init__([text])
        self.text = text
        self.parent = parent
        self.isDir = isDir
        if self.isDir:
            self.setIcon(0, TreeView._dirIcon)
            self.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.ShowIndicator)
        else:
            self.setIcon(0, TreeView._fileIcon)
            self.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.DontShowIndicator)

    def addChild(self, text, isDir=False):
        item = TreeItem(text, self, isDir)
        super(TreeItem, self).addChild(item)
        return item

    def addChildren(self, strings):
        items = [TreeItem(text, self) for text in strings]
        super(TreeItem, self).addChildren(items)
        return items

class TreeView(QtGui.QTreeWidget, Widget):
    _dirIcon = None
    _fileIcon = None

    def __init__(self, parent = None):
        super(TreeView, self).__init__(parent)
        Widget.__init__(self)
        self.connect(self, QtCore.SIGNAL('itemActivated(QTreeWidgetItem *,int)'), self._activate)
        self.connect(self, QtCore.SIGNAL('itemExpanded(QTreeWidgetItem *)'), self._expand)
        if TreeView._dirIcon is None:
            TreeView._dirIcon = self.style().standardIcon(QtGui.QStyle.SP_DirIcon)
        if TreeView._fileIcon is None:
            TreeView._fileIcon = self.style().standardIcon(QtGui.QStyle.SP_FileIcon)

    def addTopLevel(self, text, isDir=True):
        item = TreeItem(text, None, isDir)
        self.addTopLevelItem(item)
        return item

    def _activate(self, item, column):
        if not item.isDir:
            self.callEvent('onActivate', item)

    def _expand(self, item):
        if item.isDir:
            self.callEvent('onExpand', item)

class SpinBox(QtGui.QSpinBox, Widget):
    def __init__(self, value, parent = None):
        super(SpinBox, self).__init__(parent)
        Widget.__init__(self)
        self.setRange(0, 99999)
        self.setValue(value)
        self.connect(self, QtCore.SIGNAL('valueChanged(int)'), self._changed)

    def _changed(self, value):
        self.callEvent('onChange', value)

    def setValue(self, value):
        self.blockSignals(True)
        super(SpinBox, self).setValue(value)
        self.blockSignals(False)

class BrowseButton(Button):

    @staticmethod
    def conformFilter(filter):
        """Static method that corrects a filter string, if needed, by
        translating it and adding the default 'All Files' filter to it."""
        filter = getLanguageString(filter)
        if '(*.*)' not in filter:
            filter = ';;'.join([filter, getLanguageString('All Files') + ' (*.*)'])
        return filter

    @staticmethod
    def getExistingPath(path):
        path = pathToUnicode(path)
        if not os.path.isdir(path) and not os.path.isfile(path):
            path = os.path.split(path)[0]
            homePath = os.path.abspath(getPath(''))
            if os.path.isdir(homePath) and isSubPath(os.path.abspath(path), homePath):
                # Find first existing folder within MH home path
                while path and not os.path.isdir(path):
                    path = os.path.split(path)[0]
            if not os.path.isdir(path):
                path = os.getcwd()
        return os.path.normpath(path)

    def __init__(self, mode = 'open', label=None):
        if label is None:
            label = '...'
        super(BrowseButton, self).__init__(label)
        self._directory = self.getExistingPath("")
        self.filename = ""
        self._filter = ''
        self._mode = None

        self.mode = mode

    def getMode(self):
        return self._mode

    def setMode(self, mode):
        mode = mode.lower()
        if mode not in ('open', 'save', 'dir'):
            raise RuntimeError("mode '%s' not recognised; must be 'open', 'save', or 'dir'")
        self._mode = mode

    mode = property(getMode, setMode)

    def getDirectory(self):
        """Get the directory in which the dialog will browse."""
        return self._directory

    def setDirectory(self, dir):
        """Set the directory in which the dialog will browse."""
        self._directory = pathToUnicode(dir)

    directory = property(getDirectory, setDirectory)

    def getPath(self):
        return os.path.normpath(os.path.join(self.directory, self.filename))

    def setPath(self, path):
        """WARNING: Use only with complete file paths that include filename."""
        self.directory = os.path.dirname(pathToUnicode(path))
        self.filename = os.path.basename(pathToUnicode(path))

    path = property(getPath, setPath)

    def getFilter(self):
        return self._filter

    def setFilter(self, filter):
        self._filter = self.conformFilter(filter)

    filter = property(getFilter, setFilter)

    def _clicked(self, state):
        self.callEvent('beforeBrowse', None)

        path = self.getExistingPath(self.path)
        if self.mode == 'save' and self.filename:
            # Don't discard filename when saving
            path = os.path.join(path, self.filename)

        if self.mode == 'open':
            path = pathToUnicode(unicode(QtGui.QFileDialog.getOpenFileName(G.app.mainwin, directory=path, filter=self.filter)))
        elif self.mode == 'save':
            path = pathToUnicode(unicode(QtGui.QFileDialog.getSaveFileName(G.app.mainwin, directory=path, filter=self.filter)))
        elif self.mode == 'dir':
            path = pathToUnicode(unicode(QtGui.QFileDialog.getExistingDirectory(G.app.mainwin, directory=path)))

        if path:
            if self.mode == 'dir': self.directory = path
            else: self.path = path
        self.callEvent('onClicked', path)


class ColorPickButton(Button):
    """
    Button widget that opens a color picker when clicked.
    """
    # TODO add a rectangle showing the current color

    def __init__(self, initialColor = None):
        super(ColorPickButton, self).__init__("Pick")
        if initialColor is not None:
            self.color = initialColor
        else:
            import material
            self.color = material.Color()

    def getColor(self):
        return self._color

    def setColor(self, color):
        import material
        if isinstance(color, material.Color):
            self._color = color
        elif isinstance(color, QtGui.QColor):
            self._color = colorFromQColor(color)
        else:
            self._color = material.Color().copyFrom(color)

    color = property(getColor, setColor)

    def _clicked(self, state):
        currentColor = qColorFromColor(self.color)
        pickedColor = QtGui.QColorDialog.getColor(currentColor)
        if pickedColor.isValid():
            self.color = colorFromQColor(pickedColor)
            self.callEvent('onClicked', self.color)

class Action(QtGui.QAction, Widget):
    _groups = {}

    @classmethod
    def getIcon(cls, name):
        from qtui import supportsSVG
        # icon = G.app.mainwin.style().standardIcon(QtGui.QStyle.SP_MessageBoxWarning)
        svgPath = os.path.join(getSysDataPath('icons'), name + '.svg')
        if supportsSVG() and os.path.isfile(svgPath):
            path = svgPath
        else:
            path = os.path.join(getSysDataPath('icons'), name + '.png')

        if G.app.theme:
            themePath = os.path.join(getSysDataPath('themes'), G.app.theme, 'icons', name + '.svg')
            if supportsSVG() and os.path.isfile(themePath):
                path = themePath
            else:
                themePath = os.path.join(getSysDataPath('themes'), G.app.theme, 'icons', name + '.png')
                if os.path.isfile(themePath):
                    path = themePath

        if not os.path.isfile(path):
            path = os.path.join(getSysDataPath('icons'), 'notfound.png')
        icon = QtGui.QIcon(path)

        # Allows setting custom icons for active, selected and disabled states
        ext = os.path.splitext(path)[1]
        for (name, mode) in [ ("disabled", QtGui.QIcon.Disabled),
                              ("active", QtGui.QIcon.Active),
                              ("selected", QtGui.QIcon.Selected) ]:
            customIconPath = "%s_%s%s" % (os.path.splitext(path)[0], name, ext)
            if os.path.isfile(customIconPath):
                icon.addFile(customIconPath, QtCore.QSize(), mode)
        return icon

    @classmethod
    def getGroup(cls, name):
        if name not in cls._groups:
            cls._groups[name] = ActionGroup()
        return cls._groups[name]

    def __init__(self, name, text, method, tooltip = None, group = None, toggle = False):
        super(Action, self).__init__(self.getIcon(name), text, G.app.mainwin)
        self.name = name
        self.method = method
        if tooltip is not None:
            self.setToolTip(tooltip)
        if group is not None:
            self.setActionGroup(self.getGroup(group))
        if toggle:
            self.setCheckable(True)
        self.connect(self, QtCore.SIGNAL('triggered(bool)'), self._activate)

    @property
    def text(self):
        return unicode(super(Action, self).text())

    def setActionGroup(self, group):
        self.setCheckable(True)
        super(Action, self).setActionGroup(group)

    def _activate(self, checked):
        self.method()

class ActionGroup(QtGui.QActionGroup):
    def __init__(self):
        super(ActionGroup, self).__init__(G.app.mainwin)

class Actions(object):
    def __init__(self):
        self._order = []

    def __setattr__(self, name, value):
        if name[0] != '_':
            self._order.append(value)
        object.__setattr__(self, name, value)

    def __iter__(self):
        return iter(self._order)

class SizePolicy(object):
    Fixed               = QtGui.QSizePolicy.Fixed
    Minimum             = QtGui.QSizePolicy.Minimum
    Maximum             = QtGui.QSizePolicy.Maximum
    Preferred           = QtGui.QSizePolicy.Preferred
    Expanding           = QtGui.QSizePolicy.Expanding
    MinimumExpanding    = QtGui.QSizePolicy.MinimumExpanding
    Ignored             = QtGui.QSizePolicy.Ignored

class TableItem(QtGui.QTableWidgetItem):
    def setUserData(self, data):
        self.setData(QtCore.Qt.UserRole, data)

    def getUserData(self):
        return self.data(QtCore.Qt.UserRole)

    @property
    def text(self):
        return unicode(super(TableItem, self).text())

class TableView(QtGui.QTableWidget, Widget):
    def __init__(self):
        super(TableView, self).__init__()
        Widget.__init__(self)

    def setItem(self, row, col, text, data = None):
        item = TableItem(text)
        if data is not None:
            item.setUserData(data)
        super(TableView, self).setItem(row, col, item)

    def getItemData(self, row, col):
        return self.item(row, col).getUserData()

class ImageView(QtGui.QLabel, QtGui.QScrollArea, Widget):
    def __init__(self):
        super(ImageView, self).__init__()
        Widget.__init__(self)
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.setMinimumSize(50,50)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)
        #self.setScaledContents(True)
        self.ratio = 1.0
        self.workingSize = None
        self._pixmap = None

    def setImage(self, img):
        self._pixmap = getPixmap(img)
        self.adjustSize()
        self.updateGeometry()
        self.refreshImage()

    def sizeHint(self):
        if not self._pixmap:
            return super(ImageView, self).sizeHint()
        return self._pixmap.size()

    def heightForWidth(self, width):
        if not self._pixmap or self._pixmap.width() == 0:
            return width
        else:
            size = self._pixmap.size()
            return int((float(width)/size.width())*size.height())

    def resizeEvent(self, event):
        self.workingSize = event.size()
        self.refreshImage(event.size())

    def refreshImage(self, size = None):
        if not self._pixmap:
            return

        if not size:
            size = self.sizeHint()

        pixmap = self._pixmap
        w = pixmap.width()
        h = pixmap.height()
        size *= self.ratio
        if w > size.width() or h > size.height():
            pixmap = pixmap.scaled(size.width(), size.height(), QtCore.Qt.KeepAspectRatio)
        self.setPixmap(pixmap)

    def save(self, fname):
        if not os.path.splitext(fname)[1]:
            fname = fname + '.png'

        if self._pixmap:
            self._pixmap.save (fname)


class ZoomableImageView(QtGui.QScrollArea, Widget):
    def __init__(self):
        QtGui.QScrollArea.__init__(self)
        Widget.__init__(self)
        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.imageLabel.setMinimumSize(5,5)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHeightForWidth(True)
        self.imageLabel.setSizePolicy(sizePolicy)
        self.imageLabel.setScaledContents(True)
        self.setBackgroundRole(QtGui.QPalette.Dark)
        self.setWidget(self.imageLabel)
        self.workingWidth = None
        self.ratio = 1.0
        self.minratio = 0.1

    def setImage(self, img):
        pixmap = getPixmap(img)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.adjustSize()
        self.ratio = float(self.width()) / float(pixmap.width())
        self.minratio = 100.0 / float(pixmap.width())
        if self.minratio > 1.0:
            self.minratio = 1.0
        self.imageLabel.updateGeometry()
        self.refreshImage()

    def resizeEvent(self, event):
        if self.workingWidth:
            self.ratio *= float(event.size().width()) / float(self.workingWidth)
        self.workingWidth = event.size().width()
        if self.ratio > 1.0:
            self.ratio = 1.0
        self.refreshImage(True)

    def heightForWidth(self, width):
        pixmap = self.imageLabel.pixmap()
        if not pixmap or pixmap.width() == 0:
            return width
        else:
            size = pixmap.size()
            return int((float(width)/size.width())*size.height())

    def refreshImage(self, zoomAct = False, displ = (0, 0)):
        pixmap = self.imageLabel.pixmap()
        if not pixmap:
            return
        scrat = [0.0, 0.0]
        if zoomAct:
            for (index, scrollBar) in enumerate((self.horizontalScrollBar(), self.verticalScrollBar())):
                if scrollBar.maximum() > 0:
                    scrat[index] = float(scrollBar.value()) / float(scrollBar.maximum())
                else:
                    scrat[index] = 0.5
        self.imageLabel.resize(self.ratio * pixmap.size())
        if zoomAct:
            for (index, scrollBar) in enumerate((self.horizontalScrollBar(), self.verticalScrollBar())):
                if scrollBar.maximum() > 0:
                    scrollBar.setValue(int(scrat[index] * scrollBar.maximum() + displ[index]))

    def save(self, fname):
        if not os.path.splitext(fname)[1]:
            fname = fname + '.png'

        if self.imageLabel.pixmap():
            self.imageLabel.pixmap().save (fname)

    def mousePressEvent(self, event):
        self.mdown = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.RightButton:
            self.wheelEvent(QtGui.QWheelEvent(event.pos(),
                                              10 * (event.pos().y() - self.mdown.y()),
                                              event.buttons(), event.modifiers()), False)
            self.mdown = event.pos()
        else:
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + 2*(self.mdown.x() - event.pos().x()))
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + 2*(self.mdown.y() - event.pos().y()))
            self.mdown = event.pos()
            self.refreshImage()

    def wheelEvent(self, event, displace = True):
        ratbef = self.ratio
        if G.app.getSetting('invertMouseWheel'):
            delta = event.delta()
        else:
            delta = -event.delta()
        factor = 1 - delta*0.0007
        self.ratio *= factor
        if self.ratio > 1.0:
            self.ratio = 1.0
        if self.ratio < self.minratio:
            self.ratio = self.minratio
        dr = 2*abs(self.ratio - ratbef) if displace else 0
        self.refreshImage(True,
                          (dr*(event.x() - self.width()/2),
                           dr*(event.y() - self.height()/2)))


def colorFromQColor(qColor):
    import material
    if qColor.isValid():
        values = (float(qColor.red())/255,
                  float(qColor.green())/255,
                  float(qColor.blue())/255)
        return material.Color().copyFrom(values)
    else:
        return material.Color()

def qColorFromColor(color):
    import material
    if isinstance(color, material.Color):
        color = color.asTuple()
    return QtGui.QColor(int(color[0]*255),
                            int(color[1]*255),
                            int(color[2]*255))

def getPixmap(img):
    import image
    if isinstance(img, image.Image):
        img = img.toQImage()
        return QtGui.QPixmap.fromImage(img)
    elif isinstance(img, QtGui.QPixmap):
        return img
    elif isinstance(img, QtGui.QImage):
        return QtGui.QPixmap.fromImage(img)
    else:
        return QtGui.QPixmap(pathToUnicode(img))
