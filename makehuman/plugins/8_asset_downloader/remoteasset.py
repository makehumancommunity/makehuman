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
import calendar, datetime

from progress import Progress

from core import G

from .meshAssetSubdirs import ALL_CORE_ASSET_DIRS_WITH_MATERIALS_AS_TEXT

mhapi = gui3d.app.mhapi

fileForType = {}
fileForType["material"] = "mhmat"
fileForType["model"] = "mhm"
fileForType["clothes"] = "mhclo"
fileForType["hair"] = "mhclo"
fileForType["teeth"] = "mhclo"
fileForType["eyebrows"] = "mhclo"
fileForType["eyelashes"] = "mhclo"
fileForType["tongue"] = "mhclo"
fileForType["eyes"] = "mhclo"
fileForType["proxy"] = "file"
fileForType["skin"] = "mhmat"
fileForType["pose"] = "bvh"
fileForType["expression"] = "mhpose"
fileForType["rig"] = "mhskel"
fileForType["target"] = "file"


class RemoteAsset():

    def __init__(self, parent, json, assetdb=None):

        self.assetdb = assetdb
        self.cachedDestination = None
        self.parent = parent
        self.rawJson = json
        self.log = mhapi.utility.getLogChannel("assetdownload")

        self._parseGeneric()

        if self.type == "clothes":
            self._parseClothes()

        if self.type == "material":
            self._parseMaterials()

        self.root = os.path.join(self.parent.root,str(self.nid))
        if not os.path.exists(self.root):
            os.makedirs(self.root)

        self._parseFiles()

    def _getJsonKey(self,name,default):

        self.log.spam("Enter")

        out = default
        if name in self.rawJson:
            out = self.rawJson[name]
        return out

    def _parseGeneric(self):

        self.log.trace("Enter")

        self.type = self._getJsonKey("type", "unknown")
        self.license = self._getJsonKey("license", "unknown")
        self.title = self._getJsonKey("title","-- unknown title --")
        self.description = self._getJsonKey("description", "--")
        self.username = self._getJsonKey("username","unknown author")
        self.uid = self._getJsonKey("uid",-1)
        self.nid = self._getJsonKey("nid",-1)
        self.changed = self._getJsonKey("changed",None)
        self.created = self._getJsonKey("created",None)

    def _parseClothes(self):

        self.category = self._getJsonKey("category", "").lower()

        if self.category == "eyebrows":
            self.type = "eyebrows"

        if self.category == "eyelashes":
            self.type = "eyelashes"

        if self.category == "teeth":
            self.type = "teeth"

        if self.category == "hair":
            self.type = "hair"

    def _parseMaterials(self):

        self.belongs_to_metadata = self._getJsonKey("belongs_to", {})

        self.log.spam("belonging", self.belongs_to_metadata)

        if not "belonging_is_assigned" in self.belongs_to_metadata or not self.belongs_to_metadata["belonging_is_assigned"]:
            self.belongs_to_metadata["belonging_is_assigned"] = False
            return

        if "belongs_to_core_asset" in self.belongs_to_metadata:
            self.log.trace("Belongs to core asset")

            caTarget = self.belongs_to_metadata["belongs_to_core_asset"].strip()
            if not caTarget or caTarget == "" or not caTarget in ALL_CORE_ASSET_DIRS_WITH_MATERIALS_AS_TEXT:
                self.log.debug("Assigned, but not in permitted list: ", caTarget)
                return
            else:
                self.log.debug("Permitted for core asset: ", caTarget)
                udp = mhapi.locations.getUserDataPath()
                parts = caTarget.split("/")
                self.cachedDestination = os.path.abspath( os.path.join(udp, parts[0], parts[1]) )
                self.log.debug("Override installation path",self.cachedDestination)

        if "belongs_to_id" in self.belongs_to_metadata:
            if self.belongs_to_metadata["belongs_to_id"] in self.assetdb.assetsById:
                targetAsset = self.assetdb.assetsById[self.belongs_to_metadata["belongs_to_id"]]
                self.log.debug("Target asset", targetAsset.getTitle())
                self.log.debug("Target asset ID", targetAsset.getId())
                self.log.debug("Original installation path", self.getInstallPath())
                ip = targetAsset.getInstallPath()
                self.log.debug("Overriding target installation path", ip)
                self.cachedDestination = ip

    def _parseFiles(self):

        self.log.trace("Enter")

        self.remoteFiles = {}
        self.localFiles = {}

        if not "files" in self.rawJson:
            return

        self.log.spam("Files key in json",self.rawJson["files"])

        for ftype in self.rawJson["files"].keys():

            name = ftype

            if name == "illustration":
                name = "screenshot"
            if name == "render":
                name = "screenshot"

            self.remoteFiles[name] = self.rawJson["files"][ftype]

            self.log.trace("Remote file",self.remoteFiles[name])

            fn = self.remoteFiles[name].rsplit('/', 1)[-1]

            self.log.spam("fn 1",fn)

            extension = os.path.splitext(fn)[1]
            extension = extension.lower()

            if name == "screenshot":
                convertedScreenshot = os.path.join(self.root, "screenshot.jpg")
                if os.path.exists(convertedScreenshot):
                    self.localFiles[name] = convertedScreenshot
                else:
                    fn = "screenshot" + extension
                    self.localFiles[name] = os.path.join(self.root, fn)

            if name == "thumb":
                fn = "thumb.png"
                self.localFiles[name] = os.path.join(self.root, fn)

            self.log.spam("fn 2", fn)

            if not name == "screenshot" and not name == "thumb":
                ip = self.getInstallPath()
                self.log.trace("Install path",ip)
                self.localFiles[name] = os.path.join(ip,fn)

        self.log.spam("remoteFiles",self.remoteFiles)
        self.log.spam("localFiles", self.localFiles)

    def getCategory(self):
        self.log.trace("Enter")
        return self.category

    def getType(self):
        self.log.trace("Enter")
        return self.type

    def getDescription(self):
        return self.description

    def getId(self):
        self.log.trace("Enter")
        return self.nid

    def getTitle(self):
        self.log.trace("Enter")
        return self.title

    def getUsername(self):
        self.log.trace("Enter")
        return self.username

    def getAuthor(self):
        self.log.trace("Enter")
        return self.username

    def getChanged(self):
        self.log.trace("Enter")
        return self.changed

    def getCreated(self):
        self.log.trace("Enter")
        return self.created

    def getLicense(self):
        self.log.trace("Enter")
        return self.license

    def getPertinentFileName(self):
        self.log.trace("Enter")
        key = fileForType[self.type]
        if key in self.remoteFiles:
            fn = self.remoteFiles[key].rsplit('/', 1)[-1]
            self.log.trace("Pertinent file",fn)
            return fn
        else:
            self.log.warn("Could not find pertinent file for asset",self.title)
            self.log.warn("File type is",self.type)
            self.log.warn("Files contain",self.remoteFiles)

        return None

    def getScreenshotPath(self):
        self.log.trace("Enter")
        if "screenshot" in self.localFiles:
            return self.localFiles["screenshot"]
        else:
            return None

    def getThumbPath(self):
        self.log.trace("Enter")
        if "thumb" in self.localFiles:
            return self.localFiles["thumb"]
        else:
            return None

    def getInstallPath(self):
        self.log.trace("Enter")
        if self.cachedDestination is None:
            self.cachedDestination = mhapi.assets.getAssetLocation(self.title, self.type)
        return self.cachedDestination

    def getDownloadTuples(self, ignoreExisting = True, onlyMeta=False, excludeThumb=False, excludeScreenshot=False):
        self.log.trace("Enter")
        downloads = []
        for key in self.remoteFiles.keys():
            l = self.localFiles[key]
            r = self.remoteFiles[key]

            self.log.trace("l",l)
            self.log.trace("r",r)

            self.log.trace("key",key)

            if not ignoreExisting or not os.path.exists(l):

                if key == "thumb" or key == "render" or key == "screenshot":
                    self.log.trace("ismeta")
                    if key == "thumb":
                        if not excludeThumb:
                            self.log.trace("Adding file for download", r)
                            downloads.append((r, l))
                        else:
                            self.log.trace("Exclude due to excludeThumb",r)
                    else:
                        if not excludeScreenshot:
                            self.log.trace("Adding file for download", r)
                            downloads.append((r, l))
                        else:
                            self.log.trace("Exclude due to excludeScreenshot",r)
                else:
                    if not onlyMeta:
                        self.log.trace("Adding file for download",r)
                        downloads.append((r, l))
                    else:
                        self.log.trace("Exclude due to onlyMeta",r)
            else:
                self.log.trace("Ignoring file",r)

        return downloads

