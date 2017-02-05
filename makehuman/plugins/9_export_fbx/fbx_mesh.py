#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson, Jonas Hauquier

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


def writeObjectDefs(fp, meshes, nShapes, config):
    nMeshes = len(meshes)

    properties = [
        ("Color",   "p_color_rgb",      [0.8,0.8,0.8]),
        ("BBoxMin", "p_vector_3d",      [0,0,0]),
        ("BBoxMax", "p_vector_3d",      [0,0,0]),
        ("Primary Visibility", "p_bool", True),
        ("Casts Shadows", "p_bool",     True),
        ("Receive Shadows", "p_bool",   True)
    ]

    if config.binary:
        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, 'Definitions')
        fbx_binary.fbx_template_generate(elem, "Geometry", (nMeshes + nShapes), "FbxMesh", properties)
        return

    import fbx_utils
    fp.write(
'    ObjectType: "Geometry" {\n' +
'       Count: %d' % (nMeshes + nShapes) +
"""
        PropertyTemplate: "FbxMesh" {
            Properties70:  {
""" + fbx_utils.get_ascii_properties(properties, indent=4) + """
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
        writeMeshProp(fp, mesh, config)


def writeGeometryProp(fp, mesh, config):
    id,key = getId("Geometry::%s" % mesh.name)
    nVerts = len(mesh.coord)
    nFaces = len(mesh.fvert)

    coord = mesh.coord + config.offset

    properties = [
        ("MHName", "p_string", "%sMesh" % mesh.name, False, True)
    ]

    if config.binary:
        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, 'Objects')
        fbx_binary.fbx_data_mesh_element(elem, key, id, properties, coord, mesh.fvert, mesh.vnorm, mesh.texco, mesh.fuvs)
        return

    vertString = ",".join( ["%.4f,%.4f,%.4f" % tuple(co) for co in coord] )
    if mesh.vertsPerPrimitive == 4:
        indexString = ",".join( ['%d,%d,%d,%d' % (fv[0],fv[1],fv[2],-1-fv[3]) for fv in mesh.fvert] )
    else:
        indexString = ",".join( ['%d,%d,%d' % (fv[0],fv[1],-1-fv[2]) for fv in mesh.fvert] )

    import fbx_utils
    fp.write(
        '    Geometry: %d, "%s", "Mesh" {\n' % (id, key) +
        '        Properties70:  {\n' +
        fbx_utils.get_ascii_properties(properties, indent=4) + '\n' +
        '        }\n' +
        '        Vertices: *%d {\n' % (3*nVerts) +
        '            a: %s\n' % vertString +
        '        } \n' +
        '        PolygonVertexIndex: *%d {\n' % (mesh.vertsPerPrimitive*nFaces) +
        '            a: %s\n' % indexString +
        '        } \n')

    # Must use normals for shapekeys
    nNormals = len(mesh.vnorm)
    normalString = ",".join( ["%.4f,%.4f,%.4f" % tuple(no) for no in mesh.vnorm] )
    if mesh.vertsPerPrimitive == 4:
        normalIndexString = ",".join( ['%d,%d,%d,%d' % (fv[0],fv[1],fv[2],fv[3]) for fv in mesh.fvert] )
    else:
        normalIndexString = ",".join( ['%d,%d,%d' % (fv[0],fv[1],fv[2]) for fv in mesh.fvert] )

    fp.write(
        '        GeometryVersion: 124\n' +
        '        LayerElementNormal: 0 {\n' +
        '            Version: 101\n' +
        '            Name: "%s_Normal"\n' % mesh.name +
        '            MappingInformationType: "ByPolygonVertex"\n' +
        '            ReferenceInformationType: "IndexToDirect"\n' +
        '            Normals: *%d {\n' % (3*nNormals) +
        '                a: %s\n' % normalString +
        '            }\n' +
        '            NormalsIndex: *%d {\n' % (mesh.vertsPerPrimitive*len(mesh.fvert)) +
        '                a: %s\n' % normalIndexString +
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
                Type: "LayerElementUV"
                TypedIndex: 0
            }
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

    uvString = ",".join( ["%.4f,%.4f" % tuple(uv) for uv in mesh.texco] )
    indexString = ",".join( ['%d,%d,%d,%d' % tuple(fuv) for fuv in mesh.fuvs] )

    fp.write(
        '        LayerElementUV: 0 {\n' +
        '            Version: 101\n' +
        '            Name: "%s_UV"\n' % mesh.name +
        '            MappingInformationType: "ByPolygonVertex"\n' +
        '            ReferenceInformationType: "IndexToDirect"\n' +
        '            UV: *%d {\n' % (2*nUvVerts) +
        '                a: %s\n' % uvString +
        '            } \n'
        '            UVIndex: *%d {\n' % (4*nUvFaces) +
        '                a: %s\n' % indexString +
        '            }\n' +
        '        }\n')


def writeUvs2(fp, mesh):
    nUvVerts = len(mesh.texco)
    nUvFaces = len(mesh.fuvs)

    uvString = list()
    for fuv in mesh.fuvs:
        uvString.append(",".join( ['%.4f,%.4f' % (tuple(mesh.texco[vt])) for vt in fuv] ))
    uvString = ",".join(uvString)
    if mesh.vertsPerPrimitive == 4:
        indexString = ",".join( ['%d,%d,%d,%d' % (4*n,4*n+1,4*n+2,4*n+3) for n in xrange(nUvFaces)] )
    else:
        indexString = ",".join( ['%d,%d,%d' % (4*n,4*n+1,4*n+2) for n in xrange(nUvFaces)] )

    fp.write(
        '        LayerElementUV: 0 {\n' +
        '            Version: 101\n' +
        '            Name: "%s_UV"\n' % mesh.name +
        '            MappingInformationType: "ByPolygonVertex"\n' +
        '            ReferenceInformationType: "IndexToDirect"\n' +
        '            UV: *%d {\n' % (2*mesh.vertsPerPrimitive*nUvFaces) +
        '                a: %s\n' % uvString[:-1] +
        '            } \n'
        '            UVIndex: *%d {\n' % (mesh.vertsPerPrimitive*nUvFaces) +
        '                a: %s\n' % indexString +
        '            }\n' +
        '        }\n')


#--------------------------------------------------------------------
#
#--------------------------------------------------------------------

def writeMeshProp(fp, mesh, config):
    id,key = getId("Model::%sMesh" % mesh.name)

    properties = [
        ("RotationActive", "p_bool", 1),
        ("InheritType", "p_enum", 1),
        ("ScalingMax", "p_vector_3d", [0,0,0]),
        ("DefaultAttributeIndex", "p_integer", 0),
        ("MHName", "p_string", mesh.name, False, True)
    ]

    if config.binary:
        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, 'Objects')
        fbx_binary.fbx_data_model_element(elem, key, id, properties)
        return

    import fbx_utils
    fp.write(
'    Model: %d, "%s", "Mesh" {' % (id, key) +
"""
        Version: 232
        Properties70:  {
""" + fbx_utils.get_ascii_properties(properties, indent=4) + """
        }
        Shading: Y
        Culling: "CullingOff"
    }
""")

#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def writeLinks(fp, meshes, config):
    for mesh in meshes:
        ooLink(fp, 'Model::%sMesh' % mesh.name, 'Model::RootNode', config)
        #if skel:
        #    ooLink(fp, 'Model::%sMesh' % name, 'Model::%s' % skel.name)
        ooLink(fp, 'Geometry::%s' % mesh.name, 'Model::%sMesh' % mesh.name, config)


