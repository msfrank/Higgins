# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from axiom import attributes
from axiom.store import Store
from axiom.item import Item
from epsilon.extime import Time
from higgins.signals import Signal
from higgins.logger import Loggable

class _DBLogger(Loggable):
    log_domain = 'db'
logger = _DBLogger()


class _SignalsDBStore(object):
    def committed(self):
        db.db_changed.signal(None)
        logger.log_debug2("committed %s" % str(self))
        Item.committed(self)

class File(_SignalsDBStore, Item):
    path = attributes.text()
    MIMEType = attributes.text()
    size = attributes.integer()

class Artist(_SignalsDBStore, Item):
    dateAdded = attributes.timestamp()
    name = attributes.text()
    website = attributes.text(allowNone=True)
    rating = attributes.integer(allowNone=True)

class Album(_SignalsDBStore, Item):
    dateAdded = attributes.timestamp()
    name = attributes.text()
    artist = attributes.reference()
    genre = attributes.reference()
    releaseDate = attributes.integer(allowNone=True)
    rating = attributes.integer(allowNone=True)

class Song(_SignalsDBStore, Item):
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
        
class Genre(_SignalsDBStore, Item):
    name = attributes.text()

class _PlaylistIterator(object):
    def __init__(self, ids, store):
        self._ids = ids
        self._store = store
        self._idx = 0
    def __iter__(self):
        return self
    def next(self):
        try:
            id = self._ids[self._idx]
        except:
            raise StopIteration()
        song = self._store.findUnique(Song, Song.storeID==self._ids[self._idx])
        self._idx += 1
        return song

class Playlist(_SignalsDBStore, Item):
    dateAdded = attributes.timestamp()
    name = attributes.text()
    data = attributes.text()
    rating = attributes.integer(allowNone=True)

    def length(self):
        if self.data == '':
            return 0
        return len(self.data.split(','))

    def listSongs(self):
        """
        Returns a list containing all of the Song objects in the playlist.
        Raises Exception on failure.
        """
        try:
            songlist = [ int(i) for i in self.data.split(',') ]
        except:
            songlist = []
        return _PlaylistIterator(songlist, self.store)

    def insertSong(self, song, position):
        """
        Inserts a song at the specified position.  If the position is negative,
        then the song is inserted from the end of the list.  If the position is
        greater than the length of the playlist, then the song is appended to
        the end of the list.  If the position is negative and abs(position) is
        greater than the length of the playlist, then the song is prepended to
        the beginning of the list.
        Raises Exception on failure.
        """
        if not isinstance(song, Song):
            raise Exception('failed to insert song: not a Song instance')
        try:
            if self.data == '':
                self.data = str(int(song.storeID))
            else:
                songlist = self.data.split(',')
                songlist.insert(position, str(song.id))
                self.data = ','.join(songlist)
        except Exception, e:
            raise Exception("failed to insert song '%s' into playlist '%s': %s" % (song, self.name, e))

    def appendSong(self, song):
        """Appends the song to the end of the list."""
        self.insertSong(song, -1)

    def prependSong(self, song):
        """Prepends the song to the beginning of the list."""
        self.insertSong(song, 0)

    def removeSong(self, position):
        """
        Removes the song at the specified position.  Raises IndexError if the
        position is out of range, otherwise raises Exception on all other errors.
        """
        try:
            songlist = self.data.split(',')
            del songlist[position]
            self.data = ','.join(songlist)
        except IndexError, e:
            raise e
        except Exception, e:
            raise Exception("failed to remove song #%i from playlist '%s'" % (position, self.name))

class DBStore(object):
    def __init__(self):
        self._isLoaded = False
        self._store = None
        self._dbPath = None
        self.db_changed = Signal()

    def open(self, path):
        if self._isLoaded:
            raise Exception('database has already been loaded')
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
        isNew = False
        def _setIsNew(newItem):
            isNew = True
        item = self._store.findOrCreate(itemType, _setIsNew, **kwds)
        return (item, isNew)

    def get(self, itemType, comparison):
        if not self._isLoaded:
            raise Exception('database is not loaded')
        if not issubclass(itemType, Item):
            raise Exception('%s is not a subclass of axiom.item.Item' % str(type(itemType)))
        return self._store.findUnique(itemType, comparison=comparison)

    def query(self, itemType, comparison=None, limit=None, offset=None, sort=None):
        if not self._isLoaded:
            raise Exception('database is not loaded')
        return self._store.query(itemType, comparison, limit, offset, sort)

    def count(self, itemType, comparison=None, offset=None):
        if not self._isLoaded:
            raise Exception('database is not loaded')
        return self._store.count(itemType, comparison=comparison, offset=offset)


db = DBStore()
