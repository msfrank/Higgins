# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.db import db, Artist, Album, Song
from higgins.core.dispatcher import Dispatcher
from higgins.http.http import Response
from higgins.data import templates
from higgins.core.logger import logger

class LibraryResource(Dispatcher):
    def __init__(self):
        Dispatcher.__init__(self)
        self.addRoute('/?$', self.render_index)
        self.addRoute('/music/?$', self.render_music)
        self.addRoute('/music/artists/?$', self.render_music_artists)
        self.addRoute('/music/artists/(\d+)/?$', self.render_music_artist)
        self.addRoute('/music/albums/?$', self.render_music_albums)
        self.addRoute('/music/albums/(\d+)/?$', self.render_music_album)
        self.addRoute('/music/songs/?$', self.render_music_songs)
        self.addRoute('/music/songs/(\d+)/?$', self.render_music_song)
        self.addRoute('/music/genres/?$', self.render_music_genres)
        self.addRoute('/music/genres/(\d+)/?$', self.render_music_genre)
        self.addRoute('/playlists/?$', self.render_playlists)
        self.addRoute('/playlists/(\d+)/?$', self.render_playlist)

    def render_index(self, request):
        return Response(200,
            stream=templates.render('templates/library-front.html',
                { 'topnav': [('Home', '/', False), ('Library', '/library', True),]}
                )
            )

    def render_music(self, request):
        latest_songs = db.query(Song, limit=5, sort=Song.dateAdded.descending)
        popular_songs = []
        return Response(200,
            stream=templates.render('templates/library-music.html', {
                    'topnav': [('Home', '/', False), ('Library', '/library', True),],
                    'latest_songs': latest_songs,
                    'popular_songs': popular_songs
                    }
                )
            )

    def render_music_artists(self, request):
        return Response(200,
            stream=templates.render('templates/music-byartist.html',
                { 'topnav':  [('Home', '/', False), ('Library', '/library', True),]}
                )
            )

    def render_music_artist(self, request, artistID):
        artist = db.get(Artist, Artist.storeID==int(artistID))
        album_list = db.query(Album, Album.artist==artist, sort=Album.releaseDate.ascending)
        return Response(200,
            stream=templates.render('templates/music-artist.html', { 
                    'topnav':  [('Home', '/', False), ('Library', '/library', True),],
                    'artist': artist,
                    'album_list': album_list
                    }
                )
            )

    def render_music_albums(self, request):
        return renderTemplate('templates/music-byalbum.html', {})

    def render_music_album(self, request, albumID):
        album = db.get(Album, Album.storeID==int(albumID))
        song_list = db.query(Song, Song.album==album, sort=Song.trackNumber.ascending)
        return Response(200,
            stream=templates.render('templates/music-album.html', { 
                    'topnav':  [('Home', '/', False), ('Library', '/library', True),],
                    'album': album,
                    'song_list': song_list
                    }
                )
            )

    def render_music_songs(request):
        return renderTemplate('templates/music-bysong.html', {})

    def render_music_song(request, song_id):
        return renderTemplate('templates/music-song.html', {})

    def render_music_genres(request):
        return renderTemplate('templates/music-bygenre.html', {})

    def render_music_genre(request, genre_id):
        return renderTemplate('templates/music-genre.html', {})

    def render_playlists(request):
        return renderTemplate('templates/playlist-byname.html', {})

    def render_playlist(request, playlist_id):
        return renderTemplate('templates/playlist-songs.html', {})
