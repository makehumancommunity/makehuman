#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IPython Qt Console

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehumancommunity.org/

**Github Code Home Page:**    https://github.com/makehumancommunity/

**Authors:**           Jonas Hauquier, Aranuvir

**Copyright(c):**      MakeHuman Team 2001-2020

**Licensing:**         AGPL3

    This file is part of MakeHuman (www.makehumancommunity.org).

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

Ipython qtconsole for embedding in MakeHuman
"""


from core import G
import getpath
import gui

# Import the console machinery from ipython
from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.jupyter_widget import styles
from qtconsole.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport

from PyQt5 import QtWidgets


class _QIPythonWidget(RichJupyterWidget):
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


class IPythonConsoleWidget(QtWidgets.QWidget, gui.Widget):
    """ An interactive shell widget using the ipython qt console """
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        layout = QtWidgets.QVBoxLayout(self)
        self.ipyConsole = _QIPythonWidget(customBanner="Welcome to MakeHuman's embedded Jupyter console\n")

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
            with open(ipy_stylesheet_path, 'r', encoding='utf-8') as css_file:
                stylesheet = css_file.read()
        except IOError:
            # No file to load, use default theme
            stylesheet = styles.default_light_style_sheet

        # TODO not working yet (causes a crash for some reason)

        self.ipyConsole.syntax_style = "default"

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
