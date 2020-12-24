"""Traditional PyOpenGL interface to Togl

This module provides access to the Tkinter Togl widget 
with a relatively "thick" wrapper API that creates a set 
of default "examination" operations.

Note that many (most) Linux distributions have 
now split out the Tkinter bindings into a separate package,
and that Togl must be separately downloaded (a script is 
provided in the source distribution which downloads and 
installs Togl 2.0 binaries for you).

Because of the complexity and fragility of the installation, 
it is recommended that you use Pygame, wxPython, PyGtk, or 
PyQt for real-world projects, and GLUT or Pygame for simple 
demo/testing interfaces.

The Togl project is located here:

    http://togl.sourceforge.net/
"""
# A class that creates an opengl widget.
# Mike Hartshorn
# Department of Chemistry
# University of York, UK
import os,sys, logging
_log = logging.getLogger( 'OpenGL.Tk' )
from OpenGL.GL import *
from OpenGL.GLU import *
try:
    from tkinter import _default_root
    from tkinter import *
    from tkinter import dialog
except ImportError as err:
    try:
        from Tkinter import _default_root
        from Tkinter import *
        import Dialog as dialog
    except ImportError as err:
        _log.error( """Unable to import Tkinter, likely need to install a separate package (python-tk) to have Tkinter support.  You likely also want to run the src/togl.py script in the PyOpenGL source distribution to install the Togl widget""" )
        raise
import math

def glTranslateScene(s, x, y, mousex, mousey):
    glMatrixMode(GL_MODELVIEW)
    mat = glGetDoublev(GL_MODELVIEW_MATRIX)
    glLoadIdentity()
    glTranslatef(s * (x - mousex), s * (mousey - y), 0.0)
    glMultMatrixd(mat)


def glRotateScene(s, xcenter, ycenter, zcenter, x, y, mousex, mousey):
    glMatrixMode(GL_MODELVIEW)
    mat = glGetDoublev(GL_MODELVIEW_MATRIX)
    glLoadIdentity()
    glTranslatef(xcenter, ycenter, zcenter)
    glRotatef(s * (y - mousey), 1., 0., 0.)
    glRotatef(s * (x - mousex), 0., 1., 0.)
    glTranslatef(-xcenter, -ycenter, -zcenter)
    glMultMatrixd(mat)


def sub(x, y):
    return list(map(lambda a, b: a-b, x, y))


def dot(x, y):
    t = 0
    for i in range(len(x)):
        t = t + x[i]*y[i]
    return t


def glDistFromLine(x, p1, p2):
    f = list(map(lambda x, y: x-y, p2, p1))
    g = list(map(lambda x, y: x-y, x, p1))
    return dot(g, g) - dot(f, g)**2/dot(f, f)


# Keith Junius <junius@chem.rug.nl> provided many changes to Togl
TOGL_NORMAL = 1
TOGL_OVERLAY = 2

def v3distsq(a,b):
    d = ( a[0] - b[0], a[1] - b[1], a[2] - b[2] )
    return d[0]*d[0] + d[1]*d[1] + d[2]*d[2]

# new version from Daniel Faken (Daniel_Faken@brown.edu) for static 
# loading comptability
if _default_root is None:
    _default_root = Tk()

# Add this file's directory to Tcl's search path
# This code is intended to work with the src/togl.py script 
# which will populate the directory with the appropriate 
# Binary Togl distribution.  Note that Togl 2.0 and above 
# uses "stubs", so we don't care what Tk version we are using,
# but that a different build is required for 64-bit Python.
# Thus the directory structure is *not* the same as the 
# original PyOpenGL versions.
if sys.maxsize > 2**32:
    suffix = '-64'
else:
    suffix = ''
try:
    TOGL_DLL_PATH = os.path.join(
        os.path.dirname(__file__),
        'togl-'+ sys.platform + suffix,
    )
except NameError as err:
    # no __file__, likely running as an egg
    TOGL_DLL_PATH = ""

if not os.path.isdir( TOGL_DLL_PATH ):
    _log.warning( 'Expected Tk Togl installation in %s', TOGL_DLL_PATH )
_log.info( 'Loading Togl from: %s', TOGL_DLL_PATH )
_default_root.tk.call('lappend', 'auto_path', TOGL_DLL_PATH)
try:
    _default_root.tk.call('package', 'require', 'Togl')
    _default_root.tk.eval('load {} Togl')
except TclError as err:
    _log.error( """Failure loading Togl package: %s, on debian systems this is provided by `libtogl2`""", err )
    if _default_root:
        _default_root.destroy()
    raise

# This code is needed to avoid faults on sys.exit()
# [DAA, Jan 1998], updated by mcfletch 2009
import atexit
def cleanup():
    try:
        import tkinter 
    except ImportError:
        import Tkinter as tkinter
    try: 
        if tkinter._default_root: tkinter._default_root.destroy()
    except (TclError,AttributeError):
        pass
    tkinter._default_root = None
atexit.register( cleanup )

class Togl(Widget):
    """
    Togl Widget
    Keith Junius
    Department of Biophysical Chemistry
    University of Groningen, The Netherlands
    Very basic widget which provides access to Togl functions.
    """
    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, 'togl', cnf, kw)


    def render(self):
        return


    def swapbuffers(self):
        self.tk.call(self._w, 'swapbuffers')


    def makecurrent(self):
        self.tk.call(self._w, 'makecurrent')


    def alloccolor(self, red, green, blue):
        return self.tk.getint(self.tk.call(self._w, 'alloccolor', red, green, blue))


    def freecolor(self, index):
        self.tk.call(self._w, 'freecolor', index)


    def setcolor(self, index, red, green, blue):
        self.tk.call(self._w, 'setcolor', index, red, green, blue)


    def loadbitmapfont(self, fontname):
        return self.tk.getint(self.tk.call(self._w, 'loadbitmapfont', fontname))


    def unloadbitmapfont(self, fontbase):
        self.tk.call(self._w, 'unloadbitmapfont', fontbase)


    def uselayer(self, layer):
        self.tk.call(self._w, 'uselayer', layer)


    def showoverlay(self):
        self.tk.call(self._w, 'showoverlay')


    def hideoverlay(self):
        self.tk.call(self._w, 'hideoverlay')


    def existsoverlay(self):
        return self.tk.getboolean(self.tk.call(self._w, 'existsoverlay'))


    def getoverlaytransparentvalue(self):
        return self.tk.getint(self.tk.call(self._w, 'getoverlaytransparentvalue'))


    def ismappedoverlay(self):
        return self.tk.getboolean(self.tk.call(self._w, 'ismappedoverlay'))


    def alloccoloroverlay(self, red, green, blue):
        return self.tk.getint(self.tk.call(self._w, 'alloccoloroverlay', red, green, blue))


    def freecoloroverlay(self, index):
        self.tk.call(self._w, 'freecoloroverlay', index)



class RawOpengl(Widget, Misc):
    """Widget without any sophisticated bindings\
    by Tom Schwaller"""


    def __init__(self, master=None, cnf={}, **kw):
        Widget.__init__(self, master, 'togl', cnf, kw)
        self.bind('<Map>', self.tkMap)
        self.bind('<Expose>', self.tkExpose)
        self.bind('<Configure>', self.tkExpose)


    def tkRedraw(self, *dummy):
        # This must be outside of a pushmatrix, since a resize event
        # will call redraw recursively. 
        self.update_idletasks()
        self.tk.call(self._w, 'makecurrent')
        _mode = glGetDoublev(GL_MATRIX_MODE)
        try:
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            try:
                self.redraw()
                glFlush()
            finally:
                glPopMatrix()
        finally:
            glMatrixMode(_mode)
        self.tk.call(self._w, 'swapbuffers')


    def tkMap(self, *dummy):
        self.tkExpose()


    def tkExpose(self, *dummy):
        self.tkRedraw()




class Opengl(RawOpengl):
    """\
Tkinter bindings for an Opengl widget.
Mike Hartshorn
Department of Chemistry
University of York, UK
http://www.yorvic.york.ac.uk/~mjh/
"""

    def __init__(self, master=None, cnf={}, **kw):
        """\
        Create an opengl widget.
        Arrange for redraws when the window is exposed or when
        it changes size."""

        #Widget.__init__(self, master, 'togl', cnf, kw)
        RawOpengl.__init__(*(self, master, cnf), **kw)
        self.initialised = 0

        # Current coordinates of the mouse.
        self.xmouse = 0
        self.ymouse = 0

        # Where we are centering.
        self.xcenter = 0.0
        self.ycenter = 0.0
        self.zcenter = 0.0

        # The _back color
        self.r_back = 1.
        self.g_back = 0.
        self.b_back = 1.

        # Where the eye is
        self.distance = 10.0

        # Field of view in y direction
        self.fovy = 30.0

        # Position of clipping planes.
        self.near = 0.1
        self.far = 1000.0

        # Is the widget allowed to autospin?
        self.autospin_allowed = 0

        # Is the widget currently autospinning?
        self.autospin = 0

        # Basic bindings for the virtual trackball
        self.bind('<Map>', self.tkMap)
        self.bind('<Expose>', self.tkExpose)
        self.bind('<Configure>', self.tkExpose)
        self.bind('<Shift-Button-1>', self.tkHandlePick)
        #self.bind('<Button-1><ButtonRelease-1>', self.tkHandlePick)
        self.bind('<Button-1>', self.tkRecordMouse)
        self.bind('<B1-Motion>', self.tkTranslate)
        self.bind('<Button-2>', self.StartRotate)
        self.bind('<B2-Motion>', self.tkRotate)
        self.bind('<ButtonRelease-2>', self.tkAutoSpin)
        self.bind('<Button-3>', self.tkRecordMouse)
        self.bind('<B3-Motion>', self.tkScale)


    def help(self):
        """Help for the widget."""

        d = dialog.Dialog(None, {'title': 'Viewer help',
                                 'text': 'Button-1: Translate\n'
                                         'Button-2: Rotate\n'
                                         'Button-3: Zoom\n'
                                         'Reset: Resets transformation to identity\n',
                                 'bitmap': 'questhead',
                                 'default': 0,
                                 'strings': ('Done', 'Ok')})
        assert d

    def activate(self):
        """Cause this Opengl widget to be the current destination for drawing."""

        self.tk.call(self._w, 'makecurrent')


    # This should almost certainly be part of some derived class.
    # But I have put it here for convenience.
    def basic_lighting(self):
        """\
        Set up some basic lighting (single infinite light source).

        Also switch on the depth buffer."""
   
        self.activate()
        light_position = (1, 1, 1, 0)
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_background(self, r, g, b):
        """Change the background colour of the widget."""

        self.r_back = r
        self.g_back = g
        self.b_back = b

        self.tkRedraw()


    def set_centerpoint(self, x, y, z):
        """Set the new center point for the model.
        This is where we are looking."""

        self.xcenter = x
        self.ycenter = y
        self.zcenter = z

        self.tkRedraw()


    def set_eyepoint(self, distance):
        """Set how far the eye is from the position we are looking."""

        self.distance = distance
        self.tkRedraw()


    def reset(self):
        """Reset rotation matrix for this widget."""

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.tkRedraw()


    def tkHandlePick(self, event):
        """Handle a pick on the scene."""

        if hasattr(self, 'pick'):
            # here we need to use glu.UnProject

            # Tk and X have their origin top left, 
            # while Opengl has its origin bottom left.
            # So we need to subtract y from the window height to get
            # the proper pick position for Opengl

            realy = self.winfo_height() - event.y

            p1 = gluUnProject(event.x, realy, 0.)
            p2 = gluUnProject(event.x, realy, 1.)

            if self.pick(self, p1, p2):
                """If the pick method returns true we redraw the scene."""

                self.tkRedraw()


    def tkRecordMouse(self, event):
        """Record the current mouse position."""

        self.xmouse = event.x
        self.ymouse = event.y


    def StartRotate(self, event):
        # Switch off any autospinning if it was happening

        self.autospin = 0
        self.tkRecordMouse(event)


    def tkScale(self, event):
        """Scale the scene.  Achieved by moving the eye position.

        Dragging up zooms in, while dragging down zooms out
        """
        scale = 1 - 0.01 * (event.y - self.ymouse)
        # do some sanity checks, scale no more than
        # 1:1000 on any given click+drag
        if scale < 0.001:
            scale = 0.001
        elif scale > 1000:
            scale = 1000
        self.distance = self.distance * scale
        self.tkRedraw()
        self.tkRecordMouse(event)


    def do_AutoSpin(self):
        self.activate()

        glRotateScene(0.5, self.xcenter, self.ycenter, self.zcenter, self.yspin, self.xspin, 0, 0)
        self.tkRedraw()

        if self.autospin:
            self.after(10, self.do_AutoSpin)


    def tkAutoSpin(self, event):
        """Perform autospin of scene."""

        self.after(4)
        self.update_idletasks()

        # This could be done with one call to pointerxy but I'm not sure
        # it would any quicker as we would have to split up the resulting
        # string and then conv

        x = self.tk.getint(self.tk.call('winfo', 'pointerx', self._w))
        y = self.tk.getint(self.tk.call('winfo', 'pointery', self._w))

        if self.autospin_allowed:
            if x != event.x_root and y != event.y_root:
                self.autospin = 1

        self.yspin = x - event.x_root
        self.xspin = y - event.y_root

        self.after(10, self.do_AutoSpin)


    def tkRotate(self, event):
        """Perform rotation of scene."""

        self.activate()
        glRotateScene(0.5, self.xcenter, self.ycenter, self.zcenter, event.x, event.y, self.xmouse, self.ymouse)
        self.tkRedraw()
        self.tkRecordMouse(event)


    def tkTranslate(self, event):
        """Perform translation of scene."""

        self.activate()

        # Scale mouse translations to object viewplane so object tracks with mouse
        win_height = max( 1,self.winfo_height() )
        obj_c	  = ( self.xcenter, self.ycenter, self.zcenter )
        win		= gluProject( obj_c[0], obj_c[1], obj_c[2])
        obj		= gluUnProject( win[0], win[1] + 0.5 * win_height, win[2])
        dist	   = math.sqrt( v3distsq( obj, obj_c ) )
        scale	  = abs( dist / ( 0.5 * win_height ) )

        glTranslateScene(scale, event.x, event.y, self.xmouse, self.ymouse)
        self.tkRedraw()
        self.tkRecordMouse(event)


    def tkRedraw(self, *dummy):
        """Cause the opengl widget to redraw itself."""

        if not self.initialised: return
        self.activate()

        glPushMatrix()			# Protect our matrix
        self.update_idletasks()
        self.activate()
        w = self.winfo_width()
        h = self.winfo_height()
        glViewport(0, 0, w, h)

        # Clear the background and depth buffer.
        glClearColor(self.r_back, self.g_back, self.b_back, 0.)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fovy, float(w)/float(h), self.near, self.far)

        if 0:
            # Now translate the scene origin away from the world origin
            glMatrixMode(GL_MODELVIEW)
            mat = glGetDoublev(GL_MODELVIEW_MATRIX)
            glLoadIdentity()
            glTranslatef(-self.xcenter, -self.ycenter, -(self.zcenter+self.distance))
            glMultMatrixd(mat)
        else:
            gluLookAt(self.xcenter, self.ycenter, self.zcenter + self.distance,
                self.xcenter, self.ycenter, self.zcenter,
                0., 1., 0.)
            glMatrixMode(GL_MODELVIEW)
    
        # Call objects redraw method.
        self.redraw(self)
        glFlush()				# Tidy up
        glPopMatrix()			# Restore the matrix

        self.tk.call(self._w, 'swapbuffers')
    def redraw( self, *args, **named ):
        """Prevent access errors if user doesn't set redraw fast enough"""


    def tkMap(self, *dummy):
        """Cause the opengl widget to redraw itself."""

        self.tkExpose()


    def tkExpose(self, *dummy):
        """Redraw the widget.
        Make it active, update tk events, call redraw procedure and
        swap the buffers.  Note: swapbuffers is clever enough to
        only swap double buffered visuals."""

        self.activate()
        if not self.initialised:
            self.basic_lighting()
            self.initialised = 1
        self.tkRedraw()


    def tkPrint(self, file):
        """Turn the current scene into PostScript via the feedback buffer."""

        self.activate()
