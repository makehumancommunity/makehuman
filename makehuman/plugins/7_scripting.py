#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius

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

# We need this for gui controls
import gui3d
import mh
import humanmodifier
import material
import gui
import log
import os
from cStringIO import StringIO
from core import G
from codecs import open

class ScriptingView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Scripting')

        self.directory = os.getcwd()
        self.filename =  None

        box = self.addLeftWidget(gui.GroupBox('Script'))

        self.scriptText = self.addTopWidget(gui.DocumentEdit())
        self.scriptText.setText('');

        self.scriptText.setLineWrapMode(gui.DocumentEdit.NoWrap)

        self.loadButton = box.addWidget(gui.BrowseButton(mode='open'), 0, 0)
        self.loadButton.setLabel('Load ...')
        self.loadButton.directory = mh.getPath()
        self.saveButton = box.addWidget(gui.BrowseButton(mode='save'), 0, 1)
        self.saveButton.setLabel('Save ...')
        self.saveButton.directory = mh.getPath()

        @self.loadButton.mhEvent
        def onClicked(filename):
            if not filename:
                return

            if(os.path.exists(filename)):
                contents = open(filename, 'rU', encoding="utf-8").read()
                self.scriptText.setText(contents)
                dlg = gui.Dialog()
                dlg.prompt("Load script","File was loaded in an acceptable manner","OK")
                self.filename = filename
                self.directory = os.path.split(filename)[0]
            else:
                dlg = gui.Dialog()
                dlg.prompt("Load script","File %s does not exist","OK", fmtArgs=filename)

        @self.saveButton.mhEvent
        def onClicked(filename):
            if not filename:
                return

            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.scriptText.getText())
            dlg = gui.Dialog()
            dlg.prompt("Save script","File was written in an acceptable manner","OK")
            self.filename = filename
            self.directory = os.path.split(filename)[0]

        box2 = self.addLeftWidget(gui.GroupBox('Examples'))

        self.insertLabel = box2.addWidget(gui.TextView('Append example to script'))
        self.listView = box2.addWidget(gui.ListView())
        self.listView.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)

        testlist = [ 
            'applyTarget()', 
            'incrementingFilename()',
            'getHeightCm()',
            'getPositionX()',
            'getPositionY()',
            'getPositionZ()',
            'getRotationX()',
            'getRotationY()',
            'getRotationZ()',
            'getZoom()',
            'loadModel()',
            'modifyPositionX()',
            'modifyPositionY()',
            'modifyPositionZ()',
            'modifyRotationX()',
            'modifyRotationY()',
            'modifyRotationZ()',
            'modifyZoom()',
            'printCameraInfo()',
            'printDetailStack()',
            'printPositionInfo()',
            'printRotationInfo()',
            'saveModel()',
            'screenShot()',
            'setAge()',
            'setPositionX()',
            'setPositionY()',
            'setPositionZ()',
            'setRotationX()',
            'setRotationY()',
            'setRotationZ()',
            'setZoom()',
            'setWeight()',
            'setMaterial()',
            'setHeadSquareness()',
            'getModelingParameters()',
            'updateModelingParameter()',
            'updateModelingParameters()',
            'saveObj()'
        ]

        self.listView.setData(testlist)

        self.insertButton = box2.addWidget(gui.Button('Append'))

        @self.insertButton.mhEvent
        def onClicked(event):
            item = self.listView.getSelectedItem()

            if(item == 'applyTarget()'):
                text = "# applyTarget(<target file name>, <power (from 0.0 to 1.0)>)\n"
                text = text + "#\n"
                text = text + "# This will apply the target on the model. If the target was already applied, the power will be updated\n"
                text = text + "# Note that targets are relative to the data/targets directory, and should not include the .target\n"
                text = text + "# extension, so a valid target name would be, for example, \"breast/breast-dist-max\"\n\n"
                text = text + "MHScript.applyTarget('aTargetName',1.0)\n\n"
                self.scriptText.addText(text)

            if(item == 'loadModel()'):
                text = "# loadModel(<model name>,[path])\n"
                text = text + "#\n"
                text = text + "# This will load a human model from an MHM file. The <model name> part should be a string without spaces\n"
                text = text + "# and without the .MHM extension. The [path] part defaults to the user's makehuman/models directory.\n\n"
                text = text + "MHScript.loadModel('myTestModel')\n\n"
                self.scriptText.addText(text)

            if(item == 'incrementingFilename()'):
                text = "# incrementingFilename(<file name base>, [file extension], [pad length])\n"
                text = text + "#\n"
                text = text + "# This will return a file name containing a numerical component which increases by one for each call.\n"
                text = text + "# The default file extension is \".png\". The default pad length is 4. For example, the following lines:\n";
                text = text + "#\n"
                text = text + "# print incrementingFilename(\"test\",\".target\",3) + \"\\n\"\n"
                text = text + "# print incrementingFilename(\"test\",\".target\",3) + \"\\n\"\n"
                text = text + "#\n"
                text = text + "# Will print:\n"
                text = text + "#\n"
                text = text + "# test001.target\n"
                text = text + "# test002.target\n"
                text = text + "#\n"
                text = text + "# The counter is reset each time the script is executed\n\n"
                text = text + "filename = MHScript.incrementingFilename('test')\n\n"
                self.scriptText.addText(text)

            if(item == 'printCameraInfo()'):
                text = "# printCameraInfo()\n"
                text = text + "#\n"
                text = text + "# This will print info about how the camera is targeted and focused .\n\n"
                text = text + "MHScript.printCameraInfo()\n\n"
                self.scriptText.addText(text)

            if(item == 'printDetailStack()'):
                text = "# printDetailStack()\n"
                text = text + "#\n"
                text = text + "# This will print a list of all applied targets (and their weights) to standard output.\n\n"
                text = text + "MHScript.printDetailStack()\n\n"
                self.scriptText.addText(text)

            if(item == 'printPositionInfo()'):
                text = "# printPositionInfo()\n"
                text = text + "#\n"
                text = text + "# This will print info about where the human object is currently located.\n\n"
                text = text + "MHScript.printPositionInfo()\n\n"
                self.scriptText.addText(text)

            if(item == 'printRotationInfo()'):
                text = "# printRotationInfo()\n"
                text = text + "#\n"
                text = text + "# This will print info about how the human object is currently rotated.\n\n"
                text = text + "MHScript.printRotationInfo()\n\n"
                self.scriptText.addText(text)

            if(item == 'saveModel()'):
                text = "# saveModel(<model name>,[path])\n"
                text = text + "#\n"
                text = text + "# This will save the human model to an MHM file. The <model name> part should be a string without spaces\n"
                text = text + "# and without the .MHM extension. The [path] part defaults to the user's makehuman/models directory.\n"
                text = text + "# Note that this will not save any thumbnail.\n\n"
                text = text + "MHScript.saveModel('myTestModel')\n\n"
                self.scriptText.addText(text)

            if(item == 'saveObj()'):
                text = "# saveObj(<model name>,[path])\n"
                text = text + "#\n"
                text = text + "# This will save the human model to a wavefront .OBJ file. The <model name> part should be a string without spaces\n"
                text = text + "# and without the .obj extension. The [path] part defaults to the user's makehuman/exports directory.\n"
                text = text + "MHScript.saveObj('myOBJExport')\n\n"
                self.scriptText.addText(text)

            if(item == 'screenShot()'):
                text = "# screenShot(<png file name>)\n"
                text = text + "#\n"
                text = text + "# This will save a png file of how the model currently looks.\n\n"
                text = text + "MHScript.screenShot('screenshot.png')\n\n"
                self.scriptText.addText(text)

            if(item == 'setAge()'):
                text = "# setAge(age)\n"
                text = text + "#\n"
                text = text + "# Sets the age of the model. The age parameter is a float between 0 and 1, where 0 is 1 year old, 0.18 is 10 years old, 0.5 is 25 years and 1 equals 90 years old.\n\n"
                text = text + "MHScript.setAge(0.5)\n\n"
                self.scriptText.addText(text)

            if(item == 'setWeight()'):
                text = "# setWeight(weight)\n"
                text = text + "#\n"
                text = text + "# Sets the weight of the model. The weight parameter is a float between 0 and 1, where 0 is starved and\n"
                text = text + "# 1 is severely overweight\n\n"
                text = text + "MHScript.setWeight(0.5)\n\n"
                self.scriptText.addText(text)

            if(item == 'setHeadSquareness()'):
                text = "# setHeadSquareness(squareness)\n"
                text = text + "#\n"
                text = text + "# Sets the squaredness of the model's head. The squareness parameter is a float between 0 and 1, where 0 is not square and\n"
                text = text + "# 1 is very square shaped\n\n"
                text = text + "MHScript.setHeadSquareness(0.5)\n\n"
                self.scriptText.addText(text)

            if(item == 'setMaterial()'):
                text = "# setMaterial(mhmat_filename)\n"
                text = text + "#\n"
                text = text + "# Sets the skin material of the 3D model\n"
                text = text + "# The filename must be realtive to the App Resources directory\n\n"
                text = text + "MHScript.setMaterial('data/skins/young_caucasian_female/young_caucasian_female.mhmat')\n\n"
                self.scriptText.addText(text)

            if(item == 'getHeightCm()'):
                text = "# getHeightCm()\n"
                text = text + "#\n"
                text = text + "# Gets the current height of the model, in cm.\n\n"
                text = text + "height = MHScript.getHeightCm()\n"
                text = text + "print('height='+str(height))\n\n"
                self.scriptText.addText(text)

            if(item == 'getModelingParameters()'):
                text = "# getModelingParameters()\n"
                text = text + "#\n"
                text = text + "# Prints the names of all modeling aspects that can be modified on the human model.\n"
                text = text + "MHScript.getModelingParameters()\n\n"
                self.scriptText.addText(text)

            if(item == 'updateModelingParameter()'):
                text = "# updateModelingParameter(parameterName, value)\n"
                text = text + "#\n"
                text = text + "# Sets the modeling parameter with specified name of the model to the specified value.\n"
                text = text + "# The value is a float between 0 and 1, where 0 means nothing at all or minimal, and 1 is the maximum value.\n\n"
                text = text + "MHScript.updateModelingParameter('macrodetails/Age', 0.7)\n\n"
                self.scriptText.addText(text)

            if(item == 'updateModelingParameters()'):
                text = "# updateModelingParameters(dictOfParameterNameAndValue)\n"
                text = text + "#\n"
                text = text + "# Sets more modeling parameters with specified names of the model to the specified values.\n"
                text = text + "# Faster than setting parameters one by one because the 3D mesh is updated only once.\n"
                text = text + "# The values are a float between 0 and 1, where 0 means nothing at all or minimal, and 1 is the maximum value.\n\n"
                text = text + "MHScript.updateModelingParameters({'macrodetails/Caucasian': 1.000,'macrodetails/Gender': 1.000,'macrodetails/Age': 0.250})\n\n"
                self.scriptText.addText(text)

            if(item == 'setPositionX()'):
                text = "# setPositionX(xpos)\n"
                text = text + "#\n"
                text = text + "# Sets the X position of the model of the model in 3d space, where 0.0 is centered.\n\n"
                text = text + "MHScript.setPositionX(2.0)\n\n"
                self.scriptText.addText(text)

            if(item == 'getPositionX()'):
                text = "# getPositionX()\n"
                text = text + "#\n"
                text = text + "# Returns the current X position of the model of the model in 3d space.\n\n"
                text = text + "MHScript.getPositionX()\n\n"
                self.scriptText.addText(text)

            if(item == 'modifyPositionX()'):
                text = "# modifyPositionX(xmod)\n"
                text = text + "#\n"
                text = text + "# Modifies X position of the model of the model in 3d space.\n\n"
                text = text + "MHScript.modifyPositionX(-0.1)\n\n"
                self.scriptText.addText(text)

            if(item == 'setPositionZ()'):
                text = "# setPositionZ(zpos)\n"
                text = text + "#\n"
                text = text + "# Sets the Z position of the model of the model in 3d space, where 0.0 is centered.\n\n"
                text = text + "MHScript.setPositionZ(2.0)\n\n"
                self.scriptText.addText(text)

            if(item == 'getPositionZ()'):
                text = "# getPositionZ()\n"
                text = text + "#\n"
                text = text + "# Returns the current Z position of the model of the model in 3d space.\n\n"
                text = text + "MHScript.getPositionZ()\n\n"
                self.scriptText.addText(text)

            if(item == 'modifyPositionZ()'):
                text = "# modifyPositionZ(zmod)\n"
                text = text + "#\n"
                text = text + "# Modifies Z position of the model of the model in 3d space.\n\n"
                text = text + "MHScript.modifyPositionZ(-0.1)\n\n"
                self.scriptText.addText(text)

            if(item == 'setPositionY()'):
                text = "# setPositionY(ypos)\n"
                text = text + "#\n"
                text = text + "# Sets the Y position of the model of the model in 3d space, where 0.0 is centered.\n"
                text = text + "# Note that the depth of the scene is clipped, so if you move the model too far back\n"
                text = text + "# it will disappear. You will most likely want to use zoom instead of Y position.\n\n";
                text = text + "MHScript.setPositionY(2.0)\n\n"
                self.scriptText.addText(text)

            if(item == 'getPositionY()'):
                text = "# getPositionY()\n"
                text = text + "#\n"
                text = text + "# Returns the current Y position of the model of the model in 3d space.\n\n"
                text = text + "MHScript.getPositionY()\n\n"
                self.scriptText.addText(text)

            if(item == 'modifyPositionY()'):
                text = "# modifyPositionY(ymod)\n"
                text = text + "#\n"
                text = text + "# Modifies Y position of the model of the model in 3d space.\n"
                text = text + "# Note that the depth of the scene is clipped, so if you move the model too far back\n"
                text = text + "# it will disappear. You will most likely want to use zoom instead of Y position.\n\n";
                text = text + "MHScript.modifyPositionY(-0.1)\n\n"
                self.scriptText.addText(text)

            if(item == 'setRotationX()'):
                text = "# setRotationX(xrot)\n"
                text = text + "#\n"
                text = text + "# Sets the rotation around the X axis for the model, where 0.0 is frontal projection.\n"
                text = text + "# Rotation is set in degrees from -180.0 to +180.0 (these two extremes are equal)\n\n"
                text = text + "MHScript.setRotationX(90.0)\n\n"
                self.scriptText.addText(text)

            if(item == 'getRotationX()'):
                text = "# getRotationX()\n"
                text = text + "#\n"
                text = text + "# Returns the current rotatation around the X axis of the model.\n\n"
                text = text + "MHScript.getRotationX()\n\n"
                self.scriptText.addText(text)

            if(item == 'modifyRotationX()'):
                text = "# modifyRotationX(xmod)\n"
                text = text + "#\n"
                text = text + "# Modifies the rotation around the X axis for the model, where 0.0 is frontal projection.\n"
                text = text + "# Rotation is set in degrees from -180.0 to +180.0 (these two extremes are equal)\n\n"
                text = text + "MHScript.modifyRotationX(-5.0)\n\n"
                self.scriptText.addText(text)

            if(item == 'setRotationZ()'):
                text = "# setRotationZ(zrot)\n"
                text = text + "#\n"
                text = text + "# Sets the rotation around the Z axis for the model, where 0.0 is frontal projection.\n"
                text = text + "# Rotation is set in degrees from -180.0 to +180.0 (these two extremes are equal)\n\n"
                text = text + "MHScript.setRotationZ(90.0)\n\n"
                self.scriptText.addText(text)

            if(item == 'getRotationZ()'):
                text = "# getRotationZ()\n"
                text = text + "#\n"
                text = text + "# Returns the current rotatation around the Z axis of the model.\n\n"
                text = text + "MHScript.getRotationZ()\n\n"
                self.scriptText.addText(text)

            if(item == 'modifyRotationZ()'):
                text = "# modifyRotationZ(zmod)\n"
                text = text + "#\n"
                text = text + "# Modifies the rotation around the Z axis for the model, where 0.0 is frontal projection.\n"
                text = text + "# Rotation is set in degrees from -180.0 to +180.0 (these two extremes are equal)\n\n"
                text = text + "MHScript.modifyRotationZ(-5.0)\n\n"
                self.scriptText.addText(text)

            if(item == 'setRotationY()'):
                text = "# setRotationY(yrot)\n"
                text = text + "#\n"
                text = text + "# Sets the rotation around the Y axis for the model, where 0.0 is upright projection.\n"
                text = text + "# Rotation is set in degrees from -180.0 to +180.0 (these two extremes are equal)\n\n"
                text = text + "MHScript.setRotationY(90.0)\n\n"
                self.scriptText.addText(text)

            if(item == 'getRotationY()'):
                text = "# getRotationY()\n"
                text = text + "#\n"
                text = text + "# Returns the current rotatation around the Y axis of the model.\n\n"
                text = text + "MHScript.getRotationY()\n\n"
                self.scriptText.addText(text)

            if(item == 'modifyRotationY()'):
                text = "# modifyRotationY(ymod)\n"
                text = text + "#\n"
                text = text + "# Modifies the rotation around the Y axis for the model, where 0.0 is upright projection.\n"
                text = text + "# Rotation is set in degrees from -180.0 to +180.0 (these two extremes are equal)\n\n"
                text = text + "MHScript.modifyRotationY(-5.0)\n\n"
                self.scriptText.addText(text)

            if(item == 'setZoom()'):
                text = "# setZoom(zoom)\n"
                text = text + "#\n"
                text = text + "# Sets current camera zoom. In practise this moves the camera closer or further from the.\n"
                text = text + "# the model. The zoom factor is reversed ans goes from 100.0 which is far away from the\n"
                text = text + "# the model as possible (if you move further away, the model will be clipped and disappear)\n"
                text = text + "# and 0.0 is inside the model. A zoom factor of 10.0 is what is used for the face\n"
                text = text + "# projection, and is in most cases as zoomed in as is functional.\n\n"
                text = text + "MHScript.setZoom(70.0)\n\n"
                self.scriptText.addText(text)

            if(item == 'modifyZoom()'):
                text = "# modifyZoom(zmod)\n"
                text = text + "#\n"
                text = text + "# Modifies current camera zoom. In practise this moves the camera closer or further from the.\n"
                text = text + "# the model. The zoom factor is reversed ans goes from 100.0 which is far away from the\n"
                text = text + "# the model as possible (if you move further away, the model will be clipped and disappear)\n"
                text = text + "# and 0.0 is inside the model. A zoom factor of 10.0 is what is used for the face\n"
                text = text + "# projection, and is in most cases as zoomed in as is functional.\n\n"
                text = text + "MHScript.modifyZoom(1.0)\n\n"
                self.scriptText.addText(text)

            if(item == 'getZoom()'):
                text = "# getZoom()\n"
                text = text + "#\n"
                text = text + "# Returns the current camera zoom factor.\n\n"
                text = text + "MHScript.getZoom()\n\n"
                self.scriptText.addText(text)
             
    def onShow(self, event):
        gui3d.app.statusPersist('This is a rough scripting module')

    def onHide(self, event):
        gui3d.app.statusPersist('')

class ScriptingExecuteTab(gui3d.TaskView):
    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Execute')

        box = self.addLeftWidget(gui.GroupBox('Execute'))

        self.execButton = box.addWidget(gui.Button('Execute'))

        @self.execButton.mhEvent
        def onClicked(event):
            #width = G.windowWidth;
            #height = G.windowHeight;

            global MHScript
            global scriptingView

            MHScript = Scripting()
            executeScript(str(scriptingView.scriptText.toPlainText()))

        box2 = self.addLeftWidget(gui.GroupBox('Fixed canvas size'))

        self.widthLabel = box2.addWidget(gui.TextView('Width'))
        self.widthEdit = box2.addWidget(gui.TextEdit(text='0'))
        self.heightLabel = box2.addWidget(gui.TextView('Height'))
        self.heightEdit = box2.addWidget(gui.TextEdit(text='0'))
        self.getButton = box2.addWidget(gui.Button('Get'))
        self.setButton = box2.addWidget(gui.Button('Set'))

        @self.getButton.mhEvent
        def onClicked(event):
            width = G.windowWidth;
            height = G.windowHeight;
            self.widthEdit.setText(str(width))
            self.heightEdit.setText(str(height))

        @self.setButton.mhEvent
        def onClicked(event):
            dlg = gui.Dialog()

            desiredWidth = self.widthEdit.getText()
            if(desiredWidth == None or not desiredWidth.isdigit()):
                dlg.prompt("Input error","Width and height must be valid integers","OK")
                return

            desiredHeight = self.heightEdit.getText()
            if(desiredHeight == None or not desiredHeight.isdigit()):
                dlg.prompt("Input error","Width and height must be valid integers","OK")
                return

            desiredWidth = int(desiredWidth)
            desiredHeight = int(desiredHeight)

            if(desiredHeight < 100 or desiredWidth < 100):
                dlg.prompt("Input error","Width and height must be at least 100 pixels each","OK")
                return

            # This is because we're excluding a passepartout when doing screenshots.
            desiredWidth = desiredWidth + 3
            desiredHeight = desiredHeight + 3

            qmainwin = G.app.mainwin
            central = qmainwin.centralWidget() 
            cWidth = central.frameSize().width()
            cHeight = central.frameSize().height()
            width = G.windowWidth;
            height = G.windowHeight;

            xdiff = desiredWidth - width;
            ydiff = desiredHeight - height;

            cWidth = cWidth + xdiff
            cHeight = cHeight + ydiff

            central.setFixedSize(cWidth,cHeight)
            qmainwin.adjustSize()

class Scripting():
    def __init__(self):
        self.human = gui3d.app.selectedHuman
        self.fileIncrement = 0;
        self.modelPath = mh.getPath('models')
        self.cam = G.app.modelCamera
        if(not os.path.exists(self.modelPath)):
            os.makedirs(self.modelPath)

    def applyTarget(self,targetName,power):
        log.message("SCRIPT: applyTarget(" + targetName + ", " + str(power) + ")")
        self.human.setDetail(mh.getSysDataPath("targets/" + targetName + ".target"), power)
        self.human.applyAllTargets()
        mh.redraw()

    def saveModel(self,name,path = mh.getPath('models')):
        log.message("SCRIPT: saveModel(" + name + "," + path + ")")
        filename = os.path.join(path,name + ".mhm")
        self.human.save(filename,name)

    def loadModel(self,name,path = mh.getPath('models')):
        log.message("SCRIPT: loadModel(" + name + "," + path + ")")
        filename = os.path.join(path,name + ".mhm")
        self.human.load(filename, True)

    def saveObj(self, name, path = mh.getPath('exports')):
        log.message("SCRIPT: saveObj(" + name + "," + path + ")")
        filename = os.path.join(path,name + ".obj")
        import wavefront
        wavefront.writeObjFile(filename, self.human.mesh)

    def screenShot(self,fileName):
        log.message("SCRIPT: screenShot(" + fileName + ")")
        width = G.windowWidth;
        height = G.windowHeight;
        width = width - 3;
        height = height - 3;
        mh.grabScreen(1,1,width,height,fileName)

    def incrementingFilename(self,basename,suffix=".png",width=4):
        fn = basename;
        i = width - 1;
        self.fileIncrement += 1
        while(i > 0):       
            power = 10**i;
            if(self.fileIncrement < power):
                fn = fn + "0";
            i -= 1
        fn = fn + str(self.fileIncrement) + suffix
        return fn        

    def printDetailStack(self):
        log.message("SCRIPT: printDetailStack()")
        for target in self.human.targetsDetailStack.keys():
            print str(self.human.targetsDetailStack[target]) + "\t" + target

    def setAge(self,age):
        log.message("SCRIPT: setAge(" + str(age) + ")")
        self.human.setAge(age)
        mh.redraw()

    def setWeight(self,weight):
        log.message("SCRIPT: setWeight(" + str(weight) + ")")
        self.human.setWeight(weight)
        mh.redraw()

    def setMaterial(self, mhmat_filename):
        log.message("SCRIPT: setMaterial(" + mhmat_filename + ")")
        # The file must be realtive to the App Resources directory,
        # e.g.: 'data/skins/young_caucasian_female/young_caucasian_female.mhmat'
        mat = material.fromFile(mhmat_filename)
        self.human.material = mat

    def getHeightCm(self):
        return gui3d.app.selectedHuman.getHeightCm()

    def getModelingParameters(self):
        log.message("SCRIPT: getModelingParameters()")
        modifierNamesList = sorted( self.human.modifierNames )
        print "Modifier names:"
        print "\n".join( modifierNamesList )

    def updateModelingParameter(self, parameterName, value):
        log.message("SCRIPT: updateModelingParameter(parameterName, value)")
        modifier = self.human.getModifier(parameterName)
        modifier.setValue(value)
        self.human.applyAllTargets()
        mh.redraw()

    def updateModelingParameters(self, dictOfParameterNameAndValue):
        log.message("SCRIPT: updateModelingParameters("+str(dictOfParameterNameAndValue)+")")
        for key, value in dictOfParameterNameAndValue.iteritems():
            modifier = self.human.getModifier(key)
            modifier.setValue(value)
        self.human.applyAllTargets()
        mh.redraw()

    def setHeadSquareness(self, squareness):
        log.message("SCRIPT: setHeadSquareness(" + str(squareness) + ")")
        modifier = self.human.getModifier('head/head-square')
        modifier.setValue(squareness)
        self.human.applyAllTargets()
        mh.redraw()

    def setPositionX(self,xpos):
        log.message("SCRIPT: setPositionX(" + str(xpos) + ")")
        pos = self.human.getPosition()
        pos[0] = xpos
        self.human.setPosition(pos)
        mh.redraw()

    def getPositionX(self):
        log.message("SCRIPT: getPositionX()")
        pos = self.human.getPosition()
        return pos[0]

    def modifyPositionX(self,xmod):
        log.message("SCRIPT: modifyPositionX(" + str(xmod) + ")")
        pos = self.human.getPosition()
        pos[0] = pos[0] + xmod
        self.human.setPosition(pos)
        mh.redraw()

    def setPositionZ(self,zpos):
        log.message("SCRIPT: setPositionZ(" + str(zpos) + ")")
        pos = self.human.getPosition()
        pos[1] = zpos
        self.human.setPosition(pos)
        mh.redraw()

    def getPositionZ(self):
        log.message("SCRIPT: getPositionZ()")
        pos = self.human.getPosition()
        return pos[1]

    def modifyPositionZ(self,zmod):
        log.message("SCRIPT: modifyPositionZ(" + str(zmod) + ")")
        pos = self.human.getPosition()
        pos[1] = pos[1] + zmod
        self.human.setPosition(pos)
        mh.redraw()

    def setPositionY(self,ypos):
        log.message("SCRIPT: setPositionY(" + str(ypos) + ")")
        pos = self.human.getPosition()
        pos[2] = ypos
        self.human.setPosition(pos)
        mh.redraw()

    def getPositionY(self):
        log.message("SCRIPT: getPositionY()")
        pos = self.human.getPosition()
        return pos[2]

    def modifyPositionY(self,ymod):
        log.message("SCRIPT: modifyPositionY(" + str(ymod) + ")")
        pos = self.human.getPosition()
        pos[2] = pos[2] + ymod
        self.human.setPosition(pos)
        mh.redraw()

    def setRotationX(self,xrot):
        log.message("SCRIPT: setRotationX(" + str(xrot) + ")")
        rot = self.human.getRotation()
        rot[0] = xrot
        self.human.setRotation(rot)
        mh.redraw()

    def getRotationX(self):
        log.message("SCRIPT: getRotationX()")
        rot = self.human.getRotation()
        return rot[0]

    def modifyRotationX(self,xmod):
        log.message("SCRIPT: modifyRotationX(" + str(xmod) + ")")
        rot = self.human.getRotation()
        rot[0] = rot[0] + xmod
        self.human.setRotation(rot)
        mh.redraw()

    def setRotationZ(self,zrot):
        log.message("SCRIPT: setRotationZ(" + str(zrot) + ")")
        rot = self.human.getRotation()
        rot[1] = zrot
        self.human.setRotation(rot)
        mh.redraw()

    def getRotationZ(self):
        log.message("SCRIPT: getRotationZ()")
        rot = self.human.getRotation()
        return rot[1]

    def modifyRotationZ(self,zmod):
        log.message("SCRIPT: modifyRotationZ(" + str(zmod) + ")")
        rot = self.human.getRotation()
        rot[1] = rot[1] + zmod
        self.human.setRotation(rot)
        mh.redraw()

    def setRotationY(self,yrot):
        log.message("SCRIPT: setRotationY(" + str(yrot) + ")")
        rot = self.human.getRotation()
        rot[2] = yrot
        self.human.setRotation(rot)
        mh.redraw()

    def getRotationY(self):
        log.message("SCRIPT: getRotationY()")
        rot = self.human.getRotation()
        return rot[2]

    def modifyRotationY(self,ymod):
        log.message("SCRIPT: modifyRotationY(" + str(ymod) + ")")
        rot = self.human.getRotation()
        rot[2] = rot[2] + ymod
        self.human.setRotation(rot)
        mh.redraw()

    def printCameraInfo(self):
        log.message("SCRIPT: printCameraInfo()")

        # TODO update to new camera
        print "eyeX:\t" + str(self.cam.eyeX)
        print "eyeY:\t" + str(self.cam.eyeY)
        print "eyeZ:\t" + str(self.cam.eyeZ)
        print "focusX:\t" + str(self.cam.focusX)
        print "focusY:\t" + str(self.cam.focusY)
        print "focusZ:\t" + str(self.cam.focusZ)
        print "upX:\t" + str(self.cam.upX)
        print "upY:\t" + str(self.cam.upY)
        print "upZ:\t" + str(self.cam.upZ)

    def printPositionInfo(self):
        log.message("SCRIPT: printPositionInfo()")

        pos = self.human.getPosition();

        print "posX:\t" + str(pos[0])
        print "posY:\t" + str(pos[2])
        print "posZ:\t" + str(pos[1])

    def printRotationInfo(self):
        log.message("SCRIPT: printRotationInfo()")

        rot = self.human.getRotation();

        print "rotX:\t" + str(rot[0])
        print "rotY:\t" + str(rot[2])
        print "rotZ:\t" + str(rot[1])

    def getZoom(self):
        log.message("SCRIPT: getZoom()")
        return self.cam.zoomFactor

    def setZoom(self, zoom):
        log.message("SCRIPT: setZoom(" + str(zoom) + ")")
        self.cam.zoomFactor = zoom
        mh.redraw()

    def modifyZoom(self, zmod):
        log.message("SCRIPT: modifyZoom(" + str(zmod) + ")")
        self.cam.addZoom(zmod)
        mh.redraw()

MHScript = None

def executeScript(scriptSource):
    print scriptSource
    try:
        exec(scriptSource)
        dlg = gui.Dialog()
        dlg.prompt("Good job!","The script was executed without problems.","OK")
    except Exception as e:
        log.error(e, exc_info = True)
        dlg = gui.Dialog()
        dlg.prompt("Crappy script","The script produced an exception: " + format(str(e)),"OK")

scriptingView = None

def load(app):

    global scriptingView

    category = app.getCategory('Utilities')
    scriptingView = ScriptingView(category)
    executeView = ScriptingExecuteTab(category)
    taskview = category.addTask(scriptingView)
    taskview1 = category.addTask(executeView)

def unload(app):
    pass


