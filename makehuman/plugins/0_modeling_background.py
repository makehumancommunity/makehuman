# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers, Jonas Hauquier, Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO

"""

__docformat__ = 'restructuredtext'

import os

import gui3d
import geometry3d
import mh
import projection
import gui
import filechooser as fc
import log
import language
import texture

# TODO store position and scale in action
class BackgroundAction(gui3d.Action):
    def __init__(self, name, library, side, before, after):
        super(BackgroundAction, self).__init__(name)
        self.side = side
        self.library = library
        self.before = before
        self.after = after

    def do(self):
        self.library.changeBackgroundImage(self.side, self.after)
        return True

    def undo(self):
        self.library.changeBackgroundImage(self.side, self.before)
        return True

class ProjectionAction(gui3d.Action):
    def __init__(self, name, before, after, oldPixmap, newPixmap):
        super(ProjectionAction, self).__init__(name)
        self.before = before
        self.after = after
        self.oldPixmap = oldPixmap
        self.newPixmap = newPixmap

    def do(self):
        self.newPixmap.save(self.after)
        if os.path.join(self.before) == os.path.join(self.after):
            texture.reloadTexture(self.after)
        gui3d.app.selectedHuman.setTexture(self.after)
        return True

    def undo(self):
        if self.oldPixmap:
            self.oldPixmap.save(self.after)
        if os.path.join(self.before) == os.path.join(self.after):
            texture.reloadTexture(self.before)
        gui3d.app.selectedHuman.setTexture(self.before)
        return True

def pointInRect(point, rect):

    if point[0] < rect[0] or point[0] > rect[2] or point[1] < rect[1] or point[1] > rect[3]:
        return False
    else:
        return True

class BackgroundChooser(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Background')

        self.human = gui3d.app.selectedHuman

        self.backgroundsFolder = mh.getPath('backgrounds')
        if not os.path.exists(self.backgroundsFolder):
            os.makedirs(self.backgroundsFolder)

        self.backgroundsFolders = [ mh.getSysDataPath('backgrounds'),
                                    self.backgroundsFolder ]
        self.extensions = ['bmp', 'png', 'tif', 'tiff', 'jpg', 'jpeg']

        self.texture = mh.Texture()

        self.sides = { 'front': [0,0,0],
                       'back': [0,180,0],
                       'left': [0,90,0],
                       'right': [0,-90,0],
                       'top': [90,0,0],
                       'bottom': [-90,0,0],
                       'other': None }

        self.filenames = {}    # Stores (filename, aspect)
        self.transformations = {} # Stores ((posX,posY), scaleY)
        for side in self.sides.keys():
            self.filenames[side] = None
            self.transformations[side] = [(0.0, 0.0), 1.0]

        mesh = geometry3d.RectangleMesh(20, 20, centered=True)
        self.backgroundImage = gui3d.app.addObject(gui3d.Object(mesh, [0, 0, 1], visible=False))
        self.backgroundImage.mesh.setCameraProjection(0)
        self.backgroundImage.mesh.lockRotation = True;
        self.opacity = 40
        mesh.setColor([255, 255, 255, self.opacity*2.55])
        mesh.setPickable(False)
        mesh.setShadeless(True)
        mesh.setDepthless(True)
        mesh.priority = -90

        # Add icon to action toolbar
        self.backgroundImageToggle = gui.Action('background', 'Background', self.toggleBackground, toggle=True)
        gui3d.app.view_toolbar.addAction(self.backgroundImageToggle)
        gui3d.app.actions.background = self.backgroundImageToggle

        #self.filechooser = self.addTopWidget(fc.FileChooser(self.backgroundsFolders, self.extensions, None))
        #self.addLeftWidget(self.filechooser.sortBox)
        self.filechooser = self.addRightWidget(fc.IconListFileChooser(self.backgroundsFolders, self.extensions, None, None, 'Background', noneItem=True))
        self.filechooser.setIconSize(50,50)
        self.filechooser.enableAutoRefresh(False)
        #self.addLeftWidget(self.filechooser.createSortBox())

        self.backgroundBox = self.addLeftWidget(gui.GroupBox('Side'))
        self.bgSettingsBox = self.addLeftWidget(gui.GroupBox('Background settings'))

        self.radioButtonGroup = []
        for side in ['front', 'back', 'left', 'right', 'top', 'bottom', 'other']:
            radioBtn = self.backgroundBox.addWidget(gui.RadioButton(self.radioButtonGroup, label=side.capitalize(), selected=len(self.radioButtonGroup)==0))
            radioBtn.side = side
            @radioBtn.mhEvent
            def onClicked(value):
                side = self.sides[self.getSelectedSideCheckbox()]
                if side:
                    gui3d.app.axisView(side)
                self.refreshFileChooser()

        self.opacitySlider = self.bgSettingsBox.addWidget(gui.Slider(value=self.opacity, min=0,max=100, label = "Opacity: %d%%"))
        self.dragButton = self.bgSettingsBox.addWidget(gui.CheckBox('Move && Resize'))
        self.foregroundTggl = self.bgSettingsBox.addWidget(gui.CheckBox("Show in foreground"))

        @self.opacitySlider.mhEvent
        def onChanging(value):
            self.backgroundImage.mesh.setColor([255, 255, 255, 2.55*value])
        @self.opacitySlider.mhEvent
        def onChange(value):
            self.opacity = value
            self.backgroundImage.mesh.setColor([255, 255, 255, 2.55*value])
        @self.foregroundTggl.mhEvent
        def onClicked(value):
            self.setShowBgInFront(self.foregroundTggl.selected)

        @self.filechooser.mhEvent
        def onFileSelected(filename):
            side = self.getSelectedSideCheckbox()

            if self.filenames[side]:
                oldBg = self.filenames[side][0]
            else:
                oldBg = None
            gui3d.app.do(BackgroundAction("Change background",
                self,
                side,
                oldBg,
                filename))

            mh.redraw()

        @self.backgroundImage.mhEvent
        def onMouseDragged(event):
            if event.button in [mh.Buttons.LEFT_MASK, mh.Buttons.MIDDLE_MASK]:
                dx = float(event.dx)/30.0
                dy = float(-event.dy)/30.0
                self.moveBackground(dx, dy)
            elif event.button == mh.Buttons.RIGHT_MASK:
                scale = self.getBackgroundScale()
                scale += float(event.dy)/100.0

                self.setBackgroundScale(scale)

        @self.dragButton.mhEvent
        def onClicked(event):
            self.backgroundImage.mesh.setPickable(self.dragButton.selected)
            gui3d.app.selectedHuman.mesh.setPickable(not self.dragButton.selected)
            mh.redraw()

    def getSelectedSideCheckbox(self):
        for checkbox in self.radioButtonGroup:
            if checkbox.selected:
                return checkbox.side
        return None

    def setSelectedSideCheckbox(self, side):
        for checkbox in self.radioButtonGroup:
            if checkbox.side == side:
                checkbox.setSelected(True)

    def changeBackgroundImage(self, side, texturePath):
        if not side:
            return

        if texturePath:
            # Determine aspect ratio of texture
            self.texture.loadImage(mh.Image(texturePath))
            aspect = 1.0 * self.texture.width / self.texture.height

            self.filenames[side] = (texturePath, aspect)
        else:
            self.filenames[side] = None

        self.transformations[side] = [(0.0, 0.0), 1.0]

        if side == self.getCurrentSide():
            # Reload current texture
            self.setBackgroundImage(side)

        self.setBackgroundEnabled(self.isBackgroundSet())

    def getCurrentSide(self):
        rot = gui3d.app.modelCamera.getRotation()
        for (side, rotation) in self.sides.items():
            if rot == rotation:
                return side
        # Indicates an arbitrary non-defined view
        return 'other'

    def setBackgroundEnabled(self, enable):
        if enable:
            if self.isBackgroundSet():
                self.setBackgroundImage(self.getCurrentSide())
                self.backgroundImageToggle.setChecked(True)
                mh.redraw()
            else:
                gui3d.app.prompt('Background', 'No background image is set.\nTo show a background, choose an image from the Background tab\nin Settings.', 'Ok', None, None, None, 'backgroundChooseInfo')
        else: # Disable
            self.backgroundImage.hide()
            self.backgroundImageToggle.setChecked(False)
            mh.redraw()

    def setShowBgInFront(self, enabled):
        if enabled:
            self.backgroundImage.mesh.priority = 100
        else:
            self.backgroundImage.mesh.priority = -90
        mh.redraw()

    def isShowBgInFront(self):
        return self.backgroundImage.mesh.priority == 100

    def isBackgroundSet(self):
        for bgFile in self.filenames.values():
            if bgFile:
                return True
        return False

    def isBackgroundShowing(self):
        return self.backgroundImage.isVisible()

    def isBackgroundEnabled(self):
        return self.backgroundImageToggle.isChecked()

    def toggleBackground(self):
        self.setBackgroundEnabled(self.backgroundImageToggle.isChecked())

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)
        text = language.language.getLanguageString(u'Images which are placed in %s will show up here.') % self.backgroundsFolder
        gui3d.app.prompt('Info', text, 'OK', helpId='backgroundHelp')
        gui3d.app.statusPersist(text)
        self.opacitySlider.setValue(self.opacity)
        self.foregroundTggl.setChecked(self.isShowBgInFront())
        self.backgroundImage.mesh.setPickable(self.dragButton.selected)
        self.human.mesh.setPickable(not self.dragButton.selected)
        self.filechooser.refresh()
        self.filechooser.setFocus()
        self.setSelectedSideCheckbox(self.getCurrentSide())
        self.refreshFileChooser()

    def refreshFileChooser(self):
        currentBg = self.filenames[self.getSelectedSideCheckbox()]
        if currentBg:
            currentBg = currentBg[0]
        print 'setting %s' % currentBg
        self.filechooser.selectItem(currentBg)

    def onHide(self, event):

        self.backgroundImage.mesh.setPickable(False)
        self.human.mesh.setPickable(True)
        gui3d.app.statusPersist('')
        gui3d.TaskView.onHide(self, event)

    def onHumanChanging(self, event):
        if event.change == 'reset':
            for side in self.sides.keys():
                self.filenames[side] = None
            self.setBackgroundEnabled(False)

    def setBackgroundImage(self, side):
        if not side:
            self.backgroundImage.hide()
            return

        if self.filenames.get(side):
            (filename, aspect) = self.filenames.get(side)
        else:
            filename = aspect = None
        if filename:
            self.backgroundImage.show()
            self.backgroundImage.setPosition(self.human.getPosition())
            (posX, posY), scale = self.transformations[side]
            self.setBackgroundPosition(posX, posY)
            self.setBackgroundScale(scale)
            self.backgroundImage.mesh.setTexture(filename)
        else:
            self.backgroundImage.hide()
        mh.redraw()

    def onCameraRotated(self, event):
        # TODO when the camera rotates to an angle after pressing a view angle button, this method is called a lot of times repeatedly
        if self.isBackgroundEnabled():
            self.setBackgroundImage(self.getCurrentSide())

    def getCurrentBackground(self):
        if not self.isBackgroundShowing():
            return None
        return self.filenames[self.getCurrentSide()]

    def getBackgroundScale(self):
        if not self.isBackgroundShowing():
            return 0.0
        side = self.getCurrentSide()
        return self.transformations[side][1]

    def moveBackground(self, dx, dy):
        if not self.isBackgroundShowing():
            return
        side = self.getCurrentSide()
        self.backgroundImage.mesh.move(dx, dy)
        self.transformations[side][0] = self.backgroundImage.mesh.getOffset()

    def setBackgroundScale(self, scale):
        if not self.isBackgroundShowing():
            return
        side = self.getCurrentSide()
        scale = abs(float(scale))
        (_, aspect) = self.getCurrentBackground()
        self.backgroundImage.mesh.resize(scale * 20.0 * aspect, scale * 20.0)
        self.transformations[side][1] = scale

    def setBackgroundPosition(self, x, y):
        if not self.isBackgroundShowing():
            return
        side = self.getCurrentSide()
        self.backgroundImage.mesh.setPosition(x, y)
        self.transformations[side][0] = (float(x), float(y))

class TextureProjectionView(gui3d.TaskView) :

    def __init__(self, category, backgroundChooserView):
        self.human = gui3d.app.selectedHuman

        self.backgroundImage = backgroundChooserView.backgroundImage
        self.texture = backgroundChooserView.texture

        self.backgroundChooserView = backgroundChooserView

        gui3d.TaskView.__init__(self, category, 'Projection')

        self.projectionBox = self.addLeftWidget(gui.GroupBox('Projection'))

        self.backgroundBox = self.addLeftWidget(gui.GroupBox('Background settings'))
        self.chooseBGButton = self.backgroundBox.addWidget(gui.Button('Choose background'))

        @self.chooseBGButton.mhEvent
        def onClicked(event):
            mh.changeTask('Settings', 'Background')

        self.projectBackgroundButton = self.projectionBox.addWidget(gui.Button('Project background'))

        @self.projectBackgroundButton.mhEvent
        def onClicked(event):
            self.projectBackground()

        self.projectLightingButton = self.projectionBox.addWidget(gui.Button('Project lighting'))

        @self.projectLightingButton.mhEvent
        def onClicked(event):
            self.projectLighting()

        self.projectUVButton = self.projectionBox.addWidget(gui.Button('Project UV topology'))

        @self.projectUVButton.mhEvent
        def onClicked(event):
            self.projectUV()

        displayBox = self.addRightWidget(gui.GroupBox('Display settings'))
        self.shadelessButton = displayBox.addWidget(gui.CheckBox('Shadeless'))

        @self.shadelessButton.mhEvent
        def onClicked(event):
            gui3d.app.selectedHuman.mesh.setShadeless(1 if self.shadelessButton.selected else 0)

    def onShow(self, event):

        gui3d.TaskView.onShow(self, event)
        self.human.mesh.setShadeless(1 if self.shadelessButton.selected else 0)

        self.oldDiffuseShaderSetting = self.human.material.shaderConfig['diffuse']
        self.human.mesh.configureShading(diffuse = True)
        mh.redraw()

    def onHide(self, event):

        gui3d.TaskView.onHide(self, event)
        self.human.mesh.setShadeless(0)

        self.human.mesh.configureShading(diffuse = self.oldDiffuseShaderSetting)
        mh.redraw()

    def onHumanChanging(self, event):
        pass

    def projectBackground(self):
        if not self.backgroundChooserView.isBackgroundShowing():
            gui3d.app.prompt("Warning", "You need to load a background for the current view before you can project it.", "OK")
            return

        mesh = self.human.getSeedMesh()

        # for all quads, project vertex to screen
        # if one vertex falls in bg rect, project screen quad into uv quad
        # warp image region into texture
        ((x0,y0,z0), (x1,y1,z1)) = self.backgroundImage.mesh.calcBBox()
        camera = mh.cameras[self.backgroundImage.mesh.cameraMode]
        x0, y0, _ = camera.convertToScreen(x0, y0, z0, self.backgroundImage.mesh)
        x1, y1, _ = camera.convertToScreen(x1, y1, z1, self.backgroundImage.mesh)
        leftTop = (x0, y1)
        rightBottom = (x1, y0)

        dstImg = projection.mapImage(self.backgroundImage, mesh, leftTop, rightBottom)
        texPath = mh.getPath('data/skins/projection.png')
        if os.path.isfile(texPath):
            oldImg = mh.Image(texPath)
        else:
            oldImg = None

        gui3d.app.do(ProjectionAction("Change projected background texture",
                self.human.getTexture(),
                texPath,
                oldImg,
                dstImg))
        log.debug("Enabling shadeless rendering on body")
        self.shadelessButton.setChecked(True)
        self.human.mesh.setShadeless(1)
        mh.redraw()

    def projectLighting(self):
        dstImg = projection.mapLighting()
        #dstImg.resize(128, 128)
        texPath = mh.getPath('data/skins/lighting.png')
        if os.path.isfile(texPath):
            oldImg = mh.Image(texPath)
        else:
            oldImg = None

        gui3d.app.do(ProjectionAction("Change projected lighting texture",
                self.human.getTexture(),
                texPath,
                oldImg,
                dstImg))
        log.debug("Enabling shadeless rendering on body")
        self.shadelessButton.setChecked(True)
        self.human.mesh.setShadeless(1)
        mh.redraw()

    def projectUV(self):
        dstImg = projection.mapUV()
        #dstImg.resize(128, 128)
        texPath = mh.getPath('data/skins/uvtopo.png')
        if os.path.isfile(texPath):
            oldImg = mh.Image(texPath)
        else:
            oldImg = None

        gui3d.app.do(ProjectionAction("Change projected UV map texture",
                self.human.getTexture(),
                texPath,
                oldImg,
                dstImg))
        log.debug("Enabling shadeless rendering on body")
        self.shadelessButton.setChecked(True)
        self.human.mesh.setShadeless(1)
        mh.redraw()


# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Settings')
    bgChooser = BackgroundChooser(category)
    bgChooser.sortOrder = 1
    category.addTask(bgChooser)
    category = app.getCategory('Utilities')
    bgSettings = TextureProjectionView(category, bgChooser)
    bgSettings.sortOrder = 1.5
    #category.addTask(bgSettings)

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass

