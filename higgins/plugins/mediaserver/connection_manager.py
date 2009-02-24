# Portions of this code from the pymeds project  are licensed under
# the MIT license: http://opensource.org/licenses/mit-license.php
#
# Copyright 2005, Tim Potter <tpot@samba.org>
# Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

from higgins.upnp.service import Service, Action, InArgument, OutArgument
from higgins.upnp.statevar import StringStateVar, I4StateVar
from higgins.plugins.mediaserver.logger import logger

class ConnectionManager(Service):
    upnp_service_type = "urn:schemas-upnp-org:service:ConnectionManager:1"
    upnp_service_id = "urn:upnp-org:serviceId:urn:schemas-upnp-org:service:ConnectionManager"

    A_ARG_TYPE_AVTransportID = I4StateVar()
    A_ARG_TYPE_RcsID = I4StateVar()
    A_ARG_TYPE_ConnectionID = I4StateVar()
    A_ARG_TYPE_ConnectionManager = StringStateVar()
    A_ARG_TYPE_Direction = StringStateVar(allowedValueList=("Input", "Output"))
    SourceProtocolInfo = StringStateVar(sendEvents="yes")
    SinkProtocolInfo = StringStateVar(sendEvents="yes")
    CurrentConnectionIDs = StringStateVar(sendEvents="yes")
    A_ARG_TYPE_ProtocolInfo = StringStateVar()
    A_ARG_TYPE_ConnectionStatus = StringStateVar(
        allowedValueList=("OK", "ContentFormatMismatch", "InsufficientBandwidth", "UnreliableChannel", "Unknown")
        )

    def GetCurrentConnectionInfo(self, connection_id):
        pass
    GetCurrentConnectionInfo = Action(GetCurrentConnectionInfo,
        InArgument("ConnectionID", "A_ARG_TYPE_ConnectionID"),
        OutArgument("RcsID", "A_ARG_TYPE_RcsID"),
        OutArgument("AvTransportID", "A_ARG_TYPE_AVTransportID"),
        OutArgument("ProtocolInfo", "A_ARG_TYPE_ProtocolInfo"),
        OutArgument("PeerConnectionManager", "A_ARG_TYPE_ConnectionManager"),
        OutArgument("PeerConnectionID", "A_ARG_TYPE_ConnectionID"),
        OutArgument("Direction", "A_ARG_TYPE_Direction"),
        OutArgument("Status", "A_ARG_TYPE_ConnectionStatus"),
        )

    def GetProtocolInfo(self):
        pass
    GetProtocolInfo = Action(GetProtocolInfo,
        OutArgument("Source", "SourceProtocolInfo"),
        OutArgument("Sink", "SinkProtocolInfo")
        )

    def GetCurrentConnectionIDs(self):
        pass
    GetCurrentConnectionIDs = Action(GetCurrentConnectionIDs,
        OutArgument("ConnectionIDs", "CurrentConnectionIDs")
        )
