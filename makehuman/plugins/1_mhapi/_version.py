#!/usr/bin/python

from .namespace import NameSpace
import makehuman

class Version(NameSpace):
    """This namespace wraps all calls that are related to hg and MH version."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()
        
        self.rev = None
        self.revid = None
        self.branch = None

        try:       
            hg = makehuman.get_revision_hg_info()
            if hg:
                self.rev = hg[0]
                self.revid = hg[1]
                self.branch = hg[2]
        except:
            pass

    def getBranch(self):
        """Returns the name of the current local code branch, for example 'default'. If this is not possible to deduce, None is returned."""
        self.trace()
        return self.branch

    def getRevision(self):
        """Return the full textual representation of the Hg revision, for example 'r1604 (d48f36771cc0)'. If this is not possible to deduce, None is returned."""
        self.trace()
        if not self.rev:
            return None

        if not self.revid:
            return None
        
        return self.rev + " (" + self.revid + ")"

    def getRevisionId(self):
        """Return the hash id of the Hg revision, for example 'd48f36771cc0'. If this is not possible to deduce, None is returned."""
        self.trace()
        return self.revid

    def getRevisionNumber(self):
        """Returns the number of the current local revision as an integer, for example 1604. If this is not possible to deduce, None is returned."""
        self.trace()
        return self.rev

    def getFullVersion(self):
        """Returns the full textual description of the current version, for example 'MakeHuman unstable 20141120' or 'MakeHuman 1.0.2'."""
        self.trace()
        return makehuman.getVersionStr(True,True)

    def getVersionNumberAsArray(self):
        """Returns the numeric representation of the version number as cells in an array, for example [1, 0, 2]."""
        self.trace()
        return makehuman.getVersion()

    def getVersionNumberAsString(self):
        """Returns the string representation of the version number, for example '1.0.2'."""
        self.trace()
        return makehuman.getVersionDigitsStr()


