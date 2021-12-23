#!/usr/bin/python3
# -*- coding: utf-8 -*-

from .abstractop import AbstractOp

class SocketModifierOps(AbstractOp):

    def __init__(self, sockettaskview):
        super().__init__(sockettaskview)
        self.functions["applyModifier"] = self.applyModifier
        self.functions["getAppliedTargets"] = self.getAppliedTargets
        self.functions["getAvailableModifierNames"] = self.getAvailableModifierNames

    def getAvailableModifierNames(self,conn,jsonCall):
        jsonCall.data = self.api.modifiers.getAvailableModifierNames()

    def getAppliedTargets(self,conn,jsonCall):
        jsonCall.data = self.api.modifiers.getAppliedTargets()

    def applyModifier(self,conn,jsonCall):
        modifierName = jsonCall.getParam("modifier")
        power = float(jsonCall.getParam("power"))
        modifier = self.api.internals.getHuman().getModifier(modifierName)

        if not modifier:
            jsonCall.setError("No such modifier")
            return

        self.api.modifiers.applyModifier(modifierName,power,True)
        jsonCall.setData("OK")



