#!/usr/bin/python

from .namespace import NameSpace
import sys
import os
import io
import struct
import inspect
import array

from .logchannel import LogChannel

class Utility(NameSpace):
    """This namespace wraps various calls which are convenient but not necessarily MH-specific."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()

        self.isPy3 = (sys.version_info >= (3,0))
        self.debugWriter = {}

        if self.isPython3():
            import urllib.request
            self.urlrequest = urllib.request
            import importlib
            import importlib.util
            self.hasPySide = (importlib.util.find_spec("PySide") is not None)
            self.hasPyQt = (importlib.util.find_spec("PyQt4") is not None)
        else:
            import urllib2
            self.urlrequest = urllib2
            import pkgutil
            self.hasPySide = (pkgutil.find_loader("PySide") is not None)
            self.hasPyQt = (pkgutil.find_loader("PyQt4") is not None)

        self.logChannels = {}

    def getTypeAsString(self, content):

        if isinstance(content, int):
            return "int"
        if isinstance(content, float):
            return "float"
        if isinstance(content, dict):
            return "dict"
        if isinstance(content, list):
            return "list"
        if isinstance(content, array.array):
            return "array(" + content.typecode + ")"
        if self.isPy3:
            if isinstance(content, bytes):
                return "bytes"
            if isinstance(content, str):
                return "unicode"
        else:
            if isinstance(content, unicode):
                return "unicode"
            if isinstance(content, str):
                return "bytes"

        # None of the listed types matched

        with open("/tmp/missingtype.txt","a", encoding='utf-8') as f:
            f.write(str(type(content)))
            f.write("\n")

        return str(type(content))

    def getValueAsString(self, content, newLinesIfComplex=False):
        if isinstance(content, list) or isinstance(content, array.array):
            result = "[]"
            #for value in content:
            #    if result != "":
            #        if newLinesIfComplex:
            #            result = result + ",\n"
            #        else:
            #            result = result + ", "
            #    result = result + self.getValueAsString(value)
            return result
        if self.isPy3:
            if isinstance(content, str):
                return content
            if isinstance(content, bytes):
                try:
                    val = content.decode("utf-8")
                except:
                    import binascii
                    val = binascii.hexlify(content).decode("utf-8")
                return val
        else:
            if isinstance(content, str):
                return content
        if isinstance(content, float):
            # This is to parry differences in precision in py2 vs py3
            # Even when using round(), results will differ. Thus we do
            # a destructive floor instead.
            precision = 100000.0
            intContent = int(precision * round(content,8))
            floatContent = float(intContent) / precision
            return "{0:.4f}".format(floatContent)
        return str(content)

    def isPySideAvailable(self):
        return self.hasPySide

    def isPyQtAvailable(self):
        return self.hasPyQt

    def isPython3(self):
        return self.isPy3

    def getCompatibleUrlFetcher(self):
        return self.urlrequest

    def getLogChannel(self, name, defaultLevel=2, mirrorToMHLog=False):
        if name not in self.logChannels:
            self.logChannels[name] = LogChannel(name,defaultLevel,mirrorToMHLog)
        return self.logChannels[name]

    def resetDebugWriter(self, channelName = "unsorted"):
        self.debugWriter[channelName] = 0
        debugDir = self.api.locations.getUserHomePath("debugWriter")
        subPath = os.path.join( os.path.abspath(debugDir), channelName )
        if not os.path.exists(subPath):
            os.makedirs(subPath)
        fnTxt = os.path.join(subPath, "textualContent.txt")
        if os.path.exists(fnTxt):
            os.remove(fnTxt)
        fnTxt = os.path.join(subPath, "debugContent.txt")
        if os.path.exists(fnTxt):
            os.remove(fnTxt)

    def _py3debugWrite(self, content, fnBin, fnTxt):
        with open(fnBin, "wb") as f:
            wasWritten = False
            if isinstance(content, list):
                for value in content:
                    if isinstance(value, str):
                        f.write( bytes(value, 'utf-8') )
                    else:
                        if isinstance(value, float):
                            f.write( struct.pack("f", value) )
                        else:
                            f.write( bytes(value) )
                wasWritten = True
            if isinstance(content, str) and not wasWritten:
                f.write( bytes(content, 'utf-8') )
                wasWritten = True
            if not wasWritten:
                if isinstance(content, int):
                    f.write( struct.pack("<I", content) )
                else:
                    f.write( bytes(content) )

    def _py2debugWrite(self, content, fnBin, fnTxt):
        with open(fnBin, "wb") as f:
            wasWritten = False
            if isinstance(content, list):
                for value in content:
                    if isinstance(value, float):
                        f.write( struct.pack("f", value) )
                    else:
                        f.write( bytes(value) )
                wasWritten = True
            if isinstance(content, float) and not wasWritten:
                f.write( struct.pack("f", value) )
                wasWritten = True
            if not wasWritten:
                f.write( bytes(content) )

    def debugWrite(self, content, channelName = "unsorted", location = "genericLocation"):
        debugDir = self.api.locations.getUserHomePath("debugWriter")
        subPath = os.path.join( os.path.abspath(debugDir), channelName )
        if not os.path.exists(subPath):
            os.makedirs(subPath)
        increment = 0
        if channelName in self.debugWriter:
            increment = self.debugWriter[channelName]
        else:
            self.debugWriter[channelName] = 0
        increment = increment + 1
        self.debugWriter[channelName] = increment
        incrementStr = '{0:05d}'.format(increment)
        fnBin = os.path.join(subPath, "bin-" + incrementStr + "-" + location + ".bin")
        fnTxt = os.path.join(subPath, "textualContent.txt")
        fnStack = os.path.join(subPath, "stack-" + incrementStr + "-" + location + ".txt")

        if self.isPy3:
            self._py3debugWrite(content, fnBin, fnTxt)
        else:
            self._py2debugWrite(content, fnBin, fnTxt)

        with open(fnTxt, "a", encoding='utf-8') as f:
            f.write(str(increment))
            f.write("\n")
            val = self.getValueAsString(content, True)
            f.write(val)
            f.write("\n\n")

        fnDebug = os.path.join(subPath, "debugContent.txt")
        with open(fnDebug, "a", encoding='utf-8') as f:
            f.write(str(increment))
            f.write("\n")
            f.write(self.getTypeAsString(content))
            f.write("\n")

            stack = inspect.stack()

            i = len(stack) - 1

            exclude = ["makehuman.py", "qtui.py", "qtgui.py", "mhmain.py"]

            while i > 1:
                (frame, filename, line_number, function_name, lines, index) = stack[i]
                fn = os.path.basename(filename) 
                if not fn in exclude:
                    f.write(fn + " -> " + function_name)                
                    f.write("\n")
                i = i - 1

            f.write("\n")

        with open(fnStack, "w", encoding='utf-8') as f:
            f.write(str(increment))
            f.write("\n")

            stack = inspect.stack()

            i = len(stack) - 1

            exclude = ["makehuman.py", "qtui.py", "qtgui.py", "mhmain.py"]

            while i > 1:
                (frame, filename, line_number, function_name, lines, index) = stack[i]
                fn = os.path.basename(filename)
                fn = fn.replace(".py", "")
                if not fn in exclude:
                    f.write(fn + "." + function_name + "():" + str(line_number))
                    f.write("\n")
                i = i - 1
            f.write("\n")


