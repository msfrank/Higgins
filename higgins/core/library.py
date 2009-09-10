# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.db import db, Artist, Album, Song, Playlist
from higgins.core.dispatcher import Dispatcher
from higgins.core.logger import logger
from higgins.http.http import Response

class LibraryResource(Dispatcher):
    def __init__(self):
        Dispatcher.__init__(self)
        self.addRoute('/?$', self.render_index)
        self.addRoute('/music/?$', self.render_music_artists)
        self.addRoute('/music/artist/(\d+)/?$', self.render_music_artist)
        self.addRoute('/music/album/(\d+)/?$', self.render_music_album)
        self.addRoute('/music/song/(\d+)/?$', self.render_music_song)
        self.addRoute('/playlists/?$', self.render_playlists)
        self.addRoute('/playlists/(\d+)/?$', self.render_playlist)

    def render_index(self, request):
        latest_songs = db.query(Song, limit=10, sort=Song.dateAdded.descending)
        popular_songs = []
        return Response(200,
            stream=self.renderTemplate(
                'templates/library-front.html', {
                    'latest_songs': latest_songs,
                    'popular_songs': popular_songs
                    }
                )
            )

    def render_music_artists(self, request):
        artist_list = db.query(Artist)
        return Response(200,
            stream=self.renderTemplate(
                'templates/music-byartist.html', {
                    'artists': artist_list
                    }
                )
            )

    def render_music_artist(self, request, artistID):
        artist = db.get(Artist, Artist.storeID==int(artistID))
        album_list = db.query(Album, Album.artist==artist, sort=Album.releaseDate.ascending)
        return Response(200,
            stream=self.renderTemplate(
                'templates/music-artist.html', { 
                    'artist': artist,
                    'album_list': album_list
                    }
                )
            )

    def render_music_album(self, request, albumID):
        album = db.get(Album, Album.storeID==int(albumID))
        song_list = db.query(Song, Song.album==album, sort=Song.trackNumber.ascending)
        return Response(200,
            stream=self.renderTemplate(
                'templates/music-album.html', { 
                    'album': album,
                    'song_list': song_list
                    }
                )
            )

    def render_music_song(self, request, songID):
        song = db.get(Song, Song.storeID==int(songID))
        return Response(200,
            stream=self.renderTemplate(
                'templates/music-song.html', {'song': song}
                )
            )

    def render_playlists(self, request):
        pl_list = db.query(Playlist)
        return Response(200,
            stream=self.renderTemplate(
                'templates/playlist-front.html', {'pl_list': pl_list}
                )
            )

    def render_playlist(self, request, playlistID):
        playlist = db.get(Playlist, Playlist.storeID==int(playlistID))
        return Response(200,
            stream=self.renderTemplate(
                'templates/playlist-songs.html', {'playlist': playlist}
                )
            )
