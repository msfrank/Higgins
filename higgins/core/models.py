# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from django.db import models

# we must increment this every time a change is made which alters
# the database schema
DB_VERSION = 1

class File(models.Model):
    class Admin:
        list_display = ('path', 'mimetype')
    path = models.CharField(max_length=512)
    mimetype = models.CharField(max_length=80)
    size = models.IntegerField()
    def __str__(self):
        return self.path

class Artist(models.Model):
    class Admin:
        list_display = ('name', 'website')
    date_added = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)
    website = models.URLField(blank=True)
    rating = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.name

class Album(models.Model):
    class Admin:
        list_display = ('name', 'artist', 'genre')
    date_added = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)
    artist = models.ForeignKey('Artist')
    genre = models.ForeignKey('Genre', blank=True)
    release_date = models.IntegerField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.name

class Song(models.Model):
    class Admin:
        list_display = ('name', 'file')
    file = models.ForeignKey('File')
    date_added = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)
    artist = models.ForeignKey('Artist')
    album = models.ForeignKey('Album')
    featuring = models.ManyToManyField('Artist', related_name='featured_on', blank=True)
    duration = models.IntegerField()
    track_number = models.IntegerField(blank=True, null=True)
    volume_number = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    rating = models.IntegerField(blank=True, null=True)

    def print_duration(self):
        duration = self.duration / 1000
        if duration < 60:
            return '0:%02i' % duration
        if duration < 3600:
            return '%i:%02i' % (duration / 60, duration % 60)
        hrs = duration / 3600
        sec = duration - (3600 * hrs)
        min = sec / 60
        return '%i:%02i:%02i' % (hrs, min, sec)

    def __str__(self):
        return self.name
        
class Genre(models.Model):
    class Admin:
        pass
    name = models.CharField(max_length=80)
    def __str__(self):
        return self.name

class Tag(models.Model):
    class Admin:
        pass
    name = models.CharField(max_length=80)
    def __str__(self):
        return self.name

class Playlist(models.Model):
    class Admin:
        pass
    name = models.CharField(max_length=80)
    data = models.TextField(blank=True, editable=False)
    songs = models.ManyToManyField(Song, blank=True, editable=False)
    tags = models.ManyToManyField(Tag, blank=True)
    rating = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.name

    def __len__(self):
        return len(self.data.split(':'))

    def list_songs(self):
        """
        Returns a list containing all of the Song objects in the playlist.
        Raises Exception on failure.
        """
        try:
            songlist = [ int(i) for i in self.data.split(':') ]
        except:
            songlist = []
        return [ Song.objects.get(pk=id) for id in songlist]

    def insert_song(self, song, position):
        """
        Inserts a song at the specified position.  If the position is negative,
        then the song is inserted from the end of the list.  If the position is
        greater than the length of the playlist, then the song is appended to
        the end of the list.  If the position is negative and abs(position) is
        greater than the length of the playlist, then the song is prepended to
        the beginning of the list.
        Raises Exception on failure.
        """
        try:
            songlist = self.data.split(':')
            songlist.insert(position, str(song.id))
            self.data = ':'.join(songlist)
            logger.log_debug("new order for playlist '%s' is %s" % (self.name, self.data))
            self.save()
        except:
            raise Exception("failed to insert song '%s' into playlist '%s'" % (song, self.name))

    def append_song(self, song):
        """Appends the song to the end of the list."""
        self.insert_song(song, -1)

    def prepend_song(self, song):
        """Prepends the song to the beginning of the list."""
        self.insert_song(song, 0)

    def remove_song(self, position):
        """
        Removes the song at the specified position.  Raises IndexError if the
        position is out of range, otherwise raises Exception on all other errors.
        """
        try:
            songlist = self.data.split(':')
            del songlist[position]
            self.data = ':'.join(songlist)
            logger.log_debug("new order for playlist '%s' is %s" % (self.name, self.data))
            self.save()
        except IndexError, e:
            raise e
        except Exception, e:
            raise Exception("failed to remove song #%i from playlist '%s'" % (position, self.name))
