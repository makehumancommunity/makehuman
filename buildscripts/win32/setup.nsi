Name Makehuman
OutFile ../makehuman-nightly-win32.exe
LicenseData license.txt

SetCompress Auto
SetCompressor /SOLID lzma
SetCompressorDictSize 32
SetDatablockOptimize On

InstallDir $PROGRAMFILES\Makehuman

Page license
Page directory
Page instfiles

Section "Copy files"

  # Copy root files
  SetOutPath $INSTDIR
  File makehuman.exe
  File makehuman.exe.manifest
  # File mh.pyd
  File *.dll
  File main.py
  File license.txt

  # Copy data files
  SetOutPath $INSTDIR\data
  File /r /x .svn data\*.*  

  # Copy importers
  SetOutPath $INSTDIR\importers
  File /r /x .svn /x .pyc importers\*.*
  
  # Copy docs
#  SetOutPath $INSTDIR\docs
#  File /r /x .svn docs\*.pdf

  # Copy python files
  SetOutPath $INSTDIR\core
  File /r /x .svn /x .pyc core\*.py
  SetOutPath $INSTDIR\lib
  File /r /x .svn lib\*.*
  SetOutPath $INSTDIR\DLLs
  File /r /x .svn DLLs\*.*
  SetOutPath $INSTDIR\plugins
  File /r /x .svn /x .pyc plugins\*.py
  SetOutPath $INSTDIR\shared
  File /r /x .svn /x .pyc shared\*.*
  SetOutPath $INSTDIR\apps
  File /r /x .svn /x .pyc apps\*.py
  SetOutPath $INSTDIR\utils
  File /r /x .svn /x .pyc utils\*.*
  SetOutPath $INSTDIR\tools
  File /r /x .svn /x .pyc tools\*.*
  
  CreateDirectory $INSTDIR\models
  CreateDirectory $INSTDIR\exports
  CreateDirectory $INSTDIR\backgrounds


  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Makehuman" \
 		   "DisplayName" "Makehuman"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Makehuman" \
 		   "UninstallString" "$\"$INSTDIR\Uninst.exe$\""
  
SectionEnd

Section "Create uninstaller"
  
  WriteUninstaller $INSTDIR\Uninst.exe
  
SectionEnd

Section "Create shortcuts"

  CreateDirectory "$SMPROGRAMS\Makehuman"
  SetOutPath $INSTDIR
  CreateShortCut "$SMPROGRAMS\Makehuman\Makehuman.lnk" "$INSTDIR\makehuman.exe" \
    "" "$INSTDIR\makehuman.exe" 0 SW_SHOWNORMAL ""  "Makehuman"
  CreateShortCut "$SMPROGRAMS\Makehuman\Uninstall.lnk" "$INSTDIR\Uninst.exe" \
    "" "$INSTDIR\Uninst.exe" 0 SW_SHOWNORMAL ""  "Uninstall Makehuman"
    
SectionEnd

Section "Uninstall"

  # Remove Makehuman files
  Delete $INSTDIR\makehuman.exe
  Delete $INSTDIR\makehuman.exe.manifest
  Delete $INSTDIR\mh.pyd
  Delete $INSTDIR\*.dll
  Delete $INSTDIR\main.py
  Delete $INSTDIR\license.txt
  
  # Remove Makehuman data folders
  RMDir /r $INSTDIR\apps
  RMDir /r $INSTDIR\tools
  RMDir /r $INSTDIR\utils
  RMDir /r $INSTDIR\data
  RMDir /r $INSTDIR\docs
  RMDir /r $INSTDIR\core
  RMDir /r $INSTDIR\plugins
  RMDir /r $INSTDIR\shared
  RMDir /r $INSTDIR\pythonmodules
  RMDir /r $INSTDIR\importers
  
  # Remove uninstaller
  Delete $INSTDIR\Uninst.exe
  
  # Remove remaining Makehuman folders if empty
  RMDir $INSTDIR\models
  RMDir $INSTDIR\exports
  RMDir $INSTDIR\backgrounds  
  RMDir $INSTDIR
  
  # Remove shortcuts
  Delete $SMPROGRAMS\Makehuman\Makehuman.lnk
  Delete $SMPROGRAMS\Makehuman\Uninstall.lnk
  RMDir $SMPROGRAMS\Makehuman
  
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Makehuman"
SectionEnd


Function .onInit
  ReadRegStr $R0 HKLM \
  "Software\Microsoft\Windows\CurrentVersion\Uninstall\Makehuman" \
  "UninstallString"
  StrCmp $R0 "" done
  
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
  "Makehuman is already installed. $\n$\nClick 'OK' to remove the \
  previous version or 'Cancel' to cancel this upgrade." \
  IDOK uninst
  Abort

  uninst:
    ClearErrors
    ExecWait '$R0 _?=$INSTDIR'
    
    IfErrors no_remove_uninstaller done
    no_remove_uninstaller:
  done:
FunctionEnd
  