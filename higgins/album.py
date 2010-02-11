# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.http.routes import Dispatcher
from higgins.db import db, Album
from higgins.rest import RestResponse, RestInvalidInputError, RestInternalServerError
from higgins.logger import Loggable

class AlbumMethods(Dispatcher, Loggable):
    log_domain = "core"

    def __init__(self):
        Dispatcher.__init__(self)
        self.addRoute('list$', self.listAlbums, allowedMethods=('POST'))
        self.addRoute('get$', self.getAlbum, allowedMethods=('POST'))
        self.addRoute('update$', self.updateAlbum, allowedMethods=('POST'))
        self.addRoute('delete$', self.deleteAlbum, allowedMethods=('POST'))

    def updateAlbum(self, request):
        """
        change metadata about an album.  Requires albumID be specified.  Any other
        keyvalue will be interpreted as album metadata which should be updated.
        Unknown keyvalues will be ignored.
        """
        try:
            self.log_debug("updateAlbum: %s" % request.post)
            # check for required params before updating anything in the database
            albumID = request.post.get('albumID', [None])[0]
            if albumID == None:
                return RestInvalidInputError("Missing albumID")
            albumID = int(albumID)
            title = request.post.get('title', [None])[0]
            if title != None:
                title = unicode(title)
            genre = request.post.get('genre', [None])[0]
            if genre != None:
                genre = unicode(genre)
            yearReleased = request.post.get('yearReleased', [None])[0]
            if yearReleased != None:
                if yearReleased == '':
                    yearReleased = -1
                else:
                    yearReleased = int(yearReleased)
            # update the playlist object
            album = db.get(Album, Album.storeID==albumID)
            if title:
                album.name = title
            if yearReleased:
                if yearReleased < 0:
                    album.releaseDate = None
                else:
                    album.releaseDate = yearReleased
            return RestResponse()
        except Exception, e:
            self.log_debug("failed to update Album: %s" % e)
            return RestInternalServerError()
    
    def listAlbums(self, request):
        return RestInternalServerError("not yet implemented")
    
    def getAlbum(self, request):
        return RestInternalServerError("not yet implemented")
    
    def deleteAlbum(self, request):
        return RestInternalServerError("not yet implemented")
