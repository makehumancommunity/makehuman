#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Joel Palmius

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

A brief overview of what the different modules do, and how to use them:

* Canvas, in canvas.py (moved and adapted from lib/qtui.py): This is the Qt widget on which 3d graphics are drawn. If
  you want to start looking at the code, this is where most of the GL stuff is called/spawned/displayed/added.

* GLSettings, in glsettings.py (adapted from pieces here and there): This is where global GL settings are set on the
  GL context. This is also where the central "functions" object is created, based on what OpenGL version is used.

* Shader, in shader.py (moved and adapted from lib/shader.py): This is where materials are created and managed (mostly
  unported as of yet)

* Texture, in texture.py (moved and adapted from lib/texture.py): This is where image textures are transformed into
  something usable by GL (mostly unported as of yet)

* TextureCache, in texturecache.py (moved and adapted from lib/texture.py): This caches image textures so they don't
  have to be reloaded from disk (mostly unported as of yet)

Some basic principles:

In the new version of the GL code, PyOpenGL should not be used directly anywhere. Theoretically, we will not even
include the dependency later on. Instead we rely on Qt's GL wrappers. The method calls are mostly the same, but
instead of importing OpenGL as gl and then calling gl.someMethod(), we instead get a "functions" object from the
GL context of a Qt OpenGLWidget and call it "gl". Then we can still call gl.someMethod() and expect it to work
mostly the same, but we will leave much of the initialization to Qt.

But for this to work WE CAN NEVER EVER USE OPENGL CALLS DIRECTLY. All GL calls have to be made via the functions object,
gotten from a Qt OpenGL widget's context.

Since we in practice only have one widget, an instance of "Canvas", on which we draw GL stuff, then that instance is
what should manage most GL stuff.

"""

__all__ = ['Canvas','Shader','Texture','TextureCache','ScreenObject','DrawableObject','Action']

from .canvas import Canvas
from .shader import Shader
from .texture import Texture
from .texturecache import TextureCache
from .screenobject import ScreenObject
from .screenobject import Action
from .drawableobject import DrawableObject

