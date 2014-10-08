#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
Metadata Search Functionality for Tagged Settings Libraries.

**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Manuel Bastioni

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

This module implements a simple set of algorithms to handle MakeHuman 
metadata tags within large files. This is used to search for, load and 
save records in text files that are used to index library files. 
Each record in the text file contains a recordID that is the full file 
system path to a MakeHuman library file and a sequence of keywords 
attributed to that library file.  

This module has been tested with 30000 objects with 400000 tags, on an old PC,
with the following results:

- Load record using recordID, worst case:  0.00368905067444 sec
- Search records using tags, worst case:  0.0546329021454 sec
- Save/update records: 0.210602998734 sec

Because of these performance figures and because of MakeHuman file management requirements 
(single user, local files, basic usage, etc.), we have decided to use this baby-proof module 
to add new dependencies instead of using an ultra powerful external database that would be
of limited value in the context required for MakeHuman.

If the following content is contained in a plain text file called \"tags.txt\"...

::

    c:\MakeHuman\objectlibrary\obj1.obj hand long fist clenched
    c:\MakeHuman\objectlibrary\obj2.obj leg calf muscular
    c:\MakeHuman\objectlibrary\obj3.obj nose broad hooked
    c:\MakeHuman\objectlibrary\obj4.obj eye brown 
    c:\MakeHuman\objectlibrary\obj5.obj eyelash thick long
    c:\MakeHuman\objectlibrary\obj6.obj lips lush
    c:\MakeHuman\objectlibrary\obj7.obj sheyenne indian aboriginal
    ...

the following examples illustrate the use of the load search and save functions:

::

    r1 = loadRecord('tags.txt', 'c:\MakeHuman\objectlibrary\obj2.obj')
    // Sets r1 to be the list [\"c:\MakeHuman\objectlibrary\obj2.obj\",\"leg\",\"calf\",\"muscular\"]

    r2 = searchRecord('tags.txt', 'eye')
    // Sets r2 to be the list [\"c:\MakeHuman\objectlibrary\obj4.obj\",\"c:\MakeHuman\objectlibrary\obj5.obj\",\"c:\MakeHuman\objectlibrary\obj7.obj\"]

    recordToSave = 'c:\MakeHuman\objectlibrary\obj5.obj eyelash thick long black'
    saveRecord('tags.txt', recordToSave)
    // Replaces the existing 'obj5' record with the new record in the file on disk.

"""

__docformat__ = 'restructuredtext'

import time
import log

def joinRecords(record1, record2):
    """
    This function takes two records and returns a single 
    concatenated record with the same record ID as the first.  
    The record is returned as a string containing the record ID at the start.
    
    Parameters
    ----------
   
    record1:     
      *list of strings*.  The first record.
      
    record2:     
      *list of strings*.  The records to append to the first record.
    """

    recordID = record1[0]
    fields1 = set(record1[1:])
    fields2 = set(record2[1:])
    joinedRecord = fields1.union(fields2)
    joinedRecord = list(joinedRecord)
    joinedRecord.insert(0, recordID)
    log.message('joining %s', joinedRecord)
    return ' '.join(joinedRecord)


def loadRecord(archivePath, recordID):
    """
    This function reads the file specified, searches for the specified record ID
    and returns that record if found or *None* if not found. 
    The record is returned as a list of strings containing the record ID in the '0' 
    element and successive fields in the following elements.
    
    Parameters
    ----------
   
    archivePath:     
      *string*.  The file system path to the file containing the set of records.
      
    recordID:     
      *string*.  The ID of the record to load.
    """

    time1 = time.time()
    f = open(archivePath)
    record = None
    for line in f:
        if line.find(recordID) != -1:
            record = line.split()
            log.message('Found %s fields in %s sec', len(record), time.time() - time1)
            break
    f.close()
    return record


def searchRecord(archivePath, field):
    """
    This function reads the file specified, searches for the specified field
    and returns a list of the records that contain that field 
    (ie a list of strings containing recordIDs).
    
    Parameters
    ----------
   
    archivePath:     
      *string*.  The file system path to the file containing the set of records.
      
    field:     
      *string*.  The field to search for.
    """

    time1 = time.time()
    f = open(archivePath)
    recordIDs = []
    for line in f:
        if line.find(field) != -1:
            recordIDs.append(line.split()[0])
    f.close()
    log.message('Found %s records in %s sec', len(recordIDs), time.time() - time1)
    return recordIDs


def saveRecord(archivePath, recordToSave):
    """
    This function searches a file to see if the specified record ID exists, 
    building and saving a consolidated record if it does and appending a new record to 
    the end of the file if it doesn't.
    
    Parameters
    ----------
   
    archivePath:     
      *string*.  The file system path to the file containing the set of records.
      
    recordToSave:     
      *string*.  The record to save.
    """

    time1 = time.time()
    recordID = recordToSave.split()[0]
    records = []
    isExistent = None
    try:
        f = open(archivePath)
        i = 0
        for line in f:
            if line.find(recordID) != -1:
                i += 1
                isExistent = 1
                oldRecord = line.split()
                newRecord = recordToSave.split()
                if oldRecord[0] == recordID:
                    line = joinRecords(newRecord, oldRecord)
            records.append(line.strip())
        f.close()
    except:
        log.message('A new %s archive will be created', archivePath)

    if not isExistent:
        records.append(recordToSave)

    f = open(archivePath, 'w')
    for record in records:
        f.write('%s\n' % record)
    f.close()
    log.message('Record %s saved in %s sec', recordID, time.time() - time1)


