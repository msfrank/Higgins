# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.
#
# Portions of this code from the pymeds project  are licensed under
# the MIT license: http://opensource.org/licenses/mit-license.php
#
#   Copyright 2005, Tim Potter <tpot@samba.org>
#   Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

import random, string
from twisted.application.service import MultiService
from higgins.conf import conf
from higgins.upnp.ssdp_server import SSDPServer
from higgins.upnp.upnp_server import UPnPServer
from higgins.upnp.logger import UPnPLogger

class UPnPService(MultiService, UPnPLogger):

    def __init__(self):
        MultiService.__init__(self)
        self.upnp_devices = {}

    def registerUPnPDevice(self, device):
        # FIXME: needed?
        #if self.running == 0:
        #    raise Exception("UPnP service is not running")
        self.ssdp.registerDevice(device)
        self.upnp.registerDevice(device)
        self.upnp_devices[device.upnp_UDN] = device

    def unregisterUPnPDevice(self, device):
        # FIXME: needed?
        #if self.running == 0:
        #    raise Exception("UPnP service is not running")
        try:
            self.ssdp.unregisterDevice(device)
            self.upnp.unregisterDevice(device)
            del self.upnp_devices[device.upnp_UDN]
        except Exception, e:
            self.log_debug("failed to unregister device: %s" % e)

    def startService(self):
        MultiService.startService(self)
        self.ssdp = SSDPServer()
        self.ssdp.start()
        self.upnp = UPnPServer()
        self.upnp.start()
        for device in self.upnp_devices.values():
            self.upnp.registerDevice(device)
            self.ssdp.registerDevice(device)
        self.log_debug("started UPnP service")

    def stopService(self):
        MultiService.stopService(self)
        self.ssdp.stop()
        self.upnp.stop()
        self.log_debug("stopped UPnP service")
        return None

upnp_service = UPnPService()
