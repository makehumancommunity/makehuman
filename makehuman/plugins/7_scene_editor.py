#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thanasis Papoutsidakis

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Scene editor plugin.

This editor can create, load, edit and save .mhscene files,
and has tools to alter the scene's characteristics,
like lights and ambience, that are defined in the scene class.

"""

import mh
import gui
import gui3d
import guirender

import os
import scene

import glmodule


class SceneItem(object):
    def __init__(self, sceneview, label = ""):
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
            self.sceneview.readScene()


class EnvironmentSceneItem(SceneItem):
    def __init__(self, sceneview):
        SceneItem.__init__(self, sceneview, "Environment properties")

    def makeProps(self):
        SceneItem.makeProps(self)

        self.colbox = self.widget.addWidget(VectorInput("Ambience", self.sceneview.scene.environment.ambience, True))

        @self.colbox.mhEvent
        def onChange(value):
            self.sceneview.scene.environment.ambience = value
            self.sceneview.updateScene()
            
     
class LightSceneItem(SceneItem):
    def __init__(self, sceneview, light, lid):
        self.lightid = lid
        self.light = light
        SceneItem.__init__(self, sceneview, "Light %s properties" % self.lightid)

    def makeProps(self):
        SceneItem.makeProps(self)
        
        self.posbox = self.widget.addWidget(VectorInput("Position", self.light.position))

        self.focbox = self.widget.addWidget(VectorInput("Focus", self.light.focus))
        
        self.colbox = self.widget.addWidget(VectorInput("Color", self.light.color, True))

        self.specbox = self.widget.addWidget(VectorInput("Specular", self.light.specular, True))

        self.fov = self.widget.addWidget(VectorInput("Spot angle", [self.light.fov]))

        self.att = self.widget.addWidget(VectorInput("Attenuation", [self.light.attenuation]))

        self.soft = self.widget.addWidget(BooleanInput("Soft light", self.light.areaLights > 1))

        self.size = self.widget.addWidget(VectorInput("Softness", [self.light.areaLightSize]))

        self.samples = self.widget.addWidget(VectorInput("Samples", [self.light.areaLights]))

        self.removebtn = self.widget.addWidget(
            gui.Button('Remove light ' + str(self.lightid)))

        @self.posbox.mhEvent
        def onChange(value):
            self.light.position = tuple(value)
            self.sceneview.updateScene()

        @self.focbox.mhEvent
        def onChange(value):
            self.light.focus = tuple(value)

        @self.colbox.mhEvent
        def onChange(value):
            self.light.color = tuple(value)
            self.sceneview.updateScene()

        @self.specbox.mhEvent
        def onChange(value):
            self.light.specular = tuple(value)
            self.sceneview.updateScene()

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
            self.sceneview.readScene()


class SceneEditorTaskView(guirender.RenderTaskView):

    def __init__(self, category):
        guirender.RenderTaskView.__init__(self, category, 'Scene Editor')
        sceneBox = self.addLeftWidget(gui.GroupBox('Scene'))
        self.fnlbl = sceneBox.addWidget(gui.TextView('<New scene>'))
        self.saveButton = sceneBox.addWidget(gui.Button('Save'), 1, 0)
        self.loadButton = sceneBox.addWidget(gui.Button('Load ...'), 1, 1)
        self.saveAsButton = sceneBox.addWidget(gui.Button('Save As...'), 2, 0)
        self.closeButton = sceneBox.addWidget(gui.Button('Close'), 2, 1)

        itemBox = self.addLeftWidget(gui.GroupBox('Items'))
        self.itemList = itemBox.addWidget(gui.ListView())
        self.itemList.setSizePolicy(gui.SizePolicy.Ignored, gui.SizePolicy.Preferred)

        self.propsBox = gui.StackedBox()
        self.addRightWidget(self.propsBox)

        self.addButton = itemBox.addWidget(gui.Button('Add...'))
        self.adder = SceneItemAdder(self)
        self.propsBox.addWidget(self.adder.widget)

        self.items = {}
        self.activeItem = None
        self.scene = scene.Scene()
        self.readScene()

        def doLoad():
            filename = mh.getOpenFileName(mh.getPath("scenes"), 'MakeHuman scene (*.mhscene);;All files (*.*)')
            if filename:
                self.scene.load(filename)
                self.readScene()

        def doSave(filename = None):
            self.scene.save(filename)
            mhscene = gui3d.app.getCategory('Rendering').getTaskByName('Scene').scene
            if os.path.normpath(mhscene.path) == os.path.normpath(self.scene.path):
                mhscene.load(mhscene.path) # Refresh MH's current scene.

        @self.scene.mhEvent
        def onChanged(scene):
            self.updateFileTitle()

        @self.loadButton.mhEvent
        def onClicked(event):
            if self.scene.unsaved:
                gui3d.app.prompt('Confirmation',
                                 'Your scene is unsaved. Are you sure you want to close it?',
                                 'Close','Cancel',doLoad())
            else:
                doLoad()

        @self.saveButton.mhEvent
        def onClicked(event):
            if self.scene.path is None:
                self.saveAsButton.callEvent('onClicked', None)
            else:
                doSave()
            self.updateFileTitle()

        @self.closeButton.mhEvent
        def onClicked(event):
            if self.scene.unsaved:
                gui3d.app.prompt('Confirmation',
                                 'Your scene is unsaved. Are you sure you want to close it?',
                                 'Close','Cancel',self.scene.close())
            else:
                self.scene.close()
            self.readScene()

        @self.saveAsButton.mhEvent
        def onClicked(event):
            filename = mh.getSaveFileName(mh.getPath("scenes"), 'MakeHuman scene (*.mhscene);;All files (*.*)')
            if filename:
                doSave(filename)
            self.updateFileTitle()
                
        @self.itemList.mhEvent
        def onClicked(event):
            self.items[self.itemList.getSelectedItem()].showProps()

        @self.addButton.mhEvent
        def onClicked(event):
            self.adder.showProps()
            
    def readScene(self):
        self.adder.showProps()
        self.items.clear()
        self.items = {'Environment': EnvironmentSceneItem(self)}
        i = 0
        for light in self.scene.lights:
            i += 1
            self.items['Light ' + str(i)] = LightSceneItem(self, light, i)
        for item in self.items.values():
            self.propsBox.addWidget(item.widget)
        self.itemList.setData(self.items.keys()[::-1])
        self.updateFileTitle()

        self.updateScene()

    def updateScene(self):
        glmodule.setSceneLighting(self.scene)

    def updateFileTitle(self):
        if self.scene.path is None:
            lbltxt = '<New scene>'
        else:
            lbltxt = os.path.basename(self.scene.path)
        if self.scene.unsaved:
            lbltxt += '*'
        self.fnlbl.setText(lbltxt)

    def onShow(self, event):
        guirender.RenderTaskView.onShow(self, event)
        
        # Set currently edited scene
        self.updateScene()

    def onHide(self, event):
        # Restore selected scene
        sceneTask = gui3d.app.getTask('Rendering', 'Scene')
        scene = sceneTask.scene
        glmodule.setSceneLighting(scene)

        guirender.RenderTaskView.onHide(self, event)

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
    def __init__(self, name, value = [0.0, 0.0, 0.0], isColor = False):
        super(VectorInput, self).__init__(name)
        self.name = name

        self.widgets = []
        for idx,v in enumerate(value):
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
        for idx,w in enumerate(self.widgets):
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
    taskview = category.addTask(SceneEditorTaskView(category))

def unload(app):
    pass
