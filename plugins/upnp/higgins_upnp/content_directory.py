# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2005, Tim Potter <tpot@samba.org>

from twisted.web2 import channel, resource, static
from twisted.web2.http import Response as HttpResponse
from higgins.core.models import File, Song
from higgins.logging import log_debug, log_error
from xml.etree.ElementTree import Element, SubElement, tostring as xmltostring
from xml.sax.saxutils import escape as xmlescape
from soap_resource import SoapResource, SoapBag as SoapResult

class ContentDirectoryControl(SoapResource):
    def locateChild(self, request, segments):
        return self, []

    def SOAP_Browse(self, args):
        # get the method arguments
        object_id = args.get_string("ObjectID", "0")
        browse_flag = args.get_string("BrowseFlag", "")
        filter = args.get_string("Filter", "")
        request_start = args.get_integer("StartingIndex", 0)
        request_count = args.get_integer("RequestedCount", 0)
        # get the matching songs
        songs = Song.objects.all()[request_start:request_start+request_count]
        # generate the DIDL
        didl = Element("{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite}DIDL-Lite")
        for song in songs:
            item = SubElement(didl, "{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite}item")
            item.attrib["id"] = str(song.id)
            item.attrib["parentID"] = "0"
            item.attrib["restricted"] = "0"
            title = SubElement(item, "{http://purl.org/dc/elements/1.1/}title")
            title.text = song.name
            upnp_class = SubElement(item, "{urn:schemas-upnp-org:metadata-1-0/upnp}class")
            upnp_class.text = "object.item.audioItem"
            resource = SubElement(item, "{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite}res")
            resource.attrib["protocolInfo"] = "http-get:*:audio/mpeg"
            #resource.attrib["size"] = 
            resource.text = "http://%s:%i/content/%i" % ('http://127.0.0.1', 31338, song.id)
        # build the SOAP result
        result = SoapResult()
        result.set("xsd:int", "NumberReturned", len(songs))
        result.set("xsd:int", "TotalMatches", len(songs))
        result.set("xsd:int", "UpdateID", 1)
        result.set("xsd:string", "Result", xmlescape(xmltostring(didl)))
        return result

class ServiceDescription(static.Data):
    def __init__(self):
        static.Data.__init__(self, """
<scpd xmlns="urn:schemas-upnp-org:service-1-0">
    <specVersion>
        <major>1</major>
        <minor>0</minor>
    </specVersion>
    <actionList>
        <action>
            <name>Browse</name>
            <argumentList>
                <argument>
                    <name>ObjectID</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_ObjectID</relatedStateVariable>
                </argument>
                <argument>
                    <name>BrowseFlag</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_BrowseFlag</relatedStateVariable>
                </argument>
                <argument>
                    <name>Filter</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_Filter</relatedStateVariable>
                </argument>
                <argument>
                    <name>StartingIndex</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_Index</relatedStateVariable>
                </argument>
                <argument>
                    <name>RequestedCount</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable>
                </argument>
                <argument>
                    <name>SortCriteria</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_SortCriteria</relatedStateVariable>
                </argument>
                <argument>
                    <name>Result</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_Result</relatedStateVariable>
                    </argument>
                <argument>
                    <name>NumberReturned</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable>
                </argument>
                <argument>
                    <name>TotalMatches</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable>
                </argument>
                <argument>
                    <name>UpdateID</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_UpdateID</relatedStateVariable>
                </argument>
            </argumentList>
        </action>
        <action>
            <name>GetSortCapabilities</name>
            <argumentList>
                <argument>
                    <name>SortCaps</name>
                    <direction>out</direction>
                    <relatedStateVariable>SortCapabilities</relatedStateVariable>
                </argument>
            </argumentList>
        </action>
        <action>
            <name>GetSystemUpdateID</name>
            <argumentList>
                <argument>
                    <name>Id</name>
                    <direction>out</direction>
                    <relatedStateVariable>SystemUpdateID</relatedStateVariable>
                </argument>
            </argumentList>
        </action>
        <!--
        <action>
            <name>Search</name>
            <argumentList>
                <argument>
                    <name>ContainerID</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_ObjectID</relatedStateVariable>
                </argument>
                <argument>
                    <name>SearchCriteria</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_SearchCriteria</relatedStateVariable>
                </argument>
                <argument>
                    <name>Filter</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_Filter</relatedStateVariable>
                </argument>
                <argument>
                    <name>StartingIndex</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_Index</relatedStateVariable>
                </argument>
                <argument>
                    <name>RequestedCount</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable>
                </argument>
                <argument>
                    <name>SortCriteria</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_SortCriteria</relatedStateVariable>
                </argument>
                <argument>
                    <name>Result</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_Result</relatedStateVariable>
                </argument>
                <argument>
                    <name>NumberReturned</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable>
                </argument>
                <argument>
                    <name>TotalMatches</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_Count</relatedStateVariable>
                </argument>
                <argument>
                    <name>UpdateID</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_UpdateID</relatedStateVariable>
                </argument>
            </argumentList>
        </action>
        -->
        <action>
            <name>GetSearchCapabilities</name>
            <argumentList>
                <argument>
                    <name>SearchCaps</name>
                    <direction>out</direction>
                    <relatedStateVariable>SearchCapabilities</relatedStateVariable>
                </argument>
            </argumentList>
        </action>
    </actionList>
    <serviceStateTable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_BrowseFlag</name>
            <dataType>string</dataType>
            <allowedValueList>
                <allowedValue>BrowseMetadata</allowedValue>
                <allowedValue>BrowseDirectChildren</allowedValue>
            </allowedValueList>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_SearchCriteria</name>
            <dataType>string</dataType>
        </stateVariable>
        <stateVariable sendEvents="yes">
            <name>SystemUpdateID</name>
            <dataType>ui4</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_Count</name>
            <dataType>ui4</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_SortCriteria</name>
            <dataType>string</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>SortCapabilities</name>
            <dataType>string</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_Index</name>
            <dataType>ui4</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_ObjectID</name>
            <dataType>string</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_UpdateID</name>
            <dataType>ui4</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_Result</name>
            <dataType>string</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>SearchCapabilities</name>
            <dataType>string</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_Filter</name>
            <dataType>string</dataType>
        </stateVariable>
    </serviceStateTable>
</scpd>
        """, 'text/xml')

    def allowedMethods(self):
        return ('GET',)

    def locateChild(self, request, segments):
        return self, []

class ContentDirectory(resource.Resource):
    def locateChild(self, request, segments):
        if segments[0] == "scpd.xml":
            return ServiceDescription(), segments[1:]
        if segments[0] == "control":
            return ContentDirectoryControl(), segments[1:]
        return None, []
