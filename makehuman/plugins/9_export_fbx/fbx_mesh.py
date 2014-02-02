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
Fbx mesh
"""

from .fbx_utils import *

#--------------------------------------------------------------------
#   Object definitions
#--------------------------------------------------------------------

def countObjects(rmeshes, amt):
    nMeshes = len(rmeshes)
    return (nMeshes + 1)


def writeObjectDefs(fp, rmeshes, amt, nShapes):
    nMeshes = len(rmeshes)

    fp.write(
'    ObjectType: "Geometry" {\n' +
'       Count: %d' % (nMeshes + nShapes) +
"""
        PropertyTemplate: "FbxMesh" {
            Properties70:  {
                P: "Color", "ColorRGB", "Color", "",0.8,0.8,0.8
                P: "BBoxMin", "Vector3D", "Vector", "",0,0,0
                P: "BBoxMax", "Vector3D", "Vector", "",0,0,0
                P: "Primary Visibility", "bool", "", "",1
                P: "Casts Shadows", "bool", "", "",1
                P: "Receive Shadows", "bool", "", "",1
            }
        }
    }
""")

#--------------------------------------------------------------------
#   Object properties
#--------------------------------------------------------------------

def writeObjectProps(fp, rmeshes, amt, config):
    for rmesh in rmeshes:
        name = getRmeshName(rmesh, amt)
        obj = rmesh.object
        writeGeometryProp(fp, name, obj, config)
        writeMeshProp(fp, name, obj)


def writeGeometryProp(fp, name, obj, config):
    id,key = getId("Geometry::%s" % name)
    nVerts = len(obj.coord)
    nFaces = len(obj.fvert)

    fp.write(
'    Geometry: %d, "%s", "Mesh" {\n' % (id, key) +
'        Properties70:  {\n' +
'            P: "MHName", "KString", "", "", "%sMesh"\n' % name +
'        }\n' +
'        Vertices: *%d {\n' % (3*nVerts) +
'            a: ')

    coord = obj.coord - config.scale*config.offset
    string = "".join( ["%.4f,%.4f,%.4f," % tuple(co) for co in coord] )
    fp.write(string[:-1])

    fp.write('\n' +
'        } \n' +
'        PolygonVertexIndex: *%d {\n' % (4*nFaces) +
'            a: ')

    string = "".join( ['%d,%d,%d,%d,' % (fv[0],fv[1],fv[2],-1-fv[3]) for fv in obj.fvert] )
    fp.write(string[:-1])
    fp.write('\n' +
'        } \n')

    # Must use normals for shapekeys
    obj.calcNormals()
    nNormals = len(obj.vnorm)
    fp.write(
"""
        GeometryVersion: 124
        LayerElementNormal: 0 {
            Version: 101
            Name: ""
            MappingInformationType: "ByPolygonVertex"
            ReferenceInformationType: "IndexToDirect"
""" +
'            Normals: *%d {\n' % (3*nNormals) +
'                a: ')

    string = "".join( ["%.4f,%.4f,%.4f," % tuple(no) for no in obj.vnorm] )
    fp.write(string[:-1])
    fp.write('\n' +
'            } \n')

    fp.write('        } \n')

    writeUvs2(fp, obj)

    fp.write(
"""
        LayerElementMaterial: 0 {
            Version: 101
            Name: "Dummy"
            MappingInformationType: "AllSame"
            ReferenceInformationType: "IndexToDirect"
            Materials: *1 {
                a: 0
            }
        }
        LayerElementTexture: 0 {
            MappingInformationType: "ByPolygonVertex"
            ReferenceInformationType: "IndexToDirect"
            BlendMode: "Translucent"
            Name: "Dummy"
            Version: 101
            TextureAlpha: 1.0
        }
        Layer: 0 {
            Version: 100
            LayerElement:  {
                Type: "LayerElementNormal"
                TypedIndex: 0
            }
            LayerElement:  {
                Type: "LayerElementMaterial"
                TypedIndex: 0
            }
            LayerElement:  {
                Type: "LayerElementTexture"
                TypedIndex: 0
            }
""")
    if config.useNormals:
        fp.write(
"""
            LayerElement:  {
                Type: "LayerElementNormal"
                TypedIndex: 0
            }
""")
    fp.write(
"""
            LayerElement:  {
                Type: "LayerElementUV"
                TypedIndex: 0
            }
        }
    }
""")

#--------------------------------------------------------------------
#   Two different ways to write UVs
#   First method leads to crash in AD FBX converter
#--------------------------------------------------------------------

def writeUvs1(fp, obj):
    nUvVerts = len(obj.texco)
    nUvFaces = len(obj.fuvs)

    fp.write(
"""
        LayerElementUV: 0 {
            Version: 101
            Name: ""
            MappingInformationType: "ByPolygonVertex"
            ReferenceInformationType: "IndexToDirect"
""")

    fp.write(
'            UV: *%d {\n' % (2*nUvVerts) +
'                a: ')

    string = "".join( ["%.4f,%.4f," % tuple(uv) for uv in obj.texco] )
    fp.write(string[:-1])

    fp.write('\n' +
'            } \n'
'            UVIndex: *%d {\n' % (4*nUvFaces) +
'                a: ')

    string = "".join( ['%d,%d,%d,%d,' % tuple(fuv) for fuv in obj.fuvs] )
    fp.write(string[:-1])

    fp.write(
"""
            }
        }
""")


def writeUvs2(fp, obj):
    nUvVerts = len(obj.texco)
    nUvFaces = len(obj.fuvs)

    fp.write(
"""
        LayerElementUV: 0 {
            Version: 101
            Name: ""
            MappingInformationType: "ByPolygonVertex"
            ReferenceInformationType: "IndexToDirect"
""")
    fp.write(
'            UV: *%d {\n' % (8*nUvFaces) +
'                a: ')

    string = ""
    for fuv in obj.fuvs:
        string += "".join( ['%.4f,%.4f,' % (tuple(obj.texco[vt])) for vt in fuv] )
    fp.write(string[:-1])

    fp.write('\n' +
'            } \n'
'            UVIndex: *%d {\n' % (4*nUvFaces) +
'                a: ')

    string = "".join( ['%d,%d,%d,%d,' % (4*n,4*n+1,4*n+2,4*n+3) for n in range(nUvFaces)] )
    fp.write(string[:-1])

    fp.write(
"""
            }
        }
""")


#--------------------------------------------------------------------
#
#--------------------------------------------------------------------

def writeMeshProp(fp, name, obj):
    id,key = getId("Model::%sMesh" % name)
    fp.write(
'    Model: %d, "%s", "Mesh" {' % (id, key) +
"""
        Version: 232
        Properties70:  {
            P: "RotationActive", "bool", "", "",1
            P: "InheritType", "enum", "", "",1
            P: "ScalingMax", "Vector3D", "Vector", "",0,0,0
            P: "DefaultAttributeIndex", "int", "Integer", "",0
""" +
'            P: "MHName", "KString", "", "", "%s"' % name +
"""
        }
        Shading: Y
        Culling: "CullingOff"
    }
""")

#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def writeLinks(fp, rmeshes, amt):
    for rmesh in rmeshes:
        name = getRmeshName(rmesh, amt)
        ooLink(fp, 'Model::%sMesh' % name, 'Model::RootNode')
        #if amt:
        #    ooLink(fp, 'Model::%sMesh' % name, 'Model::%s' % amt.name)
        ooLink(fp, 'Geometry::%s' % name, 'Model::%sMesh' % name)


