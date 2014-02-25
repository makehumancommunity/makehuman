#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import json

def _u2s(value):
    if isinstance(value, unicode):
        return str(value)
    elif isinstance(value, dict):
        return dict([(str(key), _u2s(val)) for key, val in value.iteritems()])
    elif isinstance(value, list):
        return [_u2s(val) for val in value]
    else:
        return value

def parseINI(s, replace = []):
    try:
        result = json.loads(s)
    except ValueError:
        for src, dst in replace + [("'",'"'), (": True",": true"), (": False",": false"), (": None",": null")]:
            s = s.replace(src, dst)
        result = json.loads(s)
    return _u2s(result)

def formatINI(d):
    return json.dumps(d, indent=4, ensure_ascii=True, encoding='iso-8859-1') + '\n'
