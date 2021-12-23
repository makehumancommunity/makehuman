#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman server socket plugin

**Product Home Page:** TBD

**Code Home Page:**    TBD

**Authors:**           Joel Palmius

**Copyright(c):**      Joel Palmius 2018

**Licensing:**         MIT

Abstract
--------

This plugin opens a TCP socket and accepts some basic commands. It
does not make much sense without a corresponding client.

"""

import gui3d
import mh
import gui
import socket
import json
import sys
import getpath
import os

mhapi = gui3d.app.mhapi
isPy3 = mhapi.utility.isPy3

if isPy3:
    from .dirops import SocketDirOps
    from .meshops import SocketMeshOps
    from .modops import SocketModifierOps
    from .workerthread import WorkerThread

class SocketTaskView(gui3d.TaskView):

    def __init__(self, category, socketConfig=None):

        self.human = gui3d.app.selectedHuman
        gui3d.TaskView.__init__(self, category, 'Socket')

        self.socketConfig = {'acceptConnections': False,
                             'advanced': False,
                             'host': '127.0.0.1',
                             'port': 12345 }

        if socketConfig and isinstance(socketConfig, dict):
            self.socketConfig['acceptConnections'] = socketConfig.get('acceptConnections', False)
            self.socketConfig['advanced'] = socketConfig.get('advanced', False)
            self.socketConfig['host'] = socketConfig.get('host', '127.0.0.1')
            self.socketConfig['port'] = socketConfig.get('port', 12345)

        self.workerthread = None

        self.log = mhapi.utility.getLogChannel("socket")

        box = self.addLeftWidget(gui.GroupBox('Server'))

        self.accToggleButton = box.addWidget(gui.CheckBox('Accept connections'))
        box.addWidget(mhapi.ui.createLabel(''))
        self.advToggleButton = box.addWidget(gui.CheckBox('Advanced Setings'))
        self.hostLabel = box.addWidget(mhapi.ui.createLabel('\nHost [Default=127.0.0.1] :'))
        self.hostEdit = box.addWidget(gui.TextEdit(str(self.socketConfig.get('host'))))
        self.portLabel = box.addWidget(mhapi.ui.createLabel('\nPort [Default=12345] :'))
        self.portEdit = box.addWidget(gui.TextEdit(str(self.socketConfig.get('port'))))
        self.spacer = box.addWidget(mhapi.ui.createLabel(''))
        self.changeAddrButton = box.addWidget(gui.Button('Change Host + Port'))

        self.hostEdit.textChanged.connect(self.onHostChanged)
        self.portEdit.textChanged.connect(self.onPortChanged)

        @self.accToggleButton.mhEvent
        def onClicked(event):
            if isPy3:
                if self.accToggleButton.selected:
                    self.socketConfig['acceptConnections'] = True
                    self.openSocket()
                else:
                    self.socketConfig['acceptConnections'] = False
                    self.closeSocket()

        @self.advToggleButton.mhEvent
        def onClicked(event):
            self.enableAdvanced(self.advToggleButton.selected)
            self.socketConfig['advanced'] = self.advToggleButton.selected

        @self.changeAddrButton.mhEvent
        def onClicked(event):
            if isPy3:
                gui3d.app.prompt('Attention', 'The host and port must be changed in Blender, too', 'OK',
                                 helpId='socketInfo')
                self.accToggleButton.setChecked(True)
                self.closeSocket()
                self.openSocket()


        self.scriptText = self.addTopWidget(gui.DocumentEdit())
        if isPy3:
            self.scriptText.setText('')
        else:
            self.scriptText.setText('This version of the socket plugin requires the py3 version of MH from github.')
        self.scriptText.setLineWrapMode(gui.DocumentEdit.NoWrap)

        if isPy3:
            self.dirops = SocketDirOps(self)
            self.meshops = SocketMeshOps(self)
            self.modops = SocketModifierOps(self)
            if self.socketConfig.get('acceptConnections'):
                self.accToggleButton.setChecked(True)
                self.openSocket()
            self.enableAdvanced(self.socketConfig.get('advanced', False))
            self.advToggleButton.setChecked(self.socketConfig.get('advanced', False))


    def onHostChanged(self):
        self.socketConfig['host'] = self.hostEdit.text

    def onPortChanged(self):
        text = str(self.portEdit.text)
        if text.isdigit():
            self.socketConfig['port'] = int(text)
        else:
            self.portEdit.setText(str(self.socketConfig.get('port')))

    def enableAdvanced(self, state = False):
        if state:
            self.hostLabel.show()
            self.hostEdit.show()
            self.portLabel.show()
            self.portEdit.show()
            self.spacer.show()
            self.changeAddrButton.show()
        else:
            self.hostLabel.hide()
            self.hostEdit.hide()
            self.portLabel.hide()
            self.portEdit.hide()
            self.spacer.hide()
            self.changeAddrButton.hide()

    def threadMessage(self,message):
        self.addMessage(str(message))

    def evaluateCall(self):
        ops = None
        data = self.workerthread.jsonCall
        conn = self.workerthread.currentConnection

        if self.meshops.hasOp(data.function):
            ops = self.meshops

        if self.dirops.hasOp(data.function):
            ops = self.dirops

        if self.modops.hasOp(data.function):
            ops = self.modops

        if ops:
            jsonCall = ops.evaluateOp(conn,data)
        else:
            jsonCall = data
            jsonCall.error = "Unknown command"

        if not jsonCall.responseIsBinary:
            self.addMessage("About to serialize JSON. This might take some time.")
            response = jsonCall.serialize()
            #print("About to send:\n\n" + response)
            response = bytes(response, encoding='utf-8')
        else:
            response = jsonCall.data
            #print("About to send binary response with length " + str(len(response)))

        conn.send(response)
        conn.close()

    def addMessage(self,message,newLine = True):
        self.log.debug("addMessage: ", message)
        if newLine:
            message = message + "\n"
        self.scriptText.addText(message)

    def openSocket(self):
        self.addMessage("Starting server thread.")
        self.workerthread = WorkerThread(socketConfig=self.socketConfig)
        self.workerthread.signalEvaluateCall.connect(self.evaluateCall)
        self.workerthread.signalAddMessage.connect(self.threadMessage)
        self.workerthread.start()

    def closeSocket(self):
        #self.addMessage("Closing socket.")
        if self.workerthread:
            self.workerthread.stopListening()
        self.workerthread = None


category = None
taskview = None
cfgFile = os.path.join(getpath.getPath(),'socket.cfg')


def load(app):
    socketConfig = {}
    if os.path.isfile(cfgFile):
        try:
            with open(cfgFile, 'r', encoding='utf-8') as f:
                socketConfig = json.loads(f.read())
        except json.JSONDecodeError:
            socketConfig = None
    category = app.getCategory('Community')
    taskview = category.addTask(SocketTaskView(category, socketConfig=socketConfig))


def unload(app):
    category = app.getCategory('Community')
    taskview = category.getTaskByName('Socket')
    if taskview:
        taskview.closeSocket()
        with open(cfgFile, 'w', encoding='utf-8') as f:
            f.writelines(json.dumps(taskview.socketConfig, indent=4))
