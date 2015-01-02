# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2015
# Coding Standards: See http://www.makehuman.org/node/165

"""
Abstract

"""

import bpy
import os
from bpy.props import *

from .error import *
from .rigify import rigifyMhx

VERSION = (1,18,0)

def setVersion(bl_info):
    global VERSION, FROM_VERSION, version
    VERSION = bl_info["version"]
    version = list(VERSION[0:2])
    FROM_VERSION = 13

#
#
#

import bpy
import os
import time
import math
import mathutils
from mathutils import Vector, Matrix, Quaternion
from bpy.props import *

MHX249 = False
Blender24 = False
Blender25 = True
theDir = "~"

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

theScale = 1.0
One = 1.0/theScale
useMesh = 1
verbosity = 2
warnedTextureDir = False
warnedVersion = False

true = True
false = False
Epsilon = 1e-6
nErrors = 0
theTempDatum = None
theMessage = ""
theMhxFile = ""

#
#    toggle flags
#

T_EnforceVersion = 0x01
T_Clothes = 0x02
T_HardParents = 0x0
T_CrashSafe = 0x04

T_Diamond = 0x10
T_Shapekeys = 0x40
T_ShapeDrivers = 0x80

T_Face = T_Shapekeys
T_Shape = T_Shapekeys

T_Mesh = 0x100
T_Armature = 0x200
T_Proxy = 0x400
T_Cage = 0x800

T_Rigify = 0x1000
T_Symm = 0x4000

DefaultToggle = ( T_EnforceVersion + T_Mesh + T_Armature +
    T_Shapekeys + T_ShapeDrivers + T_Proxy + T_Clothes + T_Rigify )

toggle = DefaultToggle
toggleSettings = toggle
loadedData = None

#
#   mhxEval - a home-made, stymied but guaranteed safe eval
#

def mhxEval(expr, locls={}):
    if expr == "True":
        return True
    elif expr == "False":
        return False
    elif expr == "None":
        return None
    elif expr == "{}":
        return {}
    elif expr == "[]":
        return []

    try:
        return int(expr)
    except ValueError:
        pass

    try:
        return float(expr)
    except ValueError:
        pass

    try:
        return locls[expr]
    except KeyError:
        pass

    try:
        return globals()[expr]
    except KeyError:
        pass

    if expr[0] in ['"',"'"] and expr[-1] == expr[0]:
        return expr[1:-1]

    elif expr[0] in ["(","["]:
        words = expr[1:-1].split(",")
        lst = []
        for word in words:
            lst.append(mhxEval(word, locls))
        if expr[0] == "(":
            if len(words) == 1:
                return lst[0]
            else:
                return tuple(lst)
        else:
            return lst

    for op in ['==', '!=', '*', '&']:
        words = expr.split(op)
        if len(words) == 2:
            x = mhxEval(words[0])
            y = mhxEval(words[1])
            if op == '==':
                return (x==y)
            elif op == '!=':
                return (x!=y)
            elif op == '*':
                return x*y
            elif op == '&':
                return x&y

    raise MyError("Failed to evaluate expression:\n%s" % expr)

#
#    Dictionaries
#

def initLoadedData():
    global loadedData

    loadedData = {
    'NONE' : {},

    'Object' : {},
    'Mesh' : {},
    'Armature' : {},

    'Material' : {},
    'Image' : {},
    'MaterialTextureSlot' : {},
    'Texture' : {},

    'Bone' : {},
    'BoneGroup' : {},
    'Rigify' : {},

    'Action' : {},
    'Group' : {},

    'MeshTextureFaceLayer' : {},
    'MeshColorLayer' : {},
    'VertexGroup' : {},
    'ShapeKey' : {},
    'ParticleSystem' : {},

    'ObjectConstraints' : {},
    'ObjectModifiers' : {},
    'MaterialSlot' : {},
    }
    return

def reinitGlobalData():
    global loadedData
    for key in [
        'MeshTextureFaceLayer', 'MeshColorLayer', 'VertexGroup', 'ShapeKey',
        'ParticleSystem', 'ObjectConstraints', 'ObjectModifiers', 'MaterialSlot']:
        loadedData[key] = {}
    return

Plural = {
    'Object' : 'objects',
    'Mesh' : 'meshes',
    'Lattice' : 'lattices',
    'Curve' : 'curves',
    'Text' : 'texts',
    'Group' : 'groups',
    'Empty' : 'empties',
    'Armature' : 'armatures',
    'Bone' : 'bones',
    'BoneGroup' : 'bone_groups',
    'Pose' : 'poses',
    'PoseBone' : 'pose_bones',
    'Material' : 'materials',
    'Texture' : 'textures',
    'Image' : 'images',
}

# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------

def importMhxFile(self, context):
    global toggle
    toggle = DefaultToggle
    if self.helpers:
         toggle |= T_Diamond
    try:
        if not context.user_preferences.system.use_scripts_auto_execute:
            MyError("Auto Run Python Scripts must be turned on.\nIt is found under\n File > User Preferences > File")
        readMhxFile(self.filepath)
    except MhxError:
        print("Error when loading MHX file %s:\n" % self.filepath + theMessage)

#
#    readMhxFile(filePath):
#

def readMhxFile(filePath):
    global nErrors, theArmature, One
    global toggle, warnedVersion, theMessage, alpha7, theDir

    theArmature = None
    alpha7 = False
    warnedVersion = False
    initLoadedData()
    theMessage = ""

    theDir = os.path.dirname(filePath)
    fileName = os.path.expanduser(filePath)
    _,ext = os.path.splitext(fileName)
    if ext.lower() != ".mhx":
        print("Error: Not a mhx file: %s" % fileName.encode('utf-8', 'strict'))
        return
    print( "Opening MHX file %s " % fileName.encode('utf-8', 'strict') )
    print("Toggle %x" % toggle)
    time1 = time.clock()

    # Tokenize:
    # Create a nested list of tokens
    # ignore = False  # UNUSED
    stack = []
    tokens = []
    key = "toplevel"
    level = 0
    nErrors = 0
    comment = 0
    nesting = 0

    file= open(fileName, "rU")
    print( "Tokenizing" )
    lineNo = 0
    for line in file:
        # print(line)
        lineSplit= line.split()
        lineNo += 1
        if len(lineSplit) == 0:
            pass
        elif lineSplit[0][0] == '#':
            if lineSplit[0] == '#if':
                if comment == nesting:
                    try:
                        res = mhxEval(lineSplit[1])
                    except:
                        res = False
                    if res:
                        comment += 1
                nesting += 1
            elif lineSplit[0] == '#else':
                if comment == nesting-1:
                    comment += 1
                elif comment == nesting:
                    comment -= 1
            elif lineSplit[0] == '#endif':
                if comment == nesting:
                    comment -= 1
                nesting -= 1
        elif comment < nesting:
            pass
        elif lineSplit[0] == 'end':
            try:
                sub = tokens
                tokens = stack.pop()
                if tokens:
                    tokens[-1][2] = sub
                level -= 1
            except:
                print( "Tokenizer error at or before line %d.\nThe mhx file has been corrupted.\nTry to export it again from MakeHuman." % lineNo )
                print( line )
                stack.pop()
        elif lineSplit[-1] == ';':
            if lineSplit[0] == '\\':
                key = lineSplit[1]
                tokens.append([key,lineSplit[2:-1],[]])
            else:
                key = lineSplit[0]
                tokens.append([key,lineSplit[1:-1],[]])
        else:
            key = lineSplit[0]
            tokens.append([key,lineSplit[1:],[]])
            stack.append(tokens)
            level += 1
            tokens = []
    file.close()

    if level != 0:
        MyError("Tokenizer error (%d).\nThe mhx file has been corrupted.\nTry to export it again from MakeHuman." % level)

    # Parse:
    # Take the list of tokens and create stuff

    print( "Parsing" )
    parse(tokens)

    if theArmature:
        scn = bpy.context.scene
        scn.objects.active = theArmature
        print(scn, bpy.context.object, scn.objects.active)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        theArmature.select = True
        bpy.ops.object.mode_set(mode='POSE')
        theArmature.MhAlpha8 = not alpha7

    time2 = time.clock()
    msg = "File %s loaded in %g s" % (fileName, time2-time1)
    if nErrors:
        msg += " but there where %d errors. " % (nErrors)
    print(msg)
    return

#
#    getObject(name, var):
#

def getObject(name, var):
    try:
        return loadedData['Object'][name]
    except:
        raise MhxError("Bug: object %s not found" % ob)

#
#    checkMhxVersion(major, minor):
#

def checkMhxVersion(major, minor):
    global warnedVersion
    print("MHX", (major,minor), (VERSION[0], VERSION[1]), warnedVersion)
    if  major != VERSION[0] or minor < FROM_VERSION:
        if warnedVersion:
            return
        else:
            msg = (
"Wrong MHX version\n" +
"Expected MHX %d.%02d but the loaded file " % (VERSION[0], VERSION[1]) +
"has version MHX %d.%02d\n" % (major, minor))
            if minor < FROM_VERSION:
                msg += (
"You can disable this error message by deselecting the \n" +
"Enforce version option when importing. Better:\n" +
"Export the MHX file again with an updated version of MakeHuman.\n" +
"The most up-to-date version of MakeHuman is the nightly build.\n")
            else:
                msg += (
"Download the most recent Blender build from www.graphicall.org. \n" +
"The most up-to-date version of the import script is distributed\n" +
"with Blender. It can also be downloaded from MakeHuman. \n" +
"It is located in the importers/mhx/blender25x \n" +
"folder and is called import_scene_mhx.py. \n")
        if (toggle & T_EnforceVersion or minor > VERSION[1]):
            MyError(msg)
        else:
            print(msg)
            warnedVersion = True
    return

#
#    parse(tokens):
#

ifResult = False

def printMHXVersionInfo(versionStr, performVersionCheck = False):
    versionInfo = dict()
    val = versionStr.split()

    version[0] = int(val[0])
    version[1] = int(val[1])

    for debugVal in val[2:]:
        debugVal = debugVal.replace("_"," ")
        dKey, dVal = debugVal.split(':')
        versionInfo[ dKey.strip() ] = dVal.strip()

    if 'MHXImporter' in versionInfo:
        print("MHX importer version: ", versionInfo["MHXImporter"])
    if performVersionCheck:
        checkMhxVersion(version[0], version[1])
    else:
        print("MHX: %s.%s" % (version[0], version[1]))

    for (key, value) in versionInfo.items():
        if key == "MHXImporter":
            continue
        print("%s: %s" % (key, value))


def parse(tokens):
    global MHX249, ifResult, One, version, theArmature, theLayers
    versionInfoStr = ""

    scn = bpy.context.scene
    theLayers = list(scn.layers)
    theLayers[19] = False
    scn.layers = len(scn.layers)*[True]

    for (key, val, sub) in tokens:
        data = None
        if key == 'MHX':
            importerVerStr = "MHXImporter:_%d.%d.%d" % VERSION
            versionInfoStr = " ".join(val + [importerVerStr])

            printMHXVersionInfo(versionInfoStr, performVersionCheck = True)
        elif key == 'MHX249':
            MHX249 = mhxEval(val[0])
            print("Blender 2.49 compatibility mode is %s\n" % MHX249)
        elif MHX249:
            pass
        elif key == 'print':
            msg = concatList(val)
            print(msg)
        elif key == 'warn':
            msg = concatList(val)
            print(msg)
        elif key == 'error':
            msg = concatList(val)
            MyError(msg)
        elif key == 'NoScale':
            pass
        elif key == "Object":
            parseObject(val, sub, versionInfoStr)
        elif key == "Mesh":
            reinitGlobalData()
            data = parseMesh(val, sub)
        elif key == "Armature":
            data = parseArmature(val, sub)
        elif key == "Pose":
            data = parsePose(val, sub)
        elif key == "Action":
            data = parseAction(val, sub)
        elif key == "Material":
            data = parseMaterial(val, sub)
        elif key == "Texture":
            data = parseTexture(val, sub)
        elif key == "Image":
            data = parseImage(val, sub)
        elif key == "Group":
            data = parseGroup(val, sub)
        elif key == "DefineProperty":
            parseDefineProperty(val, sub)
        elif key == "Process":
            parseProcess(val, sub)
        elif key == "PostProcess":
            postProcess(val)
            hideLayers(val)
        elif key == "CorrectRig":
            correctRig(val)
        elif key == "Rigify":
            if toggle & T_Rigify:
                theArmature = rigifyMhx(bpy.context)
        elif key == 'AnimationData':
            try:
                ob = loadedData['Object'][val[0]]
            except:
                ob = None
            if ob:
                bpy.context.scene.objects.active = ob
                parseAnimationData(ob, val, sub)
        elif key == 'MaterialAnimationData':
            try:
                ob = loadedData['Object'][val[0]]
            except:
                ob = None
            if ob:
                bpy.context.scene.objects.active = ob
                mat = ob.data.materials[int(val[2])]
                parseAnimationData(mat, val, sub)
        elif key == 'ShapeKeys':
            try:
                ob = loadedData['Object'][val[0]]
            except:
                MyError("ShapeKeys object %s does not exist" % val[0])
            if ob:
                bpy.context.scene.objects.active = ob
                parseShapeKeys(ob, ob.data, val, sub)
        else:
            data = parseDefaultType(key, val, sub)

    scn.layers = theLayers

#
#    parseDefaultType(typ, args, tokens):
#

def parseDefaultType(typ, args, tokens):
    name = args[0]
    data = None
    expr = "bpy.data.%s.new('%s')" % (Plural[typ], name)
    data = mhxEval(expr)

    bpyType = typ.capitalize()
    loadedData[bpyType][name] = data
    if data is None:
        return None

    for (key, val, sub) in tokens:
        defaultKey(key, val, sub, data)
    return data

#
#    concatList(elts)
#

def concatList(elts):
    string = ""
    for elt in elts:
        string += " %s" % elt
    return string

#
#    parseAction(args, tokens):
#    parseActionFCurve(act, args, tokens):
#

def parseAction(args, tokens):
    name = args[0]
    act = bpy.data.actions.new(name)
    for (key, val, sub) in tokens:
        if key == 'FCurve':
            fcu = parseActionFCurve(act, val, sub)
        else:
            defaultKey(key, val, sub, act)

    ob = bpy.context.object
    ob.keyframe_insert(data_path="location", frame=1)
    ob.animation_data.action = act
    return act


def parseActionFCurve(act, args, tokens):
    datapath = args[0]
    idx = int(args[1])
    words = datapath.split('"')
    if len(words) > 1:
        bone = words[1]
    fcu = act.fcurves.new(data_path=datapath, index=idx, action_group=bone)

    keypoints = [(float(val[0]), float(val[1])) for (key, val, sub) in tokens if key == 'kp']
    fcu.keyframe_points.add(len(keypoints))
    for n,kp in enumerate(keypoints):
        fcu.keyframe_points[n].co = kp

    for (key, val, sub) in tokens:
        if key != 'kp':
            defaultKey(key, val, sub, fcu)
    return fcu


#
#    parseAnimationData(rna, args, tokens):
#    parseDriver(drv, args, tokens):
#    parseDriverVariable(var, args, tokens):
#

def parseAnimationData(rna, args, tokens):
    if not mhxEval(args[1]):
        return
    if rna.animation_data is None:
        rna.animation_data_create()
    adata = rna.animation_data
    for (key, val, sub) in tokens:
        if key == 'FCurve':
            fcu = parseAnimDataFCurve(adata, rna, val, sub)
        else:
            defaultKey(key, val, sub, adata)
    return adata


def parseAnimDataFCurve(adata, rna, args, tokens):
    if invalid(args[2]):
        return
    dataPath = args[0]
    index = int(args[1])
    n = 1
    for (key, val, sub) in tokens:
        if key == 'Driver':
            fcu = parseDriver(adata, dataPath, index, rna, val, sub)
            if fcu is None:
                return None
            fmod = fcu.modifiers[0]
            fcu.modifiers.remove(fmod)
        elif key == 'FModifier':
            parseFModifier(fcu, val, sub)
        elif key == 'kp':
            pt = fcu.keyframe_points.insert(n, 0)
            pt.interpolation = 'LINEAR'
            pt = parseKeyFramePoint(pt, val, sub)
            n += 1
        else:
            defaultKey(key, val, sub, fcu)
    return fcu


def getRnaFromDataPath(rna, dataPath):
    # Want to split with ., but bone names may contain . as well,
    # e.g. pose.bones["toe.01.R"].rotation_euler
    import re
    literals = re.findall(r'\"(.+?)\"', dataPath)  # literals will be ['toe.01.R']
    for lit in literals:
        dataPath = dataPath.replace(lit, "$LITERAL$", 1)
    words = dataPath.split('.')
    litIdx = 0
    for word in words[0:-1]:
        if "$LITERAL$" in word:
            word = word.replace("$LITERAL$", literals[litIdx])
            litIdx += 1
        words2 = word.split("[")
        if len(words2) == 1:
            rna = getattr(rna, word)
        else:
            attr = words2[0]
            idx = mhxEval(words2[1][:-1])
            rna = getattr(rna, attr)[idx]
    return rna, words[-1]


def parseDriver(adata, dataPath, index, rna, args, tokens):
    rna,channel = getRnaFromDataPath(rna, dataPath)
    fcu = rna.driver_add(channel)
    if fcu is None:
        raise MyError("Cannot parse driver:\n  %s" % dataPath)

    drv = fcu.driver
    drv.type = args[0]
    for (key, val, sub) in tokens:
        if key == 'DriverVariable':
            var = parseDriverVariable(drv, rna, val, sub)
        else:
            defaultKey(key, val, sub, drv)
    return fcu


def parseDriverVariable(drv, rna, args, tokens):
    var = drv.variables.new()
    var.name = args[0]
    var.type = args[1]
    nTarget = 0
    for (key, val, sub) in tokens:
        if key == 'Target':
            parseDriverTarget(var, nTarget, rna, val, sub)
            nTarget += 1
        else:
            defaultKey(key, val, sub, var)
    return var


def parseFModifier(fcu, args, tokens):
    fmod = fcu.modifiers.new(args[0])
    #fmod = fcu.modifiers[0]
    for (key, val, sub) in tokens:
        defaultKey(key, val, sub, fmod)
    return fmod

"""
        var = driver.variables.new()
        var.name = target_bone
        var.targets[0].id_type = 'OBJECT'
        var.targets[0].id = obj
        var.targets[0].rna_path = driver_path
"""
def parseDriverTarget(var, nTarget, rna, args, tokens):
    targ = var.targets[nTarget]
    name = args[0]
    #targ.id_type = args[1]
    dtype = args[1].capitalize()
    dtype = 'Object'
    targ.id = loadedData[dtype][name]
    for (key, val, sub) in tokens:
        if key == 'data_path':
            words = val[0].split('"')
            if len(words) > 1:
                targ.data_path = propNames(words[1])[1]
            else:
                targ.data_path = propNames(val)[1]
        else:
            defaultKey(key, val, sub, targ)
    return targ


# ---------------------------------------------------------------------
#
# ---------------------------------------------------------------------
#
#    parseMaterial(args, ext, tokens):
#    parseMTex(mat, args, tokens):
#    parseTexture(args, tokens):
#

def parseMaterial(args, tokens):
    name = args[0]
    mat = bpy.data.materials.new(name)
    if mat is None:
        return None
    loadedData['Material'][name] = mat

    scn = bpy.context.scene
    if scn.render.engine == 'BLENDER_RENDER':
        parseMaterialBlenderRender(mat, tokens)
    elif scn.render.engine == 'CYCLES':
        parseMaterialCycles(mat, tokens)
    elif scn.render.engine == 'BLENDER_GAME':
        parseMaterialBlenderRender(mat, tokens)
        #parseMaterialBlenderGame(mat, tokens)
    return mat


class CMTex:
    def __init__(self, args):
        self.index = int(args[0])
        self.texname = args[1]
        self.texco = args[2]
        self.mapto = args[3]
        self.texture = loadedData['Texture'][self.texname]


class CMaterial:
    def __init__(self):
        self.diffuse_color = [1,1,1,1]
        self.specular_color =[1,1,1,1]
        self.specular_hardness = 50
        self.alpha = 1
        self.textures = {
            'COLOR' : None,
            'SPECULAR' : None,
            'NORMAL' : None,
            'BUMP' : None,
            'DISPLACEMENT' : None,
            }

    def parse(self, tokens):
        for (key, val, sub) in tokens:
            if key == 'MTex':
                cmtex = CMTex(val)
                self.textures[cmtex.mapto] = cmtex
            elif hasattr(self, key):
                defaultKey(key, val, sub, self)

        self.diffuse_color[3] = self.alpha
        self.specular_color[3] = self.alpha

    def hasTexture(self):
        for tex in self.textures.values():
            if tex is not None:
                return True
        return False

# ---------------------------------------------------------------------
#   Cycles materials
# ---------------------------------------------------------------------

def parseMaterialCycles(mat, tokens):
    print("Creating CYCLES material", mat.name)

    mat.use_nodes= True
    mat.node_tree.nodes.clear()
    cmat = CMaterial()
    cmat.parse(tokens)

    ycoord1 = 1
    ycoord2 = 1
    ycoord3 = 1
    ycoord4 = 1
    dy1 = 300
    dy2 = 300
    dy3 = 200
    dy4 = 200

    if cmat.hasTexture():
        texco = mat.node_tree.nodes.new(type = 'ShaderNodeTexCoord')
        texco.location = (1, ycoord1)
        ycoord1 += dy1

    if cmat.textures['NORMAL']:
        normalTex = mat.node_tree.nodes.new(type = 'ShaderNodeTexImage')
        normalTex.image = cmat.textures['NORMAL'].texture.image
        normalTex.location = (251, ycoord2)
        ycoord2 += dy2
        mat.node_tree.links.new(texco.outputs['UV'], normalTex.inputs['Vector'])
        normalMap = mat.node_tree.nodes.new(type = 'ShaderNodeNormalMap')
        normalMap.space = 'TANGENT'
        mat.node_tree.links.new(normalTex.outputs['Color'], normalMap.inputs['Color'])
        normalMap.location = (501, ycoord3)
        ycoord3 += dy3
    else:
        normalMap = None

    diffuse = mat.node_tree.nodes.new(type = 'ShaderNodeBsdfDiffuse')
    diffuse.inputs["Color"].default_value = cmat.diffuse_color
    diffuse.inputs["Roughness"].default_value = 0
    diffuse.location = (501, ycoord3)
    ycoord3 += dy3
    transparent = None
    if cmat.textures['COLOR']:
        diffuseTex = mat.node_tree.nodes.new(type = 'ShaderNodeTexImage')
        diffuseTex.image = cmat.textures['COLOR'].texture.image
        mat.node_tree.links.new(texco.outputs['UV'], diffuseTex.inputs['Vector'])
        mat.node_tree.links.new(diffuseTex.outputs['Color'], diffuse.inputs['Color'])
        diffuseTex.location = (251, ycoord2)
        ycoord2 += dy2
        transparent = mat.node_tree.nodes.new(type = 'ShaderNodeBsdfTransparent')
        transparent.location = (501, ycoord3)
        ycoord3 += dy3
    if normalMap is not None:
        mat.node_tree.links.new(normalMap.outputs['Normal'], diffuse.inputs['Normal'])

    glossy = mat.node_tree.nodes.new(type = 'ShaderNodeBsdfGlossy')
    glossy.inputs["Color"].default_value = cmat.specular_color
    glossy.inputs["Roughness"].default_value = 0
    glossy.location = (501, ycoord3)
    ycoord3 += dy3
    if cmat.textures['SPECULAR']:
        glossyTex = mat.node_tree.nodes.new(type = 'ShaderNodeTexImage')
        glossyTex.image = cmat.textures['SPECULAR'].texture.image
        mat.node_tree.links.new(texco.outputs['UV'], glossyTex.inputs['Vector'])
        mat.node_tree.links.new(glossyTex.outputs['Color'], glossy.inputs['Color'])
        glossyTex.location = (251, ycoord2)
        ycoord2 += dy2
    if normalMap is not None:
        mat.node_tree.links.new(normalMap.outputs['Normal'], glossy.inputs['Normal'])

    mixGloss = mat.node_tree.nodes.new(type = 'ShaderNodeMixShader')
    mixGloss.inputs['Fac'].default_value = 0.02
    mat.node_tree.links.new(diffuse.outputs['BSDF'], mixGloss.inputs[1])
    mat.node_tree.links.new(glossy.outputs['BSDF'], mixGloss.inputs[2])
    mixGloss.location = (751, ycoord4)
    ycoord4 += dy4

    if transparent is not None:
        mixTrans = mat.node_tree.nodes.new(type = 'ShaderNodeMixShader')
        mat.node_tree.links.new(diffuseTex.outputs['Alpha'], mixTrans.inputs['Fac'])
        mat.node_tree.links.new(transparent.outputs['BSDF'], mixTrans.inputs[1])
        mat.node_tree.links.new(mixGloss.outputs['Shader'], mixTrans.inputs[2])
        mixTrans.location = (751, ycoord4)
        ycoord4 += dy4
    else:
        mixTrans = mixGloss

    output = mat.node_tree.nodes.new(type = 'ShaderNodeOutputMaterial')
    mat.node_tree.links.new(mixTrans.outputs['Shader'], output.inputs['Surface'])
    output.location = (1001, 1)

    return mat

# ---------------------------------------------------------------------
#   Blender Game engine materials
# ---------------------------------------------------------------------

def parseMaterialBlenderGame(mat, tokens):
    print("Creating BLENDER GAME material", mat.name)

# ---------------------------------------------------------------------
#   Blender Internal materials
# ---------------------------------------------------------------------

def parseMaterialBlenderRender(mat, tokens):
    print("Creating BLENDER RENDER material", mat.name)
    for (key, val, sub) in tokens:
        if key == 'MTex':
            parseMTex(mat, val, sub)
        elif key == 'Ramp':
            parseRamp(mat, val, sub)
        elif key == 'RaytraceTransparency':
            parseDefault(mat.raytrace_transparency, sub, {}, [])
        elif key == 'Halo':
            parseDefault(mat.halo, sub, {}, [])
        elif key == 'SSS':
            parseDefault(mat.subsurface_scattering, sub, {}, [])
        elif key == 'Strand':
            parseDefault(mat.strand, sub, {}, [])
        elif key == 'AnimationData':
            parseAnimationData(mat, val, sub)
        else:
            exclude = ['specular_intensity', 'tangent_shading']
            defaultKey(key, val, sub, mat)


def parseMTex(mat, args, tokens):
    cmtex = CMTex(args)
    mtex = mat.texture_slots.add()
    mtex.texture_coords = cmtex.texco
    mtex.texture = cmtex.texture
    for (key, val, sub) in tokens:
        defaultKey(key, val, sub, mtex)
    return mtex


def parseTexture(args, tokens):
    if verbosity > 2:
        print( "Parsing texture %s" % args )
    name = args[0]
    tex = bpy.data.textures.new(name=name, type=args[1])
    loadedData['Texture'][name] = tex

    for (key, val, sub) in tokens:
        if key == 'Image':
            try:
                imgName = val[0]
                img = loadedData['Image'][imgName]
                tex.image = img
            except:
                msg = "Unable to load image '%s'" % val[0]
        elif key == 'Ramp':
            parseRamp(tex, val, sub)
        elif key == 'NodeTree':
            tex.use_nodes = True
            parseNodeTree(tex.node_tree, val, sub)
        else:
            defaultKey(key, val, sub, tex, ['use_nodes', 'use_textures', 'contrast', 'use_alpha'])

    return tex

def parseRamp(data, args, tokens):
    setattr(data, "use_%s" % args[0], True)
    ramp = getattr(data, args[0])
    elts = ramp.elements
    n = 0
    for (key, val, sub) in tokens:
        if key == 'Element':
            elts[n].color = mhxEval(val[0], locals())
            elts[n].position = mhxEval(val[1], locals())
            n += 1
        else:
            defaultKey(key, val, sub, tex, ['use_nodes', 'use_textures', 'contrast'])

def parseSSS(mat, args, tokens):
    sss = mat.subsurface_scattering
    for (key, val, sub) in tokens:
        defaultKey(key, val, sub, sss)

def parseStrand(mat, args, tokens):
    strand = mat.strand
    for (key, val, sub) in tokens:
        defaultKey(key, val, sub, strand)



#
#    loadImage(filepath):
#    parseImage(args, tokens):
#

def loadImage(relFilepath):
    filepath = os.path.normpath(os.path.join(theDir, relFilepath))
    print( "Loading %s" % filepath.encode('utf-8','strict'))
    if os.path.isfile(filepath):
        #print( "Found file %s." % filepath.encode('utf-8','strict') )
        try:
            img = bpy.data.images.load(filepath)
            return img
        except:
            print( "Cannot read image" )
            return None
    else:
        print( "No such file: %s" % filepath.encode('utf-8','strict') )
        return None


def parseImage(args, tokens):
    imgName = args[0]
    img = None
    for (key, val, sub) in tokens:
        if key == 'Filename':
            filename = val[0]
            for n in range(1,len(val)):
                filename += " " + val[n]
            img = loadImage(filename)
            if img is None:
                return None
            img.name = imgName
        else:
            defaultKey(key, val, sub, img, ['depth', 'dirty', 'has_data', 'size', 'type', 'use_premultiply'])
    print ("Image %s" % img )
    loadedData['Image'][imgName] = img
    return img

#
#    parseObject(args, tokens):
#    createObject(type, name, data, datName):
#    setObjectAndData(args, typ):
#

def parseObject(args, tokens, versionInfoStr=""):
    global theLayers

    if verbosity > 2:
        print( "Parsing object %s" % args )
    name = args[0]
    typ = args[1]
    datName = args[2]

    if typ == 'EMPTY':
        ob = bpy.data.objects.new(name, None)
        loadedData['Object'][name] = ob
        linkObject(ob, None)
    else:
        try:
            data = loadedData[typ.capitalize()][datName]
        except:
            MyError("Failed to find data: %s %s %s" % (name, typ, datName))
            return

    try:
        ob = loadedData['Object'][name]
        bpy.context.scene.objects.active = ob
        #print("Found data", ob)
    except:
        ob = None

    if ob is None:
        ob = createObject(typ, name, data, datName)
        linkObject(ob, data)

    for (key, val, sub) in tokens:
        if key == 'Modifier':
            parseModifier(ob, val, sub)
        elif key == 'Constraint':
            parseConstraint(ob.constraints, None, val, sub)
        elif key == 'AnimationData':
            parseAnimationData(ob, val, sub)
        elif key == 'ParticleSystem':
            parseParticleSystem(ob, val, sub)
        elif key == 'FieldSettings':
            parseDefault(ob.field, sub, {}, [])
        elif key == 'layers':
            if val[-1] == '1':
                ob.layers = 19*[False] + [True]
            else:
                ob.layers = theLayers
            print(ob.name, list(ob.layers))
        else:
            defaultKey(key, val, sub, ob, ['type', 'data'])

    if versionInfoStr:
        ob.MhxVersionStr = versionInfoStr

    if bpy.context.object == ob:
        if ob.type == 'MESH':
            bpy.ops.object.shade_smooth()
    else:
        print("Context", ob, bpy.context.object, bpy.context.scene.objects.active)
    return

def createObject(typ, name, data, datName):
    # print( "Creating object %s %s %s" % (typ, name, data) )
    ob = bpy.data.objects.new(name, data)
    if data:
        loadedData[typ.capitalize()][datName] = data
    loadedData['Object'][name] = ob
    return ob

def linkObject(ob, data):
    #print("Data", data, ob.data)
    if data and ob.data is None:
        ob.data = data
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    #print("Linked object", ob)
    #print("Scene", scn)
    #print("Active", scn.objects.active)
    #print("Context", bpy.context.object)
    return ob

def setObjectAndData(args, typ):
    datName = args[0]
    obName = args[1]
    #bpy.ops.object.add(type=typ)
    ob = bpy.context.object
    ob.name = obName
    ob.data.name = datName
    loadedData[typ][datName] = ob.data
    loadedData['Object'][obName] = ob
    return ob.data


#
#    parseModifier(ob, args, tokens):
#


def parseModifier(ob, args, tokens):
    name = args[0]
    typ = args[1]
    if typ == 'PARTICLE_SYSTEM':
        return None
    mod = ob.modifiers.new(name, typ)
    for (key, val, sub) in tokens:
        if key == 'HookAssignNth':
            if val[0] == 'CURVE':
                hookAssignNth(mod, int(val[1]), True, ob.data.splines[0].points)
            elif val[0] == 'LATTICE':
                hookAssignNth(mod, int(val[1]), False, ob.data.points)
            elif val[0] == 'MESH':
                hookAssignNth(mod, int(val[1]), True, ob.data.vertices)
            else:
                MyError("Unknown hook %s" % val)
        else:
            defaultKey(key, val, sub, mod)
    return mod

def hookAssignNth(mod, n, select, points):
    if select:
        for pt in points:
            pt.select = False
        points[n].select = True
        sel = []
        for pt in points:
            sel.append(pt.select)
        #print(mod, sel, n, points)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.hook_reset(modifier=mod.name)
    bpy.ops.object.hook_select(modifier=mod.name)
    bpy.ops.object.hook_assign(modifier=mod.name)
    bpy.ops.object.mode_set(mode='OBJECT')
    return

#
#    parseParticleSystem(ob, args, tokens):
#    parseParticles(particles, args, tokens):
#    parseParticle(par, args, tokens):
#

def parseParticleSystem(ob, args, tokens):
    print(ob, bpy.context.object)
    pss = ob.particle_systems
    print(pss, pss.values())
    name = args[0]
    typ = args[1]
    #psys = pss.new(name, typ)
    bpy.ops.object.particle_system_add()
    print(pss, pss.values())
    psys = pss[-1]
    psys.name = name
    psys.settings.type = typ
    loadedData['ParticleSystem'][name] = psys
    print("Psys", psys)

    for (key, val, sub) in tokens:
        if key == 'Particles':
            parseParticles(psys, val, sub)
        else:
            defaultKey(key, val, sub, psys)
    return psys

def parseParticles(psys, args, tokens):
    particles = psys.particles
    bpy.ops.particle.particle_edit_toggle()
    n = 0
    for (key, val, sub) in tokens:
        if key == 'Particle':
            parseParticle(particles[n], val, sub)
            n += 1
        else:
            for par in particles:
                defaultKey(key, val, sub, par)
    bpy.ops.particle.particle_edit_toggle()
    return particles

def parseParticle(par, args, tokens):
    n = 0
    for (key, val, sub) in tokens:
        if key == 'h':
            h = par.hair[n]
            h.location = mhxEval(val[0], locals())
            h.time = int(val[1])
            h.weight = float(val[2])
            n += 1
        elif key == 'location':
            par.location = mhxEval(val[0], locals())
    return

#
#    unpackList(list_of_tuples):
#

def unpackList(list_of_tuples):
    l = []
    for t in list_of_tuples:
        l.extend(t)
    return l


#

#    parseMesh (args, tokens):
#

def parseMesh (args, tokens):
    global BMeshAware
    if verbosity > 2:
        print( "Parsing mesh %s" % args )

    mename = args[0]
    obname = args[1]
    me = bpy.data.meshes.new(mename)
    ob = createObject('MESH', obname, me, mename)

    verts = []
    edges = []
    faces = []
    vertsTex = []
    texFaces = []

    for (key, val, sub) in tokens:
        if key == 'Verts':
            verts = parseVerts(sub)
        elif key == 'Edges':
            edges = parseEdges(sub)
        elif key == 'Faces':
            faces = parseFaces(sub)

    print("Create mesh with %d verts and %d faces" % (len(verts), len(faces)))
    if faces:
        me.from_pydata(verts, [], faces)
    else:
        me.from_pydata(verts, edges, [])
    me.update()
    linkObject(ob, me)
    print("Created %s and %s" % (me, ob))

    if faces:
        try:
            me.polygons
            BMeshAware = True
        except:
            BMeshAware = False

    mats = []
    nuvlayers = 0
    for (key, val, sub) in tokens:
        if key == 'Verts' or key == 'Edges' or key == 'Faces':
            pass
        elif key == 'MeshTextureFaceLayer':
            if BMeshAware:
                parseUvTextureBMesh(val, sub, me)
            else:
                parseUvTextureNoBMesh(val, sub, me)
        elif key == 'MeshColorLayer':
            parseVertColorLayer(val, sub, me)
        elif key == 'VertexGroup':
            parseVertexGroup(ob, me, val, sub)
        elif key == 'ShapeKeys':
            parseShapeKeys(ob, me, val, sub)
        elif key == 'Material':
            try:
                mat = loadedData['Material'][val[0]]
            except:
                mat = None
            if mat:
                me.materials.append(mat)
        else:
            defaultKey(key, val, sub, me)

    for (key, val, sub) in tokens:
        if key == 'Faces':
            if BMeshAware:
                parseFaces2BMesh(sub, me)
            else:
                parseFaces2NoBMesh(sub, me)
    return me

#
#    parseVerts(tokens):
#    parseEdges(tokens):
#    parseFaces(tokens):
#    parseFaces2(tokens, me):
#

def parseVerts(tokens):
    verts = []
    for (key, val, sub) in tokens:
        if key == 'v':
            verts.append( (float(val[0]), float(val[1]), float(val[2])) )
    return verts

def parseEdges(tokens):
    edges = []
    for (key, val, sub) in tokens:
        if key == 'e':
            edges.append((int(val[0]), int(val[1])))
    return edges

def parseFaces(tokens):
    faces = []
    for (key, val, sub) in tokens:
        if key == 'f':
            if len(val) == 3:
                face = [int(val[0]), int(val[1]), int(val[2])]
            elif len(val) == 4:
                face = [int(val[0]), int(val[1]), int(val[2]), int(val[3])]
            faces.append(face)
    return faces

def parseFaces2BMesh(tokens, me):
    n = 0
    for (key, val, sub) in tokens:
        if key == 'ft':
            f = me.polygons[n]
            f.material_index = int(val[0])
            f.use_smooth = int(val[1])
            n += 1
        elif key == 'ftn':
            mn = int(val[1])
            us = int(val[2])
            npts = int(val[0])
            for i in range(npts):
                f = me.polygons[n]
                f.material_index = mn
                f.use_smooth = us
                n += 1
        elif key == 'mn':
            fn = int(val[0])
            mn = int(val[1])
            f = me.polygons[fn]
            f.material_index = mn
        elif key == 'ftall':
            mat = int(val[0])
            smooth = int(val[1])
            for f in me.polygons:
                f.material_index = mat
                f.use_smooth = smooth
    return

def parseFaces2NoBMesh(tokens, me):
    n = 0
    for (key, val, sub) in tokens:
        if key == 'ft':
            f = me.faces[n]
            f.material_index = int(val[0])
            f.use_smooth = int(val[1])
            n += 1
        elif key == 'ftn':
            mn = int(val[1])
            us = int(val[2])
            npts = int(val[0])
            for i in range(npts):
                f = me.faces[n]
                f.material_index = mn
                f.use_smooth = us
                n += 1
        elif key == 'mn':
            fn = int(val[0])
            mn = int(val[1])
            f = me.faces[fn]
            f.material_index = mn
        elif key == 'ftall':
            mat = int(val[0])
            smooth = int(val[1])
            for f in me.faces:
                f.material_index = mat
                f.use_smooth = smooth
    return


#
#    parseUvTexture(args, tokens, me,):
#    parseUvTexData(args, tokens, uvdata):
#

def parseUvTextureBMesh(args, tokens, me):
    name = args[0]
    bpy.ops.mesh.uv_texture_add()
    uvtex = me.uv_textures[-1]
    uvtex.name = name
    uvloop = me.uv_layers[-1]
    loadedData['MeshTextureFaceLayer'][name] = uvloop
    for (key, val, sub) in tokens:
        if key == 'Data':
            parseUvTexDataBMesh(val, sub, uvloop.data)
        else:
            defaultKey(key, val, sub, uvtex)
    return

def parseUvTexDataBMesh(args, tokens, data):
    n = 0
    for (key, val, sub) in tokens:
        if key == 'vt':
            data[n].uv = (float(val[0]), float(val[1]))
            n += 1
            data[n].uv = (float(val[2]), float(val[3]))
            n += 1
            data[n].uv = (float(val[4]), float(val[5]))
            n += 1
            if len(val) > 6:
                data[n].uv = (float(val[6]), float(val[7]))
                n += 1
    return

def parseUvTextureNoBMesh(args, tokens, me):
    name = args[0]
    uvtex = me.uv_textures.new(name = name)
    loadedData['MeshTextureFaceLayer'][name] = uvtex
    for (key, val, sub) in tokens:
        if key == 'Data':
            parseUvTexDataNoBMesh(val, sub, uvtex.data)
        else:
            defaultKey(key, val, sub, uvtex)
    return

def parseUvTexDataNoBMesh(args, tokens, data):
    n = 0
    for (key, val, sub) in tokens:
        if key == 'vt':
            data[n].uv1 = (float(val[0]), float(val[1]))
            data[n].uv2 = (float(val[2]), float(val[3]))
            data[n].uv3 = (float(val[4]), float(val[5]))
            if len(val) > 6:
                data[n].uv4 = (float(val[6]), float(val[7]))
            n += 1
    return

#
#    parseVertColorLayer(args, tokens, me):
#    parseVertColorData(args, tokens, data):
#

def parseVertColorLayer(args, tokens, me):
    name = args[0]
    print("VertColorLayer", name)
    vcol = me.vertex_colors.new(name)
    loadedData['MeshColorLayer'][name] = vcol
    for (key, val, sub) in tokens:
        if key == 'Data':
            parseVertColorData(val, sub, vcol.data)
        else:
            defaultKey(key, val, sub, vcol)
    return

def parseVertColorData(args, tokens, data):
    n = 0
    for (key, val, sub) in tokens:
        if key == 'cv':
            data[n].color1 = mhxEval(val[0])
            data[n].color2 = mhxEval(val[1])
            data[n].color3 = mhxEval(val[2])
            data[n].color4 = mhxEval(val[3])
            n += 1
    return


#
#    parseVertexGroup(ob, me, args, tokens):
#

def parseVertexGroup(ob, me, args, tokens):
    global toggle
    if verbosity > 2:
        print( "Parsing vertgroup %s" % args )
    grpName = args[0]
    try:
        res = mhxEval(args[1])
    except:
        res = True
    if not res:
        return

    if (toggle & T_Armature) or (grpName in ['Eye_L', 'Eye_R', 'Gums', 'Head', 'Jaw', 'Left', 'Middle', 'Right', 'Scalp']):
        try:
            group = loadedData['VertexGroup'][grpName]
        except KeyError:
            group = ob.vertex_groups.new(grpName)
            loadedData['VertexGroup'][grpName] = group
        for (key, val, sub) in tokens:
            if key == 'wv':
                group.add( [int(val[0])], float(val[1]), 'REPLACE' )
    return


#
#    parseShapeKeys(ob, me, args, tokens):
#    parseShapeKey(ob, me, args, tokens):
#    addShapeKey(ob, name, vgroup, tokens):
#    doShape(name):
#

def doShape(name):
    if (toggle & T_Shapekeys) and (name == 'Basis'):
        return True
    else:
        return (toggle & T_Face)


def parseShapeKeys(ob, me, args, tokens):
    for (key, val, sub) in tokens:
        if key == 'ShapeKey':
            parseShapeKey(ob, me, val, sub)
        elif key == 'AnimationData':
            if me.shape_keys:
                parseAnimationData(me.shape_keys, val, sub)
        elif key == 'Expression':
            prop = "Mhe" + val[0].capitalize()
            parseUnits(prop, ob, sub)
        elif key == 'Viseme':
            name = val[0].upper()
            if name in ["REST", "ETC"]:
                name = name.capitalize()
            prop = "Mhv" + name
            parseUnits(prop, ob, sub)
    ob.active_shape_key_index = 0


def parseUnits(prop, ob, sub):
    string = ""
    for words in sub:
        unit = words[0].replace("-","_")
        value = words[1][0]
        string += "%s:%s;" % (unit, value)
    rig = ob.parent
    rig[prop] = string


def parseShapeKey(ob, me, args, tokens):
    if verbosity > 2:
        print( "Parsing ob %s shape %s" % (bpy.context.object, args[0] ))
    name = args[0]
    lr = args[1]
    if invalid(args[2]):
        return

    if lr == 'Sym': # or toggle & T_Symm:
        addShapeKey(ob, name, None, tokens)
    elif lr == 'LR':
        addShapeKey(ob, name+'_L', 'Left', tokens)
        addShapeKey(ob, name+'_R', 'Right', tokens)
    else:
        MyError("ShapeKey L/R %s" % lr)
    return


def addShapeKey(ob, name, vgroup, tokens):
    skey = ob.shape_key_add(name=name, from_mix=False)
    if name != 'Basis':
        skey.relative_key = loadedData['ShapeKey']['Basis']
    skey.name = name
    if vgroup:
        skey.vertex_group = vgroup
    loadedData['ShapeKey'][name] = skey

    for (key, val, sub) in tokens:
        if key == 'sv':
            index = int(val[0])
            pt = skey.data[index].co
            pt[0] += float(val[1])
            pt[1] += float(val[2])
            pt[2] += float(val[3])
        else:
            defaultKey(key, val, sub, skey)

    return


#
#    parseArmature (obName, args, tokens)
#

def parseArmature (args, tokens):
    global toggle, theArmature
    if verbosity > 2:
        print( "Parsing armature %s" % args )

    amtname = args[0]
    obname = args[1]
    mode = args[2]

    amt = bpy.data.armatures.new(amtname)
    ob = createObject('ARMATURE', obname, amt, amtname)
    linkObject(ob, amt)
    theArmature = ob

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')

    heads = {}
    tails = {}
    for (key, val, sub) in tokens:
        if key == 'Bone':
            bname = val[0]
            if not invalid(val[1]):
                bone = amt.edit_bones.new(bname)
                parseBone(bone, amt, sub, heads, tails)
                loadedData['Bone'][bname] = bone
        elif key == 'RecalcRoll':
            rolls = {}
            for bone in amt.edit_bones:
                bone.select = False
            blist = mhxEval(val[0])
            for name in blist:
                bone = amt.edit_bones[name]
                bone.select = True
            bpy.ops.armature.calculate_roll(type='Z')
            for bone in amt.edit_bones:
                rolls[bone.name] = bone.roll
            bpy.ops.object.mode_set(mode='OBJECT')
            for bone in amt.bones:
                bone['Roll'] = rolls[bone.name]
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            defaultKey(key, val, sub, amt, ['MetaRig'])
    bpy.ops.object.mode_set(mode='OBJECT')

    return amt

#
#    parseBone(bone, amt, tokens, heads, tails):
#

def parseBone(bone, amt, tokens, heads, tails):
    for (key, val, sub) in tokens:
        if key == "head":
            bone.head = (float(val[0]), float(val[1]), float(val[2]))
        elif key == "tail":
            bone.tail = (float(val[0]), float(val[1]), float(val[2]))
        #elif key == 'restrict_select':
        #    pass
        elif key == 'hide' and val[0] == 'True':
            name = bone.name
        else:
            defaultKey(key, val, sub, bone)
    return bone

#
#    parsePose (args, tokens):
#

def parsePose (args, tokens):
    name = args[0]
    ob = loadedData['Object'][name]
    bpy.context.scene.objects.active = ob
    bpy.ops.object.mode_set(mode='POSE')
    pbones = ob.pose.bones
    nGrps = 0
    for (key, val, sub) in tokens:
        if key == 'Posebone':
            parsePoseBone(pbones, ob, val, sub)
        elif key == 'BoneGroup':
            parseBoneGroup(ob.pose, nGrps, val, sub)
            nGrps += 1
        elif key == 'SetProp':
            bone = val[0]
            prop = val[1]
            value = mhxEval(val[2])
            pb = pbones[bone]
            pb[prop] = value
        else:
            defaultKey(key, val, sub, ob.pose)
    bpy.ops.object.mode_set(mode='OBJECT')
    return ob


#
#    parsePoseBone(pbones, args, tokens):
#    parseArray(data, exts, args):
#

def parseBoneGroup(pose, nGrps, args, tokens):
    if verbosity > 2:
        print( "Parsing bonegroup %s" % args )
    name = args[0]
    bpy.ops.pose.group_add()
    bg = pose.bone_groups.active
    loadedData['BoneGroup'][name] = bg
    for (key, val, sub) in tokens:
        defaultKey(key, val, sub, bg)
    return

def parsePoseBone(pbones, ob, args, tokens):
    if invalid(args[1]):
        return
    name = args[0]
    pb = pbones[name]
    amt = ob.data
    amt.bones.active = pb.bone

    for (key, val, sub) in tokens:
        if key == 'Constraint':
            amt.bones.active = pb.bone
            cns = parseConstraint(pb.constraints, pb, val, sub)
        elif key == 'bpyops':
            amt.bones.active = pb.bone
            expr = "bpy.ops.%s" % val[0]
            raise MhxError("MHX bug: Must not exec %s" % expr)
        elif key == 'ik_dof':
            parseArray(pb, ["ik_dof_x", "ik_dof_y", "ik_dof_z"], val)
        elif key == 'ik_limit':
            parseArray(pb, ["ik_limit_x", "ik_limit_y", "ik_limit_z"], val)
        elif key == 'ik_max':
            parseArray(pb, ["ik_max_x", "ik_max_y", "ik_max_z"], val)
        elif key == 'ik_min':
            parseArray(pb, ["ik_min_x", "ik_min_y", "ik_min_z"], val)
        elif key == 'ik_stiffness':
            parseArray(pb, ["ik_stiffness_x", "ik_stiffness_y", "ik_stiffness_z"], val)
        elif key == 'hide':
            #bpy.ops.object.mode_set(mode='OBJECT')
            amt.bones[name].hide = mhxEval(val[0])
            #bpy.ops.object.mode_set(mode='POSE')

        else:
            defaultKey(key, val, sub, pb)
    return

def parseArray(data, exts, args):
    n = 1
    for ext in exts:
        setattr(data, ext, mhxEval(args[n]))
        n += 1
    return

#
#    parseConstraint(constraints, pb, args, tokens)
#

def parseConstraint(constraints, pb, args, tokens):
    if invalid(args[2]):
        return None

    cns = constraints.new(args[1])
    cns.name = args[0]
    for (key,val,sub) in tokens:
        if key == 'invert':
            parseArray(cns, ["invert_x", "invert_y", "invert_z"], val)
        elif key == 'use':
            parseArray(cns, ["use_x", "use_y", "use_z"], val)
        elif key == 'pos_lock':
            parseArray(cns, ["lock_location_x", "lock_location_y", "lock_location_z"], val)
        elif key == 'rot_lock':
            parseArray(cns, ["lock_rotation_x", "lock_rotation_y", "lock_rotation_z"], val)
        else:
            defaultKey(key, val, sub, cns, ["use_target"])


    #print("cns %s done" % cns.name)
    return cns

#
#    parseGroup (args, tokens):
#    parseGroupObjects(args, tokens, grp):
#

def parseGroup (args, tokens):
    if verbosity > 2:
        print( "Parsing group %s" % args )

    grpName = args[0]
    grp = bpy.data.groups.new(grpName)
    loadedData['Group'][grpName] = grp
    for (key, val, sub) in tokens:
        if key == 'Objects':
            parseGroupObjects(val, sub, grp)
        else:
            defaultKey(key, val, sub, grp)
    return

def parseGroupObjects(args, tokens, grp):
    rig = None
    for (key, val, sub) in tokens:
        if key == 'ob':
            try:
                ob = loadedData['Object'][val[0]]
                grp.objects.link(ob)
            except:
                ob = None
            if ob:
                print(ob, ob.type, rig, ob.parent)
                if ob.type == 'ARMATURE':
                    rig = ob
                elif ob.type == 'EMPTY' and rig and not ob.parent:
                    ob.parent = rig
                    print("SSS")
    return

#
#    parseDefineProperty(args, tokens):
#

def parseDefineProperty(args, tokens):
    prop = "%sProperty" % (args[1])
    c = '('
    for option in args[2:]:
        prop += "%s %s" % (c, option)
        c = ','
    prop += ')'
    setattr(bpy.types.Object, args[0], prop)
    return

#
#    correctRig(args):
#

def correctRig(args):
    human = args[0]
    print("CorrectRig %s" % human)
    try:
        ob = loadedData['Object'][human]
    except:
        return
    bpy.context.scene.objects.active = ob
    bpy.ops.object.mode_set(mode='POSE')
    amt = ob.data
    cnslist = []
    for pb in ob.pose.bones:
        pb.bone.select = False
        for cns in pb.constraints:
            if cns.type == 'CHILD_OF':
                cnslist.append((pb, cns, cns.influence))
                cns.influence = 0

    for (pb, cns, inf) in cnslist:
        amt.bones.active = pb.bone
        cns.influence = 1
        #print("Childof %s %s %s %.2f" % (amt.name, pb.name, cns.name, inf))
        bpy.ops.constraint.childof_clear_inverse(constraint=cns.name, owner='BONE')
        bpy.ops.constraint.childof_set_inverse(constraint=cns.name, owner='BONE')
        cns.influence = 0

    for (pb, cns, inf) in cnslist:
        cns.influence = inf
    return


#
#    postProcess(args)
#

def postProcess(args):
    human = args[0]
    print("Postprocess %s" % human)
    try:
        ob = loadedData['Object'][human]
    except:
        ob = None
    if toggle & T_Diamond == 0 and ob:
        deleteDiamonds(ob)
    return

#
#    deleteDiamonds(ob)
#    Delete joint diamonds in main mesh
#    Invisio = material # 1
#

def deleteDiamonds(ob):
    bpy.context.scene.objects.active = ob
    if not bpy.context.object:
        return

    print("Delete helper geometry in %s" % bpy.context.object)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    me = ob.data
    invisioNum = -1
    for mn,mat in enumerate(me.materials):
        if mat.name[-7:] == "Invisio":
            invisioNum = mn
            break

    if invisioNum < 0:
        print("WARNING: Nu Invisio material found. Cannot delete helper geometry")
        return
    elif BMeshAware:
        for f in me.polygons:
            if f.material_index >= invisioNum:
                for vn in f.vertices:
                    me.vertices[vn].select = True
    else:
        for f in me.faces:
            if f.material_index >= invisioNum:
                for vn in f.vertices:
                    me.vertices[vn].select = True

    if BMeshAware and toggle&T_CrashSafe:
        theMessage = (
            "\n  *** WARNING ***\n" +
            "Helper deletion turned off due to Blender crash.\n" +
            "Helpers can be deleted by deleting all selected vertices in Edit mode\n" +
            "**********\n")
        print(theMessage)
    else:
        bpy.ops.object.mode_set(mode='EDIT')
        print("Do delete")
        bpy.ops.mesh.delete(type='VERT')
        print("Verts deleted")
        bpy.ops.object.mode_set(mode='OBJECT')
        print("Back to object mode")

    for mn in range(invisioNum, len(me.materials)):
        mat = me.materials.pop()
        bpy.data.materials.remove(mat)

#
#    defaultKey(ext, args, tokens, data, exclude):
#

theProperty = None

def propNames(string):
    global alpha7
    #string = string.encode('utf-8', 'strict')

    # Alpha 7 compatibility
    if string[0:2] == "&_":
        string = "Mhf"+string[2:]
        alpha7 = True
    elif string[0] == "&":
        string = "Mha"+string[1:]
        alpha7 = True
    elif string[0] == "*":
        string = "Mhs"+string[1:]
        alpha7 = True
    elif len(string) > 4 and string[0:4] == "Hide":
        string = "Mhh"+string[4:]
        alpha7 = True

    if string[0] == "_":
        return None,None
    elif (len(string) > 3 and
          string[0:3] in ["Mha", "Mhf", "Mhs", "Mhh", "Mhv", "Mhc"]):
        name = string.replace("-","_")
        return name, '["%s"]' % name
    else:
        return string, '["%s"]' % string


def defProp(args, var):
    proptype = args[0]
    name = propNames(args[1])[0]
    value = args[2]
    rest = 'description="%s"' % args[3].replace("_", " ")
    if len(args) > 4:
        rest += ", " + args[4]

    if name:
        var[name] = value


def defNewProp(name, proptype, rest):
    prop = "%sProperty(%s)" % (proptype, rest)
    setattr(bpy.types.Object, name, eval(prop)) # safe: only called from this file


def setProperty(args, var):
    global theProperty
    tip = ""
    name = propNames(args[0])[0]
    value = mhxEval(args[1])
    if name:
        var[name] = value
        if len(args) > 2:
            tip = 'description="%s"' % args[2].replace("_", " ")
        theProperty = (name, tip, value)


def setPropKeys(args):
    global theProperty
    if theProperty is None:
        return
    (name, tip, value) = theProperty
    if len(args) >= 2 and not isinstance(value, bool):
        if "BOOLEAN" in args[1]:
            value = bool(value)
        else:
            tip = tip + "," + args[1].replace(":", "=").replace('"', " ")
    #expr = "bpy.types.Object.%s = %sProperty(%s)" % (name, proptype, tip)
    if isinstance(value, bool):
        prop = BoolProperty(tip)
    elif isinstance(value, int):
        prop = IntProperty(tip)
    elif isinstance(value, float):
        prop = FloatProperty(tip)
    elif isinstance(value, string):
        prop = StringProperty(tip)
    setattr(bpy.types.Object, name, prop)
    theProperty = None


def defaultKey(ext, args, tokens, var, exclude=[]):
    if ext == 'Property':
        return setProperty(args, var)
    elif ext == 'PropKeys':
        return setPropKeys(args)
    elif ext == 'DefProp':
        return defProp(args, var)

    if ext == 'bpyops':
        expr = "bpy.ops.%s" % args[0]
        print(expr)
        raise MhxError("MHX bug: calling %s" % expr)

    if ext in exclude:
        return
    nvar = getattr(var, ext)

    if len(args) == 0:
        MyError("Key length 0: %s" % ext)

    rnaType = args[0]
    if rnaType == 'Refer':
        typ = args[1]
        name = args[2]
        setattr(var, ext, loadedData[typ][name])
        return

    elif rnaType == 'Struct' or rnaType == 'Define':
        raise MhxError("Struct/Define!")
        typ = args[1]
        name = args[2]
        try:
            data = getattr(var, ext)
        except:
            data = None
        # print("Old structrna", nvar, data)

        if data is None:
            try:
                creator = args[3]
            except:
                creator = None

            try:
                rna = mhxEval(var, locals())
                data = mhxEval(creator)
            except:
                data = None
            # print("New struct", nvar, typ, data)

        if rnaType == 'Define':
            loadedData[typ][name] = data

        if data:
            for (key, val, sub) in tokens:
                defaultKey(key, val, sub, data)
        return

    elif rnaType == 'PropertyRNA':
        raise MhxError("PropertyRNA!")
        #print("PropertyRNA ", ext, var)
        for (key, val, sub) in tokens:
            defaultKey(ext, val, sub, nvar, [])
        return

    elif rnaType == 'Array':
        for n in range(1, len(args)):
            nvar[n-1] = mhxEval(args[n], locals())
        if len(args) > 0:
            nvar[0] = mhxEval(args[1], locals())
        return

    elif rnaType == 'List':
        raise MhxError("List!")
        data = []
        for (key, val, sub) in tokens:
            elt = mhxEval(val[1], locals())
            data.append(elt)
        setattr(var, ext, data)
        return

    elif rnaType == 'Matrix':
        raise MhxError("Matrix!")
        i = 0
        n = len(tokens)
        for (key, val, sub) in tokens:
            if key == 'row':
                for j in range(n):
                    nvar[i][j] = float(val[j])
                i += 1
        return

    else:
        try:
            data = loadedData[rnaType][args[1]]
            raise MhxError("From loaded %s %s!" % (rnaType, args[1]))
        except KeyError:
            pass
        data = mhxEval(rnaType, locals())
        setattr(var, ext, data)


#
#
#

def pushOnTodoList(var, expr):
    print("Unrecognized expression", expr)
    return
    print(dir(mhxEval(var)))
    MyError(
        "Unrecognized expression %s.\n"  % expr +
        "This can mean that Blender's python API has changed\n" +
        "since the MHX file was exported. Try to export again\n" +
        "from an up-to-date MakeHuman nightly build.\n" +
        "Alternatively, your Blender version may be obsolete.\n" +
        "Download an up-to-date version from www.graphicall.org")


#
#    parseBoolArray(mask):
#

def parseBoolArray(mask):
    list = []
    for c in mask:
        if c == '0':
            list.append(False)
        else:
            list.append(True)
    return list

#    parseMatrix(args, tokens)
#

def parseMatrix(args, tokens):
    matrix = mathutils.Matrix()
    i = 0
    for (key, val, sub) in tokens:
        if key == 'row':
            matrix[i][0] = float(val[0])
            matrix[i][1] = float(val[1])
            matrix[i][2] = float(val[2])
            matrix[i][3] = float(val[3])
            i += 1
    return matrix

#
#    parseDefault(data, tokens, subkeys, exclude):
#

def parseDefault(data, tokens, subkeys, exclude):
    for (key, val, sub) in tokens:
        if key in subkeys.keys():
            for (key2, val2, sub2) in sub:
                ndata = getattr(data, subkeys[key])
                defaultKey(key2, val2, sub2, ndata)
        else:
            defaultKey(key, val, sub, data, exclude)

#
#    invalid(condition):
#

def invalid(condition):
    global rigLeg, rigArm, toggle
    try:
        res = mhxEval(condition)
        #print("%s = %s" % (condition, res))
        return not res
    except:
        #print("%s invalid!" % condition)
        return True



#
#    hideLayers(args):
#    args = sceneLayers sceneHideLayers boneLayers boneHideLayers or nothing
#

def hideLayers(args):
    global theLayers

    if len(args) > 1:
        sceneLayers = int(args[2], 16)
        #sceneHideLayers = int(args[3], 16)
        sceneHideLayers = 0x8000
        hidelayers = [19]
        boneLayers = int(args[4], 16)
        # boneHideLayers = int(args[5], 16)
        boneHideLayers = 0
    else:
        sceneLayers = 0x00ff
        sceneHideLayers = 0
        hidelayers = []
        boneLayers = 0
        boneHideLayers = 0

    scn = bpy.context.scene
    mask = 1

    for ob in scn.objects:
        for n in hidelayers:
            if ob.layers[n]:
                ob.hide = True
                ob.hide_render = True

    if boneLayers:
        human = args[1]
        try:
            ob = loadedData['Object'][human]
        except:
            return

        mask = 1
        hidelayers = []
        for n in range(32):
            ob.data.layers[n] = True if boneLayers & mask else False
            if boneHideLayers & mask:
                hidelayers.append(n)
            mask = mask << 1

        for b in ob.data.bones:
            for n in hidelayers:
                if b.layers[n]:
                    b.hide = True





