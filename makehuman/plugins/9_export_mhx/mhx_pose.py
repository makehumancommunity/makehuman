#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makeinfo.human.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makeinfo.human.org/node/318)

**Coding Standards:**  See http://www.makeinfo.human.org/node/165

Abstract
--------

Pose
"""

import log
import os
import mh
import mh2proxy
import algos3d
import exportutils

from . import mhx_writer
from . import mhx_drivers

from core import G

def callback(progress, text=""):
    """
    Progress indicator callback
    """
    G.app.progress(progress, text)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

class Writer(mhx_writer.Writer):

    def __init__(self):
        mhx_writer.Writer.__init__(self)
        self.type == "mhx_pose"


    def writePose(self, fp):
        amt = self.armature
        config = self.config
        targets = exportutils.collect.readTargets(self.human, config)

        fp.write("""
    # --------------- Shapekeys ----------------------------- #
    """)

        self.proxyShapes('Cage', 'T_Cage', fp, [])
        self.proxyShapes('Proxymeshes', 'T_Proxy', fp, targets)
        self.proxyShapes('Clothes', 'T_Clothes', fp, [])
        for ptype in mh2proxy.SimpleProxyTypes:
            self.proxyShapes(ptype, 'T_Clothes', fp, [])

        fp.write("#if toggle&T_Mesh\n")
        self.writeShapeKeysAndDrivers(fp, "%sBody" % self.name, None, targets)

        fp.write("""
    #endif

    # --------------- Actions ----------------------------- #

    #if toggle&T_Armature
    """)

        fp.write(
            "Pose %s\n" % self.name +
            "end Pose\n")
        #amt.writeAllActions(fp)

        fp.write("Pose %s\n" % self.name)
        amt.writeControlPoses(fp, config)
        fp.write("  ik_solver 'LEGACY' ;\nend Pose\n")
        amt.writeDrivers(fp)
        fp.write("CorrectRig %s ;\n" % self.name)
        fp.write("""
    #endif
    """)


    # *** material-drivers

    #-------------------------------------------------------------------------------
    #
    #-------------------------------------------------------------------------------

    def proxyShapes(self, type, test, fp, targets):
        fp.write("#if toggle&%s\n" % test)
        for proxy in self.proxies.values():
            if proxy.name and proxy.type == type:
                self.writeShapeKeysAndDrivers(fp, self.name+proxy.name, proxy, targets)
        fp.write("#endif\n")


    def writeShape1(self, fp, sname, lr, trg, min, max, proxy, scale):
        if len(trg.verts) == 0:
            return
        fp.write(
            "ShapeKey %s %s True\n" % (sname, lr) +
            "  slider_min %.3g ;\n" % min +
            "  slider_max %.3g ;\n" % max)
        data = scale*trg.data
        fp.write("".join( ["  sv %d %.4f %.4f %.4f ;\n" %  (trg.verts[n], dr[0], -dr[2], dr[1]) for n,dr in enumerate(data)] ))
        fp.write("end ShapeKey\n")


    def writeShape(self, fp, sname, lr, trg, min, max, proxy, scale):
        if proxy:
            ptargets = proxy.getShapes([("shape",trg)], 1.0)
            if len(ptargets) > 0:
                name,trg = ptargets[0]
                self.writeShape1(fp, sname, lr, trg, min, max, proxy, scale)
        else:
            self.writeShape1(fp, sname, lr, trg, min, max, proxy, scale)


    def writeShapeKeysAndDrivers(self, fp, name, proxy, targets):
        config = self.config
        ptargets = []
        if proxy:
            obj = proxy.getSeedMesh()
            for filepath in proxy.shapekeys:
                shape = exportutils.shapekeys.getShape(filepath, obj)
                fname = os.path.splitext(os.path.basename(filepath))[0]
                ptargets.append((proxy.name+fname, shape))

        if not targets and not ptargets:
            return

        fp.write(
            "#if toggle&T_Shapekeys\n" +
            "ShapeKeys %s\n" % name +
            "  ShapeKey Basis Sym True\n" +
            "  end ShapeKey\n")

        for (sname, shape) in targets:
            self.writeShape(fp, sname, "Sym", shape, 0, 1, proxy, config.scale)

        for (sname, shape) in ptargets:
            self.writeShape(fp, sname, "Sym", shape, 0, 1, None, config.scale)

        '''
        fp.write("#if toggle&T_ShapeDrivers\n")

        if config.expressions and not proxy:
            exprList = exportutils.shapekeys.readExpressionMhm(mh.getSysDataPath("expressions"))
            self.writeExpressions(fp, exprList, "Expression")
            visemeList = exportutils.shapekeys.readExpressionMhm(mh.getSysDataPath("visemes"))
            self.writeExpressions(fp, visemeList, "Viseme")

        if config.useAdvancedMHX:
            fp.write("  AnimationData None (toggle&T_Symm==0)\n")
            self.writeShapeKeyDrivers(fp, name, proxy)
            fp.write("  end AnimationData\n\n")

        fp.write("#endif\n")
        '''

        fp.write(
            "  end ShapeKeys\n" +
            "#endif\n")


    def writeShapeKeyDrivers(self, fp, name, proxy):
        isHuman = ((not proxy) or proxy.type == 'Proxymeshes')
        amt = self.armature

        if isHuman:
            for path,name in self.customTargetFiles:
                mhx_drivers.writeShapePropDrivers(fp, amt, [name], proxy, "Mhc", callback)

            if self.config.expressions:
                mhx_drivers.writeShapePropDrivers(fp, amt, exportutils.shapekeys.getExpressionUnits(), proxy, "Mhs", callback)

            skeys = []
            for (skey, val, string, min, max) in  self.customProps:
                skeys.append(skey)
            mhx_drivers.writeShapePropDrivers(fp, amt, skeys, proxy, "Mha", callback)


    def writeExpressions(self, fp, exprList, label):
        for (name, units) in exprList:
            fp.write("  %s %s\n" % (label, name))
            for (unit, value) in units:
                fp.write("    %s %s ;\n" % (unit, value))
            fp.write("  end\n")

