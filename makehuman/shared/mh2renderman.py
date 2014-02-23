#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Renderman Export functions

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module implements functions to export a human model in Renderman format and render it
using either the Aqsis or Renderman engine.

The MakeHuman data structures are transposed into renderman objects.
"""

from getpath import getPath, getSysPath, getSysDataPath
import os
import numpy as np
import subprocess
import projection
import time
import math

class ImageLight:

    def __init__(self):
        pass
        
    def projectLighting(self):

            dstImg = projection.mapLighting()
            #dstImg.resize(128, 128);

            dstImg.save(getPath('data/skins/lighting.png'))
            #G.app.selectedHuman.setTexture(os.path.join(getPath(''), 'data', 'skins', 'lighting.tga'))


class MaterialParameter:

    def __init__(self, type, name, val):
        self.type = type
        self.val = val
        self.name = name



class RMRMaterial:

    def __init__(self, name):

        self.name = name
        self.type = "Surface"
        self.parameters = []

    def writeRibCode(self, file):
        file.write('\t\t%s "%s" '%(self.type,self.name))
        #print "Writing %s material"%(self.name)
        for p in self.parameters:
            #print p.name, p.val
            if p.type == "float":
                file.write('"%s %s" [%f] '%(p.type, p.name, p.val))
            if p.type == "string":
                file.write('"%s %s" "%s" '%(p.type, p.name, p.val))
            if p.type == "color":
                file.write('"%s %s" [%f %f %f] '%(p.type, p.name, p.val[0],  p.val[1],  p.val[2]))
        file.write('\n')

    def setParameter(self, name, val, pType = "float"):
        newParamater = True
        for p in self.parameters:
            if p.name == name:
                newParamater = False
                p.val = val
        if newParamater == True:
            #print "Setting paramater %s with value %s"%(name, str(val))
            self.parameters.append(MaterialParameter(pType, name, val))
            #for p in  self.parameters:
                #print p.name, p.val




class RMRLight:

    lightCounter = 0

    def __init__(self, ribsPath, position = [0,0,0], lookAt = [0,0,0], intensity = 1.0, type = "pointlight", blur = 0.025):

        RMRLight.lightCounter += 1
        self.ribsPath = ribsPath
        self.position = np.array(position, dtype=np.float32)
        self.lookAt = np.array(lookAt, dtype=np.float32)
        self.type = type
        self.intensity = intensity
        self.color = [1,1,1]
        self.counter = RMRLight.lightCounter
        self.samples = 64
        self.blur = blur
        self.coneangle = 0.25
        self.roll = None
        self.shadowMapDataFile = os.path.join(self.ribsPath,"%sshadow%d.zfile"%(self.type, self.counter)).replace('\\', '/')
        self.ambientOcclusionDataFile = os.path.join(self.ribsPath,"occlmap.sm" ).replace('\\', '/')
    def __str__(self):
        return "Renderman %s Light, from [%f,%f,%f] to [%f %f %f]"%(self.type,self.position[0],self.position[1],self.position[2],self.lookAt[0],self.lookAt[1],self.lookAt[2])

    def writeRibCode(self, ribfile, n=0):
        # remember z in opengl -> -z in renderman
        if self.type == "pointlight":
             ribfile.write('\tLightSource "pointlight" %i  "from" [%f %f %f] "intensity" %f "color lightcolor" [%f %f %f]\n' % (n, self.position[0], self.position[1], self.position[2],
                      self.intensity, self.color[0], self.color[1], self.color[2]))
        if self.type == "ambient":
            ribfile.write('\tLightSource "ambientlight" %i "intensity" [%f] "color lightcolor" [%f %f %f]\n'%(n, self.intensity, self.color[0], self.color[1], self.color[2]))
        if self.type == "envlight":
            ribfile.write('\tLightSource "envlight" %i "string filename" "%s" "intensity" [%f] "float samples" [ %f ] "float blur" [ %f ]\n'%(n, self.ambientOcclusionDataFile, self.intensity, self.samples, self.blur))
        if self.type == "shadowspot":
            ribfile.write('\tLightSource "shadowspot" %i "intensity" [%f] "from" [%f %f %f] "to" [%f %f %f] "coneangle" [%f] "string shadowname" ["%s"] "float blur" [%f]\n'%(n, self.intensity,\
             self.position[0],self.position[1],self.position[2], self.lookAt[0], self.lookAt[1], self.lookAt[2],\
             self.coneangle, self.shadowMapDataFile, self.blur))



    def shadowRotate(self, ribfile, angle, x, y, z):
        """
        To place the cam for shadow map
        """
        if math.fabs(angle) > 0.001:
            ribfile.write("Rotate %0.2f %0.2f %0.2f %0.2f\n"% (angle, x, y, z))

    def shadowTranslate(self, ribfile, dx, dy, dz):
        """
        To place the cam for shadow map
        """
        ribfile.write("Translate %0.2f %0.2f %0.2f\n"%(dx, dy, dz))

    def shadowProjection(self, ribfile):
        if self.coneangle != 0.0:
            fov = self.coneangle * 360.0/math.pi
            ribfile.write("Projection \"perspective\" \"fov\" [%0.2f]\n"%(fov))

    def pointToAim(self, ribfile, direction):
        """
        pointToAim(): rotate the world so the direction vector points in
        positive z by rotating about the y axis, then x. The cosine
        of each rotation is given by components of the normalized
        direction vector. Before the y rotation the direction vector
        might be in negative z, but not afterward.
        """

        if (direction[0]==0) and (direction[1]==0) and (direction[2]==0):
            return

        #The initial rotation about the y axis is given by the projection of
        #the direction vector onto the x,z plane: the x and z components
        #of the direction.

        xzlen = math.sqrt(direction[0]*direction[0]+direction[2]*direction[2]);
        if xzlen == 0:
            if direction[1] < 0:
                yrot = 180
            else:
                yrot = 0
        else:
            yrot = 180*math.acos(direction[2]/xzlen)/math.pi;

        #The second rotation, about the x axis, is given by the projection on
        #the y,z plane of the y-rotated direction vector: the original y
        #component, and the rotated x,z vector from above.

        yzlen = math.sqrt(direction[1]*direction[1]+xzlen*xzlen);
        xrot = 180*math.acos(xzlen/yzlen)/math.pi; #yzlen should never be 0

        if direction[1] > 0:
            self.shadowRotate(ribfile, xrot, 1.0, 0.0, 0.0)
        else:
            self.shadowRotate(ribfile, -xrot, 1.0, 0.0, 0.0)

        #The last rotation declared gets performed first
        if direction[0] > 0:
            self.shadowRotate(ribfile, -yrot, 0.0, 1.0, 0.0)
        else:
            self.shadowRotate(ribfile, yrot, 0.0, 1.0, 0.0)

    def placeShadowCamera(self, ribfile):
        direction = self.lookAt - self.position
        #print "VIEW",self.lookAt, self.position
        #print "DIRECTION: ", direction
        self.shadowProjection(ribfile)
        if self.roll:
            self.shadowRotate(ribfile,-self.roll, 0.0, 0.0, 1.0);
        self.pointToAim(ribfile, direction);
        self.shadowTranslate(ribfile, -self.position[0], -self.position[1], -self.position[2])


class RMRObject:

    def __init__(self, name, meshData, mtl=None):
        self.groupsDict = {}
        self.facesGroup = None
        self.material = None
        self.materialBump = None
        self.name = name
        self.facesIndices = []
        self.verts = meshData.verts
        self.meshData = meshData
        self.translationTable = [0 for vert in meshData.verts]        
        self.verts = []

        if mtl is not None:
            self.facesIndices = [[(vert.idx,face.uv[index]) for index, vert in enumerate(face.verts)] for face in meshData.faces if meshData.materials[face.idx] == mtl]
            #self.facesIndices = [[(vert.idx,face.uv[index]) for index, vert in enumerate(face.verts)] for face in meshData.faces if face.mtl == mtl]
        else:
            self.facesIndices = [[(vert.idx,face.uv[index]) for index, vert in enumerate(face.verts)] for face in meshData.faces]
        
        #Create a translation table, in case of the obj is only a part of a bigger mesh.
        #Using the translation table, we will create a new vert list for the sub object        
        processedVerts = set()
        idx = 0
        for f in self.facesIndices:
            for i in f:
                vertIndex = i[0]                
                if vertIndex not in processedVerts:                    
                    self.translationTable[vertIndex] = idx
                    idx += 1
                    processedVerts.add(vertIndex)
                    self.verts.append(meshData.verts[vertIndex])
  
        





    def writeRibCode(self, ribPath ):

        #print "ribPath = ", ribPath
        facesUVvalues = self.meshData.texco #TODO usa direttamente self.

        ribObjFile = file(ribPath, 'w')
        ribObjFile.write('Declare "st" "facevarying float[2]"\n')
        ribObjFile.write('Declare "Cs" "facevarying color"\n')
        ribObjFile.write('SubdivisionMesh "catmull-clark" [')

        if not self.facesIndices: raise RuntimeError(self.name)

        for faceIdx in self.facesIndices:
            ribObjFile.write('%i ' % (3 if faceIdx[0] == faceIdx[-1] else 4))
        ribObjFile.write('] ')

        ribObjFile.write('[')
        for faceIdx in self.facesIndices:
            faceIdx.reverse()
            if faceIdx[0] == faceIdx[-1]:
                ribObjFile.write('%i %i %i ' % (self.translationTable[faceIdx[0][0]], self.translationTable[faceIdx[1][0]], self.translationTable[faceIdx[2][0]]))
            else:
                ribObjFile.write('%i %i %i %i ' % (self.translationTable[faceIdx[0][0]], self.translationTable[faceIdx[1][0]], self.translationTable[faceIdx[2][0]], self.translationTable[faceIdx[3][0]]))
        ribObjFile.write(']')

        ribObjFile.write('''["interpolateboundary"] [0 0] [] []"P" [''')
        for vert in self.verts:
            ribObjFile.write('%f %f %f ' % (vert.co[0], vert.co[1], -vert.co[2]))
        ribObjFile.write('] ')

        ribObjFile.write('\n"st" [')
        for faceIdx in self.facesIndices:
            face = faceIdx[:-1] if faceIdx[0] == faceIdx[-1] else faceIdx
            for idx in face:
                uvIdx = idx[1]
                uvValue = facesUVvalues[uvIdx]
                ribObjFile.write('%s %s ' % (uvValue[0], 1 - uvValue[1]))
        ribObjFile.write(']')
        ribObjFile.close()



class RMRHuman(RMRObject):

    def __init__(self, human, name, obj, ribRepository):

        RMRObject.__init__(self, name, obj)
        self.subObjects = []
        self.human = human      
            
    def materialInit(self):
        self.basetexture =  os.path.splitext(os.path.basename(self.human.getTexture()))[0]
        if self.human.hairObj != None:
            self.hairtexture =  os.path.splitext(os.path.basename(self.human.hairObj.getTexture()))[0]
            self.hairMat = RMRMaterial("hairpoly")
            self.hairMat.parameters.append(MaterialParameter("string", "colortexture", self.hairtexture+".png"))
            #print "HAIRTEXTURE",  self.hairtexture
        #print "BASETEXTURE",  self.basetexture
        
        
        
        
        self.skinMat = RMRMaterial("skin2")
        self.skinMat.parameters.append(MaterialParameter("string", "colortexture", self.basetexture+".png" ))
        self.skinMat.parameters.append(MaterialParameter("string", "spectexture", self.basetexture+"_ref.png"))
        self.skinMat.parameters.append(MaterialParameter("float", "Ks", 0.1))
        self.skinMat.parameters.append(MaterialParameter("float", "Ksss", 0.2)) #TODO: using a texture
        self.skinMat.parameters.append(MaterialParameter("string", "ssstexture", "lighting.png"))

        self.skinBump = RMRMaterial("skinbump")
        self.skinBump.type = "Displacement"
        self.skinBump.parameters.append(MaterialParameter("string", "bumpTexture", self.basetexture+"_bump.png"))
        self.skinBump.parameters.append(MaterialParameter("float", "bumpVal", 0.001))

        self.corneaMat = RMRMaterial("cornea")

        self.teethMat = RMRMaterial("teeth")
        self.teethMat.parameters.append(MaterialParameter("string", "colortexture", self.basetexture+".png"))

        self.eyeBallMat = RMRMaterial("eyeball")
        self.eyeBallMat.parameters.append(MaterialParameter("string", "colortexture", self.basetexture+".png"))
        
        


    def subObjectsInit(self):
        
        
        #Because currently therea re no usemtl part in the wavefront obj, 
        #we define only a subpart for the whole character
        
        self.subObjects = []
        #self.wholebody = RMRObject("wholebody", self.meshData)
        #self.wholebody.material = self.skinMat
        #self.subObjects.append(self.wholebody)
        
        self.eyeBall = RMRObject("eye", self.meshData, 'eye')
        self.eyeBall.material = self.eyeBallMat
        self.subObjects.append(self.eyeBall)
        
        self.cornea = RMRObject("cornea", self.meshData, 'cornea')
        self.cornea.material = self.corneaMat
        self.subObjects.append(self.cornea)

        self.teeth = RMRObject("teeth", self.meshData, 'teeth')
        self.teeth.material = self.teethMat
        self.subObjects.append(self.teeth)

        self.nails = RMRObject("nails", self.meshData, 'nail')
        self.nails.material = self.skinMat
        self.subObjects.append(self.nails)

        self.skin = RMRObject("skin", self.meshData, 'skin')
        self.skin.material = self.skinMat
        self.skin.materialBump = self.skinBump
        self.subObjects.append(self.skin)        
        
        if self.human.hairObj != None:
            self.hair = RMRObject("hair", self.human.hairObj.mesh)
            self.hair.material = self.hairMat            
            self.subObjects.append(self.hair)
        

    def getSubObject(self, name):
        for subOb in self.subObjects:
            if subOb.name == name:
                return subOb

    def getHumanPosition(self):
        return (self.human.getPosition()[0], self.human.getPosition()[1],\
                self.human.getRotation()[0], self.human.getRotation()[1])


    def __str__(self):
        return "Human Character"


class RMRHeader:

    def __init__(self):

        self.screenwindow = None
        self.options = {}
        self.statistics =  ["endofframe", '[1]']
        self.projection = "perspective"
        self.sizeFormat = [800,600]
        self.clipping = None
        self.pixelsamples = [2, 2]
        self.fov = None
        self.shadingRate = 1
        self.displayName = None
        self.displayType = None
        self.displayColor = None
        self.displayName2 = None
        self.displayType2 = None
        self.displayColor2 = None
        self.cameraX = None
        self.cameraY = None
        self.cameraZ = None
        self.searchShaderPath = ""
        self.searchTexturePath = ""
        self.searchArchivePath = ""
        self.bucketSize = None
        self.eyesplits = None
        self.depthfilter = None
        self.sides = 2
        self.pixelFilter = None
        self.shadingInterpolation = None


    def setCameraPosition(self, camX,camY,camZ):
        self.cameraX = camX
        self.cameraY = camY
        self.cameraZ = camZ

    def setSearchShaderPath(self, shaderPaths):
        for p in shaderPaths:
            self.searchShaderPath += p + ":"
        self.searchShaderPath = "%s:&"%(self.searchShaderPath.replace('\\', '/'))

    def setSearchTexturePath(self, texturePaths):
        for p in texturePaths:
            self.searchTexturePath += p + ":"
        self.searchTexturePath = "%s:&"%(self.searchTexturePath.replace('\\', '/'))

    def setSearchArchivePath(self, archivePaths):
        for p in archivePaths:
            self.searchArchivePath += p + ":"
        self.searchArchivePath = "%s:&"%(self.searchArchivePath.replace('\\', '/'))

    def writeRibCode(self, ribfile):
        #Write headers
        if self.bucketSize:
            ribfile.write('Option "limits" "bucketsize" [%d %d]\n'%(self.bucketSize[0], self.bucketSize[1]))
        if self.eyesplits:
            ribfile.write('Option "limits" "eyesplits" [%d]\n'%(self.eyesplits))
        if self.depthfilter:
            ribfile.write('Hider "hidden" "depthfilter" "%s"\n'%(self.depthfilter))
        if self.pixelFilter:
            ribfile.write('PixelFilter "%s" 1 1\n'%(self.pixelFilter))
        if self.projection == "perspective" and self.fov:
            ribfile.write('Projection "%s" "fov" %f\n' % (self.projection, self.fov))
        if self.projection == "orthographic":
            ribfile.write('Projection "%s"\n' % (self.projection))
        if self.shadingInterpolation:
            ribfile.write('ShadingInterpolation "%s"\n' % self.shadingInterpolation)
        if self.clipping:
            ribfile.write('Clipping %f %f\n'%(self.clipping[0], self.clipping[1]))
        if self.screenwindow:
            ribfile.write('ScreenWindow %f %f %d %d\n'%(self.screenwindow[0], self.screenwindow[1], self.screenwindow[2], self.screenwindow[3]))
        ribfile.write('Option "statistics" "%s" %s\n'%(self.statistics[0], self.statistics[1]))
        ribfile.write('Option "searchpath" "shader" "%s"\n' %(self.searchShaderPath))
        ribfile.write('Option "searchpath" "texture" "%s"\n' %(self.searchTexturePath))
        ribfile.write('Format %s %s 1\n' % (self.sizeFormat[0],self.sizeFormat[1]))
        ribfile.write('Sides %d\n' % (self.sides))

        ribfile.write('PixelSamples %s %s\n' % (self.pixelsamples[0], self.pixelsamples[1]))
        ribfile.write('ShadingRate %s \n' % self.shadingRate)
        if self.displayName:
            ribfile.write('Display "%s" "%s" "%s"\n'%(self.displayName, self.displayType, self.displayColor))
        if self.displayName2:
            #ribfile.write('Display "+%s" "%s" "%s"\n'%(self.displayName2, self.displayType2, self.displayColor2))
            pass
        if (self.cameraX != None) and (self.cameraY != None) and (self.cameraZ != None):
            ribfile.write('\tTranslate %f %f %f\n' % (self.cameraX, self.cameraY, self.cameraZ))



class RMRScene:

    def __init__(self, app):
        camera = app.modelCamera

        #rendering properties
        self.camera = camera
        self.app = app
        #self.lastUndoItem = None
        #self.lastRotation = [0,0,0]
        #self.lastCameraPosition = [self.camera.eyeX, -self.camera.eyeY, self.camera.eyeZ]
        #self.firstTimeRendering = True
        self.renderResult = ""

        #resource paths
        self.renderPath = getPath('render/renderman_output')
        self.ribsPath = os.path.join(self.renderPath, 'ribFiles')
        self.usrShaderPath = os.path.join(self.ribsPath, 'shaders')
        
        #Texture paths
        self.usrTexturePath = os.path.join(self.ribsPath, 'textures')
        self.applicationPath = getSysPath()
        self.appTexturePath = getSysDataPath('textures')
        self.hairTexturePath = getSysDataPath('hairstyles')
        self.skinTexturePath = getPath('data/skins')
        
        #self.appObjectPath = os.path.join(self.applicationPath, 'data', '3dobjs')
        self.worldFileName = os.path.join(self.ribsPath,"world.rib").replace('\\', '/')
        self.lightsFolderPath = os.path.join(getSysDataPath('lights'), 'aqsis')       

        #mainscenefile
        self.sceneFileName = os.path.join(self.ribsPath, "scene.rib")

        #Human in the scene
        self.humanCharacter = RMRHuman(app.selectedHuman, "base.obj", app.selectedHuman.mesh, self.ribsPath)
        self.humanCharacter.materialInit()
        self.humanCharacter.subObjectsInit()
        
        #Rendering options
        #self.calcShadow = False
        #self.calcSSS = False

        ##Shadow path
        #self.shadowFileName = os.path.join(self.ribsPath,"shadow.rib").replace('\\', '/')

        ##SSS path        
        #self.bakeFilename = os.path.join(self.ribsPath,"skinbake.rib").replace('\\', '/')
        #self.lightmapFileName = os.path.join(self.ribsPath,"lightmap.rib").replace('\\', '/')
        #self.bakeTMPTexture = os.path.join(self.usrTexturePath,"bake.bake").replace('\\', '/')
        #self.bakeTexture = os.path.join(self.usrTexturePath,"bake.texture").replace('\\', '/')
        #self.lightmapTMPTexture = os.path.join(self.usrTexturePath,"lightmap.png").replace('\\', '/')
        #self.lightmapTexture = os.path.join(self.usrTexturePath,"lightmap.texture").replace('\\', '/')

        #Lights list
        self.lights = []

        #creating resources folders
        if not os.path.isdir(self.renderPath):
            os.makedirs(self.renderPath)
        if not os.path.isdir(self.ribsPath):
            os.makedirs(self.ribsPath)
        if not os.path.isdir(self.usrTexturePath):
            os.makedirs(self.usrTexturePath)
        if not os.path.isdir(self.usrShaderPath):
            os.makedirs(self.usrShaderPath)



    def __str__(self):
        return "Renderman Scene"


    def loadLighting(self, lightsFolderPath, lightFile):
        self.lights = []
        RMRLight.lightCounter = 0
        path = os.path.join(lightsFolderPath,lightFile)
        fileDescriptor = open(path)

        for data in fileDescriptor:
            #print data
            dataList = data.split()
            fromX = float(dataList[0])
            fromY = float(dataList[1])
            fromZ = float(dataList[2])
            toX = float(dataList[3])
            toY = float(dataList[4])
            toZ = float(dataList[5])
            lIntensity = float(dataList[6])
            lType = dataList[7]

            l = RMRLight(self.ribsPath,[fromX, fromY, fromZ], [toX, toY, toZ], intensity = lIntensity, type = lType)
            if len(dataList) >= 9:
                l.blur = float(dataList[8])
            if len(dataList) >= 10:
                l.coneangle = float(dataList[9])
            #print l
            self.lights.append(l)




    def writeWorldFile(self, fName, shadowMode = None, bakeMode = None):
        """

        """

        #Get global subobjs parameteres.
        self.humanCharacter.skinMat.setParameter("sweat", self.app.settings.get('rendering_aqsis_oil', 0.3))
        self.humanCharacter.materialInit()
        self.humanCharacter.subObjectsInit()

        #if len(self.humanCharacter.subObjects) < 1:
            #print "Warning: AO calculation on 0 objects"

        ribfile = file(fName, 'w')
        #if not bakeMode:
            #print "Writing world"
        for subObj in self.humanCharacter.subObjects:
            #print "rendering....", subObj.name
            ribPath = os.path.join(self.ribsPath, subObj.name + '.rib')
            ribfile.write('\tAttributeBegin\n')
            subObj.writeRibCode(ribPath)
            #if shadowMode:
                #ribfile.write('\tSurface "null"\n')
            #else:
            if subObj.materialBump:
                subObj.materialBump.writeRibCode(ribfile)
            if subObj.material:
                subObj.material.writeRibCode(ribfile)
            ribfile.write('\t\tReadArchive "%s"\n' % ribPath.replace('\\', '/'))
            ribfile.write('\tAttributeEnd\n')
        #ribfile.write('\tAttributeBegin\n')
        #if shadowMode:
        #    ribfile.write('\tSurface "null"\n')
        #ribfile.write('\tAttributeEnd\n')
        #else:
            #print "Writing bake world"
            #ribfile.write('\tAttributeBegin\n')
            #ribfile.write('\tSurface "bakelightmap" "string bakefilename" "%s" "string texturename" "%s"\n'%(self.bakeTMPTexture, self.humanCharacter.basetexture+".png"))
            #ribPath = os.path.join(self.ribsPath, 'skin.rib')
            #ribfile.write('\t\tReadArchive "%s"\n' % ribPath.replace('\\', '/'))
            #ribfile.write('\tAttributeEnd\n')

        ribfile.close()



    def writeSceneFile(self):
        """
        This function creates the frame definition for a Renderman scene.
        """
        self.renderResult = str(time.time())+".tif"


        #Getting global settings



        ribSceneHeader = RMRHeader()

        ribSceneHeader.sizeFormat = [self.app.settings.get('rendering_width', 800), self.app.settings.get('rendering_height', 600)]
        ribSceneHeader.pixelSamples = [self.app.settings.get('rendering_aqsis_samples', 2),self.app.settings.get('rendering_aqsis_samples', 2)]
        ribSceneHeader.shadingRate = self.app.settings.get('rendering_aqsis_shadingrate', 2)
        ribSceneHeader.setCameraPosition(self.camera.eyeX, -self.camera.eyeY, self.camera.eyeZ)
        ribSceneHeader.setSearchShaderPath([self.usrShaderPath])
        ribSceneHeader.setSearchTexturePath([self.appTexturePath,self.usrTexturePath,self.hairTexturePath,self.skinTexturePath])
        ribSceneHeader.fov = self.camera.fovAngle
        ribSceneHeader.displayName = os.path.join(self.ribsPath, self.renderResult).replace('\\', '/')
        ribSceneHeader.displayType = "file"
        ribSceneHeader.displayColor = "rgba"
        ribSceneHeader.displayName2 = "Final Render"
        ribSceneHeader.displayType2 = "framebuffer"
        ribSceneHeader.displayColor2 = "rgb"



        pos = self.humanCharacter.getHumanPosition()        
        ribfile = file(self.sceneFileName, 'w')

        #Write rib header
        ribSceneHeader.writeRibCode(ribfile)

        #Write rib body
        ribfile.write('\tTranslate %f %f %f\n' % (pos[0], pos[1], 0.0)) # Model
        ribfile.write('\tRotate %f 1 0 0\n' % -pos[2])
        ribfile.write('\tRotate %f 0 1 0\n' % -pos[3])
        ribfile.write('WorldBegin\n')
        for l in self.lights:
            l.writeRibCode(ribfile, l.counter)
        ribfile.write('\tReadArchive "%s"\n'%(self.worldFileName))
        ribfile.write('WorldEnd\n')
        ribfile.close()


    #def writeSkinBakeFile(self):
        #"""
        #This function creates the frame definition for a Renderman scene.
        #"""

        ##Getting global settings
        #self.xResolution, self.yResolution = self.app.settings.get('rendering_width', 800), self.app.settings.get('rendering_height', 600)
        #self.pixelSamples = [2,2]
        #self.shadingRate = 0.5

        #pos = self.humanCharacter.getHumanPosition()

        #ribfile = file(self.bakeFilename, 'w')


        #ribfile.write('FrameBegin 1\n')

        ##Getting global settings
        #ribSceneHeader = RMRHeader()
        #ribSceneHeader.sizeFormat = [self.app.settings.get('rendering_width', 800), self.app.settings.get('rendering_height', 600)]
        #ribSceneHeader.pixelSamples = [self.app.settings.get('rendering_aqsis_samples', 2),self.app.settings.get('rendering_aqsis_samples', 2)]
        #ribSceneHeader.shadingRate = self.app.settings.get('rendering_aqsis_shadingrate', 2)
        #ribSceneHeader.setCameraPosition(self.camera.eyeX, -self.camera.eyeY, self.camera.eyeZ)
        #ribSceneHeader.setSearchShaderPath([self.usrShaderPath])
        #ribSceneHeader.setSearchTexturePath([self.appTexturePath,self.usrTexturePath,self.hairTexturePath,self.skinTexturePath])
        #ribSceneHeader.fov = self.camera.fovAngle

        ##Write rib header
        #ribSceneHeader.writeRibCode(ribfile)

        ##Write rib body
        #ribfile.write('\tTranslate %f %f %f\n' % (pos[0], pos[1], 0.0)) # Model
        #ribfile.write('\tRotate %f 1 0 0\n' % -pos[2])
        #ribfile.write('\tRotate %f 0 1 0\n' % -pos[3])
        #ribfile.write('WorldBegin\n')
        #for l in self.lights:
            #l.writeRibCode(ribfile, l.counter)
        #ribfile.write('\tReadArchive "%s"\n'%(self.worldFileName+"bake.rib"))
        #ribfile.write('WorldEnd\n')
        #ribfile.write('FrameEnd\n')
        #ribfile.write('MakeTexture "%s" "%s" "periodic" "periodic" "box" 1 1 "float bake" 1024\n'%(self.bakeTMPTexture, self.bakeTexture))

        #ribfile.write('FrameBegin 2\n')

        ##Getting global settings
        #ribSceneHeader = RMRHeader()
        #ribSceneHeader.sizeFormat = [1024,1024]
        #ribSceneHeader.setCameraPosition(0,0,0.02)
        #ribSceneHeader.setSearchShaderPath([self.usrShaderPath])
        #ribSceneHeader.setSearchTexturePath([self.appTexturePath,self.usrTexturePath,self.hairTexturePath,self.skinTexturePath])
        #ribSceneHeader.shadingInterpolation = "smooth"
        #ribSceneHeader.projection = "orthographic"
        #ribSceneHeader.displayType = "file"
        #ribSceneHeader.displayColor = "rgba"
        #ribSceneHeader.displayName = self.lightmapTMPTexture

        ##Write rib header
        #ribSceneHeader.writeRibCode(ribfile)
        #ribfile.write('WorldBegin\n')
        #ribfile.write('Color [ 1 1 1 ]\n')
        #ribfile.write('\tSurface "scatteringtexture" "string texturename" "%s"\n'%(self.bakeTexture))
        ##ribfile.write('Translate 0 0 0.02\n')
        #ribfile.write('Polygon "P" [ -1 -1 0   1 -1 0   1 1 0  -1 1 0 ]"st" [ 0 1  1 1  1 0  0 0  ]\n')
        #ribfile.write('WorldEnd\n')
        #ribfile.write('FrameEnd\n')
        #ribfile.write('MakeTexture "%s" "%s" "periodic" "periodic" "box" 1 1 "float bake" 1024\n'%(self.lightmapTMPTexture, self.lightmapTexture))



    #def writeShadowFile(self):
        #"""
        #This function creates the frame definition for a Renderman scene.
        #"""

        #ribfile = file(self.shadowFileName, 'w')
        #ribSceneHeader = RMRHeader()
        #ribSceneHeader.sizeFormat = [1024,1024]
        #ribSceneHeader.pixelSamples = [1,1]
        #ribSceneHeader.shadingRate = 2
        #ribSceneHeader.setSearchShaderPath([self.usrShaderPath])
        #ribSceneHeader.setSearchTexturePath([self.appTexturePath,self.usrTexturePath,self.hairTexturePath,self.skinTexturePath])
        #ribSceneHeader.bucketSize = [32,32]
        #ribSceneHeader.eyesplits = 10
        #ribSceneHeader.depthfilter = "midpoint"
        #ribSceneHeader.pixelFilter = "box"

        ##Write rib header
        #ribSceneHeader.writeRibCode(ribfile)
        #for l in self.lights:
            #if l.type == "shadowspot":
                #ribfile.write('FrameBegin %d\n'%(l.counter))
                #ribfile.write('Display "%s" "zfile" "z"\n'%(l.shadowMapDataFile))
                #l.placeShadowCamera(ribfile)
                #ribfile.write('WorldBegin\n')
                #ribfile.write('\tSurface "null"\n')
                #ribfile.write('\tReadArchive "%s"\n'%(self.worldFileName+"shad.rib"))
                #ribfile.write('WorldEnd\n')
                #ribfile.write('FrameEnd\n')
                #shadowMapDataFileFinal = l.shadowMapDataFile.replace("zfile","shad")
                #ribfile.write('MakeShadow "%s" "%s"\n'%(l.shadowMapDataFile,shadowMapDataFileFinal))
        #ribfile.close()




    def render(self):
        
        imgLight = ImageLight()
        imgLight.projectLighting()

        filesTorender = []
        self.loadLighting(self.lightsFolderPath, "default.lights")
        #self.writeTextureFile() #TODO move in the init

        ##recalculateAll = 0
        #recalculateSSS = 0

        #recalculateAll = 1
        #if  recalculateAll == 1:
            #self.writeWorldFile(self.worldFileName+"bake.rib", bakeMode = 1)
            #self.writeSkinBakeFile()
            #filesTorender.append((self.bakeFilename, 'Calculating SSS'))

        self.writeWorldFile(self.worldFileName)
        self.writeSceneFile()
        filesTorender.append((self.sceneFileName, 'Rendering scene'))

        self.renderThread = RenderThread(self.app, filesTorender)
        self.renderThread.renderPath = os.path.join(self.ribsPath, self.renderResult).replace('\\', '/')
        self.renderThread.start()

from threading import Thread

class RenderThread(Thread):

    def __init__(self, app, filenames):

        Thread.__init__(self)
        self.app = app
        self.filenames = filenames
        self.renderPath = ""

    def progress(self, progress, status=None):
        import mh
        mh.callAsyncThread(self.app.progress, progress, status)


    def prompt(self):
        import mh
        mh.callAsyncThread(self.app.prompt,
                           "Render finished", "The image is saved in {0}".format(self.renderPath),
                           "OK", helpId="'renderFinishedPrompt'")

    def run(self):
        
        for filename, status in self.filenames:
            command = '%s "%s"' % ('aqsis -Progress', filename)            
            renderProc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)

            self.progress(0.0, status)

            try:
                while True:
                    line = renderProc.stdout.readline()
                    if line == '':
                        break
                   
                    progress = line.split()[1][0:-1]
                    self.progress(float(progress)/100.0)
            except:
                pass

            self.progress(1.0)

        self.prompt()


        
        """
        for filename in self.filenames:
            command = '%s "%s"' % ('aqsis -progress -progressformat="progress %f %p %s %S" -v 0', filename[0])
            renderProc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            
            #for line in renderProc.stdout:
              #pass
              
            #print "Rendering finished ", renderProc.stdout
        """
            
        """
        for filename, status in self.filenames:

            command = '%s "%s"' % ('aqsis -progress -progressformat="progress %f %p %s %S" -v 0', filename)
            #print command
            renderProc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)

            mh.callAsync(lambda:self.app.progress(0.0, status))

            for line in renderProc.stdout:
              if line.startswith("progress"):
                progress = line.split()
                mh.callAsync(lambda:self.app.progress(float(progress[2])/100.0))

            mh.callAsync(lambda:self.app.progress(1.0))
        """
