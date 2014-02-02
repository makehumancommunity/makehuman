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
# Script copyright (C) MakeHuman Team 2001-2014
# Coding Standards: See http://www.makehuman.org/node/165

"""
Abstract
MHX (MakeHuman eXchange format) importer for Blender 2.6x.

This script should be distributed with Blender.
If not, place it in the .blender/scripts/addons dir
Activate the script in the "Addons" tab (user preferences).
Access from the File > Import menu.

Alternatively, run the script in the script editor (Alt-P), and access from the File > Import menu
"""

bl_info = {
    'name': 'Import: MakeHuman Exchange (.mhx)',
    'author': 'Thomas Larsson',
    'version': (1,16,19),
    "blender": (2, 69, 0),
    'location': "File > Import > MakeHuman (.mhx)",
    'description': 'Import files in the MakeHuman eXchange format (.mhx)',
    'warning': '',
    'wiki_url': 'http://makehuman.org/doc/node/makehuman_blender.html',
    'category': 'MakeHuman'}

MAJOR_VERSION = bl_info["version"][0]
MINOR_VERSION = bl_info["version"][1]
FROM_VERSION = 13

majorVersion = MAJOR_VERSION
minorVersion = MINOR_VERSION

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

#
#
#

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
T_CrashSafe = 0x0

T_Diamond = 0x10
T_Replace = 0x20
T_Shapekeys = 0x40
T_ShapeDrivers = 0x80

T_Face = T_Shapekeys
T_Shape = T_Shapekeys

T_Mesh = 0x100
T_Armature = 0x200
T_Proxy = 0x400
T_Cage = 0x800

T_Rigify = 0x1000
T_Opcns = 0x2000
T_Symm = 0x4000

DefaultToggle = ( T_EnforceVersion + T_Mesh + T_Armature +
    T_Shapekeys + T_Proxy + T_Clothes + T_Rigify )

toggle = DefaultToggle
toggleSettings = toggle
loadedData = None

#
#   mhxEval(expr) - an attempt at a reasonably safe eval.
#   Note that expr never contains any whitespace due to the behavior
#   of the mhx tokenizer.
#

def mhxEval(expr, locls={}):
    globls = {
        '__builtins__' : {},
        'toggle' : toggle,
        'theScale' : theScale,
        'One' : One,
        'T_EnforceVersion' : T_EnforceVersion,
        'T_Clothes' : T_Clothes,
        'T_HardParents' : T_HardParents,
        'T_CrashSafe' : T_CrashSafe,
        'T_Diamond' : T_Diamond,
        'T_Replace' : T_Replace,
        'T_Shapekeys' : T_Shapekeys,
        'T_ShapeDrivers' : T_ShapeDrivers,
        'T_Face' : T_Face,
        'T_Shape' : T_Shape,
        'T_Mesh' : T_Mesh,
        'T_Armature' : T_Armature,
        'T_Proxy' : T_Proxy,
        'T_Cage' : T_Cage,
        'T_Rigify' : T_Rigify,
        'T_Opcns' : T_Opcns,
        'T_Symm' : T_Symm,
    }
    return eval(expr, globls, locls)

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
    'Lamp' : {},
    'Camera' : {},
    'Lattice' : {},
    'Curve' : {},
    'Text' : {},

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
    'Camera' : 'cameras',
    'Lamp' : 'lamps',
    'World' : 'worlds',
}

#
#    readMhxFile(filePath):
#

def readMhxFile(filePath):
    global nErrors, theScale, theArmature, defaultScale, One
    global toggle, warnedVersion, theMessage, alpha7, theDir

    defaultScale = theScale
    One = 1.0/theScale
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
    scn = clearScene()
    print( "Parsing" )
    parse(tokens)

    scn.objects.active = theArmature
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    theArmature.select = True
    bpy.ops.object.mode_set(mode='POSE')
    theArmature.MhAlpha8 = not alpha7
    #bpy.ops.wm.properties_edit(data_path="object", property="MhxRig", value=theArmature["MhxRig"])

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
    print("MHX", (major,minor), (MAJOR_VERSION, MINOR_VERSION), warnedVersion)
    if  major != MAJOR_VERSION or minor < FROM_VERSION:
        if warnedVersion:
            return
        else:
            msg = (
"Wrong MHX version\n" +
"Expected MHX %d.%02d but the loaded file " % (MAJOR_VERSION, MINOR_VERSION) +
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
        if (toggle & T_EnforceVersion or minor > MINOR_VERSION):
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

    majorVersion = int(val[0])
    minorVersion = int(val[1])

    for debugVal in val[2:]:
        debugVal = debugVal.replace("_"," ")
        dKey, dVal = debugVal.split(':')
        versionInfo[ dKey.strip() ] = dVal.strip()

    if 'MHXImporter' in versionInfo:
        print("MHX importer version: ", versionInfo["MHXImporter"])
    if performVersionCheck:
        checkMhxVersion(majorVersion, minorVersion)
    else:
        print("MHX: %s.%s" % (majorVersion, minorVersion))

    for (key, value) in versionInfo.items():
        if key == "MHXImporter":
            continue
        print("%s: %s" % (key, value))

def parse(tokens):
    global MHX249, ifResult, theScale, defaultScale, One
    global majorVersion, minorVersion
    versionInfoStr = ""

    for (key, val, sub) in tokens:
        data = None
        if key == 'MHX':
            importerVerStr = "MHXImporter:_%d.%d.%d" % bl_info["version"]
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
            if mhxEval(val[0]):
                theScale = 1.0
            else:
                theScale = defaultScale
            One = 1.0/theScale
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
        elif key == "Curve":
            data = parseCurve(val, sub)
        elif key == "TextCurve":
            data = parseTextCurve(val, sub)
        elif key == "Lattice":
            data = parseLattice(val, sub)
        elif key == "Group":
            data = parseGroup(val, sub)
        elif key == "Lamp":
            data = parseLamp(val, sub)
        elif key == "World":
            data = parseWorld(val, sub)
        elif key == "Scene":
            data = parseScene(val, sub)
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
                rigifyMhx(bpy.context)
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
#    parseFCurve(fcu, args, tokens):
#    parseKeyFramePoint(pt, args, tokens):
#

def parseAction(args, tokens):
    name = args[0]
    if invalid(args[1]):
        return

    ob = bpy.context.object
    bpy.ops.object.mode_set(mode='POSE')
    if ob.animation_data:
        ob.animation_data.action = None
    created = {}
    for (key, val, sub) in tokens:
        if key == 'FCurve':
            prepareActionFCurve(ob, created, val, sub)

    act = ob.animation_data.action
    loadedData['Action'][name] = act
    if act is None:
        print("Ignoring action %s" % name)
        return act
    act.name = name
    print("Action", name, act, ob)

    for (key, val, sub) in tokens:
        if key == 'FCurve':
            fcu = parseActionFCurve(act, ob, val, sub)
        else:
            defaultKey(key, val, sub, act)
    ob.animation_data.action = None
    bpy.ops.object.mode_set(mode='OBJECT')
    return act

def prepareActionFCurve(ob, created, args, tokens):
    dataPath = args[0]
    index = args[1]
    (expr, channel) = channelFromDataPath(dataPath, index)
    try:
        if channel in created[expr]:
            return
        else:
            created[expr].append(channel)
    except:
        created[expr] = [channel]

    times = []
    for (key, val, sub) in tokens:
        if key == 'kp':
            times.append(int(val[0]))

    try:
        data = mhxEval(expr)
    except:
        print("Ignoring illegal expression: %s" % expr)
        return

    n = 0
    for t in times:
        #bpy.context.scene.current_frame = t
        bpy.ops.anim.change_frame(frame = t)
        try:
            data.keyframe_insert(channel)
            n += 1
        except:
            pass
            #print("failed", data, expr, channel)
    if n != len(times):
        print("Mismatch", n, len(times), expr, channel)
    return

def channelFromDataPath(dataPath, index):
    words = dataPath.split(']')
    if len(words) == 1:
        # location
        expr = "ob"
        channel = dataPath
    elif len(words) == 2:
        # pose.bones["tongue"].location
        expr = "ob.%s]" % (words[0])
        cwords = words[1].split('.')
        channel = cwords[1]
    elif len(words) == 3:
        # pose.bones["brow.R"]["mad"]
        expr = "ob.%s]" % (words[0])
        cwords = words[1].split('"')
        channel = cwords[1]
    return (expr, channel)

def parseActionFCurve(act, ob, args, tokens):
    dataPath = args[0]
    index = args[1]
    (expr, channel) = channelFromDataPath(dataPath, index)
    index = int(args[1])

    success = False
    for fcu in act.fcurves:
        (expr1, channel1) = channelFromDataPath(fcu.data_path, fcu.array_index)
        if expr1 == expr and channel1 == channel and fcu.array_index == index:
            success = True
            break
    if not success:
        return None

    n = 0
    for (key, val, sub) in tokens:
        if key == 'kp':
            try:
                pt = fcu.keyframe_points[n]
                pt.interpolation = 'LINEAR'
                pt = parseKeyFramePoint(pt, val, sub)
                n += 1
            except:
                pass
                #print(tokens)
                #MyError("kp", fcu, n, len(fcu.keyframe_points), val)
        else:
            defaultKey(key, val, sub, fcu)
    return fcu

def parseKeyFramePoint(pt, args, tokens):
    pt.co = (float(args[0]), float(args[1]))
    if len(args) > 2:
        pt.handle1 = (float(args[2]), float(args[3]))
        pt.handle2 = (float(args[3]), float(args[5]))
    return pt

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

"""
        fcurve = con.driver_add("influence", 0)
        driver = fcurve.driver
        driver.type = 'AVERAGE'
"""
def parseDriver(adata, dataPath, index, rna, args, tokens):
    if dataPath[-1] == ']':
        words = dataPath.split(']')
        expr = "rna." + words[0] + ']'
        pwords = words[1].split('"')
        prop = pwords[1]
        bone = mhxEval(expr)
        return None
    else:
        words = dataPath.split('.')
        channel = words[-1]
        expr = "rna"
        for n in range(len(words)-1):
            expr += "." + words[n]
        expr += ".driver_add('%s', index)" % channel

    fcu = mhxEval(expr, locals())
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
        elif key == 'NodeTree':
            mat.use_nodes = True
            parseNodeTree(mat.node_tree, val, sub)
        elif key == 'AnimationData':
            parseAnimationData(mat, val, sub)
        else:
            exclude = ['specular_intensity', 'tangent_shading']
            defaultKey(key, val, sub, mat)

    return mat

def parseMTex(mat, args, tokens):
    index = int(args[0])
    texname = args[1]
    texco = args[2]
    mapto = args[3]
    tex = loadedData['Texture'][texname]
    mtex = mat.texture_slots.add()
    mtex.texture_coords = texco
    mtex.texture = tex

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
#    parseNodeTree(tree, args, tokens):
#    parseNode(node, args, tokens):
#    parseSocket(socket, args, tokens):
#

def parseNodeTree(tree, args, tokens):
    return
    print("Tree", tree, args)
    print(list(tree.nodes))
    tree.name = args[0]
    for (key, val, sub) in tokens:
        if key == 'Node':
            parseNodes(tree.nodes, val, sub)
        else:
            defaultKey(key, val, sub, tree)

def parseNodes(nodes, args, tokens):
    print("Nodes", nodes, args)
    print(list(nodes))
    node.name = args[0]
    for (key, val, sub) in tokens:
        if key == 'Inputs':
            parseSocket(node.inputs, val, sub)
        elif key == 'Outputs':
            parseSocket(node.outputs, val, sub)
        else:
            defaultKey(key, val, sub, node)

def parseNode(node, args, tokens):
    print("Node", node, args)
    print(list(node.inputs), list(node.outputs))
    node.name = args[0]
    for (key, val, sub) in tokens:
        if key == 'Inputs':
            parseSocket(node.inputs, val, sub)
        elif key == 'Outputs':
            parseSocket(node.outputs, val, sub)
        else:
            defaultKey(key, val, sub, node)

def parseSocket(socket, args, tokens):
    print("Socket", socket, args)
    socket.name = args[0]
    for (key, val, sub) in tokens:
        if key == 'Node':
            parseNode(tree.nodes, val, sub)
        else:
            defaultKey(key, val, sub, tree)



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
            verts.append( (theScale*float(val[0]), theScale*float(val[1]), theScale*float(val[2])) )
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
            pt[0] += theScale*float(val[1])
            pt[1] += theScale*float(val[2])
            pt[2] += theScale*float(val[3])
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
            bone.head = (theScale*float(val[0]), theScale*float(val[1]), theScale*float(val[2]))
        elif key == "tail":
            bone.tail = (theScale*float(val[0]), theScale*float(val[1]), theScale*float(val[2]))
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
    if (toggle&T_Opcns and pb):
        print("Active")
        aob = bpy.context.object
        print("ob", aob)
        aamt = aob.data
        print("amt", aamt)
        apose = aob.pose
        print("pose", apose)
        abone = aamt.bones.active
        print("bone", abone)
        print('Num cns before', len(list(constraints)))
        bpy.ops.pose.constraint_add(type=args[1])
        cns = constraints.active
        print('and after', pb, cns, len(list(constraints)))
    else:
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


#    parseCurve (args, tokens):
#    parseSpline(cu, args, tokens):
#    parseBezier(spline, n, args, tokens):
#

def parseCurve (args, tokens):
    if verbosity > 2:
        print( "Parsing curve %s" % args )
    bpy.ops.object.add(type='CURVE')
    cu = setObjectAndData(args, 'Curve')

    for (key, val, sub) in tokens:
        if key == 'Spline':
            parseSpline(cu, val, sub)
        else:
            defaultKey(key, val, sub, cu)
    return

def parseTextCurve (args, tokens):
    if verbosity > 2:
        print( "Parsing text curve %s" % args )
    bpy.ops.object.text_add()
    txt = setObjectAndData(args, 'Text')

    for (key, val, sub) in tokens:
        if key == 'Spline':
            parseSpline(txt, val, sub)
        elif key == 'BodyFormat':
            parseCollection(txt.body_format, sub, [])
        elif key == 'EditFormat':
            parseDefault(txt.edit_format, sub, {}, [])
        elif key == 'Font':
            parseDefault(txt.font, sub, {}, [])
        elif key == 'TextBox':
            parseCollection(txt.body_format, sub, [])
        else:
            defaultKey(key, val, sub, txt)
    return


def parseSpline(cu, args, tokens):
    typ = args[0]
    spline = cu.splines.new(typ)
    nPointsU = int(args[1])
    nPointsV = int(args[2])
    #spline.point_count_u = nPointsU
    #spline.point_count_v = nPointsV
    if typ == 'BEZIER' or typ == 'BSPLINE':
        spline.bezier_points.add(nPointsU)
    else:
        spline.points.add(nPointsU)

    n = 0
    for (key, val, sub) in tokens:
        if key == 'bz':
            parseBezier(spline.bezier_points[n], val, sub)
            n += 1
        elif key == 'pt':
            parsePoint(spline.points[n], val, sub)
            n += 1
        else:
            defaultKey(key, val, sub, spline)
    return

def parseBezier(bez, args, tokens):
    bez.co = mhxEval(args[0])
    bez.co = theScale*bez.co
    bez.handle1 = mhxEval(args[1])
    bez.handle1_type = args[2]
    bez.handle2 = mhxEval(args[3])
    bez.handle2_type = args[4]
    return

def parsePoint(pt, args, tokens):
    pt.co = mhxEval(args[0])
    pt.co = theScale*pt.co
    print(" pt", pt.co)
    return

#
#    parseLattice (args, tokens):
#

def parseLattice (args, tokens):
    if verbosity > 2:
        print( "Parsing lattice %s" % args )
    bpy.ops.object.add(type='LATTICE')
    lat = setObjectAndData(args, 'Lattice')
    for (key, val, sub) in tokens:
        if key == 'Points':
            parseLatticePoints(val, sub, lat.points)
        else:
            defaultKey(key, val, sub, lat)
    return

def parseLatticePoints(args, tokens, points):
    n = 0
    for (key, val, sub) in tokens:
        if key == 'pt':
            v = points[n].co_deform
            v.x = theScale*float(val[0])
            v.y = theScale*float(val[1])
            v.z = theScale*float(val[2])
            n += 1
    return

#
#    parseLamp (args, tokens):
#    parseFalloffCurve(focu, args, tokens):
#

def parseLamp (args, tokens):
    if verbosity > 2:
        print( "Parsing lamp %s" % args )
    bpy.ops.object.add(type='LAMP')
    lamp = setObjectAndData(args, 'Lamp')
    for (key, val, sub) in tokens:
        if key == 'FalloffCurve':
            parseFalloffCurve(lamp.falloff_curve, val, sub)
        else:
            defaultKey(key, val, sub, lamp)
    return

def parseFalloffCurve(focu, args, tokens):
    return

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
#    parseWorld (args, tokens):
#

def parseWorld (args, tokens):
    if verbosity > 2:
        print( "Parsing world %s" % args )
    world = bpy.context.scene.world
    for (key, val, sub) in tokens:
        if key == 'Lighting':
            parseDefault(world.lighting, sub, {}, [])
        elif key == 'Mist':
            parseDefault(world.mist, sub, {}, [])
        elif key == 'Stars':
            parseDefault(world.stars, sub, {}, [])
        else:
            defaultKey(key, val, sub, world)
    return

#
#    parseScene (args, tokens):
#    parseRenderSettings(render, args, tokens):
#    parseToolSettings(tool, args, tokens):
#

def parseScene (args, tokens):
    if verbosity > 2:
        print( "Parsing scene %s" % args )
    scn = bpy.context.scene
    for (key, val, sub) in tokens:
        if key == 'NodeTree':
            scn.use_nodes = True
            parseNodeTree(scn, val, sub)
        elif key == 'GameData':
            parseDefault(scn.game_data, sub, {}, [])
        elif key == 'KeyingSet':
            pass
            #parseDefault(scn.keying_sets, sub, {}, [])
        elif key == 'ObjectBase':
            pass
            #parseDefault(scn.bases, sub, {}, [])
        elif key == 'RenderSettings':
            parseRenderSettings(scn.render, sub, [])
        elif key == 'ToolSettings':
            subkeys = {'ImagePaint' : "image_paint",
                'Sculpt' : "sculpt",
                'VertexPaint' : "vertex_paint",
                'WeightPaint' : "weight_paint" }
            parseDefault(scn.tool_settings, sub, subkeys, [])
        elif key == 'UnitSettings':
            parseDefault(scn.unit_settings, sub, {}, [])
        else:
            defaultKey(key, val, sub, scn)
    return

def parseRenderSettings(render, args, tokens):
    if verbosity > 2:
        print( "Parsing RenderSettings %s" % args )
    for (key, val, sub) in tokens:
        if key == 'Layer':
            pass
            #parseDefault(scn.layers, sub, [])
        else:
            defaultKey(key, val, sub, render)
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
    ob.MhxShapekeyDrivers = (toggle&T_Shapekeys != 0 and toggle&T_ShapeDrivers != 0)
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
        if "Invis" in mat.name:
            invisioNum = mn
            break
    if invisioNum < 0:
        print("WARNING: Nu Invisio material found. Cannot delete helper geometry")
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
        theMessage = "\n  *** WARNING ***\nHelper deletion turned off due to Blender crash.\nHelpers can be deleted by deleting all selected vertices in Edit mode\n     **********\n"
        print(theMessage)
    else:
        bpy.ops.object.mode_set(mode='EDIT')
        print("Do delete")
        bpy.ops.mesh.delete(type='VERT')
        print("Verts deleted")
        bpy.ops.object.mode_set(mode='OBJECT')
        print("Back to object mode")
    return

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

def parseCollection(data, tokens, exclude):
    return


#
#    Utilities
#

#
#    extractBpyType(data):
#
"""
def extractBpyType(data):
    typeSplit = str(type(data)).split("'")
    if typeSplit[0] != '<class ':
        return None
    classSplit = typeSplit[1].split(".")
    if classSplit[0] == 'bpy' and classSplit[1] == 'types':
        return classSplit[2]
    elif classSplit[0] == 'bpy_types':
        return classSplit[1]
    else:
        return None

#
#    Bool(string):
#

def Bool(string):
    if string == 'True':
        return True
    elif string == 'False':
        return False
    else:
        MyError("Bool %s?" % string)
"""
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
#    clearScene(context):
#

def clearScene():
    global toggle
    scn = bpy.context.scene
    for n in range(len(scn.layers)):
        scn.layers[n] = True
    return scn
    print("clearScene %s %s" % (toggle & T_Replace, scn))
    if not toggle & T_Replace:
        return scn

    for ob in scn.objects:
        if ob.type in ['MESH', 'ARMATURE', 'EMPTY', 'CURVE', 'LATTICE']:
            scn.objects.active = ob
            ob.name = "#" + ob.name
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            scn.objects.unlink(ob)
            del ob

    for grp in bpy.data.groups:
        grp.name = "#" + grp.name
    #print(scn.objects)
    return scn

#
#    hideLayers(args):
#    args = sceneLayers sceneHideLayers boneLayers boneHideLayers or nothing
#

def hideLayers(args):
    if len(args) > 1:
        sceneLayers = int(args[2], 16)
        sceneHideLayers = int(args[3], 16)
        boneLayers = int(args[4], 16)
        # boneHideLayers = int(args[5], 16)
        boneHideLayers = 0
    else:
        sceneLayers = 0x00ff
        sceneHideLayers = 0
        boneLayers = 0
        boneHideLayers = 0

    scn = bpy.context.scene
    mask = 1
    hidelayers = []
    for n in range(20):
        scn.layers[n] = True if sceneLayers & mask else False
        if sceneHideLayers & mask:
            hidelayers.append(n)
        mask = mask << 1

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

    return


#
#    readDefaults():
#    writeDefaults():
#

ConfigFile = '~/mhx_import.cfg'


def readDefaults():
    global toggle, toggleSettings, theScale
    path = os.path.realpath(os.path.expanduser(ConfigFile))
    try:
        fp = open(path, 'rU')
        print('Storing defaults')
    except:
        print('Cannot open "%s" for reading' % path)
        return
    bver = ''
    for line in fp:
        words = line.split()
        if len(words) >= 3:
            try:
                toggle = int(words[0],16)
                theScale = float(words[1])
            except:
                print('Configuration file "%s" is corrupt' % path)
    fp.close()
    toggleSettings = toggle
    return

def writeDefaults():
    global toggleSettings, theScale
    path = os.path.realpath(os.path.expanduser(ConfigFile))
    try:
        fp = open(path, 'w')
        print('Storing defaults')
    except:
        print('Cannot open "%s" for writing' % path)
        return
    fp.write("%x %f Graphicall" % (toggleSettings, theScale))
    fp.close()
    return

###################################################################################
#
#   Postprocessing of rigify rig
#
#   rigifyMhx(context):
#
###################################################################################

class RigifyBone:
    def __init__(self, eb):
        self.name = eb.name
        self.realname = None
        self.realname1 = None
        self.realname2 = None
        self.fkname = None
        self.ikname = None

        self.head = eb.head.copy()
        self.tail = eb.tail.copy()
        self.roll = eb.roll
        self.deform = eb.use_deform
        self.parent = None
        self.child = None
        self.connect = False
        self.original = False
        self.extra = (eb.name in ["spine-1"])

    def __repr__(self):
        return ("<RigifyBone %s %s %s>" % (self.name, self.realname, self.realname1))


def rigifyMhx(context):
    global theArmature
    from collections import OrderedDict

    print("Modifying MHX rig to Rigify")
    scn = context.scene
    ob = context.object
    if ob.type == 'ARMATURE':
        rig = ob
    elif ob.type == 'MESH':
        rig = ob.parent
    else:
        rig = None
    if not(rig and rig.type == 'ARMATURE'):
        raise RuntimeError("Rigify: %s is neither an armature nor has armature parent" % ob)
    rig.MhxRigify = True
    scn.objects.active = rig

    group = None
    for grp in bpy.data.groups:
        if rig.name in grp.objects:
            group = grp
            break
    print("Group: %s" % group)

    # Setup info about MHX bones
    bones = OrderedDict()
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in rig.data.edit_bones:
        bone = bones[eb.name] = RigifyBone(eb)
        if eb.parent:
            bone.parent = eb.parent.name
            bones[bone.parent].child = eb.name
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create metarig
    try:
        bpy.ops.object.armature_human_metarig_add()
    except AttributeError:
        raise MyError("The Rigify add-on is not enabled. It is found under rigging.")
    bpy.ops.object.location_clear()
    bpy.ops.object.rotation_clear()
    bpy.ops.object.scale_clear()
    bpy.ops.transform.resize(value=(100, 100, 100))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Fit metarig to default MHX rig
    meta = context.object
    bpy.ops.object.mode_set(mode='EDIT')
    extra = []
    for bone in bones.values():
        try:
            eb = meta.data.edit_bones[bone.name]
        except KeyError:
            eb = None
        if eb:
            eb.head = bone.head
            eb.tail = bone.tail
            eb.roll = bone.roll
            bone.original = True
        elif bone.extra:
            extra.append(bone.name)
            bone.original = True
            eb = meta.data.edit_bones.new(bone.name)
            eb.use_connect = False
            eb.head = bones[bone.parent].tail
            eb.tail = bones[bone.child].head
            eb.roll = bone.roll
            parent = meta.data.edit_bones[bone.parent]
            child = meta.data.edit_bones[bone.child]
            child.parent = eb
            child.head = bones[bone.child].head
            parent.tail = bones[bone.parent].tail
            eb.parent = parent
            eb.use_connect = True

    # Add rigify properties to extra bones
    bpy.ops.object.mode_set(mode='OBJECT')
    for bname in extra:
        pb = meta.pose.bones[bname]
        pb["rigify_type"] = ""

    # Generate rigify rig
    bpy.ops.pose.rigify_generate()
    gen = context.object
    print("Generated", gen)
    scn.objects.unlink(meta)
    del meta

    for bone in bones.values():
        if bone.original:
            setBoneName(bone, gen)

    # Add extra bone to generated rig
    bpy.ops.object.mode_set(mode='EDIT')
    layers = 32*[False]
    layers[1] = True
    for bone in bones.values():
        if not bone.original:
            if bone.deform:
                bone.realname = "DEF-" + bone.name
            else:
                bone.realname = "MCH-" + bone.name
            eb = gen.data.edit_bones.new(bone.realname)
            eb.head = bone.head
            eb.tail = bone.tail
            eb.roll = bone.roll
            eb.use_deform = bone.deform
            if bone.parent:
                parent = bones[bone.parent]
                if parent.realname:
                    eb.parent = gen.data.edit_bones[parent.realname]
                elif parent.realname1:
                    eb.parent = gen.data.edit_bones[parent.realname1]
                else:
                    print(bone)
            eb.use_connect = (eb.parent != None and eb.parent.tail == eb.head)
            eb.layers = layers

    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in bones.values():
        if not bone.original:
            pb = gen.pose.bones[bone.realname]
            db = rig.pose.bones[bone.name]
            pb.rotation_mode = db.rotation_mode
            for cns1 in db.constraints:
                cns2 = pb.constraints.new(cns1.type)
                fixConstraint(cns1, cns2, gen, bones)

    # Add MHX properties
    for key in rig.keys():
        gen[key] = rig[key]

    # Copy MHX bone drivers
    if rig.animation_data:
        for fcu1 in rig.animation_data.drivers:
            rna,channel = fcu1.data_path.rsplit(".", 1)
            pb = mhxEval("gen.%s" % rna)
            fcu2 = pb.driver_add(channel, fcu1.array_index)
            copyDriver(fcu1, fcu2, gen)

    # Copy MHX morph drivers and change armature modifier
    for ob in rig.children:
        if ob.type == 'MESH':
            ob.parent = gen

            if ob.data.animation_data:
                for fcu in ob.data.animation_data.drivers:
                    print(ob, fcu.data_path)
                    changeDriverTarget(fcu, gen)

            if ob.data.shape_keys and ob.data.shape_keys.animation_data:
                for fcu in ob.data.shape_keys.animation_data.drivers:
                    print(skey, fcu.data_path)
                    changeDriverTarget(fcu, gen)

            for mod in ob.modifiers:
                if mod.type == 'ARMATURE' and mod.object == rig:
                    mod.object = gen

    if group:
        group.objects.link(gen)

    # Parent widgets under empty
    empty = bpy.data.objects.new("Widgets", None)
    scn.objects.link(empty)
    empty.layers = 20*[False]
    empty.layers[19] = True
    empty.parent = gen
    for ob in scn.objects:
        if ob.type == 'MESH' and ob.name[0:4] == "WGT-" and not ob.parent:
            ob.parent = empty
            grp.objects.link(ob)

    #Clean up
    gen.show_x_ray = True
    gen.data.draw_type = 'STICK'
    gen.MhxRigify = False
    name = rig.name
    scn.objects.unlink(rig)
    del rig
    gen.name = name
    bpy.ops.object.mode_set(mode='POSE')
    theArmature = gen
    print("MHX rig %s successfully rigified" % name)



def setBoneName(bone, gen):
    fkname = bone.name.replace(".", ".fk.")
    try:
        gen.data.bones[fkname]
        bone.fkname = fkname
        bone.ikname = fkname.replace(".fk.", ".ik")
    except KeyError:
        pass

    defname = "DEF-" + bone.name
    try:
        gen.data.bones[defname]
        bone.realname = defname
        return
    except KeyError:
        pass

    defname1 = "DEF-" + bone.name + ".01"
    try:
        gen.data.bones[defname1]
        bone.realname1 = defname1
        bone.realname2 = defname1.replace(".01.", ".02.")
        return
    except KeyError:
        pass

    defname1 = "DEF-" + bone.name.replace(".", ".01.")
    try:
        gen.data.bones[defname1]
        bone.realname1 = defname1
        bone.realname2 = defname1.replace(".01.", ".02")
        return
    except KeyError:
        pass

    try:
        gen.data.edit_bones[bone.name]
        bone.realname = bone.name
    except KeyError:
        pass


def fixConstraint(cns1, cns2, gen, bones):
    for key in dir(cns1):
        if ((key[0] != "_") and
            (key not in ["bl_rna", "type", "rna_type", "is_valid", "error_location", "error_rotation"])):
            expr = ("cns2.%s = cns1.%s" % (key, key))
            setattr(cns2, key, getattr(cns1, key))

    try:
        cns2.target = gen
    except AttributeError:
        pass

    if cns1.type == 'STRETCH_TO':
        bone = bones[cns1.subtarget]
        if bone.realname:
            cns2.subtarget = bone.realname
            cns2.head_tail = cns1.head_tail
        elif not bone.realname1:
            print(bone)
            halt
        elif cns1.head_tail < 0.5:
            cns2.subtarget = bone.realname1
            cns2.head_tail = 2*cns1.head_tail
        else:
            cns2.subtarget = bone.realname2
            cns2.head_tail = 2*cns1.head_tail-1

    elif cns1.type == 'TRANSFORM':
        bone = bones[cns1.subtarget]
        if bone.fkname:
            cns2.subtarget = bone.fkname
        elif bone.ikname:
            cns2.subtarget = bone.ikname
        else:
            cns2.subtarget = bone.realname


def copyDriver(fcu1, fcu2, id):
    drv1 = fcu1.driver
    drv2 = fcu2.driver

    for var1 in drv1.variables:
        var2 = drv2.variables.new()
        var2.name = var1.name
        var2.type = var1.type
        targ1 = var1.targets[0]
        targ2 = var2.targets[0]
        targ2.id = id
        targ2.data_path = targ1.data_path

    drv2.type = drv1.type
    drv2.expression = drv1.expression
    drv2.show_debug_info = drv1.show_debug_info


def changeDriverTarget(fcu, id):
    for var in fcu.driver.variables:
        targ = var.targets[0]
        targ.id = id


#
#   class OBJECT_OT_RigifyMhxButton(bpy.types.Operator):
#

class OBJECT_OT_RigifyMhxButton(bpy.types.Operator):
    bl_idname = "mhxrig.rigify_mhx"
    bl_label = "Rigify MHX rig"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            rigifyMhx(context)
        except MhxError as err:
            print("Error when rigifying mhx rig: %s" % err)
        return{'FINISHED'}

#
#   class RigifyMhxPanel(bpy.types.Panel):
#

class RigifyMhxPanel(bpy.types.Panel):
    bl_label = "Rigify MHX"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRigify)

    def draw(self, context):
        self.layout.operator("mhxrig.rigify_mhx")
        return

###################################################################################
#
#    Error popup
#
###################################################################################

DEBUG = False
from bpy.props import StringProperty, FloatProperty, EnumProperty, BoolProperty

class ErrorOperator(bpy.types.Operator):
    bl_idname = "mhx.error"
    bl_label = "Error when loading MHX file"

    def execute(self, context):
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        global theErrorLines
        maxlen = 0
        for line in theErrorLines:
            if len(line) > maxlen:
                maxlen = len(line)
        width = 20+5*maxlen
        height = 20+5*len(theErrorLines)
        #self.report({'INFO'}, theMessage)
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=width, height=height)

    def draw(self, context):
        global theErrorLines
        for line in theErrorLines:
            self.layout.label(line)

def MyError(message):
    global theMessage, theErrorLines, theErrorStatus
    theMessage = message
    theErrorLines = message.split('\n')
    theErrorStatus = True
    bpy.ops.mhx.error('INVOKE_DEFAULT')
    raise MhxError(theMessage)

class MhxError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class SuccessOperator(bpy.types.Operator):
    bl_idname = "mhx.success"
    bl_label = "MHX file successfully loaded:"
    message = StringProperty()

    def execute(self, context):
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.label(self.message + theMessage)

###################################################################################
#
#    User interface
#
###################################################################################

from bpy_extras.io_utils import ImportHelper, ExportHelper

MhxBoolProps = [
    ("enforce", "Enforce version", "Only accept MHX files of correct version", T_EnforceVersion),
    #("crash_safe", "Crash-safe", "Disable features that have caused Blender crashes", T_CrashSafe),
    ("mesh", "Mesh", "Use main mesh", T_Mesh),
    ("proxy", "Proxies", "Use proxies", T_Proxy),
    #("armature", "Armature", "Use armature", T_Armature),
    #("replace", "Replace scene", "Replace scene", T_Replace),
    ("cage", "Cage", "Load mesh deform cage", T_Cage),
    ("clothes", "Clothes", "Include clothes", T_Clothes),
    ("shapekeys", "Shapekeys", "Include shapekeys", T_Shapekeys),
    ("drivers", "Drivers", "Include drivers", T_ShapeDrivers),
    #("symm", "Symmetric shapes", "Keep shapekeys symmetric", T_Symm),
    ("diamond", "Helper geometry", "Keep helper geometry", T_Diamond),
    ("rigify", "Rigify", "Create rigify control rig", T_Rigify),
]

class ImportMhx(bpy.types.Operator, ImportHelper):
    """Import from MHX file format (.mhx)"""
    bl_idname = "import_scene.makehuman_mhx"
    bl_description = 'Import from MHX file format (.mhx)'
    bl_label = "Import MHX"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'UNDO'}

    filename_ext = ".mhx"
    filter_glob = StringProperty(default="*.mhx", options={'HIDDEN'})
    filepath = StringProperty(subtype='FILE_PATH')

    scale = FloatProperty(name="Scale", description="Default meter, decimeter = 1.0", default = theScale)
    advanced = BoolProperty(name="Override default settings", description="Use advanced import settings", default=False)
    for (prop, name, desc, flag) in MhxBoolProps:
        expr = '%s = BoolProperty(name="%s", description="%s", default=(toggleSettings&%s != 0))' % (prop, name, desc, flag)
        exec(expr)   # Trusted source: this file.


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "advanced")
        if self.advanced:
            layout.prop(self, "scale")
            for (prop, name, desc, flag) in MhxBoolProps:
                layout.prop(self, prop)


    def execute(self, context):
        global toggle, toggleSettings, theScale, MhxBoolProps
        if not self.advanced:
            toggle = DefaultToggle
        else:
            toggle = T_Armature
            for (prop, name, desc, flag) in MhxBoolProps:
                expr = '(%s if self.%s else 0)' % (flag, prop)
                toggle |=  eval(expr)   # trusted source: this file
            toggleSettings = toggle
        print("execute flags %x" % toggle)
        theScale = self.scale

        #filepathname = self.filepath.encode('utf-8', 'strict')
        try:
            if not context.user_preferences.system.use_scripts_auto_execute:
                MyError("Auto Run Python Scripts must be turned on.\nIt is found under\n File > User Preferences > File")
            readMhxFile(self.filepath)
            #bpy.ops.mhx.success('INVOKE_DEFAULT', message = self.filepath)
        except MhxError:
            print("Error when loading MHX file %s:\n" % self.filepath + theMessage)

        if self.advanced:
            writeDefaults()
            self.advanced = False
        return {'FINISHED'}


    def invoke(self, context, event):
        global toggle, theScale, MhxBoolProps
        readDefaults()
        self.scale = theScale
        for (prop, name, desc, flag) in MhxBoolProps:
            setattr(self, prop, mhxEval('(toggle&%s != 0)' % flag))
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


###################################################################################
#
#    Main panel
#
###################################################################################

MhxLayers = [
    (( 0,    'Root', 'MhxRoot'),
     ( 1,    'Spine', 'MhxFKSpine')),
    ((10,    'Head', 'MhxHead'),
     ( 8,    'Face', 'MhxFace')),
    (( 9,    'Tweak', 'MhxTweak'),
     (16,    'Clothes', 'MhxClothes')),
    #((17,    'IK Spine', 'MhxIKSpine'),
     #((13,    'Inv FK Spine', 'MhxInvFKSpine')),
    ('Left', 'Right'),
    (( 2,    'IK Arm', 'MhxIKArm'),
     (18,    'IK Arm', 'MhxIKArm')),
    (( 3,    'FK Arm', 'MhxFKArm'),
     (19,    'FK Arm', 'MhxFKArm')),
    (( 4,    'IK Leg', 'MhxIKLeg'),
     (20,    'IK Leg', 'MhxIKLeg')),
    (( 5,    'FK Leg', 'MhxFKLeg'),
     (21,    'FK Leg', 'MhxFKLeg')),
    ((12,    'Extra', 'MhxExtra'),
     (28,    'Extra', 'MhxExtra')),
    (( 6,    'Fingers', 'MhxFingers'),
     (22,    'Fingers', 'MhxFingers')),
    (( 7,    'Links', 'MhxLinks'),
     (23,    'Links', 'MhxLinks')),
    ((11,    'Palm', 'MhxPalm'),
     (27,    'Palm', 'MhxPalm')),
]

OtherLayers = [
    (( 1,    'Spine', 'MhxFKSpine'),
     ( 10,    'Head', 'MhxHead')),
    (( 9,    'Tweak', 'MhxTweak'),
     ( 8,    'Face', 'MhxFace')),
    ('Left', 'Right'),
    (( 3,    'Arm', 'MhxFKArm'),
     (19,    'Arm', 'MhxFKArm')),
    (( 5,    'Leg', 'MhxFKLeg'),
     (21,    'Leg', 'MhxFKLeg')),
    (( 7,    'Fingers', 'MhxLinks'),
     (23,    'Fingers', 'MhxLinks')),
    ((11,    'Palm', 'MhxPalm'),
     (27,    'Palm', 'MhxPalm')),
]


#
#    class MhxMainPanel(bpy.types.Panel):
#

class MhxMainPanel(bpy.types.Panel):
    bl_label = "MHX Main v %d.%d.%d" % bl_info["version"]
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig)

    def draw(self, context):
        layout = self.layout
        layout.label("Layers")
        layout.operator("mhx.pose_enable_all_layers")
        layout.operator("mhx.pose_disable_all_layers")

        rig = context.object
        if rig.MhxRig == 'MHX':
            layers = MhxLayers
        else:
            layers = OtherLayers

        for (left,right) in layers:
            row = layout.row()
            if type(left) == str:
                row.label(left)
                row.label(right)
            else:
                for (n, name, prop) in [left,right]:
                    row.prop(rig.data, "layers", index=n, toggle=True, text=name)

        layout.separator()
        layout.label("Export/Import MHP")
        layout.operator("mhx.saveas_mhp")
        layout.operator("mhx.load_mhp")


class VIEW3D_OT_MhxEnableAllLayersButton(bpy.types.Operator):
    bl_idname = "mhx.pose_enable_all_layers"
    bl_label = "Enable all layers"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig,mesh = getMhxRigMesh(context.object)
        for (left,right) in MhxLayers:
            if type(left) != str:
                for (n, name, prop) in [left,right]:
                    rig.data.layers[n] = True
        return{'FINISHED'}


class VIEW3D_OT_MhxDisableAllLayersButton(bpy.types.Operator):
    bl_idname = "mhx.pose_disable_all_layers"
    bl_label = "Disable all layers"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig,mesh = getMhxRigMesh(context.object)
        layers = 32*[False]
        pb = context.active_pose_bone
        if pb:
            for n in range(32):
                if pb.bone.layers[n]:
                    layers[n] = True
                    break
        else:
            layers[0] = True
        if rig:
            rig.data.layers = layers
        return{'FINISHED'}



def saveMhpFile(rig, scn, filepath):
    roots = []
    for pb in rig.pose.bones:
        if pb.parent is None:
            roots.append(pb)

    (pname, ext) = os.path.splitext(filepath)
    mhppath = pname + ".mhp"

    fp = open(mhppath, "w", encoding="utf-8", newline="\n")
    for root in roots:
        writeMhpBones(fp, root, None)
    fp.close()
    print("Mhp file %s saved" % mhppath)


def writeMhpBones(fp, pb, log):
    if not isMuscleBone(pb):
        b = pb.bone
        if pb.parent:
            mat = b.matrix_local.inverted() * b.parent.matrix_local * pb.parent.matrix.inverted() * pb.matrix
        else:
            mat = pb.matrix.copy()
            maty = mat[1].copy()
            matz = mat[2].copy()
            mat[1] = matz
            mat[2] = -maty

        diff = mat - Matrix()
        nonzero = False
        for i in range(4):
            if abs(diff[i].length) > 5e-3:
                nonzero = True
                break

        if nonzero:
            fp.write("%s\tmatrix" % pb.name)
            for i in range(4):
                row = mat[i]
                fp.write("\t%.4f\t%.4f\t%.4f\t%.4f" % (row[0], row[1], row[2], row[3]))
            fp.write("\n")

    for child in pb.children:
        writeMhpBones(fp, child, log)


def isMuscleBone(pb):
    layers = pb.bone.layers
    if (layers[14] or layers[15] or layers[30] or layers[31]):
        return True
    for cns in pb.constraints:
        if (cns.type == 'STRETCH_TO' or
            cns.type == 'TRANSFORM' or
            cns.type == 'TRACK_TO' or
            cns.type == 'IK' or
            cns.type[0:5] == 'COPY_'):
            return True
    return False


def loadMhpFile(rig, scn, filepath):
    unit = Matrix()
    for pb in rig.pose.bones:
        pb.matrix_basis = unit

    (pname, ext) = os.path.splitext(filepath)
    mhppath = pname + ".mhp"

    fp = open(mhppath, "rU")
    for line in fp:
        words = line.split()
        if len(words) < 4:
            continue

        try:
            pb = rig.pose.bones[words[0]]
        except KeyError:
            print("Warning: Did not find bone %s" % words[0])
            continue

        if isMuscleBone(pb):
            pass
        elif words[1] == "quat":
            q = Quaternion((float(words[2]), float(words[3]), float(words[4]), float(words[5])))
            mat = q.to_matrix().to_4x4()
            pb.matrix_basis = mat
        elif words[1] == "gquat":
            q = Quaternion((float(words[2]), float(words[3]), float(words[4]), float(words[5])))
            mat = q.to_matrix().to_4x4()
            maty = mat[1].copy()
            matz = mat[2].copy()
            mat[1] = -matz
            mat[2] = maty
            pb.matrix_basis = pb.bone.matrix_local.inverted() * mat
        elif words[1] == "matrix":
            rows = []
            n = 2
            for i in range(4):
                rows.append((float(words[n]), float(words[n+1]), float(words[n+2]), float(words[n+3])))
                n += 4
            mat = Matrix(rows)
            if pb.parent:
                pb.matrix_basis = mat
            else:
                maty = mat[1].copy()
                matz = mat[2].copy()
                mat[1] = -matz
                mat[2] = maty
                pb.matrix_basis = pb.bone.matrix_local.inverted() * mat
        elif words[1] == "scale":
            pass
        else:
            print("WARNING: Unknown line in mcp file:\n%s" % line)
    fp.close()
    print("Mhp file %s loaded" % mhppath)


class VIEW3D_OT_LoadMhpButton(bpy.types.Operator):
    bl_idname = "mhx.load_mhp"
    bl_label = "Load MHP File"
    bl_description = "Load a pose in MHP format"
    bl_options = {'UNDO'}

    filename_ext = ".mhp"
    filter_glob = StringProperty(default="*.mhp", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for mhp file",
        maxlen= 1024, default= "")

    def execute(self, context):
        loadMhpFile(context.object, context.scene, self.properties.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class VIEW3D_OT_SaveasMhpFileButton(bpy.types.Operator, ExportHelper):
    bl_idname = "mhx.saveas_mhp"
    bl_label = "Save MHP File"
    bl_description = "Save current pose in MHP format"
    bl_options = {'UNDO'}

    filename_ext = ".mhp"
    filter_glob = StringProperty(default="*.mhp", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="File Path",
        description="File path used for mhp file",
        maxlen= 1024, default= "")

    def execute(self, context):
        saveMhpFile(context.object, context.scene, self.properties.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#########################################
#
#   FK-IK snapping.
#
#########################################

def getPoseMatrix(gmat, pb):
    restInv = pb.bone.matrix_local.inverted()
    if pb.parent:
        parInv = pb.parent.matrix.inverted()
        parRest = pb.parent.bone.matrix_local
        return restInv * (parRest * (parInv * gmat))
    else:
        return restInv * gmat


def getGlobalMatrix(mat, pb):
    gmat = pb.bone.matrix_local * mat
    if pb.parent:
        parMat = pb.parent.matrix
        parRest = pb.parent.bone.matrix_local
        return parMat * (parRest.inverted() * gmat)
    else:
        return gmat


def matchPoseTranslation(pb, src, auto):
    pmat = getPoseMatrix(src.matrix, pb)
    insertLocation(pb, pmat, auto)


def insertLocation(pb, mat, auto):
    pb.location = mat.to_translation()
    if auto:
        pb.keyframe_insert("location", group=pb.name)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def matchPoseRotation(pb, src, auto):
    pmat = getPoseMatrix(src.matrix, pb)
    insertRotation(pb, pmat, auto)


def printMatrix(string,mat):
    print(string)
    for i in range(4):
        print("    %.4g %.4g %.4g %.4g" % tuple(mat[i]))


def insertRotation(pb, mat, auto):
    q = mat.to_quaternion()
    if pb.rotation_mode == 'QUATERNION':
        pb.rotation_quaternion = q
        if auto:
            pb.keyframe_insert("rotation_quaternion", group=pb.name)
    else:
        pb.rotation_euler = q.to_euler(pb.rotation_mode)
        if auto:
            pb.keyframe_insert("rotation_euler", group=pb.name)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def matchPoseTwist(pb, src, auto):
    pmat0 = src.matrix_basis
    euler = pmat0.to_3x3().to_euler('YZX')
    euler.z = 0
    pmat = euler.to_matrix().to_4x4()
    pmat.col[3] = pmat0.col[3]
    insertRotation(pb, pmat, auto)


def matchIkLeg(legIk, toeFk, mBall, mToe, mHeel, auto):
    rmat = toeFk.matrix.to_3x3()
    tHead = Vector(toeFk.matrix.col[3][:3])
    ty = rmat.col[1]
    tail = tHead + ty * toeFk.bone.length

    try:
        zBall = mBall.matrix.col[3][2]
    except AttributeError:
        return
    zToe = mToe.matrix.col[3][2]
    zHeel = mHeel.matrix.col[3][2]

    x = Vector(rmat.col[0])
    y = Vector(rmat.col[1])
    z = Vector(rmat.col[2])

    if zHeel > zBall and zHeel > zToe:
        # 1. foot.ik is flat
        if abs(y[2]) > abs(z[2]):
            y = -z
        y[2] = 0
    else:
        # 2. foot.ik starts at heel
        hHead = Vector(mHeel.matrix.col[3][:3])
        y = tail - hHead

    y.normalize()
    x -= x.dot(y)*y
    x.normalize()
    z = x.cross(y)
    head = tail - y * legIk.bone.length

    # Create matrix
    gmat = Matrix()
    gmat.col[0][:3] = x
    gmat.col[1][:3] = y
    gmat.col[2][:3] = z
    gmat.col[3][:3] = head
    pmat = getPoseMatrix(gmat, legIk)

    insertLocation(legIk, pmat, auto)
    insertRotation(legIk, pmat, auto)


def matchPoleTarget(pb, above, below, auto):
    ax,ay,az = above.matrix.to_3x3().to_euler('YZX')
    bx,by,bz = below.matrix.to_3x3().to_euler('YZX')
    x = Vector(above.matrix.col[1][:3])
    y = Vector(below.matrix.col[1][:3])
    p0 = Vector(below.matrix.col[3][:3])
    n = x.cross(y)
    if abs(n.length) > 1e-4:
        z = x - y
        n = n/n.length
        z -= z.dot(n)*n
        z = z/z.length
        p = p0 + 3.0*z
    else:
        p = p0
    gmat = Matrix.Translation(p)
    pmat = getPoseMatrix(gmat, pb)
    insertLocation(pb, pmat, auto)


def matchPoseReverse(pb, src, auto):
    gmat = src.matrix
    tail = gmat.col[3] + src.length * gmat.col[1]
    rmat = Matrix((gmat.col[0], -gmat.col[1], -gmat.col[2], tail))
    rmat.transpose()
    pmat = getPoseMatrix(rmat, pb)
    pb.matrix_basis = pmat
    insertRotation(pb, pmat, auto)


def matchPoseScale(pb, src, auto):
    pmat = getPoseMatrix(src.matrix, pb)
    pb.scale = pmat.to_scale()
    if auto:
        pb.keyframe_insert("scale", group=pb.name)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='POSE')


def snapFkArm(context, data):
    rig = context.object
    prop,old,suffix = setSnapProp(rig, data, 1.0, context, False)
    auto = context.scene.tool_settings.use_keyframe_insert_auto

    print("Snap FK Arm%s" % suffix)
    snapFk,cnsFk = getSnapBones(rig, "ArmFK", suffix)
    (uparmFk, loarmFk, handFk) = snapFk
    muteConstraints(cnsFk, True)
    snapIk,cnsIk = getSnapBones(rig, "ArmIK", suffix)
    (uparmIk, loarmIk, elbow, elbowPt, handIk) = snapIk

    matchPoseRotation(uparmFk, uparmIk, auto)
    matchPoseScale(uparmFk, uparmIk, auto)

    matchPoseRotation(loarmFk, loarmIk, auto)
    matchPoseScale(loarmFk, loarmIk, auto)

    restoreSnapProp(rig, prop, old, context)

    try:
        matchHand = rig["MhaHandFollowsWrist" + suffix]
    except KeyError:
        matchHand = True
    if matchHand:
        matchPoseRotation(handFk, handIk, auto)
        matchPoseScale(handFk, handIk, auto)

    #muteConstraints(cnsFk, False)
    return


def snapIkArm(context, data):
    rig = context.object
    prop,old,suffix = setSnapProp(rig, data, 0.0, context, True)
    auto = context.scene.tool_settings.use_keyframe_insert_auto

    print("Snap IK Arm%s" % suffix)
    snapIk,cnsIk = getSnapBones(rig, "ArmIK", suffix)
    (uparmIk, loarmIk, elbow, elbowPt, handIk) = snapIk
    snapFk,cnsFk = getSnapBones(rig, "ArmFK", suffix)
    (uparmFk, loarmFk, handFk) = snapFk
    muteConstraints(cnsIk, True)

    matchPoseTranslation(handIk, handFk, auto)
    matchPoseRotation(handIk, handFk, auto)

    matchPoleTarget(elbowPt, uparmFk, loarmFk, auto)

    #matchPoseRotation(uparmIk, uparmFk, auto)
    #matchPoseRotation(loarmIk, loarmFk, auto)

    restoreSnapProp(rig, prop, old, context)
    #muteConstraints(cnsIk, False)
    return


def snapFkLeg(context, data):
    rig = context.object
    prop,old,suffix = setSnapProp(rig, data, 1.0, context, False)
    auto = context.scene.tool_settings.use_keyframe_insert_auto

    print("Snap FK Leg%s" % suffix)
    snap,_ = getSnapBones(rig, "Leg", suffix)
    (upleg, loleg, foot, toe) = snap
    snapIk,cnsIk = getSnapBones(rig, "LegIK", suffix)
    (uplegIk, lolegIk, kneePt, ankleIk, legIk, footRev, toeRev, mBall, mToe, mHeel) = snapIk
    snapFk,cnsFk = getSnapBones(rig, "LegFK", suffix)
    (uplegFk, lolegFk, footFk, toeFk) = snapFk
    muteConstraints(cnsFk, True)

    matchPoseRotation(uplegFk, uplegIk, auto)
    matchPoseScale(uplegFk, uplegIk, auto)

    matchPoseRotation(lolegFk, lolegIk, auto)
    matchPoseScale(lolegFk, lolegIk, auto)

    restoreSnapProp(rig, prop, old, context)

    if not rig["MhaLegIkToAnkle" + suffix]:
        matchPoseReverse(footFk, footRev, auto)
        matchPoseReverse(toeFk, toeRev, auto)

    #muteConstraints(cnsFk, False)
    return


def snapIkLeg(context, data):
    rig = context.object
    scn = context.scene
    prop,old,suffix = setSnapProp(rig, data, 0.0, context, True)
    auto = scn.tool_settings.use_keyframe_insert_auto

    print("Snap IK Leg%s" % suffix)
    snapIk,cnsIk = getSnapBones(rig, "LegIK", suffix)
    (uplegIk, lolegIk, kneePt, ankleIk, legIk, footRev, toeRev, mBall, mToe, mHeel) = snapIk
    snapFk,cnsFk = getSnapBones(rig, "LegFK", suffix)
    (uplegFk, lolegFk, footFk, toeFk) = snapFk
    muteConstraints(cnsIk, True)

    legIkToAnkle = rig["MhaLegIkToAnkle" + suffix]
    if legIkToAnkle:
        matchPoseTranslation(ankleIk, footFk, auto)
    else:
        matchIkLeg(legIk, toeFk, mBall, mToe, mHeel, auto)

    matchPoseReverse(toeRev, toeFk, auto)
    matchPoseReverse(footRev, footFk, auto)

    matchPoleTarget(kneePt, uplegFk, lolegFk, auto)

    matchPoseTwist(lolegIk, lolegFk, auto)

    if not legIkToAnkle:
        matchPoseTranslation(ankleIk, footFk, auto)

    restoreSnapProp(rig, prop, old, context)
    #muteConstraints(cnsIk, False)
    return


SnapBonesAlpha8 = {
    "Arm"   : ["upper_arm", "forearm", "hand"],
    "ArmFK" : ["upper_arm.fk", "forearm.fk", "hand.fk"],
    "ArmIK" : ["upper_arm.ik", "forearm.ik", None, "elbow.pt.ik", "hand.ik"],
    "Leg"   : ["thigh", "shin", "foot", "toe"],
    "LegFK" : ["thigh.fk", "shin.fk", "foot.fk", "toe.fk"],
    "LegIK" : ["thigh.ik", "shin.ik", "knee.pt.ik", "ankle.ik", "foot.ik", "foot.rev", "toe.rev", "ball.marker", "toe.marker", "heel.marker"],
}


def getSnapBones(rig, key, suffix):
    try:
        pb = rig.pose.bones["UpLeg_L"]
    except KeyError:
        pb = None

    if pb is not None:
        raise RuntimeError("MakeHuman alpha 7 not supported after Blender 2.68")

    try:
        rig.pose.bones["thigh.fk.L"]
        names = SnapBonesAlpha8[key]
        suffix = '.' + suffix[1:]
    except KeyError:
        names = None

    if not names:
        raise RuntimeError("Not an mhx armature")

    pbones = []
    constraints = []
    for name in names:
        if name:
            try:
                pb = rig.pose.bones[name+suffix]
            except KeyError:
                pb = None
            pbones.append(pb)
            if pb is not None:
                for cns in pb.constraints:
                    if cns.type == 'LIMIT_ROTATION' and not cns.mute:
                        constraints.append(cns)
        else:
            pbones.append(None)
    return tuple(pbones),constraints


def muteConstraints(constraints, value):
    for cns in constraints:
        cns.mute = value


class VIEW3D_OT_MhxSnapFk2IkButton(bpy.types.Operator):
    bl_idname = "mhx.snap_fk_ik"
    bl_label = "Snap FK"
    bl_options = {'UNDO'}
    data = StringProperty()

    def execute(self, context):
        bpy.ops.object.mode_set(mode='POSE')
        rig = context.object
        if rig.MhxSnapExact:
            rig["MhaRotationLimits"] = 0.0
        if self.data[:6] == "MhaArm":
            snapFkArm(context, self.data)
        elif self.data[:6] == "MhaLeg":
            snapFkLeg(context, self.data)
        return{'FINISHED'}


class VIEW3D_OT_MhxSnapIk2FkButton(bpy.types.Operator):
    bl_idname = "mhx.snap_ik_fk"
    bl_label = "Snap IK"
    bl_options = {'UNDO'}
    data = StringProperty()

    def execute(self, context):
        bpy.ops.object.mode_set(mode='POSE')
        rig = context.object
        if rig.MhxSnapExact:
            rig["MhaRotationLimits"] = 0.0
        if self.data[:6] == "MhaArm":
            snapIkArm(context, self.data)
        elif self.data[:6] == "MhaLeg":
            snapIkLeg(context, self.data)
        return{'FINISHED'}


def setSnapProp(rig, data, value, context, isIk):
    words = data.split()
    prop = words[0]
    oldValue = rig[prop]
    rig[prop] = value
    ik = int(words[1])
    fk = int(words[2])
    extra = int(words[3])
    oldIk = rig.data.layers[ik]
    oldFk = rig.data.layers[fk]
    oldExtra = rig.data.layers[extra]
    rig.data.layers[ik] = True
    rig.data.layers[fk] = True
    rig.data.layers[extra] = True
    updatePose(context)
    if isIk:
        oldValue = 1.0
        oldIk = True
        oldFk = False
    else:
        oldValue = 0.0
        oldIk = False
        oldFk = True
        oldExtra = False
    return (prop, (oldValue, ik, fk, extra, oldIk, oldFk, oldExtra), prop[-2:])


def restoreSnapProp(rig, prop, old, context):
    updatePose(context)
    (oldValue, ik, fk, extra, oldIk, oldFk, oldExtra) = old
    rig[prop] = oldValue
    rig.data.layers[ik] = oldIk
    rig.data.layers[fk] = oldFk
    rig.data.layers[extra] = oldExtra
    updatePose(context)
    return


class VIEW3D_OT_MhxToggleFkIkButton(bpy.types.Operator):
    bl_idname = "mhx.toggle_fk_ik"
    bl_label = "FK - IK"
    bl_options = {'UNDO'}
    toggle = StringProperty()

    def execute(self, context):
        words = self.toggle.split()
        rig = context.object
        prop = words[0]
        value = float(words[1])
        onLayer = int(words[2])
        offLayer = int(words[3])
        rig.data.layers[onLayer] = True
        rig.data.layers[offLayer] = False
        rig[prop] = value
        # Don't do autokey - confusing.
        #if context.tool_settings.use_keyframe_insert_auto:
        #    rig.keyframe_insert('["%s"]' % prop, frame=scn.frame_current)
        updatePose(context)
        return{'FINISHED'}

#
#   MHX FK/IK Switch panel
#

class MhxFKIKPanel(bpy.types.Panel):
    bl_label = "MHX FK/IK Switch"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig == 'MHX')

    def draw(self, context):
        rig = context.object
        layout = self.layout

        row = layout.row()
        row.label("")
        row.label("Left")
        row.label("Right")

        layout.label("FK/IK switch")
        row = layout.row()
        row.label("Arm")
        self.toggleButton(row, rig, "MhaArmIk_L", " 3", " 2")
        self.toggleButton(row, rig, "MhaArmIk_R", " 19", " 18")
        row = layout.row()
        row.label("Leg")
        self.toggleButton(row, rig, "MhaLegIk_L", " 5", " 4")
        self.toggleButton(row, rig, "MhaLegIk_R", " 21", " 20")

        layout.label("IK Influence")
        row = layout.row()
        row.label("Arm")
        row.prop(rig, '["MhaArmIk_L"]', text="")
        row.prop(rig, '["MhaArmIk_R"]', text="")
        row = layout.row()
        row.label("Leg")
        row.prop(rig, '["MhaLegIk_L"]', text="")
        row.prop(rig, '["MhaLegIk_R"]', text="")

        try:
            ok = (rig["MhxVersion"] >= 12)
        except:
            ok = False
        if not ok:
            layout.label("Snapping only works with MHX version 1.12 and later.")
            return

        layout.separator()
        layout.label("Snapping")
        row = layout.row()
        row.label("Rotation Limits")
        row.prop(rig, '["MhaRotationLimits"]', text="")
        row.prop(rig, "MhxSnapExact", text="Exact Snapping")

        layout.label("Snap Arm bones")
        row = layout.row()
        row.label("FK Arm")
        row.operator("mhx.snap_fk_ik", text="Snap L FK Arm").data = "MhaArmIk_L 2 3 12"
        row.operator("mhx.snap_fk_ik", text="Snap R FK Arm").data = "MhaArmIk_R 18 19 28"
        row = layout.row()
        row.label("IK Arm")
        row.operator("mhx.snap_ik_fk", text="Snap L IK Arm").data = "MhaArmIk_L 2 3 12"
        row.operator("mhx.snap_ik_fk", text="Snap R IK Arm").data = "MhaArmIk_R 18 19 28"

        layout.label("Snap Leg bones")
        row = layout.row()
        row.label("FK Leg")
        row.operator("mhx.snap_fk_ik", text="Snap L FK Leg").data = "MhaLegIk_L 4 5 12"
        row.operator("mhx.snap_fk_ik", text="Snap R FK Leg").data = "MhaLegIk_R 20 21 28"
        row = layout.row()
        row.label("IK Leg")
        row.operator("mhx.snap_ik_fk", text="Snap L IK Leg").data = "MhaLegIk_L 4 5 12"
        row.operator("mhx.snap_ik_fk", text="Snap R IK Leg").data = "MhaLegIk_R 20 21 28"


    def toggleButton(self, row, rig, prop, fk, ik):
        if rig[prop] > 0.5:
            row.operator("mhx.toggle_fk_ik", text="IK").toggle = prop + " 0" + fk + ik
        else:
            row.operator("mhx.toggle_fk_ik", text="FK").toggle = prop + " 1" + ik + fk


###################################################################################
#
#    Control panel
#
###################################################################################

class MhxControlPanel(bpy.types.Panel):
    bl_label = "MHX Control"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig == 'MHX')

    def draw(self, context):
        lrProps = []
        props = []
        lrFaceProps = []
        faceProps = []
        plist = list(context.object.keys())
        plist.sort()
        for prop in plist:
            if prop[0:3] == 'Mha':
                if prop[-2:] == '_L':
                    lrProps.append(prop[:-2])
                elif prop[-2:] != '_R':
                    props.append(prop)
            elif prop[0:3] == 'Mhf':
                if prop[-2:] == '_L':
                    lrFaceProps.append(prop[:-2])
                elif prop[-2:] != '_R':
                    faceProps.append(prop)

        ob = context.object
        layout = self.layout
        for prop in props:
            layout.prop(ob, '["%s"]' % prop, text=prop[3:])

        layout.separator()
        row = layout.row()
        row.label("Left")
        row.label("Right")
        for prop in lrProps:
            row = layout.row()
            row.prop(ob, '["%s"]' % (prop+"_L"), text=prop[3:])
            row.prop(ob, '["%s"]' % (prop+"_R"), text=prop[3:])

        if faceProps:
            layout.separator()
            layout.label("Face shapes")
            for prop in faceProps:
                layout.prop(ob, '["%s"]' % prop, text=prop[3:])

            layout.separator()
            row = layout.row()
            row.label("Left")
            row.label("Right")
            for prop in lrFaceProps:
                row = layout.row()
                row.prop(ob, '["%s"]' % (prop+"_L"), text=prop[3:])
                row.prop(ob, '["%s"]' % (prop+"_R"), text=prop[3:])

        return

###################################################################################
#
#    Visibility panel
#
###################################################################################
#
#    class MhxVisibilityPanel(bpy.types.Panel):
#

class MhxVisibilityPanel(bpy.types.Panel):
    bl_label = "MHX Visibility"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.MhxRig)

    def draw(self, context):
        ob = context.object
        layout = self.layout
        props = list(ob.keys())
        props.sort()
        for prop in props:
            if prop[0:3] == "Mhh":
                layout.prop(ob, '["%s"]' % prop, text="Hide %s" % prop[3:])
        layout.separator()
        layout.operator("mhx.update_textures")
        layout.separator()
        layout.operator("mhx.add_hiders")
        layout.operator("mhx.remove_hiders")
        return

class VIEW3D_OT_MhxUpdateTexturesButton(bpy.types.Operator):
    bl_idname = "mhx.update_textures"
    bl_label = "Update"
    bl_options = {'UNDO'}

    def execute(self, context):
        scn = context.scene
        for mat in bpy.data.materials:
            if mat.animation_data:
                try:
                    mat["MhxDriven"]
                except:
                    continue
                for driver in mat.animation_data.drivers:
                    prop = mat.path_resolve(driver.data_path)
                    value = driver.evaluate(scn.frame_current)
                    prop[driver.array_index] = value
        return{'FINISHED'}

class VIEW3D_OT_MhxAddHidersButton(bpy.types.Operator):
    bl_idname = "mhx.add_hiders"
    bl_label = "Add Hide Property"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig = context.object
        for ob in context.scene.objects:
            if ob.select and ob != rig:
                prop = "Mhh%s" % ob.name
                defNewProp(prop, "Bool", "default=False")
                rig[prop] = False
                addHider(ob, "hide", rig, prop)
                addHider(ob, "hide_render", rig, prop)
        return{'FINISHED'}

def addHider(ob, attr, rig, prop):
    fcu = ob.driver_add(attr)
    drv = fcu.driver
    drv.type = 'SCRIPTED'
    drv.expression = "x"
    drv.show_debug_info = True
    var = drv.variables.new()
    var.name = "x"
    targ = var.targets[0]
    targ.id = rig
    targ.data_path = '["%s"]' % prop
    return

class VIEW3D_OT_MhxRemoveHidersButton(bpy.types.Operator):
    bl_idname = "mhx.remove_hiders"
    bl_label = "Remove Hide Property"
    bl_options = {'UNDO'}

    def execute(self, context):
        rig = context.object
        for ob in context.scene.objects:
            if ob.select and ob != rig:
                ob.driver_remove("hide")
                ob.driver_remove("hide_render")
                del rig["Mhh%s" % ob.name]
        return{'FINISHED'}

###################################################################################
#
#    Lipsync panel
#
###################################################################################

#
#    visemes
#

bodyLanguageVisemes = ({
    'Rest' : [
        ('MouthWidth_L', 0),
        ('MouthWidth_R', 0),
        ('MouthNarrow_L', 0),
        ('MouthNarrow_R', 0),
        ('LipsPart', 0.6),
        ('UpLipsMidHeight', 0),
        ('LoLipsMidHeight', 0),
        ('LoLipsIn', 0),
        ('MouthOpen', 0),
        ('TongueBackHeight', 0),
        ('TongueHeight', 0),
        ],
    'Etc' : [
        ('MouthWidth_L', 0),
        ('MouthWidth_R', 0),
        ('MouthNarrow_L', 0),
        ('MouthNarrow_R', 0),
        ('LipsPart', 0.4),
        ('UpLipsMidHeight', 0),
        ('LoLipsMidHeight', 0),
        ('LoLipsIn', 0),
        ('MouthOpen', 0),
        ('TongueBackHeight', 0),
        ('TongueHeight', 0),
        ],
    'MBP' : [
        ('MouthWidth_L', 0),
        ('MouthWidth_R', 0),
        ('MouthNarrow_L', 0),
        ('MouthNarrow_R', 0),
        ('LipsPart', 0),
        ('UpLipsMidHeight', 0),
        ('LoLipsMidHeight', 0),
        ('LoLipsIn', 0),
        ('MouthOpen', 0),
        ('TongueBackHeight', 0),
        ('TongueHeight', 0),
        ],
    'OO' : [
        ('MouthWidth_L', 0),
        ('MouthWidth_R', 0),
        ('MouthNarrow_L', 1.0),
        ('MouthNarrow_R', 1.0),
        ('LipsPart', 0),
        ('UpLipsMidHeight', 0),
        ('LoLipsMidHeight', 0),
        ('LoLipsIn', 0),
        ('MouthOpen', 0.4),
        ('TongueBackHeight', 0),
        ('TongueHeight', 0),
        ],
    'O' : [
        ('MouthWidth_L', 0),
        ('MouthWidth_R', 0),
        ('MouthNarrow_L', 0.9),
        ('MouthNarrow_R', 0.9),
        ('LipsPart', 0),
        ('UpLipsMidHeight', 0),
        ('LoLipsMidHeight', 0),
        ('LoLipsIn', 0),
        ('MouthOpen', 0.8),
        ('TongueBackHeight', 0),
        ('TongueHeight', 0),
        ],
    'R' : [
        ('MouthWidth_L', 0),
        ('MouthWidth_R', 0),
        ('MouthNarrow_L', 0.5),
        ('MouthNarrow_R', 0.5),
        ('LipsPart', 0),
        ('UpLipsMidHeight', 0.2),
        ('LoLipsMidHeight', -0.2),
        ('LoLipsIn', 0),
        ('MouthOpen', 0),
        ('TongueBackHeight', 0),
        ('TongueHeight', 0),
        ],
    'FV' : [
        ('MouthWidth_L', 0.2),
        ('MouthWidth_R', 0.2),
        ('MouthNarrow_L', 0),
        ('MouthNarrow_R', 0),
        ('LipsPart', 1.0),
        ('UpLipsMidHeight', 0),
        ('LoLipsMidHeight', 0.3),
        ('LoLipsIn', 0.6),
        ('MouthOpen', 0),
        ('TongueBackHeight', 0),
        ('TongueHeight', 0),
        ],
    'S' : [
        ('MouthWidth_L', 0),
        ('MouthWidth_R', 0),
        ('MouthNarrow_L', 0),
        ('MouthNarrow_R', 0),
        ('LipsPart', 0),
        ('UpLipsMidHeight', 0.5),
        ('LoLipsMidHeight', -0.7),
        ('LoLipsIn', 0),
        ('MouthOpen', 0),
        ('TongueBackHeight', 0),
        ('TongueHeight', 0),
        ],
    'SH' : [
        ('MouthWidth_L', 0.8),
        ('MouthWidth_R', 0.8),
        ('MouthNarrow_L', 0),
        ('MouthNarrow_R', 0),
        ('LipsPart', 0),
        ('UpLipsMidHeight', 1.0),
        ('LoLipsMidHeight', 0),
        ('LoLipsIn', 0),
        ('MouthOpen', 0),
        ('TongueBackHeight', 0),
        ('TongueHeight', 0),
        ],
    'EE' : [
        ('MouthWidth_L', 0.2),
        ('MouthWidth_R', 0.2),
        ('MouthNarrow_L', 0),
        ('MouthNarrow_R', 0),
        ('LipsPart', 0),
        ('UpLipsMidHeight', 0.6),
        ('LoLipsMidHeight', -0.6),
        ('LoLipsIn', 0),
        ('MouthOpen', 0.5),
        ('TongueBackHeight', 0),
        ('TongueHeight', 0),
        ],
    'AH' : [
        ('MouthWidth_L', 0),
        ('MouthWidth_R', 0),
        ('MouthNarrow_L', 0),
        ('MouthNarrow_R', 0),
        ('LipsPart', 0),
        ('UpLipsMidHeight', 0.4),
        ('LoLipsMidHeight', 0),
        ('LoLipsIn', 0),
        ('MouthOpen', 0.7),
        ('TongueBackHeight', 0),
        ('TongueHeight', 0),
        ],
    'EH' : [
        ('MouthWidth_L', 0),
        ('MouthWidth_R', 0),
        ('MouthNarrow_L', 0),
        ('MouthNarrow_R', 0),
        ('LipsPart', 0),
        ('UpLipsMidHeight', 0.5),
        ('LoLipsMidHeight', -0.6),
        ('LoLipsIn', 0),
        ('MouthOpen', 0.25),
        ('TongueBackHeight', 0),
        ('TongueHeight', 0),
        ],
    'TH' : [
        ('MouthWidth_L', 0),
        ('MouthWidth_R', 0),
        ('MouthNarrow_L', 0),
        ('MouthNarrow_R', 0),
        ('LipsPart', 0),
        ('UpLipsMidHeight', 0),
        ('LoLipsMidHeight', 0),
        ('LoLipsIn', 0),
        ('MouthOpen', 0.2),
        ('TongueBackHeight', 1.0),
        ('TongueHeight', 1.0)
        ],
    'L' : [
        ('MouthWidth_L', 0),
        ('MouthWidth_R', 0),
        ('MouthNarrow_L', 0),
        ('MouthNarrow_R', 0),
        ('LipsPart', 0),
        ('UpLipsMidHeight', 0.5),
        ('LoLipsMidHeight', -0.5),
        ('LoLipsIn', 0),
        ('MouthOpen', -0.2),
        ('TongueBackHeight', 1.0),
        ('TongueHeight', 1.0),
        ],
    'G' : [
        ('MouthWidth_L', 0),
        ('MouthWidth_R', 0),
        ('MouthNarrow_L', 0),
        ('MouthNarrow_R', 0),
        ('LipsPart', 0),
        ('UpLipsMidHeight', 0.5),
        ('LoLipsMidHeight', -0.5),
        ('LoLipsIn', 0),
        ('MouthOpen', -0.2),
        ('TongueBackHeight', 1.0),
        ('TongueHeight', 0),
        ],

    'Blink' : [
        ('UpLidUp_L', 1),
        ('UpLidUp_R', 1),
        ('LoLidDown_L', 1),
        ('LoLidDown_R', 1)
        ],

    'Unblink' : [
        ('UpLidUp_L', 0),
        ('UpLidUp_R', 0),
        ('LoLidDown_L', 0),
        ('LoLidDown_R', 0)
        ],
})

VisemePanelBones = {
    'MouthOpen' :       ('PJaw', (0,0.25)),
    'UpLipsMidHeight' : ('PUpLipMid', (0,-0.25)),
    'LoLipsMidHeight' : ('PLoLipMid', (0,-0.25)),
    'LoLipsIn':         ('PLoLipMid', (-0.25,0)),
    'MouthWidth_L' :    ('PMouth_L', (0.25,0)),
    'MouthWidth_R' :    ('PMouth_R', (-0.25,0)),
    'MouthNarrow_L' :   ('PMouth_L', (-0.25,0)),
    'MouthNarrow_R' :   ('PMouth_R', (0.25,0)),
    'LipsPart' :        ('PMouthMid', (0, -0.25)),
    'TongueBackHeight': ('PTongue', (-0.25, 0)),
    'TongueHeight' :    ('PTongue', (0, -0.25)),

    'UpLidUp_L' :       ('PUpLid_L', (0,1.0)),
    'UpLidUp_R' :       ('PUpLid_R', (0,1.0)),
    'LoLidDown_L' :     ('PLoLid_L', (0,-1.0)),
    'LoLidDown_R' :     ('PLoLid_R', (0,-1.0)),
}

VisemeList = [
    ('Rest', 'Etc', 'AH'),
    ('MBP', 'OO', 'O'),
    ('R', 'FV', 'S'),
    ('SH', 'EE', 'EH'),
    ('TH', 'L', 'G')
]

#
#   makeVisemes(ob, scn):
#   class VIEW3D_OT_MhxMakeVisemesButton(bpy.types.Operator):
#

def makeVisemes(ob, scn):
    rig = ob.parent
    if ob.type != 'MESH':
        print("Active object %s is not a mesh" % ob)
        return
    if not ob.data.shape_keys:
        print("%s has no shapekeys" % ob)
        return
    try:
        ob.data.shape_keys.key_blocks["VIS_Rest"]
        print("Visemes already created")
        return
    except KeyError:
        pass
    try:
        ob.data.shape_keys.key_blocks["MouthOpen"]
    except KeyError:
        print("Mesh does not have face shapes")
        return

    verts = ob.data.vertices
    for (vis,shapes) in bodyLanguageVisemes.items():
        if vis in ['Blink', 'Unblink']:
            continue
        vkey = ob.shape_key_add(name="VIS_%s" % vis)
        print(vkey.name)
        for n,v in enumerate(verts):
            vkey.data[n].co = v.co
        for (name,value) in shapes:
            if name[-2:] == "_R":
                continue
            skey = ob.data.shape_keys.key_blocks[name]
            factor = 0.75*value
            for n,v in enumerate(verts):
                vkey.data[n].co += factor*(skey.data[n].co - v.co)
    print("Visemes made")
    return

class VIEW3D_OT_MhxMakeVisemesButton(bpy.types.Operator):
    bl_idname = "mhx.make_visemes"
    bl_label = "Generate viseme shapekeys"
    bl_options = {'UNDO'}

    def execute(self, context):
        makeVisemes(context.object, context.scene)
        return{'FINISHED'}

#
#    mohoVisemes
#    magpieVisemes
#

MohoVisemes = dict({
    "rest" : "Rest",
    "etc" : "Etc",
    "AI" : "AH",
    "O" : "O",
    "U" : "OO",
    "WQ" : "AH",
    "L" : "L",
    "E" : "EH",
    "MBP" : "MBP",
    "FV" : "FV",
})

MagpieVisemes = dict({
    "CONS" : "Etc",
    "AI" : "AH",
    "E" : "EH",
    "O" : "O",
    "UW" : "AH",
    "MBP" : "MBP",
    "L" : "L",
    "FV" : "FV",
    "Sh" : "SH",
})

#
#    setViseme(context, vis, setKey, frame):
#    setBoneLocation(context, pbone, loc, mirror, setKey, frame):
#    class VIEW3D_OT_MhxVisemeButton(bpy.types.Operator):
#

def getVisemeSet(context, rig):
    if rig.MhxVisemeSet == "StopStaring":
        return stopStaringVisemes
    elif rig.MhxVisemeSet == "BodyLanguage":
        return bodyLanguageVisemes
    else:
        raise MhxError("Unknown viseme set %s" % visset)


def setVisemeAlpha7(context, vis, visemes, setKey, frame):
    (rig, mesh) = getMhxRigMesh(context.object)
    isPanel = False
    isProp = False
    shapekeys = None
    scale = 0.75
    if rig.MhxShapekeyDrivers:
        try:
            scale *= rig.pose.bones['PFace'].bone.length
            isPanel = True
        except:
            isProp = True
    elif mesh:
        shapekeys = mesh.data.shape_keys.key_blocks

    for (skey, value) in visemes[vis]:
        if isPanel:
            (b, (x,z)) = VisemePanelBones[skey]
            loc = mathutils.Vector((float(x*value),0,float(z*value)))
            pb = rig.pose.bones[b]
            pb.location = loc*scale
            if setKey or context.tool_settings.use_keyframe_insert_auto:
                for n in range(3):
                    pb.keyframe_insert('location', index=n, frame=frame, group=pb.name)
        elif isProp:
            skey = 'Mhf' + skey
            try:
                prop = rig[skey]
            except:
                continue
            rig[skey] = value*scale
            if setKey or context.tool_settings.use_keyframe_insert_auto:
                rig.keyframe_insert('["%s"]' % skey, frame=frame, group="Visemes")
        elif shapekeys:
            try:
                shapekeys[skey].value = value*scale
            except:
                continue
            if setKey or context.tool_settings.use_keyframe_insert_auto:
                shapekeys[skey].keyframe_insert("value", frame=frame)
    updatePose(context)
    return


class VIEW3D_OT_MhxVisemeButton(bpy.types.Operator):
    bl_idname = 'mhx.pose_viseme'
    bl_label = 'Viseme'
    bl_options = {'UNDO'}
    viseme = StringProperty()

    def invoke(self, context, event):
        (rig, mesh) = getMhxRigMesh(context.object)
        visemes = getVisemeSet(context, rig)
        setVisemeAlpha7(context, self.viseme, visemes, False, context.scene.frame_current)
        return{'FINISHED'}


def readLipsync(context, filepath, offs, struct):
    (rig, mesh) = getMhxRigMesh(context.object)
    if rig.MhxVisemeSet:
        visemes = getVisemeSet(context, rig)
    else:
        props = getProps(rig, "Mhv")
        visemes = {}
        oldKeys = []
        for prop in props:
            dummy,units = getUnitsFromString("x;"+rig[prop])
            visemes[prop] = units
        props = getProps(rig, "Mhsmouth")
        auto = context.tool_settings.use_keyframe_insert_auto
        auto = True
        factor = rig.MhxStrength
        shapekeys = getMhmShapekeys(rig, mesh)
    context.scene.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')

    fp = open(filepath, "rU")
    for line in fp:
        words= line.split()
        if len(words) < 2:
            continue
        else:
            vis = struct[words[1]]
            frame = int(words[0])+offs
        if rig.MhxVisemeSet:
            setVisemeAlpha7(context, vis, visemes, True, frame)
        else:
            setMhmProps(rig, shapekeys, "Mhsmouth", visemes["Mhv"+vis], factor, auto, frame)
    fp.close()

    #setInterpolation(rig)
    updatePose(context)
    print("Lipsync file %s loaded" % filepath)


class VIEW3D_OT_MhxMohoButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mhx.pose_load_moho"
    bl_label = "Load Moho (.dat)"
    bl_options = {'UNDO'}

    filename_ext = ".dat"
    filter_glob = StringProperty(default="*.dat", options={'HIDDEN'})
    filepath = StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        readLipsync(context, self.properties.filepath, context.scene.frame_start - 1, MohoVisemes)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class MhxLipsyncPanel(bpy.types.Panel):
    bl_label = "MHX Lipsync"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasProps(context.object, "Mhv")

    def draw(self, context):
        rig,mesh = getMhxRigMesh(context.object)
        if not rig:
            layout.label("No MHX rig found")
            return
        layout = self.layout

        if not rig.MhxVisemeSet:
            visemes = getProps(rig, "Mhv")
            if not visemes:
                layout.label("No visemes found")
                return

            layout.operator("mhx.pose_reset_expressions", text="Reset visemes").prefix="Mhsmouth"
            layout.operator("mhx.pose_key_expressions", text="Key visemes").prefix="Mhsmouth"
            layout.prop(rig, "MhxStrength")
            layout.separator()
            n = 0
            for prop in visemes:
                if n % 3 == 0:
                    row = layout.row()
                    n = 0
                row.operator("mhx.pose_mhm", text=prop[3:]).data="Mhsmouth;"+rig[prop]
                n += 1
            while n % 3 != 0:
                row.label("")
                n += 1
            layout.separator()
            row = layout.row()
            row.operator("mhx.pose_mhm", text="Blink").data="Mhsmouth;eye_left_closure:1;eye_right_closure:1"
            row.operator("mhx.pose_mhm", text="Unblink").data="Mhsmouth;eye_left_closure:0;eye_right_closure:0"
        else:
            for (vis1, vis2, vis3) in VisemeList:
                row = layout.row()
                row.operator("mhx.pose_viseme", text=vis1).viseme = vis1
                row.operator("mhx.pose_viseme", text=vis2).viseme = vis2
                row.operator("mhx.pose_viseme", text=vis3).viseme = vis3
            layout.separator()
            row = layout.row()
            row.operator("mhx.pose_viseme", text="Blink").viseme = 'Blink'
            row.operator("mhx.pose_viseme", text="Unblink").viseme = 'Unblink'
            layout.separator()
            layout.operator("mhx.make_visemes")

        layout.separator()
        row = layout.row()
        row.operator("mhx.pose_load_moho")
        #layout.operator("mhx.update")

#
#   updatePose(context):
#   class VIEW3D_OT_MhxUpdateButton(bpy.types.Operator):
#

def updatePose(context):
    scn = context.scene
    scn.frame_current = scn.frame_current
    bpy.ops.object.posemode_toggle()
    bpy.ops.object.posemode_toggle()
    return

class VIEW3D_OT_MhxUpdateButton(bpy.types.Operator):
    bl_idname = "mhx.update"
    bl_label = "Update"

    def execute(self, context):
        updatePose(context)
        return{'FINISHED'}


###################################################################################
#
#    Expression panels
#
###################################################################################

class VIEW3D_OT_MhxResetExpressionsButton(bpy.types.Operator):
    bl_idname = "mhx.pose_reset_expressions"
    bl_label = "Reset expressions"
    bl_options = {'UNDO'}
    prefix = StringProperty()

    def execute(self, context):
        rig,mesh = getMhxRigMesh(context.object)
        shapekeys = getMhmShapekeys(rig, mesh)
        clearMhmProps(rig, shapekeys, self.prefix, context.tool_settings.use_keyframe_insert_auto, context.scene.frame_current)
        updatePose(context)
        return{'FINISHED'}


class VIEW3D_OT_MhxKeyExpressionsButton(bpy.types.Operator):
    bl_idname = "mhx.pose_key_expressions"
    bl_label = "Key expressions"
    bl_options = {'UNDO'}
    prefix = StringProperty()

    def execute(self, context):
        rig,mesh = getMhxRigMesh(context.object)
        props = getProps(rig, self.prefix)
        frame = context.scene.frame_current
        for prop in props:
            rig.keyframe_insert('["%s"]'%prop, frame=frame)
        updatePose(context)
        return{'FINISHED'}


class VIEW3D_OT_MhxPinExpressionButton(bpy.types.Operator):
    bl_idname = "mhx.pose_pin_expression"
    bl_label = "Pin"
    bl_options = {'UNDO'}
    data = StringProperty()

    def execute(self, context):
        rig,mesh = getMhxRigMesh(context.object)
        words = self.data.split(";")
        prefix = words[0]
        expression = words[1]

        props = getProps(rig, prefix)
        if context.tool_settings.use_keyframe_insert_auto:
            frame = context.scene.frame_current
            for prop in props:
                old = rig[prop]
                if prop == expression:
                    rig[prop] = 1.0
                else:
                    rig[prop] = 0.0
                if abs(rig[prop] - old) > 1e-3:
                    rig.keyframe_insert('["%s"]'%prop, frame=frame)
        else:
            for prop in props:
                if prop == expression:
                    rig[prop] = 1.0
                else:
                    rig[prop] = 0.0
        updatePose(context)
        return{'FINISHED'}


def getMhmShapekeys(rig, mesh):
    if rig.MhxShapekeyDrivers:
        return None
    else:
        return mesh.data.shape_keys.key_blocks


def setMhmProps(rig, shapekeys, prefix, units, factor, auto, frame):
    clearMhmProps(rig, shapekeys, prefix, auto, frame)
    for (prop, value) in units:
        if shapekeys:
            skey = prop[3:].replace("_","-")
            shapekeys[skey].value = factor*value
            if auto:
                shapekeys[skey].keyframe_insert("value", frame=frame)
        else:
            rig[prop] = factor*value
            if auto:
                rig.keyframe_insert('["%s"]'%prop, frame=frame)


def clearMhmProps(rig, shapekeys, prefix, auto, frame):
    props = getProps(rig, prefix)
    for prop in props:
        if shapekeys:
            skey = prop[3:].replace("_","-")
            shapekeys[skey].value = 0.0
            if auto:
                shapekeys[skey].keyframe_insert("value", frame=frame)
        else:
            rig[prop] = 0.0
            if auto:
                rig.keyframe_insert('["%s"]'%prop, frame=frame)


def getUnitsFromString(string):
    words = string.split(";")
    prefix = words[0]
    units = []
    for word in words[1:]:
        if word == "":
            continue
        unit = word.split(":")
        prop = "Mhs" + unit[0]
        value = float(unit[1])
        units.append((prop, value))
    return prefix,units


class VIEW3D_OT_MhxMhmButton(bpy.types.Operator):
    bl_idname = "mhx.pose_mhm"
    bl_label = "Mhm"
    bl_options = {'UNDO'}
    data = StringProperty()

    def execute(self, context):
        rig,mesh = getMhxRigMesh(context.object)
        auto = context.tool_settings.use_keyframe_insert_auto
        frame = context.scene.frame_current
        shapekeys = getMhmShapekeys(rig, mesh)
        prefix,units = getUnitsFromString(self.data)
        setMhmProps(rig, shapekeys, prefix, units, rig.MhxStrength, auto, frame)
        updatePose(context)
        return{'FINISHED'}


def getProps(rig, prefix):
    props = []
    for prop in rig.keys():
        if prop.startswith(prefix):
            props.append(prop)
    props.sort()
    return props


def hasProps(ob, prefix):
    if ob is None:
        return False
    if ob.type == 'MESH' and ob.parent:
        rig = ob.parent
    elif ob.type == 'ARMATURE':
        rig = ob
    else:
        return False
    for prop in rig.keys():
        if prop.startswith(prefix):
            return True
    return False


class MhxExpressionsPanel(bpy.types.Panel):
    bl_label = "MHX Expressions"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasProps(context.object, "Mhe")

    def draw(self, context):
        layout = self.layout
        rig,mesh = getMhxRigMesh(context.object)
        if not rig:
            layout.label("No MHX rig found")
            return
        exprs = getProps(rig, "Mhe")
        if not exprs:
            layout.label("No expressions found")
            return

        layout.operator("mhx.pose_reset_expressions").prefix="Mhs"
        layout.operator("mhx.pose_key_expressions").prefix="Mhs"
        layout.prop(rig, "MhxStrength")
        layout.separator()
        for prop in exprs:
            layout.operator("mhx.pose_mhm", text=prop[3:]).data="Mhs;"+rig[prop]


def drawShapePanel(self, context, prefix, name):
    layout = self.layout
    rig,mesh = getMhxRigMesh(context.object)
    if not rig:
        print("No MHX rig found")
        return
    if not rig.MhxShapekeyDrivers:
        layout.label("No shapekey drivers.")
        layout.label("Set %s values in mesh context instead" % name)
        return
    props = getProps(rig, prefix)
    if not props:
        layout.label("No %ss found" % name)
        return

    layout.operator("mhx.pose_reset_expressions", text="Reset %ss" % name).prefix=prefix
    layout.operator("mhx.pose_key_expressions", text="Key %ss" % name).prefix=prefix
    #layout.operator("mhx.update")

    layout.separator()
    for prop in props:
        row = layout.split(0.85)
        row.prop(rig, '["%s"]' % prop, text=prop[3:])
        row.operator("mhx.pose_pin_expression", text="", icon='UNPINNED').data = (prefix + ";" + prop)
    return


class MhxExpressionUnitsPanel(bpy.types.Panel):
    bl_label = "MHX Expression Tuning"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasProps(context.object, "Mhs")

    def draw(self, context):
        drawShapePanel(self, context, "Mhs", "expression")


class MhxCustomShapePanel(bpy.types.Panel):
    bl_label = "MHX Custom Shapes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return hasProps(context.object, "Mhc")

    def draw(self, context):
        drawShapePanel(self, context, "Mhc", "custom shape")

###################################################################################
#
#    Common functions
#
###################################################################################
#
#   getMhxRigMesh(ob):
#

def pollMhx(ob):
    if not ob:
        return False
    elif ob.type == 'ARMATURE':
        return ob.MhxRig
    elif ob.type == 'MESH':
        par = ob.parent
        return (par and (par.type == 'ARMATURE') and par.MhxRig)
    else:
        return False

def getMhxRigMesh(ob):
    if ob.type == 'ARMATURE':
        for mesh in ob.children:
            if mesh.MhxMesh and ob.MhxRig:
                return (ob, mesh)
        return (ob, None)
    elif ob.type == 'MESH':
        par = ob.parent
        if (par and par.type == 'ARMATURE' and par.MhxRig):
            if ob.MhxMesh:
                return (par, ob)
            else:
                return (par, None)
        else:
            return (None, None)
    return (None, None)


#
#    setInterpolation(rig):
#

def setInterpolation(rig):
    if not rig.animation_data:
        return
    act = rig.animation_data.action
    if not act:
        return
    for fcu in act.fcurves:
        for pt in fcu.keyframe_points:
            pt.interpolation = 'LINEAR'
        fcu.extrapolation = 'CONSTANT'
    return

###################################################################################
#
#    initialize and register
#
###################################################################################

def menu_func(self, context):
    self.layout.operator(ImportMhx.bl_idname, text="MakeHuman (.mhx)...")

def register():
    bpy.types.Object.MhxVersionStr = StringProperty(name="Version", default="", maxlen=128)
    bpy.types.Object.MhAlpha8 = BoolProperty(default=False)
    bpy.types.Object.MhxMesh = BoolProperty(default=False)
    bpy.types.Object.MhxRig = StringProperty(default="")
    bpy.types.Object.MhxVisemeSet = StringProperty(default="")
    bpy.types.Object.MhxRigify = BoolProperty(default=False)
    bpy.types.Object.MhxSnapExact = BoolProperty(default=False)
    bpy.types.Object.MhxShapekeyDrivers = BoolProperty(default=True)
    bpy.types.Object.MhxStrength = FloatProperty(
        name = "Expression strength",
        description = "Multiply expression with this factor",
        default=1.0, min=-1.0, max=2.0
        )
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)

def unregister():
    try:
        bpy.utils.unregister_module(__name__)
    except:
        pass
    try:
        bpy.types.INFO_MT_file_import.remove(menu_func)
    except:
        pass

if __name__ == "__main__":
    unregister()
    register()





