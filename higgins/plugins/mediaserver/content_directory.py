# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from xml.etree.ElementTree import Element, SubElement
from higgins.db import db, Artist, Album, Song, File, Playlist
from higgins.settings import Configurator, IntegerSetting
from higgins.core.service import CoreHttpConfig
from higgins.upnp.device_service import UPNPDeviceService
from higgins.upnp.statevar import StringStateVar, UI4StateVar
from higgins.upnp.action import Action, InArgument, OutArgument
from higgins.upnp.error import UPNPError
from higgins.upnp.prettyprint import xmlprint
from higgins.plugins.mediaserver.logger import logger

class CDSPrivate(Configurator):
    SYSTEM_UPDATE_ID = IntegerSetting("System Update ID", 0,
        "Each time an the media library changes, the revision number is incremented by one"
        )

class ContentDirectory(UPNPDeviceService):
    serviceType = "urn:schemas-upnp-org:service:ContentDirectory:1"
    serviceID = "urn:upnp-org:serviceId:urn:schemas-upnp-org:service:ContentDirectory"

    #######################################################
    # State Variable declarations                         #
    #######################################################

    A_ARG_TYPE_BrowseFlag = StringStateVar(allowedValueList=("BrowseMetadata", "BrowseDirectChildren"))
    A_ARG_TYPE_SearchCriteria = StringStateVar()
    SystemUpdateID = UI4StateVar(sendEvents=True, defaultValue=CDSPrivate.SYSTEM_UPDATE_ID)
    #ContainerUpdateIDs = StringStateVar(sendEvents=True, defaultValue="0,1")
    A_ARG_TYPE_Count = UI4StateVar()
    A_ARG_TYPE_SortCriteria = StringStateVar()
    SortCapabilities = StringStateVar()
    A_ARG_TYPE_Index = UI4StateVar()
    A_ARG_TYPE_ObjectID = StringStateVar()
    A_ARG_TYPE_UpdateID = UI4StateVar()
    A_ARG_TYPE_Result = StringStateVar()
    SearchCapabilities = StringStateVar()
    A_ARG_TYPE_Filter = StringStateVar()

    def __init__(self):
        # start listening for the db_changed signal
        signal = db.db_changed.connect()
        signal.addCallback(self._caughtUpdate)

    def _caughtUpdate(self, unused):
        # increment the SystemUpdateID statevar
        self.SystemUpdateID.value = self.SystemUpdateID.value + 1
        CDSPrivate.SYSTEM_UPDATE_ID = self.SystemUpdateID.value
        # re-arm the db_changed signal
        signal = db.db_changed.connect()
        signal.addCallback(self._caughtUpdate)

    #######################################################
    # Action definitions                                  #
    #######################################################

    def _BrowseMetadata(self, request, objectID, filter, startingIndex, requestedCount, sortCriteria):
        # generate the DIDL envelope
        didl = Element("DIDL-Lite")
        didl.attrib["xmlns"] = "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"
        didl.attrib["xmlns:upnp"] = "urn:schemas-upnp-org:metadata-1-0/upnp/"
        didl.attrib["xmlns:dc"] = "http://purl.org/dc/elements/1.1/"
        if objectID == '0':
            container = SubElement(didl, 'container')
            container.attrib['id'] = objectID
            container.attrib['parentID'] = '-1'
            container.attrib['restricted'] = '1'
            container.attrib['childCount'] = '2'
            SubElement(container, 'dc:title').text = 'Media on Higgins'
            SubElement(container, 'upnp:class').text = 'object.container.storageFolder'
            return (1, 1, didl)
        if objectID == 'artists':
            container = SubElement(didl, 'container')
            container.attrib['id'] = objectID
            container.attrib['parentID'] = '0'
            container.attrib['restricted'] = '1'
            container.attrib['childCount'] = str(db.query(Artist).count())
            SubElement(container, 'dc:title').text = 'Music'
            SubElement(container, 'upnp:class').text = 'object.container.storageFolder'
            return (1, 1, didl)
        if objectID == 'playlists':
            container = SubElement(didl, 'container')
            container.attrib['id'] = objectID
            container.attrib['parentID'] = '0'
            container.attrib['restricted'] = '1'
            container.attrib['childCount'] = str(db.query(Playlist).count())
            SubElement(container, 'dc:title').text = 'Playlists'
            SubElement(container, 'upnp:class').text = 'object.container.storageFolder'
            return (1, 1, didl)
        key,value = objectID.split('=', 1)
        if key == 'artist':
            artist = db.get(Artist, Artist.storeID==int(value))
            container = SubElement(didl, 'container')
            container.attrib['id'] = objectID
            container.attrib['parentID'] = 'artists'
            container.attrib['restricted'] = '1'
            container.attrib['childCount'] = str(db.query(Album, Album.artist==artist).count())
            SubElement(container, 'dc:title').text = str(artist.name)
            SubElement(container, 'upnp:class').text = 'object.container.person.musicArtist'
            return (1, 1, didl)
        if key == 'album':
            album = db.get(Album, Album.storeID==int(value))
            container = SubElement(didl, 'container')
            container.attrib['id'] = objectID
            container.attrib['parentID'] = 'artist=%i' % int(album.artist.storeID)
            container.attrib['restricted'] = '1'
            container.attrib['childCount'] = str(db.query(Song, Song.album==album).count())
            SubElement(container, 'dc:title').text = str(album.name)
            SubElement(container, 'upnp:class').text = 'object.container.album.musicAlbum'
            return (1, 1, didl)
        if key == 'playlist':
            playlist = db.get(Playlist, Playlist.storeID==int(value))
            container = SubElement(didl, 'container')
            container.attrib['id'] = objectID
            container.attrib['parentID'] = 'playlists'
            container.attrib['restricted'] = '1'
            container.attrib['childCount'] = str(playlist.length)
            SubElement(container, 'dc:title').text = str(playlist.name)
            SubElement(container, 'upnp:class').text = 'object.container.playlistContainer'
            return (1, 1, didl)
        return None

    def _BrowseDirectChildren(self, request, objectID, filter, startingIndex, requestedCount, sortCriteria):
        # if startingIndex is 0, then ignore it
        if startingIndex == 0:
            startingIndex = None
        # if requestedCount is 0, then ignore it
        if requestedCount == 0:
            requestedCount = None
        # generate the DIDL envelope
        didl = Element("DIDL-Lite")
        didl.attrib["xmlns"] = "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"
        didl.attrib["xmlns:upnp"] = "urn:schemas-upnp-org:metadata-1-0/upnp/"
        didl.attrib["xmlns:dc"] = "http://purl.org/dc/elements/1.1/"
        # return children of the root directory
        if objectID == '0':
            container = SubElement(didl, "container")
            container.attrib["id"] = 'music'
            container.attrib["parentID"] = objectID
            container.attrib["restricted"] = "1"
            container.attrib['childCount'] = str(db.query(Album).count())
            SubElement(container, "upnp:class").text = "object.container.storageFolder"
            SubElement(container, "dc:title").text = 'Music'
            container = SubElement(didl, "container")
            container.attrib["id"] = 'playlists'
            container.attrib["parentID"] = objectID
            container.attrib["restricted"] = "1"
            container.attrib['childCount'] = str(db.query(Playlist).count())
            SubElement(container, "upnp:class").text = "object.container.storageFolder"
            SubElement(container, "dc:title").text = 'Playlists'
            return (2, 2, didl)
        # return artists in the music folder
        if objectID == 'music':
            artists = db.query(Artist, offset=startingIndex, limit=requestedCount, sort=Artist.name.descending)
            count = 0
            for artist in artists:
                count += 1
                container = SubElement(didl, "container")
                container.attrib["id"] = "artist=%i" % artist.storeID
                container.attrib["parentID"] = objectID
                container.attrib["restricted"] = "1"
                container.attrib['childCount'] = str(db.query(Album, Album.artist==artist).count())
                SubElement(container, "upnp:class").text = "object.container.person.musicArtist"
                SubElement(container, "dc:title").text = artist.name
            return (db.query(Artist).count(), count, didl)
        # returns playlists in the playlist folder
        if objectID == 'playlists':
            playlists = db.query(Playlist,
                offset=startingIndex,
                limit=requestedCount,
                sort=Playlist.name.descending
                )
            count = 0
            for playlist in playlists:
                count += 1
                container = SubElement(didl, "container")
                container.attrib["id"] = "playlist=%i" % playlist.storeID
                container.attrib["parentID"] = objectID
                container.attrib["restricted"] = "1"
                container.attrib['childCount'] = str(playlist.length)
                SubElement(container, "upnp:class").text = "object.container.playlistContainer"
                SubElement(container, "dc:title").text = playlist.name
            return (db.query(Playlist).count(), count, didl)
        # split objectID into key and value
        key,value = objectID.split('=', 1)
        # return albums of the specified artist
        if key == 'artist':
            artist = db.get(Artist, Artist.storeID==int(value))
            albums = db.query(Album,
                Album.artist==artist,
                offset=startingIndex,
                limit=requestedCount,
                sort=Album.name.descending
                )
            count = 0
            for album in albums:
                count += 1
                container = SubElement(didl, "container")
                container.attrib["id"] = "album=%i" % album.storeID
                container.attrib["parentID"] = objectID
                container.attrib["restricted"] = "1"
                container.attrib['childCount'] = str(db.query(Song, Song.album==album).count())
                SubElement(container, "upnp:class").text = "object.container.album.musicAlbum"
                SubElement(container, "dc:title").text = album.name
            return (db.count(Album, Album.artist==artist), count, didl)
        # return songs in the specified album
        if key == 'album':
            # determine the host:port of content
            host = request.headers.getHeader('host').split(':',1)[0]
            port = CoreHttpConfig.HTTP_PORT
            # find songs
            album = db.get(Album, Album.storeID==int(value))
            songs = db.query(Song,
                Song.album==album,
                offset=startingIndex,
                limit=requestedCount,
                sort=Song.trackNumber.ascending
                )
            count = 0
            for song in songs:
                count += 1
                item = SubElement(didl, "item")
                item.attrib["id"] = "song=%i" % song.storeID
                item.attrib["parentID"] = objectID
                item.attrib["restricted"] = "1"
                SubElement(item, "upnp:class").text = "object.item.audioItem.musicTrack"
                SubElement(item, "dc:title").text = song.name
                SubElement(item, "upnp:artist").text = str(song.artist.name)
                SubElement(item, "upnp:album").text = str(song.album.name)
                SubElement(item, "upnp:genre").text = str(song.album.genre.name)
                SubElement(item, "upnp:originalTrackNumber").text = str(song.trackNumber)
                resource = SubElement(item, "res")
                resource.attrib["protocolInfo"] = "http-get:*:%s:*" % str(song.file.MIMEType)
                resource.attrib["size"] = str(song.file.size)
                resource.text = "http://%s:%i/content/%i" % (host,port,song.file.storeID)
            return (db.count(Song, Song.album==album), count, didl)
        # return songs in the specified playlist
        if key == 'playlist':
            # determine the host:port of content
            host = request.headers.getHeader('host').split(':',1)[0]
            port = CoreHttpConfig.HTTP_PORT
            # 
            playlist = db.get(Playlist, Playlist.storeID==int(value))
            songs = playlist.listSongs(startingIndex, requestedCount)
            count = 0
            # we use startingIndex to calculate the trackNumber
            if startingIndex == None:
                startingIndex = 0
            for song in songs:
                count += 1
                item = SubElement(didl, "item")
                item.attrib["id"] = "song=%i" % song.storeID
                item.attrib["parentID"] = objectID
                item.attrib["restricted"] = "1"
                SubElement(item, "upnp:class").text = "object.item.audioItem.musicTrack"
                SubElement(item, "dc:title").text = song.name
                SubElement(item, "upnp:artist").text = str(song.artist.name)
                SubElement(item, "upnp:album").text = str(song.album.name)
                SubElement(item, "upnp:genre").text = str(song.album.genre.name)
                startingIndex += 1
                SubElement(item, "upnp:originalTrackNumber").text = str(startingIndex)
                resource = SubElement(item, "res")
                resource.attrib["protocolInfo"] = "http-get:*:%s:*" % str(song.file.MIMEType)
                resource.attrib["size"] = str(song.file.size)
                resource.text = "http://%s:%i/content/%i" % (host,port,song.file.storeID)
            return (playlist.length, count, didl)
        return None

    def Browse(self, request, objectID, browseFlag, filter, startingIndex, requestedCount, sortCriteria):
        """
        Browse the media library.  The media library is presented to the UPNP
        client in the following hierarchy:

        Root (objectID '0')
           \
            Music (objectID 'music')
            |   \
            |    Artist1 (objectID 'artist=1')
            |    |   \
            |    |    Album3 (objectID 'album=3')
            |    |        \
            |    |         Song4 (objectID 'song=4')
            |    |         |
            |    |         Song5 (objectID 'song=5')
            |    |         |
            |    |         ...
            |    |
            |    Artist2 (objectID 'artist=2')
            |    |
            |    ...
            |
            Playlists (objectID 'playlists')
                \
                 Playlist6 (objectID 'playlist=6')
                 |    \
                 |     Song7 (objectID 'song=7')
                 |     |
                 |     Song8 (objectID 'song=8')
                 |     |
                 |     ...
                 ...
        """
        # browse the metadata of one specific item
        if browseFlag == 'BrowseMetadata':
            ret = self._BrowseMetadata(request, objectID, filter, startingIndex, requestedCount, sortCriteria)
        elif browseFlag == 'BrowseDirectChildren':
            ret = self._BrowseDirectChildren(request, objectID, filter, startingIndex, requestedCount, sortCriteria)
        else:
            raise UPNPError(402, "unknown browse flag %s" % browseFlag)
        if ret == None:
            raise UPNPError(701, "ObjectID %i is invalid" % objectID)
        result = xmlprint(ret[2], pretty=False, withXMLDecl=False)
        return { 'TotalMatches': ret[0], 'NumberReturned': ret[1], 'Result': result, 'UpdateID': 0 }

    def GetSearchCapabilities(self, request):
        return { 'SearchCaps': '' }

    def GetSortCapabilities(self, request):
        return { 'SortCaps': '*' }

    def GetSystemUpdateID(self, request):
        return { "Id": 1 }


    #######################################################
    # Action declarations                                 #
    #######################################################

    Browse = Action(Browse,
        InArgument("ObjectID", A_ARG_TYPE_ObjectID),
        InArgument("BrowseFlag", A_ARG_TYPE_BrowseFlag),
        InArgument("Filter", A_ARG_TYPE_Filter),
        InArgument("StartingIndex", A_ARG_TYPE_Index),
        InArgument("RequestedCount", A_ARG_TYPE_Count),
        InArgument("SortCriteria", A_ARG_TYPE_SortCriteria),
        OutArgument("Result", A_ARG_TYPE_Result),
        OutArgument("NumberReturned", A_ARG_TYPE_Count),
        OutArgument("TotalMatches", A_ARG_TYPE_Count),
        OutArgument("UpdateID", A_ARG_TYPE_UpdateID)
        )
    GetSearchCapabilities = Action(GetSearchCapabilities,
        OutArgument("SearchCaps", SortCapabilities)
        )
    GetSortCapabilities = Action(GetSortCapabilities,
        OutArgument("SortCaps", SortCapabilities)
        )
    GetSystemUpdateID = Action(GetSystemUpdateID,
        OutArgument("Id", SystemUpdateID)
        )
