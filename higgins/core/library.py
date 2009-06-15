# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.http.page_resource import PageResource
from higgins.http.http import Response
from higgins.core.logger import logger

class LibraryResource(PageResource):
    def __init__(self):
        root = self.setRootPage(self.render_index)
        music = root.addPage('music', self.render_music)
        music.addPage('artists', self.render_music_artists).addPage('(\d+)', self.render_music_artist)
        music.addPage('albums', self.render_music_albums).addPage('(\d+)', self.render_music_album)
        music.addPage('songs', self.render_music_songs).addPage('(\d+)', self.render_music_song)
        music.addPage('genres', self.render_music_genres).addPage('(\d+)', self.render_music_genre)
        playlists = root.addPage('playlists', self.render_playlists)
        playlists.addPage('(\d+)', self.render_playlist)))

    def render_index(self, request):
        return render_to_response('templates/library-front.t', {})

    def render_music(self, request):
        return render_to_response('templates/library-music.t',{})

    def render_music_artists(request):
        return render_to_response('templates/music-byartist.t', {})

    def render_music_artist(request, artist_id):
        return render_to_response('templates/music-artist.t', {})

    def render_music_album(request, album_id):
        return render_to_response('templates/music-album.t', {})

    def render_music_song(request, song_id):
        return render_to_response('templates/music-song.t', {})

    def render_music_genres(request):
        return render_to_response('templates/music-bygenre.t', {})

    def render_music_genre(request, genre_id):
        return render_to_response('templates/music-genre.t', {})

    def render_playlists(request):
        return render_to_response('templates/playlist-byname.t', {})

    def render_playlist(request, playlist_id):
        return render_to_response('templates/playlist-songs.t', {})
