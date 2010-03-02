# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os
from higgins.http.routes import Dispatcher
from higgins.db import db, Artist, Album, Song, Genre, File
from higgins.rest import RestResponse, RestInternalServerError, RestInvalidInputError
from higgins.logger import Loggable

import warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from epsilon.extime import Time

class SongMethods(Dispatcher, Loggable):
    def __init__(self):
        Dispatcher.__init__(self)
        self.addRoute('list$', self.listSongs, allowedMethods=('POST'))
        self.addRoute('get$', self.getSong, allowedMethods=('POST'))
        self.addRoute('add$', self.addSong, allowedMethods=('POST'), acceptFile=self.acceptSongItem)
        self.addRoute('update$', self.updateSong, allowedMethods=('POST'))
        self.addRoute('delete$', self.deleteSong, allowedMethods=('POST'))

    def acceptSongItem(self, request, mimetype, subheaders):
        """
        Determine whether to accept an uploaded song.  Returning None means to
        reject the upload and stop reading the POST input, otherwise returning
        a file object will cause the upload to be written to the file.
        """
        return None

    def listSongs(self, request):
        """
        List songs in the database.  if offset is specified, then list songs
        starting at the offset.  if limit is specified, return at most limit songs.
        Limit defaults to 100, and cannot be set higher than 100.
        """
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
            error = "failed to list songs: %s" % e
            self.log_debug(error)
            return RestInternalServerError(error)
    
    def addSong(self, request):
        """
        Add a song to the database.  Requires that title, file, mimetype, and length
        be specified.  optionally, artist, genre, album, track-number, and volume-number
        can be specified.  if artist, album, or genre don't exist, they will be created.
        """
        try:
            ####################################################################
            # check for required params before adding anything to the database #
            ####################################################################
            title = request.post.get('title', None)
            if title == None:
                return RestInvalidInputError("Missing required form item 'title'")
            if 'file' in request.post:
                path = request.post.get('file')
            elif 'file' in request.files:
                path = request.files[0]
            else:
                return RestInvalidInputError("Missing required form item 'file'")
            self.log_debug("referencing %s" % request.post['file'])
            if not os.access(path, os.R_OK):
                return RestInvalidInputError("higgins doesn't have permission to read file")
            if not 'mimetype' in request.post:
                return RestInvalidInputError("Missing required form item 'mimetype'")
            size = int(os.stat(path).st_size)
            if not 'length' in request.post:
                return RestInvalidInputError("Missing required form item 'length'")
            duration = int(request.post.get('length'))
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
            song = db.create(Song, name=title, album=album, artist=artist, file=file, dateAdded=Time(), duration=duration)
            if 'track-number' in request.post:
                song.trackNumber = int(request.post.get('track-number'))
            if 'volume-number' in request.post:
                song.volumeNumber = int(request.post.get('volume-number'))
            self.log_debug("successfully added new song '%s'" % title)
            response = {
                'songID': song.storeID,
                'artistID': artist.storeID,
                'albumID': album.storeID,
                'genreID': genre.storeID
                }
            return RestResponse(response)
        except Exception, e:
            self.log_debug("failed to add song: %s" % e)
            return RestInternalServerError()
    
    def getSong(self, request):
        return RestInternalServerError("not yet implemented")
        
    def updateSong(self, request):
        """
        change metadata about a song.  Requires songID be specified.  Any other
        keyvalue will be interpreted as song metadata which should be updated.
        Unknown keyvalues will be ignored.
        """
        return RestInternalServerError("not yet implemented")
    
    def deleteSong(self, request):
        """
        delete a song.  Requires songID be specified.
        """
        return RestInternalServerError("not yet implemented")