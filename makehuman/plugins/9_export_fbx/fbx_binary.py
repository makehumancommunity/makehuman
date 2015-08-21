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
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Script copyright (C) Campbell Barton, Bastien Montagne
# Modified by Jonas Hauquier for python 2.7 compat and MakeHuman FBX export


import array
import datetime
import log

from fbx_utils import *

# Units convertors!
convert_sec_to_ktime = units_convertor("second", "ktime")
convert_sec_to_ktime_iter = units_convertor_iter("second", "ktime")

convert_mm_to_inch = units_convertor("millimeter", "inch")

convert_rad_to_deg = units_convertor("radian", "degree")
convert_rad_to_deg_iter = units_convertor_iter("radian", "degree")


# ##### Templates #####
# TODO: check all those "default" values, they should match Blender's default as much as possible, I guess?

def fbx_template_def_globalsettings(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict()
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"GlobalSettings", b"", props, nbr_users, [False])

def fbx_template_def_null(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict((
        (b"Color", ((0.8, 0.8, 0.8), "p_color_rgb", False)),
        (b"Size", (100.0, "p_double", False)),
        (b"Look", (1, "p_enum", False)),  # Cross (0 is None, i.e. invisible?).
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"NodeAttribute", b"FbxNull", props, nbr_users, [False])


def fbx_template_def_bone(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict()
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"NodeAttribute", b"LimbNode", props, nbr_users, [False])


def fbx_template_def_geometry(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict((
        (b"Color", ((0.8, 0.8, 0.8), "p_color_rgb", False)),
        (b"BBoxMin", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"BBoxMax", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"Primary Visibility", (True, "p_bool", False)),
        (b"Casts Shadows", (True, "p_bool", False)),
        (b"Receive Shadows", (True, "p_bool", False)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"Geometry", b"FbxMesh", props, nbr_users, [False])


def fbx_template_def_material(scene, settings, override_defaults=None, nbr_users=0):
    # WIP...
    props = OrderedDict((
        (b"ShadingModel", ("Phong", "p_string", False)),
        (b"MultiLayer", (False, "p_bool", False)),
        # Lambert-specific.
        (b"EmissiveColor", ((0.0, 0.0, 0.0), "p_color", True)),
        (b"EmissiveFactor", (1.0, "p_number", True)),
        (b"AmbientColor", ((0.2, 0.2, 0.2), "p_color", True)),
        (b"AmbientFactor", (1.0, "p_number", True)),
        (b"DiffuseColor", ((0.8, 0.8, 0.8), "p_color", True)),
        (b"DiffuseFactor", (1.0, "p_number", True)),
        (b"TransparentColor", ((0.0, 0.0, 0.0), "p_color", True)),
        (b"TransparencyFactor", (0.0, "p_number", True)),
        (b"Opacity", (1.0, "p_number", True)),
        (b"NormalMap", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"Bump", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"BumpFactor", (1.0, "p_double", False)),
        (b"DisplacementColor", ((0.0, 0.0, 0.0), "p_color_rgb", False)),
        (b"DisplacementFactor", (1.0, "p_double", False)),
        (b"VectorDisplacementColor", ((0.0, 0.0, 0.0), "p_color_rgb", False)),
        (b"VectorDisplacementFactor", (1.0, "p_double", False)),
        # Phong-specific.
        (b"SpecularColor", ((0.2, 0.2, 0.2), "p_color", True)),
        (b"SpecularFactor", (1.0, "p_number", True)),
        # Not sure about the name, importer uses this (but ShininessExponent for tex prop name!)
        # And in fbx exported by sdk, you have one in template, the other in actual material!!! :/
        # For now, using both.
        (b"Shininess", (20.0, "p_number", True)),
        (b"ShininessExponent", (20.0, "p_number", True)),
        (b"ReflectionColor", ((0.0, 0.0, 0.0), "p_color", True)),
        (b"ReflectionFactor", (1.0, "p_number", True)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"Material", b"FbxSurfacePhong", props, nbr_users, [False])


def fbx_template_def_texture_file(scene, settings, override_defaults=None, nbr_users=0):
    # WIP...
    # XXX Not sure about all names!
    props = OrderedDict((
        (b"TextureTypeUse", (0, "p_enum", False)),  # Standard.
        (b"AlphaSource", (2, "p_enum", False)),  # Black (i.e. texture's alpha), XXX name guessed!.
        (b"Texture alpha", (1.0, "p_double", False)),
        (b"PremultiplyAlpha", (True, "p_bool", False)),
        (b"CurrentTextureBlendMode", (1, "p_enum", False)),  # Additive...
        (b"CurrentMappingType", (0, "p_enum", False)),  # UV.
        (b"UVSet", ("default", "p_string", False)),  # UVMap name.
        (b"WrapModeU", (0, "p_enum", False)),  # Repeat.
        (b"WrapModeV", (0, "p_enum", False)),  # Repeat.
        (b"UVSwap", (False, "p_bool", False)),
        (b"Translation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"Rotation", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"Scaling", ((1.0, 1.0, 1.0), "p_vector_3d", False)),
        (b"TextureRotationPivot", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        (b"TextureScalingPivot", ((0.0, 0.0, 0.0), "p_vector_3d", False)),
        # Not sure about those two...
        (b"UseMaterial", (False, "p_bool", False)),
        (b"UseMipMap", (False, "p_bool", False)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"Texture", b"FbxFileTexture", props, nbr_users, [False])


def fbx_template_def_pose(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict()
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"Pose", b"", props, nbr_users, [False])


def fbx_template_def_deformer(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict()
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"Deformer", b"", props, nbr_users, [False])


def fbx_template_def_animstack(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict((
        (b"Description", ("", "p_string", False)),
        (b"LocalStart", (0, "p_timestamp", False)),
        (b"LocalStop", (0, "p_timestamp", False)),
        (b"ReferenceStart", (0, "p_timestamp", False)),
        (b"ReferenceStop", (0, "p_timestamp", False)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"AnimationStack", b"FbxAnimStack", props, nbr_users, [False])


def fbx_template_def_animlayer(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict((
        (b"Weight", (100.0, "p_number", True)),
        (b"Mute", (False, "p_bool", False)),
        (b"Solo", (False, "p_bool", False)),
        (b"Lock", (False, "p_bool", False)),
        (b"Color", ((0.8, 0.8, 0.8), "p_color_rgb", False)),
        (b"BlendMode", (0, "p_enum", False)),
        (b"RotationAccumulationMode", (0, "p_enum", False)),
        (b"ScaleAccumulationMode", (0, "p_enum", False)),
        (b"BlendModeBypass", (0, "p_ulonglong", False)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"AnimationLayer", b"FbxAnimLayer", props, nbr_users, [False])


def fbx_template_def_animcurvenode(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict((
        (FBX_ANIM_PROPSGROUP_NAME.encode(), (None, "p_compound", False)),
    ))
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"AnimationCurveNode", b"FbxAnimCurveNode", props, nbr_users, [False])


def fbx_template_def_animcurve(scene, settings, override_defaults=None, nbr_users=0):
    props = OrderedDict()
    if override_defaults is not None:
        props.update(override_defaults)
    return FBXTemplate(b"AnimationCurve", b"", props, nbr_users, [False])


# ##### Generators for connection elements. #####

def elem_connection(elem, c_type, uid_src, uid_dst, prop_dst=None):
    e = elem_data_single_string(elem, b"C", c_type)
    e.add_int64(uid_src)
    e.add_int64(uid_dst)
    if prop_dst is not None:
        e.add_string(prop_dst)


# ##### FBX objects generators. #####

def fbx_data_element_custom_properties(props, bid):
    """
    Store custom properties of blender ID bid (any mapping-like object, in fact) into FBX properties props.
    """
    for k, v in bid.items():
        list_val = getattr(v, "to_list", lambda: None)()

        if isinstance(v, str):
            elem_props_set(props, "p_string", k.encode(), v, custom=True)
        elif isinstance(v, int):
            elem_props_set(props, "p_integer", k.encode(), v, custom=True)
        elif isinstance(v, float):
            elem_props_set(props, "p_double", k.encode(), v, custom=True)
        elif list_val and len(list_val) == 3:
            elem_props_set(props, "p_vector", k.encode(), list_val, custom=True)


def fbx_data_bindpose_element(objectsParent, key, id, count):
    """
    Helper, since bindpose are used by both meshes shape keys and armature bones...
    """
    # We assume bind pose for our bones are their "Editmode" pose...
    # All matrices are expected in global (world) space.
    fbx_pose = elem_data_single_int64(objectsParent, b"Pose", id)
    fbx_pose.add_string(fbx_name_class(key.encode()))
    fbx_pose.add_string(b"BindPose")

    elem_data_single_string(fbx_pose, b"Type", b"BindPose")
    elem_data_single_int32(fbx_pose, b"Version", FBX_POSE_BIND_VERSION)
    elem_data_single_int32(fbx_pose, b"NbPoseNodes", count)

    return fbx_pose

def fbx_data_pose_node_element(bindposeParent, key, id, bindmat):
    fbx_posenode = elem_empty(bindposeParent, b"PoseNode")
    elem_data_single_int64(fbx_posenode, b"Node", id)
    elem_data_single_float64_array(fbx_posenode, b"Matrix", bindmat.ravel(order='C'))  # Use column-major order

def fbx_data_mesh_element(objectsParent, key, id, properties, coord, fvert, vnorm, texco, fuv):
    geom = elem_data_single_int64(objectsParent, b"Geometry", id)  #get_fbx_uuid_from_key(key))
    geom.add_string(fbx_name_class(key.encode()))
    geom.add_string(b"Mesh")

    name = key.split('::')[1]

    props = elem_properties(geom)

    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)
        #fbx_data_element_custom_properties(props, me)


    # Vertex cos.
    t_co = array.array(data_types.ARRAY_FLOAT64, coord.reshape(-1))
    elem_data_single_float64_array(geom, b"Vertices", t_co)
    del t_co

    # Polygon indices.
    # Bitwise negate last index to mark end of polygon loop
    fvert_ = fvert.copy()
    if fvert.shape[1] == 3:
        #fvert_[:,2] = -1 - fvert_[:,2]
        fvert_[:,2] = ~fvert_[:,2]
    else:
        fvert_[:,3] = ~fvert_[:,3]
    import numpy as np
    t_pvi = array.array(data_types.ARRAY_INT32, fvert_.astype(np.int32).reshape(-1))
    elem_data_single_int32_array(geom, b"PolygonVertexIndex", t_pvi)


    #elem_data_single_int32_array(geom, b"Edges", t_eli)
    del t_pvi

    elem_data_single_int32(geom, b"GeometryVersion", 124)

    # Layers

    # Normals
    t_ln = array.array(data_types.ARRAY_FLOAT64, vnorm.reshape(-1))

    lay_nor = elem_data_single_int32(geom, b"LayerElementNormal", 0)
    elem_data_single_int32(lay_nor, b"Version", FBX_GEOMETRY_NORMAL_VERSION)
    elem_data_single_string(lay_nor, b"Name", (name+"_Normal").encode())
    elem_data_single_string(lay_nor, b"MappingInformationType", b"ByPolygonVertex")
    elem_data_single_string(lay_nor, b"ReferenceInformationType", b"IndexToDirect")

    elem_data_single_float64_array(lay_nor, b"Normals", t_ln)

    elem_data_single_int32_array(lay_nor, b"NormalsIndex", fvert.reshape(-1))
    del t_ln

    # TODO export tangents
    '''
    # tspace
    tspacenumber = len(me.uv_layers)
    if tspacenumber:
        t_ln = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.loops) * 3
        # t_lnw = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.loops)
        for idx, uvlayer in enumerate(me.uv_layers):
            name = uvlayer.name
            me.calc_tangents(name)
            # Loop bitangents (aka binormals).
            # NOTE: this is not supported by importer currently.
            me.loops.foreach_get("bitangent", t_ln)
            lay_nor = elem_data_single_int32(geom, b"LayerElementBinormal", idx)
            elem_data_single_int32(lay_nor, b"Version", FBX_GEOMETRY_BINORMAL_VERSION)
            elem_data_single_string_unicode(lay_nor, b"Name", name)
            elem_data_single_string(lay_nor, b"MappingInformationType", b"ByPolygonVertex")
            elem_data_single_string(lay_nor, b"ReferenceInformationType", b"Direct")
            elem_data_single_float64_array(lay_nor, b"Binormals",
                                           chain(*nors_transformed_gen(t_ln, geom_mat_no)))
            # Binormal weights, no idea what it is.
            # elem_data_single_float64_array(lay_nor, b"BinormalsW", t_lnw)

            # Loop tangents.
            # NOTE: this is not supported by importer currently.
            me.loops.foreach_get("tangent", t_ln)
            lay_nor = elem_data_single_int32(geom, b"LayerElementTangent", idx)
            elem_data_single_int32(lay_nor, b"Version", FBX_GEOMETRY_TANGENT_VERSION)
            elem_data_single_string_unicode(lay_nor, b"Name", name)
            elem_data_single_string(lay_nor, b"MappingInformationType", b"ByPolygonVertex")
            elem_data_single_string(lay_nor, b"ReferenceInformationType", b"Direct")
            elem_data_single_float64_array(lay_nor, b"Tangents",
                                           chain(*nors_transformed_gen(t_ln, geom_mat_no)))
            # Tangent weights, no idea what it is.
            # elem_data_single_float64_array(lay_nor, b"TangentsW", t_lnw)

        # del t_lnw
    '''

    # TODO export vertex colors
    '''
    # VertexColor Layers.
    vcolnumber = len(me.vertex_colors)
    if vcolnumber:
        def _coltuples_gen(raw_cols):
            return zip(*(iter(raw_cols),) * 3 + (_infinite_gen(1.0),))  # We need a fake alpha...

        t_lc = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.loops) * 3
        for colindex, collayer in enumerate(me.vertex_colors):
            collayer.data.foreach_get("color", t_lc)
            lay_vcol = elem_data_single_int32(geom, b"LayerElementColor", colindex)
            elem_data_single_int32(lay_vcol, b"Version", FBX_GEOMETRY_VCOLOR_VERSION)
            elem_data_single_string_unicode(lay_vcol, b"Name", collayer.name)
            elem_data_single_string(lay_vcol, b"MappingInformationType", b"ByPolygonVertex")
            elem_data_single_string(lay_vcol, b"ReferenceInformationType", b"IndexToDirect")

            col2idx = tuple(set(_coltuples_gen(t_lc)))
            elem_data_single_float64_array(lay_vcol, b"Colors", chain(*col2idx))  # Flatten again...

            col2idx = {col: idx for idx, col in enumerate(col2idx)}
            elem_data_single_int32_array(lay_vcol, b"ColorIndex", (col2idx[c] for c in _coltuples_gen(t_lc)))
            del col2idx
        del t_lc
        del _coltuples_gen
    '''

    # UV layers.
    # Note: LayerElementTexture is deprecated since FBX 2011 - luckily!
    #       Textures are now only related to materials, in FBX!
    t_uv = array.array(data_types.ARRAY_FLOAT64, texco.reshape(-1))
    t_fuv = array.array(data_types.ARRAY_INT32, fuv.reshape(-1))
    uvindex = 0
    lay_uv = elem_data_single_int32(geom, b"LayerElementUV", uvindex)
    elem_data_single_int32(lay_uv, b"Version", FBX_GEOMETRY_UV_VERSION)
    elem_data_single_string_unicode(lay_uv, b"Name", (name+"_UV").encode())
    elem_data_single_string(lay_uv, b"MappingInformationType", b"ByPolygonVertex")
    elem_data_single_string(lay_uv, b"ReferenceInformationType", b"IndexToDirect")

    # TODO verify whether this crashes FBX converter as well (and needs a hack like fbx_mesh.writeUvs2)
    elem_data_single_float64_array(lay_uv, b"UV", t_uv)
    elem_data_single_int32_array(lay_uv, b"UVIndex", t_fuv)

    del t_fuv
    del t_uv

    # Face's materials.
    lay_mat = elem_data_single_int32(geom, b"LayerElementMaterial", 0)
    elem_data_single_int32(lay_mat, b"Version", FBX_GEOMETRY_MATERIAL_VERSION)
    elem_data_single_string(lay_mat, b"Name", (name+"_Material").encode())

    elem_data_single_string(lay_mat, b"MappingInformationType", b"AllSame")
    elem_data_single_string(lay_mat, b"ReferenceInformationType", b"IndexToDirect")
    elem_data_single_int32_array(lay_mat, b"Materials", [0])

    # Face's textures -perhaps obsolete.
    lay_tex = elem_data_single_int32(geom, b"LayerElementTexture", 0)
    elem_data_single_int32(lay_tex, b"Version", 101)
    elem_data_single_string(lay_tex, b"Name", (name+"_Texture").encode())

    elem_data_single_string(lay_tex, b"MappingInformationType", b"ByPolygonVertex")
    elem_data_single_string(lay_tex, b"ReferenceInformationType", b"IndexToDirect")
    elem_data_single_string(lay_tex, b"BlendMode", b"Translucent")

    # Layer TOC
    layer = elem_data_single_int32(geom, b"Layer", 0)
    elem_data_single_int32(layer, b"Version", FBX_GEOMETRY_LAYER_VERSION)

    lay_nor = elem_empty(layer, b"LayerElement")
    elem_data_single_string(lay_nor, b"Type", b"LayerElementNormal")
    elem_data_single_int32(lay_nor, b"TypedIndex", 0)

    # TODO tangents
    '''
    lay_binor = elem_empty(layer, b"LayerElement")
    elem_data_single_string(lay_binor, b"Type", b"LayerElementBinormal")
    elem_data_single_int32(lay_binor, b"TypedIndex", 0)
    lay_tan = elem_empty(layer, b"LayerElement")
    elem_data_single_string(lay_tan, b"Type", b"LayerElementTangent")
    elem_data_single_int32(lay_tan, b"TypedIndex", 0)
    '''

    # TODO vertex colors
    '''
    if vcolnumber:
        lay_vcol = elem_empty(layer, b"LayerElement")
        elem_data_single_string(lay_vcol, b"Type", b"LayerElementColor")
        elem_data_single_int32(lay_vcol, b"TypedIndex", 0)
    '''

    lay_uv = elem_empty(layer, b"LayerElement")
    elem_data_single_string(lay_uv, b"Type", b"LayerElementUV")
    elem_data_single_int32(lay_uv, b"TypedIndex", 0)

    lay_mat = elem_empty(layer, b"LayerElement")
    elem_data_single_string(lay_mat, b"Type", b"LayerElementMaterial")
    elem_data_single_int32(lay_mat, b"TypedIndex", 0)

    lay_tex = elem_empty(layer, b"LayerElement")
    elem_data_single_string(lay_tex, b"Type", b"LayerElementTexture")
    elem_data_single_int32(lay_tex, b"TypedIndex", 0)

    # Shape keys
    #fbx_data_mesh_shapes_elements(root, me_obj, me, scene_data, tmpl, props)


def fbx_data_model_element(objectsParent, key, id, properties):
    mod = elem_data_single_int64(objectsParent, b"Model", id)
    mod.add_string(fbx_name_class(key.encode()))
    mod.add_string(b"Mesh")

    elem_data_single_int32(mod, b"Version", FBX_MODELS_VERSION)

    props = elem_properties(mod)
    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)

    elem_data_single_string(mod, b"Shading", "Y")
    elem_data_single_string(mod, b"Culling", "CullingOff")


def fbx_data_material(objectsParent, key, id, properties):
    fbx_mat = elem_data_single_int64(objectsParent, b"Material", id)
    fbx_mat.add_string(fbx_name_class(key))
    fbx_mat.add_string(b"")

    elem_data_single_int32(fbx_mat, b"Version", 102)
    elem_data_single_string(fbx_mat, b"ShadingModel", "phong")
    elem_data_single_int32(fbx_mat, b"MultiLayer", 0)

    props = elem_properties(fbx_mat)
    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)


def fbx_data_texture_file_element(objectsParent, key, id, video_key, video_id, texpath, texpath_rel, properties_tex, properties_vid):
    """
    Write the (file) Texture data block.
    """
    # XXX All this is very fuzzy to me currently...
    #     Textures do not seem to use properties as much as they could.
    #     For now assuming most logical and simple stuff.

    fbx_vid = elem_data_single_int64(objectsParent, b"Video", video_id)
    fbx_vid.add_string(fbx_name_class(video_key.encode()))
    fbx_vid.add_string(b"Clip")

    props = elem_properties(fbx_vid)
    for pname, ptype, value, animatable, custom in get_properties(properties_vid):
        elem_props_set(props, ptype, pname, value, animatable, custom)

    elem_data_single_int32(fbx_vid, b"UseMipMap", 0)
    elem_data_single_string_unicode(fbx_vid, b"Filename", texpath)
    elem_data_single_string_unicode(fbx_vid, b"RelativeFilename", texpath_rel)


    fbx_tex = elem_data_single_int64(objectsParent, b"Texture", id)
    fbx_tex.add_string(fbx_name_class(key.encode()))
    fbx_tex.add_string(b"")

    elem_data_single_string(fbx_tex, b"Type", b"TextureVideoClip")
    elem_data_single_int32(fbx_tex, b"Version", FBX_TEXTURE_VERSION)
    elem_data_single_string(fbx_tex, b"TextureName", fbx_name_class(key.encode()))
    elem_data_single_string(fbx_tex, b"Media", video_key)
    elem_data_single_string_unicode(fbx_tex, b"Filename", texpath)
    elem_data_single_string_unicode(fbx_tex, b"RelativeFilename", texpath_rel)

    elem_data_single_float32_array(fbx_tex, b"ModelUVTranslation", [0,0])
    elem_data_single_float32_array(fbx_tex, b"ModelUVScaling", [1,1])
    elem_data_single_string(fbx_tex, b"Texture_Alpha_Source", "None")
    elem_data_single_int32_array(fbx_tex, b"Cropping", [0,0,0,0])

    props = elem_properties(fbx_tex)
    for pname, ptype, value, animatable, custom in get_properties(properties_tex):
        elem_props_set(props, ptype, pname, value, animatable, custom)

    # UseMaterial should always be ON imho.
    elem_props_set(props, "p_bool", b"UseMaterial", True)


def fbx_data_skeleton_bone_model(objectsParent, key, id, properties):
    # Bone "data".

    #id = get_fbx_uuid_from_key(boneDataKey)

    fbx_bo = elem_data_single_int64(objectsParent, b"Model", id)
    fbx_bo.add_string(fbx_name_class(key.encode()))
    #fbx_bo.add_string(fbx_name_class(boneName.encode(), b"NodeAttribute"))
    fbx_bo.add_string(b"LimbNode")
    elem_data_single_int32(fbx_bo, b"Version", FBX_MODELS_VERSION)
    elem_data_single_bool(fbx_bo, b"Shading", True)
    elem_data_single_string(fbx_bo, b"Culling", "CullingOff")

    props = elem_properties(fbx_bo)
    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)


def fbx_data_skeleton_bone_node(objectsParent, key, id, properties):
    # Bone "data".

    #id = get_fbx_uuid_from_key(boneDataKey)

    fbx_bo = elem_data_single_int64(objectsParent, b"NodeAttribute", id)
    fbx_bo.add_string(fbx_name_class(key.encode()))
    fbx_bo.add_string(b"LimbNode")
    elem_data_single_string(fbx_bo, b"TypeFlags", b"Skeleton")

    props = elem_properties(fbx_bo)
    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)


def fbx_data_skeleton_model(objectsParent, key, id, properties):
    # Skeleton null object (has no data).

    #id = get_fbx_uuid_from_key(boneDataKey)

    fbx_bo = elem_data_single_int64(objectsParent, b"Model", id)
    fbx_bo.add_string(fbx_name_class(key.encode()))
    fbx_bo.add_string(b"Null")
    elem_data_single_int32(fbx_bo, b"Version", FBX_MODELS_VERSION)
    elem_data_single_bool(fbx_bo, b"Shading", True)
    elem_data_single_string(fbx_bo, b"Culling", "CullingOff")

    props = elem_properties(fbx_bo)
    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)


def fbx_data_deformer(objectsParent, key, id, properties):
    fbx_skin = elem_data_single_int64(objectsParent, b"Deformer", id)
    fbx_skin.add_string(fbx_name_class(key))
    fbx_skin.add_string(b"Skin")

    props = elem_properties(fbx_skin)
    for pname, ptype, value, animatable, custom in get_properties(properties):
        elem_props_set(props, ptype, pname, value, animatable, custom)

    elem_data_single_int32(fbx_skin, b"Version", FBX_DEFORMER_SKIN_VERSION)
    elem_data_single_float64(fbx_skin, b"Link_DeformAcuracy", 50.0)  # Only vague idea what it is...


def fbx_data_subdeformer(objectsParent, key, id, indices, weights, bindmat, bindinv):
    # Create the cluster.
    fbx_clstr = elem_data_single_int64(objectsParent, b"Deformer", id)
    fbx_clstr.add_string(fbx_name_class(key))
    fbx_clstr.add_string(b"Cluster")

    elem_data_single_int32(fbx_clstr, b"Version", FBX_DEFORMER_CLUSTER_VERSION)
    # No idea what that user data might be...
    fbx_userdata = elem_data_single_string(fbx_clstr, b"UserData", b"")
    fbx_userdata.add_string(b"")
    elem_data_single_int32_array(fbx_clstr, b"Indexes", indices)
    elem_data_single_float64_array(fbx_clstr, b"Weights", weights)
    # Transform, TransformLink and TransformAssociateModel matrices...
    # They seem to be doublons of BindPose ones??? Have armature (associatemodel) in addition, though.
    # WARNING! Even though official FBX API presents Transform in global space,
    #          **it is stored in bone space in FBX data!** See:
    #          http://area.autodesk.com/forum/autodesk-fbx/fbx-sdk/why-the-values-return-
    #                 by-fbxcluster-gettransformmatrix-x-not-same-with-the-value-in-ascii-fbx-file/
    elem_data_single_float64_array(fbx_clstr, b"Transform", bindmat.ravel(order='C'))
    elem_data_single_float64_array(fbx_clstr, b"TransformLink", bindinv.ravel(order='C'))
    #elem_data_single_float64_array(fbx_clstr, b"TransformAssociateModel", matrix4_to_array(mat_world_arm))

# ##### Top-level FBX elements generators. #####

def fbx_header_elements(root, config, filepath, time=None):
    """
    Write boiling code of FBX root.
    time is expected to be a datetime.datetime object, or None (using now() in this case).
    """
    import makehuman
    app_vendor = "MakeHuman.org"
    app_name = "MakeHuman"
    app_ver = makehuman.getVersionStr()

    # ##### Start of FBXHeaderExtension element.
    header_ext = elem_empty(root, b"FBXHeaderExtension")

    elem_data_single_int32(header_ext, b"FBXHeaderVersion", FBX_HEADER_VERSION)

    elem_data_single_int32(header_ext, b"FBXVersion", FBX_VERSION)

    # No encryption!
    elem_data_single_int32(header_ext, b"EncryptionType", 0)

    if time is None:
        time = datetime.datetime.now()
    elem = elem_empty(header_ext, b"CreationTimeStamp")
    elem_data_single_int32(elem, b"Version", 1000)
    elem_data_single_int32(elem, b"Year", time.year)
    elem_data_single_int32(elem, b"Month", time.month)
    elem_data_single_int32(elem, b"Day", time.day)
    elem_data_single_int32(elem, b"Hour", time.hour)
    elem_data_single_int32(elem, b"Minute", time.minute)
    elem_data_single_int32(elem, b"Second", time.second)
    elem_data_single_int32(elem, b"Millisecond", time.microsecond // 1000)

    # The FBX converter refuses to load the character unless this is the creator.
    elem_data_single_string_unicode(header_ext, b"Creator", "FBX SDK/FBX Plugins version 2013.3")
    #elem_data_single_string_unicode(header_ext, b"Creator", "%s - %s" % (app_name, app_ver))

    # 'SceneInfo' seems mandatory to get a valid FBX file...
    # TODO use real values!
    # XXX Should we use scene.name.encode() here?
    scene_info = elem_data_single_string(header_ext, b"SceneInfo", fbx_name_class(b"GlobalInfo", b"SceneInfo"))
    scene_info.add_string(b"UserData")
    elem_data_single_string(scene_info, b"Type", b"UserData")
    elem_data_single_int32(scene_info, b"Version", FBX_SCENEINFO_VERSION)
    meta_data = elem_empty(scene_info, b"MetaData")
    elem_data_single_int32(meta_data, b"Version", FBX_SCENEINFO_VERSION)
    elem_data_single_string(meta_data, b"Title", b"")
    elem_data_single_string(meta_data, b"Subject", b"")
    elem_data_single_string(meta_data, b"Author", b"www.makehuman.org")
    elem_data_single_string(meta_data, b"Keywords", b"")
    elem_data_single_string(meta_data, b"Revision", b"")
    elem_data_single_string(meta_data, b"Comment", b"")

    props = elem_properties(scene_info)
    elem_props_set(props, "p_string_url", b"DocumentUrl", filepath)    # TODO set to current export filename?
    elem_props_set(props, "p_string_url", b"SrcDocumentUrl", filepath)
    original = elem_props_compound(props, b"Original")
    original("p_string", b"ApplicationVendor", app_vendor)
    original("p_string", b"ApplicationName", app_name)
    original("p_string", b"ApplicationVersion", app_ver)
    original("p_datetime", b"DateTime_GMT", "")
    original("p_string", b"FileName", "")
    lastsaved = elem_props_compound(props, b"LastSaved")
    lastsaved("p_string", b"ApplicationVendor", app_vendor)
    lastsaved("p_string", b"ApplicationName", app_name)
    lastsaved("p_string", b"ApplicationVersion", app_ver)
    lastsaved("p_datetime", b"DateTime_GMT", "")

    # ##### End of FBXHeaderExtension element.

    # FileID is replaced by dummy value currently...
    elem_data_single_bytes(root, b"FileId", b"FooBar")

    # CreationTime is replaced by dummy value currently, but anyway...
    elem_data_single_string_unicode(root, b"CreationTime",
                                    "{:04}-{:02}-{:02} {:02}:{:02}:{:02}:{:03}"
                                    "".format(time.year, time.month, time.day, time.hour, time.minute, time.second,
                                              time.microsecond * 1000))

    #elem_data_single_string_unicode(root, b"Creator", "%s - %s" % (app_name, app_ver))
    elem_data_single_string_unicode(root, b"Creator", "FBX SDK/FBX Plugins version 2013.3 build=20120911")

    # ##### Start of GlobalSettings element.
    global_settings = elem_empty(root, b"GlobalSettings")

    elem_data_single_int32(global_settings, b"Version", 1000)

    props = elem_properties(global_settings)

    mesh_orientation = getMeshOrientation(config)
    up_axis, front_axis, coord_axis = RIGHT_HAND_AXES[mesh_orientation]
    # Currently not sure about that, but looks like default unit of FBX is cm...
    #scale_factor = 10.0/config.scale  # MH scales the mesh coordinates, the scale factor is a constant
    scale_factor = 10
    elem_props_set(props, "p_integer", b"UpAxis", up_axis[0])
    elem_props_set(props, "p_integer", b"UpAxisSign", up_axis[1])
    elem_props_set(props, "p_integer", b"FrontAxis", front_axis[0])
    elem_props_set(props, "p_integer", b"FrontAxisSign", front_axis[1])
    elem_props_set(props, "p_integer", b"CoordAxis", coord_axis[0])
    elem_props_set(props, "p_integer", b"CoordAxisSign", coord_axis[1])
    elem_props_set(props, "p_integer", b"OriginalUpAxis", -1)
    elem_props_set(props, "p_integer", b"OriginalUpAxisSign", 1)
    elem_props_set(props, "p_double", b"UnitScaleFactor", scale_factor)
    elem_props_set(props, "p_double", b"OriginalUnitScaleFactor", scale_factor)
    elem_props_set(props, "p_color_rgb", b"AmbientColor", (0.0, 0.0, 0.0))
    elem_props_set(props, "p_string", b"DefaultCamera", "Producer Perspective")

    # Global timing data.
    elem_props_set(props, "p_enum", b"TimeMode", 0)
    elem_props_set(props, "p_timestamp", b"TimeSpanStart", 0)
    elem_props_set(props, "p_timestamp", b"TimeSpanStop", 46186158000)
    elem_props_set(props, "p_double", b"CustomFrameRate", -1)

    # ##### End of GlobalSettings element.


def fbx_documents_elements(root, name, id):
    """
    Write 'Document' part of FBX root.
    Seems like FBX support multiple documents, but until I find examples of such, we'll stick to single doc!
    time is expected to be a datetime.datetime object, or None (using now() in this case).
    """
    # ##### Start of Documents element.
    docs = elem_empty(root, b"Documents")

    elem_data_single_int32(docs, b"Count", 1)

    doc = elem_data_single_int64(docs, b"Document", id)
    doc.add_string_unicode("Scene")
    doc.add_string_unicode("Scene")

    props = elem_properties(doc)
    elem_props_set(props, "p_object", b"SourceObject")
    elem_props_set(props, "p_string", b"ActiveAnimStackName", "")

    # XXX Some kind of ID? Offset?
    #     Anyway, as long as we have only one doc, probably not an issue.
    elem_data_single_int64(doc, b"RootNode", 0)


def fbx_references_elements(root):
    """
    Have no idea what references are in FBX currently... Just writing empty element.
    """
    docs = elem_empty(root, b"References")


def fbx_definitions_elements(root, users_count):
    """
    Templates definitions. Only used by Objects data afaik (apart from dummy GlobalSettings one).
    """
    definitions = elem_empty(root, b"Definitions")

    elem_data_single_int32(definitions, b"Version", FBX_TEMPLATES_VERSION)
    elem_data_single_int32(definitions, b"Count", users_count)

    fbx_template_generate(definitions, b"GlobalSettings", 1)
    #fbx_templates_generate(definitions, scene_data.templates)


def fbx_connections_element(root):
    """
    Relations between Objects (which material uses which texture, and so on).
    """
    connections = elem_empty(root, b"Connections")
    return connections

def fbx_takes_element(root):
    # TODO actually allow exporting takes, or is it not required (according to blender fbx authors)?
    # XXX Pretty sure takes are no more needed...
    takes = elem_empty(root, b"Takes")
    elem_data_single_string(takes, b"Current", b"")
