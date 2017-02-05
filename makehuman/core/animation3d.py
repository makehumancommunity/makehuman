#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Marc Flerackers

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

This module contains functions and classes to animate a wide range of objects and attributes.

To know more about the interpolation methods used, see the following references:

* http://local.wasp.uwa.edu.au/~pbourke/miscellaneous/interpolation/
* http://en.wikipedia.org/wiki/Cubic_Hermite_spline
* http://en.wikipedia.org/wiki/Kochanek-Bartels_spline
* http://www.geometrictools.com/Documentation/KBSplines.pdf
* http://www.tinaja.com/glib/cubemath.pdf
"""

import time
import math

def linearInterpolate(v1, v2, alpha):
    """
    Good interpolator when you have two values to interpolate between, but doesn't give fluid animation
    when more points are involved since it follows straight lines between the points.
    """
    return v1 + alpha * (v2 - v1)

def cosineInterpolate(v1, v2, alpha):
    """
    When you have more than 2 points two interpolate (for example following a path), this is a better
    choice than a linear interpolator.
    """
    alpha2 = (1 - math.cos(alpha * math.pi)) / 2
    return v1 + alpha2 * (v2 - v1)

def cubicInterpolate(v0, v1, v2, v3, alpha):
    """
    Cubic interpolator. Gives better continuity along the spline than the cosine interpolator,
    however needs 4 points to interpolate.
    """
    alpha2 = alpha * alpha
    a0 = (v3 - v2) - v0 + v1
    a1 = (v0 - v1) - a0
    a2 = v2 - v0
    a3 = v1

    return (a0 * alpha) * alpha2 + a1 * alpha2 + a2 * alpha + a3
    
def hermiteInterpolate(v0, v1, v2, v3, alpha, tension, bias):
    """
    Hermite interpolator. Allows better control of the bends in the spline by providing two
    parameters to adjust them:
    
    * tension: 1 for high tension, 0 for normal tension and -1 for low tension.
    * bias: 1 for bias towards the next segment, 0 for even bias, -1 for bias towards the previous segment.
    
    Using 0 bias gives a cardinal spline with just tension, using both 0 tension and 0 bias gives a Catmul-Rom spline.
    """
    alpha2 = alpha * alpha
    alpha3 = alpha2 * alpha
    m0 = (((v1 - v0) * (1 - tension)) * (1 + bias)) / 2.0
    m0 += (((v2 - v1) * (1 - tension)) * (1 - bias)) / 2.0
    m1 = (((v2 - v1) * (1 - tension)) * (1 + bias)) / 2.0
    m1 += (((v3 - v2) * (1 - tension)) * (1 - bias)) / 2.0
    a0 = 2 * alpha3 - 3 * alpha2 + 1
    a1 = alpha3 - 2 * alpha2 + alpha
    a2 = alpha3 - alpha2
    a3 = -2 * alpha3 + 3 * alpha2

    return a0 * v1 + a1 * m0 + a2 * m1 + a3 * v2

def kochanekBartelsInterpolator(v0, v1, v2, v3, alpha, tension, continuity, bias):
    """
    Kochanek-Bartels interpolator. Allows even better control of the bends in the spline by providing three
    parameters to adjust them:
    
    * tension: 1 for high tension, 0 for normal tension and -1 for low tension.
    * continuity: 1 for inverted corners, 0 for normal corners, -1 for box corners.
    * bias: 1 for bias towards the next segment, 0 for even bias, -1 for bias towards the previous segment.
    
    Using 0 continuity gives a hermite spline.
    """
    alpha2 = alpha * alpha
    alpha3 = alpha2 * alpha
    m0 = ((((v1 - v0) * (1 - tension)) * (1 + continuity)) * (1 + bias)) / 2.0
    m0 += ((((v2 - v1) * (1 - tension)) * (1 - continuity)) * (1 - bias)) / 2.0
    m1 = ((((v2 - v1) * (1 - tension)) * (1 - continuity)) * (1 + bias)) / 2.0
    m1 += ((((v3 - v2) * (1 - tension)) * (1 + continuity)) * (1 - bias)) / 2.0
    a0 = 2 * alpha3 - 3 * alpha2 + 1
    a1 = alpha3 - 2 * alpha2 + alpha
    a2 = alpha3 - alpha2
    a3 = -2 * alpha3 + 3 * alpha2

    return a0 * v1 + a1 * m0 + a2 * m1 + a3 * v2

def quadraticBezierInterpolator(v0, v1, v2, alpha):
    r"""
    Quadratic Bezier interpolator. v0 and v2 are begin and end point respectively, v1 is a control point.
    
    .. math::
        \begin{bmatrix} 1 & -2 & 1 \\ -2 & 2 & 0 \\ 1 & 1 & 0 \end{bmatrix}
    """
    alpha2 = alpha * alpha

    return (v2 - 2 * v1 + v0) * alpha2 + ((v1 - v0) * 2) * alpha + v0


def cubicBezierInterpolator(v0, v1, v2, v3, alpha):
    r"""
    Cubic Bezier interpolator. v0 and v3 are begin and end point respectively, v1 and v2 are control points.

    .. math::
        \begin{bmatrix} -1 & 3 & -3 & 1 \\ 3 & -6 & 3 & 0 \\ -3 & 3 & 0 & 0 \\ 1 & 0 & 0 & 0 \end{bmatrix}
    """

    alpha2 = alpha * alpha
    alpha3 = alpha2 * alpha

    return ((v3 - 3 * v2 + 3 * v1) - v0) * alpha3 + (3 * v2 - 6 * v1 + 3 * v0) * alpha2 + (3 * v1 - 3 * v0) * alpha + v0

def quadraticBSplineInterpolator(v0, v1, v2, alpha):
    r"""
    Quadratic b-spline interpolator. v0 and v2 are begin and end point respectively, v1 is a control point.

    .. math::
        \frac{1}{2} \begin{bmatrix} 1 & -2 & 1 \\ -2 & 2 & 0 \\ 1 & 1 & 0 \end{bmatrix}
    """

    alpha2 = alpha * alpha

    return ((v2 - 2 * v1 + v0) * alpha2 + ((v1 - v0) * 2) * alpha + v0 + v1) / 2.0

def cubicBSplineInterpolator(v0, v1, v2, v3, alpha):
    r'''
    Cubic b-spline interpolator. v0 and v3 are begin and end point respectively, v1 and v2 are control points.

    .. math::
        \frac{1}{6} \begin{bmatrix} -1 & 3 & -3 & 1 \\ 3 & -6 & 3 & 0 \\ -3 & 0 & 3 & 0 \\ 1 & 4 & 1 & 0 \end{bmatrix}
    '''

    alpha2 = alpha * alpha
    alpha3 = alpha2 * alpha

    return (((v3 - 3 * v2 + 3 * v1) - v0) * alpha3 + (3 * v2 - 6 * v1 + 3 * v0) * alpha2 + (3 * v2 - 3 * v0) * alpha + v0 + 4 * v1 + v2) / 6.0

def cubicCatmullRomInterpolator(v0, v1, v2, v3, alpha):
    r"""
    Cubic Catmull Rom interpolator. v0 and v3 are begin and end point respectively, v1 and v2 are control points.
    
    .. math::
        \frac{1}{2} \begin{bmatrix} -1 & 3 & -3 & 1 \\ 2 & -5 & 4 & -1 \\ -1 & 0 & 1 & 0 \\ 1 & 2 & 0 & 0 \end{bmatrix}
    """
    alpha2 = alpha * alpha
    alpha3 = alpha2 * alpha

    return (((v3 - 3 * v2 + 3 * v1) - v0) * alpha3 + ((-v3 + 4 * v2) - 5 * v1 + 2 * v0) * alpha2 + (v2 - v0) * alpha + 2 * v1 + v0) / 2.0

def cubicHermiteInterpolator(v0, v1, v2, v3, alpha):
    r"""
    Cubic hermite interpolator. v0 and v3 are begin and end point respectively, v1 and v2 are control points.
    
    .. math::
        \frac{1}{6} \begin{bmatrix} 2 & 1 & -2 & 1 \\ -3 & -2 & 3 & -1 \\ 0 & 1 & 0 & 0 \\ 1 & 0 & 0 & 0 \end{bmatrix}
    """
    alpha2 = alpha * alpha
    alpha3 = alpha2 * alpha

    return (v3 - 2 * v2 + v1 + 2 * v0) * alpha3 + (((-v3 + 3 * v2) - 2 * v1) - 3 * v0) * alpha2 + v1 * alpha + v0


def ThreeDQBspline(v0, v1, v2, alpha):
    return [quadraticBSplineInterpolator(v0[i], v1[i], v2[i], alpha) for i in xrange(len(v1))]

def lerpVector(v0, v1, alpha, interpolator=linearInterpolate):
    """
    Interpolates a whole vector at once.
    """
    return [interpolator(v0[i], v1[i], alpha) for i in xrange(len(v1))]

class Action:
    """
    Base action class, does nothing
    """
    def __init__(self):
        pass

    def set(self, alpha):
        pass


class PathAction(Action):
    """
    Path action class. Moves an object along a path
    """
    def __init__(self, obj, positions):
        self.obj = obj
        self.positions = positions

    def set(self, alpha):
        keys = float(len(self.positions) - 1)
        key = int(alpha * keys)
        if key == len(self.positions) - 1:

            # Use last value

            value = self.positions[-1]
        else:

            # Offset alpha to it's own slice, and expand the slice to 0-1

            sliceLength = 1.0 / keys
            a = (alpha - key * sliceLength) * keys

            # Interpolate between current and next using the new alpha

            value = lerpVector(self.positions[key], self.positions[key + 1], a)
        self.obj.setPosition(value)

class ZoomAction(Action):
    """
    A zoom transition for a camera
    """
    def __init__(self, obj, startZoom, endZoom):
        self.obj = obj
        self.startZoom = startZoom
        self.endZoom = endZoom

    def set(self, alpha):
        value = lerpVector([self.startZoom], [self.endZoom], alpha)
        self.obj.setZoomFactor(value[0])

class RotateAction(Action):
    """
    Rotate action class. Rotates an object from a start orientation to an end orientation.
    """
    def __init__(self, obj, startAngles, endAngles):
        self.obj = obj
        self.startAngle = self.clipRotation(startAngles)
        self.endAngle = self.clipRotation(endAngles)

        self.endAngle = self.closestRotation(self.startAngle, self.endAngle)

    def set(self, alpha):
        value = lerpVector(self.startAngle, self.endAngle, alpha)
        self.obj.setRotation(value)

    @classmethod
    def clipRotation(cls, rotation):
        rotation[0] = rotation[0] % 360
        rotation[1] = rotation[1] % 360
        rotation[2] = rotation[2] % 360
        return rotation

    @classmethod
    def closestRotation(cls, beginRot, endRot):
        rotation = [0.0, 0.0, 0.0]
        rotation[0] = cls.closestAngle(beginRot[0], endRot[0])
        rotation[1] = cls.closestAngle(beginRot[1], endRot[1])
        rotation[2] = cls.closestAngle(beginRot[2], endRot[2])
        return rotation

    @classmethod
    def closestAngle(cls, beginAngle, endAngle):
        """
        Assumes that beginAngle and endAngle are clipped between [0, 360[
        Calculates end angle so that linear interpolation between beginAngle
        and the returned end angle results in a minimal rotation.
        """
        if endAngle < beginAngle:
            endAngle = 360.0 + endAngle
        angleDiff = endAngle - beginAngle
        if abs(angleDiff) > 180:
            return -(360.0 - endAngle)
        else:
            return endAngle

class ScaleAction(Action):
    """
    Scale action class. Scales an object from a start scale to an end scale.
    """
    def __init__(self, obj, startScale, endScale):
        self.obj = obj
        self.startScale = startScale
        self.endScale = endScale

    def set(self, alpha):
        value = lerpVector(self.startScale, self.endScale, alpha)
        self.obj.setScale(value)
        

class CameraAction(Action):
    """
    CameraAction action class. Animates all camera attributes.
    """
    # TODO remove?
    def __init__(self, cam, startParams, endParams):
        
        self.cam = cam
        self.startParams = startParams or (self.cam.eyeX, self.cam.eyeY, self.cam.eyeZ, self.cam.focusX, self.cam.focusY, self.cam.focusZ, self.cam.upX, self.cam.upY, self.cam.upZ)
        self.endParams = endParams or (self.cam.eyeX, self.cam.eyeY, self.cam.eyeZ, self.cam.focusX, self.cam.focusY, self.cam.focusZ, self.cam.upX, self.cam.upY, self.cam.upZ)

    def set(self, alpha):
        value = lerpVector(self.startParams, self.endParams, alpha)
        self.cam.eyeX, self.cam.eyeY, self.cam.eyeZ, self.cam.focusX, self.cam.focusY, self.cam.focusZ, self.cam.upX, self.cam.upY, self.cam.upZ = value

class UpdateAction(Action):
    """
    Updates the scene. Without this acton and animation is not visible.
    """
    def __init__(self, app):
        self.app = app

    def set(self, alpha):
        self.app.redraw()
        self.app.processEvents()


class Timeline:
    """
    A timeline combines several animation3d.Action objects to an animation.
    """
    def __init__(self, seconds):
        self.length = float(seconds)
        self.actions = []

    def append(self, action):
        self.actions.append(action)

    def start(self):
        reference = time.time()
        t = 0
        while t < self.length:
            a = t / self.length
            for action in self.actions:
                action.set(a)
            t = time.time() - reference
        for action in self.actions:
            action.set(1.0)

def animate(app, seconds, actions):
    """
    Animates the given actions by creating a animation3d.Timeline, adding an animation3d.UpdateAction and calling start.
    """
    tl = Timeline(seconds)
    for action in actions:
        tl.append(action)
    tl.append(UpdateAction(app))
    tl.start()
