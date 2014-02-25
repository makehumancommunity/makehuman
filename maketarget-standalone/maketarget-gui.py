#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
GUI for the commandline MakeTarget tool 

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Jonas Hauquier

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/319)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

.. image:: ../images/files_data.png
   :align: right   
   
This is a GUI (Graphical User Interface) for the commandline maketarget tool.
"""

## CONFIG ##

DEBUG = False    # Debug mode (no masking of exceptions)

############



import maketarget
import sys, os

if __name__ == "__main__" and len(sys.argv) > 1:
    # Run commandline version
    print "MakeTarget (v%s)"% str(maketarget.VERSION)
    
    ## for DEBUGging
    if DEBUG:
        maketarget.main(sys.argv[1:])
        sys.exit()
    ###
    
    try:
        maketarget.main(sys.argv[1:])
        print "All done"
        sys.exit()
    except Exception as e:
        # Error handling: print message to terminal
        if hasattr(e, "errCode"):
            errorCode = e.errCode
        else:
            errorCode = -1
            
        if hasattr(e, "ownMsg"):
            msg = e.ownMsg
        elif hasattr(e, "msg"):
            msg = e.msg
        else:
            msg = str(e)

        print "Error: "+msg
        sys.exit(errorCode)
else:
    # Import GUI dependencies
    import wx
    from wx import xrc


class MakeTargetGUI(wx.App):

    def OnInit(self):
        self.res = xrc.XmlResource('maketarget.xrc')
        self.init_frame()
        self.progressWindow = False
        maketarget.addProcessCallback(self)
        return True

    def init_frame(self):
        self.inputEvaluated = False
        
        self.frame = self.res.LoadFrame(None, 'MakeTarget')
        # Load panel separately (no idea how to make it a child of frame in wxformbuilder)
        # Using a panel fixes the dark grey background in windows
        self.panel = self.res.LoadPanel(self.frame, "MakeTargetPanel")
        
        # Do this explicitly to fix layout in windows
        topSizer = wx.BoxSizer(wx.VERTICAL)
        self.frame.SetSizer(topSizer);
        
        topSizer.Add(self.panel,1,wx.EXPAND)
        
        # Force this here as it does not work specifying it in xrc
        self.frame.SetMinSize((500,520))
        
        # Fix layout after adding panel to frame (this is needed on windows)
        self.panel.Layout()
        self.frame.Layout()
        self.panel.Layout()
        
        # Set title bar icon
        if os.path.isfile("resources/makehuman.ico"):
            loc = wx.IconLocation(r'resources/makehuman.ico', 0)
            self.frame.SetIcon(wx.IconFromLocation(loc))
            
        if DEBUG:
            self.frame.SetTitle("MakeTarget (v%s) (DEBUG mode)"% str(maketarget.VERSION))
        else:
            self.frame.SetTitle("MakeTarget (v%s)"% str(maketarget.VERSION))
        
        self.status = xrc.XRCCTRL(self.panel, 'status_label')
        
        self.inputTypeRadio = xrc.XRCCTRL(self.panel, 'input_type')
        self.frame.Bind(wx.EVT_RADIOBOX, self.inputTypeChanged, self.inputTypeRadio)
        
        self.infolderTypeRadio = xrc.XRCCTRL(self.panel, 'infolder_type')
        
        self.inputField = xrc.XRCCTRL(self.panel, 'input_ctrl')
        self.frame.Bind(wx.EVT_TEXT, self.validateInput, self.inputField)
        
        self.inputBrowseBtn = xrc.XRCCTRL(self.panel, 'input_browse_btn')
        self.frame.Bind(wx.EVT_BUTTON, self.browseInputFile, self.inputBrowseBtn)
        
        self.inputClrBtn = xrc.XRCCTRL(self.panel, 'input_clear_btn')
        self.frame.Bind(wx.EVT_BUTTON, self.clearInput, self.inputClrBtn)
        
        self.targetsToAddList = xrc.XRCCTRL(self.panel, 'addTarget_list')
        
        self.addTarget_addBtn = xrc.XRCCTRL(self.panel, 'addTarget_list_add')
        self.frame.Bind(wx.EVT_BUTTON, self.addTargetToAdd, self.addTarget_addBtn)
        
        self.addTarget_remBtn = xrc.XRCCTRL(self.panel, 'addTarget_list_rem')
        self.frame.Bind(wx.EVT_BUTTON, self.remTargetToAdd, self.addTarget_remBtn)
        
        self.targetsToSubList = xrc.XRCCTRL(self.panel, 'subTarget_list')
        
        self.subTarget_addBtn = xrc.XRCCTRL(self.panel, 'subTarget_list_add')
        self.frame.Bind(wx.EVT_BUTTON, self.addTargetToSub, self.subTarget_addBtn)
        
        self.subTarget_remBtn = xrc.XRCCTRL(self.panel, 'subTarget_list_rem')
        self.frame.Bind(wx.EVT_BUTTON, self.remTargetToSub, self.subTarget_remBtn)
        
        self.outputField = xrc.XRCCTRL(self.panel, 'output_path_ctrl')
        self.frame.Bind(wx.EVT_TEXT, self.validateInput, self.outputField)
        
        self.outputTypeRadio = xrc.XRCCTRL(self.panel, 'output_type_options')
        self.frame.Bind(wx.EVT_RADIOBOX, self.outputTypeChanged, self.outputTypeRadio)
        
        self.outputBrowseBtn = xrc.XRCCTRL(self.panel, 'output_browse_btn')
        self.frame.Bind(wx.EVT_BUTTON, self.browseOutputFile, self.outputBrowseBtn)
        
        
        self.makeBtn = xrc.XRCCTRL(self.panel, 'make_btn')
        self.frame.Bind(wx.EVT_BUTTON, self.makeTarget, self.makeBtn)

        self.inputTypeChanged(None)
        self.outputTypeChanged(None)

        self.frame.Show()
        
    def inputTypeChanged(self, e):
        '''Determine whether to input from folder or single file'''
        self.inputFromFolder = self.inputTypeRadio.GetStringSelection() == "Directory"
        if self.inputFromFolder:
            self.outputField.Disable()
            self.outputField.SetValue("same folder as input")
            self.outputBrowseBtn.Disable()
            self.infolderTypeRadio.Enable()
        else:
            self.outputField.SetValue("")
            self.outputField.Enable()
            self.outputBrowseBtn.Enable()
            self.infolderTypeRadio.Disable()
        self.inputField.SetValue("")
        
    def browseInputFile(self, e):
        """Browse for input .target or .obj file"""
        self.dirname = ''
        if self.inputFromFolder:
            dlg = wx.DirDialog(self.frame, "Choose an input folder to load all %ss from"% self.infolderTypeRadio.GetStringSelection(), self.dirname, wx.DD_DIR_MUST_EXIST)
        else:
            dlg = wx.FileDialog(self.frame, "Choose a target or obj file", self.dirname, "", "Target (*.target)|*.target|Wavefront OBJ (*.obj)|*.obj", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.inputField.SetValue(dlg.GetPath())
        dlg.Destroy()
    
    def clearInput(self, e):
        '''Clear input file field'''
        self.inputField.SetValue("")

    def addTargetToAdd(self, e):
        """Browse for input (multiple) .target files to ADD to result"""
        self.dirname = ''
        dlg = wx.FileDialog(self.frame, "Choose targets to add", self.dirname, "", "Target (*.target)|*.target", wx.FD_MULTIPLE)
        items = self.targetsToAddList.GetStrings()
        if dlg.ShowModal() == wx.ID_OK:
            for toAdd in dlg.GetPaths():
                if toAdd not in items:
                    self.targetsToAddList.AppendAndEnsureVisible(toAdd)
        dlg.Destroy()
        
    def remTargetToAdd(self, e):
        '''Remove selected targets from ADD target list'''
        selected = list(self.targetsToAddList.GetSelections())
        selected.reverse()
        for index in selected:
            self.targetsToAddList.Delete(index)
        
    def addTargetToSub(self, e):
        """Browse for input (multiple) .target files to SUBTRACT from result"""
        self.dirname = ''
        dlg = wx.FileDialog(self.frame, "Choose targets to subtract", self.dirname, "", "Target (*.target)|*.target", wx.FD_MULTIPLE)
        items = self.targetsToSubList.GetStrings()
        if dlg.ShowModal() == wx.ID_OK:
            for toSub in dlg.GetPaths():
                if toSub not in items:
                    self.targetsToSubList.AppendAndEnsureVisible(toSub)
        dlg.Destroy()
    
    def remTargetToSub(self, e):
        '''Remove selected targets from SUBTRACT target list'''
        selected = list(self.targetsToSubList.GetSelections())
        selected.reverse()
        for index in selected:
            self.targetsToSubList.Delete(index)
            
    def outputTypeChanged(self, e):
        '''Change output type'''
        self.outputObj = self.outputTypeRadio.GetStringSelection() == "OBJ"
        if not self.outputField.GetValue():
            return
        fileName, fileExt = os.path.splitext(self.outputField.GetValue())
        if self.inputFromFolder:
            return
        if self.outputObj:
            self.outputField.SetValue(fileName+".obj")
        else:
            self.outputField.SetValue(fileName+".target")
        
    def browseOutputFile(self, e):
        '''Browse for output file'''
        self.dirname = ''
        if self.outputObj:
            dlg = wx.FileDialog(self.frame, "Save output as", self.dirname, "", "Wavefront OBJ (*.obj)|*.obj", wx.FD_SAVE)
        else:
            dlg = wx.FileDialog(self.frame, "Save output as", self.dirname, "", "Target (*.target)|*.target", wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            outputPath = dlg.GetPath()
            if self.outputObj:
                if not outputPath.endswith(".obj"):
                    outputPath = outputPath + ".obj"
            else:
                if not outputPath.endswith(".target"):
                    outputPath = outputPath + ".target"
            self.outputField.SetValue(outputPath)
        dlg.Destroy()
            
    def validateInput(self, e):
        '''Perform sanity checks on input and determine wheter it's useful to enable "Make" button.'''
        # Avoid endless recursion
        if self.inputEvaluated:
            return
        self.inputEvaluated = True
            
        if not self.inputField.GetValue() or not os.path.exists(self.inputField.GetValue()):
            # TODO or allow not specifying input in the case where ADD or SUB targets are added? Just like the cmdline version
            if self.inputFromFolder:
                self.status.SetLabel("No input folder given or folder does not exist.")
            else:
                self.status.SetLabel("No input file given or input file does not exist.")
            self.makeBtn.Disable()
        elif self.inputFromFolder and not os.path.isdir(self.inputField.GetValue()):
            self.status.SetLabel("Illegal input option. A path is expected, not a file.")
            self.makeBtn.Disable()
        elif not self.inputFromFolder and not os.path.isfile(self.inputField.GetValue()):
            self.status.SetLabel("Illegal input option. A file is expected, not a path.")
            self.makeBtn.Disable()
        elif not self.inputFromFolder and not self.outputField.GetValue():
            self.status.SetLabel("No output path specified.")
            self.makeBtn.Disable()
        elif not self.inputFromFolder and os.path.isdir(self.outputField.GetValue()):
            self.status.SetLabel("Output path is an existing folder, cannot overwrite it.")
            self.makeBtn.Disable()
        elif not self.inputFromFolder and self.outputObj and not maketarget.isObjFile(self.outputField.GetValue()):
            self.status.SetLabel("The specified output file should be a .obj file.")
            self.makeBtn.Disable()
        elif not self.inputFromFolder and not self.outputObj and not maketarget.isTargetFile(self.outputField.GetValue()):
            self.status.SetLabel("The specified output file should be a .target file.")
            self.makeBtn.Disable()
        else:
            self.status.SetLabel("Ready to make target.")
            self.makeBtn.Enable()
                
        self.inputEvaluated = False
        return
        
    def updateProgress(self, filename, percent):
        '''Callback for updating the progress bar that is shown when processing
        multiple files from a folder.'''
        if not self.progressWindow:
            self.progressWindow = wx.ProgressDialog("Processing directory",
                               "Processing %s"% os.path.basename(filename),
                               maximum = 100,
                               parent=self.frame,
                               style = wx.PD_CAN_ABORT
                                | wx.PD_APP_MODAL
                                | wx.PD_ELAPSED_TIME
                                #| wx.PD_ESTIMATED_TIME
                                | wx.PD_REMAINING_TIME
                                )
        (cont, skip) = self.progressWindow.Update(percent, "Processing %s"% os.path.basename(filename))
        return cont

        
    def makeTarget(self, e):
        '''Start maketarget application'''
        args = list()
        if self.inputFromFolder:
            args.append("--dir=%s"% self.inputField.GetValue())
            if self.infolderTypeRadio.GetStringSelection() == "Target":
                args.append("--intype=target")
            else:
                args.append("--intype=obj")
        elif self.inputField.GetValue():
            args.append("--in=%s"% self.inputField.GetValue())
            
        for target in self.targetsToAddList.GetStrings():
            args.append("--add=%s"% target)
        for target in self.targetsToSubList.GetStrings():
            args.append("--sub=%s"% target)
        
        if not self.inputFromFolder:
            args.append("--out=%s"% self.outputField.GetValue())
            
        if self.outputObj:
            args.append("--outtype")
            args.append("obj")
        else:
            args.append("target")
        
        ## for DEBUGging
        if DEBUG:
            args.append("--verbose")
            print "MakeTarget (v%s)"% str(maketarget.VERSION)
            maketarget.main(args)
            if self.progressWindow:
                self.progressWindow.Destroy()
                self.progressWindow = False
            wx.MessageBox("Operation completed", 'Success', wx.OK)
        ###
        else:
            try:
                maketarget.main(args)
                if self.progressWindow:
                    self.progressWindow.Destroy()
                    self.progressWindow = False
                wx.MessageBox("Operation completed", 'Success', wx.OK)
            except Exception as e:
                # Error handling: retrieve error message
                if hasattr(e, "errCode"):
                    errorCode = e.errCode
                else:
                    errorCode = -1
                    
                if hasattr(e, "ownMsg"):
                    msg = e.ownMsg
                elif hasattr(e, "msg"):
                    msg = e.msg
                else:
                    msg = str(e)
                
                if errorCode == 2:
                    # Show commandline context if error is argument error
                    msg = msg + "\n\nUsed command: \nmaketarget "+ " ".join(args)

                if self.progressWindow:
                    self.progressWindow.Destroy()
                    self.progressWindow = False
                wx.MessageBox(msg, 'Error', wx.OK | wx.ICON_ERROR)
            

if __name__ == '__main__':
    app = MakeTargetGUI(False)
    app.MainLoop()
