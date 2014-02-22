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

TODO
"""

import armature
from armature.flags import *
import log

class CTarget:
    def __init__(self, var, target):
        self.variable = var
        if var.type == 'TRANSFORMS':
            (self.idtype, self.object, self.bone, self.type, self.flags) = target
            if self.type[0:3] == 'LOC':
                var.useLoc = True
        elif var.type == 'ROTATION_DIFF':
            (self.idtype, self.object, self.bone, self.flags) = target
        elif var.type == 'SINGLE_PROP':
            (self.idtype, self.object, self.datapath) = target

    def display(self):
        log.debug("      <CTarget %s %s>", self.idtype, self.object)

    def write25(self, fp):
        fp.write("          Target %s %s\n" % (self.object, self.idtype))
        if self.variable.type == 'TRANSFORMS':
            fp.write(
                "             transform_type '%s' ;\n" % self.type +
                "             bone_target '%s' ;\n" % self.bone)
            if self.flags & C_LOC:
                fp.write("             transform_space 'LOCAL_SPACE' ;\n")
            else:
                fp.write("             transform_space 'WORLD_SPACE' ;\n")
        elif self.variable.type == 'ROTATION_DIFF':
            fp.write(
                "            bone_target '%s' ;\n" % self.bone +
                "            transform_space 'WORLD_SPACE' ; \n")
        elif self.variable.type == 'SINGLE_PROP':
            fp.write("            data_path '%s' ;\n" % self.datapath)
        fp.write("          end Target\n")


class CVariable:
    def __init__(self, name, drv, type, targets):
        self.name = name
        self.type = type
        self.targets = []
        for target in targets:
            self.targets.append( CTarget(self, target) )
        if self.type == 'TRANSFORMS':
            drv.useMod = True
        elif self.type == 'ROTATION_DIFF':
            drv.useKeypoints = True
            drv.useMod = False
        elif self.type == 'SINGLE_PROP':
            if drv.coeffs:
                drv.useMod = True
        else:
            raise NameError("Unknown driver var type %s" % self.type)

    def display(self):
        log.debug("    <CVariable %s %s", self.name, self.type)
        for target in self.targets:
            target.display()
        log.debug("    >")

    def write25(self, fp):
        fp.write("        DriverVariable %s %s\n" % (self.name, self.type))
        for target in self.targets:
            target.write25(fp)
        fp.write("        end DriverVariable\n")


class CDriver:
    def __init__(self, cond, drvdata, extra, channel, index, coeffs, variables):
        self.cond = cond
        try:
            (self.drvtype, self.expr) = drvdata
        except:
            self.drvtype = drvdata
        self.extra = extra
        self.channel = channel
        self.index = index
        self.coeffs = coeffs
        self.variables = []
        self.useLoc = False
        self.useKeypoints = False
        self.useMod = False
        for (var, type, targets) in variables:
            self.variables.append( CVariable(var, self, type, targets) )

    def display(self):
        log.debug("  <CDriver %s %d", self.channel, self.index)
        for var in self.variables:
            var.display()
        log.debug("  >")

    def write25(self, fp):
        fp.write("\n"+
            "    FCurve %s %d %s\n" % (self.channel, self.index, self.cond) +
            "      Driver %s\n" % self.drvtype )
        if self.drvtype == 'SCRIPTED':
            fp.write("        expression '%s' ;\n" % self.expr)
        for var in self.variables:
            var.write25(fp)
        fp.write(
            "        show_debug_info True ;\n" +
            "      end Driver\n")

        if self.useMod:
            fp.write(
                "      FModifier GENERATOR \n" +
                "        active False ;\n" +
                "        use_additive False ;\n")

            (a0,a1) = self.coeffs
            if self.useLoc:
                fp.write("        coefficients Array %s %s*One%s ;\n" % (a0,a1,self.extra))
            else:
                fp.write("        coefficients Array %s %s%s ;\n" % (a0,a1,self.extra))

            fp.write(
                "        show_expanded True ;\n" +
                "        mode 'POLYNOMIAL' ;\n" +
                "        mute False ;\n" +
                "        poly_order 1 ;\n" +
                "      end FModifier\n")

        if self.useKeypoints:
            for (x,y) in self.coeffs:
                fp.write("      kp %.4f %.4f ; \n" % (x,y))

        fp.write(
                "      extrapolation 'CONSTANT' ;\n" +
                "      lock False ;\n" +
                "      select False ;\n" +
                "    end FCurve\n")

#
#    Functions
#

def writeDriver(fp, cond, drvdata, extra, channel, index, coeffs, variables):
    drv = CDriver(cond, drvdata, extra, channel, index, coeffs, variables)
    if fp:
        drv.write25(fp)
    return drv


"""
def writeEnumDrivers(fp, drivers):
    for (bone, cns, targ, channel) in drivers:
        drvVars = [("x", 'TRANSFORMS', [('OBJECT', amt.name, targ, channel, C_LOC)])]
        for n, cnsName in enumerate(cns):
            expr = '(x>%.1f)*(x<%.1f)' % (n-0.5, n+0.5)
            drv = writeDriver(fp, True, ('SCRIPTED', expr), "","pose.bones[\"%s\"].constraints[\"%s\"].influence" % (bone, cnsName), -1, (0,1), drvVars)
            driverList.append(drv)
    return driverList
"""


def writePropDrivers(fp, amt, drivers, suffix, prefix):
    driverList = []
    for (bone, cns, props, expr) in drivers:
        drvVars = []
        n = 1
        for prop in props:
            if suffix:
                datapath = '["%s%s_%s"]' % (prefix, prop, suffix)
            else:
                datapath = '["%s%s"]' % (prefix, prop)
            drvVars.append( ("x%d" % n, 'SINGLE_PROP', [('OBJECT', amt.name, datapath)]) )
            n += 1
        if suffix:
            bone = "%s.%s" % (bone, suffix)
        drv = writeDriver(fp, True, ('SCRIPTED', expr), "",
            "pose.bones[\"%s\"].constraints[\"%s\"].influence" % (bone, cns),
            -1, (0,1), drvVars)
        driverList.append(drv)
    return driverList


def writeShapePropDrivers(fp, amt, skeys, proxy, prefix, callback=None):
    driverList = []
    for skey in skeys:
        if useThisShape(skey, proxy):
            drvVar = ("x", 'SINGLE_PROP', [('OBJECT', amt.name, '["%s%s"]' % (prefix, skey))])
            drv = writeDriver(fp, True, ('SCRIPTED', "x"), "",
                "key_blocks[\"%s\"].value" % (skey),
                -1, (0,1), [drvVar])
            driverList.append(drv)
    return driverList


def writePropDriver(fp, amt, props, expr, dataPath, index):
    drvVars = []
    n = 1
    for prop in props:
        drvVars.append( ("x%d" % n, 'SINGLE_PROP', [('OBJECT', amt.name, '["%s"]' % (prop))]) )
        n += 1
    return writeDriver(fp, True, ('SCRIPTED', expr), "", dataPath, index, (0,1), drvVars)


def writeTextureDrivers(fp, amt, drivers):
    driverList = []
    for (tex, vlist) in drivers.items():
        drvVars = []
        (texnum, targ, channel, coeffs) = vlist
        drvVars.append( (targ, 'TRANSFORMS', [('OBJECT', amt.name, targ, channel, C_LOC)]) )
        drv = writeDriver(fp, 'toggle&T_Shapekeys', 'AVERAGE', "", "texture_slots[%d].normal_factor" % (texnum), -1, coeffs, drvVars)
        driverList.append(drv)
    return driverList


def writeShapeDrivers(fp, amt, drivers, proxy):
    driverList = []
    dlist = list(drivers.items())
    dlist.sort()
    for (shape, vlist) in dlist:
        if useThisShape(shape, proxy):
            drvVars = []
            (file, targ, channel, coeffs, min, max) = vlist
            drvVars.append( (targ, 'TRANSFORMS', [('OBJECT', amt.name, targ, channel, C_LOC)]) )
            drv = writeDriver(fp, 'toggle&T_Shapekeys', 'AVERAGE', "", "key_blocks[\"%s\"].value" % (shape), -1, coeffs, drvVars)
            driverList.append(drv)
    return driverList


def writeTargetDrivers(fp, drivers, rig, empties):
    driverList = []
    coeffs = [(0,0),(1,1)]
    for (fname, lr, expr, vars) in drivers:
        if fname in empties:
            continue
        elif lr:
            for suffix in ["_L", "_R"]:
                drvVars = []
                n = 0
                for (bone, targ) in vars:
                    n += 1
                    drvVars.append( ("x%d" % n, "ROTATION_DIFF",
                        [('OBJECT', rig, bone+suffix, C_LOC),('OBJECT', rig, targ+suffix, C_LOC)]) )
                drv = writeDriver(fp, True, ('SCRIPTED', expr), "", "key_blocks[\"%s\"].value" % (fname+suffix), -1, coeffs, drvVars)
                driverList.append(drv)
        else:
            drvVars = []
            n = 0
            for (bone, targ) in vars:
                n += 1
                drvVars.append( ("x%d" % n, "ROTATION_DIFF",
                        [('OBJECT', rig, bone, C_LOC),('OBJECT', rig, targ, C_LOC)]) )
            drv = writeDriver(fp, True, ('SCRIPTED', expr), "", "key_blocks[\"%s\"].value" % (fname+suffix), -1, coeffs, drvVars)
            driverList.append(drv)
    return driverList


def writeMuscleDrivers(fp, drivers, rig):
    driverList = []
    for (bone, cnsName, expr, targs, keypoints)  in drivers:
        drvVars = []
        if expr:
            drvdata = ('SCRIPTED', expr)
        else:
            drvdata = 'MIN'
        for (var, type, targ1, targ2) in targs:
            if type == 'ROTATION_DIFF':
                drvVars.append( (var, type, [('OBJECT', rig, targ1, C_LOC), ('OBJECT', rig, targ2, C_LOC)]) )
            elif type == 'SINGLE_PROP':
                drvVars.append( (var, type, [('OBJECT', amt.name, '["%s"]' % (targ1))]) )
        drv = writeDriver(fp, True, drvdata, "","pose.bones[\"%s\"].constraints[\"%s\"].influence" % (bone, cnsName), -1, keypoints, drvVars)
        driverList.append(drv)
    return driverList


def writeRotDiffDrivers(fp, drivers, proxy):
    driverList = []
    for (shape, vlist) in drivers.items():
        if useThisShape(shape, proxy):
            (targ1, targ2, keypoints) = vlist
            drvVars = [(targ2, 'ROTATION_DIFF', [
                ('OBJECT', amt.name, targ1, C_LOC),
                ('OBJECT', amt.name, targ2, C_LOC)]
             )]
            drv = writeDriver(fp, True, 'MIN', "", "key_blocks[\"%s\"].value" % (shape), -1, keypoints, drvVars)
            driverList.append(drv)
    return driverList


def writeScriptedBoneDrivers(fp, amt, boneDrivers):
    drivers = []
    for boneDriver in boneDrivers:
        (driven, driver, channel, expr) = boneDriver
        drivers.append(
            (driven, 'ROTE', ('SCRIPTED', expr), None, 0, (0, 1),
                [("x", 'TRANSFORMS', [('OBJECT', amt.name, driver, channel, C_LOC)])]) )
    return writeDrivers(fp, True, drivers)


def writeDrivers(fp, cond, drivers):
    driverList = []
    for drv in drivers:
        (bone, type, drvdata, name, index, coeffs, variables) = drv
        if type == 'INFL':
            drv = writeDriver(fp, cond, drvdata, "", "pose.bones[\"%s\"].constraints[\"%s\"].influence" % (bone, name), index, coeffs, variables)
        elif type == 'ROTE':
            drv = writeDriver(fp, cond, drvdata, "", "pose.bones[\"%s\"].rotation_euler" % bone, index, coeffs, variables)
        elif type == 'ROTQ':
            drv = writeDriver(fp, cond, drvdata, "", "pose.bones[\"%s\"].rotation_quaternion" % bone, index, coeffs, variables)
        elif type == 'LOC':
            drv = writeDriver(fp, cond, drvdata, "*theScale", "pose.bones[\"%s\"].location" % bone, index, coeffs, variables)
        elif type == 'SCALE':
            drv = writeDriver(fp, cond, drvdata, "", "pose.bones[\"%s\"].scale" % bone, index, coeffs, variables)
        else:
            log.message(drv)
            raise NameError("Unknown driver type %s", type)
        driverList.append(drv)
    return driverList


def useThisShape(name, proxy):
    if not proxy:
        return True
    if proxy.type == 'Proxymeshes':
        return True
    if name in proxy.shapekeys:
        return True
    if name[:-2] in proxy.shapekeys:
        return True
    return False

