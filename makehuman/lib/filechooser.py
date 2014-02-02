#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Qt filechooser widget.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Glynn Clements, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

A Qt based filechooser widget.
"""

import os

from PyQt4 import QtCore, QtGui

import qtgui as gui
import mh
import getpath

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
        self.preview.setPixmap(image)
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

class FileSort(object):
    """
    The default file sorting class. Can sort files on name, creation and modification date and size.
    """
    def __init__(self):
        pass

    def fields(self):
        """
        Returns the names of the fields on which this FileSort can sort. For each field it is assumed that the method called sortField exists.

        :return: The names of the fields on which this FileSort can sort.
        :rtype: list or tuple
        """
        return ("name", "created", "modified", "size")

    def sort(self, by, filenames):
        method = getattr(self, "sort%s" % by.capitalize())
        return method(filenames)

    def sortName(self, filenames):
        decorated = [(os.path.basename(filename), i, filename) for i, filename in enumerate(filenames)]
        return self._decoratedSort(decorated)

    def sortModified(self, filenames):
        decorated = [(os.path.getmtime(filename), i, filename) for i, filename in enumerate(filenames)]
        return self._decoratedSort(decorated)

    def sortCreated(self, filenames):
        decorated = [(os.path.getctime(filename), i, filename) for i, filename in enumerate(filenames)]
        return self._decoratedSort(decorated)

    def sortSize(self, filenames):
        decorated = [(os.path.getsize(filename), i, filename) for i, filename in enumerate(filenames)]
        return self._decoratedSort(decorated)

    def _decoratedSort(self, toSort):
        toSort.sort()
        return [filename for sortKey, i, filename in toSort]

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
            label = os.path.basename(file)
            if isinstance(self.fileChooser.extension, str):
                label = os.path.splitext(label)[0]
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
            preview = filename.replace('.' + fc.extension, '.' + fc.previewExtensions[0])
            i = 1
            while not os.path.exists(preview) and i < len(fc.previewExtensions):
                preview = filename.replace('.' + fc.extension, '.' + fc.previewExtensions[i])
                i = i + 1

        if not os.path.exists(preview) and fc.notFoundImage:
            # preview = os.path.join(fc.path, fc.notFoundImage)
            # TL: full filepath needed, so we don't look into user dir.
            preview = fc.notFoundImage

        return preview

class TaggedFileLoader(FileHandler):
    """
    Load files with tags, allowing to filter them with a tag filter.
    """

    def __init__(self, library):
        super(TaggedFileLoader, self).__init__()
        self.library = library

    def refresh(self, files):
        """
        Load tags from mhclo file.
        """
        import exportutils.config
        for file in files:
            label = os.path.basename(file)
            if isinstance(self.fileChooser.extension, str):
                label = os.path.splitext(label)[0]
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

    def __init__(self, path, extension, sort = FileSort(), doNotRecurse = False):
        super(FileChooserBase, self).__init__()
        gui.Widget.__init__(self)

        self.setPaths(path)
        self.extension = extension
        self.previewExtensions = None
        self.notFoundImage = None
        self.doNotRecurse = doNotRecurse

        self.sort = sort
        self.sortBy = self.sort.fields()[0]
        self.sortgroup = []

        self.setFileLoadHandler(FileHandler())
        self.tagFilter = None

        self._autoRefresh = True

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
        if isinstance(self.extension, str):
            extensions = [self.extension]
        else:
            extensions = self.extension

        if self.doNotRecurse:
            for path in self.paths:
                if not os.path.isdir(path):
                    continue
                for f in os.listdir(path):
                    f = os.path.join(path, f)
                    if os.path.isfile(f):
                        ext = os.path.splitext(f)[1][1:].lower()
                        if ext in extensions:
                            yield f
        else:
            for path in self.paths:
                for root, dirs, files in os.walk(path):
                    for f in files:
                        ext = os.path.splitext(f)[1][1:].lower()
                        if ext in extensions:
                            if f.lower().endswith('.' + ext):
                                yield os.path.join(root, f)

    def clearList(self):
        for i in xrange(self.children.count()):
            child = self.children.itemAt(0)
            self.children.removeItem(child)
            child.widget().hide()
            child.widget().destroy()

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

    def __init__(self, path, extension, previewExtensions='bmp', notFoundImage=None, sort=FileSort()):
        self.location = gui.TextView('')
        super(FileChooser, self).__init__(path, extension, sort)

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

    def __init__(self, path, extension, name="File chooser" , multiSelect=False, verticalScrolling=False, sort=FileSort(), noneItem = False, doNotRecurse = False):
        super(ListFileChooser, self).__init__(path, extension, sort, doNotRecurse)
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
            selections = self.getSelectedItems()
            if item not in selections:
                selections.append(item)
                self.setSelections(selections)
        else:
            self.setSelection(item)

    def deselectItem(self, item):
        selections = self.getSelectedItems()
        if item in selections:
            if self.multiSelect:
                selections.remove(item)
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
    def __init__(self, path, extension, previewExtensions='bmp', notFoundImage=None, clearImage=None, name="File chooser", multiSelect=False, verticalScrolling=False, sort=FileSort(), noneItem = False, doNotRecurse = False):
        super(IconListFileChooser, self).__init__(path, extension, name, multiSelect, verticalScrolling, sort, noneItem, doNotRecurse)
        self.setPreviewExtensions(previewExtensions)
        self.notFoundImage = notFoundImage
        self.clearImage = clearImage
        self._iconCache = {}
        #self.children.setIconSize(QtCore.QSize(50,50))
        self.setIconSize(50,50)

    def addItem(self, file, label, preview, tags=[], pos = None):
        item = super(IconListFileChooser, self).addItem(file, label, preview, tags, pos)
        if preview not in self._iconCache:
            pixmap = QtGui.QPixmap(preview)
            size = pixmap.size()
            if size.width() > 128 or size.height() > 128:
                pixmap = pixmap.scaled(128, 128, QtCore.Qt.KeepAspectRatio)
            icon = QtGui.QIcon(pixmap)
            icon.addPixmap(pixmap, QtGui.QIcon.Selected)    # make sure that the icon does not change color when item is highlighted
            self._iconCache[preview] = icon
        icon = self._iconCache[preview]
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
