#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2015

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

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
