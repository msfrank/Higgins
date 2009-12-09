# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.db import db, Artist
from higgins.core.rest import RestResponse, RestInvalidInputError, RestInternalServerError
from higgins.core.logger import logger

def updateArtist(request):
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
        logger.log_debug("failed to update Artist: %s" % e)
        return RestInternalServerError()

def listArtists(request):
    return RestInternalServerError("not yet implemented")

def getArtist(request):
    return RestInternalServerError("not yet implemented")

def deleteArtist(request):
    return RestInternalServerError("not yet implemented")
