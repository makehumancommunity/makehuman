#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------
Fbx materials and textures
"""

from .fbx_utils import *

#--------------------------------------------------------------------
#   Object definitions
#--------------------------------------------------------------------

def getObjectNumbers(rmeshes):
    nMaterials = len(rmeshes)
    nTextures = 0
    nImages = 0
    for rmesh in rmeshes:
        mat = rmesh.material
        if mat.diffuseTexture:
            nTextures += 2
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


def countObjects(rmeshes, amt):
    nMaterials,nTextures,nImages = getObjectNumbers(rmeshes)
    return (nMaterials + nTextures + nImages)


def writeObjectDefs(fp, rmeshes, amt):
    nMaterials,nTextures,nImages = getObjectNumbers(rmeshes)

    fp.write(
"""
    ObjectType: "Material" {
""" +
'    Count: %d' % (nMaterials) +
"""
        PropertyTemplate: "FbxSurfacePhong" {
            Properties70:  {
                P: "ShadingModel", "KString", "", "", "Phong"
                P: "MultiLayer", "bool", "", "",0
                P: "EmissiveColor", "Color", "", "A",0,0,0
                P: "EmissiveFactor", "Number", "", "A",1
                P: "AmbientColor", "Color", "", "A",0.2,0.2,0.2
                P: "AmbientFactor", "Number", "", "A",1
                P: "DiffuseColor", "Color", "", "A",0.8,0.8,0.8
                P: "DiffuseFactor", "Number", "", "A",1
                P: "Bump", "Vector3D", "Vector", "",0,0,0
                P: "NormalMap", "Vector3D", "Vector", "",0,0,0
                P: "BumpFactor", "double", "Number", "",1
                P: "TransparentColor", "Color", "", "A",0,0,0
                P: "TransparencyFactor", "Number", "", "A",0
                P: "DisplacementColor", "ColorRGB", "Color", "",0,0,0
                P: "DisplacementFactor", "double", "Number", "",1
                P: "VectorDisplacementColor", "ColorRGB", "Color", "",0,0,0
                P: "VectorDisplacementFactor", "double", "Number", "",1
                P: "SpecularColor", "Color", "", "A",0.2,0.2,0.2
                P: "SpecularFactor", "Number", "", "A",1
                P: "ShininessExponent", "Number", "", "A",20
                P: "ReflectionColor", "Color", "", "A",0,0,0
                P: "ReflectionFactor", "Number", "", "A",1
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
                P: "TextureTypeUse", "enum", "", "",0
                P: "Texture alpha", "Number", "", "A",1
                P: "CurrentMappingType", "enum", "", "",0
                P: "WrapModeU", "enum", "", "",0
                P: "WrapModeV", "enum", "", "",0
                P: "UVSwap", "bool", "", "",0
                P: "PremultiplyAlpha", "bool", "", "",1
                P: "Translation", "Vector", "", "A",0,0,0
                P: "Rotation", "Vector", "", "A",0,0,0
                P: "Scaling", "Vector", "", "A",1,1,1
                P: "TextureRotationPivot", "Vector3D", "Vector", "",0,0,0
                P: "TextureScalingPivot", "Vector3D", "Vector", "",0,0,0
                P: "CurrentTextureBlendMode", "enum", "", "",1
                P: "UVSet", "KString", "", "", "default"
                P: "UseMaterial", "bool", "", "",0
                P: "UseMipMap", "bool", "", "",0
            }
        }
    }

    ObjectType: "Video" {
""" +
'    Count: %d' % (nImages) +
"""
        PropertyTemplate: "FbxVideo" {
            Properties70:  {
                P: "ImageSequence", "bool", "", "",0
                P: "ImageSequenceOffset", "int", "Integer", "",0
                P: "FrameRate", "double", "Number", "",0
                P: "LastFrame", "int", "Integer", "",0
                P: "Width", "int", "Integer", "",0
                P: "Height", "int", "Integer", "",0
                P: "Path", "KString", "XRefUrl", "", ""
                P: "StartFrame", "int", "Integer", "",0
                P: "StopFrame", "int", "Integer", "",0
                P: "PlaySpeed", "double", "Number", "",0
                P: "Offset", "KTime", "Time", "",0
                P: "InterlaceMode", "enum", "", "",0
                P: "FreeRunning", "bool", "", "",0
                P: "Loop", "bool", "", "",0
                P: "AccessMode", "enum", "", "",0
            }
        }
    }
""")

#--------------------------------------------------------------------
#   Object properties
#--------------------------------------------------------------------

def writeObjectProps(fp, rmeshes, amt):

    for rmesh in rmeshes:
        mat = rmesh.material
        writeMaterial(fp, rmesh, amt)
        writeTexture(fp, mat.diffuseTexture, "DiffuseColor")
        writeTexture(fp, mat.specularMapTexture, "SpecularFactor")
        writeTexture(fp, mat.normalMapTexture, "Bump")
        writeTexture(fp, mat.transparencyMapTexture, "TransparencyFactor")
        writeTexture(fp, mat.bumpMapTexture, "BumpFactor")
        writeTexture(fp, mat.displacementMapTexture, "DisplacementFactor")


def writeMaterial(fp, rmesh, amt):
    name = getRmeshName(rmesh, amt)
    id,key = getId("Material::"+name)
    fp.write('    Material: %d, "%s", "" {' % (id, key))

    mat = rmesh.material
    fp.write(
'        Version: 102\n' +
'        ShadingModel: "phong"\n' +
'        MultiLayer: 0\n' +
'        Properties70:  {\n' +
'            P: "TransparentColor", "Color", "", "A",%.4f,%.4f,%.4f\n' % tuple(3*[1.0 - mat.opacity]) +
'            P: "TransparencyFactor", "Number", "", "A",%.4f\n' % mat.transparencyMapIntensity +
#'            P: "SpecularColor", "Color", "", "A",%.4f,%.4f,%.4f\n' % mat.specularColor.asTuple() +
#'            P: "ShininessExponent", "Number", "", "A",%.4f\n' % mat.shininess +
#'            P: "EmissiveColor", "Vector3D", "Vector", "",%.4f,%.4f,%.4f\n' % emissiveColor.asTuple() +
#'            P: "AmbientColor", "Vector3D", "Vector", "",%.4f,%.4f,%.4f\n' % ambientColor.asTuple() +
'            P: "DiffuseColor", "Vector3D", "Vector", "",%.4f,%.4f,%.4f\n' % mat.diffuseColor.asTuple() +
'            P: "DiffuseFactor", "Number", "", "A",%.4f\n' % 1.0 +
'            P: "SpecularColor", "Vector3D", "Vector", "",%.4f,%.4f,%.4f\n' % mat.specularColor.asTuple() +
'            P: "SpecularFactor", "Number", "", "A",%.4f\n' % mat.specularMapIntensity +
'            P: "Shininess", "double", "Number", "",%.4f\n' % mat.shininess +
'            P: "Reflectivity", "double", "Number", "",0\n' +
'        }\n' +
'    }\n')


def writeTexture(fp, filepath, channel):
    if not filepath:
        return
    filepath,tex = getTexturePath(filepath)
    relpath = getRelativePath(filepath)

    vid,vkey = getId("Video::%s" % tex)

    fp.write(
'    Video: %d, "%s", "Clip" {\n' % (vid, vkey) +
'        Type: "Clip"\n' +
'        Properties70:  {\n' +
'            P: "Path", "KString", "XRefUrl", "", "%s"\n' % filepath +
'        }\n' +
'        UseMipMap: 0\n' +
'        Filename: "%s"\n' % filepath +
'        RelativeFilename: "%s"\n' % relpath +
'    }\n')

    tid,tkey = getId("Texture::%s" % tex)

    fp.write(
'    Texture: %d, "%s", "" {\n' % (tid, tkey) +
'        Type: "TextureVideoClip"\n' +
'        Version: 202\n' +
'        TextureName: "%s"\n' % tkey +
'        Properties70:  {\n' +
'            P: "MHName", "KString", "", "", "%s"\n' % tkey +
'        }\n' +
'        Media: "%s"\n' % vkey +
'        Filename: "%s"\n' % filepath +
'        RelativeFilename: "%s"\n' % relpath +
'        ModelUVTranslation: 0,0\n' +
'        ModelUVScaling: 1,1\n' +
'        Texture_Alpha_Source: "None"\n' +
'        Cropping: 0,0,0,0\n' +
'    }\n')


#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def writeLinks(fp, rmeshes, amt):

    for rmesh in rmeshes:
        name = getRmeshName(rmesh, amt)
        ooLink(fp, 'Material::%s' % name, 'Model::%sMesh' % name)

        mat = rmesh.material
        for filepath,channel in [
            (mat.diffuseTexture, "DiffuseColor"),
            (mat.diffuseTexture, "TransparencyFactor"),
            (mat.specularMapTexture, "SpecularIntensity"),
            (mat.normalMapTexture, "Bump"),
            (mat.transparencyMapTexture, "TransparencyFactor"),
            (mat.bumpMapTexture, "BumpFactor"),
            (mat.displacementMapTexture, "Displacement")]:
            if filepath:
                _,tex = getTexturePath(filepath)
                opLink(fp, 'Texture::%s' % tex, 'Material::%s' % name, channel)
                ooLink(fp, 'Video::%s' % tex, 'Texture::%s' % tex)

