#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Abstract
--------

Configuration file parser using JSON format
"""

import json
import getpath

def _s2u(value):
    if isinstance(value, basestring):
        return getpath.stringToUnicode(value, ['utf-8', 'iso-8859-1'] + getpath.PATH_ENCODINGS)
    elif isinstance(value, dict):
        return dict([(str(key), _s2u(val)) for key, val in value.iteritems()])
    elif isinstance(value, list):
        return [_s2u(val) for val in value]
    else:
        return value

def parseINI(s, replace = []):
    try:
        result = json.loads(s, encoding='utf-8')
    except ValueError:
        for src, dst in replace + [("'",'"'), (": True",": true"), (": False",": false"), (": None",": null")]:
            s = s.replace(src, dst)
        result = json.loads(s, encoding='utf-8')
    return _s2u(result)

def formatINI(d):
    return json.dumps(d, indent=4, ensure_ascii=True, encoding='utf-8') + '\n'
