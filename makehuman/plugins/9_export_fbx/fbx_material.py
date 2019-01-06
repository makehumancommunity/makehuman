#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Thomas Larsson, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2019

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
Fbx materials and textures
"""

from .fbx_utils import *

#--------------------------------------------------------------------
#   Object definitions
#--------------------------------------------------------------------

def getObjectNumbers(meshes):
    """
    Number of materials, textures and images required by the materials of the
    specified meshes, to be exported to FBX format.
    """
    nMaterials = len(meshes)
    nTextures = 0
    nImages = 0
    for mesh in meshes:
        mat = mesh.material
        if mat.diffuseTexture:
            nTextures += 1
            nImages += 1
        if mat.specularMapTexture:
            nTextures += 1
            nImages += 1
        if mat.transparencyMapTexture:
            nTextures += 1
            nImages += 1
        if mat.normalMapTexture:
            nTextures += 1
            nImages += 1
        if mat.bumpMapTexture:
            nTextures += 1
            nImages += 1
        if mat.displacementMapTexture:
            nTextures += 1
            nImages += 1
    return nMaterials,nTextures,nImages


def countObjects(meshes):
    """
    Number of objects to be declared for exporting the materials, including the
    textures and images of the specified meshes.
    """
    nMaterials,nTextures,nImages = getObjectNumbers(meshes)
    return (nMaterials + nTextures + nImages)


def writeObjectDefs(fp, meshes, config):
    nMaterials,nTextures,nImages = getObjectNumbers(meshes)

    properties_mat = [
        (b"ShadingModel", ("Phong", "p_string", False)),
        (b"MultiLayer", (False, "p_bool", False)),
        (b"EmissiveColor", ((0.0, 0.0, 0.0), "p_color", True)),
        (b"EmissiveFactor", (1.0, "p_number", True)),
        (b"AmbientColor", ((0.2, 0.2, 0.2), "p_color", True)),
        (b"AmbientFactor", (1.0, "p_number", True)),
        (b"DiffuseColor", ((0.8, 0.8, 0.8), "p_color", True)),
        (b"DiffuseFactor", (1.0, "p_number", True)),
        (b"Bump", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"NormalMap", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"BumpFactor", (1.0, "p_double", False)),
        (b"TransparentColor", ((0.0, 0.0, 0.0), "p_color", True)),
        (b"TransparencyFactor", (0.0, "p_number", True)),
        (b"DisplacementColor", ((0.0, 0.0, 0.0), "p_color_rgb", False)),
        (b"DisplacementFactor", (1.0, "p_double", False)),
        (b"VectorDisplacementColor", ((0.0, 0.0, 0.0), "p_color_rgb", False)),
        (b"VectorDisplacementFactor", (1.0, "p_double", False)),
        (b"SpecularColor", ((0.2, 0.2, 0.2), "p_color", True)),
        (b"SpecularFactor", (1.0, "p_number", True)),
        (b"ShininessExponent", (20.0, "p_number", True)),
        (b"ReflectionColor", ((0.0, 0.0, 0.0), "p_color", True)),
        (b"ReflectionFactor", (1.0, "p_number", True)),
        #(b"Shininess", (20.0, "p_number", True)),
        #(b"Opacity", (1.0, "p_number", True)),
    ]

    properties_tex = [
        (b"TextureTypeUse", (0, "p_enum", False)),  # Standard.
        (b"Texture alpha", (1.0, "p_double", False)),
        (b"CurrentMappingType", (0, "p_enum", False)),  # UV.
        (b"WrapModeU", (0, "p_enum", False)),  # Repeat.
        (b"WrapModeV", (0, "p_enum", False)),  # Repeat.
        (b"UVSwap", (False, "p_bool", False)),
        (b"PremultiplyAlpha", (True, "p_bool", False)),
        (b"Translation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"Rotation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"Scaling", ((1.0, 1.0, 1.0), "p_vector_3d", False)),
        (b"TextureRotationPivot", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"TextureScalingPivot", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"CurrentTextureBlendMode", (1, "p_enum", False)),  # Additive...
        (b"UVSet", ("default", "p_string", False)),  # UVMap name.
        (b"UseMaterial", (False, "p_bool", False)),
        (b"UseMipMap", (False, "p_bool", False)),
        #(b"AlphaSource", (2, "p_enum", False)),  # Black (i.e. texture's alpha), XXX name guessed!.
    ]

    properties_vid = [
        (b"ImageSequence", (False, "p_bool", False)),
        (b"ImageSequenceOffset", (0, "p_integer", False)),
        (b"FrameRate", (0.0, "p_double", False)),
        (b"LastFrame", (0, "p_integer", False)),
        (b"Width", (0, "p_integer", False)),
        (b"Height", (0, "p_integer", False)),
        (b"Path", ("", "p_string_url", False)),
        (b"StartFrame", (0, "p_integer", False)),
        (b"StopFrame", (0, "p_integer", False)),
        (b"PlaySpeed", (0.0, "p_double", False)),
        (b"Offset", (0, "p_timestamp", False)),
        (b"InterlaceMode", (0, "p_enum", False)),  # None, i.e. progressive.
        (b"FreeRunning", (False, "p_bool", False)),
        (b"Loop", (False, "p_bool", False)),
        (b"AccessMode", (0, "p_enum", False)),  # Disk (0=Disk, 1=Mem, 2=DiskAsync).
    ]

    if config.binary:
        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, b'Definitions')
        fbx_binary.fbx_template_generate(elem, b"Material", nMaterials, b"FbxSurfacePhong", properties_mat)
        fbx_binary.fbx_template_generate(elem, b"Texture", nTextures, b"FbxFileTexture", properties_tex)
        fbx_binary.fbx_template_generate(elem, b"Video", nImages, b"FbxVideo", properties_vid)
        return

    from . import fbx_utils
    fp.write(
"""
    ObjectType: "Material" {
""" +
'    Count: %d' % (nMaterials) +
"""
        PropertyTemplate: "FbxSurfacePhong" {
            Properties70:  {
""" + fbx_utils.get_ascii_properties(properties_mat, indent=4) + """
            }
        }
    }
""")

    fp.write(
"""
    ObjectType: "Texture" {
""" +
'    Count: %d' % (nTextures) +
"""
        PropertyTemplate: "FbxFileTexture" {
            Properties70:  {
""" + fbx_utils.get_ascii_properties(properties_tex, indent=4) + """
            }
        }
    }

    ObjectType: "Video" {
""" +
'    Count: %d' % (nImages) +
"""
        PropertyTemplate: "FbxVideo" {
            Properties70:  {
""" + fbx_utils.get_ascii_properties(properties_vid, indent=4) + """
            }
        }
    }
""")

#--------------------------------------------------------------------
#   Object properties
#--------------------------------------------------------------------

def writeObjectProps(fp, meshes, config):
    for mesh in meshes:
        mat = mesh.material
        writeMaterial(fp, mesh, config)
        writeTexture(fp, mat.diffuseTexture, "DiffuseColor", config)
        writeTexture(fp, mat.specularMapTexture, "SpecularFactor", config)
        writeTexture(fp, mat.normalMapTexture, "Bump", config)
        writeTexture(fp, mat.transparencyMapTexture, "TransparencyFactor", config)
        writeTexture(fp, mat.bumpMapTexture, "BumpFactor", config)
        writeTexture(fp, mat.displacementMapTexture, "DisplacementFactor", config)


def writeMaterial(fp, mesh, config):
    id,key = getId("Material::"+mesh.name)

    mat = mesh.material
    properties = [
        (b"DiffuseColor", "p_color", mat.diffuseColor.asTuple(), b"A"),
        (b"Diffuse", "p_vector_3d", mat.diffuseColor.asTuple(), b"A"),
        (b"SpecularColor", "p_color", mat.specularColor.asTuple(), b"A"),
        (b"Specular", "p_vector_3d", mat.specularColor.asTuple(), b"A"),
        (b"Shininess", "p_double", mat.shininess, b"A"),
        (b"Reflectivity", "p_double", 0.0, b"A"),
        (b"Emissive", "p_vector_3d", mat.emissiveColor.asTuple(), b"A"),
        (b"Ambient", "p_vector_3d", mat.ambientColor.asTuple(), b"A"),
        (b"TransparencyFactor", "p_number", mat.transparencyMapIntensity, True, b"A"),
        (b"Opacity", "p_double", mat.opacity, b"A")
    ]

    if config.binary:
        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, b'Objects')
        fbx_binary.fbx_data_material(elem, bytes(key, 'utf-8'), id, properties)
        return

    from . import fbx_utils

    fp.write(
'    Material: %d, "%s", "" {' % (id, key) + """
        Version: 102
        ShadingModel: "phong"
        MultiLayer: 0
        Properties70:  {
""" + fbx_utils.get_ascii_properties(properties, indent=3) + """
        }
    }
""")


def writeTexture(fp, filepath, channel, config):
    if not filepath:
        return
    filepath = config.copyTextureToNewLocation(filepath)
    texname = getTextureName(filepath)
    relpath = getRelativePath(filepath)

    vid,vkey = getId("Video::%s" % texname)
    tid,tkey = getId("Texture::%s" % texname)

    properties_vid = [
        (b"Path", "p_string_url", filepath)
    ]

    properties_tex = [
        (b"MHName", "p_string", tkey, False, True)
    ]

    if config.binary:
        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, b'Objects')
        fbx_binary.fbx_data_texture_file_element(elem, tkey, tid, vkey, vid, filepath, relpath, properties_tex, properties_vid)
        return

    from . import fbx_utils

    fp.write(
'    Video: %d, "%s", "Clip" {' % (vid, vkey) + """
        Type: "Clip"
        Properties70:  {
""" + fbx_utils.get_ascii_properties(properties_vid, indent=3) + """
        }
        UseMipMap: 0
        Filename: "%s\"""" % filepath + """
        RelativeFilename: "%s\"""" % relpath + """
    }
""")


    fp.write(
'    Texture: %d, "%s", "" {' % (tid, tkey) + """
        Type: "TextureVideoClip"
        Version: 202
        TextureName: "%s\"""" % tkey + """
        Properties70:  {
""" + fbx_utils.get_ascii_properties(properties_tex, indent=3) + """
        }
        Media: "%s\"""" % vkey + """
        Filename: "%s\"""" % filepath + """
        RelativeFilename: "%s\"""" % relpath + """
        ModelUVTranslation: 0,0
        ModelUVScaling: 1,1
        Texture_Alpha_Source: "None"
        Cropping: 0,0,0,0
    }
""")


#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def writeLinks(fp, meshes, config):
    for mesh in meshes:
        ooLink(fp, 'Material::%s' % mesh.name, 'Model::%sMesh' % mesh.name, config)

        mat = mesh.material
        for filepath,channel in [
            (mat.diffuseTexture, b"DiffuseColor"),
            (mat.diffuseTexture, b"TransparencyFactor"),
            (mat.specularMapTexture, b"SpecularIntensity"),
            (mat.normalMapTexture, b"Bump"),
            (mat.transparencyMapTexture, b"TransparencyFactor"),
            (mat.bumpMapTexture, b"BumpFactor"),
            (mat.displacementMapTexture, b"Displacement")]:
            if filepath:
                texname = getTextureName(filepath)
                opLink(fp, 'Texture::%s' % texname, 'Material::%s' % mesh.name, channel, config)
                ooLink(fp, 'Video::%s' % texname, 'Texture::%s' % texname, config)

