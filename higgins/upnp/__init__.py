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
from higgins.service import Service
from higgins.conf import conf
from higgins.upnp.ssdp_server import SSDPServer
from higgins.upnp.upnp_server import UPnPServer
from higgins.upnp.logger import UPnPLogger

class UPnPRuntimeException(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return self.reason

class UPnPService(Service, UPnPLogger):

    def __init__(self):
        self.upnp_devices = {}

    def registerUPnPDevice(self, device):
        if self.running == 0:
            raise UPnPRuntimeException("UPnP service is not running")
        self.ssdp.registerDevice(device)
        self.upnp.registerDevice(device)
        self.upnp_devices[device.upnp_UDN] = device

    def unregisterUPnPDevice(self, device):
        if self.running == 0:
            raise UPnPRuntimeException("UPnP service is not running")
        self.ssdp.unregisterDevice(device)
        self.upnp.unregisterDevice(device)
        del self.upnp_devices[device.upnp_UDN]

    def startService(self):
        Service.startService(self)
        self.ssdp = SSDPServer()
        self.ssdp.start()
        self.upnp = UPnPServer()
        self.upnp.start()
        for device in self.upnp_devices.values():
            self.upnp.registerDevice(device)
            self.ssdp.registerDevice(device)
        self.log_debug("started UPnP service")

    def stopService(self):
        self.ssdp.stop()
        self.upnp.stop()
        Service.stopService(self)
        self.log_debug("stopped UPnP service")
        return None

upnp_service = UPnPService()
