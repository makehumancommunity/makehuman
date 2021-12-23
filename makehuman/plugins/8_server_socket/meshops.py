#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import pprint
import math
import numpy as np
import time

from transformations import quaternion_from_matrix
from .abstractop import AbstractOp
from core import G
from material import getSkinBlender

pp = pprint.PrettyPrinter(indent=4)

class SocketMeshOps(AbstractOp):

    def __init__(self, sockettaskview):
        super().__init__(sockettaskview)

        # Sync operations
        self.functions["getCoord"] = self.getCoord
        self.functions["getPose"] = self.getPose

        # Import body operations
        self.functions["getBodyFacesBinary"] = self.getBodyFacesBinary
        self.functions["getBodyMaterialInfo"] = self.getBodyMaterialInfo
        self.functions["getBodyMeshInfo"] = self.getBodyMeshInfo
        self.functions["getBodyVerticesBinary"] = self.getBodyVerticesBinary
        self.functions["getBodyTextureCoordsBinary"] = self.getBodyTextureCoordsBinary
        self.functions["getBodyFaceUVMappingsBinary"] = self.getBodyFaceUVMappingsBinary
        self.functions["getBodyWeightInfo"] = self.getBodyWeightInfo
        self.functions["getBodyWeightsVertList"] = self.getBodyWeightsVertList
        self.functions["getBodyWeights"] = self.getBodyWeights

        # Import proxy operations
        self.functions["getProxiesInfo"] = self.getProxiesInfo
        self.functions["getProxyFacesBinary"] = self.getProxyFacesBinary
        self.functions["getProxyMaterialInfo"] = self.getProxyMaterialInfo
        self.functions["getProxyVerticesBinary"] = self.getProxyVerticesBinary
        self.functions["getProxyTextureCoordsBinary"] = self.getProxyTextureCoordsBinary
        self.functions["getProxyFaceUVMappingsBinary"] = self.getProxyFaceUVMappingsBinary
        self.functions["getProxyWeightInfo"] = self.getProxyWeightInfo
        self.functions["getProxyWeightsVertList"] = self.getProxyWeightsVertList
        self.functions["getProxyWeights"] = self.getProxyWeights


        # Import skeleton operations
        self.functions["getSkeleton"] = self.getSkeleton

    def getCoord(self,conn,jsonCall):
        jsonCall.data = self.human.mesh.coord

    def getBodyVerticesBinary(self,conn,jsonCall):
        jsonCall.responseIsBinary = True
        coord = self._getBodyMesh().coord
        jsonCall.data = coord.tobytes()

    def _getProxyByUUID(self,strUuid):
        for p in self.api.mesh.getAllProxies(includeBodyProxy=True):
            if p.uuid == strUuid:
                return p
        return None

    def getProxiesInfo(self,conn,jsonCall):
        objects = []

        allProxies =self.api.mesh.getAllProxies(includeBodyProxy=False)

        if not self.human.proxy is None and not self.human.proxy.name is None:
            # print ("Proxy appended: " + self.human.proxy.name)
            allProxies.append(self.human.proxy)

        for p in allProxies:
            info = {}

            face_mask = []
            mesh =  p.object.getSeedMesh()

            # TODO: Figure out how to find hidden faces on clothes
            if p.type == "Proxymeshes":
                face_mask = self._boolsToRunLenghtIdx(self.human._Object__proxyMesh.face_mask)

            info["faceMask"] = face_mask
            info["type"] = p.type
            info["uuid"] = p.uuid
            info["name"] = p.name
            coord = mesh.coord
            shape = coord.shape
            info["numVertices"] = shape[0]
            info["verticesTypeCode"] = self.api.internals.numpyTypecodeToPythonTypeCode(coord.dtype.str)
            info["verticesBytesWhenPacked"] = coord.itemsize * coord.size
            faces = mesh.fvert
            shape = faces.shape
            info["numFaces"] = shape[0]
            info["facesTypeCode"] = self.api.internals.numpyTypecodeToPythonTypeCode(faces.dtype.str)
            info["facesBytesWhenPacked"] = faces.itemsize * faces.size
            objects.append(info)
            coord = mesh.texco
            shape = coord.shape
            info["numTextureCoords"] = shape[0]
            info["textureCoordsTypeCode"] = self.api.internals.numpyTypecodeToPythonTypeCode(coord.dtype.str)
            info["textureCoordsBytesWhenPacked"] = coord.itemsize * coord.size
            fuvs = mesh.fuvs
            shape = fuvs.shape
            info["numFaceUVMappings"] = shape[0]
            info["faceUVMappingsTypeCode"] = self.api.internals.numpyTypecodeToPythonTypeCode(fuvs.dtype.str)
            info["faceUVMappingsBytesWhenPacked"] = fuvs.itemsize * fuvs.size

        jsonCall.data = objects

    def getBodyFacesBinary(self,conn,jsonCall):
        jsonCall.responseIsBinary = True
        faces = self._getBodyMesh().fvert
        jsonCall.data = faces.tobytes()

    def getBodyMaterialInfo(self,conn,jsonCall):
        if self.human.material.name == 'XrayMaterial' and self.human._backUpMaterial:
            material = self.human._backUpMaterial
        else:
            material = self.human.material
        jsonCall.data = self.api.assets.materialToHash(material)

    def getBodyTextureCoordsBinary(self,conn,jsonCall):
        jsonCall.responseIsBinary = True
        texco = self._getBodyMesh().texco
        jsonCall.data = texco.tobytes()

    def getBodyFaceUVMappingsBinary(self,conn,jsonCall):
        jsonCall.responseIsBinary = True
        faces = self._getBodyMesh().fuvs
        jsonCall.data = faces.tobytes()

    def _getBodyMesh(self):
        return self.human._Object__seedMesh

    def _boolsToRunLenghtIdx(self, boolArray):
        out = []
        i = 0
        needNewRun = True

        while i < len(boolArray):
            if boolArray[i]:
                if needNewRun:
                    out.append([i,i])
                    needNewRun = False
                out[ len(out) - 1 ][1] = i
            else:
                needNewRun = True
            i = i + 1

        return out


    def getBodyMeshInfo(self,conn,jsonCall):
        jsonCall.data = {}

        filename = "untitled"

        if not G.app.currentFile.title is None:
            filename = G.app.currentFile.title

        name = G.app.selectedHuman.getName()
        if not name:
            name = filename

        jsonCall.data["name"] = name
        jsonCall.data["filename"] = filename

        mesh = self._getBodyMesh()

        face_mask = []
        if hasattr(mesh, "face_mask"):
            face_mask = self._boolsToRunLenghtIdx(mesh.face_mask)

        jsonCall.data["faceMask"] = face_mask

        coord = mesh.coord
        shape = coord.shape
        jsonCall.data["numVertices"] = shape[0]
        jsonCall.data["verticesTypeCode"] = coord.dtype.str
        jsonCall.data["verticesShape"] = coord.shape
        jsonCall.data["verticesBytesWhenPacked"] = coord.itemsize * coord.size

        faces = mesh.fvert
        shape = faces.shape

        jsonCall.data["numFaces"] = shape[0]
        jsonCall.data["facesTypeCode"] = faces.dtype.str
        jsonCall.data["facesShape"] = faces.shape
        jsonCall.data["facesBytesWhenPacked"] = faces.itemsize * faces.size

        faceGroupNames = []

        for fg in mesh.faceGroups:
            faceGroupNames.append(fg.name)

        jsonCall.data["faceGroups"] = self.api.mesh.getFaceGroupFaceIndexes()

        coord = mesh.texco
        shape = coord.shape
        jsonCall.data["numTextureCoords"] = shape[0]
        jsonCall.data["textureCoordsTypeCode"] = coord.dtype.str
        jsonCall.data["textureCoordsShape"] = shape
        jsonCall.data["textureCoordsBytesWhenPacked"] = coord.itemsize * coord.size

        fuvs = mesh.fuvs
        shape = fuvs.shape
        jsonCall.data["numFaceUVMappings"] = shape[0]
        jsonCall.data["faceUVMappingsTypeCode"] = fuvs.dtype.str
        jsonCall.data["faceUVMappingsShape"] = shape
        jsonCall.data["faceUVMappingsBytesWhenPacked"] = fuvs.itemsize * fuvs.size

        skin = getSkinBlender()
        skinColor = skin.getDiffuseColor()
        jsonCall.data["skinColor"] = skinColor.asTuple() + (1.0, )


    def _boneToHash(self, boneHierarchy, bone, recursionLevel=1):
        out = {}
        out["name"] = bone.name
        out["headPos"] = bone.headPos
        out["tailPos"] = bone.tailPos

        restMatrix = bone.matRestGlobal
        matrix = np.array((restMatrix[0], -restMatrix[2], restMatrix[1], restMatrix[3]))
        qw, qx, qy, qz = quaternion_from_matrix(matrix)
        if qw < 1e-4:
            roll = 0
        else:
            roll = math.pi - 2 * math.atan2(qy, qw)
        if roll < -math.pi:
            roll += 2 * math.pi
        elif roll > math.pi:
            roll -= 2 * math.pi

        out["matrix"] = [list(restMatrix[0,:]), list(restMatrix[1,:]), list(restMatrix[2,:]), list(restMatrix[3,:])]
        out["roll"] = roll

        out["children"] = []
        boneHierarchy.append(out)

        # Just a security measure.
        if recursionLevel < 30:
            for child in bone.children:
                self._boneToHash(out["children"], child, recursionLevel+1)

    def getSkeleton(self, conn, jsonCall):

        out = {}
        skeleton = self.human.getSkeleton()

        boneHierarchy = []

        yOffset = -1 * self.human.getJointPosition('ground')[1]
        out["offset"] = [0.0, 0.0, yOffset]

        if not skeleton is None:
            out["name"] = skeleton.name
            for bone in skeleton.roots:
                self._boneToHash(boneHierarchy, bone)
        else:
            out["name"] = "none"

        out["bones"] = boneHierarchy
        jsonCall.data = out

    def getBodyWeightInfo(self, conn, jsonCall):

        out = {}
        weightList = []

        skeleton = self.human.getSkeleton()
        rawWeights = self.human.getVertexWeights(skeleton)

        sumVerts = 0
        sumVertListBytes = 0
        sumWeightsBytes = 0

        boneKeys = list(rawWeights.data.keys())
        boneKeys.sort()

        for key in boneKeys:
            bw = {}
            bw["bone"] = key
            bw["numVertices"] = len(rawWeights.data[key][0])

            verts = rawWeights.data[key][0]
            weights = rawWeights.data[key][1]

            bw["vertListBytesWhenPacked"] = verts.itemsize * verts.size
            bw["weightsBytesWhenPacked"] = weights.itemsize * weights.size
            weightList.append(bw)

            sumVerts = sumVerts + bw["numVertices"]
            sumVertListBytes = sumVertListBytes + bw["vertListBytesWhenPacked"]
            sumWeightsBytes = sumWeightsBytes + bw["weightsBytesWhenPacked"]

        out["sumVerts"] = sumVerts
        out["sumVertListBytes"] = sumVertListBytes
        out["sumWeightsBytes"] = sumWeightsBytes
        out["weights"] = weightList

        jsonCall.data = out

    def getBodyWeightsVertList(self, conn, jsonCall):
        jsonCall.responseIsBinary = True

        skeleton = self.human.getSkeleton()
        rawWeights = self.human.getVertexWeights(skeleton)

        allVerts = None

        boneKeys = list(rawWeights.data.keys())
        boneKeys.sort()

        for key in boneKeys:

            if allVerts is None:
                allVerts = rawWeights.data[key][0]
            else:
                allVerts = np.append(allVerts, rawWeights.data[key][0])

        jsonCall.data = allVerts.tobytes()

    def getBodyWeights(self, conn, jsonCall):
        jsonCall.responseIsBinary = True

        skeleton = self.human.getSkeleton()
        rawWeights = self.human.getVertexWeights(skeleton)

        allVerts = None

        boneKeys = list(rawWeights.data.keys())
        boneKeys.sort()

        for key in boneKeys:

            if allVerts is None:
                allVerts = rawWeights.data[key][1]
            else:
                allVerts = np.append(allVerts, rawWeights.data[key][1])

        jsonCall.data = allVerts.tobytes()

    def getProxyWeightInfo(self, conn, jsonCall):

        out = {}
        weightList = []

        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        skeleton = self.human.getSkeleton()

        humanWeights = self.human.getVertexWeights(skeleton)
        rawWeights = proxy.getVertexWeights(humanWeights, skeleton, allowCache=True)

        #pp.pprint(rawWeights)
        #weights = mesh.getVertexWeights(pxySeedWeights)

        sumVerts = 0
        sumVertListBytes = 0
        sumWeightsBytes = 0

        boneKeys = list(rawWeights.data.keys())
        boneKeys.sort()

        for key in boneKeys:
            bw = {}
            bw["bone"] = key
            bw["numVertices"] = len(rawWeights.data[key][0])

            verts = rawWeights.data[key][0]
            weights = rawWeights.data[key][1]

            bw["vertListBytesWhenPacked"] = verts.itemsize * verts.size
            bw["weightsBytesWhenPacked"] = weights.itemsize * weights.size
            weightList.append(bw)

            sumVerts = sumVerts + bw["numVertices"]
            sumVertListBytes = sumVertListBytes + bw["vertListBytesWhenPacked"]
            sumWeightsBytes = sumWeightsBytes + bw["weightsBytesWhenPacked"]

        out["sumVerts"] = sumVerts
        out["sumVertListBytes"] = sumVertListBytes
        out["sumWeightsBytes"] = sumWeightsBytes
        out["weights"] = weightList

        jsonCall.data = out

    def getProxyWeightsVertList(self, conn, jsonCall):
        jsonCall.responseIsBinary = True

        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        skeleton = self.human.getSkeleton()

        humanWeights = self.human.getVertexWeights(skeleton)

        #start = int(round(time.time() * 1000))
        rawWeights = proxy.getVertexWeights(humanWeights, skeleton, allowCache=True)
        #stop = int(round(time.time() * 1000))
        #print("Calculating rawWeights for " + proxy.name + " took " + str(stop - start) + " milliseconds")

        allVerts = None

        boneKeys = list(rawWeights.data.keys())
        boneKeys.sort()

        for key in boneKeys:

            if allVerts is None:
                allVerts = rawWeights.data[key][0]
            else:
                allVerts = np.append(allVerts, rawWeights.data[key][0])

        jsonCall.data = allVerts.tobytes()

    def getProxyWeights(self, conn, jsonCall):
        jsonCall.responseIsBinary = True

        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        skeleton = self.human.getSkeleton()

        humanWeights = self.human.getVertexWeights(skeleton)

        #start = int(round(time.time() * 1000))
        rawWeights = proxy.getVertexWeights(humanWeights, skeleton, allowCache=True)
        #stop = int(round(time.time() * 1000))
        #print("Calculating rawWeights for " + proxy.name + " took " + str(stop - start) + " milliseconds")

        allVerts = None

        boneKeys = list(rawWeights.data.keys())
        boneKeys.sort()

        for key in boneKeys:

            if allVerts is None:
                allVerts = rawWeights.data[key][1]
            else:
                allVerts = np.append(allVerts, rawWeights.data[key][1])

        jsonCall.data = allVerts.tobytes()

    def getPose(self,conn,jsonCall):

        poseFilename = jsonCall.params.get("poseFilename") # use get, since might not be there
        
        if poseFilename is not None:
            filename, file_extension = os.path.splitext(poseFilename)
            if file_extension == ".mhpose":
                self.api.skeleton.setExpressionFromFile(poseFilename)
            if file_extension == ".bvh":
                self.api.skeleton.setPoseFromFile(poseFilename)

        self.parent.addMessage("Constructing dict with bone matrices.")
        
        skeleton = self.human.getSkeleton()
        skelobj = dict()

        bones = skeleton.getBones()
        
        for bone in bones:
            rmat = bone.getRestMatrix('zUpFaceNegY')
            skelobj[bone.name] = [ list(rmat[0,:]), list(rmat[1,:]), list(rmat[2,:]), list(rmat[3,:]) ]

        jsonCall.data = skelobj

    def _getProxyMesh(self, proxy):
        if proxy.type == "Proxymeshes":
            if not self.human.proxy is None and not self.human.proxy.name is None:
                return self.human._Object__proxyMesh
        return proxy.object.getSeedMesh()

    def getProxyVerticesBinary(self,conn,jsonCall):
        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        jsonCall.responseIsBinary = True
        coord = self._getProxyMesh(proxy).coord
        jsonCall.data = coord.tobytes()

    def getProxyFacesBinary(self,conn,jsonCall):
        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        jsonCall.responseIsBinary = True
        faces = self._getProxyMesh(proxy).fvert
        jsonCall.data = faces.tobytes()

    def getProxyMaterialInfo(self,conn,jsonCall):
        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        if proxy.type == "Proxymeshes":
            if self.human.material.name == 'XrayMaterial' and self.human._backUpMaterial:
                material = self.human._backUpMaterial
            else:
                material = self.human.material
        else:
            if self.human.material.name == 'XrayMaterial' and proxy._backUpMaterial:
                material = proxy._backUpMaterial
            else:
                material = proxy.object.material
        jsonCall.data = self.api.assets.materialToHash(material)

    def getProxyTextureCoordsBinary(self,conn,jsonCall):
        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        jsonCall.responseIsBinary = True
        texco = self._getProxyMesh(proxy).texco
        jsonCall.data = texco.tobytes()

    def getProxyFaceUVMappingsBinary(self,conn,jsonCall):
        uuid = jsonCall.params["uuid"]
        proxy = self._getProxyByUUID(uuid)
        jsonCall.responseIsBinary = True
        faces = self._getProxyMesh(proxy).fuvs
        jsonCall.data = faces.tobytes()
