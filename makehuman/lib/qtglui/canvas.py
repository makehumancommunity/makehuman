#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Glynn Clements

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

TODO
"""

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from core import G

from .glsettings import GLSettings

import math
import sys

gg_mouse_pos = None
g_mouse_pos = None

class Canvas(QOpenGLWidget):

    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    def __init__(self, parent=None, app=None):

        print("\n\nINITIALIZATION OF GL CANVAS STARTS HERE\n\n")
        self.app = app

        super(Canvas, self).__init__(parent)

        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.lastPos = QPoint()

        self.trolltechGreen = QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.trolltechPurple = QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def initializeGL(self):

        self._glsettings = GLSettings(self.context())
        self.gl = self._glsettings.getGLFunctions()

        self.object = self.makeObject()

        self.gl.glShadeModel(self.gl.GL_FLAT)
        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        self.gl.glEnable(self.gl.GL_CULL_FACE)

        print("\n\nAT THIS POINT THE GL CONTEXT SHOULD BE FULLY SET UP\n\n")

    def paintGL(self):
        self.gl.glClear(
                self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        self.gl.glLoadIdentity()
        self.gl.glTranslated(0.0, 0.0, -10.0)
        self.gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        self.gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        self.gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        self.gl.glCallList(self.object)

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        self.gl.glViewport((width - side) // 2, (height - side) // 2, side,
                side)

        self.gl.glMatrixMode(self.gl.GL_PROJECTION)
        self.gl.glLoadIdentity()
        self.gl.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        self.gl.glMatrixMode(self.gl.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)

        self.lastPos = event.pos()

    def makeObject(self):
        genList = self.gl.glGenLists(1)
        self.gl.glNewList(genList, self.gl.GL_COMPILE)

        self.gl.glBegin(self.gl.GL_QUADS)

        x1 = +0.06
        y1 = -0.14
        x2 = +0.14
        y2 = -0.06
        x3 = +0.08
        y3 = +0.00
        x4 = +0.30
        y4 = +0.22

        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)
        self.quad(x3, y3, x4, y4, y4, x4, y3, x3)

        self.extrude(x1, y1, x2, y2)
        self.extrude(x2, y2, y2, x2)
        self.extrude(y2, x2, y1, x1)
        self.extrude(y1, x1, x1, y1)
        self.extrude(x3, y3, x4, y4)
        self.extrude(x4, y4, y4, x4)
        self.extrude(y4, x4, y3, x3)

        NumSectors = 200

        for i in range(NumSectors):
            angle1 = (i * 2 * math.pi) / NumSectors
            x5 = 0.30 * math.sin(angle1)
            y5 = 0.30 * math.cos(angle1)
            x6 = 0.20 * math.sin(angle1)
            y6 = 0.20 * math.cos(angle1)

            angle2 = ((i + 1) * 2 * math.pi) / NumSectors
            x7 = 0.20 * math.sin(angle2)
            y7 = 0.20 * math.cos(angle2)
            x8 = 0.30 * math.sin(angle2)
            y8 = 0.30 * math.cos(angle2)

            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)

            self.extrude(x6, y6, x7, y7)
            self.extrude(x8, y8, x5, y5)

        self.gl.glEnd()
        self.gl.glEndList()

        return genList

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.setColor(self.trolltechGreen)

        self.gl.glVertex3d(x1, y1, -0.05)
        self.gl.glVertex3d(x2, y2, -0.05)
        self.gl.glVertex3d(x3, y3, -0.05)
        self.gl.glVertex3d(x4, y4, -0.05)

        self.gl.glVertex3d(x4, y4, +0.05)
        self.gl.glVertex3d(x3, y3, +0.05)
        self.gl.glVertex3d(x2, y2, +0.05)
        self.gl.glVertex3d(x1, y1, +0.05)

    def extrude(self, x1, y1, x2, y2):
        self.setColor(self.trolltechGreen.darker(250 + int(100 * x1)))

        self.gl.glVertex3d(x1, y1, +0.05)
        self.gl.glVertex3d(x2, y2, +0.05)
        self.gl.glVertex3d(x2, y2, -0.05)
        self.gl.glVertex3d(x1, y1, -0.05)

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def setColor(self, c):
        self.gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())

'''
class Canvas(QtOpenGL.QGLWidget):
    def __init__(self, parent, app):
        self.app = app
        self.blockRedraw = False
        format = QtOpenGL.QGLFormat()
        format.setAlpha(True)
        format.setDepthBufferSize(24)
        format.setSampleBuffers(True)
        format.setSamples(4)
        super(Canvas, self).__init__(format, parent)
        self.create()

    def create(self):
        G.canvas = self
        self.setFocusPolicy(QtCore.Qt.TabFocus)
        self.setFocus()
        self.setAutoBufferSwap(False)
        self.setAutoFillBackground(False)
        self.setAttribute(QtCore.Qt.WA_NativeWindow)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        self.setAttribute(QtCore.Qt.WA_KeyCompression, False)
        self.setMouseTracking(True)
        self.setMinimumHeight(5)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

    def getMousePos(self):
        """
        Get mouse position relative to this rendering canvas. 
        Returns None if mouse is outside canvas.
        """
        relPos = self.mapFromGlobal(QtGui.QCursor().pos())
        if relPos.x() < 0 or relPos.x() > G.windowWidth:
            return None
        if relPos.y() < 0 or relPos.y() > G.windowHeight:
            return None
        return (relPos.x(), relPos.y())

    def mousePressEvent(self, ev):
        self.mouseUpDownEvent(ev, "onMouseDownCallback")

    def mouseReleaseEvent(self, ev):
        self.mouseUpDownEvent(ev, "onMouseUpCallback")

    def mouseUpDownEvent(self, ev, direction):
        global gg_mouse_pos

        x = ev.x()
        y = ev.y()
        b = ev.button()

        gg_mouse_pos = x, y

        G.app.callEvent(direction, events3d.MouseEvent(b, x, y))

        # Update screen
        self.update()

    def wheelEvent(self, ev):
        global gg_mouse_pos
        global g_mousewheel_t

        x = ev.x()
        y = ev.y()
        d = ev.angleDelta().y()
        t = time.time()

        if g_mousewheel_t is None or t - g_mousewheel_t > MOUSEWHEEL_PICK_TIMEOUT:
            gg_mouse_pos = x, y
        else:
            x = y = None

        b = 1 if d > 0 else -1
        G.app.callEvent('onMouseWheelCallback', events3d.MouseWheelEvent(b, x, y))

        if g_mousewheel_t is None or t - g_mousewheel_t > MOUSEWHEEL_PICK_TIMEOUT:
            # Update screen
            self.update()

        g_mousewheel_t = t

    def mouseMoveEvent(self, ev):
        global gg_mouse_pos, g_mouse_pos

        x = ev.x()
        y = ev.y()

        if gg_mouse_pos is None:
            gg_mouse_pos = x, y

        if g_mouse_pos is None:
            self.app.callAsync(self.handleMouse)

        g_mouse_pos = (x, y)

    def handleMouse(self):
        global gg_mouse_pos, g_mouse_pos

        if g_mouse_pos is None:
            return

        ox, oy = gg_mouse_pos
        (x, y) = g_mouse_pos
        g_mouse_pos = None
        xrel = x - ox
        yrel = y - oy
        gg_mouse_pos = x, y

        buttons = int(G.app.mouseButtons())

        G.app.callEvent('onMouseMovedCallback', events3d.MouseEvent(buttons, x, y, xrel, yrel))

        if buttons:
            self.update()

    def initializeGL(self):
        gl.OnInit()

    def paintGL(self):
        if self.blockRedraw:
            self.app.logger_redraw.debug('paintGL (blocked)')
            return
        self.app.logger_redraw.debug('paintGL')
        gl.renderToCanvas()

    def resizeGL(self, w, h):
        G.windowHeight = h
        G.windowWidth = w
        gl.reshape(w, h)
        G.app.callEvent('onResizedCallback', events3d.ResizeEvent(w, h, False))
'''