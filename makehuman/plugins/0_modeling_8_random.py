#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Manuel Bastioni, Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

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

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import random
import gui3d
import events3d
import gui

class RandomTaskView(gui3d.TaskView):

    def __init__(self, category):
        gui3d.TaskView.__init__(self, category, 'Random')
        
        toolbox = self.addLeftWidget(gui.SliderBox('Tools'))
        self.macro = toolbox.addWidget(gui.CheckBox("Macro", True))
        self.height = toolbox.addWidget(gui.CheckBox("Height"))
        self.face = toolbox.addWidget(gui.CheckBox("Face"))
        self.symmetry = toolbox.addWidget(gui.Slider(value=-1.0, min=-1.0, max=1.0, label="Symmetry"))
        self.amount = toolbox.addWidget(gui.Slider(value=0.5, label="Amount"))
        self.create = toolbox.addWidget(gui.Button("Replace current"))
        self.modify = toolbox.addWidget(gui.Button("Adjust current"))

        self.lastRandoms = {}
        
        @self.create.mhEvent
        def onClicked(event):
            
            #human = gui3d.app.selectedHuman
            # human.resetMeshValues()
            self.lastRandoms = {}
            
            if self.macro.selected:
                self.storeLastRandom('gender', 0.5, random.random()-0.5)
                self.storeLastRandom('age', 0.5, random.random()-0.5)
                self.storeLastRandom('muscle', 0.5, random.random()-0.5)
                self.storeLastRandom('weight', 0.5, random.random()-0.5)
                
            if self.height.selected:
                self.storeLastRandom( 'height', 0, random.random()*2-1 )

            if self.face.selected:
                category = gui3d.app.getCategory('Modelling')
                taskview = category.getTaskByName('Face')
                modifiers = taskview.getModifiers()
                
                symmetricModifiers = taskview.getSymmetricModifierPairNames()
                for pair in symmetricModifiers:
                    #print "symmetric: "+pair['left']+' and '+pair['right']
                    leftValue = random.gauss( 0, 0.5 ) 
                    rightValue = random.gauss(0, 0.5 )
                    # store randoms for later
                    self.storeLastRandom(pair['left'], 0, leftValue)
                    self.storeLastRandom(pair['right'], 0, rightValue)

                singularModifiers = taskview.getSingularModifierNames()                
                for modName in singularModifiers:
                    #print "singular: "+modName
                    # get random gaussian
                    value = random.gauss( 0, 0.5 ) 
                    # non-asymmetric modifiers should only go 0..1
                    m = modifiers[modName]
                    if m.clampValue(-1.0) >= 0:
                        value = abs(value)
                    # store for later
                    self.storeLastRandom(modName, 0, value)

            self.setModifiers()
            
        @self.modify.mhEvent
        def onClicked(event):
            human = gui3d.app.selectedHuman
            
            if self.macro.selected:
                self.storeLastRandom( 'gender', human.getGender(), random.random()-0.5 )
                self.storeLastRandom( 'age', human.getAge(), random.random()-0.5 )
                self.storeLastRandom( 'weight', human.getWeight(), random.random()-0.5 )
                self.storeLastRandom( 'muscle', human.getMuscle(), random.random()-0.5 )
                
            if self.height.selected:
                self.storeLastRandom( 'height', human.getHeight(), random.random()-0.5)
            
            if self.face.selected:
                category = gui3d.app.getCategory('Modelling')
                taskview = category.getTaskByName('Face')
                modifiers = taskview.getModifiers()
                
                symmetricModifiers = taskview.getSymmetricModifierPairNames()
                for pair in symmetricModifiers:
                    #print "symmetric: "+pair['left']+' and '+pair['right']
                    leftValue = random.gauss( 0, 0.5 ) 
                    rightValue = random.gauss( 0, 0.5 ) 
                    # store randoms for later
                    self.storeLastRandom(pair['left'], modifiers[pair['left']].getValue(human), leftValue)
                    self.storeLastRandom(pair['right'], modifiers[pair['right']].getValue(human), rightValue)

                singularModifiers = taskview.getSingularModifierNames()                
                for modName in singularModifiers:
                    #print "singular: "+modName
                    # get random gaussian
                    value = random.gauss( 0, 0.5 ) 
                    # non-asymmetric modifiers should only go 0..1
                    m = modifiers[modName]
                    if m.clampValue(-1.0) >= 0:
                        value = abs(value)
                    # store for later
                    self.storeLastRandom(modName, modifiers[modName].getValue(human), value)
    
            self.setModifiers()

        @self.amount.mhEvent
        def onChange(value):
            self.setModifiers()

        @self.symmetry.mhEvent
        def onChange(value):
            self.setModifiers()

    def setModifiers(self):

        human = gui3d.app.selectedHuman
        #sliderMul = self.amount.getValue()

        if self.macro.selected:
            human.setGender( self.getRandom('gender', 0, 1 ))
            human.setAge( self.getRandom('age', 0, 1 ))
            human.setWeight( self.getRandom('weight', 0, 1 ))
            human.setMuscle( self.getRandom('muscle', 0, 1 ))

        if self.height.selected:
            human.setHeight( self.getRandom('height', -1, 1 ))

        if self.face.selected:
            category = gui3d.app.getCategory('Modelling')
            taskview = category.getTaskByName('Face')
            modifiers = taskview.getModifiers()
            symmetricModifiers = taskview.getSymmetricModifierPairNames()
            symFactor = self.symmetry.getValue()
            for pair in symmetricModifiers:
                #print "applying "+pair['left']+" and "+pair['right']
                leftValue = self.getRandom(pair['left'])
                rightValue = self.getRandom(pair['right'])
                # handle symmetry
                # -1 = left value only
                # 0 = no symmetry
                # 1 = right value only
                if symFactor < 0:
                    # hold the right value constant, adjust the left value towards its target
                    rightValue = leftValue*-symFactor + rightValue*(1.0+symFactor)
                else:
                    # hold the right value constant, adjust the left value towards its target
                    leftValue = rightValue*symFactor + leftValue*(1.0-symFactor)
                # apply
                modifiers[pair['left']].setValue(human, leftValue)
                modifiers[pair['right']].setValue(human, rightValue)

            singularModifiers = taskview.getSingularModifierNames()
            for modName in singularModifiers:
                #print "applying "+modName
                modifiers[modName].setValue(human, self.getRandom(modName) )

        human.callEvent('onChanged', events3d.HumanEvent(human, 'random'))
        human.applyAllTargets(gui3d.app.progress)
        
    # get the stored random value for the given modifierName, applying amount slider
    def getRandom( self, modifierName, minVal=-1, maxVal=1 ):
        if modifierName in self.lastRandoms:
            newVal = self.lastRandoms[modifierName]['base'] + self.lastRandoms[modifierName]['value']*self.amount.getValue()
            newVal = min(maxVal,max(minVal,newVal))
            return newVal
        else:
            return 0


    def storeLastRandom( self, modifierName, baseValue, randOffset ):
        self.lastRandoms[modifierName] = { 'base':baseValue, 'value':randOffset };

def load(app):
    category = app.getCategory('Modelling')
    taskview = category.addTask(RandomTaskView(category))

def unload(app):
    pass


