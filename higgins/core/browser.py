# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404
from django.utils import simplejson
from higgins.core.models import Artist, Album, Song, Genre, Tag, Playlist
from higgins.core.logger import logger

def front(request):
    return render_to_response('templates/library-front.t', {})

def music_front(request):
    latest_list = Song.objects.all().order_by('-date_added')[:10]
    return render_to_response('templates/library-music.t',
        { 'latest_list': latest_list }
        )

class ArtistEditorForm(forms.ModelForm):
    class Meta:
        model = Artist

def music_byartist(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    album_list = artist.album_set.all().order_by('release_date')
    if request.method == 'POST':
        editor = ArtistEditorForm(request.POST, instance=artist)
        if editor.is_valid():
            editor.save()
    else:
        editor = ArtistEditorForm(instance=artist)
    return render_to_response('templates/music-artist.t',
        { 'artist': artist, 'album_list': album_list, 'editor': editor }
        )

class AlbumEditorForm(forms.ModelForm):
    class Meta:
        model = Album

def music_byalbum(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    song_list = album.song_set.all().order_by('track_number')
    playlists = Playlist.objects.all()
    if request.method == 'POST':
        if request.POST['is-playlist'] == 'false':
            editor = AlbumEditorForm(request.POST, instance=album)
            if editor.is_valid():
                editor.save()
        else:
            playlist = Playlist.objects.get(id=request.POST['selection'])
            for id,value in request.POST.items():
                if value == 'selected':
                    song = Song.objects.get(id=int(id))
                    logger.log_debug("adding '%s' to playlist '%s'" % (song, playlist))
                    playlist.append_song(song)
            editor = AlbumEditorForm(instance=album)
    else:
        editor = AlbumEditorForm(instance=album)
    return render_to_response('templates/music-album.t',
        { 'album': album, 'song_list': song_list, 'editor': editor, 'playlists': playlists }
        )

class SongEditorForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ('name','artist','album','track_number','volume_number','rating')

def music_bysong(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    if request.method == 'POST':
        editor = SongEditorForm(request.POST, instance=song)
        if editor.is_valid():
            editor.save()
    else:
        editor = SongEditorForm(instance=song)
    return render_to_response('templates/music-song.t', { 'song': song, 'editor': editor })

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

def list_playlists(request):
    if request.method == 'GET':
        pl_list = Playlist.objects.all().order_by('name')
        return render_to_response('templates/playlist-byname.t', {'pl_list': pl_list})
    logger.log_debug("list_playlists: POST=%s" % request.POST)
    json=''
    if request.POST['action'] == 'list':
        playlists = []
        for pl in Playlist.objects.all().order_by('name'):
            playlists.append({'id': pl.id, 'title': pl.name, 'len': len(pl)})
        json = simplejson.dumps({'status': 200, 'playlists': playlists})
    elif request.POST['action'] == 'create':
        playlist = Playlist(name=request.POST['title'])
        playlist.save()
        json = simplejson.dumps({'status': 200, 'title': playlist.name, 'id': playlist.id, 'len': len(playlist)})
    elif request.POST['action'] == 'rename':
        playlist = Playlist.objects.get(id=request.POST['id'])
        playlist.name = request.POST['title']
        playlist.save()
        json = simplejson.dumps({'status': 200, 'id': request.POST['id']})
    elif request.POST['action'] == 'delete':
        playlist = Playlist.objects.get(id=request.POST['id'])
        playlist.delete()
        json = simplejson.dumps({'status': 200})
    return HttpResponse(json, mimetype="application/json")

def playlist_show(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    if request.method == 'GET':
        song_list = playlist.list_songs()
        return render_to_response('templates/playlist-songs.t',
            { 'playlist': playlist, 'song_list': song_list }
            )
    logger.log_debug("playlist_show: POST=%s" % request.POST)
    json=''
    if request.POST['action'] == 'add':
        for id in request.POST.getlist('ids'):
            song = Song.objects.get(id=int(id))
            playlist.append_song(song)
            logger.log_debug("playlist_show: added song %s" % song.name)
        playlist.save()
        json = simplejson.dumps({'status': 200})
    return HttpResponse(json, mimetype="application/json")
