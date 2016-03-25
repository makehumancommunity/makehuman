#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
IPython Qt Console

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2016

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

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

Ipython qtconsole for embedding in MakeHuman
"""

import os
import imp
from pygments.formatters import HtmlFormatter
from pygments.style import StyleMeta

from core import G
import getpath
import gui

# Import the console machinery from ipython
try:
    from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
    from IPython.qt.console.ipython_widget import styles
    from IPython.qt.inprocess import QtInProcessKernelManager
    from IPython.lib import guisupport
except ImportError:
    from qtconsole.rich_ipython_widget import RichIPythonWidget
    from qtconsole.ipython_widget import styles
    from qtconsole.inprocess import QtInProcessKernelManager
    from IPython.lib import guisupport

from PyQt4 import QtCore, QtGui, QtSvg

class _QIPythonWidget(RichIPythonWidget):
    """ Convenience class for a live IPython console widget.
    We can replace the standard banner using the customBanner argument"""
    def __init__(self, customBanner=None, *args, **kwargs):
        if customBanner!=None:
            self.banner=customBanner

        super(_QIPythonWidget, self).__init__(*args,**kwargs)

        # Embed the kernel within the event loop and expose the application
        # context
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.kernel.gui = 'qt4'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            guisupport.get_app_qt4().exit()            
        self.exit_requested.connect(stop)

    def pushVariables(self, variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.kernel_manager.kernel.shell.push(variableDict)

    def clearTerminal(self):
        """ Clears the terminal """
        self._control.clear()    

    def printText(self, text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)        

    def executeCommand(self, command):
        """ Execute a command in the frame of the console widget """
        self._execute(command,False)


def load_pygments_style(style):
    """Get an instance of a pygments Style class from a python file.
    Finds the first class definition of type pygments.style.Style and returns an
    instance of it.
    """
    # TODO include these contents in the css at compile time, 
    # we don't want to include python source files as data
    module = imp.load_source(style, getpath.getSysDataPath('themes/%s.pygments' % style))

    for member_name in dir(module):
        member = getattr(module, member_name)
        if isinstance(member, StyleMeta):
            return member

def pygments_style_to_css(style):
    """Convert a pygments Style class or name of a style in pygments styles 
    folder into CSS. This is the CSS that contains the styling of the syntax
    highlighting. """
    return HtmlFormatter(style=style).get_style_defs('.highlight')


class IPythonConsoleWidget(QtGui.QWidget, gui.Widget):
    """ An interactive shell widget using the ipython qt console """
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        self.ipyConsole = _QIPythonWidget(customBanner="Welcome to MakeHuman the embedded ipython console\n")

        self.set_theme(G.app.theme)

        layout.addWidget(self.ipyConsole)

        exposed_variables = {'G': G}
        self.ipyConsole.pushVariables(exposed_variables)
        self.ipyConsole.printText("The variable 'G' allows access to the MakeHuman application. Use the 'whos' command for information.")                           

    def onThemeChanged(self, event):
        self.set_theme(G.app.theme)

    def set_theme(self, theme):
        """ Set the theme of the terminal and syntax highlighting.
        """
        ipy_stylesheet_path = getpath.getSysDataPath('themes/%s_console.css' % theme)
        try:
            with open(ipy_stylesheet_path, 'r') as css_file:
                stylesheet = css_file.read()
        except IOError:
            # No file to load, use default theme
            stylesheet = styles.default_light_style_sheet

        # TODO not working yet (causes a crash for some reason)
        '''
        # Try parsing pygments Style python class if available, and add it to CSS
        try:
            style_obj = load_pygments_style(theme)

            # Append syntax highlighting CSS to stylesheet
            stylesheet += "\n\n" + pygments_style_to_css(style_obj)
            # Use syntax highlighting defined in CSS stylesheet
            self.ipyConsole.syntax_style = ""
        except:
            # else use default syntax style
            self.ipyConsole.syntax_style = "monokai"
        '''
        self.ipyConsole.syntax_style = "monokai"

        self.ipyConsole.style_sheet = stylesheet

    def pushVariables(self,variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.ipyConsole.pushVariables(variableDict)

    def clearTerminal(self):
        """ Clears the terminal """
        self.ipyConsole.clearTerminal()

    def printText(self, text):
        """ Prints some plain text to the console """
        self.ipyConsole.printText(text)

    def executeCommand(self, command):
        """ Execute a command in the frame of the console widget """
        self.ipyConsole.executeCommand(command)

