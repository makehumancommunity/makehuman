#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Translation and localization module.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Manuel Bastioni, Marc Flerackers, Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Language file loading and translation.
"""

import os
import log
import json
from getpath import getPath, getSysDataPath

class Language(object):
    def __init__(self):
        self.language = None
        self.languageStrings = None
        self.missingStrings = set()
        self.rtl = False

    def setLanguage(self, lang):
        self.languageStrings = None
        path = os.path.join(getSysDataPath("languages/"), lang + ".ini")
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
            
    def getLanguageString(self, string):
        if not self.languageStrings:
            return string
        result = self.languageStrings.get(string)
        if result is not None:
            return result
        self.missingStrings.add(string)
        return string
            
    def dumpMissingStrings(self):
        if not self.language:
            return
        path = os.path.join(getPath(''), "data", "languages", self.language + ".missing")
        pathdir = os.path.dirname(path)
        if not os.path.isdir(pathdir):
            os.makedirs(pathdir)
        with open(path, 'w') as f:
            for string in self.missingStrings:
                f.write('"%s": "",\n' % string.encode('utf8'))

language = Language()
