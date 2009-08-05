# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os
import simplejson
from epsilon.extime import Time
from higgins.db import db, Artist, Album, Song, Genre, File
from higgins.http.url_dispatcher import UrlDispatcher
from higgins.http.http_headers import MimeType
from higgins.http.http import Response
from higgins.core.logger import logger

NO_ERROR = 0
ERROR_INTERNAL_SERVER_ERROR = 1
ERROR_INVALID_INPUT = 2

_APIErrors = [
    "No Error",
    "Internal Server Error"
    "Validation Error"
    ]

class RestResponse(Response):
    def __init__(self, data, type='json'):
        headers = {}
        if type == 'json':
            data['status'] = 0
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

class APIResource(UrlDispatcher):
    def __init__(self):
        UrlDispatcher.__init__(self)
        self.addRoute('songs/?$', self.manageSongs, allowedMethods=('GET','POST'))
        self.addRoute('songs/(\d+)/?$',
                      self.manageSongItem,
                      allowedMethods=('GET','POST'),
                      acceptFile=self.acceptSongItem
                      )
        #self.addRoute('/videos/', self.manageVideos)
        #self.addRoute('/videos/(\d+)$', self.manageVideoItem)
        #self.addRoute('/photos/', self.managePhotos)
        #self.addRoute('/photos/(\d+)$', self.managePhotoItem)
        #self.addRoute('/playlists/$', self.managePlaylists)
        #self.addRoute('/playlists/(\d+)$', self.managePlaylistItem)

    def acceptSongItem(self, request, mimetype, subheaders):
        return None

    def manageSongs(self, request):
        if request.method == 'GET':
            offset = request.args.get('offset', None)
            if offset != None: offset = int(offset[0])
            limit = request.args.get('limit', None)
            if limit != None: offset = int(limit[0])
            items = []
            for song in db.query(Song, offset=offset, limit=limit):
                items.append({'name': song.name,
                             'songID': song.storeID,
                             'artistID': song.artist.storeID,
                             'albumID': song.album.storeID
                             })
            if offset == None: offset = 0
            response = {'nitems': len(items), 'offset': offset, 'items': items}
            return RestResponse(response)
        elif request.method == 'POST':
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
                if not 'MIMEType' in request.post:
                    return RestErrorResponse(ERROR_INVALID_INPUT, "Missing required form item 'mimetype'")
                size = int(os.stat(path).st_size)
                # create the file object
                file = db.create(File, path=path, size=size, MIMEType=request.post.get('MIMEType'))
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
        return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)

    def manageSongItem(self, request, item):
        return RestErrorResponse(ERROR_INTERNAL_SERVER_ERROR)
