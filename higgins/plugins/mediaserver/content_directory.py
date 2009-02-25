# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from xml.etree.ElementTree import Element, SubElement, tostring as xmltostring
from higgins.upnp.service import Service, Action, Argument, StateVar
from higgins.core.models import File, Song
from higgins.plugins.mediaserver.logger import logger

class ContentDirectory(Service):
    upnp_service_type = "urn:schemas-upnp-org:service:ContentDirectory:1"
    upnp_service_id = "urn:upnp-org:serviceId:urn:schemas-upnp-org:service:ContentDirectory"

    A_ARG_TYPE_BrowserFlag = StateVar(StateVar.TYPE_STRING,
                                      sendEvents="no",
                                      allowedValueList=("BrowseMetadata", "BrowseDirectChildren")
        )
    A_ARG_TYPE_SearchCriteria = StateVar(StateVar.TYPE_STRING, sendEvents="no")
    SystemUpdateID = StateVar(StateVar.TYPE_UI4, sendEvents="yes")
    A_ARG_TYPE_Count = StateVar(StateVar.TYPE_UI4, sendEvents="no")
    A_ARG_TYPE_SortCriteria = StateVar(StateVar.TYPE_STRING, sendEvents="no")
    SortCapabilities = StateVar(StateVar.TYPE_STRING, sendEvents="no")
    A_ARG_TYPE_Index = StateVar(StateVar.TYPE_UI4, sendEvents="no")
    A_ARG_TYPE_ObjectID = StateVar(StateVar.TYPE_STRING, sendEvents="no")
    A_ARG_TYPE_UpdateID = StateVar(StateVar.TYPE_UI4, sendEvents="no")
    A_ARG_TYPE_Result = StateVar(StateVar.TYPE_STRING, sendEvents="no")
    SearchCapabilities = StateVar(StateVar.TYPE_STRING, sendEvents="no")
    A_ARG_TYPE_Filter = StateVar(StateVar.TYPE_STRING, sendEvents="no")

    def GetSystemUpdateID(self):
        return { "Id": 1 }
    GetSystemUpdateID = Action(GetSystemUpdateID,
        Argument("Id", Argument.DIRECTION_OUT, "SystemUpdateID")
        )

    def Browse(self, objectID, browseFlag, filter, startingIndex, requestedCount, sortCriteria):
        # get the matching songs
        songs = Song.objects.all()[startingIndex:startingIndex + requestedCount]
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
            #item.attrib["size"] = song.file.size
            #item.attrib["duration"] = song.duration
            upnp_class = SubElement(item, "upnp:class")
            upnp_class.text = "object.item.audioItem"
            title = SubElement(item, "dc:title")
            title.text = song.name
            upnp_artist = SubElement(item, "upnp:artist")
            upnp_artist.text = str(song.artist.name)
            upnp_album = SubElement(item, "upnp:album")
            upnp_album.text = str(song.album.name)
            #upnp_genre = SubElement(item, "upnp:genre")
            #upnp_genre.text = 
            resource = SubElement(item, "res")
            resource.attrib["protocolInfo"] = "http-get:*:audio/mpeg:*"
            #resource.attrib["size"] = 
            resource.text = "http://%s:%i/content/%i" % (self.addr, self.port, song.id)
        result = xmltostring(didl)
        return { 'NumberReturned': len(songs), 'TotalMatches': len(songs), 'Result': result, 'UpdateID': 1 }
    Browse = Action(Browse,
        Argument("ObjectID", Argument.DIRECTION_IN, "A_ARG_TYPE_ObjectID"),
        Argument("BrowseFlag", Argument.DIRECTION_IN, "A_ARG_TYPE_BrowseFlag"),
        Argument("Filter", Argument.DIRECTION_IN, "A_ARG_TYPE_Filter"),
        Argument("StartingIndex", Argument.DIRECTION_IN, "A_ARG_TYPE_Index"),
        Argument("RequestedCount", Argument.DIRECTION_IN, "A_ARG_TYPE_Count"),
        Argument("SortCriteria", Argument.DIRECTION_IN, "A_ARG_TYPE_SortCriteria"),
        Argument("Result", Argument.DIRECTION_OUT, "A_ARG_TYPE_Result"),
        Argument("NumberReturned", Argument.DIRECTION_OUT, "A_ARG_TYPE_Count"),
        Argument("TotalMatches", Argument.DIRECTION_OUT, "A_ARG_TYPE_Count"),
        Argument("UpdateID", Argument.DIRECTION_OUT, "A_ARG_TYPE_UpdateID")
        )

    #def GetSortCapabilities(self):
    #    pass
    #GetSortCapabilities = Action(GetSortCapabilities,
    #    Argument("SortCaps", Argument.DIRECTION_OUT, "SortCapabilities"),
    #    )
