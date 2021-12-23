#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman community assets

**Product Home Page:** http://www.makehumancommunity.org

**Code Home Page:**    https://github.com/makehumancommunity/community-plugins

**Authors:**           Joel Palmius

**Copyright(c):**      Joel Palmius 2016

**Licensing:**         MIT

Abstract
--------

This plugin manages community assets

"""

import gui3d
import mh
import gui
import json
import os
import re
import platform
import calendar
import datetime

from progress import Progress

from core import G

mhapi = gui3d.app.mhapi

if mhapi.utility.isPython3():
    from PyQt5 import QtGui
    from PyQt5 import QtCore
    from PyQt5.QtGui import *
    from PyQt5 import QtWidgets
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
else:
    if mhapi.utility.isPySideAvailable():
        from PySide import QtGui
        from PySide import QtCore
        from PySide.QtGui import *
        from PySide.QtCore import *
    else:
        from PyQt4 import QtGui
        from PyQt4 import QtCore
        from PyQt4.QtGui import *
        from PyQt4.QtCore import *

class AssetTableModel(QAbstractTableModel):

    def __init__(self, data, headers, parent=None):
        QAbstractTableModel.__init__(self,parent)
        self.log = mhapi.utility.getLogChannel("assetdownload")

        self.__data=data     # Initial Data
        self.__headers=headers

    def rowCount( self, parent ):
        self.log.trace("rowCount")
        return len(self.__data)

    def columnCount( self , parent ):
        self.log.trace("columnCount")
        return len(self.__headers)

    def data ( self , index , role ):
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.__data[row][column]

            if mhapi.utility.isPython3():
                return str(value)
            else:
                return QString(value)

    def headerData(self, section, orientation = Qt.Horizontal, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and self.__headers is not None:
            if orientation == Qt.Horizontal:
                if mhapi.utility.isPython3():
                    return self.__headers[section]
                else:
                    return QString(self.__headers[section])
            else:
                if mhapi.utility.isPython3():
                    return str(section + 1)
                else:
                    return QString(str(section + 1))

