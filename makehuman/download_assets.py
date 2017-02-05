#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    https://bitbucket.org/MakeHuman/makehuman/

**Authors:**           Jonas Hauquier

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

Simple download script to fetch additional assets from ftp.
Syncs local and FTP content using FTP's modified dates and a locally cached
index file.
"""

## CONFIG #################################
ftpUrl = "download.tuxfamily.org"
ftpPath = "/makehuman/assets/"
defaultRepo = "base"

default_nodelete = False
###########################################

def version():
    return "1.2"


import os
import sys
import shutil
from ftplib import FTP

sys.path = ["./lib"] + sys.path
from getpath import getSysDataPath, isSubPath, getSysPath

def downloadFromFTP(ftp, filePath, destination):
    fileSize = ftp.size(filePath)
    downloaded = [0]    # Is a list so we can pass and change it in an inner func
    global f
    if destination:
        f = open(destination, 'wb')
    else:
        f = ""

    def writeChunk(data):
        global f
        if destination:
            f.write(data)
        else:
            f = f+str(data)

        downloaded[0] += len(data)
        percentage = 100 * float(downloaded[0]) / fileSize
        if destination:
            sys.stdout.write("  Downloaded %d%% of %d bytes\r" % (percentage, fileSize))

        if percentage >= 100 and destination:
            sys.stdout.write('\n')

    ftp.retrbinary('RETR '+filePath, writeChunk)
    if destination:
        f.close()
    else:
        return f


def downloadFile(ftp, filePath, destination, fileProgress):
    filePath = filePath.replace('\\', '/')
    destination = destination.replace('\\', '/')
    if os.path.dirname(destination) and not os.path.isdir(os.path.dirname(destination)):
        os.makedirs(os.path.dirname(destination))

    #print "[%d%% done] Downloading file %s to %s" % (fileProgress, url, filename)
    print "[%d%% done] Downloading file %s" % (fileProgress, os.path.basename(destination))
    print "             %s ==> %s" % (filePath, destination)
    downloadFromFTP(ftp, filePath, destination)

def parseContentsFile(filename):
    from codecs import open
    f = open(filename, 'rU', encoding="utf-8")
    fileData = f.read()
    contents = {}
    for l in fileData.split('\n'):
        if not l:
            continue
        if l.startswith('#') or l.startswith('//'):
            continue
        c=l.split()
        try:
            contents[c[0]] = long(c[1])
        except:
            contents[c[0]] = 0
    f.close()
    return contents

def writeContentsFile(filename, contents):
    from codecs import open
    f = open(filename, 'w', encoding="utf-8")
    for fPath, mtime in contents.items():
        f.write("%s %s\n" % (fPath, mtime))
    f.close()

def getNewFiles(oldContents, newContents, destinationFolder):
    result = []
    for (filename, newTime) in newContents.items():
        destFile = os.path.join(destinationFolder, filename.lstrip('/'))
        if not os.path.isfile(destFile):
            result.append(filename)
        elif filename in oldContents:
            oldTime = oldContents[filename]
            if newTime > oldTime:
                result.append(filename)
        else:
            result.append(filename)
    return result

def getRemovedFiles(oldContents, newContents, destinationFolder):
    toRemove = []
    for filename in oldContents.keys():
        if filename not in newContents:
            destFile = os.path.join(destinationFolder, filename.lstrip('/'))
            if os.path.isfile(destFile):
                toRemove.append(filename)
    return toRemove

def getFTPContents(ftp):
    def walkFTP(ftp, subFraction = None, currentProgress = None):
        if subFraction is None:
            subFraction = 1.0
        if currentProgress is None:
            currentProgress = 0.0

        percentage = 100 * currentProgress
        sys.stdout.write("[%d%% done] Getting repository contents\r" % percentage)
        sys.stdout.flush()

        path = ftp.pwd()    # TODO relpath to root path
        contentsList = []
        directories = []
        s = ftp.retrlines('LIST', contentsList.append)

        for line in contentsList:
            if line.startswith('d'): # is a folder
                directories.append(line.split()[8])

        if len(directories):
            subFraction /= float(len(directories))

        filesList = [f for f in ftp.nlst() if f not in directories]
        if len(filesList):
            filesFraction = 1.0/len(filesList)
        result = []
        for fname in filesList:
            mtime = ftp.sendcmd('MDTM %s' % fname)
            mtime = int(mtime[3:].strip())
            #mtime = int(time.mktime(time.strptime(mtime[3:].strip(), '%Y%m%d%H%M%S')))
            fpath = os.path.join(path, fname)
            result.append( (fpath, mtime) )
            percentage += 100 * (filesFraction * subFraction)
            sys.stdout.write("[%d%% done] Getting repository contents\r" % percentage)
            sys.stdout.flush()

        for dir_ in directories:
            ftp.cwd(dir_.replace('\\', '/'))
            result.extend( walkFTP(ftp, subFraction, currentProgress) )
            ftp.cwd('..')
            currentProgress += subFraction

        return result

    print 'Retrieving new repository content...'
    rootPath = ftp.pwd()
    contentsList = walkFTP(ftp)
    sys.stdout.write("[100% done] Getting repository contents\r")
    sys.stdout.write('\n')
    sys.stdout.flush()
    result = {}
    # make paths relative to rootpath
    for (p, mtime) in contentsList:
        result[os.path.relpath(p, rootPath)] = mtime

    return result

def downloadFromHTTP(url, destination):
    import urllib

    def chunk_report(bytes_so_far, chunk_size, total_size):
        percentage = float(bytes_so_far) / total_size
        percentage = round(percentage*100, 2)
        sys.stdout.write("  Downloaded %d%% of %d bytes\r" % (percentage, total_size))
        sys.stdout.flush()

        if bytes_so_far >= total_size:
            sys.stdout.write('\n')

    def chunk_read(response, chunk_size=512, report_hook=None):
        total_size = response.info().getheader('Content-Length').strip()
        total_size = int(total_size)
        bytes_so_far = 0

        while True:
            chunk = response.read(chunk_size)
            f.write(chunk)
            bytes_so_far += len(chunk)

            if not chunk:
                break

            if report_hook:
                report_hook(bytes_so_far, chunk_size, total_size)

        return bytes_so_far

    f = open(destination, 'wb')
    response = urllib.urlopen(url)
    if response.getcode() != 200:
        raise RuntimeError('Failed to download file %s (error code %s)' % (url, response.getcode()))
    chunk_read(response, report_hook=chunk_report)
    f.close()

def isArchived(ftp):
    return 'archive_url.txt' in ftp.nlst()

def getArgs():
    if len(sys.argv) < 2:
        return dict()

    import argparse    # requires python >= 2.7
    parser = argparse.ArgumentParser()

    # optional arguments
    parser.add_argument('-v', '--version', action='version', version=version())
    parser.add_argument("-d", "--nodelete", action="store_true", help="Don't delete old version when updating files")

    # optional positional arguments
    parser.add_argument("repository", default=defaultRepo, nargs='?', help="Alternative repository name to download from (optional)")

    argOptions = vars(parser.parse_args())
    return argOptions

def getVersion():
    """
    Version of MakeHuman software
    """
    import sys
    sys.path = ["."] + sys.path
    import makehuman
    return '.'.join([str(i) for i in makehuman.version[:2]])


if __name__ == '__main__':
    global DONTREMOVE

    args = getArgs()
    repo = args.get('repository', defaultRepo)
    for c in ['.', '/', '\\']:
        if c in repo:
            raise RuntimeError('Invalid argument for "repository", illegal character')
    DONTREMOVE = args.get('nodelete', default_nodelete)

    # Obtain MH version to download assets for
    version = getVersion()

    print 'Refreshing assets from repository "%s" (version %s)' % (repo, version)

    ftpPath = os.path.join(ftpPath, version.lstrip('/'), repo.lstrip('/'))
    ftpPath = os.path.normpath(ftpPath)
    ## Use simple sync mechanism, maybe in the future we can use rsync over http?
    # Download contents list
    baseName = os.path.basename(ftpPath)
    contentsFile = getSysPath('%s_%s_contents.txt' % (baseName, version.replace('.','-')))
    if os.path.isfile(contentsFile):
        # Parse previous contents file
        oldContents = parseContentsFile(contentsFile)
        if len(oldContents) > 0 and len(str(oldContents[oldContents.keys()[0]])) < 5:
            # Ignore old style contents file
            oldContents = {}
    else:
        oldContents = {}

    # Setup FTP connection
    print "Connecting to FTP..."
    ftp = FTP(ftpUrl)
    ftp.login()
    ftp.cwd(ftpPath.replace('\\', '/'))

    # Verify if there is an archive reference URL
    if isArchived(ftp):
        print "Redirected to asset archive"
        archiveUrl = downloadFromFTP(ftp, 'archive_url.txt', None).strip()
        filename = os.path.basename(archiveUrl)
        zipDest = os.path.join(getSysPath(), filename)
        if os.path.exists(zipDest):
            print "Archive %s already exists, not downloading again." % zipDest
            sys.exit()
        print "Downloading archive from HTTP (%s)" % archiveUrl
        # Download and extract archive
        downloadFromHTTP(archiveUrl, zipDest)
        print "Extracting zip archive..."
        import zipfile
        zFile = zipfile.ZipFile(zipDest)
        zFile.extractall(getSysDataPath())

        print "All done."
        sys.exit()

    # Get contents from FTP
    newContents = getFTPContents(ftp)

    destinationFolder = getSysDataPath()
    toDownload = getNewFiles(oldContents, newContents, destinationFolder)
    toRemove = getRemovedFiles(oldContents, newContents, destinationFolder)

    # Remove files removed on FTP
    for filePath in toRemove:
        filename = os.path.join(destinationFolder, filePath.lstrip('/'))

        if not isSubPath(filename, destinationFolder):
            raise RuntimeError("ERROR: File destinations are jailed inside the sys data path (%s), destination path (%s) tries to escape!" % (destinationFolder, filename))

        if DONTREMOVE:
            newFile = filename + '.removedasset'
            i = 0
            while os.path.isfile(newFile):
                newFile = filename + '.' + str(i) + '.removedasset'
                i = i+1
            shutil.move(filename, newFile)
            print "Moved removed file to %s (removed from FTP)" % newFile
        else:
            print "Removing file %s (removed from FTP)" % filename
            os.remove(filename)

    TOTAL_FILES = len(toDownload)

    fIdx = 0
    for filePath in toDownload:
        filename = os.path.join(destinationFolder, filePath.lstrip('/'))

        if not isSubPath(filename, destinationFolder):
            raise RuntimeError("ERROR: File destinations are jailed inside the sys data path (%s), destination path (%s) tries to escape!" % (destinationFolder, filename))

        if os.path.exists(filename) and DONTREMOVE:
            newFile = filename + '.oldasset'
            i = 0
            while os.path.exists(newFile):
                newFile = filename + '.' + str(i) + '.oldasset'
                i = i+1
            shutil.move(filename, newFile)
            print "Moved old version of updated file to %s" % newFile

        fileProgress = round(100 * float(fIdx)/TOTAL_FILES, 2)
        downloadFile(ftp, filePath, filename, fileProgress)
        fIdx += 1

    ftp.close()

    writeContentsFile(contentsFile, newContents)

    print "All done."

