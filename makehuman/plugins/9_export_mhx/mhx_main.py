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

MakeHuman to MHX (MakeHuman eXchange format) exporter. MHX files can be loaded into Blender
"""

MAJOR_VERSION = 1
MINOR_VERSION = 16

import module3d
import gui3d
import os
import time
import codecs
import numpy
import math
import log

#import cProfile

import mh2proxy
import exportutils
import posemode

from . import mhx_writer
from . import posebone
from . import mhx_materials
from . import mhx_mesh
from . import mhx_proxy
from . import mhx_armature
from . import mhx_pose


#-------------------------------------------------------------------------------
#   Export MHX file
#-------------------------------------------------------------------------------

def exportMhx(human, filepath, config):
    from .mhx_armature import setupArmature

    gui3d.app.progress(0, text="Exporting MHX")
    log.message("Exporting %s" % filepath.encode('utf-8'))
    time1 = time.clock()
    config.setHuman(human)
    config.setupTexFolder(filepath)
    config.setOffset(human)

    filename = os.path.basename(filepath)
    name = config.goodName(os.path.splitext(filename)[0])
    amt = setupArmature(name, human, config)
    fp = codecs.open(filepath, 'w', encoding='utf-8')
    fp.write(
        "# MakeHuman exported MHX\n" +
        "# www.makeinfo.human.org\n" +
        "MHX %d %d" % (MAJOR_VERSION, MINOR_VERSION))
    for key,value in amt.objectProps:
        fp.write(' %s:_%s' % (key.replace(" ","_"), value.replace('"','')))
    fp.write(
        " ;\n"  +
        "#if Blender24\n" +
        "  error 'This file can only be read with Blender 2.5' ;\n" +
        "#endif\n")

    if config.scale != 1.0:
        amt.rescale(config.scale)
    proxies = config.getProxies()
    writer = Writer(name, human, amt, config, proxies)
    writer.writeFile(fp)
    fp.close()
    log.message("%s exported" % filepath.encode('utf-8'))
    gui3d.app.progress(1.0)


class Writer(mhx_writer.Writer):

    def __init__(self, name, human, amt, config, proxies):
        mhx_writer.Writer.__init__(self)

        self.name = name
        self.type = "mhx_main"
        self.human = human
        self.armature = amt
        self.config = config
        self.proxies = proxies
        self.customTargetFiles = exportutils.custom.listCustomFiles(config)

        self.matWriter = mhx_materials.Writer().fromOtherWriter(self)
        self.meshWriter = mhx_mesh.Writer().fromOtherWriter(self)
        self.proxyWriter = mhx_proxy.Writer(self.matWriter, self.meshWriter).fromOtherWriter(self)
        self.poseWriter = mhx_pose.Writer().fromOtherWriter(self)


    def writeFile(self, fp):
        amt = self.armature
        config = self.config

        if not config.cage:
            fp.write(
                "#if toggle&T_Cage\n" +
                "  error 'This MHX file does not contain a cage. Unselect the Cage import option.' ;\n" +
                "#endif\n")

        fp.write("NoScale True ;\n")
        amt.writeGizmos(fp)

        gui3d.app.progress(0.1, text="Exporting armature")
        amt.writeArmature(fp, MINOR_VERSION, self)

        gui3d.app.progress(0.15, text="Exporting materials")
        fp.write("\nNoScale False ;\n\n")
        self.matWriter.writeMaterials(fp)

        if config.cage:
            self.proxyWriter.writeProxyType('Cage', 'T_Cage', 4, fp, 0.2, 0.25)

        gui3d.app.progress(0.25, text="Exporting main mesh")
        fp.write("#if toggle&T_Mesh\n")
        self.meshWriter.writeMesh(fp, self.human.getSeedMesh())
        fp.write("#endif\n")

        self.proxyWriter.writeProxyType('Proxymeshes', 'T_Proxy', 3, fp, 0.35, 0.4)
        self.proxyWriter.writeProxyType('Clothes', 'T_Clothes', 2, fp, 0.4, 0.55)
        for ptype in mh2proxy.SimpleProxyTypes:
            self.proxyWriter.writeProxyType(ptype, 'T_Clothes', 0, fp, 0.55, 0.6)

        self.poseWriter.writePose(fp)

        self.writeGroups(fp)
        amt.writeFinal(fp)


    def writeGroups(self, fp):
        amt = self.armature
        fp.write("""
    # ---------------- Groups -------------------------------- #

    """)
        fp.write(
            "PostProcess %sBody %s 0000003f 00080000 %s 0000c000 ;\n" % (amt.name, amt.name, amt.visibleLayers) +
            "Group %s\n"  % amt.name +
            "  Objects\n" +
            "    ob %s ;\n" % amt.name +
            "#if toggle&T_Mesh\n" +
            "    ob %sBody ;\n" % amt.name +
            "#endif\n")

        self.groupProxy('Cage', 'T_Cage', fp)
        self.groupProxy('Proxymeshes', 'T_Proxy', fp)
        self.groupProxy('Clothes', 'T_Clothes', fp)
        self.groupProxy('Hair', 'T_Clothes', fp)
        self.groupProxy('Eyes', 'T_Clothes', fp)
        self.groupProxy('Genitals', 'T_Clothes', fp)

        fp.write(
            "    ob CustomShapes ;\n" +
            "  end Objects\n" +
            "  layers Array 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1  ;\n" +
            "end Group\n")
        return


    def groupProxy(self, type, test, fp):
        amt = self.armature
        fp.write("#if toggle&%s\n" % test)
        for proxy in self.proxies.values():
            if proxy.type == type:
                name = amt.name + proxy.name
                fp.write("    ob %s ;\n" % name)
        fp.write("#endif\n")
        return

