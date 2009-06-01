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

    # Higgins description variables
    pretty_name = "UPnP Media Server"
    description = "Share media using UPnP"

    # UPnP description variables
    manufacturer = "Higgins Project"
    modelName = "Higgins"
    deviceType = "urn:schemas-upnp-org:device:MediaServer:1"
    friendlyName = "Media on Higgins"
    description = "Higgins UPnP A/V Media Server"

    # UPnP services
    connection_manager = ConnectionManager()
    content_directory = ContentDirectory()

    def startService(self):
        UPNPDevice.startService(self)
        logger.log_debug("started mediaserver service")

    def stopService(self):
        logger.log_debug("stopped mediaserver service")
        return UPNPDevice.stopService(self)
