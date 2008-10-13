# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
# Copyright 2005, Tim Potter <tpot@samba.org>

from twisted.web2 import channel, resource, static
from twisted.web2.http import Response as HttpResponse
from higgins.logging import log_debug, log_error

class ConnectionManagerControl(resource.Resource):
    def locateChild(self, request, segments):
        return self, []

    def render_GET(self, request):
        log_debug("ConnectionManagerControl: GET request=%s", request)
        return HttpResponse(200)

    def render_POST(self, request):
        log_debug("ConnectionManagerControl: POST request=%s", request)
        return HttpResponse(200)

class ServiceDescription(static.Data):
    def allowedMethods(self):
       return ('GET',)

    def __init__(self):
        static.Data.__init__(self, """
<scpd xmlns="urn:schemas-upnp-org:service-1-0">
    <specVersion>
        <major>1</major>
        <minor>0</minor>
    </specVersion>
    <actionList>
        <action>
            <name>GetCurrentConnectionInfo</name>
            <argumentList>
                <argument>
                    <name>ConnectionID</name>
                    <direction>in</direction>
                    <relatedStateVariable>A_ARG_TYPE_ConnectionID</relatedStateVariable>
                </argument>
                <argument>
                    <name>RcsID</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_RcsID</relatedStateVariable>
                </argument>
                <argument>
                    <name>AVTransportID</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_AVTransportID</relatedStateVariable>
                </argument>
                <argument>
                    <name>ProtocolInfo</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_ProtocolInfo</relatedStateVariable>
                </argument>
                <argument>
                    <name>PeerConnectionManager</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_ConnectionManager</relatedStateVariable>
                </argument>
                <argument>
                    <name>PeerConnectionID</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_ConnectionID</relatedStateVariable>
                </argument>
                <argument>
                    <name>Direction</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_Direction</relatedStateVariable>
                </argument>
                <argument>
                    <name>Status</name>
                    <direction>out</direction>
                    <relatedStateVariable>A_ARG_TYPE_ConnectionStatus</relatedStateVariable>
                </argument>
            </argumentList>
        </action>
        <action>
            <name>GetProtocolInfo</name>
            <argumentList>
                <argument>
                    <name>Source</name>
                    <direction>out</direction>
                    <relatedStateVariable>SourceProtocolInfo</relatedStateVariable>
                </argument>
                <argument>
                    <name>Sink</name>
                    <direction>out</direction>
                    <relatedStateVariable>SinkProtocolInfo</relatedStateVariable>
                </argument>
            </argumentList>
        </action>
        <action>
            <name>GetCurrentConnectionIDs</name>
            <argumentList>
                <argument>
                    <name>ConnectionIDs</name>
                    <direction>out</direction>
                    <relatedStateVariable>CurrentConnectionIDs</relatedStateVariable>
                </argument>
            </argumentList>
        </action>
    </actionList>
    <serviceStateTable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_ProtocolInfo</name>
            <dataType>string</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_ConnectionStatus</name>
            <dataType>string</dataType>
            <allowedValueList>
                <allowedValue>OK</allowedValue>
                <allowedValue>ContentFormatMismatch</allowedValue>
                <allowedValue>InsufficientBandwidth</allowedValue>
                <allowedValue>UnreliableChannel</allowedValue>
                <allowedValue>Unknown</allowedValue>
            </allowedValueList>
        </stateVariable>
            <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_AVTransportID</name>
            <dataType>i4</dataType>
        </stateVariable>
            <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_RcsID</name>
            <dataType>i4</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_ConnectionID</name>
            <dataType>i4</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_ConnectionManager</name>
            <dataType>string</dataType>
        </stateVariable>
        <stateVariable sendEvents="yes">
            <name>SourceProtocolInfo</name>
            <dataType>string</dataType>
        </stateVariable>
        <stateVariable sendEvents="yes">
            <name>SinkProtocolInfo</name>
            <dataType>string</dataType>
        </stateVariable>
        <stateVariable sendEvents="no">
            <name>A_ARG_TYPE_Direction</name>
            <dataType>string</dataType>
            <allowedValueList>
                <allowedValue>Input</allowedValue>
                <allowedValue>Output</allowedValue>
            </allowedValueList>
        </stateVariable>
        <stateVariable sendEvents="yes">
            <name>CurrentConnectionIDs</name>
            <dataType>string</dataType>
        </stateVariable>
    </serviceStateTable>
</scpd>
        """, 'text/xml')

    def locateChild(self, request, segments):
        return self, []

class ConnectionManager(resource.Resource):
    def locateChild(self, request, segments):
        if segments[0] == "scpd.xml":
            return ServiceDescription(), segments[1:]
        if segments[0] == "control":
            return ConnectionManagerControl(), segments[1:]
        return None, []
