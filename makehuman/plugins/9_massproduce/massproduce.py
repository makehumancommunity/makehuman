#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import gui3d
import gui
from core import G
from progress import Progress
from .randomizeaction import RandomizeAction
from .randomizationsettings import RandomizationSettings
from .humanstate import HumanState
from .modifiergroups import ModifierInfo

mhapi = gui3d.app.mhapi

import mh, time, os, re

from PyQt5.QtWidgets import *

import pprint
pp = pprint.PrettyPrinter(indent=4)

DEFAULT_TABLE_HEIGHT=250
DEFAULT_LABEL_COLUMN_WIDTH=300

class MassProduceTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Mass produce')

        self.human = G.app.selectedHuman

        self.log = mhapi.utility.getLogChannel("massproduce")

        self.randomizationSettings = RandomizationSettings()

        self._setupLeftPanel(self.randomizationSettings)
        self._setupMainPanel(self.randomizationSettings)
        self._setupRightPanel(self.randomizationSettings)

    def _setupLeftPanel(self, r):
        self.addLeftWidget( self._createMacroSettings(r) )
        self.addLeftWidget(mhapi.ui.createLabel())
        self.addLeftWidget( self._createModelingSettings(r) )

    def _setupMainPanel(self, r):

        self.mainSettingsPanel = QWidget()
        self.mainSettingsLayout = QVBoxLayout()

        self._setupRandomizeProxies(self.mainSettingsLayout, r)
        self._setupRandomizeMaterials(self.mainSettingsLayout, r)
        self._setupAllowedSkinsTables(self.mainSettingsLayout, r)
        self._setupAllowedHairTable(self.mainSettingsLayout, r)
        self._setupAllowedEyebrowsTable(self.mainSettingsLayout, r)
        self._setupAllowedEyelashesTable(self.mainSettingsLayout, r)
        self._setupClothesTables(self.mainSettingsLayout, r)

        self.mainSettingsLayout.addStretch()
        self.mainSettingsPanel.setLayout(self.mainSettingsLayout)

        self.mainScroll = QScrollArea()
        self.mainScroll.setWidget(self.mainSettingsPanel)
        self.mainScroll.setWidgetResizable(True)

        self.addTopWidget(self.mainScroll)

    def _setupRightPanel(self, r):
        self.addRightWidget(self._createExportSettings(r))
        self.addRightWidget(mhapi.ui.createLabel())
        self.addRightWidget(self._createProducePanel(r))

    def _setupRandomizeMaterials(self, layout, r):
        layout.addWidget(mhapi.ui.createLabel("Randomize materials:"))
        layout.addWidget(r.addUI("materials", "randomizeSkinMaterials", mhapi.ui.createCheckBox(label="Randomize skins", selected=True)))
        #layout.addWidget(r.addUI("materials", "randomizeHairMaterials", mhapi.ui.createCheckBox(label="Randomize hair material", selected=True)))
        #layout.addWidget(r.addUI("materials", "randomizeClothesMaterials", mhapi.ui.createCheckBox(label="Randomize clothes material", selected=True)))
        layout.addWidget(mhapi.ui.createLabel())

    def _setupRandomizeProxies(self, layout, r):
        layout.addWidget(mhapi.ui.createLabel("Randomize clothes and body parts:"))
        layout.addWidget(r.addUI("proxies", "hair", mhapi.ui.createCheckBox(label="Randomize hair", selected=True)))
        layout.addWidget(r.addUI("proxies", "eyelashes", mhapi.ui.createCheckBox(label="Randomize eyelashes", selected=True)))
        layout.addWidget(r.addUI("proxies", "eyebrows", mhapi.ui.createCheckBox(label="Randomize eyebrows", selected=True)))
        layout.addWidget(r.addUI("proxies", "fullClothes", mhapi.ui.createCheckBox(label="Randomize full body clothes", selected=True)))
        layout.addWidget(r.addUI("proxies", "upperClothes", mhapi.ui.createCheckBox(label="Randomize upper body clothes", selected=False)))
        layout.addWidget(r.addUI("proxies", "lowerClothes", mhapi.ui.createCheckBox(label="Randomize lower body clothes", selected=False)))
        layout.addWidget(r.addUI("proxies", "shoes", mhapi.ui.createCheckBox(label="Randomize shoes", selected=True)))
        layout.addWidget(mhapi.ui.createLabel())

    def _generalMainTableSettings(self, table):
        table.setColumnWidth(0, DEFAULT_LABEL_COLUMN_WIDTH)
        table.setMinimumHeight(DEFAULT_TABLE_HEIGHT - 50)
        table.setMaximumHeight(DEFAULT_TABLE_HEIGHT)

    def _setupClothesTables(self, layout, r):
        sysClothes = mhapi.assets.getAvailableSystemClothes()
        userClothes = mhapi.assets.getAvailableUserClothes()

        allClothes = []
        allClothes.extend(sysClothes)
        allClothes.extend(userClothes)
        
        femaleFullExplicit = ["female elegantsuit01",
        "female casualsuit02",
        "female casualsuit01",
        "female sportsuit01"]
        
        maleFullExplicit = ["male worksuit01",
        "male elegantsuit01",        
        "male casualsuit06",
        "male casualsuit05",
        "male casualsuit04",
        "male casualsuit02",       
        "male casualsuit01",        
        "male casualsuit03"]

        femaleFullKeyword = ["gown","dress","swimsuit"]
        maleFullKeyword = ["wetsuit"]
        
        femaleUpperExplicit = []
        maleUpperExplicit = []
        femaleUpperKeyword = ["bra","top","shirt","sweater"]
        maleUpperKeyword = ["top","shirt","sweater"]

        femaleLowerExplicit = []
        maleLowerExplicit = []
        femaleLowerKeyword = ["skirt","jeans","string","shorts","pants"]
        maleLowerKeyword = ["jeans","shorts","pants","trunk"]

        femaleShoesExplicit = []
        maleShoesExplicit = []
        femaleShoesKeyword = ["boot","shoe","sneaker","sock"]
        maleShoesKeyword = ["boot","shoe","sneaker","sock"]        

        clothesInfos = dict()
        allNames = []
        for fullPath in allClothes:
            bn = os.path.basename(fullPath).lower()
            bn = re.sub(r'.mhclo', '', bn)
            bn = re.sub(r'.mhpxy', '', bn)
            bn = re.sub(r'_', ' ', bn)
            bn = bn.strip()

            name = bn

            clothesInfo = dict()
            clothesInfo["fullPath"] = fullPath
            clothesInfo["name"] = name

            clothesInfo["maleFull"] = False
            clothesInfo["femaleFull"] = False
            
            clothesInfo["maleUpper"] = False
            clothesInfo["femaleUpper"] = False
            
            clothesInfo["maleLower"] = False
            clothesInfo["femaleLower"] = False
            
            clothesInfo["maleShoes"] = False
            clothesInfo["femaleShoes"] = False

            clothesInfo["mixedFull"] = False
            clothesInfo["mixedUpper"] = False
            clothesInfo["mixedLower"] = False
            clothesInfo["mixedShoes"] = False
            
            if not "female" in name:
                if name in maleFullExplicit:
                    clothesInfo["maleFull"] = True
                for k in maleFullKeyword:
                    if k in name:
                        clothesInfo["maleFull"] = True

                if name in maleUpperExplicit:
                    clothesInfo["maleUpper"] = True
                for k in maleUpperKeyword:
                    if k in name:
                        clothesInfo["maleUpper"] = True

                if name in maleLowerExplicit:
                    clothesInfo["maleLower"] = True
                for k in maleLowerKeyword:
                    if k in name:
                        clothesInfo["maleLower"] = True

                if name in maleShoesExplicit:
                    clothesInfo["maleShoes"] = True
                for k in maleShoesKeyword:
                    if k in name:
                        clothesInfo["maleShoes"] = True

            if name in femaleFullExplicit:
                clothesInfo["femaleFull"] = True
            for k in femaleFullKeyword:
                if k in name:
                    clothesInfo["femaleFull"] = True

            if name in femaleUpperExplicit:
                clothesInfo["femaleUpper"] = True
            for k in femaleUpperKeyword:
                if k in name:
                    clothesInfo["femaleUpper"] = True

            if name in femaleLowerExplicit:
                clothesInfo["femaleLower"] = True
            for k in femaleLowerKeyword:
                if k in name:
                    clothesInfo["femaleLower"] = True

            if name in femaleShoesExplicit:
                clothesInfo["femaleShoes"] = True
            for k in femaleShoesKeyword:
                if k in name:
                    clothesInfo["femaleShoes"] = True

            clothesInfo["mixedFull"] = clothesInfo["femaleFull"] or clothesInfo["maleFull"]
            clothesInfo["mixedUpper"] = clothesInfo["femaleUpper"] or clothesInfo["maleUpper"]
            clothesInfo["mixedLower"] = clothesInfo["femaleLower"] or clothesInfo["maleLower"]
            clothesInfo["mixedShoes"] = clothesInfo["femaleShoes"] or clothesInfo["maleShoes"]

            clothesInfos[name] = clothesInfo
            allNames.append(name)

        allNames.sort()

        # part = ["Full","Upper","Lower","Shoes"]
        # gender = ["male","female"]
        # with open("/tmp/table.html","w") as f:
        #     f.write("<html>\n<body>\n<table>\n")
        #     f.write("<tr><td><b>Name</b></td>")
        #
        #     for p in part:
        #         for g in gender:
        #             f.write("<td><b>" + g + p + "</b></td>")
        #     f.write("</tr>\n")
        #     for name in allNames:
        #         f.write("<tr>")
        #         i = clothesInfos[name]
        #         f.write("<tr><td>" + name + "</td>")
        #         for p in part:
        #             for g in gender:
        #                 if i[g+p]:
        #                     f.write("<td>XXX</td>")
        #                 else:
        #                     f.write("<td>---</td>")
        #         f.write("</tr>\n")
        #
        #     f.write("</body></html>")


        self.allowedFullTable = QTableWidget()
        self.allowedFullTable.setRowCount(len(allNames))
        self.allowedFullTable.setColumnCount(4)
        self.allowedFullTable.setHorizontalHeaderLabels(["Clothes", "Mixed", "Female", "Male"])

        self.allowedUpperTable = QTableWidget()
        self.allowedUpperTable.setRowCount(len(allNames))
        self.allowedUpperTable.setColumnCount(4)
        self.allowedUpperTable.setHorizontalHeaderLabels(["Clothes", "Mixed", "Female", "Male"])

        self.allowedLowerTable = QTableWidget()
        self.allowedLowerTable.setRowCount(len(allNames))
        self.allowedLowerTable.setColumnCount(4)
        self.allowedLowerTable.setHorizontalHeaderLabels(["Clothes", "Mixed", "Female", "Male"])

        self.allowedShoesTable = QTableWidget()
        self.allowedShoesTable.setRowCount(len(allNames))
        self.allowedShoesTable.setColumnCount(4)
        self.allowedShoesTable.setHorizontalHeaderLabels(["Clothes", "Mixed", "Female", "Male"])

        i = 0
        for name in allNames:

            info = clothesInfos[name]

            self.allowedFullTable.setItem(i, 0, QTableWidgetItem(name))
            self.allowedUpperTable.setItem(i, 0, QTableWidgetItem(name))
            self.allowedLowerTable.setItem(i, 0, QTableWidgetItem(name))
            self.allowedShoesTable.setItem(i, 0, QTableWidgetItem(name))

            miF = r.addUI("allowedFullClothes", name, mhapi.ui.createCheckBox(""), subName="mixed")
            maF = r.addUI("allowedFullClothes", name, mhapi.ui.createCheckBox(""), subName="male")
            feF = r.addUI("allowedFullClothes", name, mhapi.ui.createCheckBox(""), subName="female")

            miU = r.addUI("allowedUpperClothes", name, mhapi.ui.createCheckBox(""), subName="mixed")
            maU = r.addUI("allowedUpperClothes", name, mhapi.ui.createCheckBox(""), subName="male")
            feU = r.addUI("allowedUpperClothes", name, mhapi.ui.createCheckBox(""), subName="female")

            miL = r.addUI("allowedLowerClothes", name, mhapi.ui.createCheckBox(""), subName="mixed")
            maL = r.addUI("allowedLowerClothes", name, mhapi.ui.createCheckBox(""), subName="male")
            feL = r.addUI("allowedLowerClothes", name, mhapi.ui.createCheckBox(""), subName="female")

            miS = r.addUI("allowedShoes", name, mhapi.ui.createCheckBox(""), subName="mixed")
            maS = r.addUI("allowedShoes", name, mhapi.ui.createCheckBox(""), subName="male")
            feS = r.addUI("allowedShoes", name, mhapi.ui.createCheckBox(""), subName="female")

            self.allowedFullTable.setCellWidget(i, 1, miF)
            self.allowedFullTable.setCellWidget(i, 2, feF)
            self.allowedFullTable.setCellWidget(i, 3, maF)

            self.allowedUpperTable.setCellWidget(i, 1, miU)
            self.allowedUpperTable.setCellWidget(i, 2, feU)
            self.allowedUpperTable.setCellWidget(i, 3, maU)

            self.allowedLowerTable.setCellWidget(i, 1, miL)
            self.allowedLowerTable.setCellWidget(i, 2, feL)
            self.allowedLowerTable.setCellWidget(i, 3, maL)

            self.allowedShoesTable.setCellWidget(i, 1, miS)
            self.allowedShoesTable.setCellWidget(i, 2, feS)
            self.allowedShoesTable.setCellWidget(i, 3, maS)

            r.addUI("allowedFullClothes", name, info["fullPath"], subName="fullPath")
            r.addUI("allowedUpperClothes", name, info["fullPath"], subName="fullPath")
            r.addUI("allowedLowerClothes", name, info["fullPath"], subName="fullPath")
            r.addUI("allowedShoes", name, info["fullPath"], subName="fullPath")

            miF.setChecked(info["mixedFull"])
            maF.setChecked(info["maleFull"])
            feF.setChecked(info["femaleFull"])

            miU.setChecked(info["mixedUpper"])
            maU.setChecked(info["maleUpper"])
            feU.setChecked(info["femaleUpper"])

            miL.setChecked(info["mixedLower"])
            maL.setChecked(info["maleLower"])
            feL.setChecked(info["femaleLower"])

            miS.setChecked(info["mixedShoes"])
            maS.setChecked(info["maleShoes"])
            feS.setChecked(info["femaleShoes"])

            i = i + 1

        self._generalMainTableSettings(self.allowedFullTable)
        self._generalMainTableSettings(self.allowedUpperTable)
        self._generalMainTableSettings(self.allowedLowerTable)
        self._generalMainTableSettings(self.allowedShoesTable)

        layout.addWidget(mhapi.ui.createLabel(""))
        layout.addWidget(mhapi.ui.createLabel("Allowed full body clothes:"))
        layout.addWidget(self.allowedFullTable)

        layout.addWidget(mhapi.ui.createLabel(""))
        layout.addWidget(mhapi.ui.createLabel("Allowed upper body clothes:"))
        layout.addWidget(self.allowedUpperTable)

        layout.addWidget(mhapi.ui.createLabel(""))
        layout.addWidget(mhapi.ui.createLabel("Allowed lower body clothes:"))
        layout.addWidget(self.allowedLowerTable)

        layout.addWidget(mhapi.ui.createLabel(""))
        layout.addWidget(mhapi.ui.createLabel("Allowed shoes:"))
        layout.addWidget(self.allowedShoesTable)

    def _setupAllowedHairTable(self, layout, r):
        sysHair = mhapi.assets.getAvailableSystemHair()
        userHair = mhapi.assets.getAvailableUserHair()

        hair = []
        hair.extend(sysHair)
        hair.extend(userHair)

        femaleOnly = [
            "bob01",
            "bob02",
            "long01",
            "braid01",
            "ponytail01"
        ]

        maleOnly = [
            "short02",
            "short04"
        ]

        hairInfo = dict()

        for fullPath in hair:
            bn = os.path.basename(fullPath).lower()
            bn = re.sub(r'.mhclo', '', bn)
            bn = re.sub(r'.mhpxy', '', bn)
            bn = re.sub(r'_', ' ', bn)
            bn = bn.strip()

            hairName = bn

            if not hairName in hairInfo:
                hairInfo[hairName] = dict()
                hairInfo[hairName]["fullPath"] = fullPath

                allowMixed = True
                allowFemale = True
                allowMale = True

                if hairName in femaleOnly:
                    allowMale = False

                if hairName in maleOnly:
                    allowFemale = False

                hairInfo[hairName]["allowMixed"] = allowMixed
                hairInfo[hairName]["allowFemale"] = allowFemale
                hairInfo[hairName]["allowMale"] = allowMale

        hairNames = list(hairInfo.keys())
        hairNames.sort()

        self.allowedHairTable = QTableWidget()
        self.allowedHairTable.setRowCount(len(hairNames))
        self.allowedHairTable.setColumnCount(4)
        self.allowedHairTable.setHorizontalHeaderLabels(["Hair", "Mixed", "Female", "Male"])

        i = 0
        for hairName in hairNames:
            hairSettings = hairInfo[hairName]
            hairWidgets = dict()

            self.allowedHairTable.setItem(i, 0, QTableWidgetItem(hairName))
            hairWidgets["mixed"] = r.addUI("allowedHair", hairName, mhapi.ui.createCheckBox(""), subName="mixed")
            hairWidgets["female"] = r.addUI("allowedHair", hairName, mhapi.ui.createCheckBox(""), subName="female")
            hairWidgets["male"] = r.addUI("allowedHair", hairName, mhapi.ui.createCheckBox(""), subName="male")
            r.addUI("allowedHair", hairName, hairSettings["fullPath"], subName="fullPath")

            self.allowedHairTable.setCellWidget(i, 1, hairWidgets["mixed"])
            self.allowedHairTable.setCellWidget(i, 2, hairWidgets["female"])
            self.allowedHairTable.setCellWidget(i, 3, hairWidgets["male"])

            hairWidgets["mixed"].setChecked(hairSettings["allowMixed"])
            hairWidgets["female"].setChecked(hairSettings["allowFemale"])
            hairWidgets["male"].setChecked(hairSettings["allowMale"])

            i = i + 1

        self._generalMainTableSettings(self.allowedHairTable)

        layout.addWidget(mhapi.ui.createLabel(""))
        layout.addWidget(mhapi.ui.createLabel("Allowed hair:"))
        layout.addWidget(self.allowedHairTable)

    def _setupAllowedEyebrowsTable(self, layout, r):
        sysEyebrows = mhapi.assets.getAvailableSystemEyebrows()
        userEyebrows = mhapi.assets.getAvailableUserEyebrows()

        eyebrows = []
        eyebrows.extend(sysEyebrows)
        eyebrows.extend(userEyebrows)

        eyebrowsInfo = dict()

        for fullPath in eyebrows:
            bn = os.path.basename(fullPath).lower()
            bn = re.sub(r'.mhclo', '', bn)
            bn = re.sub(r'.mhpxy', '', bn)
            bn = re.sub(r'_', ' ', bn)
            bn = bn.strip()

            eyebrowsName = bn

            if not eyebrowsName in eyebrowsInfo:
                eyebrowsInfo[eyebrowsName] = dict()
                eyebrowsInfo[eyebrowsName]["fullPath"] = fullPath

                allowMixed = True
                allowFemale = True
                allowMale = True

                # TODO: Check if any eyebrows look gender specific

                eyebrowsInfo[eyebrowsName]["allowMixed"] = allowMixed
                eyebrowsInfo[eyebrowsName]["allowFemale"] = allowFemale
                eyebrowsInfo[eyebrowsName]["allowMale"] = allowMale

        eyebrowsNames = list(eyebrowsInfo.keys())
        eyebrowsNames.sort()

        self.allowedEyebrowsTable = QTableWidget()
        self.allowedEyebrowsTable.setRowCount(len(eyebrowsNames))
        self.allowedEyebrowsTable.setColumnCount(4)
        self.allowedEyebrowsTable.setHorizontalHeaderLabels(["Eyebrows", "Mixed", "Female", "Male"])

        i = 0
        for eyebrowsName in eyebrowsNames:
            eyebrowsSettings = eyebrowsInfo[eyebrowsName]
            eyebrowsWidgets = dict()

            self.allowedEyebrowsTable.setItem(i, 0, QTableWidgetItem(eyebrowsName))
            eyebrowsWidgets["mixed"] = r.addUI("allowedEyebrows", eyebrowsName, mhapi.ui.createCheckBox(""), subName="mixed")
            eyebrowsWidgets["female"] = r.addUI("allowedEyebrows", eyebrowsName, mhapi.ui.createCheckBox(""), subName="female")
            eyebrowsWidgets["male"] = r.addUI("allowedEyebrows", eyebrowsName, mhapi.ui.createCheckBox(""), subName="male")
            r.addUI("allowedEyebrows", eyebrowsName, eyebrowsSettings["fullPath"], subName="fullPath")

            self.allowedEyebrowsTable.setCellWidget(i, 1, eyebrowsWidgets["mixed"])
            self.allowedEyebrowsTable.setCellWidget(i, 2, eyebrowsWidgets["female"])
            self.allowedEyebrowsTable.setCellWidget(i, 3, eyebrowsWidgets["male"])

            eyebrowsWidgets["mixed"].setChecked(eyebrowsSettings["allowMixed"])
            eyebrowsWidgets["female"].setChecked(eyebrowsSettings["allowFemale"])
            eyebrowsWidgets["male"].setChecked(eyebrowsSettings["allowMale"])

            i = i + 1

        self._generalMainTableSettings(self.allowedEyebrowsTable)

        layout.addWidget(mhapi.ui.createLabel(""))
        layout.addWidget(mhapi.ui.createLabel("Allowed eyebrows:"))
        layout.addWidget(self.allowedEyebrowsTable)

    def _setupAllowedEyelashesTable(self, layout, r):
        sysEyelashes = mhapi.assets.getAvailableSystemEyelashes()
        userEyelashes = mhapi.assets.getAvailableUserEyelashes()

        eyelashes = []
        eyelashes.extend(sysEyelashes)
        eyelashes.extend(userEyelashes)

        eyelashesInfo = dict()

        for fullPath in eyelashes:
            bn = os.path.basename(fullPath).lower()
            bn = re.sub(r'.mhclo', '', bn)
            bn = re.sub(r'.mhpxy', '', bn)
            bn = re.sub(r'_', ' ', bn)
            bn = bn.strip()

            eyelashesName = bn

            if not eyelashesName in eyelashesInfo:
                eyelashesInfo[eyelashesName] = dict()
                eyelashesInfo[eyelashesName]["fullPath"] = fullPath

                allowMixed = True
                allowFemale = True
                allowMale = True

                # TODO: Check if any eyelashes look gender specific

                eyelashesInfo[eyelashesName]["allowMixed"] = allowMixed
                eyelashesInfo[eyelashesName]["allowFemale"] = allowFemale
                eyelashesInfo[eyelashesName]["allowMale"] = allowMale

        eyelashesNames = list(eyelashesInfo.keys())
        eyelashesNames.sort()

        self.allowedEyelashesTable = QTableWidget()
        self.allowedEyelashesTable.setRowCount(len(eyelashesNames))
        self.allowedEyelashesTable.setColumnCount(4)
        self.allowedEyelashesTable.setHorizontalHeaderLabels(["Eyelashes", "Mixed", "Female", "Male"])

        i = 0
        for eyelashesName in eyelashesNames:
            eyelashesSettings = eyelashesInfo[eyelashesName]
            eyelashesWidgets = dict()

            self.allowedEyelashesTable.setItem(i, 0, QTableWidgetItem(eyelashesName))
            eyelashesWidgets["mixed"] = r.addUI("allowedEyelashes", eyelashesName, mhapi.ui.createCheckBox(""), subName="mixed")
            eyelashesWidgets["female"] = r.addUI("allowedEyelashes", eyelashesName, mhapi.ui.createCheckBox(""), subName="female")
            eyelashesWidgets["male"] = r.addUI("allowedEyelashes", eyelashesName, mhapi.ui.createCheckBox(""), subName="male")
            r.addUI("allowedEyelashes", eyelashesName, eyelashesSettings["fullPath"], subName="fullPath")

            self.allowedEyelashesTable.setCellWidget(i, 1, eyelashesWidgets["mixed"])
            self.allowedEyelashesTable.setCellWidget(i, 2, eyelashesWidgets["female"])
            self.allowedEyelashesTable.setCellWidget(i, 3, eyelashesWidgets["male"])

            eyelashesWidgets["mixed"].setChecked(eyelashesSettings["allowMixed"])
            eyelashesWidgets["female"].setChecked(eyelashesSettings["allowFemale"])
            eyelashesWidgets["male"].setChecked(eyelashesSettings["allowMale"])

            i = i + 1

        self._generalMainTableSettings(self.allowedEyelashesTable)

        layout.addWidget(mhapi.ui.createLabel(""))
        layout.addWidget(mhapi.ui.createLabel("Allowed eyelashes:"))
        layout.addWidget(self.allowedEyelashesTable)


    def _setupAllowedSkinsTables(self, layout, r):

        sysSkins = mhapi.assets.getAvailableSystemSkins()
        userSkins = mhapi.assets.getAvailableUserSkins()

        allowedFemaleSkins = dict()
        allowedMaleSkins = dict()

        #pp.pprint(sysSkins)
        #pp.pprint(userSkins)

        skinBaseNames = []
        for s in sysSkins:
            bn = os.path.basename(s).lower()
            bn = re.sub(r'.mhmat','',bn)
            bn = re.sub(r'_', ' ', bn)
            skinBaseNames.append(bn)

            allowedFemaleSkins[bn] = dict()
            allowedFemaleSkins[bn]["fullPath"] = os.path.abspath(s)
            allowedMaleSkins[bn] = dict()
            allowedMaleSkins[bn]["fullPath"] = os.path.abspath(s)

        for s in userSkins:
            bn = os.path.basename(s).lower()
            bn = re.sub(r'.mhmat', '', bn)
            bn = re.sub(r'_', ' ', bn)
            skinBaseNames.append(bn)

            allowedFemaleSkins[bn] = dict()
            allowedFemaleSkins[bn]["fullPath"] = os.path.abspath(s)
            allowedMaleSkins[bn] = dict()
            allowedMaleSkins[bn]["fullPath"] = os.path.abspath(s)

        skinBaseNames.sort()

        self.allowedFemaleSkinsTable = QTableWidget()
        self.allowedFemaleSkinsTable.setRowCount(len(skinBaseNames))
        self.allowedFemaleSkinsTable.setColumnCount(5)
        self.allowedFemaleSkinsTable.setHorizontalHeaderLabels(["Skin", "Mixed", "African", "Asian", "Caucasian"])


        self.allowedMaleSkinsTable = QTableWidget()
        self.allowedMaleSkinsTable.setRowCount(len(skinBaseNames))
        self.allowedMaleSkinsTable.setColumnCount(5)
        self.allowedMaleSkinsTable.setHorizontalHeaderLabels(["Skin", "Mixed", "African", "Asian", "Caucasian"])

        skins = dict()

        i = 0
        for n in skinBaseNames:

            female = allowedFemaleSkins[n]
            male = allowedMaleSkins[n]

            self.allowedFemaleSkinsTable.setItem(i, 0, QTableWidgetItem(n))
            self.allowedMaleSkinsTable.setItem(i, 0, QTableWidgetItem(n))

            male["mixed"] = r.addUI("allowedMaleSkins",n,mhapi.ui.createCheckBox(""),subName="mixed")
            male["african"] = r.addUI("allowedMaleSkins",n,mhapi.ui.createCheckBox(""),subName="african")
            male["asian"] = r.addUI("allowedMaleSkins",n,mhapi.ui.createCheckBox(""),subName="asian")
            male["caucasian"] = r.addUI("allowedMaleSkins",n,mhapi.ui.createCheckBox(""),subName="caucasian")
            r.addUI("allowedMaleSkins", n, allowedMaleSkins[n]["fullPath"], subName="fullPath")

            self.allowedMaleSkinsTable.setCellWidget(i, 1, male["mixed"])
            self.allowedMaleSkinsTable.setCellWidget(i, 2, male["african"])
            self.allowedMaleSkinsTable.setCellWidget(i, 3, male["asian"])
            self.allowedMaleSkinsTable.setCellWidget(i, 4, male["caucasian"])

            female["mixed"] = r.addUI("allowedFemaleSkins",n,mhapi.ui.createCheckBox(""),subName="mixed")
            female["african"] = r.addUI("allowedFemaleSkins",n,mhapi.ui.createCheckBox(""),subName="african")
            female["asian"] = r.addUI("allowedFemaleSkins",n,mhapi.ui.createCheckBox(""),subName="asian")
            female["caucasian"] = r.addUI("allowedFemaleSkins",n,mhapi.ui.createCheckBox(""),subName="caucasian")
            r.addUI("allowedFemaleSkins", n, allowedFemaleSkins[n]["fullPath"], subName="fullPath")

            self.allowedFemaleSkinsTable.setCellWidget(i, 1, female["mixed"])
            self.allowedFemaleSkinsTable.setCellWidget(i, 2, female["african"])
            self.allowedFemaleSkinsTable.setCellWidget(i, 3, female["asian"])
            self.allowedFemaleSkinsTable.setCellWidget(i, 4, female["caucasian"])

            if self._matchesEthnicGender(n,"female") and not "special" in n:

                female["mixed"].setChecked(True)

                if self._matchesEthnicGender(n,ethnicity="african"):
                    female["african"].setChecked(True)
                if self._matchesEthnicGender(n,ethnicity="asian") and not self._matchesEthnicGender(n,ethnicity="caucasian"):
                    female["asian"].setChecked(True)
                if self._matchesEthnicGender(n,ethnicity="caucasian"):
                    female["caucasian"].setChecked(True)

            if self._matchesEthnicGender(n,"male") and not self._matchesEthnicGender(n,"female") and not "special" in n:

                male["mixed"].setChecked(True)

                if self._matchesEthnicGender(n,ethnicity="african"):
                    male["african"].setChecked(True)
                if self._matchesEthnicGender(n,ethnicity="asian") and not self._matchesEthnicGender(n,ethnicity="caucasian"):
                    male["asian"].setChecked(True)
                if self._matchesEthnicGender(n,ethnicity="caucasian"):
                    male["caucasian"].setChecked(True)


            i = i + 1

        self._generalMainTableSettings(self.allowedFemaleSkinsTable)
        self._generalMainTableSettings(self.allowedMaleSkinsTable)

        i = 1
        while i < 5:
            self.allowedFemaleSkinsTable.setColumnWidth(i, 80)
            self.allowedMaleSkinsTable.setColumnWidth(i, 80)
            i = i + 1


        layout.addWidget(mhapi.ui.createLabel("Allowed female skins:"))
        layout.addWidget(self.allowedFemaleSkinsTable)

        layout.addWidget(mhapi.ui.createLabel(""))

        layout.addWidget(mhapi.ui.createLabel("Allowed male skins:"))
        layout.addWidget(self.allowedMaleSkinsTable)

        self.allowedFemaleSkins = allowedFemaleSkins
        self.allowedMaleSkins = allowedMaleSkins


    def _matchesEthnicGender(self, teststring, gender = None, ethnicity = None):

        if not gender is None:
            if not gender in teststring:
                return False
        if not ethnicity is None:
            if not ethnicity in teststring:
                return False

        return True


    def _createExportSettings(self, r):
        self.exportPanel = mhapi.ui.createGroupBox("Export settings")
        self.exportPanel.addWidget(mhapi.ui.createLabel("File name base"))
        r.addUI("output", "fnbase", self.exportPanel.addWidget(mhapi.ui.createTextEdit("mass")))
        self.exportPanel.addWidget(mhapi.ui.createLabel(""))

        data = ["MHM","OBJ","MHX2","FBX","DAE"]

        self.exportPanel.addWidget(mhapi.ui.createLabel("File format"))
        r.addUI("output", "fileformat", self.exportPanel.addWidget(mhapi.ui.createComboBox(data=data)))

        info = "\nFiles end up in the\n"
        info +="usual directory, named\n"
        info +="with the file name base\n"
        info +="plus four digits plus\n"
        info +="file extension."

        self.exportPanel.addWidget(mhapi.ui.createLabel(info))

        return self.exportPanel

    def _createProducePanel(self, r):
        self.producePanel = mhapi.ui.createGroupBox("Produce")

        self.producePanel.addWidget(mhapi.ui.createLabel("Number of characters"))
        r.addUI("output", "numfiles", self.producePanel.addWidget(mhapi.ui.createTextEdit("5")))
        self.producePanel.addWidget(mhapi.ui.createLabel(""))
        self.produceButton = self.producePanel.addWidget(mhapi.ui.createButton("Produce"))

        @self.produceButton.mhEvent
        def onClicked(event):
            self._onProduceClick()

        return self.producePanel

    def _createModelingSettings(self, r):
        self.modelingPanel = mhapi.ui.createGroupBox("Modeling settings")

        defaultUnchecked = ["arms","hands","legs","feet"]

        mfi = ModifierInfo()
        gn = mfi.getModifierGroupNames()
        for n in gn:
            sel = not n in defaultUnchecked
            label = n
            if n == "breast":
                label = "breasts (if fem)"
            r.addUI("modeling", n, self.modelingPanel.addWidget(mhapi.ui.createCheckBox(label="Randomize " + label, selected=sel)))

        self.modelingPanel.addWidget(mhapi.ui.createLabel())
        r.addUI("modeling", "maxdev", self.modelingPanel.addWidget(mhapi.ui.createSlider(value=0.3, min=0.0, max=1.0, label="Max deviation from default")))

        #self.modelingPanel.addWidget(mhapi.ui.createLabel())
        #r.addUI("modeling", "symmetry", self.modelingPanel.addWidget(mhapi.ui.createSlider(value=0.7, min=0.0, max=1.0, label="Symmetry")))

        return self.modelingPanel

    def _createMacroSettings(self, r):
        self.macroPanel = mhapi.ui.createGroupBox("Macro settings")

        r.addUI("macro", "randomizeAge", self.macroPanel.addWidget(mhapi.ui.createCheckBox(label="Randomize age", selected=True)))
        r.addUI("macro", "ageMinimum", self.macroPanel.addWidget(mhapi.ui.createSlider(label="Minimum age", value=0.45)))
        r.addUI("macro", "ageMaximum", self.macroPanel.addWidget(mhapi.ui.createSlider(label="Maximum age", value=0.95)))

        self.macroPanel.addWidget(mhapi.ui.createLabel())

        r.addUI("macro", "randomizeWeight", self.macroPanel.addWidget(mhapi.ui.createCheckBox(label="Randomize weight", selected=True)))
        r.addUI("macro", "weightMinimum", self.macroPanel.addWidget(mhapi.ui.createSlider(label="Minimum weight", value=0.1)))
        r.addUI("macro", "weightMaximum", self.macroPanel.addWidget(mhapi.ui.createSlider(label="Maximum weight", value=0.9)))

        self.macroPanel.addWidget(mhapi.ui.createLabel())

        r.addUI("macro", "randomizeHeight", self.macroPanel.addWidget(mhapi.ui.createCheckBox(label="Randomize height", selected=True)))
        r.addUI("macro", "heightMinimum", self.macroPanel.addWidget(mhapi.ui.createSlider(label="Minimum height", value=0.2)))
        r.addUI("macro", "heightMaximum", self.macroPanel.addWidget(mhapi.ui.createSlider(label="Maximum height", value=0.9)))

        self.macroPanel.addWidget(mhapi.ui.createLabel())

        r.addUI("macro", "randomizeMuscle", self.macroPanel.addWidget(mhapi.ui.createCheckBox(label="Randomize muscle", selected=True)))
        r.addUI("macro", "muscleMinimum", self.macroPanel.addWidget(mhapi.ui.createSlider(label="Minimum muscle", value=0.3)))
        r.addUI("macro", "muscleMaximum", self.macroPanel.addWidget(mhapi.ui.createSlider(label="Maximum muscle", value=0.8)))

        self.macroPanel.addWidget(mhapi.ui.createLabel())

        r.addUI("macro", "gender", self.macroPanel.addWidget(mhapi.ui.createCheckBox(label="Randomize gender", selected=True)))
        r.addUI("macro", "genderabsolute", self.macroPanel.addWidget(mhapi.ui.createCheckBox(label="Absolute gender", selected=True)))

        self.macroPanel.addWidget(mhapi.ui.createLabel())

        r.addUI("macro", "ethnicity", self.macroPanel.addWidget(mhapi.ui.createCheckBox(label="Randomize ethnicity", selected=True)))
        r.addUI("macro", "ethnicityabsolute", self.macroPanel.addWidget(mhapi.ui.createCheckBox(label="Absolute ethnicity", selected=True)))

        return self.macroPanel

    def _onProduceClick(self):
        #print("Produce")

        #self.randomizationSettings.dumpValues()

        self.initialState = HumanState()

        i = int(self.randomizationSettings.getValue("output","numfiles"))
        base = self.randomizationSettings.getValue("output","fnbase")

        max = i

        prog = Progress()

        while i > 0:
            prg = float(max - i + 1) / float(max)
            prgStr = str( max - i + 1) + " / " + str(max)
            prog(prg, desc="Randomizing " + prgStr)
            self.nextState = HumanState(self.randomizationSettings)
            self.nextState.applyState(False)
            format = self.randomizationSettings.getValue("output","fileformat")
            name = base + str(i).rjust(4,"0")

            prog(prg, desc="Exporting " + prgStr)

            if format == "MHM":
                path = mhapi.locations.getUserHomePath("models")
                if not os.path.exists(path):
                    os.makedirs(path)
                name = name + ".mhm"
                self.human.save(os.path.join(path,name))
            if format == "OBJ":
                mhapi.exports.exportAsOBJ(name + ".obj")
            if format == "DAE":
                mhapi.exports.exportAsDAE(name + ".dae")
            if format == "FBX":
                mhapi.exports.exportAsFBX(name + ".fbx")
            if format == "MHX2" or format == "MHX":
                mhapi.exports.exportAsMHX2(name + ".mhx2")

            prog(prg, desc="Evaluating")

            i = i - 1
            self.initialState.applyState(True)
            self.human.applyAllTargets()

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setText("Done!")
        self.msg.setWindowTitle("Produce")
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.show()
