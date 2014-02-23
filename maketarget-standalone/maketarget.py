#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Commandline MakeTarget tool 

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
   
This is a commandline version implementing the basic MakeTarget functionality.

For more info on the usage of this tool, see usage()
"""

## CONFIG ##

BASE_OBJ_SVN_PATH = "../../../data/3dobjs/base.obj"

DEBUG = False    # Debug mode (no masking of exceptions)

############



import getopt, sys, os, glob, shutil

from maketargetlib import *


def usage():
    '''Print commandline usage information'''
    print """\
Maketarget stand-alone console application.
Options:
    -i --in     input obj or target
    -o --out    output obj or target
    -s --sub    target to subtract from obj
    -a --add    target to add to obj
    -d --dir    input folder to load all objs or targets from
    --intype    type of file to be input, obj (default) or target
                only applicable if --dir is used
    --outtype   type of file that will be output, obj or target (default)
    -h --help   this info
    -v --verbose    verbose mode, shows extra information
    
Usage scenarios:
    maketarget -i foo.obj -o foo.target
        Load foo.obj as input, compare it with base.obj and output the 
        difference as foo.target.
    maketarget --sub=foo1.target -i foo.obj -o foo.target
        Load foo.obj, subtract foo1.target from it, and output the difference
        between the resulting obj and base.obj as foo.target.
    maketarget --add=foo1.target -i foo.obj -o foo.target
        Load foo.obj, add foo1.target to it, and output the difference
        between the resulting obj and base.obj as foo.target.
    maketarget --dir=myfolder
        Load all objs from myfolder, save the difference between the base.obj 
        and each of the input objs to a target file with the same name as the 
        input obj.
    maketarget --dir=myfolder --sub=foo1.target
        Load all objs from myfolder, subtract foo1.target from each of them, and
        save the difference between base.obj and each of the resulting objs to 
        atarget file with the same name as the input obj.
    maketarget --dir=myfolder --add=foo1.target
        Load all objs from myfolder, add foo1.target to each of them, and
        save the difference between base.obj and each of the resulting objs to 
        a target file with the same name as the input obj.
    maketarget --outtype=obj -i foo.target -o foo.obj
        Load foo.target, apply it to base.obj and output the resulting obj as
        foo.obj.
    maketarget --outtype=obj --dir=myfolder --intype=target
        Load all target files from myfolder, apply each of them to base.obj and
        save the result of each to obj with the same name as the target file.
    maketarget --outtype obj --dir myfolder --intype target --sub foo1.target
        Load all target files in myfolder, apply each of them to base.obj while
        also subtracting foo1.target from the result. Save each combination to
        an obj with the same name as the input target.
    maketarget --outtype obj --dir myfolder --intype target --add foo1.target
        Load all target files in myfolder, apply each of them to base.obj while
        also adding foo1.target to the result. Save each combination to an obj 
        with the same name as the input target.
"""
    

def backupIfExists(path):
    '''Backs up the file if it exists to a not existing file, such that a backup
    is never lost. Works only on files, not dirs. The file will be moved away
    so a new one can be written.'''
    if not os.path.exists(path):
        return
    
    if os.path.isdir(path):
        return
        
    backupPath = path+ ".bak"
    count = 0
    while os.path.exists(backupPath):
        backupPath = "%s.bak.%d"% (path, count)
        count = count +1

    # Move to backup location
    shutil.move(path, backupPath)
    return backupPath
    
    
BASE_OBJ = False  # Globally stored base.obj

def getBaseObj():
    '''Load and return a copy of the base.obj file.'''
    global BASE_OBJ
    
    if not BASE_OBJ:
        # Only read base.obj once, then return a deep copy of the obj in memory
        try:
            # First try to get obj from path in svn, otherwise fall back on local base.obj in resources/
            if os.path.isfile(BASE_OBJ_SVN_PATH):
                verbosePrint("Using base.obj in svn at location %s"% BASE_OBJ_SVN_PATH)
                BASE_OBJ = Obj(BASE_OBJ_SVN_PATH)
            else:
                verbosePrint("Using local base.obj at location %s"% os.path.join("resources", "base.obj"))
                BASE_OBJ = Obj(os.path.join("resources", "base.obj"))
        except IOError:
            e = Exception("Failed to load base OBJ from %s."% os.path.join("resources", "base.obj"))
            e.errCode = -1
            raise e

    # Uses a custom copy constructor as deep copying is very slow (slower than loading the file from disk)
    return Obj(BASE_OBJ)
    
   
def isTargetFile(filePath):
    '''Determines whether file path points to file with .target extension.'''
    return os.path.basename(filePath).lower().endswith('.target')
      
def isObjFile(filePath):
    '''Determines whether file path points to file with .obj extension.'''
    return os.path.basename(filePath).lower().endswith('.obj')
      
def getOutputName(inputFilename):
    '''Return matching output name for the specified input name, when
    using the program in batch operation on an entire directory.'''
    fileName, fileExt = os.path.splitext(os.path.basename(inputFilename))
    outPath = os.path.dirname(inputFilename)
    return os.path.join(outPath, fileName+outputExtension)
       
def verbosePrint(msg):
    '''Print message when in verbose mode.'''
    if verbose:
        print msg
    
def performAdditionalCalculations(obj):
    '''Perform additional subs or adds on obj when specified in commandline.
    Modifies obj.'''
    for t in targetsToAdd:
        t = Target(t)
        obj.addTarget(t)
    for t in targetsToSubtract:
        t = Target(t)
        obj.subtractTarget(t)
            
def processInputObj(obj, outputFile):
    '''Process input obj to output file. obj can either be an Obj instance
    or a str pointing to the obj file location.'''
    if isinstance(obj, basestring):
        obj = Obj(obj)
        
    performAdditionalCalculations(obj)

    # Make backup if output file already exists
    backupLocation = backupIfExists(outputFile)
    if backupLocation:
        verbosePrint("Output file %s already exists. Backed up to %s"% (outputFile, backupLocation))
    
    if outType == "obj":
        verbosePrint("Writing obj to %s"% outputFile)
        obj.write(outputFile)
    else:
        diff = obj.getDifferenceAsTarget(base)
        verbosePrint("Writing target to %s (target has %d vertices)"% (outputFile, diff.getNbVerts()))
        diff.write(outputFile)
        
def processInputTarget(inputTarget, outputPath):
    '''Process input target.'''
    if isinstance(inputTarget, basestring):
        inputTarget = Target(inputTarget)
    
    # Apply input target on base
    obj = getBaseObj()
    obj.addTarget(inputTarget)
    # The rest is analogous to the processing of input OBJs
    processInputObj(obj, outputPath)
  
def parseArguments(args):
    '''Parse commandline options.'''
    global verbose, outputPath, inputTarget, inputObj, inputDir, targetsToSubtract, targetsToAdd, inType, outType
    
    try:
        opts, args = getopt.getopt(args, "i:o:s:a:d:hv", ["help", "out=", "in=", "dir=", "intype=", "outtype=", "add=", "sub=", "verbose"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -g not recognized"
        usage()
        sys.exit(2)

    verbose = False
            
    outputPath = False
        
    inType = False
    outType = False

    inputTarget = False
    inputObj = False
    inputDir = False
        
    targetsToSubtract = list()
    targetsToAdd = list()
        
    for opt, val in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-v", "--verbose"):
            verbose = True
        elif opt in ("-o", "--out"):
            if val == "ut" or val.startswith("ut="):
                e = Exception("Use either -o or --out. Not -out.")
                e.errCode = 2
                raise e
            if not val:
                e = Exception("No value specified for output (-o) option. Value is required.")
                e.errCode = 2
                raise e
            if outputPath:
                e = Exception("Multiple output (-o) options given, only one expected.")
                e.errCode = 2
                raise e
            if os.path.isdir(val):
                e = Exception("The specified output file %s is a directory." % val)
                e.errCode = 2
                raise e
            if os.path.dirname(val) != "" and not os.path.isdir(os.path.dirname(val)):
                e = Exception("The directory containing the specified output file %s does not exist." % val)
                e.errCode = 2
                raise e
            outputPath = val
        elif opt in ("-i", "--in"):
            if val == "n" or val.startswith("n="):
                e = Exception("Use either -i or --in. Not -in.")
                e.errCode = 2
                raise e
            if not val:
                e = Exception("No value specified for input (-i) option. Value is required.")
                e.errCode = 2
                raise e
            if not os.path.isfile(val):
                e = Exception("The specified input file %s cannot be found." % val)
                e.errCode = 2
                raise e
            if inputTarget or inputObj:
                e = Exception("Multiple input (-i) options given, only one expected.")
                e.errCode = 2
                raise e
            if isTargetFile(val):
                inputTarget = val
            elif isObjFile(val):
                inputObj = val
            else:
                e = Exception("Unrecognized input file. Either .target or .obj file expected.")
                e.errCode = 2
                raise e
        elif opt in ("-s", "--sub"):
            if val == "ub" or val.startswith("ub="):
                e = Exception("Use either -s or --sub. Not -sub.")
                e.errCode = 2
                raise e
            if not val:
                e = Exception("No value specified for subtract (--sub) option. Value is required.")
                e.errCode = 2
                raise e
            if not os.path.isfile(val):
                e = Exception("The specified input file %s cannot be found." % val)
                e.errCode = 2
                raise e
            if not isTargetFile(val):
                e = Exception("Expects .target file for --sub option.")
                e.errCode = 2
                raise e
            else:
                targetsToSubtract.append(val)
        elif opt in ("-a", "--add"):
            if val == "dd" or val.startswith("dd="):
                e = Exception("Use either -a or --add. Not -add.")
                e.errCode = 2
                raise e
            if not val:
                e = Exception("No value specified for addition (--add) option. Value is required.")
                e.errCode = 2
                raise e
            if not os.path.isfile(val):
                e = Exception("The specified input file %s cannot be found." % val)
                e.errCode = 2
                raise e
            if not isTargetFile(val):
                e = Exception("Expects .target file for --add option.")
                e.errCode = 2
                raise e
            else:
                targetsToAdd.append(val)
        elif opt == "--intype":
            if inType:
                e = Exception("Input type already specified. This option can only be set once.")
                e.errCode = 2
                raise e
            if val == "obj":
                inType = "obj"
            elif val == "target":
                inType = "target"
            else:
                e = Exception('Invalid input type specified. Choose either "obj" or "target".')
                e.errCode = 2
                raise e
        elif opt == "--outtype":
            if outType:
                e = Exception("Output type already specified. This option can only be set once.")
                e.errCode = 2
                raise e
            if val == "obj":
                outType = "obj"
            elif val == "target":
                outType = "target"
            else:
                e = Exception('Invalid output type specified. Choose either "obj" or "target".')
                e.errCode = 2
                raise e
        elif opt in ("-d", "--dir"):
            if val == "ir" or val.startswith("ir="):
                e = Exception("Use either -d or --dir. Not -dir.")
                e.errCode = 2
                raise e
            if not val:
                e = Exception("No value specified for input dir (--dir) option. Value is required.")
                e.errCode = 2
                raise e
            if inputDir:
                e = Exception("Multiple input dir (--dir) options given, only one expected.")
                e.errCode = 2
                raise e
            else:
                inputDir = val
        else:
            assert False
            
    if inputDir and not inType:
        # Set to default
        inType = "obj"
    if inputDir and not outType:
        # Set to default
        outType = "target"

  
#TODO it might be better to only require --outtype when using --dir, and determine the outtype from the extension of -o value (like with -i)  
def sanityCheckInput():
    '''Perform sanity checks on commandline input.'''
    # NOTE: --add foo.target and -i foo.target are actually the same. The only difference is that -i is allowed only once.
        
    if inType and not inputDir:
        e = Exception("Illegal option. Only set --intype together with --dir.")
        e.errCode = 2
        raise e
    if inputDir and (inputTarget or inputObj):
        e = Exception("Illegal input option. Either choose --dir or individual --in file, not both.")
        e.errCode = 2
        raise e
    if inputDir and outputPath:
        e = Exception("Illegal output option. Do not specify an output file (--out) together with input dir (--dir).")
        e.errCode = 2
        raise e
    if outputPath and outType == "obj" and not isObjFile(outputPath):
        e = Exception("The specified output file should be a .obj file.")
        e.errCode = 2
        raise e
    elif outputPath and outType == "target" and not isTargetFile(outputPath):
        e = Exception("The specified output file should be a .target file.")
        e.errCode = 2
        raise e
    if not inputDir and not outputPath:
        e = Exception("No output option specified (--out or --dir). Nothing will be written.")
        e.errCode = 2
        raise e    # TODO Or allow some dry-run mode or output to terminal? You can dry-run while still demanding proper params, just not actually write anything
    if outType == "obj" and (inputObj or inType == "obj") and not targetsToAdd and not targetsToSubtract:
        # Input obj, don't add any other targets and output the same obj again
        e = Exception("This command does nothing useful.")
        e.errCode = 2
        raise e
    if outType == "target" and (inputTarget or inType == "target") and not targetsToAdd and not targetsToSubtract:
        # Input a target and calculate and output that exact same target
        e = Exception("This command does nothing useful.")
        e.errCode = 2
        raise e
    if not inputDir and not inputObj and not inputTarget and not targetsToSubtract and not targetsToAdd:
        # No inputs at all
        e = Exception("No inputs given. Nothing to do.")
        e.errCode = 2
        raise e
    if outType == "target" and not inputDir and not inputObj and not inputTarget and len(targetsToAdd) == 1 and not targetsToSubtract:
        e = Exception("This command does nothing useful. It's the same as maketarget.py --i %s --out %s"% (targetsToAdd[0], outputPath))
        e.errCode = 2
        raise e
            
def verboseDetailProcess():
    '''Give detailed overview of the process to be performed.'''
    print "\nInput:"
    print "------"
    if inputDir:
        if inType == "obj":
            print "  All OBJs from directory: %s"% inputDir
        else:
            print "  All targets from directory: %s"% inputDir
    elif inputTarget:
        print "  Target: %s"% inputTarget
    elif inputObj:
        print "  OBJ: %s"% inputObj
    else:
        print "  Only using base.obj as input."
            
    if len(targetsToSubtract) >0 or len(targetsToAdd) >0:
        print "\nExtra operations:"
        print "------------------"
        if len(targetsToAdd) >0:
            print "  Add targets: %s"% ", ".join(targetsToAdd)
        if len(targetsToSubtract) >0:
            print "  Subtract targets: %s"% ", ".join(targetsToSubtract)

    print "\nOutput:"
    print "--------"
    if outType == "obj":
        print "  Output type: OBJ"
    else:
        print "  Output type: target"
    if inputDir:
        print "  Output files: %s/*%s"% (inputDir, outputExtension)
    elif outputPath:
        print "  Output to file: %s"% outputPath
    print "\n"
    
    
procCallBacks = list()

def addProcessCallback(processCallback):
    '''Add a callback to be alerted on the progress when processing multiple
    files in a directory. Can be used for a progress bar in a GUI or a cancel
    operation button.
    Callback objects need an updateProgress(filename, percent) method and
    should return True to continue, False to cancel the process.'''
    global procCallBacks
    procCallBacks.append(processCallback)
    
def notifyCallbacks(filename, percent):
    '''Notify all registered callback objects of progress.'''
    result = True
    for cb in procCallBacks:
        if not cb.updateProgress(filename, percent):
            result = False
    return result


def main(args):
    '''Main method of the commandline program.'''
    global outputExtension, base
    
    parseArguments(args)
       
    sanityCheckInput()
            
    if outType == "obj":
        outputExtension = ".obj"
    else:
        outputExtension = ".target"
                
    # Verbose detail of operation to perform
    if verbose:
        verboseDetailProcess()
            
    # Load globally used (and unmodified) base obj
    base = getBaseObj()
            
    if inputDir:
        count = 0
        if inType == "obj":
            objs = glob.glob(os.path.join(inputDir, "*.obj"))
            for iObj in objs:
                if not notifyCallbacks(getOutputName(iObj), (100*count)/len(objs)):
                    verbosePrint("Process canceled.")
                    return
                count = count +1
                verbosePrint("Processing %s (output to %s)"% (iObj, getOutputName(iObj)))
                processInputObj(iObj, getOutputName(iObj))
                verbosePrint("\n")
        else:
            tgts = glob.glob(os.path.join(inputDir, "*.target"))
            for iTgt in tgts:
                if not notifyCallbacks(getOutputName(iTgt), (100*count)/len(tgts)):
                    verbosePrint("Process canceled.")
                    return
                count = count +1
                verbosePrint("Processing %s (output to %s)"% (iTgt, getOutputName(iTgt)))
                processInputTarget(iTgt, getOutputName(iTgt))
                verbosePrint("\n")
    elif inputObj:
        verbosePrint("Processing %s (output to %s)"% (inputObj, outputPath))
        processInputObj(inputObj, outputPath)
    elif inputTarget:
        verbosePrint("Processing %s (output to %s)"% (inputTarget, outputPath))
        processInputTarget(inputTarget, outputPath)
    else:
        # Start with only base.obj
        # Load second base object
        base2 = getBaseObj()
        processInputObj(base2, outputPath)
            
        
        
if __name__ == "__main__":

    ## for DEBUGging
    if DEBUG:
        print "MakeTarget (v%s) (DEBUG)"% str(VERSION)
        main(sys.argv[1:])
        sys.exit()
    ###

    try:
        print "MakeTarget (v%s)"% str(VERSION)
        main(sys.argv[1:])
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

