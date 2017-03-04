#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Qt filechooser widget.

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

A Qt based filechooser widget.
"""

import os

from PyQt4 import QtCore, QtGui

import qtgui as gui
import mh
import getpath
import log
from sorter import Sorter

class ThumbnailCache(object):
    aspect_mode = QtCore.Qt.KeepAspectRatioByExpanding
    scale_mode = QtCore.Qt.SmoothTransformation

    def __init__(self, size):
        self.cache = {}
        self.size = size

    def __getitem__(self, name):
        nstat = os.stat(name)
        if name in self.cache:
            stat, pixmap = self.cache[name]
            if stat.st_size == nstat.st_size and stat.st_mtime == nstat.st_mtime:
                return pixmap
            else:
                del self.cache[name]
        pixmap = self.loadImage(name)
        self.cache[name] = (nstat, pixmap)
        return pixmap

    def loadImage(self, path):
        pixmap = QtGui.QPixmap(path)
        width, height = self.size
        pixmap = pixmap.scaled(width, height, self.aspect_mode, self.scale_mode)
        pwidth = pixmap.width()
        pheight = pixmap.height()
        if pwidth > width or pheight > height:
            x0 = max(0, (pwidth - width) / 2)
            y0 = max(0, (pheight - height) / 2)
            pixmap = pixmap.copy(x0, y0, width, height)
        return pixmap

class FileChooserRectangle(gui.Button):
    _size = (128, 128)
    _imageCache = ThumbnailCache(_size)

    def __init__(self, owner, file, label, imagePath):
        super(FileChooserRectangle, self).__init__()
        gui.Widget.__init__(self)
        self.owner = owner
        self.file = file

        self.layout = QtGui.QGridLayout(self)
        self.layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)

        image = self._imageCache[imagePath]
        self.preview = QtGui.QLabel()
        self.preview.setPixmap(getpath.pathToUnicode(image))
        self.layout.addWidget(self.preview, 0, 0)
        self.layout.setRowStretch(0, 1)
        self.layout.setColumnMinimumWidth(0, self._size[0])
        self.layout.setRowMinimumHeight(0, self._size[1])

        self.label = QtGui.QLabel()
        self.label.setText(label)
        self.label.setMinimumWidth(1)
        self.layout.addWidget(self.label, 1, 0)
        self.layout.setRowStretch(1, 0)

    def onClicked(self, event):
        self.owner.selection = self.file
        self.owner.callEvent('onFileSelected', self.file)

class FlowLayout(QtGui.QLayout):
    def __init__(self, parent = None):
        super(FlowLayout, self).__init__(parent)
        self._children = []

    def addItem(self, item):
        self._children.append(item)

    def count(self):
        return len(self._children)

    def itemAt(self, index):
        if index < 0 or index >= self.count():
            return None
        return self._children[index]

    def takeAt(self, index):
        child = self.itemAt(index)
        if child is not None:
            del self._children[index]
        return child

    def hasHeightForWidth(self):
        return True

    def _doLayout(self, width, real=False):
        x = 0
        y = 0
        rowHeight = 0
        for child in self._children:
            size = child.sizeHint()
            w = size.width()
            h = size.height()
            if x + w > width:
                x = 0
                y += rowHeight
                rowHeight = 0
            rowHeight = max(rowHeight, h)
            if real:
                child.setGeometry(QtCore.QRect(x, y, w, h))
            x += w
        return y + rowHeight

    def heightForWidth(self, width):
        return self._doLayout(width, False)

    def sizeHint(self):
        width = 0
        height = 0
        for child in self._children:
            size = child.sizeHint()
            w = size.width()
            h = size.height()
            width += w
            height = max(height, h)
        return QtCore.QSize(width, height)

    def setGeometry(self, rect):
        self._doLayout(rect.width(), True)

    def expandingDirections(self):
        return QtCore.Qt.Vertical

    def minimumSize(self):
        if not self._children:
            return QtCore.QSize(0, 0)
        return self._children[0].sizeHint()


class FileSort(Sorter):
    """
    The default file sorting class. Can sort files on name,
    creation and modification date and size.

    It provides an interface for sorting files by
    reading metadata from them.
    """

    def __init__(self):
        super(FileSort, self).__init__()
        self._metaMethods = self.Methods()
        self._meta = {}

        self.methods = [
            ("name", os.path.basename),
            ("created", os.path.getctime),
            ("modified", os.path.getmtime),
            ("size", os.path.getsize)]

    def getMetaFields(self):
        return self._metaMethods.fields()

    def setMetaFields(self, mf):
        self._metaMethods = [(field,
            lambda filename: self._meta[filename][field]) for field in mf]

    metaFields = property(getMetaFields, setMetaFields)

    def fields(self):
        """
        Override Sorter.getFields to append the MetaFields at the result.
        """

        return super(FileSort, self).fields() + self.metaFields

    def getMethod(self, field):
        """
        Override Sorter.getMethod so that it also returns the ordering
        methods generated by the metadata.
        """

        if field in self.methods:
            return self.methods[field]
        else:
            return self._metaMethods[field]

    def sort(self, by, filenames):
        self.updateMeta(filenames)
        return super(FileSort, self).sort(by, filenames)

    def insert(self, by, filename, filenames):
        self.updateMeta(filenames + [filename])
        return super(FileSort, self).insert(by, filename, filenames)

    def updateMeta(self, filenames):
        for filename in filenames:
            try:
                if filename in self._meta and \
                self._meta[filename]['modified'] >= os.path.getmtime(filename):
                    continue
                self._meta[filename] = self.getMeta(filename)
                self._meta[filename]['modified'] = os.path.getmtime(filename)
            except IOError:
                log.warning("Filechooser could not update metadata of file %s (IO error)" % filename)

    def getMeta(self, filename):
        """
        Reads and returns a dictionary with metadata associated with the
        given file. To be overriden by classes using metadata.
        """

        return {}


class FileSortRadioButton(gui.RadioButton):
    def __init__(self, chooser, group, selected, field):
        gui.RadioButton.__init__(self, group, "By %s" % field, selected)
        self.field = field
        self.chooser = chooser

    def onClicked(self, event):
        self.chooser.sortBy = self.field
        self.chooser.refresh()

class TagFilter(gui.GroupBox):
    def __init__(self):
        super(TagFilter, self).__init__('Tag filter')
        self.tags = set()
        self.selectedTags = set()
        self.tagToggles = []

    def setTags(self, tags):
        self.clearAll()
        for tag in tags:
            self.addTag(tag)

    def addTag(self, tag):
        tag = tag.lower()
        if tag in self.tags:
            return

        self.tags.add(tag)
        toggle = self.addWidget(gui.CheckBox(tag.capitalize()))
        toggle.tag = tag
        self.tagToggles.append(toggle)

        @toggle.mhEvent
        def onClicked(event):
            self.setTagState(toggle.tag, toggle.selected)

    def addTags(self, tags):
        for tag in tags:
            self.addTag(tag)

    def setTagState(self, tag, enabled):
        tag = tag.lower()
        if tag not in self.tags:
            return

        if enabled:
            self.selectedTags.add(tag)
        else:
            self.selectedTags.remove(tag)

        self.callEvent('onTagsChanged', self.selectedTags)

    def clearAll(self):
        for tggl in self.tagToggles:
            tggl.hide()
            tggl.destroy()
        self.tagToggles = []
        self.selectedTags.clear()
        self.tags.clear()

    def getSelectedTags(self):
        return self.selectedTags

    def getTags(self):
        return self.tags

    def filterActive(self):
        return len(self.getSelectedTags()) > 0

    def filter(self, items):
        if not self.filterActive():
            for item in items:
                item.setHidden(False)
            return

        for item in items:
            #if len(self.selectedTags.intersection(file.tags)) > 0:  # OR
            if len(self.selectedTags.intersection(item.tags)) == len(self.selectedTags):  # AND
                item.setHidden(False)
            else:
                item.setHidden(True)

class FileHandler(object):
    def __init__(self):
        self.fileChooser = None

    def refresh(self, files):
        for file in files:
            label = getpath.pathToUnicode( os.path.basename(file) )
            if len(self.fileChooser.extensions) > 0:
                label = os.path.splitext(label)[0].replace('_', ' ').capitalize()
            label = label[0].capitalize() + label[1:]
            self.fileChooser.addItem(file, label, self.getPreview(file))

    def getSelection(self, item):
        return item.file

    def matchesItem(self, listItem, item):
        return abspath(listItem.file) == abspath(item)

    def matchesItems(self, listItem, items):
        return abspath(listItem.file) in [abspath(i) for i in items]

    def setFileChooser(self, fileChooser):
        self.fileChooser = fileChooser

    def getPreview(self, filename):
        fc = self.fileChooser

        if not filename:
            return fc.notFoundImage

        preview = filename
        if preview and fc.previewExtensions:
            #log.debug('%s, %s', fc.extension, fc.previewExtensions)
            preview = os.path.splitext(filename)[0]+ '.' + fc.previewExtensions[0]
            i = 1
            while not os.path.exists(preview) and i < len(fc.previewExtensions):
                preview = os.path.splitext(filename)[0] + '.' + fc.previewExtensions[i]
                i = i + 1

        if not os.path.isfile(preview) and fc.notFoundImage:
            # preview = os.path.join(fc.path, fc.notFoundImage)
            # TL: full filepath needed, so we don't look into user dir.
            preview = fc.notFoundImage

        return preview

class TaggedFileLoader(FileHandler):
    """
    Load files with tags, allowing to filter them with a tag filter.
    Requires a pointer to the library that handles items in the filechooser.
    This library object needs to implement a getTags(filename) method.
    """

    def __init__(self, library):
        super(TaggedFileLoader, self).__init__()
        self.library = library

    def refresh(self, files):
        """
        Load tags from mhclo file.
        """
        for file in files:
            label = getpath.pathToUnicode( os.path.basename(file) )
            if len(self.fileChooser.extensions) > 0:
                label = os.path.splitext(label)[0].replace('_', ' ')
            label = label[0].capitalize() + label[1:]
            tags = self.library.getTags(filename = file)
            self.fileChooser.addItem(file, label, self.getPreview(file), tags)

class MhmatFileLoader(FileHandler):

    def __init__(self):
        super(MhmatFileLoader, self).__init__()

    def getPreview(self, filename):
        # TODO this makes filechooser loading quite slow for materials without a thumbnail, but it does provide a preview
        thumb = super(MhmatFileLoader, self).getPreview(filename)
        if getpath.canonicalPath(thumb) == getpath.canonicalPath(self.fileChooser.notFoundImage):
            import material
            mat = material.fromFile(filename)
            if mat.diffuseTexture:
                return mat.diffuseTexture
        return thumb

class FileChooserBase(QtGui.QWidget, gui.Widget):

    def __init__(self, path, extensions, sort = FileSort(), doNotRecurse = False):
        super(FileChooserBase, self).__init__()
        gui.Widget.__init__(self)

        self.setPaths(path)
        if isinstance(extensions, basestring):
            self.extensions = [extensions]
        else:
            self.extensions = extensions
        self.previewExtensions = None
        self.notFoundImage = None
        self.doNotRecurse = doNotRecurse

        self.sort = sort
        self.sortBy = self.sort.fields()[0]
        self.sortgroup = []

        self.setFileLoadHandler(FileHandler())
        self.tagFilter = None

        self._autoRefresh = True
        self.mutexExtensions = False

    def createSortBox(self):
        sortBox = gui.GroupBox('Sort')

        self.refreshButton = sortBox.addWidget(gui.Button('Refresh'))
        for i, field in enumerate(self.sort.fields()):
            sortBox.addWidget(FileSortRadioButton(self, self.sortgroup, i == 0, field))

        @self.refreshButton.mhEvent
        def onClicked(value):
            self.refresh()

        return sortBox

    def createTagFilter(self):
        self.tagFilter = TagFilter()
        @self.tagFilter.mhEvent
        def onTagsChanged(selectedTags):
            self.applyTagFilter()

        return self.tagFilter

    def setPaths(self, value):
        self.paths = value if isinstance(value, list) else [value]

    def getPaths(self):
        return self.paths

    def setPreviewExtensions(self, value):
        if not value:
            self.previewExtensions = None
        elif isinstance(value, list):
            self.previewExtensions = value
        else:
            self.previewExtensions = [value]

    def _updateScrollBar(self):
        pass

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Resize:
            mh.callAsync(self._updateScrollBar)
        return False

    def search(self):
        return getpath.search(self.paths, self.extensions, 
                              recursive = not self.doNotRecurse, 
                              mutexExtensions = self.mutexExtensions)

    def clearList(self):
        for i in xrange(self.children.count()):
            child = self.children.itemAt(0)
            self._removeListItem(child)

    def refresh(self, keepSelections=True):
        self.clearList()

        files = set(self.search())
        files = self.sort.sort(self.sortBy, files)
        self.loadHandler.refresh(files)

        self.applyTagFilter()

        mh.redraw()
        self.callEvent('onRefresh', self)

    def applyTagFilter(self):
        if not self.tagFilter:
            return
        self.tagFilter.filter(self.children.getItems())
        self.children.updateGeometry()

    def _getListItem(self, item):
        for listItem in self.children.getItems():
            if self.loadHandler.matchesItem(listItem, item):
                return listItem
        return None

    def _removeListItem(self, listItem):
        self.children.removeItem(listItem)
        listItem.widget().hide()
        listItem.widget().destroy()

    def addTags(self, item, tags):
        tags = [t.lower() for t in tags]
        listItem = self._getListItem(item)
        if listItem:
            listItem.tags = listItem.tags.union(tags)

    def setTags(self, item, tags):
        tags = [t.lower() for t in tags]
        listItem = self._getListItem(item)
        if listItem:
            listItem.tags = tags

    def getAllTags(self):
        tags = set()
        for listItem in self.children.getItems():
            tags = tags.union(listItem.tags)
        return tags

    def setFileLoadHandler(self, loadHandler):
        loadHandler.setFileChooser(self)
        self.loadHandler = loadHandler

    def addItem(self, file, label, preview, tags = []):
        if self.tagFilter:
            self.tagFilter.addTags(tags)
        return None

    def removeItem(self, file):
        listItem = self._getListItem(file)
        if listItem is not None:
            self._removeListItem(listItem)

    def onShow(self, event):
        if self._autoRefresh:
            self.refresh()

    def enableAutoRefresh(self, enabled):
        """
        Set to true to auto perform refresh() when the filechooser widget
        receives an onShow() event. Enabled by default.
        """
        self._autoRefresh = enabled

class FileChooser(FileChooserBase):
    """
    A FileChooser widget. This widget can be used to let the user choose an existing file.

    :param path: The path from which the recursive search is started.
    :type path: str
    :param extension: The extension(s) of the files to display.
    :type extension: str or list
    :param previewExtension: The extension of the preview for the files. None if the file itself is to be used.
    :type previewExtension: str or None
    :param notFoundImage: The full filepath of the image to be used in case the preview is not found.
    :type notFoundImage: str or None
    :param sort: A file sorting instance which will be used to provide sorting of the found files.
    :type sort: FileSort
    """

    def __init__(self, path, extensions, previewExtensions='bmp', notFoundImage=None, sort=FileSort()):
        self.location = gui.TextView('')
        super(FileChooser, self).__init__(path, extensions, sort)

        self.setPreviewExtensions(previewExtensions)

        self.selection = ''
        self.childY = {}
        self.notFoundImage = notFoundImage
        # Try to find a "not found" icon if none is specified
        if not self.notFoundImage:
            for path in self.getPaths():
                imgPath = os.path.join(path, 'notfound.thumb')
                if os.path.isfile(imgPath):
                    self.notFoundImage = imgPath
                    break
        if not self.notFoundImage or not os.path.isfile(self.notFoundImage):
            imgPath = getpath.getSysDataPath('notfound.thumb')
            self.notFoundImage = imgPath

        self.layout = QtGui.QGridLayout(self)

        self.sortBox = self.createSortBox()
        self.layout.addWidget(self.sortBox, 0, 0)
        self.layout.setRowStretch(0, 0)
        self.layout.setColumnStretch(0, 0)

        self.layout.addWidget(QtGui.QWidget(), 1, 0)

        self.files_sc = QtGui.QScrollArea()
        self.files_sc.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.files_sc.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.layout.addWidget(self.files_sc, 0, 1, 2, -1)
        self.layout.setRowStretch(1, 1)
        self.layout.setColumnStretch(1, 1)

        self.files = QtGui.QWidget()
        self.files_sc.installEventFilter(self)
        self.files_sc.setWidget(self.files)
        self.files_sc.setWidgetResizable(True)
        self.children = FlowLayout(self.files)
        self.children.setSizeConstraint(QtGui.QLayout.SetMinimumSize)

        self.layout.addWidget(self.location, 2, 0, 1, -1)
        self.layout.setRowStretch(2, 0)

    def addItem(self, file, label, preview, tags=[], pos = None):
        item = FileChooserRectangle(self, file, label, preview)
        item.tags = tags
        self.children.addWidget(item)
        super(FileChooser, self).addItem(file, label, preview, tags)
        return item

    def setPaths(self, value):
        super(FileChooser, self).setPaths(value)
        locationLbl = "  |  ".join(self.paths)
        self.location.setText(abspath(locationLbl))


class ListFileChooser(FileChooserBase):

    def __init__(self, path, extensions, name="File chooser" , multiSelect=False, verticalScrolling=False, sort=FileSort(), noneItem = False, doNotRecurse = False):
        super(ListFileChooser, self).__init__(path, extensions, sort, doNotRecurse)
        self.listItems = []
        self.multiSelect = multiSelect
        self.noneItem = noneItem

        self.layout = QtGui.QGridLayout(self)
        self.mainBox = gui.GroupBox(name)
        self.children = gui.ListView()
        if self.multiSelect:
            self.children.allowMultipleSelection(True)
        self.layout.addWidget(self.mainBox)
        self.mainBox.addWidget(self.children)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        self.children.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.MinimumExpanding)
        self.children.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.children.setVerticalScrollingEnabled(verticalScrolling)

        # Remove frame and background color from list widget (native theme)
        self.children.setFrameShape(QtGui.QFrame.NoFrame)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255,255,255,0))
        self.children.setPalette(palette)

        @self.children.mhEvent
        def onClicked(item):
            self.callEvent('onFileSelected', self.loadHandler.getSelection(item))

        @self.children.mhEvent
        def onItemChecked(item):
            self.callEvent('onFileSelected', self.loadHandler.getSelection(item))

        @self.children.mhEvent
        def onItemUnchecked(item):
            self.callEvent('onFileDeselected', self.loadHandler.getSelection(item))

        @self.children.mhEvent
        def onClearSelection(value):
            self.callEvent('onDeselectAll', None)

    def resizeEvent(self, event):
        for listItem in self.children.getItems():
            listItem.updateTooltip()

    def setVerticalScrollingEnabled(self, enabled):
            self.children.setVerticalScrollingEnabled(enabled)

    def createSortBox(self):
        self.sortBox = super(ListFileChooser, self).createSortBox()
        if self.multiSelect:
            deselectAllBtn = self.sortBox.addWidget(gui.Button('Deselect all'))
            @deselectAllBtn.mhEvent
            def onClicked(value):
                self.deselectAll()
        return self.sortBox

    def addItem(self, file, label, preview, tags=[], pos = None):
        item = gui.ListItem(label)
        item.file = file
        item.preview = preview
        item.tags = tags
        super(ListFileChooser, self).addItem(file, label, preview, tags)
        return self.children.addItemObject(item, pos)

    def getHighlightedItem(self):
        items = self.children.selectedItems()
        if len(items) > 0:
            return self.loadHandler.getSelection(items[0])
        else:
            return None

    def getSelectedItem(self):
        return self.getHighlightedItem()

    def getSelectedItems(self):
        items = self.children.selectedItems()
        return [self.loadHandler.getSelection(item) for item in items]

    def selectItem(self, item):
        if self.multiSelect:
            if not self.isSelected(item):
                selections = self.getSelectedItems()
                selections.append(item)
                self.setSelections(selections)
        else:
            self.setSelection(item)

    def isSelected(self, item):
        listItem = self._getListItem(item)
        if listItem is None:
            return False
        return listItem.isSelected()

    def deselectItem(self, item):
        if self.isSelected(item):
            if self.multiSelect:
                listItem = self._getListItem(item)
                selections = self.getSelectedItems()
                selections.remove( self.loadHandler.getSelection(listItem) )
                self.setSelections(selections)
            else:
                self.deselectAll()

    def setSelection(self, item):
        if self.multiSelect:
            return

        self.deselectAll()

        for listItem in self.children.getItems():
            if self.loadHandler.matchesItem(listItem, item):
                self.children.setCurrentItem(listItem)
                return

    def contains(self, item):
        for listItem in self.children.getItems():
            if self.loadHandler.matchesItem(listItem, item):
                return True
        return False

    def setSelections(self, items):
        if not self.multiSelect:
            return

        for listItem in self.children.getItems():
            listItem.setChecked( self.loadHandler.matchesItems(listItem, items) )

    def setHighlightedItem(self, item):
        if item != None:
            for listItem in self.children.getItems():
                if self.loadHandler.matchesItem(listItem, item):
                    self.children.setCurrentItem(listItem)
                    return
        else:
            self.children.setCurrentItem(None)

    def deselectAll(self):
        # TODO emit event
        self.children.clearSelection()

    def clearList(self):
        self.children.clear()

    def setFocus(self):
        self.children.setFocus()

    def refresh(self, keepSelections=True):
        if keepSelections:
            selections = self.getSelectedItems()
            if self.multiSelect:
                highLighted = self.getHighlightedItem()
        else:
            self.deselectAll()

        super(ListFileChooser, self).refresh()

        # Add None item
        if not self.multiSelect and self.noneItem:
            if not self.clearImage or not os.path.isfile(self.clearImage):
                if self.notFoundImage:
                    ext = os.path.splitext(self.notFoundImage)[1]
                    clearIcon = os.path.join(os.path.dirname(self.notFoundImage), 'clear'+ext)
                else:
                    clearIcon = getpath.getSysDataPath('clear.thumb')
            else:
                clearIcon = self.clearImage
            self.addItem(None, "None", clearIcon, pos = 0)

        for listItem in self.children.getItems():
            listItem.updateTooltip()

        if keepSelections:
            if self.multiSelect:
                self.setSelections(selections)
                self.setHighlightedItem(highLighted)
            elif len(selections) > 0:
                self.setSelection(selections[0])

class IconListFileChooser(ListFileChooser):
    def __init__(self, path, extensions, previewExtensions='bmp', notFoundImage=None, clearImage=None, name="File chooser", multiSelect=False, verticalScrolling=False, sort=FileSort(), noneItem = False, doNotRecurse = False):
        super(IconListFileChooser, self).__init__(path, extensions, name, multiSelect, verticalScrolling, sort, noneItem, doNotRecurse)
        self.setPreviewExtensions(previewExtensions)
        self.notFoundImage = notFoundImage
        self.clearImage = clearImage
        self._iconCache = {}
        #self.children.setIconSize(QtCore.QSize(50,50))
        self.setIconSize(50,50)
        self.children.setWordWrap(True)

    def addItem(self, file, label, preview, tags=[], pos = None):
        item = super(IconListFileChooser, self).addItem(file, label, preview, tags, pos)
        preview = getpath.pathToUnicode(preview)
        mtime = os.path.getmtime(preview) if os.path.isfile(preview) else 0
        if preview not in self._iconCache or mtime > self._iconCache[preview][1]:
            pixmap = QtGui.QPixmap(preview)
            size = pixmap.size()
            if size.width() > 128 or size.height() > 128:
                pixmap = pixmap.scaled(128, 128, QtCore.Qt.KeepAspectRatio)
            icon = QtGui.QIcon(pixmap)
            icon.addPixmap(pixmap, QtGui.QIcon.Selected)    # make sure that the icon does not change color when item is highlighted
            self._iconCache[preview] = (icon, mtime)
        icon = self._iconCache[preview][0]
        item.setIcon(icon)
        return item

    def setIconSize(self, width, height):
        self.children.setIconSize(QtCore.QSize(width, height))

def abspath(path):
    """
    Helper function to determine canonical path if a valid (not None) pathname
    is specified.
    Canonical pathnames are used for reliable comparison of two paths.
    """
    if path:
        return getpath.canonicalPath(path)
    else:
        return None
