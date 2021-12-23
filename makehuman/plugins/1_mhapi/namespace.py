#!/usr/bin/python

import inspect
import sys
from abc import *

# When developing the API we want to get a continuous output of which
# methods are called and within which namespace. Setting this to true
# will print all such accesses to the console prompt
api_tracing = False

# The following is an ugly copy/paste, but since python2 and python3 
# have different syntaxes regarding abstract base classes, this is 
# the most stable solution

if sys.version_info >= (3,0):

    class NameSpace(ABC):
    
        def __init__(self):
            global api_tracing
            self.tracing = api_tracing
            self.trace()
    
        # Utility method for printing info about where we are in the code
        # to the console prompt. In the future we should probably use the
        # log function instead.
        def trace(self):
            if self.tracing:
                info = dict()
    
                stack = inspect.currentframe().f_back
                info["line_number"] = str(stack.f_lineno)
                info["caller_name"] = stack.f_globals["__name__"]
                info["file_name"] = stack.f_globals["__file__"]
                info["caller_method"] = inspect.stack()[1][3]
    
                stack = inspect.stack()
                info["caller_class"] = str(stack[1][0].f_locals["self"].__class__)
    
                print("TRACE {}.{}():{}".format(info["caller_name"], info["caller_method"], info["line_number"]))

else:

    class NameSpace:
    
        __metaclass__ = ABCMeta

        def __init__(self):
            global api_tracing
            self.tracing = api_tracing
            self.trace()
    
        # Utility method for printing info about where we are in the code
        # to the console prompt. In the future we should probably use the
        # log function instead.
        def trace(self):
            if self.tracing:
                info = dict()
    
                stack = inspect.currentframe().f_back
                info["line_number"] = str(stack.f_lineno)
                info["caller_name"] = stack.f_globals["__name__"]
                info["file_name"] = stack.f_globals["__file__"]
                info["caller_method"] = inspect.stack()[1][3]
    
                stack = inspect.stack()
                info["caller_class"] = str(stack[1][0].f_locals["self"].__class__)
    
                print("TRACE {}.{}():{}".format(info["caller_name"], info["caller_method"], info["line_number"]))



