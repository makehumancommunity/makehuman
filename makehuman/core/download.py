#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Marc Flerackers

**Copyright(c):**      MakeHuman Team 2001-2014

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------

TODO
"""

import os
import urllib2
import mh
from threading import Thread
import log

class MediaSync(Thread):
    
    def __init__(self, app, path, url, callback=None):
        
        Thread.__init__(self)
        self.app = app
        self.path = path
        self.url = url
        self.callback = callback
        
    def run(self):
        
        cache = DownloadCache(self.path)
        mh.callAsyncThread(self.app.progress, 0.0, 'Downloading media list')
        success, code = cache.download(os.path.join(self.url, 'media.ini'))
        if success:
            f = open(os.path.join(self.path, 'media.ini'), 'r')
            filenames = f.readlines()
            n = float(len(filenames))
            for index, filename in enumerate(filenames):
                try:
                    filename = filename.split()[0]
                    mh.callAsyncThread(self.app.progress, index/n, 'Downloading %s' % filename)
                    url = os.path.join(self.url, filename)
                    success, code = cache.download(url)
                except:
                    pass
            f.close()
            mh.callAsyncThread(self.app.progress, 1.0)
        else:
            mh.callAsyncThread(self.app.progress, 1.0)
            mh.callAsyncThread(self.app.prompt, 'Error', 'Failed to sync media from %s, error %d.' % (self.path, code), 'OK')
            
        if self.callback:
             mh.callAsyncThread(self.callback)

class DownloadCache():

    class NotModifiedHandler(urllib2.BaseHandler):
  
        def http_error_304(self, req, fp, code, message, headers):
            
            addinfourl = urllib2.addinfourl(fp, headers, req.get_full_url())
            addinfourl.code = code
            
            return addinfourl
        
    def __init__(self, path):
    
        self.path = path
            
        cachePath = os.path.join(self.path, 'cache.ini')
        self.cache = {}
        if os.path.exists(cachePath):
            try:
                with open(cachePath, 'r') as f:
                    self.cache = mh.parseINI(f.read())
            except ValueError:
                os.remove(cachePath)
            
    def download(self, url):
        
        filename = os.path.basename(url)
        
        if os.path.exists(os.path.join(self.path, filename)):
            etag, modified = self.cache.get(filename, (None, None))
        else:
            etag, modified = None, None
        
        try:
            downloaded, etag, modified, data = self.__downloadConditionally(url, etag, modified)
        except urllib2.HTTPError, e:
            log.notice('Could not download %s: %s', url, e)
            return False, e.code
                
        if downloaded:
            with open(os.path.join(self.path, filename), 'wb') as f:
                f.write(data)
            self.cache[filename] = (etag, modified)
            
        cachePath = os.path.join(self.path, 'cache.ini')
        with open(cachePath, 'w') as f:
            f.write(mh.formatINI(self.cache))

        return True, (200 if downloaded else 304)
        
    @classmethod
    def __downloadConditionally(cls, url, etag=None, modified=None):
    
        request = urllib2.Request(url)
        
        if etag:
            request.add_header("If-None-Match", etag)
      
        if modified:
            request.add_header("If-Modified-Since", modified)
     
        opener = urllib2.build_opener(cls.NotModifiedHandler())
        handle = opener.open(request)
        headers = handle.info()
     
        if hasattr(handle, 'code') and handle.code == 304:
            return False, None, None, None
        else:
            return True, headers.getheader("ETag"), headers.getheader("Last-Modified"), handle.read()
