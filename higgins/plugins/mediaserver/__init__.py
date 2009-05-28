# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.upnp.device import UPNPDevice
from higgins.plugins.mediaserver.connection_manager import ConnectionManager
from higgins.plugins.mediaserver.content_directory import ContentDirectory
from higgins.plugins.mediaserver.logger import logger

class MediaserverDevice(UPNPDevice):
    pretty_name = "UPnP Media Server"
    description = "Share media using UPnP"
    upnp_manufacturer = "Higgins Project"
    upnp_model_name = "Higgins"
    upnp_device_type = "urn:schemas-upnp-org:device:MediaServer:1"
    upnp_friendly_name = "Media on Higgins"
    upnp_description = "Higgins UPnP A/V Media Server"
    connection_manager = ConnectionManager()
    content_directory = ContentDirectory()

    def __init__(self):
        pass

    def startService(self):
        UPNPDevice.startService(self)
        logger.log_debug("started mediaserver service")

    def stopService(self):
        logger.log_debug("stopped mediaserver service")
        return UPNPDevice.stopService(self)
