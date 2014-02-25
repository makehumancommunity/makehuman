#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Glynn Clements, Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""
from core import G

import numpy as np

import OpenGL
OpenGL.ERROR_CHECKING = G.args.get('debugopengl', False)
OpenGL.ERROR_LOGGING = G.args.get('debugopengl', False)
OpenGL.FULL_LOGGING = G.args.get('fullloggingopengl', False)
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.framebufferobjects import *
from OpenGL.GL.ARB.transpose_matrix import *
from OpenGL.GL.ARB.multisample import *
from OpenGL.GL.ARB.texture_multisample import *

from image import Image
import debugdump
import log
from texture import Texture, getTexture, NOTFOUND_TEXTURE
from shader import Shader
import profiler

g_primitiveMap = [GL_POINTS, GL_LINES, GL_TRIANGLES, GL_QUADS]

TEX_NOT_FOUND = False
MAX_TEXTURE_UNITS = 0

def grabScreen(x, y, width, height, filename = None):
    if width <= 0 or height <= 0:
        raise RuntimeError("width or height is 0")

    log.debug('grabScreen: %d %d %d %d', x, y, width, height)

    # Draw before grabbing, to make sure we grab a rendering and not a picking buffer
    draw()

    sx0 = x
    sy0 = G.windowHeight - y - height
    sx1 = sx0 + width
    sy1 = sy0 + height

    sx0 = max(sx0, 0)
    sx1 = min(sx1, G.windowWidth)
    sy0 = max(sy0, 0)
    sy1 = min(sy1, G.windowHeight)

    rwidth = sx1 - sx0
    rwidth -= rwidth % 4
    sx1 = sx0 + rwidth
    rheight = sy1 - sy0

    surface = np.empty((rheight, rwidth, 3), dtype = np.uint8)

    log.debug('glReadPixels: %d %d %d %d', sx0, sy0, rwidth, rheight)

    glReadPixels(sx0, sy0, rwidth, rheight, GL_RGB, GL_UNSIGNED_BYTE, surface)

    if width != rwidth or height != rheight:
        surf = np.zeros((height, width, 3), dtype = np.uint8) + 127
        surf[...] = surface[:1,:1,:]
        dx0 = (width - rwidth) / 2
        dy0 = (height - rheight) / 2
        dx1 = dx0 + rwidth
        dy1 = dy0 + rheight
        surf[dy0:dy1,dx0:dx1] = surface
        surface = surf

    surface = np.ascontiguousarray(surface[::-1,:,:])
    surface = Image(data = surface)

    if filename is not None:
        surface.save(filename)
        log.message("Saved screengrab to %s", filename)

    return surface

pickingBuffer = None
pickingBufferDirty = True

def updatePickingBuffer():
    width = G.windowWidth
    height = G.windowHeight
    rwidth = (width + 3) / 4 * 4

    # Resize the buffer in case the window size has changed
    global pickingBuffer
    if pickingBuffer is None or pickingBuffer.shape != (height, rwidth, 3):
        pickingBuffer = np.empty((height, rwidth, 3), dtype = np.uint8)

    # Turn off lighting
    glDisable(GL_LIGHTING)

    # Turn off antialiasing
    glDisable(GL_BLEND)
    if have_multisample:
        glDisable(GL_MULTISAMPLE)

    # Clear screen
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    drawMeshes(True)

    # Make sure the data is 1 byte aligned
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    #glFlush()
    #glFinish()

    glReadPixels(0, 0, rwidth, height, GL_RGB, GL_UNSIGNED_BYTE, pickingBuffer)

    # Turn on antialiasing
    glEnable(GL_BLEND)
    if have_multisample:
        glEnable(GL_MULTISAMPLE)

    # restore lighting
    glEnable(GL_LIGHTING)

    # draw()
    global pickingBufferDirty
    pickingBufferDirty = False

def markPickingBufferDirty():
    """
    Indicate that the picking buffer is outdated (has gone stale) and should be
    updated before performing new mouse picking queries (deferred update).
    """
    global pickingBufferDirty
    pickingBufferDirty = True

def getPickedColor(x = None, y = None):
    if x is None or y is None:
        pos = getMousePos()
        if pos is None:
            return (0, 0, 0)
        else:
            x, y = pos
    elif x is None or y is None:
        return (0, 0, 0)

    y = G.windowHeight - y

    if y < 0 or y >= G.windowHeight or x < 0 or x >= G.windowWidth:
        return (0, 0, 0)

    if pickingBuffer is None or pickingBufferDirty:
        updatePickingBuffer()

    return tuple(pickingBuffer[y,x,:])

def queryDepth(x, y):
    if x is None or y is None:
        pos = getMousePos()
        if pos is None:
            return (0, 0, 0)
        else:
            x, y = pos
    elif x is None or y is None:
        return (0, 0, 0)

    y = G.windowHeight - y

    if y < 0 or y >= G.windowHeight or x < 0 or x >= G.windowWidth:
        return 0.0

    # We read only the depth value for the required pixel directly from GPU memory
    # Without caching the depth buffer
    # To be certain the depth buffer in GPU is up to date we force a refresh
    # of the picking buffer (which fills the depth buffer properly).
    updatePickingBuffer()

    sz = np.zeros((1,), dtype=np.float32)
    glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, sz)
    return sz[0]

def reshape(w, h):
    try:
        # Prevent a division by zero when minimising the window
        if h == 0:
            h = 1
        # Set the drawable region of the window
        glViewport(0, 0, w, h)
        # set up the projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # go back to modelview matrix so we can move the objects about
        glMatrixMode(GL_MODELVIEW)

        updatePickingBuffer()
    except StandardError:
        log.error('gl.reshape', exc_info=True)

def getMousePos():
    """
    Get mouse position relative to rendering canvas. Returns None if mouse is
    outside canvas.
    """
    return G.canvas.getMousePos()

def drawBegin():
    # clear the screen & depth buffer
    glClearColor(G.clearColor[0], G.clearColor[1], G.clearColor[2], G.clearColor[3])
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

def drawEnd():
    pass

have_multisample = None
have_activeTexture = None

def A(*args):
    if len(args) > 0 and hasattr(args[0], '__iter__'): # Iterable as argument
        if len(args) == 1:
            return np.array(list(args), dtype=np.float32)
        else:
            # Flatten arguments into one list
            l = list(args[0])
            for e in args[1:]:
                if hasattr(e, '__iter__'):
                    l.extend(e)
                else:
                    l.append(e)
            return np.array(l, dtype=np.float32)
    return np.array(list(args), dtype=np.float32)

def OnInit():
    try:
        # Start with writing relevant info to the debug dump in case stuff goes
        # wrong at a later time
        debugdump.dump.appendGL()
        debugdump.dump.appendMessage("GL.VENDOR: " + glGetString(GL_VENDOR))
        debugdump.dump.appendMessage("GL.RENDERER: " + glGetString(GL_RENDERER))
        debugdump.dump.appendMessage("GL.VERSION: " + glGetString(GL_VERSION))
        debugdump.dump.appendMessage("GLSL.VERSION: " + Shader.glslVersionStr())
    except Exception as e:
        log.error("Failed to write GL debug info to debug dump: %s", format(str(e)))

    global have_multisample
    if G.args.get('nomultisampling', False):
        have_multisample = False
    else:
        have_multisample = glInitMultisampleARB()

    try:
        # Number of samples is setup in the QGLWidget context
        nb_samples = glGetInteger(OpenGL.GL.ARB.multisample.GL_SAMPLES_ARB)
        debugdump.dump.appendMessage("GL.EXTENSION: GL_ARB_multisample %s (%sx samples)" % ("enabled" if have_multisample else "not available", nb_samples))
    except Exception as e:
        log.error("Failed to write GL debug info to debug dump: %s", format(str(e)))

    global have_activeTexture
    have_activeTexture = bool(glActiveTexture)

    global MAX_TEXTURE_UNITS
    if have_activeTexture:
        MAX_TEXTURE_UNITS = glGetInteger(GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS)
    else:
        MAX_TEXTURE_UNITS = 1

    # Set global scene ambient
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, A(0.0, 0.0, 0.0, 1.0))

    # Lights and materials
    lightPos = A( -10.99, 20.0, 20.0, 1.0)  # Light - Position
    ambientLight =  A(0.0, 0.0, 0.0, 1.0)   # Light - Ambient Values
    diffuseLight =  A(1.0, 1.0, 1.0, 1.0)   # Light - Diffuse Values
    specularLight = A(1.0, 1.0, 1.0, 1.0)   # Light - Specular Values

    MatAmb = A(0.11, 0.11, 0.11, 1.0)       # Material - Ambient Values
    MatDif = A(1.0, 1.0, 1.0, 1.0)          # Material - Diffuse Values
    MatSpc = A(0.2, 0.2, 0.2, 1.0)          # Material - Specular Values
    MatShn = A(10.0,)                       # Material - Shininess
    MatEms = A(0.0, 0.0, 0.0, 1.0)          # Material - Emission Values

    glEnable(GL_DEPTH_TEST)                                  # Hidden surface removal
    # glEnable(GL_CULL_FACE)                                   # Inside face removal
    # glEnable(GL_ALPHA_TEST)
    # glAlphaFunc(GL_GREATER, 0.0)
    glDisable(GL_DITHER)
    glEnable(GL_LIGHTING)                                    # Enable lighting
    # TODO set light properties based on selected scene
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLight)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLight)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specularLight)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
    glLightModeli(GL_LIGHT_MODEL_COLOR_CONTROL, GL_SEPARATE_SPECULAR_COLOR) #  If we enable this, we have stronger specular highlights
    glMaterialfv(GL_FRONT, GL_AMBIENT, MatAmb)               # Set Material Ambience
    glMaterialfv(GL_FRONT, GL_DIFFUSE, MatDif)               # Set Material Diffuse
    glMaterialfv(GL_FRONT, GL_SPECULAR, MatSpc)              # Set Material Specular
    glMaterialfv(GL_FRONT, GL_SHININESS, MatShn)             # Set Material Shininess
    glMaterialfv(GL_FRONT, GL_EMISSION, MatEms)              # Set Material Emission
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)     # Vertex colors affect materials (lighting is enabled)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)   # Vertex colors affect ambient and diffuse of material
    # glEnable(GL_TEXTURE_2D)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # Activate and specify pointers to vertex and normal array
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glEnableClientState(GL_VERTEX_ARRAY)
    if have_multisample:
        glEnable(GL_MULTISAMPLE)
        #glSampleCoverage(1.0, GL_FALSE)
        # TODO probably not needed, is used for GL_SAMPLE_COVERAGE, which we do not use (do not confuse with GL_SAMPLE_ALPHA_TO_COVERAGE)
        #glSampleCoverageARB(1.0, GL_FALSE)  # TODO flip mask each time

    global TEX_NOT_FOUND
    TEX_NOT_FOUND = getTexture(NOTFOUND_TEXTURE)
    if TEX_NOT_FOUND in (None, False):
        log.error('Unable to load texture %s, this might cause errors.', NOTFOUND_TEXTURE)

def OnExit():
    # Deactivate the pointers to vertex and normal array
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)
    # glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    log.message("Exit from event loop\n")

def setSceneLighting(scene):
    """
    Set lighting based on a scene config.
    """
    # Set global scene ambient
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, A(scene.environment.ambience, 1.0))

    # TODO support skybox

    # Set lights (OpenGL fixed function supports up to 8 lights)
    for lIdx in range(8):
        if lIdx < len(scene.lights):
            # All lights are simple point lights (only basic parameters)
            light = scene.lights[lIdx]

            lightPos = A(light.position, 1.0)          # Light - Position
            diffuseLight = A(light.color, 1.0)         # Light - Diffuse
            specularLight = A(light.specular, 1.0)     # Light - Specular
            # Always force ambient value of light off (only using global ambient)
            ambientLight =  A(0.0, 0.0, 0.0, 1.0)      # Light - Ambient

            glLightfv(GL_LIGHT0 + lIdx, GL_POSITION, lightPos)
            glLightfv(GL_LIGHT0 + lIdx, GL_DIFFUSE, diffuseLight)
            glLightfv(GL_LIGHT0 + lIdx, GL_SPECULAR, specularLight)
            glLightfv(GL_LIGHT0 + lIdx, GL_AMBIENT, ambientLight)

            glEnable(GL_LIGHT0 + lIdx)
        else:
            glDisable(GL_LIGHT0 + lIdx)

def cameraPosition(camera, eye):
    if not camera.updated:
        camera.updateCamera()
        camera.updated = True
    proj, mv = camera.getMatrices(eye)
    glMatrixMode(GL_PROJECTION)
    glLoadMatrixd(np.ascontiguousarray(proj.T))
    glMatrixMode(GL_MODELVIEW)
    glLoadMatrixd(np.ascontiguousarray(mv.T))

def transformObject(obj):
    camera = G.cameras[obj.cameraMode]
    human = G.app.selectedHuman
    m = camera.getModelMatrix(obj)
    glMultMatrixd(np.ascontiguousarray(m.T))

def drawMesh(obj):
    if not obj.visibility:
        return

    if G.args.get('fullloggingopengl', False):
        log.debug("Rendering mesh %s", obj.name)

    glDepthFunc(GL_LEQUAL)

    # Transform the current object
    glPushMatrix()
    transformObject(obj)

    glColor3f(1.0, 1.0, 1.0)

    useShader = obj.shader and obj.solid and not obj.shadeless

    if not useShader:
        if obj.isTextured and obj.texture and obj.solid:
            # Bind texture for fixed function shading
            if have_activeTexture:
                glActiveTexture(GL_TEXTURE0)
            glEnable(GL_TEXTURE_2D)
            tex = getTexture(obj.texture)
            if tex not in (False, None):
                glBindTexture(GL_TEXTURE_2D, tex.textureId)
            else:
                glBindTexture(GL_TEXTURE_2D, TEX_NOT_FOUND.textureId)
            if have_activeTexture:
                for gl_tex_idx in xrange(GL_TEXTURE0 + 1, GL_TEXTURE0 + MAX_TEXTURE_UNITS):
                    glActiveTexture(gl_tex_idx)
                    glBindTexture(GL_TEXTURE_2D, 0)
                    glDisable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_1D, 0)
                    glDisable(GL_TEXTURE_1D)
        else:
            # Disable all textures (when in fixed function textureless shading mode)
            for gl_tex_idx in xrange(GL_TEXTURE0, GL_TEXTURE0 + MAX_TEXTURE_UNITS):
                if have_activeTexture:
                    glActiveTexture(gl_tex_idx)
                glBindTexture(GL_TEXTURE_2D, 0)
                glDisable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_1D, 0)
                glDisable(GL_TEXTURE_1D)

    if obj.nTransparentPrimitives:
        # TODO not needed for alpha-to-coverage rendering (it's face order independent)
        # TODO for other pipelines/older harware better to statically sort faces of hair meshes around BBox center
        #obj.sortFaces()
        pass

    # Fill the array pointers with object mesh data
    if obj.hasUVs:
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glTexCoordPointer(2, GL_FLOAT, 0, obj.UVs)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, obj.verts)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 0, obj.norms)
    glEnableClientState(GL_COLOR_ARRAY)
    if not useShader and obj.solid:
        # Vertex colors should be multiplied with the diffuse material value, also for fixed function
        # (with the exception of wireframe rendering)
        glColorPointer(4, GL_UNSIGNED_BYTE, 0, obj.color_diff)
    else:
        glColorPointer(4, GL_UNSIGNED_BYTE, 0, obj.color)

    # Disable lighting if the object is shadeless
    if obj.shadeless:
        glDisable(GL_LIGHTING)
    else:
        glEnable(GL_LIGHTING)

    if obj.cull:
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK if obj.cull > 0 else GL_FRONT)
    else:
        glDisable(GL_CULL_FACE)

    if obj.solid:
        # Set material properties
        mat = obj.material
        MatAmb = A(mat.ambientColor.values, 1.0)         # Material - Ambient
        MatDif = A(mat.diffuseColor.values, mat.opacity) # Material - Diffuse
        MatSpc = A(mat.specularColor.values, 1.0)        # Material - Specular
        MatShn = A(128 * mat.shininess)                  # Material - Shininess
        MatEms = A(mat.emissiveColor.values, 1.0)        # Material - Emission
    else:
        # Wireframe
        # Set some default material properties
        MatAmb = A(0.11, 0.11, 0.11, 1.0)       # Material - Ambient Values
        MatDif = A(1.0, 1.0, 1.0, 1.0)          # Material - Diffuse Values
        MatSpc = A(0.2, 0.2, 0.2, 1.0)          # Material - Specular Values
        MatShn = A(10.0,)                       # Material - Shininess
        MatEms = A(0.0, 0.0, 0.0, 1.0)          # Material - Emission Values

    glMaterialfv(GL_FRONT, GL_AMBIENT, MatAmb)          # Set Material Ambience
    glMaterialfv(GL_FRONT, GL_DIFFUSE, MatDif)          # Set Material Diffuse
    glMaterialfv(GL_FRONT, GL_SPECULAR, MatSpc)         # Set Material Specular
    glMaterialfv(GL_FRONT, GL_SHININESS, MatShn)        # Set Material Shininess
    glMaterialfv(GL_FRONT, GL_EMISSION, MatEms)         # Set Material Emission

    if obj.useVertexColors:
        # Vertex colors affect materials (lighting is enabled)
        glEnable(GL_COLOR_MATERIAL)
        # Vertex colors affect diffuse of material
        glColorMaterial(GL_FRONT, GL_DIFFUSE)
    else:
        glDisable(GL_COLOR_MATERIAL)

    # Enable the shader if the driver supports it and there is a shader assigned
    if useShader:
        glUseProgram(obj.shader)

        # Set custom attributes
        if obj.shaderObj.requiresVertexTangent():
            glVertexAttribPointer(obj.shaderObj.vertexTangentAttrId, 4, GL_FLOAT, GL_FALSE, 0, obj.tangents)
            glEnableVertexAttribArray(obj.shaderObj.vertexTangentAttrId)

        # TODO
        # This should be optimized, since we only need to do it when it's changed
        # Validation should also only be done when it is set
        obj.shaderObj.setUniforms(obj.shaderParameters)
    elif Shader.supported():
        glUseProgram(0)

    # draw the mesh
    if not obj.solid:
        # Wireframe drawing
        glEnable(GL_COLOR_MATERIAL)
        glDisableClientState(GL_COLOR_ARRAY)
        glColor3f(0.0, 0.0, 0.0)
        glDisable(GL_LIGHTING)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)   # Vertex colors affect ambient and diffuse of material
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        glDrawElements(g_primitiveMap[obj.vertsPerPrimitive-1], obj.primitives.size, GL_UNSIGNED_INT, obj.primitives)

        glEnableClientState(GL_COLOR_ARRAY)
        glEnable(GL_LIGHTING)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)

        glDrawElements(g_primitiveMap[obj.vertsPerPrimitive-1], obj.primitives.size, GL_UNSIGNED_INT, obj.primitives)

        glDisable(GL_POLYGON_OFFSET_FILL)
        glDisable(GL_COLOR_MATERIAL)
    elif obj.nTransparentPrimitives:
        if have_multisample and obj.alphaToCoverage:
            # Enable alpha-to-coverage (also called CSAA)
            # using the multisample buffer for alpha to coverage disables its use for MSAA (anti-aliasing)
            glEnable(GL_SAMPLE_ALPHA_TO_COVERAGE)
            #glEnable(GL_SAMPLE_ALPHA_TO_ONE)  # Enable this if transparent objects are too transparent
            glDisable(GL_BLEND) # Disable alpha blending
        else:
            glDepthMask(GL_FALSE)
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GREATER, 0.0)
        glDrawElements(g_primitiveMap[obj.vertsPerPrimitive-1], obj.primitives.size, GL_UNSIGNED_INT, obj.primitives)
        glDisable(GL_ALPHA_TEST)
        if have_multisample and obj.alphaToCoverage:
            glDisable(GL_SAMPLE_ALPHA_TO_COVERAGE)
            glEnable(GL_BLEND)
        else:
            glDepthMask(GL_TRUE)
    elif obj.depthless:
        glDepthMask(GL_FALSE)
        glDisable(GL_DEPTH_TEST)
        glDrawElements(g_primitiveMap[obj.vertsPerPrimitive-1], obj.primitives.size, GL_UNSIGNED_INT, obj.primitives)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
    else:
        glDrawElements(g_primitiveMap[obj.vertsPerPrimitive-1], obj.primitives.size, GL_UNSIGNED_INT, obj.primitives)

    if obj.solid and not obj.nTransparentPrimitives:
        glDisableClientState(GL_COLOR_ARRAY)
        for i, (start, count) in enumerate(obj.groups):
            color = obj.gcolor(i)
            if color is None or np.all(color[:3] == 255):
                continue
            glColor4ub(*color)
            indices = obj.primitives[start:start+count,:]
            glDrawElements(g_primitiveMap[obj.vertsPerPrimitive-1], indices.size, GL_UNSIGNED_INT, indices)
        glEnableClientState(GL_COLOR_ARRAY)

    # Disable the shader if the driver supports it and there is a shader assigned
    if useShader:
        glUseProgram(0)

    # Restore state defaults
    if have_activeTexture:
        glActiveTexture(GL_TEXTURE0)
    glDisable(GL_CULL_FACE)
    glColor3f(1.0, 1.0, 1.0)
    glColorMaterial(GL_FRONT, GL_DIFFUSE)

    if obj.useVertexColors:
        glDisable(GL_COLOR_MATERIAL)

    # Disable custom vertex arrays again
    if useShader and obj.shaderObj.requiresVertexTangent():
        glDisableVertexAttribArray(obj.shaderObj.vertexTangentAttrId)

    # Re-enable lighting if it was disabled
    glEnable(GL_LIGHTING)

    glColorMaterial(GL_FRONT, GL_DIFFUSE)

    if obj.isTextured and obj.texture and obj.solid:
        glDisable(GL_TEXTURE_2D)

    if obj.hasUVs:
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

    glPopMatrix()

def pickMesh(obj):
    if not obj.visibility:
        return
    if not obj.pickable:
        return

    # Transform the current object
    glPushMatrix()
    transformObject(obj)

    # Fill the array pointers with object mesh data
    glVertexPointer(3, GL_FLOAT, 0, obj.verts)
    glNormalPointer(GL_FLOAT, 0, obj.norms)

    # Use color to pick i
    glDisableClientState(GL_COLOR_ARRAY)

    # Disable lighting
    glDisable(GL_LIGHTING)

    if obj.cull:
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK if obj.cull > 0 else GL_FRONT)

    # draw the meshes
    for i, (start, count) in enumerate(obj.groups):
        glColor3ub(*obj.clrid(i))
        indices = obj.primitives[start:start+count,:]
        glDrawElements(g_primitiveMap[obj.vertsPerPrimitive-1], indices.size, GL_UNSIGNED_INT, indices)

    glDisable(GL_CULL_FACE)

    glEnable(GL_LIGHTING)
    glEnableClientState(GL_COLOR_ARRAY)

    glPopMatrix()

def drawOrPick(pickMode, obj):
    if pickMode:
        if hasattr(obj, 'pick'):
            obj.pick()
    else:
        if hasattr(obj, 'draw'):
            obj.draw()

_hasRenderToTexture = None
def hasRenderToTexture():
    global _hasRenderToTexture
    if _hasRenderToTexture is None:
        _hasRenderToTexture = all([
            bool(glGenFramebuffers), bool(glBindFramebuffer), bool(glFramebufferTexture2D)])
    return _hasRenderToTexture

def hasRenderSkin():
    return hasRenderToTexture()

_hasRenderToRenderbuffer = None
def hasRenderToRenderbuffer():
    global _hasRenderToRenderbuffer
    if _hasRenderToRenderbuffer is None:
        _hasRenderToRenderbuffer = all([
            bool(glGenRenderbuffers), bool(glBindRenderbuffer), bool(glRenderbufferStorage),
            bool(glGenFramebuffers), bool(glBindFramebuffer), bool(glFramebufferRenderbuffer)])
    return _hasRenderToRenderbuffer


def renderSkin(dst, vertsPerPrimitive, verts, index = None, objectMatrix = None,
               texture = None, UVs = None, textureMatrix = None,
               color = None, clearColor = None):

    if isinstance(dst, Texture):
        glBindTexture(GL_TEXTURE_2D, dst.textureId)
    elif isinstance(dst, Image):
        dst = Texture(image = dst)
    elif isinstance(dst, tuple):
        dimensions = dst
        dst = Texture(size = dimensions)
        if dst.width < dimensions[0] or dst.height < dimensions[1]:
            raise RuntimeError('Could not allocate render texture with dimensions: %s' % str(dst))
    else:
        raise RuntimeError('Unsupported destination: %r' % dst)

    width, height = dst.width, dst.height

    framebuffer = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
    glFramebufferTexture2D(GL_DRAW_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, dst.textureId, 0)
    glFramebufferTexture2D(GL_READ_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, dst.textureId, 0)

    if clearColor is not None:
        glClearColor(clearColor[0], clearColor[1], clearColor[2], clearColor[3])
        glClear(GL_COLOR_BUFFER_BIT)

    glVertexPointer(verts.shape[-1], GL_FLOAT, 0, verts)

    if texture is not None and UVs is not None:
        if isinstance(texture, Image):
            tex = Texture()
            tex.loadImage(texture)
            texture = tex
        if isinstance(texture, Texture):
            texture = texture.textureId
        glEnable(GL_TEXTURE_2D)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexCoordPointer(UVs.shape[-1], GL_FLOAT, 0, UVs)

    if color is not None:
        glColorPointer(color.shape[-1], GL_UNSIGNED_BYTE, 0, color)
        glEnableClientState(GL_COLOR_ARRAY)
    else:
        glDisableClientState(GL_COLOR_ARRAY)
        glColor4f(1, 1, 1, 1)

    glDisableClientState(GL_NORMAL_ARRAY)
    glDisable(GL_LIGHTING)

    glDepthMask(GL_FALSE)
    glDisable(GL_DEPTH_TEST)
    # glDisable(GL_CULL_FACE)

    glPushAttrib(GL_VIEWPORT_BIT)
    glViewport(0, 0, width, height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    if objectMatrix is not None:
        glLoadTransposeMatrixd(objectMatrix)
    else:
        glLoadIdentity()

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 1, 0, 1, -100, 100)

    if textureMatrix is not None:
        glMatrixMode(GL_TEXTURE)
        glPushMatrix()
        glLoadTransposeMatrixd(textureMatrix)

    if index is not None:
        glDrawElements(g_primitiveMap[vertsPerPrimitive-1], index.size, GL_UNSIGNED_INT, index)
    else:
        glDrawArrays(g_primitiveMap[vertsPerPrimitive-1], 0, verts[:,:,0].size)

    if textureMatrix is not None:
        glMatrixMode(GL_TEXTURE)
        glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glPopAttrib()

    glEnable(GL_DEPTH_TEST)
    glDepthMask(GL_TRUE)

    glEnable(GL_LIGHTING)
    glEnableClientState(GL_NORMAL_ARRAY)

    glEnableClientState(GL_COLOR_ARRAY)

    glDisable(GL_TEXTURE_2D)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)

    surface = np.empty((height, width, 4), dtype = np.uint8)
    glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, surface)
    surface = Image(data = np.ascontiguousarray(surface[::-1,:,:3]))

    glFramebufferTexture2D(GL_DRAW_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, 0, 0)
    glFramebufferTexture2D(GL_READ_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, 0, 0)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glDeleteFramebuffers(np.array([framebuffer]))
    glBindTexture(GL_TEXTURE_2D, 0)

    return surface

def renderToBuffer(width, height, productionRender = True):
    """
    Perform offscreen render and return the pixelbuffer.
    Verify whether OpenGL drivers support renderbuffers using 
    hasRenderToRenderbuffer().
    """
    # Create and bind framebuffer
    framebuffer = glGenFramebuffers(1)
    #glBindFramebuffer(GL_DRAW_FRAMEBUFFER, framebuffer)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

    # Now that framebuffer is bound, verify whether dimensions are within max supported dimensions
    maxWidth, maxHeight = glGetInteger(GL_MAX_VIEWPORT_DIMS)
    aspect = float(height) / width
    width = min(width, maxWidth)
    height = min(height, maxHeight)
    # Maintain original aspect ratio
    if aspect * width < height:
        height = int(aspect * width)
    else:
        width = int(height / aspect)

    # Create and bind renderbuffers
    renderbuffer = glGenRenderbuffers(1)    # We need a renderbuffer for both color and depth
    depthRenderbuffer = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, renderbuffer)
    global have_multisample
    if have_multisample:
        glRenderbufferStorageMultisample(GL_RENDERBUFFER, 4, GL_RGBA, width, height)
    else:
        glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA, width, height)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, renderbuffer)

    glBindRenderbuffer(GL_RENDERBUFFER, depthRenderbuffer)
    if have_multisample:
        glRenderbufferStorageMultisample(GL_RENDERBUFFER, 4, GL_DEPTH_COMPONENT16, width, height)
    else:
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT16, width, height)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthRenderbuffer)

    # TODO check with glCheckFramebufferStatus ?
    if not glCheckFramebufferStatus(GL_FRAMEBUFFER):
        pass # TODO

    # Adapt camera projection matrix to framebuffer size
    oldWidth = G.windowWidth
    oldHeight = G.windowHeight
    G.windowWidth = width
    G.windowHeight = height
    glPushAttrib(GL_VIEWPORT_BIT)
    glViewport(0, 0, width, height)

    # Neutral background color
    oldClearColor = G.clearColor
    G.clearColor = (0.5,0.5,0.5, 1)

    # Draw scene as usual
    draw(productionRender)

    G.clearColor = oldClearColor

    if have_multisample:
        # If we have drawn to a multisample renderbuffer, we need to transfer it to a simple buffer to read it
        downsampledFramebuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_READ_FRAMEBUFFER, framebuffer)       # Multisampled FBO
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, downsampledFramebuffer) # Regular FBO
        regularRenderbuffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, regularRenderbuffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, regularRenderbuffer)
        glBlitFramebuffer(0, 0, width, height, 0, 0, width, height, GL_COLOR_BUFFER_BIT, GL_NEAREST)

        # Dealloc what we no longer need
        glDeleteFramebuffers(np.array([framebuffer]))
        framebuffer = downsampledFramebuffer
        del downsampledFramebuffer
        glDeleteRenderbuffers(1, np.array([renderbuffer]))
        renderbuffer = regularRenderbuffer
        del regularRenderbuffer

    # Read pixels
    surface = np.empty((height, width, 4), dtype = np.uint8)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
    glReadBuffer(GL_COLOR_ATTACHMENT0)
    glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, surface)

    surface = Image(data = np.ascontiguousarray(surface[::-1,:,[2,1,0]]))

    # Unbind frame buffer
    glDeleteFramebuffers(np.array([framebuffer]))
    glDeleteRenderbuffers(1, np.array([renderbuffer]))
    glDeleteRenderbuffers(1, np.array([depthRenderbuffer]))
    glBindRenderbuffer(GL_RENDERBUFFER, 0)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # Restore viewport dimensions to those of the window
    G.windowWidth = oldWidth
    G.windowHeight = oldHeight
    glPushAttrib(GL_VIEWPORT_BIT)
    glViewport(0, 0, oldWidth, oldHeight)

    return surface

def renderAlphaMask(width, height, productionRender = True):
    """
    Render alpha mask suiting a render to renderbufer, that can be used for
    compositing the produced render on a background.
    Verify whether OpenGL drivers support renderbuffers using 
    hasRenderToRenderbuffer().
    """
    # Create and bind framebuffer
    framebuffer = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

    # Now that framebuffer is bound, verify whether dimensions are within max supported dimensions
    maxWidth, maxHeight = glGetInteger(GL_MAX_VIEWPORT_DIMS)
    width = min(width, maxWidth)
    height = min(height, maxHeight)

    # Create and bind renderbuffers
    renderbuffer = glGenRenderbuffers(1)    # We need a renderbuffer for both color and depth
    depthRenderbuffer = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, renderbuffer)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA, width, height)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, renderbuffer)

    glBindRenderbuffer(GL_RENDERBUFFER, depthRenderbuffer)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT16, width, height)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthRenderbuffer)

    # TODO check with glCheckFramebufferStatus ?
    if not glCheckFramebufferStatus(GL_FRAMEBUFFER):
        pass # TODO

    # Adapt camera projection matrix to framebuffer size
    oldWidth = G.windowWidth
    oldHeight = G.windowHeight
    G.windowWidth = width
    G.windowHeight = height
    glPushAttrib(GL_VIEWPORT_BIT)
    glViewport(0, 0, width, height)

    # Transparent background color
    oldClearColor = G.clearColor
    G.clearColor = (0.5, 0.5, 0.5, 0)
    # Change blend func to accumulate alpha
    glBlendFunc(GL_ONE, GL_ONE)
    # Disable multisampling
    global have_multisample
    old_have_multisample = have_multisample
    have_multisample = False

    # Draw scene as usual
    draw(productionRender)

    # Restore rendering defaults
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    have_multisample = old_have_multisample
    G.clearColor = oldClearColor

    # Read pixels
    surface = np.empty((height, width, 4), dtype = np.uint8)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
    glReadBuffer(GL_COLOR_ATTACHMENT0)
    glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, surface)

    # Grayscale image of only alpha channel
    surface = Image(data = np.ascontiguousarray(surface[::-1,:,[3,3,3]]))

    # Unbind frame buffer
    glDeleteFramebuffers(np.array([framebuffer]))
    glDeleteRenderbuffers(1, np.array([renderbuffer]))
    glDeleteRenderbuffers(1, np.array([depthRenderbuffer]));
    glBindRenderbuffer(GL_RENDERBUFFER, 0)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # Restore viewport dimensions to those of the window
    G.windowWidth = oldWidth
    G.windowHeight = oldHeight
    glPushAttrib(GL_VIEWPORT_BIT)
    glViewport(0, 0, oldWidth, oldHeight)

    return surface

def drawMeshes(pickMode, productionRender = False):
    if G.world is None:
        return

    cameraMode = None
    # Update only the model camera (leave the static one)
    G.cameras[0].updated = False

    # Draw all objects contained by G.world
    for obj in sorted(G.world, key = (lambda obj: obj.priority)):
        if productionRender and obj.excludeFromProduction:
            continue
        camera = G.cameras[obj.cameraMode]
        if camera.stereoMode:
            glColorMask(GL_TRUE, GL_FALSE, GL_FALSE, GL_TRUE) # Red
            cameraPosition(camera, 1)
            drawOrPick(pickMode, obj)
            glClear(GL_DEPTH_BUFFER_BIT)
            glColorMask(GL_FALSE, GL_TRUE, GL_TRUE, GL_TRUE) # Cyan
            cameraPosition(camera, 2)
            drawOrPick(pickMode, obj)
            # To prevent the GUI from overwritting the red model, we need to render it again in the z-buffer
            glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE) # None, only z-buffer
            cameraPosition(camera, 1)
            drawOrPick(pickMode, obj)
            glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE) # All
            cameraMode = None
        else:
            if cameraMode != obj.cameraMode:
                cameraPosition(camera, 0)
                cameraMode = obj.cameraMode
            drawOrPick(pickMode, obj)

def _draw(productionRender = False):
    drawBegin()
    drawMeshes(False, productionRender)
    drawEnd()

def draw(productionRender = False):
    try:
        if profiler.active():
            profiler.accum('_draw()', globals(), locals())
        else:
            _draw(productionRender)
        return True
    except StandardError:
        log.error('gl.draw', exc_info=True)
        return False

def renderToCanvas():
    if draw():
        G.canvas.swapBuffers()
        # Indicate that picking buffer is out of sync with rendered frame (deferred update)
        markPickingBufferDirty()
