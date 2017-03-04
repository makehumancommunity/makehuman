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

import transformations as tm

from .fbx_utils import *

#--------------------------------------------------------------------
#   Object definitions
#--------------------------------------------------------------------

def getObjectCounts(meshes):
    """
    Count the total number of vertex groups and shapes required for all
    specified meshes.
    """
    nVertexGroups = 0
    for mesh in meshes:
        if mesh.vertexWeights is None:
            continue
        for weights in mesh.vertexWeights.data:
            if weights:
                nVertexGroups += 1

    nShapes = 0
    for mesh in meshes:
        if hasattr(mesh, 'shapes') and mesh.shapes is not None:
            for key,shape in mesh.shapes:
                if shape:
                    nShapes += 1

    return nVertexGroups, nShapes

def countObjects(meshes, skel):
    """
    Count the total number of vertex groups and shapes combined, as required
    for all specified meshes. If no skeleton rig is attached to the mesh, no
    vertex groups for bone weights are required.
    """
    nVertexGroups, nShapes = getObjectCounts(meshes)
    if skel:
        return (nVertexGroups + 1 + 2*nShapes)
    else:
        return 2*nShapes


def writeObjectDefs(fp, meshes, skel, config):
    nVertexGroups, nShapes = getObjectCounts(meshes)
    count = countObjects(meshes, skel)

    if config.binary:
        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, 'Definitions')
        if count > 0:
            fbx_binary.fbx_template_generate(elem, "Deformer", count)
        if skel:
            fbx_binary.fbx_template_generate(elem, "Pose", 1)
        return

    if count > 0:
        fp.write(
'    ObjectType: "Deformer" {\n' +
'       Count: %d' % count +
"""
    }
""")

    if skel:
        fp.write("""
    ObjectType: "Pose" {
        Count: 1
    }
""")


#--------------------------------------------------------------------
#   Object properties
#--------------------------------------------------------------------

def writeObjectProps(fp, meshes, skel, config):
    if skel:
        writeBindPose(fp, meshes, skel, config)

        for mesh in meshes:
            writeDeformer(fp, mesh.name, config)
            for bone in skel.getBones():
                try:
                    weights = mesh.vertexWeights.data[bone.name]
                except KeyError:
                    continue
                writeSubDeformer(fp, mesh.name, bone, weights, config)

    for mesh in meshes:
        # TODO support binary FBX shapekey export
        if hasattr(mesh, 'shapes') and mesh.shapes is not None:
            for sname,shape in mesh.shapes:
                writeShapeGeometry(fp, mesh.name, sname, shape, config)
                writeShapeDeformer(fp, mesh.name, sname)
                writeShapeSubDeformer(fp, mesh.name, sname)


def writeShapeGeometry(fp, name, sname, shape, config):
        id,key = getId("Geometry::%s_%sShape" % (name, sname))
        nVerts = len(shape.verts)
        fp.write(
            '    Geometry: %d, "%s", "Shape" {\n' % (id, key) +
            '        version: 100\n' +
            '        Indexes: *%d   {\n' % nVerts +
            '            a: ')

        string = "".join( ['%d,' % vn for vn in shape.verts] )
        fp.write(string[:-1])

        fp.write('\n' +
            '        }\n' +
            '        Vertices: *%d   {\n' % (3*nVerts) +
            '            a: ')

        target = config.scale * shape.data + config.offset
        string = "".join( ["%.4f,%.4f,%.4f," % tuple(dr) for dr in target] )
        fp.write(string[:-1])

        # Must use normals for shapekeys
        fp.write('\n' +
            '        }\n' +
            '        Normals: *%d {\n' % (3*nVerts) +
            '            a: ')

        string = nVerts * "0,0,0,"
        fp.write(string[:-1])

        fp.write('\n' +
            '        }\n' +
            '    }\n')


def writeShapeDeformer(fp, name, sname):
    id,key = getId("Deformer::%s_%sShape" % (name, sname))
    fp.write(
        '    Deformer: %d, "%s", "BlendShape" {\n' % (id, key) +
        '        Version: 100\n' +
        '    }\n')


def writeShapeSubDeformer(fp, name, sname, shape):
    sid,skey = getId("SubDeformer::%s_%sShape" % (name, sname))
    fp.write(
        '    Deformer: %d, "%s", "BlendShapeChannel" {' % (sid, skey) +
"""
        version: 100
        deformpercent: 0.0
        FullWeights: *1   {
            a: 100
        }
    }
""")


def writeDeformer(fp, name, config):
    id,key = getId("Deformer::%s" % name)

    properties = [
        ("MHName", "p_string", "%sSkin" % name, False, True)
    ]

    if config.binary:
        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, 'Objects')
        fbx_binary.fbx_data_deformer(elem, key, id, properties)
        return

    import fbx_utils

    fp.write(
'    Deformer: %d, "%s", "Skin" {' % (id, key) +
"""
        Version: 101
        Properties70:  {
""" + fbx_utils.get_ascii_properties(properties, indent=3) + """
        }
        Link_DeformAcuracy: 50
    }
""")


def writeSubDeformer(fp, name, bone, weights, config):
    id,key = getId("SubDeformer::%s_%s" % (bone.name, name))

    bindmat,bindinv = bone.getBindMatrix(config.offset)

    if config.binary:
        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, 'Objects')
        fbx_binary.fbx_data_subdeformer(elem, key, id, weights[0], weights[1], bindmat, bindinv)
        return

    nVertexWeights = len(weights[0])
    indexString = ','.join(["%d" % vn for vn in weights[0]])
    weightString = ','.join(["%4f" % w for w in weights[1]])

    fp.write(
        '    Deformer: %d, "%s", "Cluster" {\n' % (id, key) +
        '        Version: 100\n' +
        '        UserData: "", ""\n' +
        '        Indexes: *%d {\n' % nVertexWeights +
        '            a: %s\n' % indexString +
        '        } \n' +
        '        Weights: *%d {\n' % nVertexWeights +
        '            a: %s\n' % weightString +
        '        }\n')

    writeMatrix(fp, 'Transform', bindmat)
    writeMatrix(fp, 'TransformLink', bindinv)
    fp.write('    }\n')


def writeBindPose(fp, meshes, skel, config):
    id,key = getId("Pose::" + skel.name)
    nBones = skel.getBoneCount()
    nMeshes = len(meshes)

    # Skeleton bind matrix
    skelbindmat = tm.rotation_matrix(math.pi/2, (1,0,0))

    count = 1 + nMeshes + nBones

    if config.binary:
        from . import fbx_binary
        elem = fbx_binary.get_child_element(fp, 'Objects')
        pelem = fbx_binary.fbx_data_bindpose_element(elem, key, id, count)
    else:
        fp.write(
            '    Pose: %d, "%s", "BindPose" {\n' % (id, key)+
            '        Type: "BindPose"\n' +
            '        Version: 100\n' +
            '        NbPoseNodes: %d\n' % count)

    startLinking()

    key = "Model::%s" % skel.name
    if config.binary:
        id,_ = getId(key)
        fbx_binary.fbx_data_pose_node_element(pelem, key, id, skelbindmat)
    else:
        poseNode(fp, key, skelbindmat)

    for mesh in meshes:
        key = "Model::%sMesh" % mesh.name
        if config.binary:
            id,_ = getId(key)
            fbx_binary.fbx_data_pose_node_element(pelem, key, id, skelbindmat)
        else:
            poseNode(fp, key, skelbindmat)

    for bone in skel.getBones():
        key = "Model::%s" % bone.name
        bindmat,_ = bone.getBindMatrix(config.offset)
        if config.binary:
            id,_ = getId(key)
            fbx_binary.fbx_data_pose_node_element(pelem, key, id, bindmat)
        else:
            poseNode(fp, key, bindmat)

    stopLinking()

    if not config.binary:
        fp.write('    }\n')


def poseNode(fp, key, matrix):
    pid,_ = getId(key)
    matrix[:3,3] = 0
    fp.write(
'        PoseNode:  {\n' +
'            Node: %d\n' % pid)
    writeMatrix(fp, 'Matrix', matrix, "    ")
    fp.write('        }\n')

#--------------------------------------------------------------------
#   Links
#--------------------------------------------------------------------

def writeLinks(fp, meshes, skel, config):

    if skel:
        for mesh in meshes:
            ooLink(fp, 'Deformer::%s' % mesh.name, 'Geometry::%s' % mesh.name, config)
            for bone in skel.getBones():
                subdef = 'SubDeformer::%s_%s' % (bone.name, mesh.name)
                try:
                    getId(subdef)
                except NameError:
                    continue
                ooLink(fp, subdef, 'Deformer::%s' % mesh.name, config)
                ooLink(fp, 'Model::%s' % bone.name, subdef, config)

    for mesh in meshes:
        if hasattr(mesh, 'shapes') and mesh.shapes is not None:
            for sname, shape in mesh.shapes:
                deform = "Deformer::%s_%sShape" % (mesh.name, sname)
                subdef = "SubDeformer::%s_%sShape" % (mesh.name, sname)
                ooLink(fp, "Geometry::%s_%sShape" % (mesh.name, sname), subdef)
                ooLink(fp, subdef, deform)
                ooLink(fp, deform, "Geometry::%s" % mesh.name)


