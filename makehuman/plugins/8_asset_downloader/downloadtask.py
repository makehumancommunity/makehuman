#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      ..

**Product Home Page:** TBD

**Code Home Page:**    TBD

**Authors:**           Joel Palmius

**Copyright(c):**      Joel Palmius 2016

**Licensing:**         MIT

"""

import gui3d
import mh
import socket
import json
import os
import time
import sys
import io
import urllib

from progress import Progress

mhapi = gui3d.app.mhapi

qtSignal = None
qtSlot = None

if mhapi.utility.isPython3():
    from PyQt5 import QtGui
    from PyQt5 import QtCore
    from PyQt5.QtGui import *
    from PyQt5 import QtWidgets
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    qtSignal = QtCore.pyqtSignal
    qtSlot = QtCore.pyqtSlot
else:
    if mhapi.utility.isPySideAvailable():
        from PySide import QtGui
        from PySide import QtCore
        from PySide.QtGui import *
        from PySide.QtCore import *
        qtSignal = QtCore.Signal
        qtSlot = QtCore.Slot
    else:
        from PyQt4 import QtGui
        from PyQt4 import QtCore
        from PyQt4.QtGui import *
        from PyQt4.QtCore import *
        qtSignal = QtCore.pyqtSignal
        qtSlot = QtCore.pyqtSlot


class DownloadThread(QThread):

    signalProgress = qtSignal(float)
    signalFinished = qtSignal(str)

    def __init__(self, downloadTuples, parent = None, overrideProgressSteps=None):
        QThread.__init__(self, parent)
        self.log = mhapi.utility.getLogChannel("assetdownload")
        self.exiting = False
        self.downloadTuples = downloadTuples
        self.log.debug("Downloadtuples length:",len(downloadTuples))
        self.request = mhapi.utility.getCompatibleUrlFetcher()
        self.overrideProgressSteps = overrideProgressSteps

    def run(self):
        self.log.trace("Enter")
        self.onProgress(0.0)

        total = len(self.downloadTuples)
        current = 0

        lastReport = time.time()

        downloadStatus = "OK"

        for dt in self.downloadTuples:
            remote = dt[0]
            local = dt[1]
            dn = os.path.dirname(local)
            if not os.path.exists(dn):
                os.makedirs(dn)
            current = current + 1
            self.log.trace("About to download", remote)
            self.log.trace("Destination is", local)

            remote = remote.replace(" ", "%20")

            try:
                requrl = self.request.urlopen(remote)
                cl = requrl.info().get('Content-Length').strip()
                self.log.debug("Content length", cl)

                megabytes = 0

                if cl:
                    if mhapi.utility.isPy3 and str(cl).isnumeric():
                        megabytes = float(cl) / 1000000.0
                    if not mhapi.utility.isPy3 and unicode(cl).isnumeric():
                        megabytes = float(cl) / 1000000.0

                self.log.debug("Content megabytes", megabytes)

                if megabytes < 1.0:
                    self.log.debug("File to be downloaded in one chunk, size is less than one meg")
                    data = requrl.read()
                    with open(local,"wb") as f:
                        f.write(data)
                        self.log.debug("Successfully downloaded",remote)
                else:
                    # Very large file
                    self.log.info("File to be downloaded in chunks, size is", megabytes)
                    buf = io.BytesIO()
                    size = 0
                    megabytes = int(int(cl) / 1000000) + 1
                    while True:
                        buf1 = requrl.read(100 * 1000) # 100kb size blocks
                        if not buf1:
                            break
                        buf.write(buf1)
                        size += len(buf1)
                        self.log.spam("Downloaded buffer size",size)
                        sizemegs = int(size / 1000000)

                        now = time.time()
                        now = now - 0.5
                        if now > lastReport:
                            lastReport = now
                            fileProgress = float(sizemegs) / float(megabytes)
                            fileProgress = float(current - 1) + fileProgress
                            if self.overrideProgressSteps is None:
                                self.onProgress(float(fileProgress) / float(total))
                            else:
                                self.onProgress(float(fileProgress) / float(self.overrideProgressSteps))
                    with open(local,"wb") as f:
                        f.write(buf.getvalue())
                        self.log.debug("Successfully downloaded",remote)

            except urllib.error.HTTPError as e:
                self.log.error("Caught http error", e)
                downloadStatus = str(e.code) + ";" + remote
                break
            except:
                self.log.error("Exception in download",sys.exc_info())
                self.log.warn("Could not download",remote)

            now = time.time()
            now = now - 0.5
            if now > lastReport:
                lastReport = now
                if self.overrideProgressSteps is None:
                    self.onProgress(float(current) / float(total))
                else:
                    self.onProgress(float(current) / float(self.overrideProgressSteps))

        self.onFinished(downloadStatus)
        self.exiting = True

    def onProgress(self, prog = 0.0):
        self.log.trace("onProgress",prog)
        self.signalProgress.emit(prog)

    def onFinished(self, status = "OK"):
        self.log.trace("Enter")
        self.signalFinished.emit(status)

    def __del__(self):
        self.log.trace("Enter")
        self.exiting = True
        self.log = None
        self.downloadTuples = None
        self.request = None


class DownloadTask():

    def __init__(self, parentWidget, downloadTuples, onFinished=None, onProgress=None, overrideProgressSteps=None):
        self.log = mhapi.utility.getLogChannel("assetdownload")

        self.parentWidget = parentWidget
        self.onFinished = onFinished
        self.onProgress = onProgress
        self.overrideProgressSteps = overrideProgressSteps

        self.downloadThread = DownloadThread(downloadTuples, overrideProgressSteps = self.overrideProgressSteps)

        self.downloadThread.signalProgress.connect(self._onProgress)
        self.downloadThread.signalFinished.connect(self._onFinished)

        self.progress = Progress()

        self.log.debug("About to start downloading")
        self.log.spam("downloadTuples",downloadTuples)

        self.downloadThread.start()

    def _onProgress(self, prog=0.0):
        self.log.trace("_onProgress",prog)

        self.progress(prog,desc="Downloading files...")

        if self.onProgress is not None:
            self.log.trace("onProgress callback is defined")
            self.onProgress(prog)
        else:
            self.log.trace("onProgress callback is not defined")

    def _onFinished(self, status = "OK"):
        self.log.trace("Enter")
        self.log.debug("Status", status)

        if self.overrideProgressSteps is None:
            self.progress(1.0)

        self.downloadThread.signalProgress.disconnect(self._onProgress)
        self.downloadThread.signalFinished.disconnect(self._onFinished)

        if self.onFinished is not None:
            self.log.trace("onFinished callback is defined")

            code = 0; file = None

            if status != "OK":
                (code, file) = status.split(";",2)
                code = int(code)
            self.onFinished(code, file)

        else:
            self.log.trace("onFinished callback is not defined")

        self.downloadThread = None
