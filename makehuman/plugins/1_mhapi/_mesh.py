#!/usr/bin/python

from .namespace import NameSpace

class Mesh(NameSpace):
    """This namespace wraps call which works directly on mesh vertices, edges and faces."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()

    def getVertexCoordinates(self):
        """Return an array with the current position of vertices"""
        self.trace()
        human = self.api.internals.getHuman()
        return human.mesh.coord

    def getAllProxies(self, includeBodyProxy=False):
        human = self.api.internals.getHuman()
        return human.getProxies(includeBodyProxy)

    def getCurrentProxy(self):
        return self.api.internals.getHuman().proxy

    def getCurrentHair(self):
        return self.api.internals.getHuman().hairProxy

    def getCurrentEyes(self):
        return self.api.internals.getHuman().eyesProxy

    def getCurrentEyebrows(self):
        return self.api.internals.getHuman().eyebrowsProxy

    def getCurrentEyelashes(self):
        return self.api.internals.getHuman().eyelashesProxy

    def getCurrentTeeth(self):
        return self.api.internals.getHuman().teethProxy

    def getCurrentTongue(self):
        return self.api.internals.getHuman().tongueProxy

    def getClothes(self):
        human = self.api.internals.getHuman()
        return list(human._clothesProxies.values())

    def getFaceGroupFaceIndexes(self):
        faceGroups = []
        faceGroups.append({ "name": "body", "fgStartStops": [[0, 13378]]} )
        faceGroups.append({ "name": "helper-genital", "fgStartStops": [[17793, 17975]]} )
        faceGroups.append({ "name": "helper-hair", "fgStartStops": [[17455, 17653]]} )
        faceGroups.append({ "name": "helper-l-eye", "fgStartStops": [[17653, 17723]]} )
        faceGroups.append({ "name": "helper-l-eyelashes-1", "fgStartStops": [[18073, 18074], [18075, 18077], [18079, 18081], [18084, 18086], [18090, 18091], [18093, 18094], [18095, 18097], [18118, 18140], [18152, 18163]]} )
        faceGroups.append({ "name": "helper-l-eyelashes-2", "fgStartStops": [[18071, 18073], [18074, 18075], [18077, 18079], [18081, 18084], [18086, 18090], [18091, 18093], [18094, 18095], [18097, 18118], [18140, 18152]]} )
        faceGroups.append({ "name": "helper-lower-teeth", "fgStartStops": [[18023, 18071]]} )
        faceGroups.append({ "name": "helper-r-eye", "fgStartStops": [[17723, 17793]]} )
        faceGroups.append({ "name": "helper-r-eyelashes-1", "fgStartStops": [[18165, 18166], [18167, 18169], [18171, 18173], [18176, 18178], [18182, 18183], [18185, 18186], [18187, 18189], [18210, 18232], [18244, 18255]]} )
        faceGroups.append({ "name": "helper-r-eyelashes-2", "fgStartStops": [[18163, 18165], [18166, 18167], [18169, 18171], [18173, 18176], [18178, 18182], [18183, 18185], [18186, 18187], [18189, 18210], [18232, 18244]]} )
        faceGroups.append({ "name": "helper-skirt", "fgStartStops": [[16771, 17455]]} )
        faceGroups.append({ "name": "helper-tights", "fgStartStops": [[13378, 16027], [18479, 18480]]} )
        faceGroups.append({ "name": "helper-tongue", "fgStartStops": [[18255, 18479]]} )
        faceGroups.append({ "name": "helper-upper-teeth", "fgStartStops": [[17975, 18023]]} )
        faceGroups.append({ "name": "joint-ground", "fgStartStops": [[18480, 18486]]} )
        faceGroups.append({ "name": "joint-head-2", "fgStartStops": [[16747, 16753]]} )
        faceGroups.append({ "name": "joint-head", "fgStartStops": [[16375, 16381]]} )
        faceGroups.append({ "name": "joint-jaw", "fgStartStops": [[16729, 16735]]} )
        faceGroups.append({ "name": "joint-l-ankle", "fgStartStops": [[16195, 16201]]} )
        faceGroups.append({ "name": "joint-l-clavicle", "fgStartStops": [[16363, 16369]]} )
        faceGroups.append({ "name": "joint-l-elbow", "fgStartStops": [[16351, 16357]]} )
        faceGroups.append({ "name": "joint-l-eye", "fgStartStops": [[16027, 16033]]} )
        faceGroups.append({ "name": "joint-l-eye-target", "fgStartStops": [[16387, 16393]]} )
        faceGroups.append({ "name": "joint-l-finger-1-1", "fgStartStops": [[16327, 16333]]} )
        faceGroups.append({ "name": "joint-l-finger-1-2", "fgStartStops": [[16321, 16327]]} )
        faceGroups.append({ "name": "joint-l-finger-1-3", "fgStartStops": [[16315, 16321]]} )
        faceGroups.append({ "name": "joint-l-finger-1-4", "fgStartStops": [[16309, 16315]]} )
        faceGroups.append({ "name": "joint-l-finger-2-1", "fgStartStops": [[16303, 16309]]} )
        faceGroups.append({ "name": "joint-l-finger-2-2", "fgStartStops": [[16261, 16267]]} )
        faceGroups.append({ "name": "joint-l-finger-2-3", "fgStartStops": [[16255, 16261]]} )
        faceGroups.append({ "name": "joint-l-finger-2-4", "fgStartStops": [[16213, 16219]]} )
        faceGroups.append({ "name": "joint-l-finger-3-1", "fgStartStops": [[16297, 16303]]} )
        faceGroups.append({ "name": "joint-l-finger-3-2", "fgStartStops": [[16267, 16273]]} )
        faceGroups.append({ "name": "joint-l-finger-3-3", "fgStartStops": [[16249, 16255]]} )
        faceGroups.append({ "name": "joint-l-finger-3-4", "fgStartStops": [[16219, 16225]]} )
        faceGroups.append({ "name": "joint-l-finger-4-1", "fgStartStops": [[16291, 16297]]} )
        faceGroups.append({ "name": "joint-l-finger-4-2", "fgStartStops": [[16273, 16279]]} )
        faceGroups.append({ "name": "joint-l-finger-4-3", "fgStartStops": [[16243, 16249]]} )
        faceGroups.append({ "name": "joint-l-finger-4-4", "fgStartStops": [[16225, 16231]]} )
        faceGroups.append({ "name": "joint-l-finger-5-1", "fgStartStops": [[16285, 16291]]} )
        faceGroups.append({ "name": "joint-l-finger-5-2", "fgStartStops": [[16279, 16285]]} )
        faceGroups.append({ "name": "joint-l-finger-5-3", "fgStartStops": [[16237, 16243]]} )
        faceGroups.append({ "name": "joint-l-finger-5-4", "fgStartStops": [[16231, 16237]]} )
        faceGroups.append({ "name": "joint-l-foot-1", "fgStartStops": [[16075, 16081]]} )
        faceGroups.append({ "name": "joint-l-foot-2", "fgStartStops": [[16069, 16075]]} )
        faceGroups.append({ "name": "joint-l-hand-2", "fgStartStops": [[16339, 16345]]} )
        faceGroups.append({ "name": "joint-l-hand-3", "fgStartStops": [[16333, 16339]]} )
        faceGroups.append({ "name": "joint-l-hand", "fgStartStops": [[16345, 16351]]} )
        faceGroups.append({ "name": "joint-l-knee", "fgStartStops": [[16201, 16207]]} )
        faceGroups.append({ "name": "joint-l-lowerlid", "fgStartStops": [[16381, 16387]]} )
        faceGroups.append({ "name": "joint-l-scapula", "fgStartStops": [[16369, 16375]]} )
        faceGroups.append({ "name": "joint-l-shoulder", "fgStartStops": [[16357, 16363]]} )
        faceGroups.append({ "name": "joint-l-toe-1-1", "fgStartStops": [[16189, 16195]]} )
        faceGroups.append({ "name": "joint-l-toe-1-2", "fgStartStops": [[16183, 16189]]} )
        faceGroups.append({ "name": "joint-l-toe-1-3", "fgStartStops": [[16177, 16183]]} )
        faceGroups.append({ "name": "joint-l-toe-2-1", "fgStartStops": [[16171, 16177]]} )
        faceGroups.append({ "name": "joint-l-toe-2-2", "fgStartStops": [[16129, 16135]]} )
        faceGroups.append({ "name": "joint-l-toe-2-3", "fgStartStops": [[16123, 16129]]} )
        faceGroups.append({ "name": "joint-l-toe-2-4", "fgStartStops": [[16117, 16123]]} )
        faceGroups.append({ "name": "joint-l-toe-3-1", "fgStartStops": [[16165, 16171]]} )
        faceGroups.append({ "name": "joint-l-toe-3-2", "fgStartStops": [[16135, 16141]]} )
        faceGroups.append({ "name": "joint-l-toe-3-3", "fgStartStops": [[16105, 16111]]} )
        faceGroups.append({ "name": "joint-l-toe-3-4", "fgStartStops": [[16111, 16117]]} )
        faceGroups.append({ "name": "joint-l-toe-4-1", "fgStartStops": [[16159, 16165]]} )
        faceGroups.append({ "name": "joint-l-toe-4-2", "fgStartStops": [[16141, 16147]]} )
        faceGroups.append({ "name": "joint-l-toe-4-3", "fgStartStops": [[16093, 16099]]} )
        faceGroups.append({ "name": "joint-l-toe-4-4", "fgStartStops": [[16099, 16105]]} )
        faceGroups.append({ "name": "joint-l-toe-5-1", "fgStartStops": [[16153, 16159]]} )
        faceGroups.append({ "name": "joint-l-toe-5-2", "fgStartStops": [[16147, 16153]]} )
        faceGroups.append({ "name": "joint-l-toe-5-3", "fgStartStops": [[16081, 16087]]} )
        faceGroups.append({ "name": "joint-l-toe-5-4", "fgStartStops": [[16087, 16093]]} )
        faceGroups.append({ "name": "joint-l-upper-leg", "fgStartStops": [[16207, 16213]]} )
        faceGroups.append({ "name": "joint-l-upperlid", "fgStartStops": [[16393, 16399]]} )
        faceGroups.append({ "name": "joint-mouth", "fgStartStops": [[16765, 16771]]} )
        faceGroups.append({ "name": "joint-neck", "fgStartStops": [[16723, 16729]]} )
        faceGroups.append({ "name": "joint-pelvis", "fgStartStops": [[16039, 16045]]} )
        faceGroups.append({ "name": "joint-r-ankle", "fgStartStops": [[16525, 16531]]} )
        faceGroups.append({ "name": "joint-r-clavicle", "fgStartStops": [[16693, 16699]]} )
        faceGroups.append({ "name": "joint-r-elbow", "fgStartStops": [[16681, 16687]]} )
        faceGroups.append({ "name": "joint-r-eye", "fgStartStops": [[16033, 16039]]} )
        faceGroups.append({ "name": "joint-r-eye-target", "fgStartStops": [[16711, 16717]]} )
        faceGroups.append({ "name": "joint-r-finger-1-1", "fgStartStops": [[16657, 16663]]} )
        faceGroups.append({ "name": "joint-r-finger-1-2", "fgStartStops": [[16651, 16657]]} )
        faceGroups.append({ "name": "joint-r-finger-1-3", "fgStartStops": [[16645, 16651]]} )
        faceGroups.append({ "name": "joint-r-finger-1-4", "fgStartStops": [[16639, 16645]]} )
        faceGroups.append({ "name": "joint-r-finger-2-1", "fgStartStops": [[16633, 16639]]} )
        faceGroups.append({ "name": "joint-r-finger-2-2", "fgStartStops": [[16591, 16597]]} )
        faceGroups.append({ "name": "joint-r-finger-2-3", "fgStartStops": [[16585, 16591]]} )
        faceGroups.append({ "name": "joint-r-finger-2-4", "fgStartStops": [[16543, 16549]]} )
        faceGroups.append({ "name": "joint-r-finger-3-1", "fgStartStops": [[16627, 16633]]} )
        faceGroups.append({ "name": "joint-r-finger-3-2", "fgStartStops": [[16597, 16603]]} )
        faceGroups.append({ "name": "joint-r-finger-3-3", "fgStartStops": [[16579, 16585]]} )
        faceGroups.append({ "name": "joint-r-finger-3-4", "fgStartStops": [[16549, 16555]]} )
        faceGroups.append({ "name": "joint-r-finger-4-1", "fgStartStops": [[16621, 16627]]} )
        faceGroups.append({ "name": "joint-r-finger-4-2", "fgStartStops": [[16603, 16609]]} )
        faceGroups.append({ "name": "joint-r-finger-4-3", "fgStartStops": [[16573, 16579]]} )
        faceGroups.append({ "name": "joint-r-finger-4-4", "fgStartStops": [[16555, 16561]]} )
        faceGroups.append({ "name": "joint-r-finger-5-1", "fgStartStops": [[16615, 16621]]} )
        faceGroups.append({ "name": "joint-r-finger-5-2", "fgStartStops": [[16609, 16615]]} )
        faceGroups.append({ "name": "joint-r-finger-5-3", "fgStartStops": [[16567, 16573]]} )
        faceGroups.append({ "name": "joint-r-finger-5-4", "fgStartStops": [[16561, 16567]]} )
        faceGroups.append({ "name": "joint-r-foot-1", "fgStartStops": [[16405, 16411]]} )
        faceGroups.append({ "name": "joint-r-foot-2", "fgStartStops": [[16399, 16405]]} )
        faceGroups.append({ "name": "joint-r-hand-2", "fgStartStops": [[16669, 16675]]} )
        faceGroups.append({ "name": "joint-r-hand-3", "fgStartStops": [[16663, 16669]]} )
        faceGroups.append({ "name": "joint-r-hand", "fgStartStops": [[16675, 16681]]} )
        faceGroups.append({ "name": "joint-r-knee", "fgStartStops": [[16531, 16537]]} )
        faceGroups.append({ "name": "joint-r-lowerlid", "fgStartStops": [[16705, 16711]]} )
        faceGroups.append({ "name": "joint-r-scapula", "fgStartStops": [[16699, 16705]]} )
        faceGroups.append({ "name": "joint-r-shoulder", "fgStartStops": [[16687, 16693]]} )
        faceGroups.append({ "name": "joint-r-toe-1-1", "fgStartStops": [[16519, 16525]]} )
        faceGroups.append({ "name": "joint-r-toe-1-2", "fgStartStops": [[16513, 16519]]} )
        faceGroups.append({ "name": "joint-r-toe-1-3", "fgStartStops": [[16507, 16513]]} )
        faceGroups.append({ "name": "joint-r-toe-2-1", "fgStartStops": [[16501, 16507]]} )
        faceGroups.append({ "name": "joint-r-toe-2-2", "fgStartStops": [[16459, 16465]]} )
        faceGroups.append({ "name": "joint-r-toe-2-3", "fgStartStops": [[16453, 16459]]} )
        faceGroups.append({ "name": "joint-r-toe-2-4", "fgStartStops": [[16447, 16453]]} )
        faceGroups.append({ "name": "joint-r-toe-3-1", "fgStartStops": [[16495, 16501]]} )
        faceGroups.append({ "name": "joint-r-toe-3-2", "fgStartStops": [[16465, 16471]]} )
        faceGroups.append({ "name": "joint-r-toe-3-3", "fgStartStops": [[16435, 16441]]} )
        faceGroups.append({ "name": "joint-r-toe-3-4", "fgStartStops": [[16441, 16447]]} )
        faceGroups.append({ "name": "joint-r-toe-4-1", "fgStartStops": [[16489, 16495]]} )
        faceGroups.append({ "name": "joint-r-toe-4-2", "fgStartStops": [[16471, 16477]]} )
        faceGroups.append({ "name": "joint-r-toe-4-3", "fgStartStops": [[16423, 16429]]} )
        faceGroups.append({ "name": "joint-r-toe-4-4", "fgStartStops": [[16429, 16435]]} )
        faceGroups.append({ "name": "joint-r-toe-5-1", "fgStartStops": [[16483, 16489]]} )
        faceGroups.append({ "name": "joint-r-toe-5-2", "fgStartStops": [[16477, 16483]]} )
        faceGroups.append({ "name": "joint-r-toe-5-3", "fgStartStops": [[16411, 16417]]} )
        faceGroups.append({ "name": "joint-r-toe-5-4", "fgStartStops": [[16417, 16423]]} )
        faceGroups.append({ "name": "joint-r-upper-leg", "fgStartStops": [[16537, 16543]]} )
        faceGroups.append({ "name": "joint-r-upperlid", "fgStartStops": [[16717, 16723]]} )
        faceGroups.append({ "name": "joint-spine-1", "fgStartStops": [[16063, 16069]]} )
        faceGroups.append({ "name": "joint-spine-2", "fgStartStops": [[16057, 16063]]} )
        faceGroups.append({ "name": "joint-spine-3", "fgStartStops": [[16051, 16057]]} )
        faceGroups.append({ "name": "joint-spine-4", "fgStartStops": [[16045, 16051]]} )
        faceGroups.append({ "name": "joint-tongue-1", "fgStartStops": [[16759, 16765]]} )
        faceGroups.append({ "name": "joint-tongue-2", "fgStartStops": [[16753, 16759]]} )
        faceGroups.append({ "name": "joint-tongue-3", "fgStartStops": [[16741, 16747]]} )
        faceGroups.append({ "name": "joint-tongue-4", "fgStartStops": [[16735, 16741]]} )
        return faceGroups

