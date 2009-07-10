# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import simplejson
from higgins.db import db, Artist, Album, Song, Genre
from higgins.http.url_dispatcher import UrlDispatcher
from higgins.http.http_headers import MimeType
from higgins.http.http import Response
from higgins.core.logger import logger

class APIResource(UrlDispatcher):
    def __init__(self):
        self.addRoute('songs/?$', self.manage_songs, allowedMethods=('GET','POST'))
        self.addRoute('songs/(\d+)/?$',
                      self.manage_song_item,
                      allowedMethods=('GET','POST','PUT','DELETE'),
                      acceptFile=self.accept_song_item)
        #self.addRoute('/videos/', self.manage_videos)
        #self.addRoute('/videos/(\d+)$', self.manage_video_item)
        #self.addRoute('/photos/', self.manage_photos)
        #self.addRoute('/photos/(\d+)$', self.manage_photo_item)
        #self.addRoute('/playlists/$', self.manage_playlists)
        #self.addRoute('/playlists/(\d+)$', self.manage_playlist_item)

    def accept_song_item(self, request):
        return None

    def manage_songs(self, request):
        logger.log_debug('manage_songs: method=%s, args=%s, post=%s' %
                        (request.method, request.args, request.post)
                        )
        if request.method == 'GET':
            offset = request.args.get('offset', None)
            if offset != None: offset = int(offset[0])
            limit = request.args.get('limit', None)
            if limit != None: offset = int(limit[0])
            items = []
            for song in db.query(Song, offset=offset, limit=limit):
                items.append({'name': song.name,
                             'id': song.storeID,
                             'artist': song.artist.storeID,
                             'album': song.album.storeID
                             })
            if offset == None: offset = 0
            response = {'nitems': len(items), 'offset': offset, 'items': items}
            response = simplejson.dumps(response)
            return Response(200, {'content-type':MimeType.fromString('application/json')}, response)
        elif request.method == 'POST':
        #    try:
                # title is required
                title = request.post.get('title', None)
                if title == None:
                    return HttpResponse(400, stream="Missing required form item 'title")
                # create or get the artist object
                value = request.post.get('artist', '')
                artist = db.getOrCreate(Artist, name=value)
                # create or get the genre object
                value = request.post.get('genre', '')
                genre = db.getOrCreate(Genre, name=value)
                # create or get the album object
                value = request.post.get('album', '')
                album = db.getOrCreate(Album, name=value, artist=artist, genre=genre)
                # create the song object
                song = db.create(Song, name=title, album=album, artist=artist)
                if 'track' in request.post:
                    song.trackNumber = int(request.post['track'])
                if 'length' in request.post:
                    song.duration = int(request.post['length'])
                logger.log_debug("successfully added new song '%s'" % title)
                return Response(200, stream="success!")
        #    except Exception, e:
        #        logger.log_debug("failed to add song: %s" % e)
        #        return Response(500, stream="Internal Server Error")
        return Response(500)

    def manage_song_item(self, request, item):
        logger.log_debug('manage_songs: method=%s, args=%s, post=%s' %
                        (request.method, request.args, request.post)
                        )
        return Response(200)

    def manage_playlists(request):
        return Response(200)

    def manage_playlist_item(request, playlist_id):
        return Response(200)
