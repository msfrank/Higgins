# Contains portions of code from pymeds:
#   Licensed under the MIT license
#   http://opensource.org/licenses/mit-license.php
#   Copyright 2005, Tim Potter <tpot@samba.org>
#   Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

import random, string
from ssdp_server import SSDPServer
from upnp_server import UPnPServer
from logger import UPnPLogger
from higgins.conf import conf
from higgins.service import Service

class UPnPRuntimeException(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return self.reason

class UPnPService(Service, UPnPLogger):

    def __init__(self):
        self.is_running = False
        self.upnp_devices = {}
        from higgins.loader import devices
        for factory in devices:
            device = factory()
            self.upnp_devices[device.upnp_UDN] = device

    def registerUPnPDevice(self, device):
        if not self.is_running:
            raise UPnPRuntimeException("UPnP service is not running")
        self.ssdp.registerDevice(device)
        self.upnp_devices[device.upnp_UDN] = device

    def unregisterUPnPDevice(self, device):
        if not self.is_running:
            raise UPnPRuntimeException("UPnP service is not running")
        self.ssdp.unregisterDevice(device)
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
        self.is_running = True
        self.log_debug("started UPnP service")

    def stopService(self):
        self.ssdp.stop()
        self.upnp.stop()
        self.is_running = False
        Service.stopService(self)
        self.log_debug("stopped UPnP service")
        return None
