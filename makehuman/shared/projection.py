#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers, Glynn Clements

**Copyright(c):**      MakeHuman Team 2001-2017

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehuman.org).

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


Abstract
--------

Methods that help create texture maps by projection on the model.
Supported creators:
Light map creator
Image map creator
UV map creator

"""

import numpy as np
from core import G
import mh
import log
import matrix
import image_operations
from progress import Progress

def v4to3(v):
    v = np.asarray(v)
    return v[:3,0] / v[3:,0]

def vnormalize(v):
    return v / np.sqrt(np.sum(v ** 2, axis=-1))[...,None]

class Shader(object):
    pass

class UvAlphaShader(Shader):
    def __init__(self, dst, texture, uva):
        self.dst = dst
        self.texture = texture
        self.size = np.array([texture.width, texture.height])
        self.uva = uva

    def shade(self, i, xy, uvw):
        dst = self.dst.data[xy[...,1],xy[...,0]]
        uva = np.sum(self.uva[i][None,None,:,:] * uvw[...,[1,2,0]][:,:,:,None], axis=2)
        ix = np.floor(uva[:,:,:2] * self.size[None,None,:]).astype(int)
        ix = np.minimum(ix, self.size - 1)
        ix = np.maximum(ix, 0)
        src = self.texture.data[ix[...,1], ix[...,0]]
        a = uva[:,:,2]
        return a[:,:,None] * (src.astype(float) - dst) + dst

class ColorShader(Shader):
    def __init__(self, colors):
        self.colors = colors

    def shade(self, i, xy, uvw):
        return np.sum(self.colors[i][None,None,:,:] * uvw[...,[1,2,0]][:,:,:,None], axis=2)

class MaskShader(Shader):
    def __init__(self, color=[255,255,255,255]):
        self.color = color

    def shade(self, i, xy, uvw):
        shape = list(xy.shape)[:-1]
        return np.tile(self.color, shape).reshape(shape + [4])

def RasterizeTriangles(dst, coords, shader):
    """
    Software rasterizer.
    """
    delta = coords - coords[:,[1,2,0],:]
    perp = np.concatenate((delta[:,:,1,None], -delta[:,:,0,None]), axis=-1)
    dist = np.sum(perp[:,0,:] * delta[:,2,:], axis=-1)
    perp /= dist[:,None,None]
    base = np.sum(perp * coords, axis=-1)

    cmin = np.floor(np.amin(coords, axis=1)).astype(int)
    cmax = np.ceil( np.amax(coords, axis=1)).astype(int)

    minx = cmin[:,0]
    maxx = cmax[:,0]
    miny = cmin[:,1]
    maxy = cmax[:,1]

    progress = Progress(len(coords), None).HighFrequency(200)
    for i in xrange(len(coords)):
        ixy = np.mgrid[miny[i]:maxy[i],minx[i]:maxx[i]].transpose([1,2,0])[:,:,::-1]
        xy = ixy + 0.5
        uvw = np.sum(perp[i,None,None,:,:] * xy[:,:,None,:], axis=-1) - base[i,None,None,:]
        mask = np.all(uvw > 0, axis=-1)
        col = shader.shade(i, ixy, uvw)
        # log.debug('dst: %s', dst.data[miny[i]:maxy[i],minx[i]:maxx[i]].shape)
        # log.debug('src: %s', col.shape)
        dst.data[miny[i]:maxy[i],minx[i]:maxx[i],:][mask] = col[mask]
        progress.step()

def getCamera(mesh):
    ex, ey, ez = G.app.modelCamera.eye
    eye = np.matrix([ex,ey,ez,1]).T
    fx, fy, fz = G.app.modelCamera.focus
    focus = np.matrix([fx,fy,fz,1]).T
    transform = mesh.transform.I
    eye = v4to3(transform * eye)
    focus = v4to3(transform * focus)
    camera = vnormalize(eye - focus)
    # log.debug('%s %s %s', eye, focus, camera)
    return camera

def getFaces(mesh):
    group_mask = np.ones(len(mesh._faceGroups), dtype=bool)
    for g in mesh._faceGroups:
        if g.name.startswith('joint') or g.name.startswith('helper'):
            group_mask[g.idx] = False
    faces = np.argwhere(group_mask[mesh.group])[...,0]
    return faces

def mapImageSoft(srcImg, mesh, leftTop, rightBottom):
    progress = Progress() (0)
    dstImg = mh.Image(G.app.selectedHuman.getTexture())

    dstW = dstImg.width
    dstH = dstImg.height

    srcImg = srcImg.convert(dstImg.components)

    camera = getCamera(mesh)
    faces = getFaces(mesh)

    # log.debug('matrix: %s', G.app.modelCamera.getConvertToScreenMatrix())

    progress(0.05)
    texco = np.asarray([0,dstH])[None,None,:] + mesh.texco[mesh.fuvs[faces]] * np.asarray([dstW,-dstH])[None,None,:]
    matrix_ = np.asarray(G.app.modelCamera.getConvertToScreenMatrix(mesh))
    coord = np.concatenate((mesh.coord[mesh.fvert[faces]], np.ones((len(faces),4,1))), axis=-1)
    # log.debug('texco: %s, coord: %s', texco.shape, coord.shape)
    coord = np.sum(matrix_[None,None,:,:] * coord[:,:,None,:], axis = -1)
    # log.debug('coord: %s', coord.shape)
    coord = coord[:,:,:2] / coord[:,:,3:]
    progress(0.1)
    # log.debug('coord: %s', coord.shape)
    # log.debug('coords: %f-%f, %f-%f',
    #           np.amin(coord[...,0]), np.amax(coord[...,0]),
    #           np.amin(coord[...,1]), np.amax(coord[...,1]))
    # log.debug('rect: %s %s', leftTop, rightBottom)
    coord -= np.asarray([leftTop[0], leftTop[1]])[None,None,:]
    coord /= np.asarray([rightBottom[0] - leftTop[0], rightBottom[1] - leftTop[1]])[None,None,:]
    alpha = np.sum(mesh.vnorm[mesh.fvert[faces]] * camera[None,None,:], axis=-1)
    alpha = np.maximum(0, alpha)
    # alpha[...] = 1 # debug
    # log.debug('alpha: %s', alpha.shape)
    # log.debug('coords: %f-%f, %f-%f',
    #           np.amin(coord[...,0]), np.amax(coord[...,0]),
    #           np.amin(coord[...,1]), np.amax(coord[...,1]))
    progress(0.15)
    uva = np.concatenate((coord, alpha[...,None]), axis=-1)
    # log.debug('uva: %s', uva.shape)
    valid = np.any(alpha >= 0, axis=1)
    # log.debug('valid: %s', valid.shape)
    texco = texco[valid,:,:]
    uva = uva[valid,:,:]

    # log.debug('%s %s', texco.shape, uva.shape)
    # log.debug('src: %s, dst: %s', srcImg.data.shape, dstImg.data.shape)

    log.debug("mapImage: begin render")

    progress(0.2, 0.6)
    RasterizeTriangles(dstImg, texco[:,[0,1,2],:], UvAlphaShader(dstImg, srcImg, uva[:,[0,1,2],:]))
    progress(0.6, 0.99)
    RasterizeTriangles(dstImg, texco[:,[2,3,0],:], UvAlphaShader(dstImg, srcImg, uva[:,[2,3,0],:]))
    progress.finish()

    log.debug("mapImage: end render")

    return dstImg

def mapImageGL(srcImg, mesh, leftTop, rightBottom):
    progress = Progress() (0)
    log.debug("mapImageGL: 1")

    dstImg = G.app.selectedHuman.meshData.object3d.textureTex

    dstW = dstImg.width
    dstH = dstImg.height

    left, top = leftTop
    right, bottom = rightBottom

    camera = getCamera(mesh)

    coords = mesh.r_texco

    texmat = G.app.modelCamera.getConvertToScreenMatrix(mesh)
    texmat = matrix.scale((1/(right - left), 1/(top - bottom), 1)) * matrix.translate((-left, -bottom, 0)) * texmat
    texmat = np.asarray(texmat)

    texco = mesh.r_coord

    alpha = np.sum(mesh.r_vnorm * camera[None,:], axis=-1)
    alpha = np.maximum(alpha, 0)
    color = (np.array([0, 0, 0, 0])[None,...] + alpha[...,None]) * 255

    color = np.ascontiguousarray(color, dtype=np.uint8)
    texco = np.ascontiguousarray(texco, dtype=np.float32)

    progress(0.5, 0.99)
    result = mh.renderSkin(dstImg, mesh.vertsPerPrimitive, coords, index = mesh.index,
                           texture = srcImg, UVs = texco, textureMatrix = texmat,
                           color = color, clearColor = None)

    progress(1)
    return result

def mapImage(imgMesh, mesh, leftTop, rightBottom):
    if mh.hasRenderSkin():
        try:
            return mapImageGL(imgMesh.mesh.object3d.textureTex, mesh, leftTop, rightBottom)
        except Exception, e:
            log.debug(e)
            log.debug("Hardware skin rendering failed, falling back to software render.")
            return mapImageSoft(mh.Image(imgMesh.getTexture()), mesh, leftTop, rightBottom)
    else:
        return mapImageSoft(mh.Image(imgMesh.getTexture()), mesh, leftTop, rightBottom)


'''fixSeams

A function for removing UV seams from projected images.

When creating images through projection, interference with the
limits of the UV map tend to produce dark seams on the mesh
along the lines that define the limits. Using this procedure,
one can repair these seams by UV mask aided post-processing.

Pass the image to be fixed in the 'img' parameter, and the mesh
from which the UV mask will be projected in the 'mesh' parameter.
If you already have a mask projected, you can pass it in place
of the 'mesh' parameter. The function will additionally return
the new expanded mask.

The seam fix can be expanded furtherly in case the projected
image is intented for blurring or other sampling operation
affected by pixels outside the UV border, by adjusting the
'border' parameter.

'''

def fixSeams(img, mesh, border = 1):
    from image_operations import Image, expand
    mask = mesh if isinstance(mesh, Image) else mapMask(img.size, mesh)
    img, mask = expand(img, mask, border)
    return (img, mask) if isinstance(mesh, Image) else img

def mapLightingSoft(lightpos = (-10.99, 20.0, 20.0), mesh = None, res = (1024, 1024), border = 1):
    """
    Create a lightmap for the selected human (software renderer).
    """
    progress = Progress() (0)

    if mesh is None:
        mesh = G.app.selectedHuman.mesh

    W = res[0]
    H = res[1]

    dstImg = mh.Image(width=W, height=H, components=4)
    dstImg.data[...] = 0

    delta = lightpos - mesh.coord
    ld = vnormalize(delta)
    del delta
    s = np.sum(ld * mesh.vnorm, axis=-1)
    del ld
    s = np.maximum(0, np.minimum(255, (s * 256))).astype(np.uint8)
    mesh.color[...,:3] = s[...,None]
    mesh.color[...,3] = 255
    del s

    faces = getFaces(mesh)

    coords = np.asarray([0,H])[None,None,:] + mesh.texco[mesh.fuvs[faces]] * np.asarray([W,-H])[None,None,:]
    colors = mesh.color[mesh.fvert[faces]]
    # log.debug("mapLighting: %s %s %s", faces.shape, coords.shape, colors.shape)

    log.debug("mapLighting: begin render")

    progress(0.1, 0.5)
    RasterizeTriangles(dstImg, coords[:,[0,1,2],:], ColorShader(colors[:,[0,1,2],:]))
    progress(0.5, 0.9)
    RasterizeTriangles(dstImg, coords[:,[2,3,0],:], ColorShader(colors[:,[2,3,0],:]))

    progress(0.9, 0.99)
    dstImg = fixSeams(dstImg, mesh, border)

    log.debug("mapLighting: end render")

    mesh.setColor([255, 255, 255, 255])

    progress.finish()
    return dstImg

def mapLightingGL(lightpos = (-10.99, 20.0, 20.0), mesh = None, res = (1024, 1024), border = 1):
    """
    Create a lightmap for the selected human (hardware accelerated).
    """
    progress = Progress() (0)

    if mesh is None:
        mesh = G.app.selectedHuman.mesh

    W = res[0]
    H = res[1]

    delta = lightpos - mesh.coord
    ld = vnormalize(delta)
    del delta
    s = np.sum(ld * mesh.vnorm, axis=-1)
    del ld
    s = np.maximum(0, np.minimum(255, (s * 256))).astype(np.uint8)
    mesh.color[...,:3] = s[...,None]
    mesh.color[...,3] = 255
    del s

    progress(0.1)
    mesh.markCoords(colr = True)
    mesh.update()

    coords = mesh.r_texco
    colors = mesh.r_color

    progress(0.2, 0.5)
    dstImg = mh.renderSkin((W, H), mesh.vertsPerPrimitive, coords, index = mesh.index,
                           color = colors, clearColor = (0, 0, 0, 0))

    progress(0.5, 0.99)
    dstImg = fixSeams(dstImg, mesh, border)

    mesh.setColor([255, 255, 255, 255])

    log.debug('mapLightingGL: %s', dstImg.data.shape)

    progress(1)
    return dstImg

def mapLighting(lightpos = (-10.99, 20.0, 20.0), mesh = None, res = (1024, 1024), border = 1):
    """
    Bake lightmap for human from one light.
    Uses OpenGL hardware acceleration if the necessary OGL features are
    available, otherwise uses a slower software rasterizer.
    """
    if mh.hasRenderSkin():
        try:
            return mapLightingGL(lightpos, mesh, res, border)
        except Exception, e:
            log.debug(e)
            log.debug("Hardware skin rendering failed, falling back to software render.")
            return mapLightingSoft(lightpos, mesh, res, border)
    else:
        return mapLightingSoft(lightpos, mesh, res, border)

def mapSceneLighting(scn, object = None, res = (1024, 1024), border = 1):
    """
    Create a lightmap for a scene with one or multiple lights.
    This happens by adding the lightmaps produced by each light,
    plus the scene ambience.
    """

    if object is None:
        object = G.app.selectedHuman

    objrot = G.app.modelCamera.getRotation()
    def calcLightPos(light):
        return tuple(
            matrix.transform3(
                matrix.rotx(-objrot[0]) *
                matrix.roty(-objrot[1]) *
                matrix.rotz(-objrot[2]),
                light.position))

    def getLightmap(light):
        lmap = mapLighting(calcLightPos(light), object.mesh, res, border)
        return image_operations.Image(data = lmap.data * light.color.values)

    progress = Progress(1 + len(scn.lights))

    # Ambience
    lmap = image_operations.colorAsImage(
        (scn.environment.ambience * object.material.diffuseColor).values, None, *res)
    if (object.material.shaderConfig['ambientOcclusion']
        and not object.material.aoMapTexture is None):
        aomap = image_operations.Image(data = object.material.aoMapTexture)
        aomap = image_operations.resized(aomap, *lmap.size)
        lmap = image_operations.multiply(lmap, image_operations.mix(
            aomap, image_operations.getWhite(lmap), object.material.aoMapIntensity))
    progress.step()

    # Lights
    if scn.lights:
        amb = lmap
        lmap = getLightmap(scn.lights[0]).data
        progress.step()
        for light in scn.lights[1:]:
            lmap = image_operations.mixData(lmap, getLightmap(light).data, 1, 1)
            progress.step()
        lmap = image_operations.Image(data = lmap)
        if len(scn.lights) > 1:
            lmap = image_operations.normalize(lmap)

        # Ambience calculation function: lmap = lmap + (1 - lmap) * amb
        lmap = image_operations.mix(
            lmap, image_operations.multiply(
                image_operations.invert(lmap), amb), 1, 1)

    return lmap

def mapMask(dimensions = (1024, 1024), mesh = None):
    """
    Create a texture map mask, for finding the texture map borders.
    """
    if mh.hasRenderSkin():
        try:
            if mesh is None:
                mesh = G.app.selectedHuman.mesh
            return mh.renderSkin(dimensions, mesh.vertsPerPrimitive,
                                 mesh.r_texco, index = mesh.index,
                                 clearColor = (0, 0, 0, 0))
        except Exception, e:
            log.debug(e)
            log.debug("Hardware skin rendering failed, falling back to software render.")
            return mapMaskSoft(dimensions, mesh)
    else:
        return mapMaskSoft(dimensions, mesh)

def mapMaskSoft(dimensions = (1024, 1024), mesh = None):
    """
    Create a texture mask for the selected human (software renderer).
    """
    progress = Progress() (0)
    if mesh is None:
        mesh = G.app.selectedHuman.mesh

    W = dimensions[0]
    H = dimensions[1]

    components = 4
    dstImg = mh.Image(width=W, height=H, components=components)
    dstImg.data[...] = np.tile([0,0,0,255], (H,W)).reshape((H,W,components))

    faces = getFaces(mesh)

    coords = np.asarray([0,H])[None,None,:] + mesh.texco[mesh.fuvs[faces]] * np.asarray([W,-H])[None,None,:]
    shape = mesh.fvert[faces].shape
    shape = tuple(list(shape) + [components])
    colors = np.repeat(1, np.prod(shape)).reshape(shape)

    log.debug("mapMask: begin render")

    progress(0.1, 0.55)
    RasterizeTriangles(dstImg, coords[:,[0,1,2],:], MaskShader())
    progress(0.55, 0.99)
    RasterizeTriangles(dstImg, coords[:,[2,3,0],:], MaskShader())

    log.debug("mapMask: end render")

    progress.finish()
    return dstImg

def rasterizeHLines(dstImg, edges, delta):
    flip = delta[:,0] < 0
    p = np.where(flip[:,None,None], edges[:,::-1,:], edges[:,:,:])
    del edges
    d = np.where(flip[:,None], -delta, delta)
    del delta, flip
    x0 = p[:,0,0]
    x1 = p[:,1,0]
    y0 = p[:,0,1]
    del p
    dx = d[:,0]
    dy = d[:,1]
    m = dy / dx
    del dx, dy, d
    c = y0 - m * x0
    x0 = np.floor(x0).astype(int)
    x1 = np.ceil(x1).astype(int)
    del y0

    data = dstImg.data[::-1]

    progress = Progress(len(x0), None)
    for i in xrange(len(x0)):
        x = np.arange(x0[i], x1[i])
        y = m[i] * (x + 0.5) + c[i]
        data[np.floor(y).astype(int),x,:] = 255
        progress.step()

def rasterizeVLines(dstImg, edges, delta):
    flip = delta[:,1] < 0
    p = np.where(flip[:,None,None], edges[:,::-1,:], edges[:,:,:])
    del edges
    d = np.where(flip[:,None], -delta, delta)
    del delta, flip
    x0 = p[:,0,0]
    y0 = p[:,0,1]
    y1 = p[:,1,1]
    del p
    dx = d[:,0]
    dy = d[:,1]
    m = dx / dy
    del dx, dy, d
    c = x0 - m * y0
    y0 = np.floor(y0).astype(int)
    y1 = np.ceil(y1).astype(int)
    del x0

    data = dstImg.data[::-1]

    progress = Progress(len(y0), None)
    for i in xrange(len(y0)):
        y = np.arange(y0[i], y1[i]) + 0.5
        x = m[i] * y + c[i]
        data[y.astype(int),np.floor(x).astype(int),:] = 255
        progress.step()

def mapUVSoft(mesh = None):
    """
    Project the UV map topology of the selected human mesh onto a texture
    (software rasterizer).
    """
    progress = Progress() (0)

    if mesh is None:
        mesh = G.app.selectedHuman.mesh

    W = 2048
    H = 2048

    dstImg = mh.Image(width=W, height=H, components=3)
    dstImg.data[...] = 0

    faces = getFaces(mesh)

    log.debug("mapUV: begin setup")

    fuvs = mesh.fuvs[faces]
    del faces
    edges = np.array([fuvs, np.roll(fuvs, 1, axis=-1)]).transpose([1,2,0]).reshape((-1,2))
    del fuvs
    edges = np.where((edges[:,0] < edges[:,1])[:,None], edges, edges[:,::-1])
    ec = edges[:,0] + (edges[:,1] << 16)
    del edges
    ec = np.unique(ec)
    edges = np.array([ec & 0xFFFF, ec >> 16]).transpose()
    del ec
    edges = mesh.texco[edges] * (W, H)
    progress(0.05)

    delta = edges[:,1,:] - edges[:,0,:]
    vertical = np.abs(delta[:,1]) > np.abs(delta[:,0])
    horizontal = -vertical

    hdelta = delta[horizontal]
    vdelta = delta[vertical]
    del delta
    hedges = edges[horizontal]
    vedges = edges[vertical]
    del edges, horizontal, vertical

    log.debug("mapUV: begin render")

    progress(0.1, 0.55, "Projecting UV map")
    rasterizeHLines(dstImg, hedges, hdelta)
    progress(0.55, 0.99, "Projecting UV map")
    rasterizeVLines(dstImg, vedges, vdelta)
    progress(1)

    log.debug("mapUV: end render")

    return dstImg.convert(3)

def mapUVGL():
    """
    Project the UV map topology of the selected human mesh onto a texture
    (hardware accelerated).
    """
    progress = Progress() (0)

    if mesh is None:
        mesh = G.app.selectedHuman.mesh

    W = 2048
    H = 2048

    dstImg = mh.Texture(size=(W,H), components=3)

    log.debug("mapUVGL: begin setup")

    fuvs = mesh.index
    edges = np.array([fuvs, np.roll(fuvs, 1, axis=-1)]).transpose([1,2,0]).reshape((-1,2))
    del fuvs
    edges = np.where((edges[:,0] < edges[:,1])[:,None], edges, edges[:,::-1])
    ec = edges[:,0] + (edges[:,1] << 16)
    del edges
    ec = np.unique(ec)
    edges = np.array([ec & 0xFFFF, ec >> 16]).transpose()
    del ec

    log.debug("mapUVGL: begin render")

    coords = mesh.r_texco
    edges = np.ascontiguousarray(edges, dtype=np.uint32)

    progress(0.6, 0.99)
    dstImg = mh.renderSkin(dstImg, 2, coords, index = edges, clearColor = (0, 0, 0, 255))

    log.debug("mapUV: end render")
    progress(1)

    return dstImg.convert(3)

def mapUV():
    """
    Project the UV map topology of the selected human mesh onto a texture.
    Uses OpenGL hardware acceleration if the necessary OGL features are
    available, otherwise uses a slower software rasterizer.
    """
    if mh.hasRenderSkin():
        try:
            return mapUVGL()
        except Exception, e:
            log.debug(e)
            log.debug("Hardware skin rendering failed, falling back to software render.")
            return mapUVSoft()
    else:
        return mapUVSoft()

