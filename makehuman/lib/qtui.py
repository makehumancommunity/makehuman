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

import sys
import os
import log

# Set the QT API to PyQt4
os.environ['QT_API'] = 'pyqt'

# Use version 2 of PyQt4 API
import sip
sip.setapi(u'QDate', 2)
sip.setapi(u'QDateTime', 2)
sip.setapi(u'QString', 2)
sip.setapi(u'QTextStream', 2)
sip.setapi(u'QTime', 2)
sip.setapi(u'QUrl', 2)
sip.setapi(u'QVariant', 2)

from PyQt4 import QtCore, QtGui, QtOpenGL

from core import G
import glmodule as gl
import events3d
import qtgui
import queue
import time
import getpath

import makehuman
import getpath
if False and makehuman.isBuild():
    # Set absolute Qt plugin path programatically on frozen deployment to fix
    # crashes when Qt is on DLL PATH in windows.
    # No qt.conf file should be present in the application folder!
    deployment_path = getpath.canonicalPath(getpath.getSysPath())
    QtCore.QCoreApplication.addLibraryPath(os.path.join(deployment_path,'qt4_plugins'))
    # Plugins will be loaded when QCoreApplication object is constructed. Some
    # Qt deployments are known to prepend new library paths at this time, such
    # as /usr/lib/qt4/plugins on some linux platforms, but this is not a likely
    # case on windows platforms.

# Timeout in seconds after which moving the mousewheel will pick a new mouse pos
# TODO make this configureable in settings?
MOUSEWHEEL_PICK_TIMEOUT = 0.5

class Modifiers:
    SHIFT = int(QtCore.Qt.ShiftModifier)
    CTRL  = int(QtCore.Qt.ControlModifier)
    ALT   = int(QtCore.Qt.AltModifier)
    META  = int(QtCore.Qt.MetaModifier)

class Keys:
    a = QtCore.Qt.Key_A
    b = QtCore.Qt.Key_B
    c = QtCore.Qt.Key_C
    d = QtCore.Qt.Key_D
    e = QtCore.Qt.Key_E
    f = QtCore.Qt.Key_F
    g = QtCore.Qt.Key_G
    h = QtCore.Qt.Key_H
    i = QtCore.Qt.Key_I
    j = QtCore.Qt.Key_J
    k = QtCore.Qt.Key_K
    l = QtCore.Qt.Key_L
    m = QtCore.Qt.Key_M
    n = QtCore.Qt.Key_N
    o = QtCore.Qt.Key_O
    p = QtCore.Qt.Key_P
    q = QtCore.Qt.Key_Q
    r = QtCore.Qt.Key_R
    s = QtCore.Qt.Key_S
    t = QtCore.Qt.Key_T
    u = QtCore.Qt.Key_U
    v = QtCore.Qt.Key_V
    w = QtCore.Qt.Key_W
    x = QtCore.Qt.Key_X
    y = QtCore.Qt.Key_Y
    z = QtCore.Qt.Key_Z

    N0 = QtCore.Qt.Key_0
    N1 = QtCore.Qt.Key_1
    N2 = QtCore.Qt.Key_2
    N3 = QtCore.Qt.Key_3
    N4 = QtCore.Qt.Key_4
    N5 = QtCore.Qt.Key_5
    N6 = QtCore.Qt.Key_6
    N7 = QtCore.Qt.Key_7
    N8 = QtCore.Qt.Key_8
    N9 = QtCore.Qt.Key_9

    F1  = QtCore.Qt.Key_F1
    F2  = QtCore.Qt.Key_F2
    F3  = QtCore.Qt.Key_F3
    F4  = QtCore.Qt.Key_F4
    F5  = QtCore.Qt.Key_F5
    F6  = QtCore.Qt.Key_F6
    F7  = QtCore.Qt.Key_F7
    F8  = QtCore.Qt.Key_F8
    F9  = QtCore.Qt.Key_F9
    F10 = QtCore.Qt.Key_F10
    F11 = QtCore.Qt.Key_F11
    F12 = QtCore.Qt.Key_F12
    F13 = QtCore.Qt.Key_F13
    F14 = QtCore.Qt.Key_F14
    F15 = QtCore.Qt.Key_F15

    UP        = QtCore.Qt.Key_Up
    DOWN      = QtCore.Qt.Key_Down
    LEFT      = QtCore.Qt.Key_Left
    RIGHT     = QtCore.Qt.Key_Right

    PAGEUP    = QtCore.Qt.Key_PageUp
    PAGEDOWN  = QtCore.Qt.Key_PageDown
    HOME      = QtCore.Qt.Key_Home
    END       = QtCore.Qt.Key_End
    INSERT    = QtCore.Qt.Key_Insert
    DELETE    = QtCore.Qt.Key_Delete
    PAUSE     = QtCore.Qt.Key_Pause

    RETURN    = QtCore.Qt.Key_Return
    BACKSPACE = QtCore.Qt.Key_Backspace
    ESCAPE    = QtCore.Qt.Key_Escape
    TAB       = QtCore.Qt.Key_Tab

    PLUS      = QtCore.Qt.Key_Plus
    MINUS     = QtCore.Qt.Key_Minus
    PERIOD    = QtCore.Qt.Key_Period

    SHIFT     = QtCore.Qt.Key_Shift
    CTRL      = QtCore.Qt.Key_Control
    ALT       = QtCore.Qt.Key_Alt
    META      = QtCore.Qt.Key_Meta

Keys._all = set(getattr(Keys, k)
                for k in dir(Keys)
                if k[0] != '_')

class Buttons:
    LEFT = QtCore.Qt.LeftButton
    MIDDLE = QtCore.Qt.MidButton
    RIGHT = QtCore.Qt.RightButton

    LEFT_MASK = LEFT
    MIDDLE_MASK = MIDDLE
    RIGHT_MASK = RIGHT

g_mouse_pos = None
gg_mouse_pos = None
g_mousewheel_t = None

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
        self.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)

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
        d = ev.delta()
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

class VLayout(QtGui.QLayout):
    def __init__(self, parent = None):
        super(VLayout, self).__init__(parent)
        self._children = []

    def addItem(self, item):
        self._children.append(item)

    def count(self):
        return len(self._children)

    def itemAt(self, index):
        if index < 0 or index >= self.count():
            return None
        return self._children[index]

    def takeAt(self, index):
        child = self.itemAt(index)
        if child is not None:
            del self._children[index]
        return child

    def _doLayout(self, x, y, width, height, real=False):
        for i, child in enumerate(self._children):
            widget = child.widget()
            if widget and not widget.isVisible():
                continue

        x1 = x + width
        y1 = y + height

        for i, child in enumerate(self._children):
            widget = child.widget()
            if not widget or widget.isHidden():
                w = 0
                h = 0
            else:
                size = child.maximumSize()
                w = size.width()
                h = size.height()
            if real:
                child.setGeometry(QtCore.QRect(x, y, min(w, x1 - x), min(h, y1 - y)))
            width = max(width, w)
            y += h
        return width, y

    def sizeHint(self):
        width, height = self._doLayout(0, 0, 1e9, 1e9, False)
        return QtCore.QSize(width, height)

    def maximumSize(self):
        return self.sizeHint()

    def setGeometry(self, rect):
        self._doLayout(rect.x(), rect.y(), rect.width(), rect.height(), True)

    def expandingDirections(self):
        return QtCore.Qt.Vertical

class TaskPanel(qtgui.VScrollArea):
    def __init__(self):
        super(TaskPanel, self).__init__()
        self.setMinimumHeight(250)
        self.child = QtGui.QWidget()
        self.child.setContentsMargins(0, 0, 0, 0)
        self.child.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Preferred)
        self.setWidget(self.child)
        self.layout = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom, self.child)

    def addWidget(self, widget, *args, **kwargs):
        self.layout.addWidget(widget, *args, **kwargs)
        return widget

    def removeWidget(self, widget):
        self.layout.removeWidget(widget)

class CategoryPanel(QtGui.QWidget, qtgui.Widget):
    def __init__(self):
        super(CategoryPanel, self).__init__()
        qtgui.Widget.__init__(self)
        self.layout = QtGui.QBoxLayout(QtGui.QBoxLayout.BottomToTop, self)

    def addWidget(self, widget, *args, **kwargs):
        self.layout.addWidget(widget, *args, **kwargs)
        return widget

    def removeWidget(self, widget):
        self.layout.removeWidget(widget)

def getQtVersionString():
    return str(QtCore.qVersion())

def getQtVersion():
    return [ int(versionNb) for versionNb in getQtVersionString().split(".") ]

def supportsSVG():
    """
    Determines whether Qt supports SVG image files.
    """
    qtVersion = getQtVersion()
    # Care needs to be taken that pyinstaller windows builds and
    # OSX py2app builds include the qt svg lib and plugin
    return qtVersion[0] >= 4 and qtVersion[1] >= 2 and \
        'svg' in supportedImageFormats()

def supportsJPG():
    return 'jpg' in supportedImageFormats()

def supportedImageFormats():
    """
    The image formats supported by MakeHuman. This is determined by the plugins
    that were loaded into the Qt libraries.
    """
    return [ str(s).lower() for s in QtGui.QImageReader.supportedImageFormats() ]

class Frame(QtGui.QMainWindow):
    title = "MakeHuman"

    def __init__(self, app, size):
        self.app = app
        super(Frame, self).__init__()

        self.setWindowTitle(self.title)
        if supportsSVG():
            # SVG icons allow better resolution when resized
            self.setWindowIcon(QtGui.QIcon(getpath.getSysPath("icons/makehuman_bg.svg")))
        else:
            # Older Qt libraries do not support svg icons
            self.setWindowIcon(QtGui.QIcon(getpath.getSysPath("icons/makehuman.png")))

        self.setAttribute(QtCore.Qt.WA_KeyCompression, False)
        self.setAcceptDrops(True)
        self.resize(*size)
        
        # work-around for mac QT toolbar bug described in: https://bugreports.qt-project.org/browse/QTBUG-18567
        if sys.platform.startswith("darwin"):
            self.toolbar = self.addToolBar("Toolbar")
            self.toolbar.hide()

        self.statusBar = qtgui.StatusBar()
        self.setStatusBar(self.statusBar)
        self.central = QtGui.QWidget()
        self.setCentralWidget(self.central)
        self.create()

    def panel(self):
        widget = QtGui.QWidget()
        widget.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, False)
        widget.setAutoFillBackground(True)
        widget.setContentsMargins(0, 0, 0, 0)
        return widget

    def create(self):
        self.v_layout = QtGui.QGridLayout(self.central)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(0)

        self.tab_panel = self.panel()
        self.v_layout.addWidget(self.tab_panel, 0, 0)
        self.v_layout.setRowStretch(0, 0)

        self.tab_layout = QtGui.QGridLayout(self.tab_panel)
        self.tab_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs = qtgui.Tabs()
        self.tab_layout.addWidget(self.tabs)

        self.h_layout = QtGui.QGridLayout()
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(0)
        self.v_layout.addLayout(self.h_layout, 1, 0)
        self.v_layout.setRowStretch(1, 1)

        self.b_panel = self.panel()
        self.bottom = QtGui.QBoxLayout(QtGui.QBoxLayout.BottomToTop, self.b_panel)
        self.v_layout.addWidget(self.b_panel, 2, 0)
        self.v_layout.setRowStretch(2, 0)

        self.l_panel = self.panel()
        self.left_top = QtGui.QStackedLayout(self.l_panel)
        self.h_layout.addWidget(self.l_panel, 0, 0)
        self.h_layout.setColumnStretch(0, 0)

        self.t_layout = QtGui.QBoxLayout(QtGui.QBoxLayout.TopToBottom)
        self.h_layout.addLayout(self.t_layout, 0, 1)
        self.h_layout.setColumnStretch(1, 1)

        self.t_panel = self.panel()
        self.top = VLayout(self.t_panel)
        self.top.setSizeConstraint(QtGui.QLayout.SetMinAndMaxSize)
        self.t_layout.addWidget(self.t_panel)
        self.t_panel.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Maximum)

        self.canvas = Canvas(self, app = self.app)
        self.t_layout.addWidget(self.canvas)

        self.r_panel = self.panel()
        self.right_top    = QtGui.QStackedLayout(self.r_panel)
        self.h_layout.addWidget(self.r_panel, 0, 2)
        self.h_layout.setColumnStretch(2, 0)

        self.progressBar = qtgui.ProgressBar()
        self.bottom.addWidget(self.progressBar)

    def changeEvent(self, event):
        """QMainWindow method override that is called whenever a change
        happens on the widget."""
        if event.type() == QtCore.QEvent.WindowStateChange:
            if 'normal geometry' in self.windowState:
                self.normalStateGeometry = self.storeGeometry()
        QtGui.QMainWindow.changeEvent(self, event)

    def resizeEvent(self, event):
        """QMainWindow method override that is called when
        the widget is resized."""
        if 'normal geometry' in self.windowState:
            self.normalStateGeometry = self.storeGeometry()
        QtGui.QMainWindow.resizeEvent(self, event)

    def moveEvent(self, event):
        """QMainWindow method override that is called when
        the widget is moved."""
        if 'normal geometry' in self.windowState:
            self.normalStateGeometry = self.storeGeometry()
        QtGui.QMainWindow.moveEvent(self, event)

    def addPanels(self):
        left = TaskPanel()
        right = TaskPanel()
        left.setObjectName("LeftTaskPanel")
        right.setObjectName("RightTaskPanel")
        self.left_top.addWidget(left)
        self.right_top.addWidget(right)
        return left, right

    def showPanels(self, left, right):
        self.left_top.setCurrentWidget(left)
        self.right_top.setCurrentWidget(right)

    def addTopWidget(self, widget, *args, **kwargs):
        self.top.addWidget(widget, *args, **kwargs)
        return widget

    def removeTopWidget(self, widget):
        self.top.removeWidget(widget)

    def closeEvent(self, ev):
        ev.ignore()
        self.app.callEvent('onQuit', None)

    def refreshLayout(self, widget=None):
        if widget is None:
            widget = self
        widget.updateGeometry()
        for child in QtGui.QWidget.children(widget):
            if child.isWidgetType():
                self.refreshLayout(child)

    @staticmethod
    def _asWindowStateSet(stateflags):
        """Construct a set of window state strings
        from a QWindowStates flags object.

        Multiple window states may apply to the same window, for example
        a window might be shown minimized, but set to be maximized when
        restored."""

        state = set()
        if stateflags & QtCore.Qt.WindowMaximized:
            state.add('maximized')
        if stateflags & QtCore.Qt.WindowMinimized:
            state.add('minimized')
        if stateflags & QtCore.Qt.WindowFullScreen:
            state.add('fullscreen')
        if stateflags & QtCore.Qt.WindowActive:
            state.add('active')
        if not (stateflags &
            (QtCore.Qt.WindowMaximized | QtCore.Qt.WindowFullScreen)):
            state.add('normal geometry')
            if not stateflags & QtCore.Qt.WindowMinimized:
                state.add('normal')
        return state

    def getWindowState(self):
        """Return a set of window state strings that apply to the frame."""
        return self._asWindowStateSet(QtGui.QMainWindow.windowState(self))

    def setWindowState(self, state):
        """Set the window state according to a window state set
        retrieved by getWindowState()."""
        # Order matters here. A window might be maximized when restored,
        # but currently minimized in taskbar.
        if 'maximized' in state:
            self.showMaximized()
        if 'fullscreen' in state:
            self.showFullscreen()
        if 'normal geometry' in state:
            self.showNormal()
        if 'minimized' in state:
            self.showMinimized()

    windowState = property(getWindowState, setWindowState)

    def storeGeometry(self):
        """Return a saveable dictionary describing the window's geometry.
        It can be used for saving the window's shape into a settings file."""
        geometry = {'width': self.width(), 'height': self.height(),
            'x': self.pos().x(), 'y': self.pos().y()
            } if 'normal geometry' in self.windowState \
            else self.normalStateGeometry.copy()
        geometry['state'] = list(self.windowState)
        return geometry

    def restoreGeometry(self, geometry):
        """Set the window shape according to a dictionary saved
        with storeGeometry()."""
        self.normalStateGeometry = geometry
        self.resize(geometry['width'], geometry['height'])
        self.move(geometry['x'], geometry['y'])
        self.windowState = set(geometry['state'])

    def dragEnterEvent(self, event):
        """Decide whether to accept files dragged into the MakeHuman window."""
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            path = getpath.pathToUnicode(url.toLocalFile())
            if os.path.splitext(path)[1].lower() == '.mhm':
                event.acceptProposedAction()

    def dropEvent(self, event):
        """Support drag and dropping .MHM files in the MakeHuman window to load
        them"""
        mime_data = event.mimeData()
        if not mime_data.hasUrls():
            return

        url = mime_data.urls()[0]
        path = getpath.pathToUnicode(url.toLocalFile())
        if os.path.splitext(path)[1].lower() != '.mhm':
            return

        if self.app.currentFile.modified:
            self.app.prompt("Load", "You have unsaved changes. Are you sure you want to close the current file?",
                             "Yes", "No", lambda: self.app.loadHumanMHM(path))
        else:
            self.app.loadHumanMHM(path)


class LogWindow(qtgui.ListView):

    def __init__(self):
        super(LogWindow, self).__init__()
        self.level = log.DEBUG
        self.allowMultipleSelection(True)

    def setLevel(self, level):
        self.level = level
        self.updateView()

    def updateView(self):
        for i in xrange(self.count()):
            ilevel = self.getItemData(i)
            self.showItem(i, ilevel >= self.level)
            self.setItemColor(i, log.getLevelColor(ilevel))

    def addLogMessage(self, text, level = None):
        index = self.count()
        color = log.getLevelColor(level)
        self.addItem(text, color, level)
        self.showItem(index, level >= self.level)

class AsyncEvent(QtCore.QEvent):
    def __init__(self, callback, args, kwargs):
        super(AsyncEvent, self).__init__(QtCore.QEvent.User)
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

class Application(QtGui.QApplication, events3d.EventHandler):
    def __init__(self):
        super(Application, self).__init__(sys.argv)
        self.mainwin = None
        self.log_window = None
        self.statusBar = None
        self.progressBar = None
        self.splash = None
        self.messages = None
        self.g_timers = {}
        self.logger_async = log.getLogger('mh.callAsync')
        self.logger_redraw = log.getLogger('mh.redraw')
        self.logger_event = log.getLogger('mh.event')
        self.eventHandlers = []
        # self.installEventFilter(self)

    def OnInit(self):
        import debugdump
        debugdump.dump.appendQt()

        self.messages = queue.Manager(self._postAsync)
        self.mainwin = Frame(self, (G.windowWidth, G.windowHeight))
        self.statusBar = self.mainwin.statusBar
        self.progressBar = self.mainwin.progressBar
        self.mainwin.show()
        self.log_window = LogWindow()
        
    def started(self):
        self.callEvent('onStart', None)

    def start(self):
        self.OnInit()
        self.callAsync(self.started)
        self.messages.start()
        self.exec_()
        gl.OnExit()

    def stop(self):
        self.callEvent('onStop', None)
        sys.exit()
        
    def redraw(self):
        self.logger_redraw.debug('Application.redraw')
        if self.mainwin and self.mainwin.canvas:
            self.mainwin.canvas.update()

    def addLogMessage(self, text, level = None):
        if self.log_window is not None:
            self.log_window.addLogMessage(text, level)

    def processEvents(self, flags = QtCore.QEventLoop.ExcludeUserInputEvents):
        """
        Process any asynchronous events in the queue without having to return
        to the qt main event loop. Especially useful for making sure that any
        callAsync tasks are run.
        Excluding user input events (which is set as the default flag) prevents
        unwanted recursions caused by an event firing another event because of
        user interaction.
        """
        super(Application, self).processEvents(flags)

    def event(self, event):
        self.logger_event.debug('event(%s)', event)
        if event.type() == QtCore.QEvent.User:
            # Handle custom user-defined event (AsyncEvent)
            event.callback(*event.args, **event.kwargs)
            return True
        # Handle standard Qt event
        return super(Application, self).event(event)

    def notify(self, object, event):
        self.logger_event.debug('notify(%s, %s(%s))', object, event, event.type())
        return super(Application, self).notify(object, event)

    def eventFilter(self, object, event):
        self.logger_event.debug('eventFilter(%s, %s(%s))', object, event, event.type())
        return False

    def addEventHandler(self, handler, sortOrder=None):
        if sortOrder is None:
            orders = [h.sortOrder for h in self.eventHandlers]
            o = max(orders) +1
            handler.sortOrder = o

        self.eventHandlers.append(handler)
        self.eventHandlers.sort(key = lambda h: h.sortOrder)

    def callEventHandlers(self, event_type, event):
        for handler in self.eventHandlers:
            handler.callEvent(event_type, event)

    def addTimer(self, milliseconds, callback):
        timer_id = self.startTimer(milliseconds)
        self.g_timers[timer_id] = callback
        return timer_id

    def removeTimer(self, id):
        self.killTimer(id)
        del self.g_timers[id]

    def handleTimer(self, id):
        if id not in self.g_timers:
            return
        callback = self.g_timers[id]
        callback()

    def timerEvent(self, ev):
        self.handleTimer(ev.timerId())

    def _postAsync(self, event):
        self.postEvent(self, event)

    def callAsync(self, func, *args, **kwargs):
        """
        Invoke an asynchronous event.
        """
        self.logger_async.debug('callAsync: %s(%s, %s)', func, args, kwargs)
        self._postAsync(AsyncEvent(func, args, kwargs))

def getSaveFileName(directory, filter = "All files (*.*)"):
    return unicode(QtGui.QFileDialog.getSaveFileName(
        G.app.mainwin, directory = directory, filter = filter))

def getOpenFileName(directory, filter = "All files (*.*)"):
    return unicode(QtGui.QFileDialog.getOpenFileName(
        G.app.mainwin, directory = directory, filter = filter))

def getExistingDirectory(directory):
    return unicode(QtGui.QFileDialog.getExistingDirectory(
        G.app.mainwin, directory = directory))

def setShortcut(modifier, key, action):
    action.setShortcut(QtGui.QKeySequence(modifier + key))

def callAsyncThread(func, *args, **kwargs):
    """
    Invoke callAsync from another thread than that of the main window.
    This can be used to allow other threads access to the GUI (qt only allows
    GUI access from the main thread).
    """
    G.app.messages.post(AsyncEvent(func, args, kwargs))
