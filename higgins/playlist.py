# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from epsilon.extime import Time
from higgins.http.routes import Dispatcher
from higgins.db import db, Song, File, Playlist
from higgins.rest import RestResponse, RestInternalServerError, RestInvalidInputError
from higgins.logger import Loggable

class PlaylistMethods(Dispatcher, Loggable):
    log_domain = "core"

    def __init__(self):
        self.addRoute('list$', self.listPlaylists, allowedMethods=('POST'))
        self.addRoute('get$', self.getPlaylist, allowedMethods=('POST'))
        self.addRoute('add$', self.addPlaylist, allowedMethods=('POST'))
        self.addRoute('update$', self.updatePlaylist, allowedMethods=('POST'))
        self.addRoute('delete$', self.deletePlaylist, allowedMethods=('POST'))
        self.addRoute('addItems$', self.addPlaylistItems, allowedMethods=('POST'))
        self.addRoute('reorderItems$', self.reorderPlaylistItems, allowedMethods=('POST'))
        self.addRoute('deleteItems$', self.deletePlaylistItems, allowedMethods=('POST'))

    def listPlaylists(request):
        """
        List songs in the database.  if offset is specified, then list songs
        starting at the offset.  if limit is specified, return at most limit songs.
        Limit defaults to 100, and cannot be set higher than 100.
        """
        try:
            # create the song object
            pl_list = []
            q = db.query(Playlist)
            for playlist in q:
                pl_list.append({
                    'playlistID': playlist.storeID,
                    'title': playlist.name,
                    'nitems': playlist.length
                    })
            response = { 'playlists': pl_list, 'nitems': q.count() }
            return RestResponse(response)
        except Exception, e:
            self.log_debug("failed to list playlists: %s" % e)
            return RestInternalServerError()
    
    def addPlaylist(request):
        """
        Add a playlist to the database.  Requires that title be specified.
        """
        try:
            # check for required params before adding anything to the database
            title = request.post.get('title', [None])[0]
            if title == None:
                return RestInvalidInputError("Missing title")
            title = unicode(title)
            self.log_debug("new playlist title is '%s'" % title)
            # create the song object
            playlist = db.create(Playlist, name=title, dateAdded=Time())
            self.log_debug("added new playlist '%s'" % title)
            response = { 'playlistID': playlist.storeID, 'title': title }
            return RestResponse(response)
        except Exception, e:
            self.log_debug("failed to add playlist: %s" % e)
            return RestInternalServerError()
    
    def getPlaylist(request):
        """
        Gets metadata associated with a playlist.  Requires that playlistID be
        specified.
        """
        try:
            # check for required params
            playlistID = request.post.get('playlistID', [None])[0]
            if playlistID == None:
                return RestInvalidInputError("Missing playlistID")
            playlistID = int(playlistID)
            # look up the playlist object
            playlist = db.get(Playlist, Playlist.storeID==playlistID)
            songs = [song.storeID for song in playlist.listSongs()]
            response = { 'playlistID': playlist.storeID, 'title': playlist.name, 'songs': songs, 'nitems': len(songs) }
            return RestResponse(response)
        except Exception, e:
            self.log_debug("failed to get playlist: %s" % e)
            return RestInternalServerError()
    
    def updatePlaylist(request):
        """
        change metadata about a playlist.  Requires playlistID be specified.  Any
        other keyvalue will be interpreted as playlist metadata which should be updated.
        Unknown keyvalues will be ignored.
        """
        try:
            # check for required params before adding anything to the database
            playlistID = request.post.get('playlistID', [None])[0]
            if playlistID == None:
                return RestInvalidInputError("Missing playlistID")
            playlistID = int(playlistID)
            # update the playlist object
            playlist = db.get(Playlist, Playlist.storeID==playlistID)
            if 'title' in request.post:
                playlist.name = unicode(request.post.get('title')[0])
            self.log_debug("updated playlist '%s'" % playlist.name)
            response = { 'playlistID': playlist.storeID, 'title': playlist.name }
            return RestResponse(response)
        except Exception, e:
            self.log_debug("failed to add playlist: %s" % e)
            return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)
    
    def deletePlaylist(request):
        """
        delete a playlist.  Requires playlistID be specified.
        """
        try:
            # check for required params before adding anything to the database
            playlistID = request.post.get('playlistID', [None])[0]
            if playlistID == None:
                return RestInvalidInputError("Missing playlistID")
            playlistID = int(playlistID)
            # delete the playlist object
            playlist = db.delete(Playlist, Playlist.storeID==playlistID)
            self.log_debug("removed playlist %i" % playlistID)
            return RestResponse()
        except Exception, e:
            self.log_debug("failed to add playlist: %s" % e)
            return RestInternalServerError()
    
    def addPlaylistItems(request):
        try:
            # check for required params
            playlistID = request.post.get('playlistID', [None])[0]
            if playlistID == None:
                return RestInvalidInputError("Missing playlistID")
            playlistID = int(playlistID)
            songIDs = request.post.get('songIDs', None)
            if songIDs == None:
                return RestInvalidInputError("Missing songIDs")
            # add songs to the playlist object
            playlist = db.get(Playlist, Playlist.storeID==playlistID)
            for songID in songIDs:
                song = db.get(Song, Song.storeID==songID)
                playlist.appendSong(song)
                self.log_debug("added %s to %s" % (song.name, playlist.name))
            return RestResponse()
        except Exception, e:
            self.log_debug("failed to add playlist: %s" % e)
            return RestInternalServerError()
    
    def reorderPlaylistItems(request):
        """
        change the item ordering in a playlist.
        """
        return RestInternalServerError("not yet implemented")
    
    def deletePlaylistItems(request):
        """
        remove items from a playlist.
        """
        return RestInternalServerError("not yet implemented")
