#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gui3d

mhapi = gui3d.app.mhapi

class RandomizeAction(gui3d.Action):
    def __init__(self, human, before, after):
        super(RandomizeAction, self).__init__("Randomize")
        self.human = human
        self.before = before
        self.after = after

    def do(self):
        self._assignModifierValues(self.after)
        return True

    def undo(self):
        self._assignModifierValues(self.before)
        return True

    def _assignModifierValues(self, valuesDict):
        _tmp = self.human.symmetryModeEnabled
        self.human.symmetryModeEnabled = False
        for mName, val in list(valuesDict.items()):
            try:
                self.human.getModifier(mName).setValue(val)
            except:
                pass
        self.human.applyAllTargets()
        self.human.symmetryModeEnabled = _tmp