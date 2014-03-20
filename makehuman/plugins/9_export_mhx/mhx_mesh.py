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

Mesh
"""

import numpy
import os
import log
from . import mhx_writer
from . import mhx_drivers

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------

class Writer(mhx_writer.Writer):

    def __init__(self):
        mhx_writer.Writer.__init__(self)
        self.type == "mhx_mesh"


    def writeMesh(self, fp, mesh):
        config = self.config
        scale = config.scale

        meshname = self.meshName()
        amt = self.armature
        coords = config.scale * (mesh.coord - config.offset)

        fp.write(
            "\nMesh %s %s\n" % (meshname, meshname) +
            "  Verts\n" +
            "".join(["    v %.4f %.4f %.4f ;\n" % (x,-z,y) for (x,y,z) in coords] ) +
            "  end Verts\n")

        fp.write(
            "  Faces\n" +
            "".join(["    f %d %d %d %d ;\n" % tuple(fv) for fv in mesh.fvert] ))
        self.writeFaceNumbers(fp)
        fp.write("  end Faces\n")

        fp.write(
            "  MeshTextureFaceLayer UVTex\n" +
            "    Data\n")
        uvs = mesh.texco
        fuvs = mesh.fuvs
        for fuv in fuvs:
            fp.write( "      vt" + "".join([" %.4g %.4g" %(tuple(uvs[vt])) for vt in fuv]) + " ;\n")
        fp.write(
"""
    end Data
    active True ;
    active_clone True ;
    active_render True ;
  end MeshTextureFaceLayer
""")

        self.writeBaseMaterials(fp)
        self.writeVertexGroups(fp, None)

        weights = {}
        for proxy in self.proxies.values():
            if proxy.deleteVerts.any():
                weights["Delete_" + proxy.name] = proxy.deleteVerts
        self.writeBoolWeights(fp, weights)

        ox,oy,oz = config.scale*config.offset
        fp.write(
            "end Mesh\n\n"+
            "Object %s MESH %s\n"  % (meshname, meshname) +
            "  Property MhxOffsetX %.4f ;\n" % ox +
            "  Property MhxOffsetY %.4f ;\n" % oy +
            "  Property MhxOffsetZ %.4f ;\n" % oz +
            "  layers Array 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0  ;\n")

        self.writeArmatureModifier(fp, None)

        model = (
            "caucasian:%.4f_" % self.human.getCaucasian() +
            "asian:%.4f_" % self.human.getAsian() +
            "african:%.4f_" % self.human.getAfrican() +
            "gender:%.4f_" % self.human.getGender() +
            "age:%.4f_" % self.human.getAge() +
            "weight:%.4f_" % self.human.getWeight() +
            "muscle:%.4f_" % self.human.getMuscle() +
            "height:%.4f_" % self.human.getHeight() +
            "bodyProportions:%.4f_" % self.human.getBodyProportions()
        )

        fp.write(
            "  parent Refer Object %s ;" % self.name +
"""
  parent_type 'OBJECT' ;
  color Array 1.0 1.0 1.0 1.0  ;
  select True ;
  lock_location Array 1 1 1 ;
  lock_rotation Array 1 1 1 ;
  lock_scale Array 1 1 1  ;
  Property MhxMesh True ;
  Property MhHuman True ;
""" +
            "  Property MhxScale theScale*%.4f ;\n" % scale +
            "  Property MhxModel \"%s\" ;\n" % model)

        enable = True
        for proxy in self.proxies.values():
            if proxy.deleteVerts.any():
                fp.write(
                    "  Modifier Mask%s MASK\n" % proxy.name +
                    "    mode 'VERTEX_GROUP' ;\n" +
                    "    vertex_group 'Delete_%s' ;\n" % proxy.name +
                    "    invert_vertex_group True ;\n" +
                    "    show_viewport %s ;\n" % enable +
                    "    show_render %s ;\n" % enable +
                    "  end Modifier\n")

        fp.write(
"""
  Modifier SubSurf SUBSURF
    levels 0 ;
    render_levels 1 ;
  end Modifier
end Object
""")


    #-------------------------------------------------------------------------------
    #   Armature modifier.
    #-------------------------------------------------------------------------------

    def writeArmatureModifier(self, fp, proxy):
        amt = self.armature
        config = self.config

        if (config.cage and
            not (proxy and proxy.cage)):

            fp.write(
"""
  #if toggle&T_Cage
    Modifier MeshDeform MESH_DEFORM
      invert_vertex_group False ;
""" +
"  object Refer Object %sCageMesh ;" % self.name +
"""
      precision 6 ;
      use_dynamic_bind True ;
    end Modifier
    Modifier Armature ARMATURE
      invert_vertex_group False ;
""" +
"  object Refer Object %s ;" % self.name +
"""
      use_bone_envelopes False ;
      use_multi_modifier True ;
      use_vertex_groups True ;
      vertex_group 'Cage' ;
    end Modifier
  #else
    Modifier Armature ARMATURE
""" +
"  object Refer Object %s ;" % self.name +
"""
      use_bone_envelopes False ;
      use_vertex_groups True ;
    end Modifier
  #endif
""")

        else:

            fp.write(
"""
    Modifier Armature ARMATURE
""" +
"  object Refer Object %s ;" % self.name +
"""
      use_bone_envelopes False ;
      use_vertex_groups True ;
    end Modifier
""")

    #-------------------------------------------------------------------------------
    #   Face numbers
    #-------------------------------------------------------------------------------

    def writeFaceNumbers(self, fp):
        from exportutils.collect import deleteGroup

        obj = self.human.meshData
        fmats = numpy.zeros(len(obj.coord), int)

        # TODO use facemask set on module3d instead (cant we reuse filterMesh from collect module?)
        deleteVerts = None
        deleteGroups = []

        for fg in obj.faceGroups:
            fmask = obj.getFaceMaskForGroups([fg.name])
            if deleteGroup(fg.name, deleteGroups):
                fmats[fmask] = 3
            elif fg.name == "helper-tights":
                fmats[fmask] = 2
            elif fg.name in ["helper-hair", "joint-ground"]:
                fmats[fmask] = 5
            elif fg.name == "helper-skirt":
                fmats[fmask] = 4
            elif fg.name[0:6] == "joint-":
                fmats[fmask] = 1
            elif fg.name[0:7] == "helper-":
                fmats[fmask] = 3

        if deleteVerts != None:
            for fn,fverts in enumerate(obj.fvert):
                if deleteVerts[fverts[0]]:
                    fmats[fn] = 6

        mn = -1
        fn = 0
        f0 = 0
        for fverts in obj.fvert:
            if fmats[fn] != mn:
                if fn != f0:
                    fp.write("  ftn %d %d 1 ;\n" % (fn-f0, mn))
                mn = fmats[fn]
                f0 = fn
            fn += 1
        if fn != f0:
            fp.write("  ftn %d %d 1 ;\n" % (fn-f0, mn))

    #-------------------------------------------------------------------------------
    #   Material access
    #-------------------------------------------------------------------------------

    def writeBaseMaterials(self, fp):
        for matname in ["Skin", "Invisio", "Red", "Green", "Blue", "Yellow"]:
            fp.write("  Material %s ;\n" % self.materialName(matname))

#-------------------------------------------------------------------------------
#   Vertex groups
#-------------------------------------------------------------------------------

    def writeVertexGroups(self, fp, proxy):
        amt = self.armature

        if proxy and proxy.weights:
            self.writeRigWeights(fp, proxy.weights)
            return
        if proxy:
            weights = proxy.getWeights(amt.vertexWeights, amt)
        else:
            weights = amt.vertexWeights
        self.writeRigWeights(fp, weights)


    def writeRigWeights(self, fp, weights):
        for grp in weights.keys():
            fp.write(
                "\n  VertexGroup %s\n" % grp +
                "".join( ["    wv %d %.4g ;\n" % tuple(vw) for vw in weights[grp]] ) +
                "  end VertexGroup\n")


    def writeBoolWeights(self, fp, weights):
        for grp in weights.keys():
            string = "".join( ["    wv %d 1 ;\n" % vn for vn,val in enumerate(weights[grp]) if val] )
            if string:
                fp.write(
                    "\n  VertexGroup %s\n" % grp +
                    string +
                    "  end VertexGroup\n")


