#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2020

**Licensing:**         AGPL3

    This file is part of MakeHuman Community (www.makehumancommunity.org).

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
    if isinstance(value, str):
        return value
    elif isinstance(value, dict):
        return dict([(str(key), _s2u(val)) for key, val in list(value.items())])
    elif isinstance(value, list):
        return [_s2u(val) for val in value]
    else:
        return value


def parseINI(s, replace = []):
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    try:
        result = json.loads(s)
    except ValueError:
        for src, dst in replace + [("'",'"'), (": True",": true"), (": False",": false"), (": None",": null")]:
            s = s.replace(src, dst)
        result = json.loads(s)
    return _s2u(result)


def formatINI(d):
    return json.dumps(d, indent=4, ensure_ascii=False) + '\n'
