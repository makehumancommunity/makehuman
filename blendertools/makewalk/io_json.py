# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2014
# Coding Standards:    See http://www.makehuman.org/node/165

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
        with gzip.open(realpath, 'wb') as fp:
            fp.write(bytes)
    else:
        string = encodeJsonData(struct, "")
        with open(filepath, "w", encoding="utf-8") as fp:
            fp.write(string)
            fp.write("\n")


def encodeJsonData(data, pad=""):
    if data == None:
        return "none"
    elif isinstance(data, bool):
        if data == True:
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
        if data == []:
            return "[]"
        elif leafList(data):
            string = "["
            for elt in data:
                string += encodeJsonData(elt) + ", "
            return string[:-2] + "]"
        else:
            string = "["
            for elt in data:
                string += "\n    " + pad + encodeJsonData(elt, pad+"    ") + ","
            return string[:-1] + "\n%s]" % pad
    elif isinstance(data, dict):
        if data == {}:
            return "{}"
        string = "{"
        for key,value in data.items():
            string += "\n    %s\"%s\" : " % (pad, key) + encodeJsonData(value, pad+"    ") + ","
        return string[:-1] + "\n%s}" % pad


def leafList(data):
    for elt in data:
        if isinstance(elt, (list,tuple,dict)):
            return False
    return True
