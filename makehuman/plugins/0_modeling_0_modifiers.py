#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Generic modifiers
TODO
"""

import gui
import gui3d
import humanmodifier
import modifierslider
from core import G
import log

class GroupBoxRadioButton(gui.RadioButton):
    def __init__(self, task, group, label, groupBox, selected=False):
        super(GroupBoxRadioButton, self).__init__(group, label, selected)
        self.groupBox = groupBox
        self.task = task

    def onClicked(self, event):
        self.task.groupBox.showWidget(self.groupBox)

class ModifierTaskView(gui3d.TaskView):
    _group = None
    _label = None

    def __init__(self, category):
        super(ModifierTaskView, self).__init__(category, self._name, label=self._label)

        def resolveOptionsDict(opts, type = 'simple'):
            # Function to analyze options passed
            # with a dictionary in the features.
            if not 'cam' in opts.keys():
                opts['cam'] = 'noSetCamera'
            if not 'min' in opts.keys():
                if type == 'paired':
                    opts['min'] = -1.0
                else:
                    opts['min'] = 0.0
            if not 'max' in opts.keys():
                opts['max'] = 1.0
            if 'reverse' in opts.keys() and opts['reverse'] == True:
                temp = opts['max']
                opts['max'] = opts['min']
                opts['min'] = temp
            if not 'label' in opts.keys():
                opts['label'] = None

        self.groupBoxes = []
        self.radioButtons = []
        self.sliders = []
        self.modifiers = {}

        self.categoryBox = self.addRightWidget(gui.GroupBox('Category'))
        self.groupBox = self.addLeftWidget(gui.StackedBox())

        for name, base, templates in self._features:
            title = name.capitalize()

            # Create box
            box = self.groupBox.addWidget(gui.GroupBox(title))
            self.groupBoxes.append(box)

            # Create radiobutton
            self.categoryBox.addWidget(GroupBoxRadioButton(self, self.radioButtons, title, box, selected = len(self.radioButtons) == 0))

            # Create sliders
            for index, template in enumerate(templates):
                macro = len(template) == 3
                if macro:
                    tname, tvar, opts = template
                    resolveOptionsDict(opts, 'macro')
                    if tname:
                        groupName = base + "-" + tname
                    else:
                        groupName = base
                    modifier = humanmodifier.MacroModifier(groupName, tvar)
                    modifier.setHuman(G.app.selectedHuman)
                    self.modifiers[tvar] = modifier
                    tpath = '-'.join(template[1:-1])
                    slider = modifierslider.MacroSlider(modifier, opts['label'], ('%s.png' % tpath).lower(),
                                                       opts['cam'], opts['min'], opts['max'])
                else:
                    paired = len(template) == 4
                    if paired:
                        tname, tleft, tright, opts = template
                        resolveOptionsDict(opts, 'paired')
                        left  = '-'.join([base, tname, tleft])
                        right = '-'.join([base, tname, tright])
                    else:
                        tname, opts = template
                        resolveOptionsDict(opts)
                        tleft = None
                        tright = None

                    if opts['label'] is None:
                        tlabel = tname.split('-')
                        if len(tlabel) > 1 and tlabel[0] == base:
                            tlabel = tlabel[1:]
                        opts['label'] = ' '.join([word.capitalize() for word in tlabel])

                    groupName = base
                    name = tname
                    modifier = humanmodifier.UniversalModifier(groupName, name, tleft, tright, centerExt=None)
                    modifier.setHuman(G.app.selectedHuman)

                    tpath = '-'.join(template[0:-1])
                    modifierName = tpath
                    clashIndex = 0
                    while modifierName in self.modifiers:
                        log.debug('modifier clash: %s', modifierName)
                        modifierName = '%s%d' % (tpath, clashIndex)
                        clashIndex += 1

                    self.modifiers[modifierName] = modifier
                    slider = modifierslider.UniversalSlider(modifier, opts['label'], '%s.png' % tpath,
                                                           opts['cam'], opts['min'], opts['max'])

                box.addWidget(slider)
                self.sliders.append(slider)

        self.updateMacro()

        self.groupBox.showWidget(self.groupBoxes[0])

    def getModifiers(self):
        return self.modifiers

    def getSymmetricModifierPairNames(self):
        return [dict(left = name, right = "l-" + name[2:])
                for name in self.modifiers
                if name.startswith("r-")]

    def getSingularModifierNames(self):
        return [name
                for name in self.modifiers
                if name[:2] not in ("r-", "l-")]

    def updateMacro(self):
        for modifier in self.modifiers.itervalues():
            if isinstance(modifier, humanmodifier.MacroModifier):
                modifier.setValue(modifier.getValue())

    def onShow(self, event):
        gui3d.TaskView.onShow(self, event)

        if G.app.settings.get('cameraAutoZoom', True):
            self.setCamera()

        for slider in self.sliders:
            slider.update()

    def onHumanChanged(self, event):
        for slider in self.sliders:
            slider.update()

        if event.change in ('reset', 'load', 'random'):
            self.updateMacro()

    def loadHandler(self, human, values):
        if values[0] == 'status':
            return

        if values[0] == self._group:
            modifier = self.modifiers.get(values[1], None)
            if modifier:
                modifier.setValue(float(values[2]))

    def saveHandler(self, human, file):
        for name, modifier in self.modifiers.iteritems():
            if name is None:
                continue
            value = modifier.getValue()
            if value or isinstance(modifier, humanmodifier.MacroModifier):
                file.write('%s %s %f\n' % (self._group, name, value))

    def setCamera(self):
        pass

class FaceTaskView(ModifierTaskView):
    _name = 'Face'
    _group = 'face'
    _features = [
        ('head shape', 'head', [
            ('head-age', 'less', 'more', {'cam' : 'frontView'}),
            ('head-angle', 'in', 'out', {'cam' : 'rightView'}),
            ('head-oval', {'cam' : 'frontView'}),
            ('head-round', {'cam' : 'frontView'}),
            ('head-rectangular', {'cam' : 'frontView'}),
            ('head-square', {'cam' : 'frontView'}),
            ('head-triangular', {'cam' : 'frontView'}),
            ('head-invertedtriangular', {'cam' : 'frontView'}),
            ('head-diamond', {'cam' : 'frontView'}),
            ]),
        ('head size', 'head', [
            ('head-scale-depth', 'less', 'more', {'cam' : 'rightView'}),
            ('head-scale-horiz', 'less', 'more', {'cam' : 'frontView'}),
            ('head-scale-vert', 'more', 'less', {'cam' : 'frontView'}),
            ('head-trans', 'in', 'out', {'cam' : 'frontView'}),
            ('head-trans', 'down', 'up', {'cam' : 'frontView'}),
            ('head-trans', 'forward', 'backward', {'cam' : 'rightView'}),
            ]),
        ('forehead', 'forehead', [
            ('forehead-trans-depth', 'forward', 'backward', {'cam' : 'rightView'}),
            ('forehead-scale-vert', 'less', 'more', {'cam' : 'rightView'}),
            ('forehead-nubian', 'less', 'more', {'cam' : 'rightView'}),
            ('forehead-temple', 'in', 'out', {'cam' : 'frontView'}),
            ]),
        ('eyebrows', 'eyebrows', [
            ('eyebrows-trans-depth', 'less', 'more', {'cam' : 'rightView'}),
            ('eyebrows-angle', 'up', 'down', {'cam' : 'frontView'}),
            ('eyebrows-trans-vert', 'less', 'more', {'cam' : 'frontView'}),
            ]),
        ('neck', 'neck', [
            ('neck-scale-depth', 'less', 'more', {'cam' : 'rightView'}),
            ('neck-scale-horiz', 'less', 'more', {'cam' : 'frontView'}),
            ('neck-scale-vert', 'more', 'less', {'cam' : 'frontView'}),
            ('neck-trans-horiz', 'in', 'out', {'cam' : 'frontView'}),
            ('neck-trans-vert', 'down', 'up', {'cam' : 'frontView'}),
            ('neck-trans-depth', 'forward', 'backward', {'cam' : 'rightView'}),
            ]),
        ('right eye', 'eyes', [
            ('r-eye-height1', 'min', 'max', {'cam' : 'frontView'}),
            ('r-eye-height2', 'min', 'max', {'cam' : 'frontView'}),
            ('r-eye-height3', 'min', 'max', {'cam' : 'frontView'}),
            ('r-eye-push1', 'in', 'out', {'cam' : 'frontView'}),
            ('r-eye-push2', 'in', 'out', {'cam' : 'frontView'}),
            ('r-eye-move', 'in', 'out', {'cam' : 'frontView'}),
            ('r-eye-move', 'up', 'down', {'cam' : 'frontView'}),
            ('r-eye-size', 'small', 'big', {'cam' : 'frontView'}),
            ('r-eye-corner1', 'up', 'down', {'cam' : 'frontView'}),
            ('r-eye-corner2', 'up', 'down', {'cam' : 'frontView'})
            ]),
        ('left eye', 'eyes', [
            ('l-eye-height1', 'min', 'max', {'cam' : 'frontView'}),
            ('l-eye-height2', 'min', 'max', {'cam' : 'frontView'}),
            ('l-eye-height3', 'min', 'max', {'cam' : 'frontView'}),
            ('l-eye-push1', 'in', 'out', {'cam' : 'frontView'}),
            ('l-eye-push2', 'in', 'out', {'cam' : 'frontView'}),
            ('l-eye-move', 'in', 'out', {'cam' : 'frontView'}),
            ('l-eye-move', 'up', 'down', {'cam' : 'frontView'}),
            ('l-eye-size', 'small', 'big', {'cam' : 'frontView'}),
            ('l-eye-corner1', 'up', 'down', {'cam' : 'frontView'}),
            ('l-eye-corner2', 'up', 'down', {'cam' : 'frontView'}),
            ]),        
        ('nose size', 'nose', [
            ('nose-trans-vert', 'up', 'down', {'cam' : 'frontView'}),
            ('nose-trans-depth', 'forward', 'backward', {'cam' : 'rightView'}),
            ('nose-trans-horiz', 'in', 'out', {'cam' : 'frontView'}),
            ('nose-scale-vert', 'incr', 'decr', {'cam' : 'frontView'}),
            ('nose-scale-horiz', 'incr', 'decr', {'cam' : 'frontView'}),
            ('nose-scale-depth', 'incr', 'decr', {'cam' : 'rightView'}),
            ]),
        ('nose size details', 'nose', [
            ('nose-nostril-width', 'min', 'max', {'cam' : 'frontView'}),
            ('nose-point-width', 'less', 'more', {'cam' : 'frontView'}),
            ('nose-height', 'min', 'max', {'cam' : 'rightView'}),
            ('nose-width1', 'min', 'max', {'cam' : 'frontView'}),
            ('nose-width2', 'min', 'max', {'cam' : 'frontView'}),
            ('nose-width3', 'min', 'max', {'cam' : 'frontView'}),            
            ]),
        ('nose features', 'nose', [
            ('nose-compression', 'compress', 'uncompress', {'cam' : 'rightView'}),
            ('nose-curve', 'convex', 'concave', {'cam' : 'rightView'}),
            ('nose-greek', 'moregreek', 'lessgreek', {'cam' : 'rightView'}),
            ('nose-hump', 'morehump', 'lesshump', {'cam' : 'rightView'}),
            ('nose-volume', 'potato', 'point', {'cam' : 'rightView'}),            
            ('nose-nostrils-angle', 'up', 'down', {'cam' : 'rightView'}),
            ('nose-point', 'up', 'down', {'cam' : 'rightView'}),
            ('nose-septumangle', 'decr', 'incr', {'cam' : 'rightView'}),
            ('nose-flaring', 'decr', 'incr', {'cam' : 'rightView'}),
            ]),        
        ('mouth size', 'mouth', [
            ('mouth-scale-horiz', 'incr', 'decr', {'cam' : 'frontView'}),
            ('mouth-scale-vert', 'incr', 'decr', {'cam' : 'frontView'}),
            ('mouth-scale-depth', 'incr', 'decr', {'cam' : 'rightView'}),
            ('mouth-trans', 'in', 'out', {'cam' : 'frontView'}),
            ('mouth-trans', 'up', 'down', {'cam' : 'frontView'}),
            ('mouth-trans', 'forward', 'backward', {'cam' : 'rightView'}),
            ]),
        ('mouth size details', 'mouth', [
            ('mouth-lowerlip-height', 'min', 'max', {'cam' : 'frontView'}),            
            ('mouth-lowerlip-width', 'min', 'max', {'cam' : 'frontView'}),
            ('mouth-upperlip-height', 'min', 'max', {'cam' : 'frontView'}),
            ('mouth-upperlip-width', 'min', 'max', {'cam' : 'frontView'}),
            ('mouth-cupidsbow-width', 'min', 'max', {'cam' : 'frontView'}),
            ]),
        ('mouth features', 'mouth', [
            ('mouth-lowerlip-ext', 'up', 'down', {'cam' : 'frontView'}),
            ('mouth-angles', 'up', 'down', {'cam' : 'frontView'}),
            ('mouth-lowerlip-middle', 'up', 'down', {'cam' : 'frontView'}),
            ('mouth-lowerlip-volume', 'deflate', 'inflate', {'cam' : 'rightView'}),
            ('mouth-philtrum-volume', 'increase', 'decrease', {'cam' : 'rightView'}),
            ('mouth-upperlip-volume', 'deflate', 'inflate', {'cam' : 'rightView'}),
            ('mouth-upperlip-ext', 'up', 'down', {'cam' : 'frontView'}),
            ('mouth-upperlip-middle', 'up', 'down', {'cam' : 'frontView'}),
            ('mouth-cupidsbow', 'decr', 'incr', {'cam' : 'frontView'}),
            ]),
        ('right ear', 'ears', [
            ('r-ear-trans-depth', 'backward', 'forward', {'cam' : 'rightView'}),
            ('r-ear-size', 'big', 'small', {'cam' : 'rightView'}),
            ('r-ear-trans-vert', 'down', 'up', {'cam' : 'rightView'}),
            ('r-ear-height', 'min', 'max', {'cam' : 'rightView'}),
            ('r-ear-lobe', 'min', 'max', {'cam' : 'rightView'}),
            ('r-ear-shape1', 'pointed', 'triangle', {'cam' : 'rightView'}),
            ('r-ear-rot', 'backward', 'forward', {'cam' : 'rightView'}),
            ('r-ear-shape2', 'square', 'round', {'cam' : 'rightView'}),
            ('r-ear-width', 'max', 'min', {'cam' : 'rightView'}),
            ('r-ear-wing', 'out', 'in', {'cam' : 'frontView'}),
            ('r-ear-flap', 'out', 'in', {'cam' : 'frontView'}),
            ]),
        ('left ear', 'ears', [
            ('l-ear-trans-depth', 'backward', 'forward', {'cam' : 'leftView'}),
            ('l-ear-size', 'big', 'small', {'cam' : 'leftView'}),
            ('l-ear-trans-vert', 'down', 'up', {'cam' : 'leftView'}),
            ('l-ear-height', 'min', 'max', {'cam' : 'leftView'}),
            ('l-ear-lobe', 'min', 'max', {'cam' : 'leftView'}),
            ('l-ear-shape1', 'pointed', 'triangle', {'cam' : 'leftView'}),
            ('l-ear-rot', 'backward', 'forward', {'cam' : 'leftView'}),
            ('l-ear-shape2', 'square', 'round', {'cam' : 'leftView'}),
            ('l-ear-width', 'max', 'min', {'cam' : 'leftView'}),
            ('l-ear-wing', 'out', 'in', {'cam' : 'frontView'}),
            ('l-ear-flap', 'out', 'in', {'cam' : 'frontView'}),
            ]),
        ('chin', 'chin', [
            ('chin-prominent', 'less', 'more', {'cam' : 'rightView'}),
            ('chin-width', 'min', 'max', {'cam' : 'frontView'}),
            ('chin-height', 'min', 'max', {'cam' : 'frontView'}),
            ('chin-bones', 'in', 'out', {'cam' : 'frontView'}),
            ('chin-prognathism', 'less', 'more', {'cam' : 'rightView'}),
            ]),
        ('cheek', 'cheek', [
            ('l-cheek-volume', 'deflate', 'inflate', {'cam' : 'frontView'}),                      
            ('l-cheek-bones', 'in', 'out', {'cam' : 'frontView'}),
            ('l-cheek-inner', 'deflate', 'inflate', {'cam' : 'frontView'}),
            ('l-cheek-trans-vert', 'down', 'up', {'cam' : 'frontView'}),   
            ('r-cheek-volume', 'deflate', 'inflate', {'cam' : 'frontView'}),
            ('r-cheek-bones', 'in', 'out', {'cam' : 'frontView'}),
            ('r-cheek-inner', 'deflate', 'inflate', {'cam' : 'frontView'}),
            ('r-cheek-trans-vert', 'down', 'up', {'cam' : 'frontView'}),
            ]),
        ]

    def setCamera(self):
        G.app.setFaceCamera()

class TorsoTaskView(ModifierTaskView):
    _name = 'Torso'
    _group = 'torso'
    _features = [
        ('Torso', 'torso', [
            ('torso-scale-depth', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ('torso-scale-horiz', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ('torso-scale-vert', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ('torso-trans', 'in', 'out', {'cam' : 'setGlobalCamera'}),
            ('torso-trans', 'down', 'up', {'cam' : 'setGlobalCamera'}),
            ('torso-trans', 'forward', 'backward', {'cam' : 'setGlobalCamera'}),
            ('torso-vshape', 'less', 'more', {'cam' : 'setGlobalCamera'}),
            ]),
        ('Hip', 'hip', [
            ('hip-scale-depth', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ('hip-scale-horiz', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ('hip-scale-vert', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ('hip-trans', 'in', 'out', {'cam' : 'setGlobalCamera'}),
            ('hip-trans', 'down', 'up', {'cam' : 'setGlobalCamera'}),
            ('hip-trans', 'forward', 'backward', {'cam' : 'setGlobalCamera'}),
            ]),
        ('Stomach', 'stomach', [
            ('stomach-tone', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ('stomach-pregnant', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ]),
        ('Buttocks', 'buttocks', [
            ('buttocks-volume', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ]),
        ('Pelvis', 'pelvis', [
            ('pelvis-tone', 'decr', 'incr', {'cam' : 'setGlobalCamera'}),
            ])
        ]

class ArmsLegsTaskView(ModifierTaskView):
    _name = 'Arms and Legs'
    _group = 'armslegs'
    _features = [
        ('right hand', 'armslegs', [   
            ('r-hand-fingers-diameter', 'decr', 'incr', {'cam' : 'setRightHandFrontCamera'}),
            ('r-hand-fingers-length', 'decr', 'incr', {'cam' : 'setRightHandFrontCamera'}), 
            ('r-hand-scale', 'decr', 'incr', {'cam' : 'setRightHandFrontCamera'}),       
            ('r-hand-trans', 'in', 'out', {'cam' : 'setRightHandFrontCamera'}),            
            ]),
        ('left hand', 'armslegs', [  
            ('l-hand-fingers-diameter', 'decr', 'incr', {'cam' : 'setRightHandFrontCamera'}),
            ('l-hand-fingers-length', 'decr', 'incr', {'cam' : 'setRightHandFrontCamera'}), 
            ('l-hand-scale', 'decr', 'incr', {'cam' : 'setRightHandFrontCamera'}),              
            ('l-hand-trans', 'in', 'out', {'cam' : 'setLeftHandFrontCamera'}),            
            ]),
        ('right foot', 'armslegs', [
            ('r-foot-scale', 'decr', 'incr', {'cam' : 'setRightFootRightCamera'}),            
            ('r-foot-trans', 'in', 'out', {'cam' : 'setRightFootFrontCamera'}),
            ('r-foot-trans', 'down', 'up', {'cam' : 'setRightFootFrontCamera'}),
            ('r-foot-trans', 'forward', 'backward', {'cam' : 'setRightFootRightCamera'}),
            ]),
        ('left foot', 'armslegs', [
            ('l-foot-scale', 'decr', 'incr', {'cam' : 'setLeftFootLeftCamera'}),             
            ('l-foot-trans', 'in', 'out', {'cam' : 'setLeftFootFrontCamera'}),
            ('l-foot-trans', 'down', 'up', {'cam' : 'setLeftFootFrontCamera'}),
            ('l-foot-trans', 'forward', 'backward', {'cam' : 'setLeftFootLeftCamera'}),
            ]),
        ('right arm', 'armslegs', [
            ('r-lowerarm-scale-depth', 'decr', 'incr', {'cam' : 'setRightArmTopCamera'}),
            ('r-lowerarm-scale-horiz', 'decr', 'incr', {'cam' : 'setRightArmFrontCamera'}),
            ('r-lowerarm-scale-vert', 'decr', 'incr', {'cam' : 'setRightArmFrontCamera'}),
            ('r-upperarm-scale-depth', 'decr', 'incr', {'cam' : 'setRightArmTopCamera'}),
            ('r-upperarm-scale-horiz', 'decr', 'incr', {'cam' : 'setRightArmFrontCamera'}),
            ('r-upperarm-scale-vert', 'decr', 'incr', {'cam' : 'setRightArmFrontCamera'}),
            ]),
        ('left arm', 'armslegs', [
            ('l-lowerarm-scale-depth', 'decr', 'incr', {'cam' : 'setLeftArmTopCamera'}),
            ('l-lowerarm-scale-horiz', 'decr', 'incr', {'cam' : 'setLeftArmFrontCamera'}),
            ('l-lowerarm-scale-vert', 'decr', 'incr', {'cam' : 'setLeftArmFrontCamera'}),
            ('l-upperarm-scale-depth', 'decr', 'incr', {'cam' : 'setLeftArmTopCamera'}),
            ('l-upperarm-scale-horiz', 'decr', 'incr', {'cam' : 'setLeftArmFrontCamera'}),
            ('l-upperarm-scale-vert', 'decr', 'incr', {'cam' : 'setLeftArmFrontCamera'}),
            ]),  
        ('right leg', 'armslegs', [
            ('r-leg-genu', 'varun', 'valgus', {'cam' : 'setRightLegRightCamera'}),
            ('r-lowerleg-scale-depth', 'decr', 'incr', {'cam' : 'setRightLegRightCamera'}),
            ('r-lowerleg-scale-horiz', 'decr', 'incr', {'cam' : 'setRightLegFrontCamera'}),
            ('r-lowerleg-scale-vert', 'decr', 'incr', {'cam' : 'setRightLegFrontCamera'}),            
            ('r-upperleg-scale-depth', 'decr', 'incr', {'cam' : 'setRightLegRightCamera'}),
            ('r-upperleg-scale-horiz', 'decr', 'incr', {'cam' : 'setRightLegFrontCamera'}),
            ('r-upperleg-scale-vert', 'decr', 'incr', {'cam' : 'setRightLegFrontCamera'}),            
            ]),      
        ('left leg', 'armslegs', [
            ('l-leg-genu', 'varun', 'valgus', {'cam' : 'setLeftLegLeftCamera'}),
            ('l-lowerleg-scale-depth', 'decr', 'incr', {'cam' : 'setLeftLegLeftCamera'}),
            ('l-lowerleg-scale-horiz', 'decr', 'incr', {'cam' : 'setLeftLegFrontCamera'}),
            ('l-lowerleg-scale-vert', 'decr', 'incr', {'cam' : 'setLeftLegFrontCamera'}),            
            ('l-upperleg-scale-depth', 'decr', 'incr', {'cam' : 'setLeftLegLeftCamera'}),
            ('l-upperleg-scale-horiz', 'decr', 'incr', {'cam' : 'setLeftLegFrontCamera'}),
            ('l-upperleg-scale-vert', 'decr', 'incr', {'cam' : 'setLeftLegFrontCamera'}),            
            ])       
        ]

class GenderTaskView(ModifierTaskView):
    _name = 'Gender'
    _group = 'gendered'
    _features = [
        ('Breast', 'breast', [
            (None, 'BreastSize', {'label' : 'Breast size'}),
            (None, 'BreastFirmness', {'label' : 'Breast firmness'}),
            ('breast-trans-vert', 'down', 'up', {'label':'Vertical position'}),
            ('breast-dist', 'min', 'max', {'label':'Horizontal distance'}),
            ('breast-point', 'min', 'max', {'label':'Pointiness'}),
            ('breast-volume-vert', 'up', 'down', {'label':'Volume'}),
            ]),
        ('Genitals', 'genitals', [
            ('penis-length', 'min', 'max', {}),
            ('penis-circ', 'min', 'max', {}),
            ('penis-testicles', 'min', 'max', {}),
            ('penis-bulgeeffect', 'one', 'two', {}),
            ]),
        ]

class MacroTaskView(ModifierTaskView):
    _name = 'Macro modelling'
    _group = 'macro'
    _label = 'Main'

    _features = [
        ('Macro', 'macrodetails', [
            (None, 'Gender', {'label' : 'Gender'}),
            (None, 'Age', {'label' : 'Age'}),
            ('universal', 'Muscle', {'label' : 'Muscle'}),
            ('universal', 'Weight', {'label' : 'Weight'}),
            ('height', 'Height', {'label' : 'Height'}),
            ('proportions', 'BodyProportions', {'label' : 'Proportions'}),
            (None, 'African', {'label' : 'African'}),
            (None, 'Asian', {'label' : 'Asian'}),
            (None, 'Caucasian', {'label' : 'Caucasian'}),
            ]),
        ]

    def __init__(self, category):
        super(MacroTaskView, self).__init__(category)
        for race, modifier, slider in self.raceSliders():
            slider.setValue(1.0/3)
            modifier._defaultValue = 1.0/3

    def raceSliders(self):
        # TODO refactor using human.getModifiers()
        for slider in self.sliders:
            modifier = slider.modifier
            if not isinstance(modifier, humanmodifier.MacroModifier):
                continue
            variable = modifier.variable
            if variable in ('African', 'Asian', 'Caucasian'):
                yield (variable, modifier, slider)

    def syncStatus(self):
        human = G.app.selectedHuman

        if human.getGender() == 0.0:
            gender = G.app.getLanguageString('female')
        elif human.getGender() == 1.0:
            gender = G.app.getLanguageString('male')
        elif abs(human.getGender() - 0.5) < 0.01:
            gender = G.app.getLanguageString('neutral')
        else:
            gender = G.app.getLanguageString('%.2f%% female, %.2f%% male') % ((1.0 - human.getGender()) * 100, human.getGender() * 100)

        age = human.getAgeYears()
        muscle = (human.getMuscle() * 100.0)
        weight = (50 + (150 - 50) * human.getWeight())
        height = human.getHeightCm()
        if G.app.settings['units'] == 'metric':
            units = 'cm'
        else:
            units = 'in'
            height *= 0.393700787

        self.setStatus('Gender: %s, Age: %d, Muscle: %.2f%%, Weight: %.2f%%, Height: %.2f %s', gender, age, muscle, weight, height, units)

    def syncRaceSliders(self, event):
        human = event.human
        for race, modifier, slider in self.raceSliders():
            if slider.slider.isSliderDown():
                # Do not update slider when it is being clicked or dragged
                continue
            slider.setValue(1.0/3)
            value = modifier.getValue()
            modifier.setValue(value)
            slider.setValue(value)

    def setStatus(self, format, *args):
        G.app.statusPersist(format, *args)

    def onShow(self, event):
        self.syncStatus()
        super(MacroTaskView, self).onShow(event)

    def onHide(self, event):
        self.setStatus('')
        super(MacroTaskView, self).onHide(event)

    def onHumanChaging(self, event):
        super(MacroTaskView, self).onHumanChanging(event)
        if event.change in ('caucasian', 'asian', 'african'):
            self.syncRaceSliders(event)

    def onHumanChanged(self, event):
        super(MacroTaskView, self).onHumanChanged(event)
        if self.isVisible():
            self.syncStatus()
        if event.change in ('caucasian', 'asian', 'african'):
            self.syncRaceSliders(event)

def load(app):
    category = app.getCategory('Modelling')

    G.app.noSetCamera = (lambda: None)

    for type in [MacroTaskView, GenderTaskView, FaceTaskView, TorsoTaskView, ArmsLegsTaskView]:
        taskview = category.addTask(type(category))
        if taskview._group is not None:
            app.addLoadHandler(taskview._group, taskview.loadHandler)
            app.addSaveHandler(taskview.saveHandler)

def unload(app):
    pass
