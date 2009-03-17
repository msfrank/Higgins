# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.upnp.device_service import UPNPDeviceService
from higgins.upnp.action import Action, InArgument, OutArgument
from higgins.upnp.statevar import StringStateVar, I4StateVar
from higgins.plugins.mediaserver.logger import logger

class ConnectionManager(UPNPDeviceService):
    upnp_service_type = "urn:schemas-upnp-org:service:ConnectionManager:1"
    upnp_service_id = "urn:upnp-org:serviceId:urn:schemas-upnp-org:service:ConnectionManager"

    #######################################################
    # State Variable declarations                         #
    #######################################################

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

    #######################################################
    # Action definitions                                  #
    #######################################################

    def GetProtocolInfo(self, request):
        return { 'Source': 'http-get', 'Sink': '' }

    def GetCurrentConnectionInfo(self, request, connection_id):
        return {
            'RcsID': 0,
            'AVTransportID': 0,
            'ProtocolInfo': 'http-get',
            'PeerConnectionManager': '',
            'PeerConnectionID': -1,
            'Direction': 'Input',
            'Status': 'OK'
            }

    def GetCurrentConnectionIDs(self, request):
        return { 'ConnectionIDs': '0' }

    #######################################################
    # Action declarations                                 #
    #######################################################

    GetCurrentConnectionInfo = Action(GetCurrentConnectionInfo,
        InArgument("ConnectionID", A_ARG_TYPE_ConnectionID),
        OutArgument("RcsID", A_ARG_TYPE_RcsID),
        OutArgument("AvTransportID", A_ARG_TYPE_AVTransportID),
        OutArgument("ProtocolInfo", A_ARG_TYPE_ProtocolInfo),
        OutArgument("PeerConnectionManager", A_ARG_TYPE_ConnectionManager),
        OutArgument("PeerConnectionID", A_ARG_TYPE_ConnectionID),
        OutArgument("Direction", A_ARG_TYPE_Direction),
        OutArgument("Status", A_ARG_TYPE_ConnectionStatus),
        )
    GetProtocolInfo = Action(GetProtocolInfo,
        OutArgument("Source", SourceProtocolInfo),
        OutArgument("Sink", SinkProtocolInfo)
        )
    GetCurrentConnectionIDs = Action(GetCurrentConnectionIDs,
        OutArgument("ConnectionIDs", CurrentConnectionIDs)
        )
