#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thanasis Papoutsidakis

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

Scene editor plugin.

This editor can create, load, edit and save .mhscene files,
and has tools to alter the scene's characteristics,
like lights and ambience, that are defined in the scene class.

"""

import mh
import gui
from core import G
import guirender


class SceneItem(object):
    def __init__(self, sceneview, label=""):
        # Call this last
        self.sceneview = sceneview
        self.label = label
        self.widget = gui.GroupBox(label)
        self.makeProps()

    def makeProps(self):
        pass

    def showProps(self):
        self.sceneview.propsBox.showWidget(self.widget)
        self.sceneview.activeItem = self

    def update(self):
        pass

    def __del__(self):
        self.widget.destroy()


class SceneItemAdder(SceneItem):
    # Virtual scene item for adding scene items.
    def __init__(self, sceneview):
        SceneItem.__init__(self, sceneview, "Add scene item")

    def makeProps(self):
        SceneItem.makeProps(self)
        self.lightbtn = self.widget.addWidget(gui.Button('Add light'))

        @self.lightbtn.mhEvent
        def onClicked(event):
            self.sceneview.scene.addLight()


class EnvironmentSceneItem(SceneItem):
    def __init__(self, sceneview):
        SceneItem.__init__(self, sceneview, "Environment properties")

    def makeProps(self):
        SceneItem.makeProps(self)

        self.colbox = self.widget.addWidget(
            VectorInput("Ambience",
                self.sceneview.scene.environment.ambience, True))

        @self.colbox.mhEvent
        def onChange(value):
            self.sceneview.scene.environment.ambience = value


class LightSceneItem(SceneItem):
    def __init__(self, sceneview, light, lid):
        self.lightid = lid
        self.light = light
        SceneItem.__init__(
            self, sceneview, "Light %s properties" % self.lightid)

    def makeProps(self):
        SceneItem.makeProps(self)

        self.posbox = self.widget.addWidget(
            VectorInput("Position", self.light.position))

        self.focbox = self.widget.addWidget(
            VectorInput("Focus", self.light.focus))

        self.colbox = self.widget.addWidget(
            VectorInput("Color", self.light.color, True))

        self.specbox = self.widget.addWidget(
            VectorInput("Specular", self.light.specular, True))

        self.fov = self.widget.addWidget(
            VectorInput("Spot angle", [self.light.fov]))

        self.att = self.widget.addWidget(
            VectorInput("Attenuation", [self.light.attenuation]))

        self.soft = self.widget.addWidget(
            BooleanInput("Soft light", self.light.areaLights > 1))

        self.size = self.widget.addWidget(
            VectorInput("Softness", [self.light.areaLightSize]))

        self.samples = self.widget.addWidget(
            VectorInput("Samples", [self.light.areaLights]))

        self.removebtn = self.widget.addWidget(
            gui.Button('Remove light ' + str(self.lightid)))

        @self.posbox.mhEvent
        def onChange(value):
            self.light.position = tuple(value)

        @self.focbox.mhEvent
        def onChange(value):
            self.light.focus = tuple(value)

        @self.colbox.mhEvent
        def onChange(value):
            self.light.color = tuple(value)

        @self.specbox.mhEvent
        def onChange(value):
            self.light.specular = tuple(value)

        @self.fov.mhEvent
        def onChange(value):
            self.light.fov = value[0]

        @self.att.mhEvent
        def onChange(value):
            self.light.attenuation = value[0]

        @self.soft.mhEvent
        def onChange(value):
            if value and self.light.areaLights <= 1:
                self.light.areaLights = 2
                self.samples.setValue([2])
            elif self.light.areaLights > 1:
                self.light.areaLights = 1
                self.samples.setValue([1])

        @self.size.mhEvent
        def onChange(value):
            self.light.attenuation = value[0]

        @self.samples.mhEvent
        def onChange(value):
            self.light.areaLights = int(value[0])
            self.soft.setValue(self.light.areaLights > 1)

        @self.removebtn.mhEvent
        def onClicked(event):
            self.sceneview.scene.removeLight(self.light)


class SceneEditorTaskView(guirender.RenderTaskView):

    def __init__(self, category):
        guirender.RenderTaskView.__init__(self, category, 'Scene Editor')

        # Declare settings
        G.app.addSetting('Scene_Editor_FileDlgPath', mh.getDataPath('scenes'))

        sceneBox = self.addLeftWidget(gui.GroupBox('Scene'))
        self.fnlbl = sceneBox.addWidget(gui.TextView('<New scene>'))
        self.saveButton = sceneBox.addWidget(gui.Button('Save'), 1, 0)
        self.loadButton = sceneBox.addWidget(gui.Button('Load ...'), 1, 1)
        self.saveAsButton = sceneBox.addWidget(gui.Button('Save As...'), 2, 0)
        self.closeButton = sceneBox.addWidget(gui.Button('Close'), 2, 1)

        itemBox = self.addLeftWidget(gui.GroupBox('Items'))
        self.itemList = itemBox.addWidget(gui.ListView())
        self.itemList.setSizePolicy(
            gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)

        self.propsBox = gui.StackedBox()
        self.addRightWidget(self.propsBox)

        self.addButton = itemBox.addWidget(gui.Button('Add...'))
        self.adder = SceneItemAdder(self)
        self.propsBox.addWidget(self.adder.widget)
        self.activeItem = None

        self._scene = None

        def doLoad():
            filename = mh.getOpenFileName(
                G.app.getSetting('Scene_Editor_FileDlgPath'),
                'MakeHuman scene (*.mhscene);;All files (*.*)')
            if filename:
                G.app.setSetting('Scene_Editor_FileDlgPath', filename)
                self.scene.load(filename)

        def doSave(filename):
            ok = self.scene.save(filename)
            if ok and self._scene.file.path is not None \
                and self._scene.file.path == self.scene.file.path:
                # Refresh MH's current scene if it was modified.
                self._scene.load(self._scene.file.path)

        @self.loadButton.mhEvent
        def onClicked(event):
            if self.scene.file.modified:
                G.app.prompt('Confirmation',
                    'Your scene is unsaved. Are you sure you want to close it?',
                    'Close', 'Cancel', doLoad)
            else:
                doLoad()

        @self.saveButton.mhEvent
        def onClicked(event):
            if self.scene.file.path is None:
                self.saveAsButton.callEvent('onClicked', event)
            else:
                doSave(self.scene.file.path)

        @self.closeButton.mhEvent
        def onClicked(event):
            if self.scene.file.modified:
                G.app.prompt('Confirmation',
                    'Your scene is unsaved. Are you sure you want to close it?',
                    'Close', 'Cancel', self.scene.reset)
            else:
                self.scene.reset()

        @self.saveAsButton.mhEvent
        def onClicked(event):
            filename = mh.getSaveFileName(
                G.app.getSetting('Scene_Editor_FileDlgPath'),
                'MakeHuman scene (*.mhscene);;All files (*.*)')
            if filename:
                G.app.setSetting('Scene_Editor_FileDlgPath', filename)
                doSave(filename)

        @self.itemList.mhEvent
        def onClicked(item):
            item.getUserData().showProps()

        @self.addButton.mhEvent
        def onClicked(event):
            self.adder.showProps()

    @property
    def scene(self):
        return G.app.scene

    def readScene(self):
        self.adder.showProps()
        self.itemList.setData([])
        self.itemList.addItem("Environment", data=EnvironmentSceneItem(self))
        for i, light in enumerate(self.scene.lights):
            self.itemList.addItem("Light " + str(i), data=LightSceneItem(self, light, i))
        for item in self.itemList.getItems():
            self.propsBox.addWidget(item.getUserData().widget)

    def updateFileTitle(self, file):
        lbltxt = file.name
        if lbltxt is None:
            lbltxt = '<New scene>'
        if file.modified:
            lbltxt += '*'
        self.fnlbl.setText(lbltxt)

    def onSceneChanged(self, event):
        if not self.isShown():
            return

        self.updateFileTitle(event.file)
        if any(term in event.reasons for term in ("load", "add", "remove")):
            self.readScene()

    def onShow(self, event):
        # Swap to edited scene and store app's scene
        temp = self._scene
        self._scene = G.app.scene
        G.app.scene = temp

        guirender.RenderTaskView.onShow(self, event)

        # Create edited scene if it does not exist
        if G.app.scene is None:
            from scene import Scene
            G.app.scene = Scene()

    def onHide(self, event):
        guirender.RenderTaskView.onHide(self, event)

        # Restore app's scene and store edited scene
        temp = self._scene
        self._scene = G.app.scene
        G.app.scene = temp


class BooleanInput(gui.GroupBox):
    def __init__(self, name, value):
        super(BooleanInput, self).__init__(name)
        self.name = name

        self.widget = gui.CheckBox()
        self.widget.setChecked(value)
        self.addWidget(self.widget, 0, 0)

        @self.widget.mhEvent
        def onClicked(arg=None):
            self.callEvent('onChange', self.getValue())

    def getValue(self):
        return self.widget.selected

    def setValue(self, value):
        self.widget.setChecked(value)


class VectorInput(gui.GroupBox):
    def __init__(self, name, value=[0.0, 0.0, 0.0], isColor=False):
        super(VectorInput, self).__init__(name)
        self.name = name

        self.widgets = []
        for idx, v in enumerate(value):
            w = FloatValue(self, v)
            self.widgets.append(w)
            self.addWidget(w, 0, idx)
        self._value = value

        if isColor:
            self.colorPicker = gui.ColorPickButton(value)

            @self.colorPicker.mhEvent
            def onClicked(color):
                self.setValue(list(color.asTuple()))

            self.addWidget(self.colorPicker, 1, 0)
        else:
            self.colorPicker = None

    def setValue(self, value):
        for idx, w in enumerate(self.widgets):
            w.setValue(value[idx])
        self._value = value
        if self.colorPicker:
            self.colorPicker.color = self.getValue()
        self.callEvent('onChange', self.getValue())

    def getValue(self):
        return self._value

    def onActivate(self, arg=None):
        try:
            self._value = [w.value for w in self.widgets]
            if self.colorPicker:
                self.colorPicker.color = self.getValue()
            self.callEvent('onChange', self.getValue())
        except:
            pass


class NumberValue(gui.TextEdit):
    def __init__(self, parent, value):
        super(NumberValue, self).__init__(str(value), self._validator)
        self.parent = parent

    def sizeHint(self):
        size = self.minimumSizeHint()
        size.width = size.width() * 3
        return size

    def onActivate(self, arg=None):
        try:
            self.parent.callEvent('onActivate', self.value)
        except:
            pass

    def onChange(self, arg=None):
        try:
            self.parent.callEvent('onActivate', self.value)
        except:
            pass

    def setValue(self, value):
        self.setText(str(value))


class FloatValue(NumberValue):
    _validator = gui.floatValidator

    @property
    def value(self):
        return float(self.text)


class IntValue(NumberValue):
    _validator = gui.intValidator

    @property
    def value(self):
        return int(self.text)


def load(app):
    category = app.getCategory('Utilities')
    category.addTask(SceneEditorTaskView(category))


def unload(app):
    pass
