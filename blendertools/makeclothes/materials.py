#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

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
Utility for making clothes to MH characters.
"""

import bpy
import os
import shutil
from . import mc
from .error import MHError, addWarning

'''
def checkObjectHasDiffuseTexture(ob):
    """
    An object must either lack material, or have a diffuse texture.
    """
    if ob.data.materials:
        mat = ob.data.materials[0]
        if mat is None:
            return True
        else:
            for mtex in mat.texture_slots:
                if mtex is None:
                    continue
                if mtex.use_map_color_diffuse:
                    tex = mtex.texture
                    if tex.type == 'IMAGE' and tex.image is not None:
                        return True
        return False
    else:
        return True
'''

def writeMaterial(ob, folder):
    """
    Create an mhmat file and write material settings there.
    """
    if ob.data.materials:
        mat = ob.data.materials[0]
        if mat is None:
            return None
        else:
            name = mc.goodName(mat.name)
            _,filepath = mc.getFileName(ob, folder, "mhmat")
            outdir = os.path.dirname(filepath)
            fp = mc.openOutputFile(filepath)
            try:
                matfile = writeMaterialFile(fp, mat, name, outdir)
            finally:
                fp.close()
            print("%s created" % filepath)
            return os.path.basename(filepath)
    return None


def writeMaterialFile(fp, mat, name, outdir):
    """
    Write a material (.mhmat) file in the output folder.
    Also copies all textures to the output folder
    """

    fp.write(
        '# MakeHuman Material definition\n' +
        '\n' +
        'name %sMaterial\n' % name +
        '\n' +
        '// Color shading attributes\n'
        'diffuseColor  %.4g %.4g %.4g\n' % tuple(mat.diffuse_intensity * mat.diffuse_color) +
        'specularColor  %.4g %.4g %.4g\n' % tuple(mat.specular_intensity * mat.specular_color) +
        'shininess %.4g\n' % max(0, min(mat.specular_hardness/255, 1)) +
        'opacity %.4g\n' % mat.alpha +
        '\n' +
        '// Textures and properties\n')

    useDiffuse = useSpecular = useBump = useNormal = useDisplacement = "false"
    for slotNo,mtex in enumerate(mat.texture_slots):
        if mtex is None or not mat.use_textures[slotNo]:
            continue
        tex = mtex.texture
        if (tex.type != 'IMAGE' or
            tex.image is None):
            continue
        if tex.image.filepath == "":
            raise MHError("Texture %s image must be saved first" % tex.name)
        srcpath = tex.image.filepath
        texpath = os.path.basename(srcpath).replace(" ","_")

        if mtex.use_map_color_diffuse:
            fp.write('diffuseTexture %s\n' % texpath)
            useDiffuse = "true"
        if mtex.use_map_alpha:
            useAlpha = "true"
        if mtex.use_map_specular:
            fp.write('specularTexture %s\n' % texpath)
            useSpecular = "true"
        if mtex.use_map_normal:
            if True:
                fp.write('bumpTexture %s\n' % texpath)
                useBump = "true"
            else:
                fp.write('normalTexture %s\n' % texpath)
                useNormal = "true"
        if mtex.use_map_displacement:
            fp.write('displacementTexture %s\n' % texpath)
            useDisplacement = "true"

        trgpath = os.path.join(outdir, texpath)
        print("Copy texture %s => %s" % (srcpath, trgpath))
        try:
            shutil.copy(srcpath, trgpath)
        except FileNotFoundError:
            addWarning("Texture\n \"%s\" \nnot found\n" % srcpath)

    fp.write(
        '\n' +
        '// Shader programme\n' +
        'shader data/shaders/glsl/phong\n' +
        '\n' +
        '// Configure built-in shader defines\n' +
        'shaderConfig diffuse %s\n' % useDiffuse +
        'shaderConfig bump %s\n' % useBump +
        'shaderConfig normal  %s\n' % useNormal +
        'shaderConfig displacement  %s\n' % useDisplacement +
        'shaderConfig spec  %s\n' % useSpecular +
        'shaderConfig vertexColors false\n')

