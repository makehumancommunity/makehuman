#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (http://www.makehuman.org/doc/node/the_makehuman_application.html)

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

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------
Fbx mesh
"""

from .fbx_utils import *

#--------------------------------------------------------------------
#   Object definitions
#--------------------------------------------------------------------

def countObjects(meshes):
    """
    Number of mesh objects required for exporting the specified meshes.
    """
    nMeshes = len(meshes)
    return (nMeshes + 1)


def writeObjectDefs(fp, meshes, nShapes):
    nMeshes = len(meshes)

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

def writeObjectProps(fp, meshes, config):
    for mesh in meshes:
        writeGeometryProp(fp, mesh, config)
        writeMeshProp(fp, mesh)


def writeGeometryProp(fp, mesh, config):
    id,key = getId("Geometry::%s" % mesh.name)
    nVerts = len(mesh.coord)
    nFaces = len(mesh.fvert)

    fp.write(
'    Geometry: %d, "%s", "Mesh" {\n' % (id, key) +
'        Properties70:  {\n' +
'            P: "MHName", "KString", "", "", "%sMesh"\n' % mesh.name +
'        }\n' +
'        Vertices: *%d {\n' % (3*nVerts) +
'            a: ')

    coord = mesh.coord + config.offset
    string = "".join( ["%.4f,%.4f,%.4f," % tuple(co) for co in coord] )
    fp.write(string[:-1])

    fp.write('\n' +
'        } \n' +
'        PolygonVertexIndex: *%d {\n' % (4*nFaces) +
'            a: ')

    string = "".join( ['%d,%d,%d,%d,' % (fv[0],fv[1],fv[2],-1-fv[3]) for fv in mesh.fvert] )
    fp.write(string[:-1])
    fp.write('\n' +
'        } \n')

    # Must use normals for shapekeys
    nNormals = len(mesh.vnorm)
    fp.write(
"""
        GeometryVersion: 124
        LayerElementNormal: 0 {
            Version: 101
"""
'            Name: "%s_Normal"' % mesh.name +
"""
            MappingInformationType: "ByPolygonVertex"
            ReferenceInformationType: "IndexToDirect"
""" +
'            Normals: *%d {\n' % (3*nNormals) +
'                a: ')

    string = "".join( ["%.4f,%.4f,%.4f," % tuple(no) for no in mesh.vnorm] )
    fp.write(string[:-1])

    fp.write('\n' +
'            }\n' +
'            NormalsIndex: *%d {\n' % (4*len(mesh.fvert)) +
'                a: ')

    string = "".join( ['%d,%d,%d,%d,' % (fv[0],fv[1],fv[2],fv[3]) for fv in mesh.fvert] )
    fp.write(string[:-1])

    fp.write('\n' +
'            } \n')

    fp.write('        } \n')

    writeUvs2(fp, mesh)

    fp.write(
"""
        LayerElementMaterial: 0 {
            Version: 101
""" +
'            Name: "%s_Material"' % mesh.name +
"""
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
""" +
'            Name: "%s_Texture"' % mesh.name +
"""
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
            LayerElement:  {
                Type: "LayerElementNormal"
                TypedIndex: 0
            }
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

def writeUvs1(fp, mesh):
    nUvVerts = len(mesh.texco)
    nUvFaces = len(mesh.fuvs)

    fp.write(
        '        LayerElementUV: 0 {\n' +
        '            Version: 101\n' +
        '            Name: "%s_UV"\n' % mesh.name +
        '            MappingInformationType: "ByPolygonVertex"\n' +
        '            ReferenceInformationType: "IndexToDirect"\n' +
        '            UV: *%d {\n' % (2*nUvVerts) +
        '                a: ')

    string = "".join( ["%.4f,%.4f," % tuple(uv) for uv in mesh.texco] )
    fp.write(string[:-1])

    fp.write('\n' +
        '            } \n'
        '            UVIndex: *%d {\n' % (4*nUvFaces) +
        '                a: ')

    string = "".join( ['%d,%d,%d,%d,' % tuple(fuv) for fuv in mesh.fuvs] )
    fp.write(string[:-1])

    fp.write('\n' +
        '            }\n' +
        '        }\n')


def writeUvs2(fp, mesh):
    nUvVerts = len(mesh.texco)
    nUvFaces = len(mesh.fuvs)

    fp.write(
        '        LayerElementUV: 0 {\n' +
        '            Version: 101\n' +
        '            Name: "%s_UV"\n' % mesh.name +
        '            MappingInformationType: "ByPolygonVertex"\n' +
        '            ReferenceInformationType: "IndexToDirect"\n' +
        '            UV: *%d {\n' % (8*nUvFaces) +
        '                a: ')

    string = ""
    for fuv in mesh.fuvs:
        string += "".join( ['%.4f,%.4f,' % (tuple(mesh.texco[vt])) for vt in fuv] )
    fp.write(string[:-1])

    fp.write('\n' +
        '            } \n'
        '            UVIndex: *%d {\n' % (4*nUvFaces) +
        '                a: ')

    string = "".join( ['%d,%d,%d,%d,' % (4*n,4*n+1,4*n+2,4*n+3) for n in range(nUvFaces)] )
    fp.write(string[:-1])

    fp.write('\n' +
        '            }\n' +
        '        }\n')


#--------------------------------------------------------------------
#
#--------------------------------------------------------------------

def writeMeshProp(fp, mesh):
    id,key = getId("Model::%sMesh" % mesh.name)
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
'            P: "MHName", "KString", "", "", "%s"' % mesh.name +
"""
        }
        Shading: Y
        Culling: "CullingOff"
    }
""")

#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def writeLinks(fp, meshes):
    for mesh in meshes:
        ooLink(fp, 'Model::%sMesh' % mesh.name, 'Model::RootNode')
        #if skel:
        #    ooLink(fp, 'Model::%sMesh' % name, 'Model::%s' % skel.name)
        ooLink(fp, 'Geometry::%s' % mesh.name, 'Model::%sMesh' % mesh.name)


