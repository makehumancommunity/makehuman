#!/usr/bin/python

from .namespace import NameSpace
from .JsonCall import JsonCall

from core import G

class Internals(NameSpace):
    """The *internals* namespace hierarcy consists of a number of namespaces collecting calls for gaining low-level access to internal MakeHuman functionality.
The idea with these is that you *can* get access to such functionality if you need it, but most definitely not that you *should*.

In the vast majority of cases, you would benefit from first trying to find a relevant call elsewhere in the API, and as a last resort look here."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.JsonCall = JsonCall
        self.trace()

    def getHuman(self):
        """Get the central human object."""
        self.trace()
        return G.app.selectedHuman

    def getApp(self):
        """Get the central app object."""
        self.trace()
        return G.app

    def getSkeleton(self):
        """Get the human's skeleton, if any."""
        self.trace()
        return G.app.selectedHuman.getSkeleton()

    def numpyTypecodeToPythonTypeCode(self, numpyTypeCode):
        """Get the python array type code that is closest to the given numpy type code."""
        if numpyTypeCode == "<f4":
            return "f"

        if numpyTypeCode == "<u4":
            return "I"

        return numpyTypeCode




