#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Aranuvir

**Copyright(c):**      MakeHuman Team 2001-2020

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

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
This module will automatically convert mhm files in the 'models' folder. In the tags line ';' will be the new tag
separator. Whitespaces masked with ',,' will be reverted.

TODO
"""

import getpath as gp
import os.path
import shutil
import log
import filecmp

def load(app):

    fileList = gp.search(gp.getPath('models'), extensions='.mhm', recursive=True)

    for filepath in fileList:

        isChanged = False
        hasFailed = False

        if os.path.isfile(filepath):

            with open(filepath, 'r') as f:
                lines = f.readlines()

            for idx, line in enumerate(lines):
                if line.startswith('tags'):
                    if ',,' in line:
                        data = line.split()
                        lines[idx] = data[0] + ' ' + ';'.join([d.replace(',,', ' ') for d in data[1:]]) + '\n'
                        isChanged = True
                        log.message('Replacing %s: "%s" by "%s"' % (filepath, line.strip(), lines[idx].strip()))
                        break
                    else:
                        break

            if isChanged:

                backup_filepath = filepath + '~'

                if not os.path.isfile(backup_filepath):
                    try:
                        shutil.copy2(filepath, backup_filepath)
                    except:
                        log.warning('Failed to backup %s. Changes will not be stored' % filepath)
                        hasFailed = True
                else:
                    log.warning('Backup file %s already exists.' % backup_filepath)
                    hasFailed = True

                if filecmp.cmp(filepath, backup_filepath, shallow=False) and not hasFailed:
                    log.message('Created backup file: %s' % backup_filepath)
                    try:
                        with open(filepath, 'w') as f:
                            f.writelines(lines)
                        log.message('Successfully converted: %s' % filepath)
                    except:
                        log.warning('Cannot write changes to %s' % filepath)
                        hasFailed = True
                else:
                    log.warning('Failed to backup %s. Changes will not be stored' % filepath)
                    hasFailed = True

            if hasFailed:
                log.warning('Failed to convert %s. The tags line should be fixed in a text editor.' % filepath)


def unload(app):
    pass