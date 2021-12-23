#!/usr/bin/python

from .namespace import NameSpace

class Viewport(NameSpace):
    """This namespace wraps calls which relate to the viewport (camera position etc)."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()

