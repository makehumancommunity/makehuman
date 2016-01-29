#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

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


import math

from collections import namedtuple, OrderedDict


from . import encode_bin, data_types


# "Constants"
FBX_VERSION = 7300
FBX_HEADER_VERSION = 1003
FBX_SCENEINFO_VERSION = 100
FBX_TEMPLATES_VERSION = 100

FBX_MODELS_VERSION = 232

FBX_GEOMETRY_VERSION = 124
# Revert back normals to 101 (simple 3D values) for now, 102 (4D + weights) seems not well supported by most apps
# currently, apart from some AD products.
FBX_GEOMETRY_NORMAL_VERSION = 101
FBX_GEOMETRY_BINORMAL_VERSION = 101
FBX_GEOMETRY_TANGENT_VERSION = 101
FBX_GEOMETRY_SMOOTHING_VERSION = 102
FBX_GEOMETRY_VCOLOR_VERSION = 101
FBX_GEOMETRY_UV_VERSION = 101
FBX_GEOMETRY_MATERIAL_VERSION = 101
FBX_GEOMETRY_LAYER_VERSION = 100
FBX_GEOMETRY_SHAPE_VERSION = 100
FBX_DEFORMER_SHAPE_VERSION = 100
FBX_DEFORMER_SHAPECHANNEL_VERSION = 100
FBX_POSE_BIND_VERSION = 100
FBX_DEFORMER_SKIN_VERSION = 101
FBX_DEFORMER_CLUSTER_VERSION = 100
FBX_MATERIAL_VERSION = 102
FBX_TEXTURE_VERSION = 202
FBX_ANIM_KEY_VERSION = 4008

FBX_NAME_CLASS_SEP = b"\x00\x01"
FBX_ANIM_PROPSGROUP_NAME = "d"

FBX_KTIME = 46186158000  # This is the number of "ktimes" in one second (yep, precision over the nanosecond...)


# MAT_CONVERT_BONE = Matrix.Rotation(math.pi / 2.0, 4, 'Z')  # Blender is +Y, FBX is -X.


BLENDER_OBJECT_TYPES_MESHLIKE = {'MESH'}


def getMeshOrientation(config):
    if config.yUpFaceZ:
        return ('Y', 'Z')
    if config.yUpFaceX:
        return ('Y', 'X')
    if config.zUpFaceNegY:
        return ('Z', '-Y')
    if config.zUpFaceX:
        return ('Z', 'X')
    return ('Y', 'Z')

RIGHT_HAND_AXES = {
    # Up, Front -> FBX values (tuples of (axis, sign), Up, Front, Coord).
    ('X',  'Y'):  ((0, 1),  (1, 1),  (2, 1)),
    ('X',  '-Y'): ((0, 1),  (1, -1), (2, -1)),
    ('X',  'Z'):  ((0, 1),  (2, 1),  (1, -1)),
    ('X',  '-Z'): ((0, 1),  (2, -1), (1, 1)),
    ('-X', 'Y'):  ((0, -1), (1, 1),  (2, -1)),
    ('-X', '-Y'): ((0, -1), (1, -1), (2, 1)),
    ('-X', 'Z'):  ((0, -1), (2, 1),  (1, 1)),
    ('-X', '-Z'): ((0, -1), (2, -1), (1, -1)),
    ('Y',  'X'):  ((1, 1),  (0, 1),  (2, -1)),
    ('Y',  '-X'): ((1, 1),  (0, -1), (2, 1)),
    ('Y',  'Z'):  ((1, 1),  (2, 1),  (0, 1)),
    ('Y',  '-Z'): ((1, 1),  (2, -1), (0, -1)),
    ('-Y', 'X'):  ((1, -1), (0, 1),  (2, 1)),
    ('-Y', '-X'): ((1, -1), (0, -1), (2, -1)),
    ('-Y', 'Z'):  ((1, -1), (2, 1),  (0, -1)),
    ('-Y', '-Z'): ((1, -1), (2, -1), (0, 1)),
    ('Z',  'X'):  ((2, 1),  (0, 1),  (1, 1)),
    ('Z',  '-X'): ((2, 1),  (0, -1), (1, -1)),
    ('Z',  'Y'):  ((2, 1),  (1, 1),  (0, -1)),
    ('Z',  '-Y'): ((2, 1),  (1, -1), (0, 1)),  # Blender system!
    ('-Z', 'X'):  ((2, -1), (0, 1),  (1, -1)),
    ('-Z', '-X'): ((2, -1), (0, -1), (1, 1)),
    ('-Z', 'Y'):  ((2, -1), (1, 1),  (0, 1)),
    ('-Z', '-Y'): ((2, -1), (1, -1), (0, -1)),
}


FBX_FRAMERATES = (
    (-1.0, 14),  # Custom framerate.
    (120.0, 1),
    (100.0, 2),
    (60.0, 3),
    (50.0, 4),
    (48.0, 5),
    (30.0, 6),  # BW NTSC.
    (30.0 / 1.001, 9),  # Color NTSC.
    (25.0, 10),
    (24.0, 11),
    (24.0 / 1.001, 13),
    (96.0, 15),
    (72.0, 16),
    (60.0 / 1.001, 17),
)


# ##### Misc utilities #####

# Note: this could be in a utility (math.units e.g.)...

UNITS = {
    "meter": 1.0,  # Ref unit!
    "kilometer": 0.001,
    "millimeter": 1000.0,
    "foot": 1.0 / 0.3048,
    "inch": 1.0 / 0.0254,
    "turn": 1.0,  # Ref unit!
    "degree": 360.0,
    "radian": math.pi * 2.0,
    "second": 1.0,  # Ref unit!
    "ktime": FBX_KTIME,
}


def units_convertor(u_from, u_to):
    """Return a convertor between specified units."""
    conv = UNITS[u_to] / UNITS[u_from]
    return lambda v: v * conv


def units_convertor_iter(u_from, u_to):
    """Return an iterable convertor between specified units."""
    conv = units_convertor(u_from, u_to)

    def convertor(it):
        for v in it:
            yield(conv(v))

    return convertor


def matrix4_to_array(mat):
    """Concatenate matrix's columns into a single, flat tuple"""
    # blender matrix is row major, fbx is col major so transpose on write
    return tuple(f for v in mat.transposed() for f in v)


def array_to_matrix4(arr):
    """Convert a single 16-len tuple into a valid 4D Blender matrix"""
    # Blender matrix is row major, fbx is col major so transpose on read
    return Matrix(tuple(zip(*[iter(arr)]*4))).transposed()


def similar_values(v1, v2, e=1e-6):
    """Return True if v1 and v2 are nearly the same."""
    if v1 == v2:
        return True
    return ((abs(v1 - v2) / max(abs(v1), abs(v2))) <= e)


def similar_values_iter(v1, v2, e=1e-6):
    """Return True if iterables v1 and v2 are nearly the same."""
    if v1 == v2:
        return True
    for v1, v2 in zip(v1, v2):
        if (v1 != v2) and ((abs(v1 - v2) / max(abs(v1), abs(v2))) > e):
            return False
    return True

def vcos_transformed_gen(raw_cos, m=None):
    # Note: we could most likely get much better performances with numpy, but will leave this as TODO for now.
    gen = zip(*(iter(raw_cos),) * 3)
    return gen if m is None else (m * Vector(v) for v in gen)

def nors_transformed_gen(raw_nors, m=None):
    # Great, now normals are also expected 4D!
    # XXX Back to 3D normals for now!
    # gen = zip(*(iter(raw_nors),) * 3 + (_infinite_gen(1.0),))
    gen = zip(*(iter(raw_nors),) * 3)
    return gen if m is None else (m * Vector(v) for v in gen)


'''
# ##### UIDs code. #####

# ID class (mere int).
class UUID(int):
    pass


# UIDs storage.
_keys_to_uuids = {}
_uuids_to_keys = {}


def _key_to_uuid(uuids, key):
    # TODO: Check this is robust enough for our needs!
    # Note: We assume we have already checked the related key wasn't yet in _keys_to_uids!
    #       As int64 is signed in FBX, we keep uids below 2**63...
    if isinstance(key, int) and 0 <= key < 2**63:
        # We can use value directly as id!
        uuid = key
    else:
        uuid = hash(key)
        if uuid < 0:
            uuid = -uuid
        if uuid >= 2**63:
            uuid //= 2
    # Try to make our uid shorter!
    if uuid > int(1e9):
        t_uuid = uuid % int(1e9)
        if t_uuid not in uuids:
            uuid = t_uuid
    # Make sure our uuid *is* unique.
    if uuid in uuids:
        inc = 1 if uuid < 2**62 else -1
        while uuid in uuids:
            uuid += inc
            if 0 > uuid >= 2**63:
                # Note that this is more that unlikely, but does not harm anyway...
                raise ValueError("Unable to generate an UUID for key {}".format(key))
    return UUID(uuid)


def get_fbx_uuid_from_key(key):
    """
    Return an UUID for given key, which is assumed hasable.
    """
    uuid = _keys_to_uuids.get(key, None)
    if uuid is None:
        uuid = _key_to_uuid(_uuids_to_keys, key)
        _keys_to_uuids[key] = uuid
        _uuids_to_keys[uuid] = key
    return uuid


# XXX Not sure we'll actually need this one?
def get_key_from_fbx_uuid(uuid):
    """
    Return the key which generated this uid.
    """
    assert(uuid.__class__ == UUID)
    return _uuids_to_keys.get(uuid, None)


    """Return (stack/layer, ID, fbxprop, item) curve key."""
    return "|".join((get_blender_anim_id_base(scene, ref_id), obj_key, fbx_prop_name,
                     fbx_prop_item_name, "AnimCurve"))
'''

# ##### Element generators. #####

# Note: elem may be None, in this case the element is not added to any parent.
def elem_empty(elem, name):
    sub_elem = encode_bin.FBXElem(name)
    if elem is not None:
        elem.elems.append(sub_elem)
    return sub_elem


def _elem_data_single(elem, name, value, func_name):
    sub_elem = elem_empty(elem, name)
    getattr(sub_elem, func_name)(value)
    return sub_elem


def _elem_data_vec(elem, name, value, func_name):
    sub_elem = elem_empty(elem, name)
    func = getattr(sub_elem, func_name)
    for v in value:
        func(v)
    return sub_elem

def get_child_element(parentelem, name):
    for child in parentelem.elems:
        if child.id == name:
            return child
    return None

def elem_data_single_bool(elem, name, value):
    return _elem_data_single(elem, name, value, "add_bool")


def elem_data_single_int16(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int16")


def elem_data_single_int32(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int32")


def elem_data_single_int64(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int64")


def elem_data_single_float32(elem, name, value):
    return _elem_data_single(elem, name, value, "add_float32")


def elem_data_single_float64(elem, name, value):
    return _elem_data_single(elem, name, value, "add_float64")


def elem_data_single_bytes(elem, name, value):
    return _elem_data_single(elem, name, value, "add_bytes")


def elem_data_single_string(elem, name, value):
    return _elem_data_single(elem, name, value, "add_string")


def elem_data_single_string_unicode(elem, name, value):
    return _elem_data_single(elem, name, value, "add_string_unicode")


def elem_data_single_bool_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_bool_array")


def elem_data_single_int32_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int32_array")


def elem_data_single_int64_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_int64_array")


def elem_data_single_float32_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_float32_array")


def elem_data_single_float64_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_float64_array")


def elem_data_single_byte_array(elem, name, value):
    return _elem_data_single(elem, name, value, "add_byte_array")


def elem_data_vec_float64(elem, name, value):
    return _elem_data_vec(elem, name, value, "add_float64")


# ##### Generators for standard FBXProperties70 properties. #####

def elem_properties(elem):
    return elem_empty(elem, b"Properties70")


# Properties definitions, format: (b"type_1", b"label(???)", "name_set_value_1", "name_set_value_2", ...)
# XXX Looks like there can be various variations of formats here... Will have to be checked ultimately!
#     Also, those "custom" types like 'FieldOfView' or 'Lcl Translation' are pure nonsense,
#     these are just Vector3D ultimately... *sigh* (again).
FBX_PROPERTIES_DEFINITIONS = {
    # Generic types.
    "p_bool": (b"bool", b"", "add_int32"),  # Yes, int32 for a bool (and they do have a core bool type)!!!
    "p_integer": (b"int", b"Integer", "add_int32"),
    "p_ulonglong": (b"ULongLong", b"", "add_int64"),
    "p_double": (b"double", b"Number", "add_float64"),  # Non-animatable?
    "p_number": (b"Number", b"", "add_float64"),  # Animatable-only?
    "p_enum": (b"enum", b"", "add_int32"),
    "p_vector_3d": (b"Vector3D", b"Vector", "add_float64", "add_float64", "add_float64"),  # Non-animatable?
    "p_vector": (b"Vector", b"", "add_float64", "add_float64", "add_float64"),  # Animatable-only?
    "p_color_rgb": (b"ColorRGB", b"Color", "add_float64", "add_float64", "add_float64"),  # Non-animatable?
    "p_color": (b"Color", b"", "add_float64", "add_float64", "add_float64"),  # Animatable-only?
    "p_string": (b"KString", b"", "add_string_unicode"),
    "p_string_url": (b"KString", b"Url", "add_string_unicode"),
    "p_string_xrefurl": (b"KString", b"XrefUrl", "add_string_unicode"),
    "p_timestamp": (b"KTime", b"Time", "add_int64"),
    "p_datetime": (b"DateTime", b"", "add_string_unicode"),
    # Special types.
    "p_object": (b"object", b""),  # XXX Check this! No value for this prop??? Would really like to know how it works!
    "p_compound": (b"Compound", b""),
    # Specific types (sic).
    # ## Objects (Models).
    "p_lcl_translation": (b"Lcl Translation", b"", "add_float64", "add_float64", "add_float64"),
    "p_lcl_rotation": (b"Lcl Rotation", b"", "add_float64", "add_float64", "add_float64"),
    "p_lcl_scaling": (b"Lcl Scaling", b"", "add_float64", "add_float64", "add_float64"),
    "p_visibility": (b"Visibility", b"", "add_float64"),
    "p_visibility_inheritance": (b"Visibility Inheritance", b"", "add_int32"),
    # ## Cameras!!!
    "p_roll": (b"Roll", b"", "add_float64"),
    "p_opticalcenterx": (b"OpticalCenterX", b"", "add_float64"),
    "p_opticalcentery": (b"OpticalCenterY", b"", "add_float64"),
    "p_fov": (b"FieldOfView", b"", "add_float64"),
    "p_fov_x": (b"FieldOfViewX", b"", "add_float64"),
    "p_fov_y": (b"FieldOfViewY", b"", "add_float64"),
}

def get_ascii_properties(properties, indent=0):
    result = []
    for p in properties:
        if len(p) < 3:
            continue
        if len(p) == 3:
            name, ptype, value = p
            animatable = False
            custom = False
        elif len(p) == 4:
            name, ptype, value, animatable = p
            custom = False
        else:
            name, ptype, value, animatable, custom = p

        result.append( indent*'    ' + get_ascii_property(name, ptype, value, animatable, custom) )

    return '\n'.join(result)

def get_ascii_property(name, ptype, value, animatable=False, custom=False):
    if isinstance(value, tuple):
        value = list(value)
    elif not isinstance(value, list):
        value = [value]

    flags = _elem_props_flags(animatable, custom)
    ptype = FBX_PROPERTIES_DEFINITIONS[ptype]

    if len(ptype) > 2 and 'string' in ptype[2]:
        value = ['"%s"' % v for v in value]
    elif len(ptype) > 2 and 'int' in ptype[2]:
        value = [int(v) for v in value]

    return 'P: "%s", "%s", "%s", "%s", %s' % (name, ptype[0], ptype[1], flags, (','.join([str(v) for v in value])))

def _elem_props_set(elem, ptype, name, value, flags):
    p = elem_data_single_string(elem, b"P", name)
    for t in ptype[:2]:
        p.add_string(t)
    p.add_string(flags)
    if len(ptype) == 3:
        getattr(p, ptype[2])(value)
    elif len(ptype) > 3:
        # We assume value is iterable, else it's a bug!
        for callback, val in zip(ptype[2:], value):
            getattr(p, callback)(val)


def _elem_props_flags(animatable, custom):
    if animatable and custom:
        return b"AU"
    elif animatable:
        return b"A"
    elif custom:
        return b"U"
    return b""


def elem_props_set(elem, ptype, name, value=None, animatable=False, custom=False):
    ptype = FBX_PROPERTIES_DEFINITIONS[ptype]
    import log
    log.debug('propset %s %s %s', name, value, type(value))
    _elem_props_set(elem, ptype, name, value, _elem_props_flags(animatable, custom))


def elem_props_compound(elem, cmpd_name, custom=False):
    def _setter(ptype, name, value, animatable=False, custom=False):
        name = cmpd_name + b"|" + name
        elem_props_set(elem, ptype, name, value, animatable=animatable, custom=custom)

    elem_props_set(elem, "p_compound", cmpd_name, custom=custom)
    return _setter


def elem_props_template_init(templates, template_type):
    """
    Init a writing template of given type, for *one* element's properties.
    """
    ret = OrderedDict()
    tmpl = templates.get(template_type)
    if tmpl is not None:
        written = tmpl.written[0]
        props = tmpl.properties
        ret = OrderedDict((name, [val, ptype, anim, written]) for name, (val, ptype, anim) in props.items())
    return ret


def elem_props_template_set(template, elem, ptype_name, name, value, animatable=False):
    """
    Only add a prop if the same value is not already defined in given template.
    Note it is important to not give iterators as value, here!
    """
    ptype = FBX_PROPERTIES_DEFINITIONS[ptype_name]
    if len(ptype) > 3:
        value = tuple(value)
    tmpl_val, tmpl_ptype, tmpl_animatable, tmpl_written = template.get(name, (None, None, False, False))
    # Note animatable flag from template takes precedence over given one, if applicable.
    if tmpl_ptype is not None:
        if (tmpl_written and
            ((len(ptype) == 3 and (tmpl_val, tmpl_ptype) == (value, ptype_name)) or
             (len(ptype) > 3 and (tuple(tmpl_val), tmpl_ptype) == (value, ptype_name)))):
            return  # Already in template and same value.
        _elem_props_set(elem, ptype, name, value, _elem_props_flags(tmpl_animatable, False))
        template[name][3] = True
    else:
        _elem_props_set(elem, ptype, name, value, _elem_props_flags(animatable, False))


def elem_props_template_finalize(template, elem):
    """
    Finalize one element's template/props.
    Issue is, some templates might be "needed" by different types (e.g. NodeAttribute is for lights, cameras, etc.),
    but values for only *one* subtype can be written as template. So we have to be sure we write those for the other
    subtypes in each and every elements, if they are not overriden by that element.
    Yes, hairy, FBX that is to say. When they could easily support several subtypes per template... :(
    """
    for name, (value, ptype_name, animatable, written) in template.items():
        if written:
            continue
        ptype = FBX_PROPERTIES_DEFINITIONS[ptype_name]
        _elem_props_set(elem, ptype, name, value, _elem_props_flags(animatable, False))


# ##### Templates #####
# TODO: check all those "default" values, they should match Blender's default as much as possible, I guess?

FBXTemplate = namedtuple("FBXTemplate", ("type_name", "prop_type_name", "properties", "nbr_users", "written"))

def get_properties(properties):
    for p in properties:
        if len(p) < 3:
            continue
        if len(p) == 3:
            name, ptype, value = p
            animatable = False
            custom = False
        elif len(p) == 4:
            name, ptype, value, animatable = p
            custom = False
        else:
            name, ptype, value, animatable, custom = p

        yield (name, ptype, value, animatable, custom)

def fbx_template_generate(definitionsNode, objectType_name, users_count, propertyTemplate_name=None, properties=[]):
    template = elem_data_single_string(definitionsNode, b"ObjectType", objectType_name)
    elem_data_single_int32(template, b"Count", users_count)

    if propertyTemplate_name and len(properties) > 0:
        elem = elem_data_single_string(template, b"PropertyTemplate", propertyTemplate_name)
        props = elem_properties(elem)

        for name, ptype, value, animatable, custom in get_properties(properties):
            try:
                elem_props_set(props, ptype, name, value, animatable, custom)
            except Exception as e:
                import log
                log.debug("FBX: Failed to write template prop (%r) (%s)", e, str((props, ptype, name, value, animatable)))


def fbx_name_class(name, cls=None):
    if cls is None:
        cls,name = name.split('::')
    return FBX_NAME_CLASS_SEP.join((name, cls))

