# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from axiom import attributes
from axiom.store import Store
from axiom.item import Item
from higgins.signals import Signal
from higgins.logger import Loggable

class DBLogger(Loggable):
    log_domain = 'db'
logger = DBLogger()

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
    dateAdded = attributes.timestamp()
    name = attributes.text()
    artist = attributes.reference()
    genre = attributes.reference()
    releaseDate = attributes.integer(allowNone=True)
    rating = attributes.integer(allowNone=True)

class Song(Item):
    dateAdded = attributes.timestamp()
    name = attributes.text()
    artist = attributes.reference()
    album = attributes.reference()
    duration = attributes.integer()
    trackNumber = attributes.integer(allowNone=True)
    volumeNumber = attributes.integer(allowNone=True)
    rating = attributes.integer(allowNone=True)
    file = attributes.reference()

    def printDuration(self):
        duration = self.duration / 1000
        if duration < 60:
            return '0:%02i' % duration
        if duration < 3600:
            return '%i:%02i' % (duration / 60, duration % 60)
        hrs = duration / 3600
        sec = duration - (3600 * hrs)
        min = sec / 60
        return '%i:%02i:%02i' % (hrs, min, sec)
        
class Genre(Item):
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

class DBStore(object):
    def __init__(self):
        self._isLoaded = False
        self._store = None
        self._dbPath = None
        self.db_changed = Signal()

    def open(self, path):
        if self._isLoaded:
            raise Exception('database has already been loaded')
        class SignallingStore(Store):
            def __init__(self, dbdir, dbstore):
                Store.__init__(self, dbdir)
                self._dbstore = dbstore
            def _postCommitHook(self):
                try:
                    Store._postCommitHook(self)
                    self._dbstore.db_changed.signal(None)
                except Exception, e:
                    logger.log_debug("_postCommitHook: %s" % str(e))
        #self._store = SignallingStore(path, self)
        self._store = Store(path)
        self._dbPath = path
        self._isLoaded = True

    def close(self):
        if not self._isLoaded:
            raise Exception('database is not loaded')
        self._store.close()
        #self._store._dbstore = None
        self._store = None
        self._dbPath = None
        self._isLoaded = False

    def create(self, itemType, **kwds):
        if not self._isLoaded:
            raise Exception('database is not loaded')
        if not issubclass(itemType, Item):
            raise Exception('%s is not a subclass of axiom.item.Item' % str(type(itemType)))
        kwds['store'] = self._store
        return itemType(**kwds)

    def getOrCreate(self, itemType, **kwds):
        if not self._isLoaded:
            raise Exception('database is not loaded')
        if not issubclass(itemType, Item):
            raise Exception('%s is not a subclass of axiom.item.Item' % str(type(itemType)))
        return self._store.findOrCreate(itemType, **kwds)

    def query(self, itemType, comparison=None, limit=None, offset=None, sort=None):
        if not self._isLoaded:
            raise Exception('database is not loaded')
        return self._store.query(itemType, comparison, limit, offset, sort)


db = DBStore()
