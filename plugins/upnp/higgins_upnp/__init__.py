# Contains portions of code from pymeds:
#   Licensed under the MIT license
#   http://opensource.org/licenses/mit-license.php
#   Copyright 2005, Tim Potter <tpot@samba.org>
#   Copyright 2006 John-Mark Gurney <gurney_j@resnet.uroegon.edu>

import random, string
from twisted.application.service import Service
from media_server import MSService
from ssdp_server import SSDPService
from logger import UPnPLogger
from higgins.conf import conf

class UpnpService(Service, UPnPLogger):
    def __init__(self):
        self.name = "UPnP"
        self.description = "Exposes the Higgins media store as a UPnP share"
        if conf.get("UPNP_SHARE_NAME") == None:
            conf.set(UPNP_SHARE_NAME="Higgins UPnP Share")
        if conf.get("UPNP_UUID") == None:
            conf.set(UPNP_UUID=''.join([ 'uuid:'] + map(lambda x: random.choice(string.letters), xrange(20))))

    def startService(self):
        Service.startService(self)
        self.ssdp = SSDPService()
        self.ssdp.start()
        self.ms = MSService(self.ssdp)
        self.ms.start()
        self.log_debug ("started UPnP service")

    def stopService(self):
        self.ssdp.stop()
        self.ms.stop()
        Service.stopService(self)
        self.log_debug("stopped UPnP service")
        return None

from django import forms

class UpnpConfig(forms.Form):
    UPNP_SHARE_NAME = forms.CharField(label="UPnP Share Name")
