# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from xml.etree.ElementTree import Element, SubElement, tostring as xmltostring
from higgins.core.models import Artist, Album, Song, File, Playlist
from higgins.core.service import CoreHttpConfig
from higgins.upnp.device_service import UPNPDeviceService
from higgins.upnp.statevar import StringStateVar, UI4StateVar
from higgins.upnp.action import Action, InArgument, OutArgument
from higgins.upnp.error import UPNPError
from higgins.plugins.mediaserver.logger import logger

class ContentDirectory(UPNPDeviceService):
    upnp_service_type = "urn:schemas-upnp-org:service:ContentDirectory:1"
    upnp_service_id = "urn:upnp-org:serviceId:urn:schemas-upnp-org:service:ContentDirectory"

    #######################################################
    # State Variable declarations                         #
    #######################################################

    A_ARG_TYPE_BrowseFlag = StringStateVar(allowedValueList=("BrowseMetadata", "BrowseDirectChildren"))
    A_ARG_TYPE_SearchCriteria = StringStateVar()
    SystemUpdateID = UI4StateVar(sendEvents=True, defaultValue=0)
    ContainerUpdateIDs = StringStateVar(sendEvents=True, defaultValue="0,1")
    A_ARG_TYPE_Count = UI4StateVar()
    A_ARG_TYPE_SortCriteria = StringStateVar()
    SortCapabilities = StringStateVar()
    A_ARG_TYPE_Index = UI4StateVar()
    A_ARG_TYPE_ObjectID = StringStateVar()
    A_ARG_TYPE_UpdateID = UI4StateVar()
    A_ARG_TYPE_Result = StringStateVar()
    SearchCapabilities = StringStateVar()
    A_ARG_TYPE_Filter = StringStateVar()

    #######################################################
    # Action definitions                                  #
    #######################################################

    def Browse(self, request, objectID, browseFlag, filter, startingIndex, requestedCount, sortCriteria):
        # determine the host:port of content
        host = request.headers.getHeader('host').split(':',1)[0]
        port = CoreHttpConfig.HTTP_PORT
        # break up the objectID into segments.  objectIDs have the following form:
        # 0/<artist>/<album>/<song>
        segments = objectID.split('/')
        if len(segments) < 1 or segments[0] != '0':
            raise UPNPError(701, "ObjectID %i is invalid" % objectID)
        # generate the DIDL envelope
        didl = Element("{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}DIDL-Lite")
        didl.attrib["xmlns"] = "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"
        didl.attrib["xmlns:upnp"] = "urn:schemas-upnp-org:metadata-1-0/upnp/"
        didl.attrib["xmlns:dc"] = "http://purl.org/dc/elements/1.1/"
        # browse the metadata of one specific item
        if browseFlag == 'BrowseMetadata':
            if len(segments) == 1:
                container = SubElement(didl, 'container')
                container.attrib['id'] = objectID
                container.attrib['parentID'] = '-1'
                container.attrib['restricted'] = 'true'
                container.attrib['childCount'] = str(len(Artist.objects.all()))
                SubElement(container, 'dc:title').text = 'Music on Higgins'
                SubElement(container, 'upnp:class').text = 'object.container.storageFolder'
            elif len(segments) == 2:
                artist = Artist.objects.get(id=int(segments[1]))
                container = SubElement(didl, 'container')
                container.attrib['id'] = objectID
                container.attrib['parentID'] = '0'
                container.attrib['restricted'] = 'true'
                container.attrib['childCount'] = str(len(Album.objects.filter(artist=artist)))
                SubElement(container, 'dc:title').text = str(artist.name)
                SubElement(container, 'upnp:class').text = 'object.container.person.musicArtist'
            elif len(segments) == 3:
                album = Album.objects.get(id=int(segments[2]), artist=int(segments[1]))
                container = SubElement(didl, 'container')
                container.attrib['id'] = objectID
                container.attrib['parentID'] = '/'.join(segments[:1])
                container.attrib['restricted'] = 'true'
                container.attrib['childCount'] = str(len(Song.objects.filter(album=album)))
                SubElement(container, 'dc:title').text = str(album.name)
                SubElement(container, 'upnp:class').text = 'object.container.album.musicAlbum'
            total_matches = 1
            number_returned = 1
        elif browseFlag == 'BrowseDirectChildren':
            def getMatches(startingIndex, requestedCount, qset):
                # don't return more than 100 items
                total_matches = len(qset)
                if requestedCount > 100 or requestedCount == 0:
                    requestedCount = 100
                if startingIndex >= total_matches:
                    raise UPNPError(402, "startingIndex %i is out of range" % startingIndex)
                if startingIndex + requestedCount > total_matches:
                    requestedCount = total_matches - startingIndex
                matches = qset[startingIndex:startingIndex + requestedCount]
                number_returned = len(matches)
                retval = (matches, total_matches, number_returned)
                logger.log_debug("getMatches: %s" % str(retval))
                return retval
            # determine the number of matches
            if len(segments) == 1:
                qset = Artist.objects.all()
                matches,total_matches,number_returned = getMatches(startingIndex, requestedCount, qset)
                for artist in matches:
                    container = SubElement(didl, "container")
                    container.attrib["id"] = objectID + '/' + str(artist.id)
                    container.attrib["parentID"] = '/'.join(segments[:-1])
                    container.attrib["restricted"] = "true"
                    container.attrib['childCount'] = str(len(Album.objects.filter(artist=artist)))
                    SubElement(container, "upnp:class").text = "object.container.person.musicArtist"
                    SubElement(container, "dc:title").text = artist.name
            elif len(segments) == 2:
                qset = Album.objects.filter(artist=int(segments[1]))
                matches,total_matches,number_returned = getMatches(startingIndex, requestedCount, qset)
                for album in matches:
                    container = SubElement(didl, "container")
                    container.attrib["id"] = objectID + '/' + str(album.id)
                    container.attrib["parentID"] = '/'.join(segments[:-1])
                    container.attrib["restricted"] = "true"
                    container.attrib['childCount'] = str(len(Song.objects.filter(album=album)))
                    SubElement(container, "upnp:class").text = "object.container.album.musicAlbum"
                    SubElement(container, "dc:title").text = album.name
            elif len(segments) == 3:
                qset = Song.objects.filter(album=int(segments[2]))
                matches,total_matches,number_returned = getMatches(startingIndex, requestedCount, qset)
                for song in matches:
                    item = SubElement(didl, "item")
                    item.attrib["id"] = objectID + '/' + str(song.id)
                    item.attrib["parentID"] = '/'.join(segments[:-1])
                    item.attrib["restricted"] = "true"
                    SubElement(item, "upnp:class").text = "object.item.audioItem.musicTrack"
                    SubElement(item, "dc:title").text = song.name
                    SubElement(item, "upnp:artist").text = str(song.artist.name)
                    SubElement(item, "dc:creator").text = str(song.artist.name)
                    SubElement(item, "upnp:album").text = str(song.album.name)
                    resource = SubElement(item, "res")
                    resource.attrib["protocolInfo"] = "http-get:*:%s:*" % str(song.file.mimetype)
                    resource.attrib["size"] = str(song.file.size)
                    resource.text = "http://%s:%i/content/%i" % (host, port, song.id)
        else:
            raise UPNPError(402, "unknown browse flag %s" % browseFlag)
        result = xmltostring(didl)
        update_id = 1
        return {
            'NumberReturned': number_returned,
            'TotalMatches': total_matches,
            'Result': result,
            'UpdateID': update_id
            }

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
