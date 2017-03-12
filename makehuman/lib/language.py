#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Translation and localization module.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Joel Palmius, Marc Flerackers, Glynn Clements

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

Language file loading and translation.
"""

import os
import log
import json
from getpath import getPath, getSysDataPath, getDataPath

import collections

class Language(object):
    def __init__(self):
        self.language = None
        self.languageStrings = None
        self.missingStrings = OrderedSet()
        self.rtl = False

    def setLanguage(self, lang):
        self.languageStrings = None
        path = os.path.join(getSysDataPath("languages/"), lang + ".json")
        if not os.path.isfile(path):
            return
        with open(path, 'rU') as f:
            try:
                self.languageStrings = json.loads(f.read())
            except:
                log.error('Error in language file %s', lang, exc_info=True)
                self.languageStrings = None
        self.language = lang
        self.rtl = False
        if self.languageStrings and '__options__' in self.languageStrings:
            self.rtl = self.languageStrings['__options__'].get('rtl', False)
            
    def getLanguageString(self, string, appendData=None, appendFormat=None):
        if not string:
            return string
        if string == "%%s":
            return string
        if isinstance(string,list):
            if len(string) == 2:
                appendData = string[1];
                string = string[0];
            else:
                if len(string) == 3:
                    appendFormat = string[2]
                    appendData = string[1]
                    string = string[0]

        if self.languageStrings is None:
            result = string
        else:
            result = self.languageStrings.get(string)

        if result is not None:
            if appendData is not None:
                if appendFormat is not None:
                    result = result + (appendFormat % appendData)
                else:
                    result = result + appendData
            return result
        self.missingStrings.add(string)
        return string
            
    def dumpMissingStrings(self):
        if not self.language:
            return
        path = os.path.join(getSysDataPath("languages/"), self.language + ".missing")
        pathdir = os.path.dirname(path)
        if not os.path.isdir(pathdir):
            os.makedirs(pathdir)
        with open(path, 'wb') as f:
            for string in self.missingStrings:
                if self.language == "master":
                    f.write('"%s": "%s",\n' % (string.replace('\n', '\\n').encode('utf8'), string.replace('\n', '\\n').encode('utf8')))
                else:
                    f.write('"%s": "",\n' % string.replace('\n', '\\n').encode('utf8'))


class OrderedSet(collections.MutableSet):
    """
    Set that maintains insertion order.

    This is a python recipe, as referenced in the official documentation
    (http://docs.python.org/2/library/collections.html)
    Source: http://code.activestate.com/recipes/576694/
    """

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

def getLanguages():
    """
    The languages available on this MH installation, by listing all .json
    files in the languages folder in user and system data path.
    """
    langDirFiles = os.listdir(getSysDataPath('languages'))
    try:
        langDirFiles = langDirFiles + os.listdir(getDataPath('languages'))
    except:
        pass
    return ['english'] + sorted([os.path.basename(filename).replace('.json', '') for filename in langDirFiles if filename.split(os.extsep)[-1] == "json"])


language = Language()
