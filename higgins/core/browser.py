# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.forms import ModelForm
from higgins.core.models import Artist, Album, Song, Genre, Tag

def front(request):
    return render_to_response('templates/library-front.t', {})

def music_front(request):
    latest_list = Song.objects.all().order_by('-date_added')[:10]
    return render_to_response('templates/library-music.t',
        { 'latest_list': latest_list }
        )

def music_byartist(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    album_list = artist.album_set.all().order_by('release_date')
    return render_to_response('templates/music-artist.t',
        { 'artist': artist, 'album_list': album_list }
        )

def music_bysong(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    return render_to_response('templates/music-song.t', { 'song': song })

class AlbumEditorForm(ModelForm):
    class Meta:
        model = Album

def music_byalbum(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    song_list = album.song_set.all().order_by('track_number')
    if request.method == 'POST':
        editor = AlbumEditorForm(request.POST, instance=album)
        if editor.is_valid():
            editor.save()
    else:
        editor = AlbumEditorForm(instance=album)
    return render_to_response('templates/music-album.t',
        { 'album': album, 'song_list': song_list, 'editor': editor }
        )

def music_bygenre(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)
    album_list = genre.album_set.all().order_by('name')
    return render_to_response('templates/music-genre.t',
        { 'genre': genre, 'album_list': album_list }
        )

def music_artists(request):
    artist_list = Artist.objects.all().order_by('name')
    return render_to_response('templates/music-byartist.t',
        { 'artist_list': artist_list }
        )

def music_genres(request):
    genre_list = Genre.objects.all().order_by('name')
    return render_to_response('templates/music-bygenre.t',
        { 'genre_list': genre_list }
        )

def music_tags(request):
    tag_list = Tag.objects.all().order_by('name')
    return render_to_response('templates/music-bytag.t',
        { 'tag_list': tag_list }
        )
