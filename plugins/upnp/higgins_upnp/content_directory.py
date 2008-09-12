# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2005, Tim Potter <tpot@samba.org>

from twisted.web import http, resource, soap
from higgins.logging import log_debug, log_error
import SOAPpy

class UPnPPublisher(soap.SOAPPublisher):
    """UPnP requires OUT parameters to be returned in a slightly
    different way than the SOAPPublisher class does."""

    def _gotResult(self, result, request, methodName):
        response = SOAPpy.buildSOAP(kw=result, encoding=self.encoding)
        self._sendResponse(request, response)
        log_debug("UPnPPublisher._gotResult()")

    def _gotError(self, failure, request, methodName):
        class errorCode(Exception):
            def __init__(self, status):
                self.status = status
        e = failure.value
        status = 500
        if isinstance(e, SOAPpy.faultType):
            fault = e
        else:
            if isinstance(e, errorCode):
                status = e.status
            #else:
            #    failure.printTraceback(file = log.logfile)
            fault = SOAPpy.faultType("%s:Server" % SOAPpy.NS.ENV_T, "Method %s failed." % methodName)
        response = SOAPpy.buildSOAP(fault, encoding=self.encoding)
        self._sendResponse(request, response, status=status)
        log_debug("UPnPPublisher._gotError(): status=%d, failure=%s, fault=%s", (status,failure,fault))

class ContentDirectoryControl(UPnPPublisher, dict):
    updateID = property(lambda x: x['0'].updateID)
    urlbase = property(lambda x: x._urlbase)
    BrowseFlags = ('BrowseMetaData', 'BrowseDirectChildren')

    def __init__(self):
        UPnPPublisher.__init__(self)

    def soap_GetSearchCapabilities(self, *args, **kwargs):
        """Required: Return the searching capabilities supported by the device."""
        log_debug('GetSearchCapabilities()')
        return { 'SearchCapabilitiesResponse': { 'SearchCaps': '' }}

    def soap_GetSortCapabilities(self, *args, **kwargs):
        """Required: Return the CSV list of meta-data tags that can be used in sortCriteria."""
        log_debug('GetSortCapabilities()')
        return { 'SortCapabilitiesResponse': { 'SortCaps': '' }}

    def soap_GetSystemUpdateID(self, *args, **kwargs):
        """Required: Return the current value of state variable SystemUpdateID."""
        log_debug('GetSystemUpdateID()')
        return { 'SystemUpdateIdResponse': { 'Id': self.updateID }}

    def soap_Browse(self, *args):
        log_debug('Browse()')
        return { 'Result': "", 'NumberReturned': 0, 'TotalMatches': 0, 'UpdateID': self.updateID }

class ServiceDescription(resource.Resource):
    isLeaf = True
    allowedMethods = ('GET',)
    def render_GET(self, request):
        return """
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
        """

class ContentDirectory(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("scpd.xml", ServiceDescription())
        self.putChild("control", ContentDirectoryControl())
