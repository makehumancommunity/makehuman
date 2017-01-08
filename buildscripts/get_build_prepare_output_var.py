#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
Simple parser for the build_prepare output file

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2015

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

Quickly retrieve values from the build_prepare.out file from commandline.
"""

import sys

def parse(filepath, variable):
    f = open(filepath, 'rb')
    for line in f:
        if line.startswith('  '):
            tokens = [t.strip() for t in line.split(':')]
            if len(tokens) >= 2 and tokens[0].lower() == variable.lower():
                f.close()
                return ': '.join(tokens[1:])
    f.close()

def _parse_args():
    if len(sys.argv) < 2:
        return dict()

    import argparse    # requires python >= 2.7
    parser = argparse.ArgumentParser()

    # optional arguments
    parser.add_argument('--token', '-t', metavar='n', default=None, type=int,
                   help='Only return this space delimited token from the variable (starting at 0)')

    # positional arguments
    parser.add_argument("filePath", default=None, nargs='?', help="Path to .build_prepare.out file")
    parser.add_argument("variable", default=None, nargs='?', help="Name of the variable to retrieve")

    argOptions = vars(parser.parse_args())
    return argOptions


if __name__ == '__main__':
    args = _parse_args()

    if args.get('filePath', None) is None:
        raise RuntimeError("filePath argument not specified")
    if args.get('variable', None) is None:
        raise RuntimeError("variable argument not specified")

    result = parse(args['filePath'], args['variable'])

    if args.get('token', None) is not None and result:
        result = result.split(' ')[args.get('token')]

    print result
