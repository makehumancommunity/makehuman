"""Debug utilities for EGL operations"""
from OpenGL.EGL import *
import itertools


def eglErrorName(value):
    """Returns error constant if known, otherwise returns value"""
    return KNOWN_ERRORS.get(value, value)


KNOWN_ERRORS = {
    EGL_SUCCESS: EGL_SUCCESS,
    EGL_NOT_INITIALIZED: EGL_NOT_INITIALIZED,
    EGL_BAD_ACCESS: EGL_BAD_ACCESS,
    EGL_BAD_ALLOC: EGL_BAD_ALLOC,
    EGL_BAD_ATTRIBUTE: EGL_BAD_ATTRIBUTE,
    EGL_BAD_CONTEXT: EGL_BAD_CONTEXT,
    EGL_BAD_CONFIG: EGL_BAD_CONFIG,
    EGL_BAD_CURRENT_SURFACE: EGL_BAD_CURRENT_SURFACE,
    EGL_BAD_DISPLAY: EGL_BAD_DISPLAY,
    EGL_BAD_SURFACE: EGL_BAD_SURFACE,
    EGL_BAD_MATCH: EGL_BAD_MATCH,
    EGL_BAD_PARAMETER: EGL_BAD_PARAMETER,
    EGL_BAD_NATIVE_PIXMAP: EGL_BAD_NATIVE_PIXMAP,
    EGL_BAD_NATIVE_WINDOW: EGL_BAD_NATIVE_WINDOW,
    EGL_CONTEXT_LOST: EGL_CONTEXT_LOST,
}


def write_ppm(buf, filename):
    """Write height * width * 3-component buffer as ppm to filename
    
    This lets us write a simple image format without
    using any libraries that can be viewed on most
    linux workstations.
    """
    with open(filename, "w") as f:
        h, w, c = buf.shape
        print("P3", file=f)
        print("# ascii ppm file created by pyopengl", file=f)
        print("%i %i" % (w, h), file=f)
        print("255", file=f)
        for y in range(h - 1, -1, -1):
            for x in range(w):
                pixel = buf[y, x]
                l = " %3d %3d %3d" % (pixel[0], pixel[1], pixel[2])
                f.write(l)
            f.write("\n")


def debug_config(display, config):
    """Get debug display for the given configuration"""
    result = {}
    value = EGLint()
    for attr in CONFIG_ATTRS:
        if not eglGetConfigAttrib(display, config, attr, value):
            log.warning("Failed to get attribute %s from config", attr)
            continue
        if attr in BITMASK_FIELDS:
            attr_value = {}
            for subattr in BITMASK_FIELDS[attr]:
                if value.value & subattr:
                    attr_value[subattr.name] = True
        else:
            attr_value = value.value
        result[attr.name] = attr_value
    return result


def debug_configs(display, configs=None, max_count=256):
    """Present a formatted list of configs for the display"""
    if configs is None:
        configs = (EGLConfig * max_count)()
        num_configs = EGLint()
        eglGetConfigs(display, configs, max_count, num_configs)
        if not num_configs.value:
            return []
        configs = configs[: num_configs.value]
    debug_configs = [debug_config(display, cfg) for cfg in configs]
    return debug_configs


SURFACE_TYPE_BITS = [
    EGL_MULTISAMPLE_RESOLVE_BOX_BIT,
    EGL_PBUFFER_BIT,
    EGL_PIXMAP_BIT,
    EGL_SWAP_BEHAVIOR_PRESERVED_BIT,
    EGL_VG_ALPHA_FORMAT_PRE_BIT,
    EGL_VG_COLORSPACE_LINEAR_BIT,
    EGL_WINDOW_BIT,
]
RENDERABLE_TYPE_BITS = [
    EGL_OPENGL_BIT,
    EGL_OPENGL_ES_BIT,
    EGL_OPENGL_ES2_BIT,
    EGL_OPENGL_ES3_BIT,
    EGL_OPENVG_BIT,
]
CAVEAT_BITS = [
    EGL_NONE,
    EGL_SLOW_CONFIG,
    EGL_NON_CONFORMANT_CONFIG,
]
TRANSPARENT_BITS = [
    EGL_NONE,
    EGL_TRANSPARENT_RGB,
]

CONFIG_ATTRS = [
    EGL_CONFIG_ID,
    EGL_RED_SIZE,
    EGL_GREEN_SIZE,
    EGL_BLUE_SIZE,
    EGL_DEPTH_SIZE,
    EGL_ALPHA_SIZE,
    EGL_ALPHA_MASK_SIZE,
    EGL_BUFFER_SIZE,
    EGL_STENCIL_SIZE,
    EGL_BIND_TO_TEXTURE_RGB,
    EGL_BIND_TO_TEXTURE_RGBA,
    EGL_COLOR_BUFFER_TYPE,
    EGL_CONFIG_CAVEAT,
    EGL_CONFORMANT,
    EGL_LEVEL,
    EGL_LUMINANCE_SIZE,
    EGL_MAX_PBUFFER_WIDTH,
    EGL_MAX_PBUFFER_HEIGHT,
    EGL_MAX_PBUFFER_PIXELS,
    EGL_MIN_SWAP_INTERVAL,
    EGL_MAX_SWAP_INTERVAL,
    EGL_NATIVE_RENDERABLE,
    EGL_NATIVE_VISUAL_ID,
    EGL_NATIVE_VISUAL_TYPE,
    EGL_RENDERABLE_TYPE,
    EGL_SAMPLE_BUFFERS,
    EGL_SAMPLES,
    EGL_SURFACE_TYPE,
    EGL_TRANSPARENT_TYPE,
    EGL_TRANSPARENT_RED_VALUE,
    EGL_TRANSPARENT_GREEN_VALUE,
    EGL_TRANSPARENT_BLUE_VALUE,
]

BITMASK_FIELDS = dict(
    [
        (EGL_SURFACE_TYPE, SURFACE_TYPE_BITS),
        (EGL_RENDERABLE_TYPE, RENDERABLE_TYPE_BITS),
        (EGL_CONFORMANT, RENDERABLE_TYPE_BITS),
        (EGL_CONFIG_CAVEAT, CAVEAT_BITS),
        (EGL_TRANSPARENT_TYPE, TRANSPARENT_BITS),
    ]
)


def bit_renderer(bit):
    def render(value):
        if bit.name in value:
            return " Y"
        else:
            return " ."

    return render


CONFIG_FORMAT = [
    (EGL_CONFIG_ID, "0x%x", "id", "cfg"),
    (EGL_BUFFER_SIZE, "%i", "sz", "bf"),
    (EGL_LEVEL, "%i", "l", "lv"),
    (EGL_RED_SIZE, "%i", "r", "cbuf"),
    (EGL_GREEN_SIZE, "%i", "g", "cbuf"),
    (EGL_BLUE_SIZE, "%i", "b", "cbuf"),
    (EGL_ALPHA_SIZE, "%i", "a", "cbuf"),
    (EGL_DEPTH_SIZE, "%i", "th", "dp"),
    (EGL_STENCIL_SIZE, "%i", "t", "s"),
    (EGL_SAMPLES, "%i", "ns", "mult"),
    (EGL_SAMPLE_BUFFERS, "%i", "bu", "mult"),
    (EGL_NATIVE_VISUAL_ID, "0x%x", "id", "visual"),
    (EGL_RENDERABLE_TYPE, bit_renderer(EGL_OPENGL_BIT), "gl", "render"),
    (EGL_RENDERABLE_TYPE, bit_renderer(EGL_OPENGL_ES_BIT), "es", "render"),
    (EGL_RENDERABLE_TYPE, bit_renderer(EGL_OPENGL_ES2_BIT), "e2", "render"),
    (EGL_RENDERABLE_TYPE, bit_renderer(EGL_OPENGL_ES3_BIT), "e3", "render"),
    (EGL_RENDERABLE_TYPE, bit_renderer(EGL_OPENVG_BIT), "vg", "render"),
    (EGL_SURFACE_TYPE, bit_renderer(EGL_WINDOW_BIT), "wn", "surface"),
    (EGL_SURFACE_TYPE, bit_renderer(EGL_PBUFFER_BIT), "pb", "surface"),
    (EGL_SURFACE_TYPE, bit_renderer(EGL_PIXMAP_BIT), "px", "surface"),
]


def format_debug_configs(debug_configs, formats=CONFIG_FORMAT):
    """Format config for compact debugging display
    
    Produces a config summary display for a set of 
    debug_configs as a text-mode table.

    Uses `formats` (default `CONFIG_FORMAT`) to determine 
    which fields are extracted and how they are formatted
    along with the column/subcolum set to be rendered in
    the overall header.

    returns formatted ASCII table for display in debug
    logs or utilities
    """
    columns = []
    for (key, format, subcol, col) in formats:
        column = []
        max_width = 0
        for row in debug_configs:
            if isinstance(row, EGLConfig):
                raise TypeError(row, "Call debug_config(display,config)")
            try:
                value = row[key.name]
            except KeyError:
                formatted = "_"
            else:
                if isinstance(format, str):
                    formatted = format % (value)
                else:
                    formatted = format(value)
            max_width = max((len(formatted), max_width))
            column.append(formatted)
        columns.append(
            {
                "rows": column,
                "key": key,
                "format": format,
                "subcol": subcol,
                "col": col,
                "width": max_width,
            }
        )
    headers = []
    subheaders = []
    rows = [headers, subheaders]
    last_column = None
    last_column_width = 0
    for header, subcols in itertools.groupby(columns, lambda x: x["col"]):
        subcols = list(subcols)
        width = sum([col["width"] for col in subcols]) + (len(subcols) - 1)
        headers.append(header.center(width, ".")[:width])
    for column in columns:
        subheaders.append(column["subcol"].rjust(column["width"])[: column["width"]])
    rows.extend(
        zip(*[[v.rjust(col["width"], " ") for v in col["rows"]] for col in columns])
    )
    return "\n".join([" ".join(row) for row in rows])
