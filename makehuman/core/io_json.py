#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Utility reading and writing JSON files. Optionally the file may be
gzipped for saving space.
"""

import json
import gzip

def loadJson(filepath):
    try:
        with gzip.open(filepath, 'rb') as fp:
            bytes = fp.read()
    except IOError:
        bytes = None

    if bytes:
        string = bytes.decode("utf-8")
        struct = json.loads(string)
    else:
        with open(filepath, "rU") as fp:
            struct = json.load(fp)

    return struct


def saveJson(struct, filepath, binary=False):
    if binary:
        bytes = json.dumps(struct)
        with gzip.open(filepath, 'wb') as fp:
            fp.write(bytes)
    else:
        import codecs
        string = encodeJsonData(struct, "    ")
        with codecs.open(filepath, "w", encoding="utf-8") as fp:
            fp.write(string)
            fp.write("\n")


def encodeJsonData(data, pad=""):
    if isinstance(data, bool):
        if data:
            return "true"
        else:
            return "false"
    elif isinstance(data, float):
        if abs(data) < 1e-6:
            return "0"
        else:
            return "%.5g" % data
    elif isinstance(data, int):
        return str(data)
    elif isinstance(data, str):
        return "\"%s\"" % data
    elif isinstance(data, (list, tuple)):
        if leafList(data):
            string = "["
            for elt in data:
                string += encodeJsonData(elt) + ","
            return string[:-1] + "]"
        else:
            string = "["
            for elt in data:
                string += "\n    " + pad + encodeJsonData(elt, pad+"    ") + ","
            return string[:-1] + "\n%s]" % pad
    elif isinstance(data, dict):
        string = "{"
        for key,value in data.items():
            string += "\n    %s\"%s\" : " % (pad, key) + encodeJsonData(value, pad+"    ") + ","
        return string[:-1] + "\n%s}" % pad


def leafList(data):
    for elt in data:
        if isinstance(elt, (list,tuple,dict)):
            return False
    return True
