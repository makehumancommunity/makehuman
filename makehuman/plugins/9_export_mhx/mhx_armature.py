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

MHX armature
"""

import math
import numpy as np
import transformations as tm
from collections import OrderedDict
import exportutils
import log

from armature.armature import Armature
from armature.flags import *

from . import posebone
from . import mhx_drivers

#-------------------------------------------------------------------------------
#   Setup Armature
#-------------------------------------------------------------------------------

def setupArmature(name, human, config):
    from armature.parser import Parser
    from . import mhx_rigify

    options = config.rigOptions
    if options is None:
        return None
    else:
        log.message("Setup MHX rig %s" % name)
        if isinstance(options, mhx_rigify.RigifyOptions):
            amt = mhx_rigify.RigifyArmature(name, options, config)
            amt.parser = mhx_rigify.RigifyParser(amt, human)
        else:
            amt = ExportArmature(name, options, config)
            amt.parser = Parser(amt, human)
        amt.setup()
        log.message("Using rig with options %s" % options)
        return amt

#-------------------------------------------------------------------------------
#   Armature used for mhx export
#-------------------------------------------------------------------------------

class ExportArmature(Armature):

    def __init__(self, name, options, config):
        Armature.__init__(self, name, options)
        self.scale = options.scale
        self.config = config

        layers = L_MAIN|L_UPSPNFK|L_LARMFK|L_RARMFK|L_LLEGFK|L_RLEGFK|L_HEAD
        if options.useFingers:
            layers |= L_LHANDIK|L_RHANDIK
        else:
            layers |= L_LHANDFK|L_RHANDFK|L_LPALM|L_RPALM|L_TWEAK
        if options.useFaceRig:
            layers |= L_PANEL
        self.visibleLayers = "%08x" % layers

        self.activeBoneLayers = layers
        if options.useIkArms:
            self.activeBoneLayers |= L_LARMIK|L_RARMIK
        if options.useIkLegs:
            self.activeBoneLayers |= L_LLEGIK|L_RLEGIK

        self.objectProps += [("MhxRig", '"%s"' % options.rigtype.replace(" ","_"))]
        self.customProps = []
        self.bbones = {}
        self.boneGroups = []
        self.poseInfo = {}


    def setup(self):
        Armature.setup(self)

        if self.options.clothesRig:
            for proxy in self.proxies.values():
                if proxy.rig:
                    coord = proxy.getCoords()
                    self.fromRigFile(proxy.rig, env.human.meshData, coord=coord)
                    proxy.weights = self.prefixWeights(weights, proxy.name)
                    #appendRigBones(boneList, proxy.name, L_CLO, body, amt)


    def writeGizmos(self, fp):
        if not self.parser.gizmos:
            return

        fp.write(
            "Object CustomShapes EMPTY None\n" +
            "  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;\n" +
            "end Object\n\n")

        for name,gizmo in self.parser.gizmos.items():
            fp.write(
                '# ----------------------------- MESH --------------------- # \n\n' +
                'Mesh %s %s \n' % (name,name) +
                '  Verts\n')
            for v in gizmo["verts"]:
                fp.write('    v %.3f %.3f %.3f ;\n' % tuple(v))
            fp.write(
                '  end Verts\n' +
                '  Edges\n')
            for e in gizmo["edges"]:
                fp.write('    e %d %d ;\n' % tuple(e))
            fp.write(
                '  end Edges\n' +
                'end Mesh\n\n' +
                'Object %s MESH %s\n' % (name, name) +
                '  layers Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1  ;\n')

            if gizmo["subsurf"]:
                fp.write(
"""
    Modifier Subsurf SUBSURF
      levels 1 ;
      render_levels 2 ;
      subdivision_type 'CATMULL_CLARK' ;
      use_subsurf_uv True ;
    end Modifier
""")

            fp.write(
                '  parent Refer Object CustomShapes ;\n' +
                'end Object\n\n')


    def writeEditBones(self, fp):
        offs = self.config.scale * self.config.offset

        for bone in self.bones.values():
            fp.write("\n  Bone %s %s\n" % (bone.name, True))
            (x, y, z) = bone.head - offs
            fp.write("    head  %.6g %.6g %.6g  ;\n" % (x,-z,y))
            (x, y, z) = bone.tail - offs
            fp.write("    tail %.6g %.6g %.6g  ;\n" % (x,-z,y))

            if bone.parent:
                fp.write("    parent Refer Bone %s ; \n" % (bone.parent))
                parent = self.bones[bone.parent]
                vec = parent.tail - bone.head
                dist = math.sqrt(np.dot(vec,vec))
                conn = (bone.conn and dist < 1e-5)
                fp.write("    use_connect %s ; \n" % conn)
            else:
                fp.write("    use_connect False ; \n")

            fp.write(
                "    roll %.6g ; \n" % (bone.roll) +
                "    use_deform %s ; \n" % (bone.deform) +
                "    show_wire %s ; \n" % (bone.wire))

            if bone.hide:
                fp.write("    hide True ; \n")

            if 0 and bone.bbone:
                (bin, bout, bseg) = bone.bbone
                fp.write(
                    "    bbone_in %d ; \n" % (bin) +
                    "    bbone_out %d ; \n" % (bout) +
                    "    bbone_segments %d ; \n" % (bseg))

            if bone.norot:
                fp.write("    use_inherit_rotation False ; \n")
            if bone.scale:
                fp.write("    use_inherit_scale True ; \n")
            else:
                fp.write("    use_inherit_scale False ; \n")
            fp.write("    layers Array ")

            bit = 1
            for n in range(32):
                if bone.layers & bit:
                    fp.write("1 ")
                else:
                    fp.write("0 ")
                bit = bit << 1

            fp.write(" ; \n" +
                "    use_local_location %s ; \n" % bone.lloc +
                "    lock %s ; \n" % bone.lock +
                "    use_envelope_multiply False ; \n"+
                "    hide_select %s ; \n" % (bone.restr) +
                "  end Bone \n")


    BoneGroups = [
        ('Spine', 'THEME01', L_UPSPNFK),
        ('ArmFK.L', 'THEME02', L_LARMFK),
        ('ArmFK.R', 'THEME03', L_RARMFK),
        ('ArmIK.L', 'THEME04', L_LARMIK),
        ('ArmIK.R', 'THEME05', L_RARMIK),
        ('LegFK.L', 'THEME06', L_LLEGFK),
        ('LegFK.R', 'THEME07', L_RLEGFK),
        ('LegIK.L', 'THEME14', L_LLEGIK),
        ('LegIK.R', 'THEME09', L_RLEGIK),
    ]

    def getBoneGroup(self, bone):
        for bgroup,_,layer in self.BoneGroups:
            if bone.layers & layer & self.activeBoneLayers:
                return bgroup
        return None

    def writeBoneGroups(self, fp):
        if not fp:
            return
        for (name, theme, layer) in self.BoneGroups:
            if layer & self.activeBoneLayers:
                fp.write(
                    "    BoneGroup %s\n" % name +
                    "      name '%s' ;\n" % name +
                    "      color_set '%s' ;\n" % theme +
                    "    end BoneGroup\n")
        return


    def writeControlPoses(self, fp, options):
        self.writeBoneGroups(fp)

        for bone in self.bones.values():
            bgroup = self.getBoneGroup(bone)
            posebone.writePoseBone(
                fp, self, bone.name,
                bone.customShape, bgroup,
                bone.lockLocation, bone.lockRotation, bone.lockScale,
                bone.ikDof, bone.poseFlags, bone.constraints)


    def writeDrivers(self, fp):
        parser = self.parser
        if (parser.lrPropDrivers or
            parser.propDrivers or
            parser.boneDrivers):
            fp.write("AnimationData %s True\n" % self.name)
            mhx_drivers.writePropDrivers(fp, self, parser.lrPropDrivers, "L", "Mha")
            mhx_drivers.writePropDrivers(fp, self, parser.lrPropDrivers, "R", "Mha")
            mhx_drivers.writePropDrivers(fp, self, parser.propDrivers, "", "Mha")
            mhx_drivers.writeScriptedBoneDrivers(fp, self, parser.boneDrivers)

            fp.write(
"""
  action_blend_type 'REPLACE' ;
  action_extrapolation 'HOLD' ;
  action_influence 1 ;
  use_nla True ;
end AnimationData
""")


    def writeActions(self, fp):
        #rig_arm.WriteActions(fp)
        #rig_leg.WriteActions(fp)
        #rig_finger.WriteActions(fp)
        return


    def writeProperties(self, fp, env):
        for (key, val) in self.objectProps:
            fp.write("  Property %s %s ;\n" % (key, val))

        if not self.config.useAdvancedMHX:
            return

        '''
        fp.write("#if toggle&T_ShapeDrivers\n")
        self.writeHideProp(fp, self.name)
        for proxy in env.proxies.values():
            self.writeHideProp(fp, proxy.name)

        for path,name in env.customTargetFiles:
            self.defProp(fp, "FLOAT", "Mhc"+name, 0, name, -1.0, 2.0)

        for (key, val, string, min, max) in self.customProps:
            self.defProp(fp, "FLOAT", key, val, string, min, max)

        if self.options.useExpressions:
            fp.write("#if toggle&T_Shapekeys\n")
            for skey in exportutils.shapekeys.getExpressionUnits():
                self.defProp(fp, "FLOAT", "Mhs%s"%skey, 0.0, skey, -1.0, 2.0)
                #fp.write("  DefProp Float Mhs%s 0.0 %s min=-1.0,max=2.0 ;\n" % (skey, skey))
            fp.write("#endif\n")
        fp.write("#endif\n")
        '''

        if self.options.useIkArms:
            fp.write(
"""
  Property MhaArmIk_L 0.0 Left_arm_FK/IK ;
  PropKeys MhaArmIk_L "min":0.0,"max":1.0, ;

  Property MhaArmIk_R 0.0 Right_arm_FK/IK ;
  PropKeys MhaArmIk_R "min":0.0,"max":1.0, ;

""")

        if self.options.useSockets:
            fp.write(
"""
  Property MhaArmHinge_L False Left_arm_hinge ;
  PropKeys MhaArmHinge_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaLegHinge_L False Left_leg_hinge ;
  PropKeys MhaLegHinge_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaArmHinge_R False Right_arm_hinge ;
  PropKeys MhaArmHinge_R "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaLegHinge_R False Right_leg_hinge ;
  PropKeys MhaLegHinge_R "type":'BOOLEAN',"min":0,"max":1, ;
""")

        if self.options.useElbows:
            fp.write(
"""
  Property MhaElbowPlant_L False Left_elbow_plant ;
  PropKeys MhaElbowPlant_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaElbowPlant_R False Right_elbow_plant ;
  PropKeys MhaElbowPlant_R "type":'BOOLEAN',"min":0,"max":1, ;

""")

        if self.options.useIkLegs:
            fp.write(
"""
  Property MhaLegIk_L 0.0 Left_leg_FK/IK ;
  PropKeys MhaLegIk_L "min":0.0,"max":1.0, ;

  Property MhaLegIkToAnkle_L False Left_leg_IK_to_ankle ;
  PropKeys MhaLegIkToAnkle_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaLegIk_R 0.0 Right_leg_FK/IK ;
  PropKeys MhaLegIk_R "min":0.0,"max":1.0, ;

  Property MhaLegIkToAnkle_R False Right_leg_IK_to_ankle ;
  PropKeys MhaLegIkToAnkle_R "type":'BOOLEAN',"min":0,"max":1, ;

""")

        if self.options.useFingers:
            fp.write(
"""
  Property MhaFingerControl_L True Left_fingers_controlled ;
  PropKeys MhaFingerControl_L "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaFingerControl_R True Right_fingers_controlled ;
  PropKeys MhaFingerControl_R "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaGazeFollowsHead 1.0 Gaze_follows_world_or_head ;
  PropKeys MhaGazeFollowsHead "type":'BOOLEAN',"min":0.0,"max":1.0, ;

""")

        if self.options.useStretchyBones:
            fp.write(
"""
  Property MhaArmStretch_L 0.1 Left_arm_stretch_amount ;
  PropKeys MhaArmStretch_L "min":0.0,"max":1.0, ;

  Property MhaLegStretch_L 0.1 Left_leg_stretch_amount ;
  PropKeys MhaLegStretch_L "min":0.0,"max":1.0, ;

  Property MhaArmStretch_R 0.1 Right_arm_stretch_amount ;
  PropKeys MhaArmStretch_R "min":0.0,"max":1.0, ;

  Property MhaLegStretch_R 0.1 Right_leg_stretch_amount ;
  PropKeys MhaLegStretch_R "min":0.0,"max":1.0, ;

""")

        fp.write(
"""
  Property MhaRotationLimits 0.8 Influence_of_rotation_limit_constraints ;
  PropKeys MhaRotationLimits "min":0.0,"max":1.0, ;
""")

        if self.options.advancedSpine:

            fp.write("""
  Property MhaSpineInvert False Spine_from_shoulders_to_pelvis ;
  PropKeys MhaSpineInvert "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaSpineIk False Spine_FK/IK ;
  PropKeys MhaSpineIk "type":'BOOLEAN',"min":0,"max":1, ;

  Property MhaSpineStretch 0.2 Spine_stretch_amount ;
  PropKeys MhaSpineStretch "min":0.0,"max":1.0, ;
""")


    def defProp(self, fp, type, key, val, string, min=0, max=1):
        #fp.write("  DefProp %s %s %s %s min=%s,max=%s ;\n" % (type, key, val, string, min, max))
        if type == "BOOLEAN":
            fp.write(
                '  Property %s %s %s ;\n' % (key, val, string) +
                '  PropKeys %s "type":\'%s\', "min":%d,"max":%d, ;\n' % (key, type, min, max))
        elif type == "FLOAT":
            fp.write(
                '  Property %s %.6f %s ;\n' % (key, val, string) +
                '  PropKeys %s "min":%.6f,"max":%.6f, ;\n' % (key, min, max))
        else:
            halt


    def writeArmature(self, fp, version, env):

        fp.write("""
# ----------------------------- ARMATURE --------------------- #

NoScale False ;
""")

        fp.write("Armature %s %s   Normal \n" % (self.name, self.name))
        self.writeEditBones(fp)

        fp.write("""
  show_axes False ;
  show_bone_custom_shapes True ;
  show_group_colors True ;
  show_names False ;
  draw_type 'STICK' ;
  layers Array 1 1 1 1 1 1 1 1  1 1 1 1 1 1 1 1  1 1 1 1 1 1 1 1  1 1 1 1 1 1 1 1  ;
  layers_protected Array 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0  ;
  pose_position 'POSE' ;
  use_mirror_x False ;

end Armature
""")

        fp.write(
            "Object %s ARMATURE %s\n"  % (self.name, self.name) +
            "  Property MhxVersion %d ;\n" % version)

        fp.write("""
  layers Array 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0  ;
  up_axis 'Z' ;
  show_x_ray True ;
  draw_type 'WIRE' ;
""" +
            "  Property MhxScale theScale*%.4f ;\n" % self.config.scale +
            "  Property _RNA_UI {} ;\n")

        self.writeProperties(fp, env)

        fp.write("""
end Object
""")


    def writeHideProp(self, fp, name):
        self.defProp(fp, "BOOLEAN", "Mhh%s"%name, False, "Control_%s_visibility"%name)
        #fp.write("  DefProp Bool Mhh%s False Control_%s_visibility ;\n" % (name, name))
        return


    def writeFinal(self, fp):
        return

