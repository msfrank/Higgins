# Contains portions of code from pymeds:
#   Licensed under the MIT license
#   http://opensource.org/licenses/mit-license.php
#   Copyright 2005, Tim Potter <tpot@samba.org>
#   Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

import random, string
from twisted.application.service import Service
from ssdp_server import SSDPService
from higgins.logging import Loggable
from higgins.conf import conf

def getUDN(name):
    udn = conf.get(name)
    if udn == None:
        udn=''.join([ 'uuid:'] + map(lambda x: random.choice(string.letters), xrange(20)))
        conf[name] = udn
    return udn

class UpnpRuntimeException(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return self.reason

class UpnpService(Service, Loggable):

    def __init__(self):
        self.is_running = False
        self.upnp_devices = {}

    def registerUpnpDevice(self, device):
        if not self.is_running:
            raise UpnpRuntimeException("upnp service is not running")
        self.ms.registerDevice(device)
        self.upnp_devices[device.upnp_UDN] = device

    def unregisterUpnpDevice(self, device):
        if not self.is_running:
            raise UpnpRuntimeException("upnp service is not running")
        self.ms.unregisterDevice(device)
        del self.upnp_devices[device.upnp_UDN]

    def startService(self):
        Service.startService(self)
        self.ssdp = SSDPService()
        self.ssdp.start()
        self.ms = MSService(self.ssdp)
        self.ms.start()
        self.is_running = True
        self.log_debug("started UPnP service")

    def stopService(self):
        self.ssdp.stop()
        self.ms.stop()
        self.is_running = False
        Service.stopService(self)
        self.log_debug("stopped UPnP service")
        return None
