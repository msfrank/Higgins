# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.http.routes import Dispatcher
from higgins.db import db, Artist
from higgins.rest import RestResponse, RestInvalidInputError, RestInternalServerError
from higgins.logger import Loggable

class ArtistMethods(Dispatcher, Loggable):
    log_domain = "core"

    def __init__(self):
        Dispatcher.__init__(self)
        self.addRoute('list$', self.listArtists, allowedMethods=('POST'))
        self.addRoute('get$', self.getArtist, allowedMethods=('POST'))
        self.addRoute('update$', self.updateArtist, allowedMethods=('POST'))
        self.addRoute('delete$', self.deleteArtist, allowedMethods=('POST'))

    def updateArtist(self, request):
        """
        change metadata about an artist.  Requires artistID be specified.  Any other
        keyvalue will be interpreted as artist metadata which should be updated.
        Unknown keyvalues will be ignored.
        """
        try:
            # check for required params before updating anything in the database
            artistID = request.post.get('artistID', [None])[0]
            if artistID == None:
                return RestInvalidInputError("Missing artistID")
            artistID = int(artistID)
            name = request.post.get('name', [None])[0]
            if name != None:
                name = unicode(name)
            # update the playlist object
            artist = db.get(Artist, Artist.storeID==artistID)
            if name:
                artist.name = name
            return RestResponse()
        except Exception, e:
            self.log_debug("failed to update Artist: %s" % e)
            return RestInternalServerError()
    
    def listArtists(self, request):
        return RestInternalServerError("not yet implemented")
    
    def getArtist(self, request):
        return RestInternalServerError("not yet implemented")
    
    def deleteArtist(self, request):
        return RestInternalServerError("not yet implemented")
