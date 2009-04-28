# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.upnp.device_service import UPNPDeviceService
from higgins.upnp.action import Action, InArgument, OutArgument
from higgins.upnp.statevar import StringStateVar, I4StateVar
from higgins.plugins.mediaserver.logger import logger

class AVTransport(UPNPDeviceService):
    upnp_service_type = "urn:schemas-upnp-org:service:AVTransport:1"
    upnp_service_id = "urn:upnp-org:serviceId:urn:schemas-upnp-org:service:AVTransport"

    #######################################################
    # State Variable declarations                         #
    #######################################################

    TransportState = StringStateVar(allowedValueList=("STOPPED","PLAYING"))
    TransportStatus = StringStateVar()
    PlaybackStorageMedium = StringStateVar()
    RecordStorageMedium = StringStateVar()
    PossiblePlaybackStorageMedia = StringStateVar()
    PossibleRecordStorageMedia = StringStateVar()
    CurrentPlayMode = StringStateVar()
    TransportPlaySpeed = StringStateVar()
    RecordMediumWriteStatus = StringStateVar()
    CurrentRecordQualityMode = StringStateVar()
    PossibleRecordQualityModes = StringStateVar()
    NumberOfTracks = UI4StateVar(allowedMin=0)
    CurrentTrack = UI4StateVar(allowedMin=0, allowedStep=1)
    CurrentTrackDuration = StringStateVar()
    CurrentMediaDuration = StringStateVar()
    CurrentTrackMetaData = StringStateVar()
    CurrentTrackURI = StringStateVar()
    AVTransportURI = StringStateVar()
    AVTransportURIMetaData = StringStateVar()
    NextAVTransportURI = StringStateVar()
    NextAVTransportURIMetaData = StringStateVar()
    RelativeTimePosition = StringStateVar()
    AbsoluteTimePosition = StringStateVar()
    RelativeCounterPosition = I4StateVar()
    AbsoluteCounterPosition = I4StateVar()
    CurrentTransportActions = StringStateVar()
    LastChange = StringStateVar(sendEvents="yes")
    A_ARG_TYPE_SeekMode = StringStateVar()
    A_ARG_TYPE_SeekTarget = StringStateVar()
    A_ARG_TYPE_InstanceID = UI4StateVar()

    #######################################################
    # Action definitions                                  #
    #######################################################

    def SetAVTransportURI(self, request, id, uri, metadata):
        pass

    def GetMediaInfo(self, request, id):
        return {
            'NrTracks': ntracks,
            'MediaDuration': duration,
            'CurrentURI': uri,
            'CurrentURIMetaData': metadata,
            'NextURI': next,
            'NextURIMetaData': metadata,
            'PlayMedium': play_medium,
            'RecordMedium': record_medium,
            'WriteStatus': write_status
            }

    def GetTransportInfo(self, request, id):
        return {
            "CurrentTransportState": TransportState,
            "CurrentTransportStatus": TransportStatus,
            "CurrentSpeed": TransportPlaySpeed
            }

    def GetPositionInfo(self, request, id):
        return {
            "Track": CurrentTrack,
            "TrackDuration": CurrentTrackDuration,
            "TrackMetaData": CurrentTrackMetaData,
            "TrackURI": CurrentTrackURI,
            "RelTime": RelativeTimePosition,
            "AbsTime": AbsoluteTimePosition,
            "RelCount": RelativeCounterPosition,
            "AbsCount": AbsoluteCounterPosition
            }

    def GetDeviceCapabilities(self, request, id):
        return {
            "PlayMedia": PossiblePlaybackStorageMedia,
            "RecMedia": PossibleRecordStorageMedia,
            "RecQualityModes": PossibleRecordQualityModes
            }
    
    def GetTransportSettings(self, request, id):
        return {
            "PlayMode": CurrentPlayMode,
            "RecQualityMode": CurrentRecordQualityMode
            }
        
    def Play(self, request, id):
        return { "Speed": 1 }

    def Pause(self, request, id):
        pass
    
    def Stop(self, request, id):
        pass
    
    def Seek(self, request, id, unit, target):
        pass
    
    def Previous(self, request, id):
        pass
    
    def Next(self, request, id):
        pass

    #######################################################
    # Action declarations                                 #
    #######################################################

    SetAVTransportURI = Action(SetAVTransportURI,
        InArgument("InstanceID", A_ARG_TYPE_InstanceID),
        InArgument("CurrentURI", AVTransportURI),
        InArgument("CurrentURIMetaData", AVTransportURIMetaData)
        )
    GetMediaInfo = Action(GetMediaInfo,
        InArgument("InstanceID", A_ARG_TYPE_InstanceID),
        OutArgument("NrTracks", NumberOfTracks),
        OutArgument("MediaDuration", CurrentMediaDuration),
        OutArgument("CurrentURI", AVTransportURI),
        OutArgument("CurrentURIMetaData", AVTransportURIMetaData),
        OutArgument("NextURI", NextAVTransportURI),
        OutArgument("NextURIMetaData", NextAVTransportURIMetaData),
        OutArgument("PlayMedium", PlaybackStorageMedium),
        OutArgument("RecordMedium", RecordStorageMedium),
        OutArgument("WriteStatus", RecordMediumWriteStatus)
        )
    GetTransportInfo = Action(GetTransportInfo,
        InArgument("InstanceID", A_ARG_TYPE_InstanceID),
        OutArgument("CurrentTransportState", TransportState),
        OutArgument("CurrentTransportStatus", TransportStatus),
        OutArgument("CurrentSpeed", TransportPlaySpeed)
        )
    GetPositionInfo = Action(GetPositionInfo,
        InArgument("InstanceID", A_ARG_TYPE_InstanceID),
        OutArgument("Track", CurrentTrack),
        OutArgument("TrackDuration", CurrentTrackDuration),
        OutArgument("TrackMetaData", CurrentTrackMetaData),
        OutArgument("TrackURI", CurrentTrackURI),
        OutArgument("RelTime", RelativeTimePosition),
        OutArgument("AbsTime", AbsoluteTimePosition),
        OutArgument("RelCount", RelativeCounterPosition),
        OutArgument("AbsCount", AbsoluteCounterPosition)
        )
    GetDeviceCapabilities = Action(GetDeviceCapabilities,
        InArgument("InstanceID", A_ARG_TYPE_InstanceID),
        OutArgument("PlayMedia", PossiblePlaybackStorageMedia),
        OutArgument("RecMedia", PossibleRecordStorageMedia),
        OutArgument("RecQualityModes", PossibleRecordQualityModes)
        )
    GetTransportSettings = Action(GetTransportSettings,
        InArgument("InstanceID", A_ARG_TYPE_InstanceID),
        OutArgument("PlayMode", CurrentPlayMode),
        OutArgument("RecQualityMode", CurrentRecordQualityMode)
        )
    Play = Action(Play,
        InArgument("InstanceID", A_ARG_TYPE_InstanceID),
        OutArgument("Speed", TransportPlaySpeed)
        )
    Pause = Action(Pause,
        InArgument("InstanceID", A_ARG_TYPE_InstanceID),
        )
    Stop = Action(Stop,
        InArgument("InstanceID", A_ARG_TYPE_InstanceID)
        )
    Seek = Action(Seek,
        InArgument("InstanceID", A_ARG_TYPE_InstanceID),
        InArgument("Unit", A_ARG_TYPE_SeekMode),
        InArgument("Target", A_ARG_TYPE_SeekTarget)
        )
    Previous = Action(Previous,
        InArgument("InstanceID", A_ARG_TYPE_InstanceID),
        )
    Next = Action(Next,
        InArgument("InstanceID", A_ARG_TYPE_InstanceID),
        )
