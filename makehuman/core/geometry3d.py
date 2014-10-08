#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module contains classes for commonly used geometry
"""

import module3d
import numpy as np

class RectangleMesh(module3d.Object3D):

    """
    A filled rectangle.
    
    :param width: The width.
    :type width: int or float
    :param height: The height.
    :type height: int or float
    :param centered True to center the mesh around its local origin.
    :type centered bool
    :param texture: The texture.
    :type texture: str
    """
            
    def __init__(self, width, height, centered = False, texture=None):

        module3d.Object3D.__init__(self, 'rectangle_%s' % texture)

        self.centered = centered
        
        # create group
        fg = self.createFaceGroup('rectangle')
        
        # The 4 vertices
        v = self._getVerts(width, height)
        
        # The 4 uv values
        uv = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
        
        # The face
        fv = [(0,1,2,3)]
        fuv = [(0,1,2,3)]

        self.setCoords(v)
        self.setUVs(uv)
        self.setFaces(fv, fuv, fg.idx)

        self.setTexture(texture)
        self.setCameraProjection(1)
        self.setShadeless(1)
        self.updateIndexBuffer()

    def _getVerts(self, width, height):
        if self.centered:
            v = [
                (-width/2, -height/2, 0.0),
                (width/2, -height/2, 0.0),
                (width/2, height/2, 0.0),
                (-width/2, height/2, 0.0)
                ]
        else:
            v = [
                (0.0, 0.0, 0.0),
                (width, 0.0, 0.0),
                (width, height, 0.0),
                (0.0, height, 0.0)
                ]
        return v

    def move(self, dx, dy):
        self.coord += (dx, dy, 0)
        self.markCoords(coor=True)
        self.update()

    def setPosition(self, x, y):
        width, height = self.getSize()
        v = np.asarray(self._getVerts(width, height), dtype=np.float32)
        v += (x, y, 0)
        self.changeCoords(v)
        self.update()

    def resetPosition(self):
        width, height = self.getSize()
        v = self._getVerts(width, height)
        self.changeCoords(v)
        self.update()

    def resize(self, width, height):
        dx, dy = self.getOffset()
        v = np.asarray(self._getVerts(width, height), dtype=np.float32)
        v[:, 0] += dx
        v[:, 1] += dy
        self.changeCoords(v)
        self.update()

    def getSize(self):
        ((x0,y0,z0),(x1,y1,z1)) = self.calcBBox()
        return (x1 - x0, y0 - y1)

    def getOffset(self):
        ((x0,y0,z0),(x1,y1,z1)) = self.calcBBox()
        if self.centered:
            w, h = (x1 - x0, y0 - y1)
            dx = x0+w/2
            dy = y1+h/2
        else:
            dx = x0
            dy = y1
        return dx, dy
       
class FrameMesh(module3d.Object3D):
    """
    A wire rectangle.

    :param width: The width.
    :type width: int or float
    :param height: The height.
    :type height: int or float
    """
            
    def __init__(self, width, height):

        module3d.Object3D.__init__(self, 'frame', 2)
        
        # create group
        fg = self.createFaceGroup('frame')

        # The 4 vertices
        v = [
            (0.0, 0.0, 0.0),
            (width, 0.0, 0.0),
            (width, height, 0.0),
            (0.0, height, 0.0)
            ]
        
        # The 4 uv values
        uv = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
        
        # The faces
        f = [(0,3),(1,0),(2,1),(3,2)]

        self.setCoords(v)
        self.setUVs(uv)
        self.setFaces(f, f, fg.idx)
        
        self.setCameraProjection(1)
        self.setShadeless(1)
        self.updateIndexBuffer()

    def move(self, dx, dy):
        self.coord += (dx, dy, 0)
        self.markCoords(coor=True)
        self.update()

    def resize(self, width, height):
        v = [
            (0.0, 0.0, 0.0),
            (width, 0.0, 0.0),
            (width, height, 0.0),
            (0.0, height, 0.0)
            ]
        self.changeCoords(v)
        self.update()     

class Cube(module3d.Object3D):

    """
    A cube.
    
    :param width: The width.
    :type width: int or float
    :param height: The height, if 0 it will be equal to width.
    :type height: int or float
    :param depth: The depth, if 0 it will be equal to width.
    :type depth: int or float
    :param texture: The texture.
    :type texture: str
    """
            
    def __init__(self, width, height=0, depth=0, texture=None):

        module3d.Object3D.__init__(self, 'cube_%s' % texture)
        
        self.width = width
        self.height = height or width
        self.depth = depth or width
        
        # create group
        fg = self.createFaceGroup('cube')
        
        # The 8 vertices
        v = [(x,y,z) for z in [0,self.depth] for y in [0,self.height] for x in [0,self.width]]

        #         /0-----1\
        #        / |     | \
        #       |4---------5|
        #       |  |     |  |
        #       |  3-----2  |  
        #       | /       \ |
        #       |/         \|
        #       |7---------6|
        
        # The 4 uv values
        uv = ([0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0])
        
        # The 6 faces
        f = [
            (4, 5, 6, 7), # front
            (1, 0, 3, 2), # back
            (0, 4, 7, 3), # left
            (5, 1, 2, 6), # right
            (0, 1, 5, 4), # top
            (7, 6, 2, 3), # bottom
            ]

        self.setCoords(v)
        self.setUVs(uv)
        self.setFaces(f, fg.idx)

        self.setTexture(texture)
        self.setCameraProjection(0)
        self.setShadeless(0)
        self.updateIndexBuffer()
        
    def resize(self, width, height, depth):
        v = [(x,y,z) for z in [0,depth] for y in [0,height] for x in [0,width]]
        self.changeCoords(v)
        self.update()

class GridMesh(module3d.Object3D):
    def __init__(self, rows, columns, spacing=1, offset=0, plane=0, subgrids = 0, static = False):
        """
        Plane: 0 for back plane, 1 for ground plane
        """

        typeName = "ground" if plane == 1 else "back"
        module3d.Object3D.__init__(self, '%s_grid' % typeName, vertsPerPrimitive = 2)
        self.plane = plane

        # create group
        fg = self.createFaceGroup('grid')

        hBoxes = rows
        vBoxes = columns

        # Nb of lines
        rows += 1
        columns += 1

        # Vertices
        size = (columns+rows)
        self.subgrids = subgrids
        if self.subgrids > 0:
            size = size + vBoxes * (subgrids - 1) + hBoxes * (subgrids - 1)
        v = np.zeros((2 * size, 3), dtype = np.float32)
        f = np.zeros((size, 2), dtype = np.float32)
        hBegin = (-(rows/2)) * spacing
        hEnd = hBegin + (rows * spacing)
        vBegin = (-(columns/2)) * spacing
        vEnd = vBegin + (columns * spacing)
        # Horizontal lines
        for i in xrange(rows):
            pos = hBegin + (i * spacing)
            if plane == 1:
                v[2*i]    = [pos, offset, vBegin      ]
                v[2*i +1] = [pos, offset, vEnd-spacing]
            else:
                v[2*i]    = [vBegin,       pos, offset]
                v[2*i +1] = [vEnd-spacing, pos, offset]
            f[i] = [2*i, 2*i +1]

        # Vertical lines
        for i in xrange(columns):
            pos = vBegin + (i * spacing)
            if plane == 1:
                v[2* (rows+i)   ] = [hBegin,       offset, pos]
                v[2* (rows+i) +1] = [hEnd-spacing, offset, pos]
            else:
                v[2* (rows+i)   ] = [pos, hBegin,       offset]
                v[2* (rows+i) +1] = [pos, hEnd-spacing, offset]
            f[rows+ i] = [2* (rows+i), 2* (rows+i) +1]

        self.mainGridEnd = 2*(columns+rows)

        # Subgrid
        if self.subgrids > 0:
            boxspacing = spacing
            spacing = float(spacing) / self.subgrids

            # Horizontal lines
            sub = self.mainGridEnd/2
            for i in xrange(hBoxes*(subgrids-1)):
                boxOffset = (spacing * (i // (subgrids-1)))
                pos = spacing + hBegin + (i * spacing) + boxOffset
                if plane == 1:
                    v[2* (sub+i)]    = [pos, offset, vBegin         ]
                    v[2* (sub+i) +1] = [pos, offset, vEnd-boxspacing]
                else:
                    v[2* (sub+i)]    = [vBegin,          pos, offset]
                    v[2* (sub+i) +1] = [vEnd-boxspacing, pos, offset]
                f[sub+ i] = [2*(sub+i), 2*(sub+i) +1]

            # Vertical lines
            sub += hBoxes*(subgrids-1)
            for i in xrange(vBoxes*(subgrids-1)):
                boxOffset = (spacing * (i // (subgrids-1)))
                pos = spacing + vBegin + (i * spacing) + boxOffset
                if plane == 1:
                    v[2* (sub+i)   ] = [hBegin,          offset, pos]
                    v[2* (sub+i) +1] = [hEnd-boxspacing, offset, pos]
                else:
                    v[2* (sub+i)   ] = [pos, hBegin,          offset]
                    v[2* (sub+i) +1] = [pos, hEnd-boxspacing, offset]
                f[sub+ i] = [2* (sub+i), 2* (sub+i) +1]

        self.setCoords(v)
        self.setFaces(f, None, fg.idx)
        self.updateIndexBuffer()

        self.setCameraProjection(1 if static else 0)
        self.setShadeless(1)

        self.restrictVisibleToCamera = False    # Set to True to only show the grid when the camera is set to a defined parallel view (front, left, top, ...)
        self.restrictVisibleAboveGround = False # Set to true to make the grid invisible when camera inclination is below 0
        self.minSubgridZoom = 1.0   # Minimum zoom factor of the camera in which the subgrid will be shown
        self.placeAtFeet = False

        self._subgridVisible = True

    def hasSubGrid(self):
        #return self.mainGridEnd < (len(self.coord) - 2)
        return self.subgrids > 0

    def setMainColor(self, color):
        """
        Set the color of the main grid.
        """
        self._setVertColors(color, 0, self.mainGridEnd)

    def setSubColor(self, color):
        """
        Set the color of the sub grid.
        """
        if not self.hasSubGrid():
            return

        self._setVertColors(color, self.mainGridEnd, len(self.coord))

    def _setVertColors(self, color, beginIdx, endIdx):
        color = list(color)
        if len(color) == 3:
            color = color + [1.0]

        size = endIdx - beginIdx

        color = np.asarray([255*c for c in color], dtype=np.uint8)
        col = np.tile(color, size).reshape((size, 4))

        clr = self.color.copy()
        clr[beginIdx:endIdx] = col[:]
        self.setColor(clr)

    @module3d.Object3D.visibility.getter
    def visibility(self):
        from core import G
        camera = G.cameras[self.cameraMode]

        if self.hasSubGrid():
            subgridVisible = (camera.zoomFactor/camera.radius*10) >= self.minSubgridZoom

            if subgridVisible != self._subgridVisible:
                # Update subgrid visibility
                self._subgridVisible = subgridVisible
                mask = self.face_mask
                #mask = np.ones(self.getFaceCount(), dtype=np.bool)
                if subgridVisible:
                    mask[self.mainGridEnd/2:] = True
                else:
                    mask[self.mainGridEnd/2:] = False
                self.changeFaceMask(mask)
                self.updateIndexBufferFaces()

        if self.restrictVisibleAboveGround:
            if camera.getVerticalInclination() > 180 or camera.getVerticalInclination() < 0:
                return False

        if self.restrictVisibleToCamera:
            #return camera.isInParallelView()
            # Hide the grid in top and bottom view:
            return camera.isInFrontView() or camera.isInBackView() or camera.isInSideView()
        elif self.plane == 1 and (camera.isInFrontView() or camera.isInBackView() or camera.isInSideView()):
            # Hide if this is a horizontal grid and camera is looking at it horizontally
            return False
        elif self.plane == 0 and (camera.isInTopView() and camera.isInBottomView()):
            # Hide if this is a vertical grid and camera is looking at it horizontally
            return False
        else:
            return super(GridMesh, self).visibility

    @module3d.Object3D.loc.getter
    def loc(self):
        result = np.zeros(3, dtype=np.float32)
        result[:] = super(GridMesh, self).loc[:]
        if self.placeAtFeet:
            from core import G
            human = G.app.selectedHuman
            result[1] = human.getJointPosition('ground')[1]
        return result

