#!/usr/bin/python

from .namespace import NameSpace

import getpath
import os
import sys
import re
import shutil
import glob
import fnmatch
import proxy
import gui3d

from core import G

class Assets(NameSpace):
    """This namespace wraps all calls that are related to reading and managing assets."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()

        self.assetTypes = ["material",
                           "model",
                           "clothes",
                           "hair",
                           "teeth",
                           "eyebrows",
                           "eyelashes",
                           "tongue",
                           "eyes",
                           "proxy",
                           "skin",
                           "pose",
                           "expression",
                           "rig",
                           "target",
                           "node_setups_and_blender_specific"]

        self.extensionToType = dict()
        self.extensionToType[".mhmat"] = "material"
        self.extensionToType[".mhclo"] = "proxy"
        self.extensionToType[".proxy"] = "proxy"
        self.extensionToType[".target"] = "target"
        self.extensionToType[".mhm"] = "models"

        self.typeToExtension = {'material'  :   'mhmat',
                                'models'    :   'mhm',
                                'model'     :   'mhm',
                                'clothes'   :   'mhclo',
                                'hair'      :   'mhclo',
                                'teeth'     :   'mhclo',
                                'eyebrows'  :   'mhclo',
                                'eyelashes' :   'mhclo',
                                'tongue'    :   'mhclo',
                                'eyes'      :   'mhclo',
                                'proxymeshes':  'proxy',
                                'target'    :   'target',
                                'skin'      :   'mhmat'}
        
        self.genericExtraKeys = ["tag"]
        self.genericKeys = ["name","description", "uuid"]
        self.genericCommentKeys = ["license","homepage","author"]

        self.proxyKeys = [
            "basemesh",
            "obj_file",
            "max_pole",
            "material",
            "z_depth",
            "x_scale",
            "y_scale",
            "z_scale"
        ]

        self.materialKeys = [
            "diffuseColor",
            "specularColor",
            "emissiveColor",
            "ambientColor",
            "diffuseTexture",
            "bumpmapTexture",
            "normalmapTexture",
            "displacementmapTexture",
            "specularmapTexture",
            "transparencymapTexture",
            "aomapTexture",
            "diffuseIntensity",
            "bumpMapIntensity",
            "normalMapIntensity",
            "displacementMapIntensity",
            "specularMapIntensity",
            "transparencyMapIntensity",
            "aoMapIntensity",
            "shininess",
            "opacity",
            "translucency",
            "shadeless",
            "wireframe",
            "transparent",
            "alphaToCoverage",
            "backfaceCull",
            "depthless",
            "castShadows",
            "receiveShadows",

        ] # There are also SSS settings, but I don't know if those actually works

        self.keyList = self.genericExtraKeys + self.genericCommentKeys + self.genericKeys +self.materialKeys + \
                       self.proxyKeys

        self.zDepth = {"Body": 31,
                       "Underwear and lingerie": 39,
                       "Socks and stockings": 43,
                       "Shirt and trousers": 47,
                       "Sweater": 50,
                       "Indoor jacket": 53,
                       "Shoes and boots": 57,
                       "Coat": 61,
                       "Backpack": 69
                      }

    def _parseGenericAssetInfo(self,fullPath):

        info = dict()

        fPath, ext = os.path.splitext(fullPath)
        basename = os.path.basename(fullPath)

        info["type"] = self.extensionToType[ext]
        info["absolute path"] = fullPath
        info["extension"] = ext
        info["basename"] = basename
        info["rawlines"] = []
        info["location"] = os.path.dirname(fullPath)
        info["parentdir"] = os.path.basename(info["location"])

        with open(fullPath, 'r', encoding='utf8') as f:
            contents = f.readlines()
            for line in contents:
                info["rawlines"].append(re.sub(r"[\x0a\x0d]+",'',line))

        info["rawkeys"] = []
        info["rawcommentkeys"] = []

        for line in info["rawlines"]:
            m = re.match(r"^([a-zA-Z_]+)\s+(.*)$",line)
            if m:
                info["rawkeys"].append([m.group(1),m.group(2)])
            m = re.match(r"^#\s+([a-zA-Z_]+)\s+(.*)$",line)
            if m:
                info["rawcommentkeys"].append([m.group(1),m.group(2)])
        
        for genericExtraKeyName in self.genericExtraKeys:
            info[genericExtraKeyName] = set()
            for rawkey in info["rawkeys"]:
                rawKeyName = rawkey[0]
                rawKeyValue = rawkey[1]
                if rawKeyName == genericExtraKeyName:
                    info[genericExtraKeyName].add(rawKeyValue)

        for genericKeyName in self.genericKeys:
            info[genericKeyName] = None
            for rawkey in info["rawkeys"]:
                rawKeyName = rawkey[0]
                rawKeyValue = rawkey[1]
                if rawKeyName == genericKeyName:
                    info[genericKeyName] = rawKeyValue

        for genericCommentKeyName in self.genericCommentKeys:
            info[genericCommentKeyName] = None
            for commentKey in info["rawcommentkeys"]:
                commentKeyName = commentKey[0]
                commentKeyValue = commentKey[1]
                if commentKeyName == genericCommentKeyName:
                    info[commentKeyName] = commentKeyValue

        return info

    def _parseProxyKeys(self,assetInfo):
        for pk in self.proxyKeys:
            assetInfo[pk] = None
            for k in assetInfo["rawkeys"]:
                key = k[0]
                value = k[1]
                if key == pk:
                    assetInfo[pk] = value

    def _parseMaterialKeys(self,assetInfo):
        for pk in self.materialKeys:
            assetInfo[pk] = None
            for k in assetInfo["rawkeys"]:
                key = k[0]
                value = k[1]
                if key == pk:
                    assetInfo[pk] = value

    def _addPertinentKeyInfo(self,assetInfo):

        pertinentKeys = list(self.genericKeys)
        pertinentExtraKeys = list(self.genericExtraKeys)
        pertinentCommentKeys = list(self.genericCommentKeys)

        if assetInfo["type"] == "proxy":
            pertinentKeys.extend(self.proxyKeys)

        if assetInfo["type"] == "material":
            pertinentKeys.extend(self.materialKeys)

        assetInfo["pertinentKeys"] = pertinentKeys
        assetInfo["pertinentExtraKeys"] = pertinentExtraKeys
        assetInfo["pertinentCommentKeys"] = pertinentCommentKeys

    def assetTitleToDirName(self, assetTitle):
        """Convert an asset title (as shown for example in a list) to a normalized file name"""
        normalizedTitle = assetTitle.strip()
        normalizedTitle = re.sub(r'_+', ' ', normalizedTitle)
        normalizedTitle = normalizedTitle.strip()
        normalizedTitle = re.sub(r'\s+', '_', normalizedTitle)
        normalizedTitle = re.sub(r'[*:,\[\]/\\\(\)]+', '', normalizedTitle)
        return normalizedTitle

    def getAssetTypes(self):
        """Returns a non-live list of known asset types"""
        return list(self.assetTypes)

    def getAssetLocation(self, assetTitle, assetType):
        """Get the full normal (user) path for an asset based on its title and type"""
        alreadyKosher = ["clothes",
                         "hair",
                         "teeth",
                         "eyebrows",
                         "eyelashes",
                         "tongue",
                         "eyes"]

        needsPlural = ["material",
                       "model",
                       "skin",
                       "pose",
                       "expression",
                       "rig"]

        normalizedTitle = self.assetTitleToDirName(assetTitle)

        if assetType == "model":
            root = self.api.locations.getUserHomePath("models")
            return os.path.join(root, normalizedTitle)
        
        if assetType in alreadyKosher:
            root = self.api.locations.getUserDataPath(assetType)
            return os.path.join(root,normalizedTitle)

        if assetType in needsPlural:
            root = self.api.locations.getUserDataPath(assetType + "s")
            return os.path.join(root,normalizedTitle)

        if assetType == "proxy":
            return self.api.locations.getUserDataPath("proxymeshes")

        if assetType == "target":
            return self.api.locations.getUserDataPath("custom")

        if assetType == "model":
            return self.api.locations.getUserHomePath("models")

        raise ValueError("Could not convert title to location for asset with type",assetType)

    def openAssetFile(self, path, strip = False):
        """Opens an asset file and returns a hash describing it"""
        fullPath = self.api.locations.getUnicodeAbsPath(path)
        if not os.path.isfile(fullPath):
            return None
        info = self._parseGenericAssetInfo(fullPath)

        self._addPertinentKeyInfo(info)

        if info["type"] == "proxy":
            self._parseProxyKeys(info)

        if info["type"] == "material":
            self._parseMaterialKeys(info)

        thumbPath = os.path.splitext(path)[0] + ".thumb"

        if os.path.isfile(thumbPath):
            info["thumb_path"] = thumbPath
        else:
            info["thumb_path"] = None

        if strip:
            info.pop("rawlines",None)
            info.pop("rawkeys",None)
            info.pop("rawcommentkeys",None)

        return info

    def writeAssetFile(self, assetInfo, createBackup = True):
        """ This (over)writes the asset file named in the assetInfo's "absolute path" key. If createBackup is set to True, any pre-existing file will be backed up to it's former name + ".bak" """
        if not assetInfo:
            raise ValueError('Cannot use None as assetInfo')

        ap = assetInfo["absolute path"]
        bak = ap + ".bak"

        if createBackup and os.path.isfile(ap):
            shutil.copy(ap,bak)

        with open(ap, 'w', encoding='utf8') as f:

            stillNeedToDumpCommentKeys = True

            writtenKeys = []
            writtenCommentKeys = []
            writtenExtraKeys = []

            remainingKeys = list(assetInfo["pertinentKeys"])
            remainingCommentKeys = list(assetInfo["pertinentCommentKeys"])
            remainingExtraKeys = list(assetInfo["pertinentExtraKeys"])

            for line in assetInfo["rawlines"]:
                allowWrite = True
                m = re.match(r"^([a-zA-Z_]+)\s+(.*)$",line)
                if m:
                    # If this is the first line without a hash sign, we want to 
                    # dump the remaining comment keys before doing anything else
                    if stillNeedToDumpCommentKeys:
                        if len(remainingCommentKeys) > 0:
                            for key in remainingCommentKeys:
                                if not assetInfo[key] is None:
                                    f.write("# " + key + " " + assetInfo[key] + "\x0a")

                        stillNeedToDumpCommentKeys = False

                    key = m.group(1)

                    if key in remainingKeys:
                        allowWrite = False
                        if not assetInfo[key] is None:
                            f.write(key + " " + assetInfo[key] + "\x0a")
                        writtenKeys.append(key)
                        remainingKeys.remove(key)

                    if key in remainingExtraKeys:
                        allowWrite = False

                        if not assetInfo[key] is None and len(assetInfo[key]) > 0 and not key in writtenExtraKeys:
                            for val in assetInfo[key]:
                                f.write(key + " " + val + "\x0a")
                        writtenExtraKeys.append(key)
                        remainingExtraKeys.remove(key)

                    if key in writtenExtraKeys:
                        allowWrite = False

                m = re.match(r"^#\s+([a-zA-Z_]+)\s+(.*)$",line)
                if m:
                    key = m.group(1)

                    if key in remainingCommentKeys:
                        allowWrite = False
                        if not assetInfo[key] is None:
                            f.write("# " + key + " " + assetInfo[key] + "\x0a")
                        writtenCommentKeys.append(key)
                        remainingCommentKeys.remove(key)

                if allowWrite:
                    f.write(line + "\x0a")

            if len(remainingKeys) > 0:
                for key in remainingKeys:
                    if not assetInfo[key] is None:
                        f.write(key + " " + assetInfo[key] + "\x0a")

            if len(remainingExtraKeys) > 0:
                for key in remainingExtraKeys:
                    if not assetInfo[key] is None and len(assetInfo[key]) > 0:
                        for val in assetInfo[key]:
                            f.write(key + " " + val + "\x0a")

        return True

    def materialToHash(self, material):
        """Convert a material object to a hash containing all its settings"""
        output = {}

        fn = os.path.abspath(material.filename)

        # meta

        output["name"] = material.name
        output["description"] = material.description
        output["materialFile"] = fn

        # colors

        output["ambientColor"] = material.ambientColor.values
        output["diffuseColor"] = material.diffuseColor.values
        output["specularColor"] = material.specularColor.values
        output["emissiveColor"] = material.emissiveColor.values

        # textures

        output["diffuseTexture"] = material.diffuseTexture
        output["bumpMapTexture"] = material.bumpMapTexture
        output["normalMapTexture"] = material.normalMapTexture
        output["displacementMapTexture"] = material.displacementMapTexture
        output["specularMapTexture"] = material.specularMapTexture
        output["transparencyMapTexture"] = material.transparencyMapTexture
        output["aoMapTexture"] = material.aoMapTexture

        # texture intensities

        output["bumpMapIntensity"] = material.bumpMapIntensity
        output["normalMapIntensity"] = material.normalMapIntensity
        output["displacementMapIntensity"] = material.displacementMapIntensity
        output["specularMapIntensity"] = material.specularMapIntensity
        output["transparencyMapIntensity"] = material.transparencyMapIntensity
        output["aoMapIntensity"] = material.aoMapIntensity

        # subsurface

        output["sssEnabled"] = material.sssEnabled
        output["sssRScale"] = material.sssRScale
        output["sssGScale"] = material.sssGScale
        output["sssBScale"] = material.sssBScale

        # various

        output["uvMap"] = material.uvMap
        output["shininess"] = material.shininess
        output["opacity"] = material.opacity
        output["translucency"] = material.translucency
        output["shadeless"] = material.shadeless
        output["wireframe"] = material.wireframe
        output["transparent"] = material.transparent
        output["alphaToCoverage"] = material.alphaToCoverage
        output["backfaceCull"] = material.backfaceCull
        output["depthless"] = material.depthless
        output["castShadows"] = material.castShadows
        output["receiveShadows"] = material.receiveShadows
        output["autoBlendSkin"] = material.autoBlendSkin

        # viewport color
        if material.usesViewPortColor():
            output["viewPortColor"] = material.viewPortColor.values
            output["viewPortAlpha"] = material._viewPortAlpha

        for key in output.keys():
            if output[key] is None:
                output[key] = ""

        definedKeys = []
        for key in output:
            definedKeys.append(str(key).lower())

        with open(fn, 'r', encoding='utf-8') as f:
            line = f.readline()
            while line:
                parsedLine = line.strip()
                if parsedLine and not parsedLine.startswith("#") and not parsedLine.startswith("/"):
                    match = re.search(r'^([a-zA-Z]+)\s+(.*)$', parsedLine)
                    if match:
                        key = match.group(1)
                        value = match.group(2)
                        if not key.lower() in definedKeys:
                            # There was a key defined in the material file, but it has not been picked up
                            # by MH. So we insert it in the produced hash and let the recipient decide
                            # what to do with it, if anything
                            output[key] = value
                line = f.readline()

        return output

    def _findMaterials(self,path):
        matches = []
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, '*.mhmat'):
                matches.append(os.path.join(root, filename))
        return matches

    def _findProxies(self,path):

        basenames = []
        matches = []
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, '*.mhpxy'):
                matches.append(os.path.join(root, filename))
                basenames.append(os.path.basename(filename))

        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, '*.mhclo'):
                bn = os.path.basename(filename)
                if not bn in basenames:
                    matches.append(os.path.join(root, filename))

        return matches

    def getAvailableSystemSkins(self):
        """Get a list with full paths to all system skins (the MHMAT files)"""
        path = getpath.getSysDataPath("skins")
        return self._findMaterials(path)

    def getAvailableUserSkins(self):
        """Get a list with full paths to all user skins (the MHMAT files)"""
        path = getpath.getDataPath("skins")
        return self._findMaterials(path)

    def getAvailableSystemHair(self):
        """Get a list with full paths to all system hair (the MHCLO files)"""
        path = getpath.getSysDataPath("hair")
        return self._findProxies(path)

    def getAvailableUserHair(self):
        """Get a list with full paths to all user hair (the MHCLO files)"""
        path = getpath.getDataPath("hair")
        return self._findProxies(path)

    def getAvailableSystemEyebrows(self):
        """Get a list with full paths to all system eyebrows (the MHCLO files)"""
        path = getpath.getSysDataPath("eyebrows")
        return self._findProxies(path)

    def getAvailableUserEyebrows(self):
        """Get a list with full paths to all user eyebrows (the MHCLO files)"""
        path = getpath.getDataPath("eyebrows")
        return self._findProxies(path)

    def getAvailableSystemEyelashes(self):
        """Get a list with full paths to all system eyelashes (the MHCLO files)"""
        path = getpath.getSysDataPath("eyelashes")
        return self._findProxies(path)

    def getAvailableUserEyelashes(self):
        """Get a list with full paths to all user eyelashes (the MHCLO files)"""
        path = getpath.getDataPath("eyelashes")
        return self._findProxies(path)

    def getAvailableSystemClothes(self):
        """Get a list with full paths to all system clothes (the MHCLO files)"""
        path = getpath.getSysDataPath("clothes")
        return self._findProxies(path)

    def getAvailableUserClothes(self):
        """Get a list with full paths to all user clothes (the MHCLO files)"""
        path = getpath.getDataPath("clothes")
        return self._findProxies(path)

    def _equipProxy(self, category, tab, filename):
        tv = self.api.ui.getTaskView(category, tab)
        if tv is None:
            raise ValueError("Could not find taskview " + str(category) + "/" + str(tab))
        tv.proxyFileSelected(filename)

    def _unequipProxy(self, category, tab, filename):
        tv = self.api.ui.getTaskView(category, tab)
        if tv is None:
            raise ValueError("Could not find taskview " + str(category) + "/" + str(tab))
        tv.proxyFileDeselected(filename)

    def _getEquippedProxies(self, category, tab, onlyFirst=False):
        tv = self.api.ui.getTaskView(category, tab)
        if tv is None:
            raise ValueError("Could not find taskview " + str(category) + "/" + str(tab))
        ps = tv.selectedProxies

        if onlyFirst:
            if ps is None or len(ps) < 1:
                return None
            return ps[0].file
        else:
            ret = []
            if ps is None:
                return []
            for p in ps:
                ret.append(p.file)
            return ret

    def equipHair(self, mhclofile):
        """Equip a MHCLO file with hair. This will automatically unequip previously equipped hair."""
        self._equipProxy("Geometries","Hair",mhclofile)

    def unequipHair(self, mhclofile):
        """Unequip a MHCLO file with hair"""
        self._unequipProxy("Geometries", "Hair", mhclofile)

    def getEquippedHair(self):
        """Get the currently equipped hair, if any"""
        return self._getEquippedProxies("Geometries","Hair",onlyFirst=True)

    def equipEyebrows(self, mhclofile):
        """Equip a MHCLO file with eyebrows. This will automatically unequip previously equipped eyebrows."""
        self._equipProxy("Geometries", "Eyebrows", mhclofile)

    def unequipEyebrows(self, mhclofile):
        """Unequip a MHCLO file with eyebrows"""
        self._unequipProxy("Geometries", "Eyebrows", mhclofile)

    def getEquippedEyebrows(self):
        """Get the currently equipped eyebrows, if any"""
        return self._getEquippedProxies("Geometries", "Eyebrows", onlyFirst=True)

    def equipEyelashes(self, mhclofile):
        """Equip a MHCLO file with eyelashes. This will automatically unequip previously equipped eyelashes."""
        self._equipProxy("Geometries", "Eyelashes", mhclofile)

    def unequipEyelashes(self, mhclofile):
        """Unequip a MHCLO file with eyelashes"""
        self._unequipProxy("Geometries", "Eyelashes", mhclofile)

    def getEquippedEyelashes(self):
        """Get the currently equipped eyelashes, if any"""
        return self._getEquippedProxies("Geometries", "Eyelashes", onlyFirst=True)

    def equipClothes(self, mhclofile):
        """Equip a MHCLO file with clothes"""
        self._equipProxy("Geometries", "Clothes", mhclofile)

    def unequipClothes(self, mhclofile):
        """Unequip a MHCLO file with clothes"""
        self._unequipProxy("Geometries", "Clothes", mhclofile)

    def getEquippedClothes(self):
        """Get a list of all currently equipped clothes"""
        return self._getEquippedProxies("Geometries", "Clothes")

    def unequipAllClothes(self):
        """Unequip all clothes"""
        for c in self.getEquippedClothes():
            self.unequipClothes(c)
