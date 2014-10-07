#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makeinfo.human.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makeinfo.human.org/node/318)

**Coding Standards:**  See http://www.makeinfo.human.org/node/165

Abstract
--------

Proxies
"""

import os
import log
from core import G

from . import mhx_writer
#from . import mhx_mesh
#from . import mhx_material

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

class Writer(mhx_writer.Writer):

    def __init__(self, matWriter, meshWriter):
        mhx_writer.Writer.__init__(self)
        self.type = "mhx_proxy"
        self.matWriter = matWriter
        self.meshWriter = meshWriter


    def writeProxyType(self, type, test, layer, fp, t0, t1):
        n = 0
        for proxy in self.proxies.values():
            if proxy.type == type:
                n += 1
        if n == 0:
            return

        dt = (t1-t0)/n
        t = t0
        for proxy in self.proxies.values():
            if proxy.type == type:
                G.app.progress(t, ["Exporting"," %s"], proxy.name)
                self.writeProxy(fp, proxy, layer)
                t += dt


    #-------------------------------------------------------------------------------
    #
    #-------------------------------------------------------------------------------

    def writeProxy(self, fp, pxy, layer):
        fp.write("NoScale False ;\n")

        obj = pxy.getSeedMesh()
        mat = obj.material
        if pxy.type != 'Proxymeshes':
            self.writeProxyMaterial(fp, mat, pxy)

        pxyname = self.meshName(pxy)
        coords = self.config.scale * pxy.getCoords() + self.config.offset

        fp.write(
            "Mesh %s %s \n" % (pxyname, pxyname) +
            "  Verts\n" +
            "".join( ["  v %.4f %.4f %.4f ;\n" % (x,-z,y) for x,y,z in coords] ) +
            "  end Verts\n")

        fp.write(
            "  Faces\n" +
            "".join( ["    f %d %d %d %d ;\n" % tuple(fv) for fv in obj.fvert] ) +
            "    ftall 0 1 ;\n" +
            "  end Faces\n")

        # UVs

        fp.write(
            "  MeshTextureFaceLayer %s\n" % "Texture" +
            "    Data \n")
        uvs = obj.texco
        for fuv in obj.fuvs:
            fp.write("    vt" + "".join( [" %.4g %.4g" % tuple(uvs[vt]) for vt in fuv] ) + " ;\n")
        fp.write(
            "    end Data\n" +
            "  end MeshTextureFaceLayer\n")

        # Proxy vertex groups

        self.meshWriter.writeVertexGroups(fp, pxy)

        if pxy.type == 'Proxymeshes':
            fp.write("  Material %s ;\n" % self.materialName("Skin"))
        elif pxy.material:
            fp.write("  Material %s ;\n" % self.materialName(mat.name, pxy))

        # Proxy object

        fp.write(
            "end Mesh\n\n" +
            "Object %s MESH %s \n" % (pxyname, pxyname) +
            "  parent Refer Object %s ;\n" % self.name +
            "  hide False ;\n" +
            "  hide_render False ;\n")

        # Proxy layers

        fp.write("layers Array ")
        for n in range(20):
            if n == layer:
                fp.write("1 ")
            else:
                fp.write("0 ")
        fp.write(";\n\n")

        self.meshWriter.writeArmatureModifier(fp, pxy)

        fp.write(
"""
      parent_type 'OBJECT' ;
      color Array 1.0 1.0 1.0 1.0  ;
      show_name True ;
      select True ;
      lock_location Array 1 1 1 ;
      lock_rotation Array 1 1 1 ;
      lock_scale Array 1 1 1  ;
      Property MhxProxy True ;
""")
        fp.write(
            '      Property MhxScale theScale*%.4f ;\n' % self.config.scale +
            '      Property MhxProxyName "%s" ;\n' % pxy.name.replace(" ","_") +
            '      Property MhxProxyUuid "%s" ;\n' % pxy.uuid +
            '      Property MhxProxyFile "%s" ;\n' % pxy.file.replace("\\", "/").replace(" ","%20") +
            '      Property MhxProxyType "%s" ;\n' % pxy.type +
            '    end Object')

    #-------------------------------------------------------------------------------
    #
    #-------------------------------------------------------------------------------

    def writeProxyMaterial(self, fp, mat, pxy):
        if mat.diffuseTexture:
            alpha = 0
        else:
            alpha = 1

        texnames = self.matWriter.writeTextures(fp, mat, pxy)

        # Write materials

        fp.write("Material %s \n" % self.materialName(mat.name, pxy))
        self.matWriter.writeMTexes(fp, texnames, mat)
        self.matWriter.writeMaterialSettings(fp, mat, alpha)

        fp.write(
            "  Property MhxDriven True ;\n" +
            "end Material\n\n")
