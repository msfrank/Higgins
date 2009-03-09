# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from higgins.core.models import Artist, Album, Song, Genre, Tag

def index(request):
    latest_list = Song.objects.all().order_by('-date_added')[:10]
    return render_to_response('templates/browser-index.t',
        { 'latest_list': latest_list }
        )

def byartist(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    album_list = artist.album_set.all().order_by('release_date')
    return render_to_response('templates/browser-artist.t',
        { 'artist': artist, 'album_list': album_list }
        )

def bysong(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    return render_to_response('templates/browser-song.t', { 'song': song })

def byalbum(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    song_list = album.song_set.all().order_by('track_number')
    return render_to_response('templates/browser-album.t',
        { 'album': album, 'song_list': song_list }
        )

def bygenre(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)
    album_list = genre.album_set.all().order_by('name')
    return render_to_response('templates/browser-genre.t',
        { 'genre': genre, 'album_list': album_list }
        )

def artists(request):
    artist_list = Artist.objects.all().order_by('name')
    return render_to_response('templates/browser-byartist.t',
        { 'artist_list': artist_list }
        )

def genres(request):
    genre_list = Genre.objects.all().order_by('name')
    return render_to_response('templates/browser-bygenre.t',
        { 'genre_list': genre_list }
        )

def tags(request):
    tag_list = Tag.objects.all().order_by('name')
    return render_to_response('templates/browser-bytag.t',
        { 'tag_list': tag_list }
        )
