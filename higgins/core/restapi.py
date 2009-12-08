# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os
import simplejson
from epsilon.extime import Time
from higgins.db import db, Artist, Album, Song, Genre, File, Playlist
from higgins.core.dispatcher import Dispatcher
from higgins.core.logger import logger
from higgins.http.http_headers import MimeType
from higgins.http.http import Response

NO_ERROR = 0
ERROR_INTERNAL_SERVER_ERROR = 1
ERROR_INVALID_INPUT = 2

_APIErrors = [
    "No Error",
    "Internal Server Error",
    "Validation Error"
    ]

class RestResponse(Response):
    def __init__(self, data={}, type='json'):
        headers = {}
        if type == 'json':
            data['status'] = NO_ERROR
            headers['content-type'] = MimeType.fromString('application/json')
            stream = simplejson.dumps(data)
        else:
            raise Exception('Unknown response format %s' % type)
        Response.__init__(self, 200, headers, stream)

class RestErrorResponse(Response):
    def __init__(self, status, extra=None, type='json'):
        headers = {}
        if type == 'json':
            data = { 'status': status, 'error': _APIErrors[status] }
            if extra:
                data['extra'] = extra
            headers['content-type'] = MimeType.fromString('application/json')
            stream = simplejson.dumps(data)
        else:
            raise Exception('Unknown response format %s' % type)
        Response.__init__(self, 200, headers, stream)

class APIResource(Dispatcher):
    def __init__(self):
        Dispatcher.__init__(self)
        self.addRoute('songs$', self.listSongs, allowedMethods=('POST'))
        self.addRoute('song/add$', self.addSong, allowedMethods=('POST'), acceptFile=self.acceptSongItem)
        self.addRoute('song/update$', self.updateSong, allowedMethods=('POST'))
        self.addRoute('song/delete$', self.deleteSong, allowedMethods=('POST'))
        self.addRoute('album/update$', self.updateAlbum, allowedMethods=('POST'))
        self.addRoute('artist/update$', self.updateArtist, allowedMethods=('POST'))
        self.addRoute('playlists$', self.listPlaylists, allowedMethods=('POST'))
        self.addRoute('playlist/add$', self.addPlaylist, allowedMethods=('POST'))
        self.addRoute('playlist/get$', self.getPlaylist, allowedMethods=('POST'))
        self.addRoute('playlist/update$', self.updatePlaylist, allowedMethods=('POST'))
        self.addRoute('playlist/delete$', self.deletePlaylist, allowedMethods=('POST'))
        self.addRoute('playlist/addItems$', self.addPlaylistItems, allowedMethods=('POST'))
#self.addRoute('playlist/reorderItems$', self.reorderPlaylistItems, allowedMethods=('POST'))
#self.addRoute('playlist/deleteItems$', self.addPlaylistItems, allowedMethods=('POST'))

    def acceptSongItem(self, request, mimetype, subheaders):
        return None

    def listSongs(self, request):
        try:
            offset = request.post.get('offset', None)
            if offset != None:
                offset = int(offset)
            limit = request.post.get('limit', None)
            if limit != None:
                limit = int(limit)
            else:
                limit = 100
            if limit > 100:
                limit = 100
            items = []
            for song in db.query(Song, offset=offset, limit=limit):
                items.append({'name': song.name,
                             'songID': song.storeID,
                             'artistID': song.artist.storeID,
                             'albumID': song.album.storeID
                             })
            if offset == None:
                offset = 0
            response = {'nitems': len(items), 'offset': offset, 'items': items}
            return RestResponse(response)
        except Exception, e:
            logger.log_debug("failed to list songs: %s" % e)
            return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)

    def addSong(self, request):
        try:
            ####################################################################
            # check for required params before adding anything to the database #
            ####################################################################
            title = request.post.get('title', None)
            if title == None:
                return RestErrorResponse(ERROR_INVALID_INPUT, "Missing required form item 'title'")
            if 'file' in request.post:
                path = request.post.get('file')
            elif 'file' in request.files:
                path = request.files[0]
            else:
                return RestErrorResponse(ERROR_INVALID_INPUT, "Missing required form item 'file'")
            logger.log_debug("referencing %s" % request.post['file'])
            if not os.access(path, os.R_OK):
                return RestErrorResponse(ERROR_INVALID_INPUT, "higgins doesn't have permission to read file")
            if not 'mimetype' in request.post:
                return RestErrorResponse(ERROR_INVALID_INPUT, "Missing required form item 'mimetype'")
            size = int(os.stat(path).st_size)
            # create the file object
            file = db.create(File, path=path, size=size, MIMEType=request.post.get('mimetype'))
            # create or get the artist object
            value = request.post.get('artist', '')
            artist,artistIsNew = db.getOrCreate(Artist, name=value)
            if artistIsNew:
                artist.dateAdded = Time()
            # create or get the genre object
            value = request.post.get('genre', '')
            genre,genreIsNew = db.getOrCreate(Genre, name=value)
            if genreIsNew:
                genre.dateAdded = Time()
            # create or get the album object
            value = request.post.get('album', '')
            album,albumIsNew = db.getOrCreate(Album, name=value, artist=artist, genre=genre)
            if albumIsNew:
                album.dateAdded = Time()
            # create the song object
            song = db.create(Song, name=title, album=album, artist=artist, file=file, dateAdded=Time())
            if 'trackNumber' in request.post:
                song.trackNumber = int(request.post.get('trackNumber'))
            if 'volumeNumber' in request.post:
                song.volumeNumber = int(request.post.get('volumeNumber'))
            if 'length' in request.post:
                song.duration = int(request.post.get('length'))
            logger.log_debug("successfully added new song '%s'" % title)
            response = {
                'songID': song.storeID,
                'artistID': artist.storeID,
                'albumID': album.storeID,
                'genreID': genre.storeID
                }
            return RestResponse(response)
        except Exception, e:
            logger.log_debug("failed to add song: %s" % e)
            return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)

    def updateSong(self, request):
        return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)

    def deleteSong(self, request):
        return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)

    def updateAlbum(self, request):
        try:
            logger.log_debug("updateAlbum: %s" % request.post)
            # check for required params before updating anything in the database
            albumID = request.post.get('albumID', [None])[0]
            if albumID == None:
                return RestErrorResponse(ERROR_INVALID_INPUT, "Missing albumID")
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
            logger.log_debug("failed to update Album: %s" % e)
            return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)

    def updateArtist(self, request):
        try:
            # check for required params before updating anything in the database
            artistID = request.post.get('artistID', [None])[0]
            if artistID == None:
                return RestErrorResponse(ERROR_INVALID_INPUT, "Missing artistID")
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
            return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)

    def listPlaylists(self, request):
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
            logger.log_debug("failed to list playlists: %s" % e)
            return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)

    def addPlaylist(self, request):
        try:
            # check for required params before adding anything to the database
            title = request.post.get('title', [None])[0]
            if title == None:
                return RestErrorResponse(ERROR_INVALID_INPUT, "Missing title")
            title = unicode(title)
            logger.log_debug("new playlist title is '%s'" % title)
            # create the song object
            playlist = db.create(Playlist, name=title, dateAdded=Time())
            logger.log_debug("added new playlist '%s'" % title)
            response = { 'playlistID': playlist.storeID, 'title': title }
            return RestResponse(response)
        except Exception, e:
            logger.log_debug("failed to add playlist: %s" % e)
            return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)

    def getPlaylist(self, request):
        try:
            # check for required params
            playlistID = request.post.get('playlistID', [None])[0]
            if playlistID == None:
                return RestErrorResponse(ERROR_INVALID_INPUT, "Missing playlistID")
            playlistID = int(playlistID)
            # look up the playlist object
            playlist = db.get(Playlist, Playlist.storeID==playlistID)
            songs = [song.storeID for song in playlist.listSongs()]
            response = { 'playlistID': playlist.storeID, 'title': playlist.name, 'songs': songs, 'nitems': len(songs) }
            return RestResponse(response)
        except Exception, e:
            logger.log_debug("failed to add playlist: %s" % e)
            return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)

    def updatePlaylist(self, request):
        try:
            # check for required params before adding anything to the database
            playlistID = request.post.get('playlistID', [None])[0]
            if playlistID == None:
                return RestErrorResponse(ERROR_INVALID_INPUT, "Missing playlistID")
            playlistID = int(playlistID)
            title = request.post.get('title', [None])[0]
            if title == None:
                return RestErrorResponse(ERROR_INVALID_INPUT, "Missing title")
            title = unicode(title)
            # update the playlist object
            playlist = db.get(Playlist, Playlist.storeID==playlistID)
            playlist.name = title
            logger.log_debug("updated playlist '%s'" % title)
            response = { 'playlistID': playlist.storeID, 'title': title }
            return RestResponse(response)
        except Exception, e:
            logger.log_debug("failed to add playlist: %s" % e)
            return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)

    def deletePlaylist(self, request):
        try:
            # check for required params before adding anything to the database
            playlistID = request.post.get('playlistID', [None])[0]
            if playlistID == None:
                return RestErrorResponse(ERROR_INVALID_INPUT, "Missing playlistID")
            playlistID = int(playlistID)
            # delete the playlist object
            playlist = db.delete(Playlist, Playlist.storeID==playlistID)
            logger.log_debug("successfully removed playlist %i" % playlistID)
            return RestResponse()
        except Exception, e:
            logger.log_debug("failed to add playlist: %s" % e)
            return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)

    def addPlaylistItems(self, request):
        try:
            # check for required params
            playlistID = request.post.get('playlistID', [None])[0]
            if playlistID == None:
                return RestErrorResponse(ERROR_INVALID_INPUT, "Missing playlistID")
            playlistID = int(playlistID)
            songIDs = request.post.get('songIDs', None)
            if songIDs == None:
                return RestErrorResponse(ERROR_INVALID_INPUT, "Missing songIDs")
            # delete the playlist object
            playlist = db.get(Playlist, Playlist.storeID==playlistID)
            for songID in songIDs:
                song = db.get(Song, Song.storeID==songID)
                playlist.appendSong(song)
                logger.log_debug("added %s to %s" % (song.name, playlist.name))
            return RestResponse()
        except Exception, e:
            logger.log_debug("failed to add playlist: %s" % e)
            return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)
