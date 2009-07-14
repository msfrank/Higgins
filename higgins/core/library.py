# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.db import db, Song
from higgins.http.url_dispatcher import UrlDispatcher
from higgins.http.http import Response
from higgins.data import templates
from higgins.core.logger import logger

class LibraryResource(UrlDispatcher):
    def __init__(self):
        self.addRoute('/?$', self.render_index)
        self.addRoute('/music/?$', self.render_music)
        self.addRoute('/music/artists/?$', self.render_music_artists)
        self.addRoute('/music/artists/(\d+)$', self.render_music_artist)
        self.addRoute('/music/albums/?$', self.render_music_albums)
        self.addRoute('/music/albums/(\d+)$', self.render_music_album)
        self.addRoute('/music/songs/?$', self.render_music_songs)
        self.addRoute('/music/songs/(\d+)$', self.render_music_song)
        self.addRoute('/music/genres/?$', self.render_music_genres)
        self.addRoute('/music/genres/(\d+)$', self.render_music_genre)
        self.addRoute('/playlists/?$', self.render_playlists)
        self.addRoute('/playlists/(\d+)$', self.render_playlist)

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

    def render_music_artists(request):
        return Response(200,
            stream=templates.render('templates/music-byartist.html',
                { 'topnav':  [('Home', '/', False), ('Library', '/library', True),]}
                )
            )

    def render_music_artist(request, artist_id):
        return renderTemplate('templates/music-artist.html', {})

    def render_music_albums(request):
        return renderTemplate('templates/music-byalbum.html', {})

    def render_music_album(request, album_id):
        return renderTemplate('templates/music-album.html', {})

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
