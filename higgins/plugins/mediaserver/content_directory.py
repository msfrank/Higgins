# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from xml.etree.ElementTree import Element, SubElement, tostring as xmltostring
from higgins.core.models import File, Song
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
    SystemUpdateID = UI4StateVar(sendEvents=True, defaultValue=1)
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
        # browse the metadata of one specific item
        if browseFlag == 'BrowseMetadata':
            songs = Song.objects.filter(id=int(objectID))
            total_matches = len(songs)
        elif browseFlag == 'BrowseDirectChildren':
            if objectID != '0':
                raise UPNPError(701, "ObjectID %i is invalid" % objectID)
            # don't return more than 250 items
            if requestedCount > 100:
                requestedCount = 100
            # get the matching songs
            total_matches = len(Song.objects.all())
            if startingIndex >= total_matches:
                raise UPNPError(402, "startingIndex %i is out of range" % startingIndex)
            if startingIndex + requestedCount > total_matches:
                requestedCount = total_matches - startingIndex
            songs = Song.objects.all()[startingIndex:startingIndex + requestedCount]
        else:
            raise UPNPError(402, "unknown browse flag %s" % browseFlag)
        # generate the DIDL
        didl = Element("{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}DIDL-Lite")
        didl.attrib["xmlns"] = "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"
        didl.attrib["xmlns:upnp"] = "urn:schemas-upnp-org:metadata-1-0/upnp/"
        didl.attrib["xmlns:dc"] = "http://purl.org/dc/elements/1.1/"
        for song in songs:
            item = SubElement(didl, "item")
            item.attrib["id"] = str(song.id)
            item.attrib["parentID"] = "0"
            item.attrib["restricted"] = "0"
            upnp_class = SubElement(item, "upnp:class")
            upnp_class.text = "object.item.audioItem.musicTrack"
            title = SubElement(item, "dc:title")
            title.text = song.name
            upnp_artist = SubElement(item, "upnp:artist")
            upnp_artist.text = str(song.artist.name)
            upnp_artist = SubElement(item, "dc:creator")
            upnp_artist.text = str(song.artist.name)
            upnp_album = SubElement(item, "upnp:album")
            upnp_album.text = str(song.album.name)
            resource = SubElement(item, "res")
            resource.attrib["protocolInfo"] = "http-get:*:%s:*" % str(song.file.mimetype)
            resource.attrib["size"] = str(song.file.size)
            resource.text = "http://%s:%i/content/%i" % (host, port, song.id)
        result = xmltostring(didl)
        number_returned = len(songs)
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
