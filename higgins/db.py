# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from axiom.item import Item
from axiom import attributes
from higgins.signals import Signal


# we must increment this every time a change is made which alters
# the database schema
DB_VERSION = 1


class File(Item):
    path = attributes.path()
    mimetype = attributes.text()
    size = attributes.integer()

class Artist(Item):
    date_added = attributes.timestamp()
    name = attributes.text()
    website = attributes.text(allowNone=True)
    rating = attributes.integer(allowNone=True)

class Album(Item):
    date_added = attributes.timestamp()
    name = attributes.text()
    artist = attributes.reference()
    genre = attributes.reference()
    release_date = attributes.integer(allowNone=True)
    rating = attributes.integer(allowNone=True)

class Song(Item):
    date_added = attributes.timestamp()
    name = attributes.text()
    artist = attributes.reference()
    album = attributes.reference()
    duration = attributes.integer()
    track_number = attributes.integer(allowNone=True)
    volume_number = attributes.integer(allowNone=True)
    rating = attributes.integer(allowNone=True)
    file = attributes.reference()

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
        
class Genre(models.Model):
    name = attributes.text()

#class Playlist(models.Model):
#    date_added = attributes.timestamp()
#    name = attributes.text()
#    data = attributes.text()
#    rating = attributes.integer(allowNone=True)
#
#    def length(self):
#        if self.data == '':
#            return 0
#        return len(self.data.split(','))
#
#    def list_songs(self):
#        """
#        Returns a list containing all of the Song objects in the playlist.
#        Raises Exception on failure.
#        """
#        try:
#            songlist = [ int(i) for i in self.data.split(',') ]
#        except:
#            songlist = []
#        return [ Song.objects.get(pk=id) for id in songlist]
#
#    def insert_song(self, song, position):
#        """
#        Inserts a song at the specified position.  If the position is negative,
#        then the song is inserted from the end of the list.  If the position is
#        greater than the length of the playlist, then the song is appended to
#        the end of the list.  If the position is negative and abs(position) is
#        greater than the length of the playlist, then the song is prepended to
#        the beginning of the list.
#        Raises Exception on failure.
#        """
#        try:
#            if self.data == '':
#                self.data = '%i' % song.id
#            else:
#                songlist = self.data.split(':')
#                songlist.insert(position, str(song.id))
#                self.data = ':'.join(songlist)
#            self.save()
#        except Exception, e:
#            raise Exception("failed to insert song '%s' into playlist '%s': %s" % (song, self.name, e))
#
#    def append_song(self, song):
#        """Appends the song to the end of the list."""
#        self.insert_song(song, -1)
#
#    def prepend_song(self, song):
#        """Prepends the song to the beginning of the list."""
#        self.insert_song(song, 0)
#
#    def remove_song(self, position):
#        """
#        Removes the song at the specified position.  Raises IndexError if the
#        position is out of range, otherwise raises Exception on all other errors.
#        """
#        try:
#            songlist = self.data.split(',')
#            del songlist[position]
#            self.data = ','.join(songlist)
#            self.save()
#        except IndexError, e:
#            raise e
#        except Exception, e:
#            raise Exception("failed to remove song #%i from playlist '%s'" % (position, self.name))

#
#
db_changed = Signal()

#
#
#_itemCommitted = Deferred()
#_commitFlag = False
#def _onItemCommitted(result):
#    _commitFlag = True
#_itemCommitted.addCallback(_onItemCommitted)
