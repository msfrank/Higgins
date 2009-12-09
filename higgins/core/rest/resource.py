# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.core.dispatcher import Dispatcher
from higgins.core.logger import logger

from higgins.core.rest.song import *
from higgins.core.rest.album import *
from higgins.core.rest.artist import *
from higgins.core.rest.playlist import *

class RestResource(Dispatcher):
    def __init__(self):
        Dispatcher.__init__(self)

        # API methods operating on songs
        self.addRoute('listSongs$', listSongs, allowedMethods=('POST'))
        self.addRoute('getSong$', getSong, allowedMethods=('POST'))
        self.addRoute('addSong$', addSong, allowedMethods=('POST'), acceptFile=acceptSongItem)
        self.addRoute('updateSong$', updateSong, allowedMethods=('POST'))
        self.addRoute('deleteSong$', deleteSong, allowedMethods=('POST'))

        # API methods operating on albums
        self.addRoute('listAlbums$', listAlbums, allowedMethods=('POST'))
        self.addRoute('getAlbum$', getAlbum, allowedMethods=('POST'))
        self.addRoute('updateAlbum$', updateAlbum, allowedMethods=('POST'))
        self.addRoute('deleteAlbum$', deleteAlbum, allowedMethods=('POST'))

        # API methods operating on artists
        self.addRoute('listArtists$', listArtists, allowedMethods=('POST'))
        self.addRoute('getArtist$', getArtist, allowedMethods=('POST'))
        self.addRoute('updateArtist$', updateArtist, allowedMethods=('POST'))
        self.addRoute('deleteArtist$', deleteArtist, allowedMethods=('POST'))

        # API methods operating on playlists
        self.addRoute('listPlaylists$', listPlaylists, allowedMethods=('POST'))
        self.addRoute('getPlaylist$', getPlaylist, allowedMethods=('POST'))
        self.addRoute('addPlaylist$', addPlaylist, allowedMethods=('POST'))
        self.addRoute('updatePlaylist$', updatePlaylist, allowedMethods=('POST'))
        self.addRoute('deletePlaylist$', deletePlaylist, allowedMethods=('POST'))
        self.addRoute('addPlaylistItems$', addPlaylistItems, allowedMethods=('POST'))
        self.addRoute('reorderPlaylistItems$', reorderPlaylistItems, allowedMethods=('POST'))
        self.addRoute('deletePlaylistItems$', deletePlaylistItems, allowedMethods=('POST'))
