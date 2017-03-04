#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
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

Common base class for all proxy chooser libraries.
"""

import os
import gui3d
import gui
import events3d
import mh
import files3d
import proxy
import filechooser as fc
import log
import getpath
import filecache


class ProxyAction(gui3d.Action):
    def __init__(self, name, library, before, after):
        super(ProxyAction, self).__init__(name)
        self.library = library
        self.before = before
        self.after = after

    def do(self):
        self.library.selectProxy(self.after)
        return True

    def undo(self):
        self.library.selectProxy(self.before)
        return True


class MultiProxyAction(gui3d.Action):
    def __init__(self, name, library, mhcloFile, add):
        super(MultiProxyAction, self).__init__(name)
        self.library = library
        self.mhclo = mhcloFile
        self.add = add

    def do(self):
        if self.add:
            self.library.selectProxy(self.mhclo)
        else:
            self.library.deselectProxy(self.mhclo)
        return True

    def undo(self):
        if self.add:
            self.library.deselectProxy(self.mhclo)
        else:
            self.library.selectProxy(self.mhclo)
        return True


class ProxyChooserTaskView(gui3d.TaskView, filecache.MetadataCacher):
    """
    Common base class for all proxy chooser libraries.
    """

    def __init__(self, category, proxyName, tabLabel = None, multiProxy = False, tagFilter = False, descriptionWidget = False):
        if not tabLabel:
            tabLabel = proxyName.capitalize()
        proxyName = proxyName.lower().replace(" ", "_")
        self.proxyName = proxyName
        gui3d.TaskView.__init__(self, category, tabLabel)
        filecache.MetadataCacher.__init__(self, self.getFileExtension(), self.proxyName + '_filecache.mhc')

        self.label = tabLabel
        self.multiProxy = multiProxy
        self.tagFilter = tagFilter
        self.descriptionWidget = descriptionWidget

        self.homeProxyDir = getpath.getPath(os.path.join('data', proxyName))
        self.sysProxyDir = mh.getSysDataPath(proxyName)

        if not os.path.exists(self.homeProxyDir):
            os.makedirs(self.homeProxyDir)

        self.paths = [self.homeProxyDir , self.sysProxyDir]

        self.human = gui3d.app.selectedHuman

        self._proxyFilePerUuid = None

        self.selectedProxies = []

        self.createFileChooser()


    def createFileChooser(self):
        """
        Overwrite to do custom initialization of filechooser widget.
        """
        #self.filechooser = self.addTopWidget(fc.FileChooser(self.paths, 'mhclo', 'thumb', mh.getSysDataPath(proxyName+'/notfound.thumb')))
        notfoundIcon = self.getNotFoundIcon()
        if not os.path.isfile(notfoundIcon):
            notfoundIcon = getpath.getSysDataPath('notfound.thumb')

        if self.multiProxy:
            clearIcon = None
        else:
            clearIcon = self.getClearIcon()
            if not os.path.isfile(clearIcon):
                clearIcon = getpath.getSysDataPath('clear.thumb')

        self.filechooser = fc.IconListFileChooser(self.paths, self.getFileExtension(), 'thumb', notfoundIcon, clearIcon, name=self.label, multiSelect=self.multiProxy, noneItem = not self.multiProxy)
        self.addRightWidget(self.filechooser)

        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(False)
        if not isinstance(self.getFileExtension(), basestring) and \
           len(self.getFileExtension()) > 1:
            self.filechooser.mutexExtensions = True
        #self.addLeftWidget(self.filechooser.createSortBox())

        if self.tagFilter:
            self.filechooser.setFileLoadHandler(fc.TaggedFileLoader(self))
            self.addLeftWidget(self.filechooser.createTagFilter())

        if self.descriptionWidget:
            descBox = self.addLeftWidget(gui.GroupBox('Description'))
            self.descrLbl = descBox.addWidget(gui.TextView(''))
            self.descrLbl.setSizePolicy(gui.QtGui.QSizePolicy.Ignored, gui.QtGui.QSizePolicy.Preferred)
            self.descrLbl.setWordWrap(True)

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            self.proxyFileSelected(filename)

        if self.multiProxy:
            @self.filechooser.mhEvent
            def onFileDeselected(filename):
                self.proxyFileDeselected(filename)

            @self.filechooser.mhEvent
            def onDeselectAll(value):
                self.deselectAllProxies()

    def getMetadataImpl(self, filename):
        return proxy.peekMetadata(filename, self.getProxyType())

    def getTagsFromMetadata(self, metadata):
        uuid, tags = metadata
        return tags

    def getSearchPaths(self):
        return self.paths

    def getSaveName(self):
        """
        The name used by save and load handlers to store the proxy mesh.
        """
        return self.proxyName

    def getFileExtension(self):
        """
        The file extension for proxy files of this type.
        Order determines precedence: the first extension in the list is preferred.
        """
        return ['mhpxy', 'mhclo']

    def getProxyType(self):
        """
        The type name of the proxies this library manages.
        """
        return self.proxyName.capitalize()

    def getNotFoundIcon(self):
        """
        The default icon to show when no icon is found for a proxy in this
        library.
        If this icon does not exist either, it will show the default icon in
        data/notfound.thumb
        """
        return os.path.join(self.sysProxyDir, 'notfound.thumb')

    def getClearIcon(self):
        """
        The icon to show for the "select None" entry in the filechooser of this
        library. Only applies when this is not a multiselect library (not self.multiProxy).
        If this icon does not exist, it will show the default icon in
        data/clear.thumb
        """
        return os.path.join(self.sysProxyDir, 'clear.thumb')

    def proxyFileSelected(self, filename):
        """
        Called when user selects a file from the filechooser widget.
        Creates an action that invokes selectProxy().
        """
        if self.multiProxy:
            action = MultiProxyAction("Change %s" % self.proxyName,
                                      self,
                                      filename,
                                      True)
        else:
            if self.isProxySelected():
                oldFile = self.getSelection()[0].file
            else:
                oldFile = None
            action = ProxyAction("Change %s" % self.proxyName,
                                 self,
                                 oldFile,
                                 filename)
        gui3d.app.do(action)

    def proxyFileDeselected(self, filename):
        """
        Called when user deselects a file from the filechooser widget.
        Creates an action that invokes deselectProxy().
        This method only has effect when this library allows multiple proxy
        selection.
        """
        if not self.multiProxy:
            return

        action = MultiProxyAction("Change %s" % self.proxyName,
                                  self,
                                  filename,
                                  False)
        gui3d.app.do(action)

    def getObjectLayer(self):
        """
        Returns the rendering depth order with which objects of this proxy type
        should be rendered.
        Will be used as mesh rendering priority.
        """
        # TODO remove, this is bogus
        raise NotImplementedError("Implement ProxyChooserTaskView.getObjectLayer()!")

    def proxySelected(self, pxy):
        """
        Do custom work specific to this library when a proxy object was loaded.
        """
        raise NotImplementedError("Implement ProxyChooserTaskView.proxySelected()!")

    def proxyDeselected(self, pxy, suppressSignal = False):
        """
        Do custom work specific to this library when a proxy object was unloaded.
        """
        raise NotImplementedError("Implement ProxyChooserTaskView.proxyDeselected()!")

    def selectProxy(self, mhclofile):
        """
        Called when a new proxy has been selected.
        If this library selects only a single proxy, specifying None as
        mhclofile parameter will deselect the current proxy and set the selection
        to "none".
        If this library allows selecting multiple proxies, specifying None as
        mhclofile will have no effect.
        """
        if not mhclofile:
            if self.multiProxy:
                return
            else:
                self.deselectProxy(None)
                return

        log.message('Selecting proxy file "%s" from %s library.', mhclofile, self.proxyName)
        human = self.human

        pxy = proxy.loadProxy(human, mhclofile, type=self.getProxyType())

        if pxy.uuid in [p.uuid for p in self.getSelection() if p is not None]:
            log.debug("Proxy with UUID %s (%s) already loaded in %s library. Skipping.", pxy.uuid, pxy.file, self.proxyName)
            return

        if not self.multiProxy and self.isProxySelected():
            # Deselect previously selected proxy
            self.deselectProxy(None, suppressSignal = True)

        mesh,obj = pxy.loadMeshAndObject(human)
        mesh.setPickable(True)  # Allow mouse picking for proxies attached to human
        
        if not mesh:
            return

        gui3d.app.addObject(obj)

        self.filechooser.selectItem(mhclofile)
        self.filechooser.selectItem( self.getAlternativeFile(mhclofile) )  # In case an ascii or binary file was loaded instead

        self.adaptProxyToHuman(pxy, obj)
        obj.setSubdivided(human.isSubdivided()) # Copy subdivided state of human

        # Add to selection
        self.selectedProxies.append(pxy)

        self.filechooser.selectItem(mhclofile)

        if self.descriptionWidget:
            self.descrLbl.setText(pxy.description)

        self.proxySelected(pxy)

        self.signalChange()

    def deselectProxy(self, mhclofile, suppressSignal = False):
        """
        Deselect specified proxy from library selections. If this library only
        supports selecting a single proxy, the mhclofile parameter is ignored,
        and it will just deselected the currently selected proxy.
        """
        if self.multiProxy:
            idx = self._getProxyIndex(mhclofile)
            if idx == None:
                return
        else:
            if self.isProxySelected():
                idx = 0
            else:
                return

        pxy = self.selectedProxies[idx]
        obj = pxy.object
        gui3d.app.removeObject(obj)
        del self.selectedProxies[idx]
        self.filechooser.deselectItem(mhclofile)
        self.filechooser.deselectItem( self.getAlternativeFile(mhclofile) )  # In case an ascii or binary file was loaded instead

        self.proxyDeselected(pxy, suppressSignal)
        pxy.object = None   # Drop pointer to object

        if not self.multiProxy:
            # Select None item in file list
            self.filechooser.selectItem(None)

        if not suppressSignal:
            self.signalChange()

    def deselectAllProxies(self):
        selectionsCopy = list(self.getSelection())
        for p in selectionsCopy:
            self.deselectProxy(p.file, suppressSignal = True)
        self.signalChange()

    def isProxySelected(self):
        return len(self.getSelection()) > 0

    def getSelection(self):
        """
        Return the selected proxies as a list.
        If no proxy is selected, returns empty list.
        If this is library allows selecting multiple proxies, the list can
        contain multiple entries, if this is library allows selecting only a
        single proxy, the list is either of length 0 or 1.
        """
        return list(self.selectedProxies)

    def getObjects(self):
        """
        Returns a list of objects beloning to the proxies returned by getSelection()
        The order corresponds with that of getSelection().
        """
        return [pxy.object for pxy in self.getSelection()]

    def hideObjects(self):
        """
        Hide the objects created by selected proxies in this library.
        """
        for obj in self.getObjects():
            obj.mesh.visibility = False

    def showObjects(self):
        """
        Show the objects created by selected proxies in this library
        (make visible).
        """
        for obj in self.getObjects():
            obj.mesh.visibility = True

    def _getProxyIndex(self, mhcloFile):
        """
        Get the index of specified mhclopath within the list returned by getSelection()
        Returns None if the proxy of specified path is not in selection.
        """
        mhcloFile = getpath.canonicalPath(mhcloFile)
        altFile = getpath.canonicalPath(self.getAlternativeFile(mhcloFile))
        for pIdx, p in enumerate(self.getSelection()):
            if getpath.canonicalPath(p.file) in [mhcloFile, altFile]:
                return pIdx
        return None

    def getAlternativeFile(self, filename):
        """
        If a path to a compiled proxy file is given, returns the ascii version,
        if the ascii version path is given, returns the path to the compiled
        binary proxy file.
        """
        if not filename:
            return filename 
        if os.path.splitext(filename)[1] == '.mhpxy':
            return os.path.splitext(filename)[0] + self.getAsciiFileExtension()
        else:
            return os.path.splitext(filename)[0] + '.mhpxy'

    def getAsciiFileExtension(self):
        """
        The file extension used for ASCII (non-compiled) proxy source files
        for the proxies managed by this library.
        """
        return proxy.getAsciiFileExtension(self.getProxyType())

    def resetSelection(self):
        """
        Undo selection of all proxies.
        """
        if not self.isProxySelected():
            return

        #self.filechooser.deselectAll()
        self.deselectAllProxies()

    def adaptProxyToHuman(self, pxy, obj, updateSubdivided=True, fit_to_posed=False, fast=False):
        mesh = obj.getSeedMesh()
        pxy.update(mesh, fit_to_posed, fast)
        mesh.update()
        # Update subdivided mesh if smoothing is enabled
        if updateSubdivided and obj.isSubdivided():
            obj.getSubdivisionMesh()

    def signalChange(self):
        human = self.human
        event = events3d.HumanEvent(human, 'proxy')
        event.pxy = self.proxyName
        human.callEvent('onChanged', event)

    def onShow(self, event):
        if self._filecache is None:
            # Init cache
            self.loadCache()
            self.updateFileCache(self.getSearchPaths(), self.getFileExtensions())

        # When the task gets shown, set the focus to the file chooser
        gui3d.TaskView.onShow(self, event)
        self.filechooser.refresh()
        selectedProxies = self.getSelection()
        if len(selectedProxies) > 1:
            fnames = [p.file for p in selectedProxies] + \
                     [self.getAlternativeFile(p.file) for p in selectedProxies]
            self.filechooser.setSelections(fnames)
        elif len(selectedProxies) > 0:
            proxypath = selectedProxies[0].file
            if self.filechooser.contains(proxypath):
                self.filechooser.selectItem(proxypath)
            else:
                self.filechooser.selectItem(self.getAlternativeFile(proxypath))
        elif not self.multiProxy:
            # Select "None" item in list
            self.filechooser.selectItem(None)
        self.filechooser.setFocus()

    def onHide(self, event):
        gui3d.TaskView.onHide(self, event)

    def onHumanChanged(self, event):
        if event.change == 'reset':
            self.resetSelection()
        if event.change in ['targets', 'modifier']:
            for obj in self.getObjects():
                if obj.isSubdivided():
                    obj.getSeedMesh().setVisibility(0)
                    obj.getSubdivisionMesh(False).setVisibility(1)

            self.showObjects() # Make sure objects are shown again after onHumanChanging events
            #log.debug("Human changed, adapting all proxies (event: %s)", event)
            self.adaptAllProxies()
        if event.change in ['poseRefresh']:
            # Update subdivided proxies after posing
            for obj in self.getObjects():
                if obj.isSubdivided():
                    obj.getSubdivisionMesh()

    def onHumanChanging(self, event):
        if event.change == 'modifier':
            if gui3d.app.getSetting('realtimeFitting'):
                self.adaptAllProxies(updateSubdivided=False, fit_to_posed=True, fast=True)
                for obj in self.getObjects():
                    if obj.isSubdivided():
                        obj.getSeedMesh().setVisibility(1)
                        obj.getSubdivisionMesh(False).setVisibility(0)
            else:
                self.hideObjects()

    def adaptAllProxies(self, updateSubdivided=True, fit_to_posed=False, fast=False):
        proxyCount = len(self.getSelection())
        if proxyCount > 0:
            pass  #log.message("Adapting all %s proxies (%s).", self.proxyName, proxyCount)
        for pIdx, pxy in enumerate(self.getSelection()):
            obj = self.getObjects()[pIdx]
            self.adaptProxyToHuman(pxy, obj, updateSubdivided, fit_to_posed, fast)

    def loadHandler(self, human, values, strict):
        if values[0] == 'status':
            return

        if self._filecache is None:
            # Init cache
            self.loadCache()
            self.updateFileCache(self.getSearchPaths(), self.getFileExtensions(), True)

        if values[0] == self.getSaveName():
            if len(values) >= 3:
                name = values[1]
                uuid = values[2]
                proxyFile = self.findProxyByUuid(uuid)
                if not proxyFile:
                    if strict:
                        raise RuntimeError("%s library could not load %s proxy with UUID %s, file not found." % (self.proxyName, name, uuid))
                    log.warning("%s library could not load %s proxy with UUID %s, file not found.", self.proxyName, name, uuid)
                    return
                self.selectProxy(proxyFile)
            else:
                filename = values[1]
                log.error("Not loading %s %s. Loading proxies from filename is no longer supported, they need to be referenced by UUID.", self.proxyName, filename)

    def saveHandler(self, human, file):
        for pxy in self.getSelection():
            file.write('%s %s %s\n' % (self.getSaveName(), pxy.name, pxy.getUuid()))

    def findProxyMetadataByFilename(self, path):
        """
        Retrieve proxy metadata by canonical path from metadata cache.
        Returns None or metadata in the form: (mtime, uuid, tags)
        """
        proxyId = getpath.canonicalPath(path)

        if self._filecache is None:
            # Init cache
            self.loadCache()
            self.updateFileCache(self.getSearchPaths(), self.getFileExtensions(), True)

        if self._proxyFilePerUuid is None:
            self._loadUuidLookup()

        if proxyId not in self._filecache:
            # Try again once more, but update the metadata cache first (lazy cache for performance reasons)
            self.updateFileCache(self.getSearchPaths(), self.getFileExtensions(), True)
            self._loadUuidLookup()

            if proxyId not in self._filecache:
                log.warning('Could not get metadata for proxy with filename %s. Does not exist in %s library.', proxyId, self.proxyName)
                return None

        metadata = self._filecache[proxyId]
        mtime = metadata[0]
        if mtime < os.path.getmtime(proxyId):
            # Queried file was updated, update stale cache
            self.updateFileCache(self.getSearchPaths(), self.getFileExtensions(), True)
            self._loadUuidLookup()
            metadata = self._filecache[proxyId]

        return metadata

    def findProxyByUuid(self, uuid):
        """
        Find proxy file in this library by UUID.
        Proxy files can only be found if they are in the file metadata cache.
        Returns the path of the proxy file if it is found, else returns None.
        The returned path is a canonical path name.
        """
        if self._filecache is None:
            # Init cache
            self.loadCache()
            self.updateFileCache(self.getSearchPaths(), self.getFileExtensions(), True)

        if self._proxyFilePerUuid is None:
            self._loadUuidLookup()

        if uuid not in self._proxyFilePerUuid:
            # Try again once more, but update the proxy UUID lookup table first (lazy cache for performance reasons)
            self.updateFileCache(self.getSearchPaths(), self.getFileExtensions(), True)
            self._loadUuidLookup()
            if uuid not in self._proxyFilePerUuid:
                log.warning('Could not find a proxy with UUID %s. Does not exist in %s library.', uuid, self.proxyName)
                return None

        return self._proxyFilePerUuid[uuid]

    def _loadUuidLookup(self):
        items = [ (values[1], path) for (path, values) in self._filecache.items() ]
        self._proxyFilePerUuid = dict()
        for (_uuid, path) in items:
            if _uuid in self._proxyFilePerUuid and self._proxyFilePerUuid[_uuid] != path:
                log.warning("WARNING: Duplicate UUID found for different proxy files in %s library (files %s and %s share uuid %s). Make sure that all proxy files in your data folders have unique UUIDs (unless they are exactly the same file). Else this may lead to unexpected behaviour.", self.proxyName, path, self._proxyFilePerUuid[_uuid], _uuid)
            self._proxyFilePerUuid[_uuid] = path

    def getTags(self, uuid = None, filename = None):
        """
        Get tags associated with proxies.
        When no uuid and filename are specified, returns the all the tags found
        in this collection (all proxy files managed by this library).
        Specify a filename or uuid to get all tags belonging to that proxy file.
        Always returns a set of tags (so contains no duplicates), unless no proxy
        was found upon which None is returned.
        An empty library (no proxies) or a library where no proxy file contains
        tags will always return an empty set.
        """
        if uuid and filename:
            raise RuntimeWarning("getTags: Specify either uuid or filename, not both!")

        if uuid:
            proxyFile = self.findProxyByUuid(uuid)
            if not proxyFile:
                log.warning('Could not get tags for proxy with UUID %s. Does not exist in %s library.', uuid, self.proxyName)
                return set()
            filecache.MetadataCacher.getTags(self, proxyFile)
        elif filename:
            return filecache.MetadataCacher.getTags(self, filename)
        else:
            return self.getAllTags()

    def registerLoadSaveHandlers(self):
        gui3d.app.addLoadHandler(self.getSaveName(), self.loadHandler)
        priority = 2    # Make sure proxy choosers come before material library
        gui3d.app.addSaveHandler(self.saveHandler, priority)

