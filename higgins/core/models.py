from django.db import models

class File(models.Model):
    class Admin:
        list_display = ('path', 'mimetype')
    path = models.CharField(maxlength=512)
    mimetype = models.CharField(maxlength=80)
    size = models.IntegerField()
    def __str__(self):
        return self.path

class Artist(models.Model):
    class Admin:
        list_display = ('name', 'website')
    date_added = models.DateTimeField(auto_now_add=True)
    name = models.CharField(maxlength=256)
    website = models.URLField(blank=True)
    rating = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.name

class Album(models.Model):
    class Admin:
        list_display = ('name', 'artist', 'genre')
    date_added = models.DateTimeField(auto_now_add=True)
    name = models.CharField(maxlength=256)
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
    name = models.CharField(maxlength=256)
    artist = models.ForeignKey('Artist')
    album = models.ForeignKey('Album')
    featuring = models.ManyToManyField('Artist', related_name='featured_on', blank=True)
    duration = models.IntegerField()
    track_number = models.IntegerField(blank=True, null=True)
    volume_number = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    rating = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.name
        
class Genre(models.Model):
    class Admin:
        pass
    name = models.CharField(maxlength=80)
    def __str__(self):
        return self.name

class Tag(models.Model):
    class Admin:
        pass
    name = models.CharField(maxlength=80)
    def __str__(self):
        return self.name

#class Playlist(models.Model):
#    class Admin:
#        pass
#    name = models.CharField(maxlength=80)
#    items = models.ManyToManyField('PlaylistItem')
#    tags = models.ManyToManyField('Tag', blank=True)
#    rating = models.IntegerField(blank=True, null=True)
#
#class PlaylistItem(models.Model):
#    class Admin:
#        pass
#    song = models.ForeignKey('Song')
#    prev_item = models.ForeignKey('PlaylistItem', blank=True)
#    next_item = models.ForeignKey('PlaylistItem', blank=True)
